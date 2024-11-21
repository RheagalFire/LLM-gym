import json

from gym_reader.logger import get_logger

from gym_reader.settings import get_settings
from gym_reader.clients.github_client import (
    fetch_file_diff,
    fetch_file_content_at_commit,
)
from gym_reader.data_models import RepoConfig
from gym_reader.agents.extractor_agent import ContentExtractorAgent
from gym_reader.semantic_search.index import GymIndex
from gym_reader.clients.qdrant_client import qdrant_client
from gym_reader.clients.openai_client import openai_client
from gym_reader.clients.meilisearch_client import meilisearch_client
from gym_reader.clients.prisma_client import prisma_singleton
import yaml
import fnmatch
import re
from tqdm import tqdm
from gym_db.gym_db.db_funcs import DbOps, enums


# Create an Extractor Agent
extractor_agent = ContentExtractorAgent()
# Create a Gym Index
gym_index = GymIndex(qdrant_client, meilisearch_client, openai_client)


def read_config_file(file_path: str) -> RepoConfig:
    with open(file_path) as file:
        config = yaml.safe_load(file)
    return RepoConfig(**config)


async def get_dbops_client():
    prisma_client = await prisma_singleton.get_client()
    dbops = DbOps(prisma_client)
    return dbops


# A specific identifier for the comment
settings = get_settings()
config_file_path = settings.CONFIG_FILE_PATH
repo_config = read_config_file(config_file_path)
log = get_logger(__name__)


def get_links_from_diff(file_diff_content):
    """
    Extracts added and deleted links from a Markdown file diff.

    Args:
        file_diff_content (str): The content of the file diff.

    Returns:
        tuple: A tuple containing two lists:
            - added_links (list): Links that were added.
            - deleted_links (list): Links that were deleted.
    """
    added_links = []
    deleted_links = []

    # Regular expression to match Markdown links: [text](url)
    link_pattern = r"\[.*?\]\((.*?)\)"

    # Split the diff content into lines
    lines = file_diff_content.split("\n")

    for line in lines:
        # Skip file information lines in diff output
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue

        # Check for added lines
        if line.startswith("+"):
            line_content = line[1:].strip()
            urls = re.findall(link_pattern, line_content)
            added_links.extend(urls)

        # Check for deleted lines
        if line.startswith("-"):
            line_content = line[1:].strip()
            urls = re.findall(link_pattern, line_content)
            deleted_links.extend(urls)

    return added_links, deleted_links


def extract_links(content):
    """
    Extracts all Markdown links from the provided content.

    Args:
        content (str): The Markdown content from which to extract links.

    Returns:
        list: A list of extracted URLs.
    """
    # Regular expression to match Markdown links: [text](url)
    link_pattern = r"\[.*?\]\((https?://[^\s)]+)\)"

    # Find all matches in the content
    links = re.findall(link_pattern, content)

    return links


async def process_payload_for_push(payload, request):
    payload = json.loads(payload.get("payload", {}))
    # Extract branch name
    branch_name = payload.get("ref", "").split("/")[-1]

    # Extract repository full name
    repo_full_name = payload.get("repository", {}).get("full_name", "")

    # Extract request ID from headers
    request_id = request.headers.get("X-Request-ID", "default-request-id")

    # Extract the latest commit SHA
    latest_commit_sha = payload.get("head_commit", {}).get("id", "")

    # Extract file paths, names, and extensions
    file_changes = payload.get("head_commit", {}).get("modified", [])
    file_details = [
        {
            "path": file,
            "name": file.split("/")[-1],
            "extension": file.split(".")[-1] if "." in file else "",
        }
        for file in file_changes
    ]

    # Fetch owner and repo
    if "/" in repo_full_name:
        owner, repo = repo_full_name.split("/", 1)
    else:
        owner, repo = repo_full_name, ""

    return {
        "latest_commit_sha": latest_commit_sha,
        "branch_name": branch_name,
        "repo_full_name": repo_full_name,
        "request_id": request_id,
        "file_details": file_details,
        "owner": owner,
        "repo": repo,
    }


async def push_action_handler(payload, request):
    dbops = await get_dbops_client()
    event_data = await process_payload_for_push(payload, request)
    log.debug(f"Event data: {event_data}")
    # get the data from the event_data
    branch_name = event_data.get("branch_name")
    file_details = event_data.get("file_details")
    owner = event_data.get("owner")
    repo = event_data.get("repo")
    latest_commit_sha = event_data.get("latest_commit_sha")
    github_token = settings.PAT_TOKEN

    if repo_config.base_branch != branch_name:
        log.info(
            f"Branch name {branch_name} is not the base branch {repo_config.base_branch}"
        )
        return None

    added_links = []
    deleted_links = []
    for file_detail in file_details:
        if not any(
            fnmatch.fnmatch(file_detail["path"], pattern)
            for pattern in repo_config.search_paths
        ):
            log.info(
                f"File path {file_detail['path']} does not match any pattern in the search paths {repo_config.search_paths}"
            )
            continue
        if file_detail["extension"] not in repo_config.include_extensions:
            log.info(
                f"File extension {file_detail['extension']} is not in the include extensions {repo_config.include_extensions}"
            )
            continue

        # get the file diff
        file_diff = await fetch_file_diff(owner, repo, latest_commit_sha, github_token)
        file_content = await fetch_file_content_at_commit(
            owner, repo, file_detail["path"], latest_commit_sha, github_token
        )

        # get all the links from the file content
        all_links = extract_links(file_content)
        log.debug(f"All links: {all_links}")

        # get the added and deleted links from the file diff
        added_links, deleted_links = get_links_from_diff(file_diff)

        # if any deleted link is in added_link, remove it from the deleted_links
        deleted_links = [link for link in deleted_links if link not in added_links]

        # let's check which links are present and which are not
        added_links = [
            link for link in all_links if not gym_index.check_if_link_exists(link, repo)
        ]
        log.debug(f"Added links: {added_links}")

        # for added links, let's upsert the document to the database
        for added_link in tqdm(added_links, total=len(added_links)):
            try:
                type = enums.DocumentType.Link.value
                document_record = await dbops.upsert_document(added_link, type, repo)
            except Exception as e:
                log.error(f"Error upserting document {added_link}: {e}", exc_info=True)
                continue

            # No indexing logic here, just upsert the document
            # The indexing will be handled by the indexing service

    try:
        if deleted_links:
            for deleted_link in deleted_links:
                document_record = await dbops.get_document_record_by_url(deleted_link)
                if document_record:
                    await dbops.update_document_deleted_status_by_uuid(
                        document_record.uuid, True
                    )
            # mark the document as deleted in the database
            # No indexing logic here
    except Exception as e:
        log.error(f"Error deleting from qdrant collection: {e}", exc_info=True)
    log.debug(f"Added links: {added_links}")
    log.debug(f"Deleted links: {deleted_links}")
    return True
