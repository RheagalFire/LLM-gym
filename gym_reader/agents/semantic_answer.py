from gym_reader.agents.base_agent import Agent
from gym_reader.programmes.programmes import (
    TypedChainOfThoughtProgramme as DspyProgramme,
    TypedProgramme as DspySimpleProgramme,
    InstructorProgramme as InstructorProgramme,
)
from typing import List, Dict
import logging
from gym_reader.clients.qdrant_client import qdrant_client
from gym_reader.clients.meilisearch_client import meilisearch_client
from gym_reader.clients.openai_client import openai_client
from gym_reader.signatures.signatures import (
    GenerateAnswerFromContent,
    QueryRewriterSignature,
)
from gym_reader.semantic_search.hybrid_search import HybridSearch
from gym_reader.clients.instructor_client import client_instructor
from gym_reader.data_models import Library
from gym_reader.agents.utils import create_pydantic_model_from_signature

log = logging.getLogger(__name__)


class ContextAwareAnswerAgent(Agent):
    def __init__(self):
        self.class_name = __class__.__name__
        self.input_variables = [
            "search_query",
            "collection_name",
            "conversation_history",
        ]
        self.output_variables = ["answer"]
        self.desc = """
        It takes in a search query that will be used to fetch the results from a vector store and returns the top results from the vector store.\n
        It also takes in a collection name that will be used to fetch the results from a specific collection in the vector store.
        The agent uses query rewriting based on conversation history to improve search results.
        """
        super().__init__(DspyProgramme(signature=GenerateAnswerFromContent))
        self.hybrid_search = HybridSearch(
            qdrant_client=qdrant_client,
            meilisearch_client=meilisearch_client,
            openai_client=openai_client,
        )
        self.query_rewriter = DspySimpleProgramme(signature=QueryRewriterSignature)
        # TODO: Use this later
        self.instructor_programme = InstructorProgramme(client_instructor)

    def forward(
        self,
        search_query: str,
        collection_name: str,
        conversation_history: List[Dict[str, str]],
        request_id: str = None,
        model=None,
        method=Library.INSTRUCTOR,
    ):
        # Rewrite the query based on conversation history
        rewritten_query = self.rewrite_query(
            search_query, conversation_history, request_id=request_id, model=model
        )

        # Search for the code using hybrid search agent with the rewritten query
        search_results = self.hybrid_search.search(
            query=rewritten_query, collection_name=collection_name
        )
        if method == Library.INSTRUCTOR:
            system_message_from_docstring = GenerateAnswerFromContent.__doc__
            log.debug(system_message_from_docstring)
            DynamicOutputModel = create_pydantic_model_from_signature(
                GenerateAnswerFromContent
            )
            log.debug(DynamicOutputModel.model_json_schema())
            user_message = f"""
            Query: {rewritten_query}
            Conversation History: {conversation_history}
            summary_of_contents_of_links: {search_results.summary}
            relevant_content: {search_results.relevant_content}
            """
            self.prediction_object = self.instructor_programme.forward(
                request_id=request_id,
                model=model,
                messages=[
                    {"role": "system", "content": system_message_from_docstring},
                    {"role": "user", "content": user_message},
                ],
                response_model=DynamicOutputModel,
            )
            return self.prediction_object
        else:
            # Pass the top result to the programme
            self.prediction_object = self.programme.forward(
                query=rewritten_query,
                conversation_history=conversation_history,
                summary_of_contents_of_links=search_results.summary,
                relevant_content=search_results.relevant_content,
                request_id=request_id,
                model=model,
            )
            return self.prediction_object

    def __call__(
        self,
        search_query,
        collection_name,
        conversation_history,
        request_id: str = None,
        model=None,
    ):
        return self.forward(
            search_query,
            collection_name,
            conversation_history,
            request_id=request_id,
            model=model,
        )

    def rewrite_query(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        request_id: str = None,
        model=None,
    ) -> str:
        """
        Rewrites the query based on conversation history using TypedPredictor.

        Args:
            query (str): The original search query.
            conversation_history (List[Dict[str, str]]): A list of dictionaries containing the conversation history.

        Returns:
            str: The rewritten query.
        """
        log.debug(f"Original query: {query}")
        rewritten_query = self.query_rewriter.forward(
            conversation_history=str(conversation_history),
            query=query,
            request_id=request_id,
            model=model,
        )
        log.debug(f"Rewritten query: {rewritten_query.rewritten_query}")
        return rewritten_query.rewritten_query


__all__ = ["ContextAwareAnswerAgent"]
