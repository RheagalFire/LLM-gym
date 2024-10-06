from gym_reader.agents.base_agent import Agent
from gym_reader.programmes.programmes import (
    TypedChainOfThoughtProgramme as DspyProgramme,
    InstructorProgramme,
)
import logging
from gym_reader.signatures.signatures import (
    ContentExtractorSignature,
)
from gym_reader.data_models import Library
from gym_reader.agents.utils import create_pydantic_model_from_signature
from gym_reader.clients.instructor_client import client_instructor
from gym_reader.data_models import PayloadForIndexing
from gym_reader.clients.spider_web_crawler import spider_client
import uuid

log = logging.getLogger(__name__)


class ContentExtractorAgent(Agent):
    def __init__(self):
        self.class_name = __class__.__name__
        self.input_variables = [
            "content",
        ]
        self.output_variables = ["keywords", "summary", "title"]
        self.desc = """
        This agent extracts the keywords, summary and title from the given content.
        """
        super().__init__(DspyProgramme(signature=ContentExtractorSignature))
        self.instructor_programme = InstructorProgramme(client_instructor)

    def forward(
        self,
        link: str,
        request_id: str = None,
        model=None,
        method=Library.INSTRUCTOR,
    ) -> PayloadForIndexing:
        search_result = spider_client.search(link)
        parent_content = search_result[0]["content"]
        parent_link = search_result[0]["url"]
        child_contents = []
        child_links = []
        for link in search_result[1:]:
            child_contents.append(link["content"])
            child_links.append(link["url"])

        if method == Library.DSPY:
            self.prediction_object = self.programme.forward(
                content=parent_content,
                request_id=request_id,
                model=model,
            )
            result = PayloadForIndexing(
                uuid=str(uuid.uuid4()),
                parent_link=parent_link,
                child_links=child_links,
                parent_content=parent_content,
                child_contents=child_contents,
                parent_summary=self.prediction_object.summary,
                parent_title=self.prediction_object.title,
                parent_keywords=self.prediction_object.keywords,
            )
            return result
        elif method == Library.INSTRUCTOR:
            # get the docstring from the signature
            system_message_from_docstring = ContentExtractorSignature.__doc__
            log.debug(system_message_from_docstring)
            DynamicOutputModel = create_pydantic_model_from_signature(
                ContentExtractorSignature
            )
            log.debug(DynamicOutputModel.model_json_schema())
            self.prediction_object = self.instructor_programme.forward(
                request_id=request_id,
                model=model,
                messages=[
                    {"role": "system", "content": system_message_from_docstring},
                    {"role": "user", "content": parent_content},
                ],
                response_model=DynamicOutputModel,
            )
            result = PayloadForIndexing(
                uuid=str(uuid.uuid4()),
                parent_link=parent_link,
                child_links=child_links,
                parent_content=parent_content,
                child_contents=child_contents,
                parent_summary=self.prediction_object.summary,
                parent_title=self.prediction_object.title,
                parent_keywords=self.prediction_object.keywords,
            )
            return result

    def __call__(
        self,
        content,
        request_id: str = None,
        model=None,
    ):
        return self.forward(
            content,
            request_id=request_id,
            model=model,
        )


__all__ = ["ContentExtractorAgent"]
