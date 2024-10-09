from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from enum import Enum


class SearchResult(BaseModel):
    summary: List[Dict[str, str]]
    content_score: List[float]
    summary_score: List[float]
    entire_content_of_the_link: List[str]


class RepoConfig(BaseModel):
    base_branch: str
    search_paths: List[str]
    include_extensions: List[str]


class Library(str, Enum):
    DSPY = "dspy"
    INSTRUCTOR = "instructor"


class PayloadForIndexing(BaseModel):
    uuid: str
    parent_link: str
    parent_content: str
    child_links: List[str]
    child_contents: List[str]
    parent_summary: str
    parent_title: str
    parent_keywords: List[str]


class Message(BaseModel):
    content: str
    role: str


class ChatPayload(BaseModel):
    messages: List[Message]
    collection_name: str


class Answer(BaseModel):
    content: str
    role: str


class ResponseModel(BaseModel):
    data: Optional[Answer] = None
    meta: Optional[Any] = None
    error: Optional[Any] = None
