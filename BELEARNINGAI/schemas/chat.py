"""
Chat Schemas
Định nghĩa request/response schemas cho chat endpoints
Tuân thủ API_SCHEMA.md Section 2.6
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ChatMessageRequest(BaseModel):
    """Request schema cho chat message - Section 2.6.1"""

    question: str = Field(..., description="Câu hỏi của học viên")
    conversation_id: Optional[str] = Field(None, description="UUID conversation để duy trì context")
    context_type: Optional[Literal["lesson", "module", "general"]] = Field("general", description="Loại context")
    image_base64: Optional[str] = None
    image_mime_type: Optional[str] = None

    question: str = Field(..., description="Câu hỏi của học viên", examples=["Python list comprehension là gì?"])
    conversation_id: Optional[str] = Field(None, description="UUID conversation để duy trì context")
    context_type: Optional[Literal["lesson", "module", "general"]] = Field("general", description="Loại context")

    #Image support
    image_base64: Optional[str] = Field(
        None,
        description="Ảnh dạng base64 (không bao gồm prefix 'data:image/...')",
        examples=["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="]
    )
    image_mime_type: Optional[str] = Field(
        None,
        description="MIME type: image/png, image/jpeg, image/webp, image/gif",
        examples=["image/png"]
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "question": "Python list comprehension là gì?",
                    "conversation_id": None,
                    "context_type": "general"
                },
                {
                    "question": "Code này bị lỗi gì? Giải thích và sửa giúp tôi",
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "context_type": "lesson",
                    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==",
                    "image_mime_type": "image/png"
                }
            ]
        }

# ============================================================================
# RESPONSE SCHEMAS - Section 2.6.1
# ============================================================================

class SourceInfo(BaseModel):
    """Thông tin nguồn trích dẫn từ course content"""
    type: str = Field(..., description="lesson|module|resource")
    id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tiêu đề nguồn")
    excerpt: str = Field(..., description="Đoạn trích liên quan")


class RelatedLesson(BaseModel):
    """Bài học liên quan được suggest"""
    lesson_id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tiêu đề bài học")
    url: str = Field(..., description="Link đến lesson")


class ChatMessageResponse(BaseModel):
    """Response schema cho chat message - Section 2.6.1"""
    conversation_id: str = Field(..., description="UUID conversation")
    message_id: str = Field(..., description="UUID của message này")
    question: str = Field(..., description="Câu hỏi đã gửi")
    answer: str = Field(..., description="Câu trả lời từ AI, markdown format")
    sources: List[SourceInfo] = Field(default_factory=list, description="Nguồn trích dẫn")
    related_lessons: List[RelatedLesson] = Field(default_factory=list, description="Bài học liên quan")
    timestamp: datetime = Field(..., description="Thời gian tạo message")
    tokens_used: Optional[int] = Field(None, description="Số tokens AI đã dùng (optional)")

    #Image support
    has_image: bool = Field(default=False, description="Message có kèm ảnh không")
    image_analyzed: bool = Field(default=False, description="AI đã phân tích ảnh chưa")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                    "question": "Python list comprehension là gì?",
                    "answer": "List comprehension là cú pháp ngắn gọn để tạo list mới từ iterable có sẵn...",
                    "sources": [],
                    "related_lessons": [],
                    "timestamp": "2024-12-26T10:30:00Z",
                    "tokens_used": 150,
                    "has_image": False,
                    "image_analyzed": False
                },
                {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message_id": "7ba7b810-9dad-11d1-80b4-00c04fd430c9",
                    "question": "Code này bị lỗi gì?",
                    "answer": "Tôi thấy trong ảnh code của bạn có lỗi ở dòng 5: thiếu dấu ':' sau if statement...",
                    "sources": [
                        {
                            "type": "lesson",
                            "id": "lesson-123",
                            "title": "Python Control Flow",
                            "excerpt": "If statements require a colon..."
                        }
                    ],
                    "related_lessons": [
                        {
                            "lesson_id": "lesson-123",
                            "title": "Python Control Flow",
                            "url": "/courses/python-101/lessons/lesson-123"
                        }
                    ],
                    "timestamp": "2024-12-26T10:35:00Z",
                    "tokens_used": 250,
                    "has_image": True,
                    "image_analyzed": True
                }
            ]
        }


# ============================================================================
# RESPONSE SCHEMAS - Section 2.6.2 (Chat History)
# ============================================================================

class ConversationListItem(BaseModel):
    """Item trong danh sách conversations"""
    conversation_id: str = Field(..., description="UUID")
    course_id: str = Field(..., description="UUID khóa học")
    course_title: str = Field(..., description="Tên khóa học")
    topic_summary: str = Field(..., description="Chủ đề chính được AI tóm tắt")
    message_count: int = Field(..., description="Số messages trong conversation")
    last_message_preview: str = Field(..., description="Preview message cuối, 100 ký tự")
    created_at: datetime = Field(..., description="Thời gian bắt đầu")
    last_updated: datetime = Field(..., description="Thời gian message cuối cùng")


class GroupedByDate(BaseModel):
    """Nhóm conversations theo thời gian"""
    today: List[str] = Field(default_factory=list, description="Conversation IDs hôm nay")
    yesterday: List[str] = Field(default_factory=list, description="Conversation IDs hôm qua")
    this_week: List[str] = Field(default_factory=list, description="Conversation IDs tuần này")
    older: List[str] = Field(default_factory=list, description="Conversation IDs cũ hơn")


class ChatHistoryListResponse(BaseModel):
    """Response schema cho chat history - Section 2.6.2"""
    conversations: List[ConversationListItem] = Field(..., description="Danh sách conversations")
    grouped_by_date: GroupedByDate = Field(..., description="Nhóm theo thời gian")
    total: int = Field(..., description="Tổng số conversations")
    skip: int = Field(..., description="Pagination skip")
    limit: int = Field(..., description="Pagination limit")


# ============================================================================
# RESPONSE SCHEMAS - Section 2.6.3 (Conversation Detail)
# ============================================================================

class MessageSource(BaseModel):
    """Nguồn trích dẫn trong message"""
    type: str = Field(..., description="lesson|module|resource")
    title: str = Field(..., description="Tiêu đề nguồn")
    url: str = Field(..., description="Link đến nguồn")


class Message(BaseModel):
    """Message trong conversation"""
    message_id: str = Field(..., description="UUID")
    role: str = Field(..., description="user|assistant")
    content: str = Field(..., description="Nội dung message, markdown format")
    timestamp: datetime = Field(..., description="Thời gian tạo message")
    sources: Optional[List[MessageSource]] = Field(None, description="Nguồn trích dẫn (optional)")


class CourseInfo(BaseModel):
    """Thông tin khóa học trong conversation detail"""
    course_id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tên khóa học")
    thumbnail_url: Optional[str] = Field(None, description="URL ảnh thumbnail")


class ConversationDetailResponse(BaseModel):
    """Response schema cho conversation detail - Section 2.6.3"""
    conversation_id: str = Field(..., description="UUID conversation")
    course: CourseInfo = Field(..., description="Thông tin khóa học")
    created_at: datetime = Field(..., description="Thời gian bắt đầu conversation")
    last_updated: datetime = Field(..., description="Thời gian message cuối")
    message_count: int = Field(..., description="Số lượng messages")
    messages: List[Message] = Field(..., description="Danh sách messages")


# ============================================================================
# RESPONSE SCHEMAS - Section 2.6.4 & 2.6.5 (Delete)
# ============================================================================

class ChatDeleteResponse(BaseModel):
    """Response schema cho xóa một conversation - Section 2.6.5"""
    conversation_id: str = Field(..., description="UUID đã xóa")
    message: str = Field(..., description="Thông báo")
    deleted_at: datetime = Field(..., description="Thời gian xóa")


class ChatDeleteAllResponse(BaseModel):
    """Response schema cho xóa tất cả conversations - Section 2.6.4"""
    deleted_count: int = Field(..., description="Số conversations đã xóa")
    message: str = Field(..., description="Thông báo")
    deleted_at: datetime = Field(..., description="Thời gian xóa")
