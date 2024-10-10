import dspy
from typing import List, Dict


class GenerateAnswerFromContent(dspy.Signature):
    __doc__ = """
    >>> You are a specialized agent which is expert at answering questions based on the context provided to you.
    >>> Your answers should be by default verbose and thorouhg unless specified otherwise in the query. 
    >>> You should give references to the links which were referenced to answer the query.
    >>> Citations are list of the **links** which were referenced to answer the query. Do not instruction on how you are generating the citations Just give the list of the **links** which were referenced to answer the query.
    """
    query: str = dspy.InputField(
        desc="The query to be answered. This query is to be answered based on the context provided to you below",
    )
    summary_of_contents_of_links: List[Dict[str, str]] = dspy.InputField(
        desc="The summaries of the contents of the relevant pieces which should be used to answer the asked query. This is mapping of title to the content of the link",
    )
    entire_content_of_the_link: List[str] = dspy.InputField(
        desc="The entire content of the links which should be referenced to answer the query. This is also the mapping of title to the content of the link",
    )
    generated_answer: str = dspy.OutputField(
        desc="The answer to the query based on the context provided to you",
    )
    citations: List[str] = dspy.OutputField(
        desc="The list of the **links** which were referenced to answer the query",
    )


class ContentExtractorSignature(dspy.Signature):
    __doc__ = """
    Extract these fields from the given content:\n
    >>> keywords: The List of keywords(comma separated) which are can be used to search the content\n
    >>> summary: The summary of the content which is a short description of the content\n
    >>> title: The title of the content which is a short description of the content\n
    """
    content: str = dspy.InputField(
        desc="The content from which the keywords, summary and title are to be extracted"
    )
    keywords: List[str] = dspy.OutputField(
        desc="The List of keywords(comma separated) which are can be used to search the content"
    )
    summary: str = dspy.OutputField(
        desc="The summary of the content which is a short description of the 'content'"
    )
    title: str = dspy.OutputField(
        desc="The title of the content which is a short description of the 'content'"
    )


class QueryRewriterSignature(dspy.Signature):
    __doc__ = """
    Rewrite the given query based on the conversation history to improve search results.

    Instructions for the LLM:
    >>> Analyze the conversation history to understand the context.
    >>> Identify key topics, concepts, and user intentions from the history.
    >>> Expand or modify the original query to incorporate relevant context.
    >>> Ensure the rewritten query is more specific and targeted.
    >>> Maintain the original intent of the query while enhancing its effectiveness.
    >>> Do not introduce new topics that are not related to the original query or conversation.
    >>> Keep the rewritten query concise and focused.

    Attributes:
        conversation_history (str): The conversation history as a string.
        query (str): The original search query.
        rewritten_query (str): The improved, context-aware search query.
    """
    conversation_history: str = dspy.InputField(
        desc="The conversation history as a string"
    )
    query: str = dspy.InputField(desc="The original search query")
    rewritten_query: str = dspy.OutputField(
        desc="The rewritten, context-aware search query"
    )
