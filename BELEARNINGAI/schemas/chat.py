"""
Chat Schemas
Định nghĩa request/response schemas cho chat endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ChatMessageRequest(BaseModel):
    question: str = Field(..., description="User question")
    conversation_id: Optional[str] = Field(None, description="UUID to continue existing conversation")


class SourceInfo(BaseModel):
    lesson_id: str = Field(..., description="UUID")
    lesson_title: str
    relevance_score: float = Field(..., description="0-100")


class ChatMessageResponse(BaseModel):
    conversation_id: str = Field(..., description="UUID")
    course_id: str = Field(..., description="UUID")
    question: str
    answer: str = Field(..., description="Markdown formatted with code highlighting")
    generated_at: datetime
    sources: List[SourceInfo]


class ConversationListItem(BaseModel):
    id: str = Field(..., description="UUID")
    course_id: str = Field(..., description="UUID")
    course_title: str
    summary: str = Field(..., description="AI summary of topic")
    last_message_at: datetime
    message_count: int


class ChatHistoryListResponse(BaseModel):
    conversations: List[ConversationListItem]
    total: int
    skip: int
    limit: int


class Message(BaseModel):
    id: str = Field(..., description="UUID")
    role: str = Field(..., description="user|assistant")
    content: str
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    id: str = Field(..., description="UUID conversation")
    course_id: str = Field(..., description="UUID")
    course_title: str
    summary: str = Field(..., description="AI summary")
    messages: List[Message]
    total_messages: int
    created_at: datetime
    last_updated: datetime


class ChatDeleteResponse(BaseModel):
    message: str


class ChatDeleteAllResponse(BaseModel):
    message: str
    deleted_count: int
    note: str
