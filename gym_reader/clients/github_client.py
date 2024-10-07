import httpx
import aiohttp


async def fetch_diff_content_for_pr(
    owner: str, repo: str, pull_number: int, token: str
) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",  # Request diff format
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


async def fetch_file_diff(owner, repo, commit_sha, github_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3.diff",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


async def fetch_file_content_at_commit(
    owner: str, repo: str, file_path: str, commit_sha: str, token: str
) -> str:
    """
    Fetches the content of a file at a specific commit SHA.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        file_path (str): Path to the file in the repository.
        commit_sha (str): The commit SHA to retrieve the file from.
        token (str): GitHub access token.

    Returns:
        str: The content of the file as a string.

    Raises:
        httpx.HTTPStatusError: If the HTTP request fails.
        Exception: If the file content cannot be retrieved.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.raw",  # To get raw file content
    }
    params = {"ref": commit_sha}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        try:
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Failed to fetch file content: {e.response.status_code}"
            ) from e


async def post_github_comment(
    pr_number: int, comment: str, owner: str, repo: str, token: str
):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"body": comment}, headers=headers)
        response.raise_for_status()


async def get_existing_comment(
    pr_number: int, owner: str, repo: str, token: str, identifier: str
):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                comments = await response.json()
                for comment in comments:
                    if identifier in comment["body"]:
                        return comment
    return None


async def update_github_comment(
    comment_id: int, new_body: str, owner: str, repo: str, token: str
):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {"body": new_body}
    async with aiohttp.ClientSession() as session:
        async with session.patch(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to update comment: {response.status}")
