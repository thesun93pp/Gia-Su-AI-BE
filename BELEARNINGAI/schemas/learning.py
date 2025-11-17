"""
Learning Schemas - Module & Lesson Content
Định nghĩa request/response schemas cho learning endpoints (Section 2.4.1-2.4.2)
Tuân thủ: CHUCNANG.md Section 2.4, ENDPOINTS.md learning_router
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


# ============================================================================
# SECTION 2.4.1: XEM THÔNG TIN MODULE
# ============================================================================

class LessonSummaryInModule(BaseModel):
    """Summary của lesson trong module detail"""
    id: str = Field(..., description="UUID của lesson")
    title: str = Field(..., description="Tiêu đề lesson")
    order: int = Field(..., description="Thứ tự lesson trong module")
    duration_minutes: int = Field(..., description="Thời lượng ước tính (phút)")
    content_type: str = Field(..., description="text|video|mixed")
    is_completed: bool = Field(..., description="Trạng thái hoàn thành của user hiện tại")
    is_locked: bool = Field(False, description="Bị khóa do chưa hoàn thành lesson trước")


class LearningOutcome(BaseModel):
    """Mục tiêu học tập của module"""
    id: str = Field(..., description="UUID")
    outcome: str = Field(..., description="Mô tả mục tiêu cụ thể")
    skill_tag: str = Field(..., description="Tag để tracking, vd: 'python-functions'")
    is_mandatory: bool = Field(..., description="Kiến thức bắt buộc hay tùy chọn")


class ResourceItem(BaseModel):
    """Tài nguyên đính kèm"""
    id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tên tài nguyên")
    type: str = Field(..., description="pdf|slide|code|video|link")
    url: str = Field(..., description="Link download/view")
    size_mb: Optional[float] = Field(None, description="Kích thước file (MB)")
    description: Optional[str] = Field(None, description="Mô tả ngắn")


class ModuleDetailResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/modules/{module_id}
    Section 2.4.1: Xem thông tin chi tiết module
    """
    id: str = Field(..., description="UUID của module")
    title: str = Field(..., description="Tiêu đề module")
    description: str = Field(..., description="Mô tả chi tiết module")
    difficulty: str = Field(..., description="Basic|Intermediate|Advanced")
    order: int = Field(..., description="Thứ tự module trong khóa học")
    
    # Lessons trong module
    lessons: List[LessonSummaryInModule] = Field(..., description="Danh sách lessons theo thứ tự")
    
    # Learning outcomes
    learning_outcomes: List[LearningOutcome] = Field(..., description="Mục tiêu học tập")
    
    # Thời lượng học
    estimated_hours: float = Field(..., description="Thời gian học ước tính (giờ)")
    
    # Tài nguyên đính kèm
    resources: List[ResourceItem] = Field(default_factory=list, description="Tài nguyên học tập")
    
    # Trạng thái của user hiện tại
    completion_status: str = Field(..., description="not-started|in-progress|completed")
    completed_lessons_count: int = Field(..., description="Số lessons đã hoàn thành")
    total_lessons_count: int = Field(..., description="Tổng số lessons")
    progress_percent: float = Field(..., description="% hoàn thành (0-100)")
    
    # Prerequisites
    prerequisites: List[str] = Field(default_factory=list, description="Danh sách module IDs tiên quyết")


# ============================================================================
# SECTION 2.4.2: XEM NỘI DUNG BÀI HỌC
# ============================================================================

class AttachmentFile(BaseModel):
    """Tài liệu đính kèm trong lesson"""
    id: str = Field(..., description="UUID")
    filename: str = Field(..., description="Tên file")
    file_type: str = Field(..., description="pdf|docx|code|other")
    url: str = Field(..., description="Link download")
    size_mb: float = Field(..., description="Kích thước file (MB)")


class VideoInfo(BaseModel):
    """Thông tin video bài giảng"""
    url: str = Field(..., description="Link video")
    duration_seconds: int = Field(..., description="Thời lượng video (giây)")
    thumbnail_url: Optional[str] = Field(None, description="Link thumbnail")
    quality: List[str] = Field(default_factory=lambda: ["360p", "720p", "1080p"], description="Chất lượng có sẵn")


class LessonContentResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/lessons/{lesson_id}
    Section 2.4.2: Xem nội dung bài học
    """
    id: str = Field(..., description="UUID của lesson")
    title: str = Field(..., description="Tiêu đề lesson")
    module_id: str = Field(..., description="UUID của module cha")
    module_title: str = Field(..., description="Tên module")
    order: int = Field(..., description="Thứ tự lesson")
    duration_minutes: int = Field(..., description="Thời lượng ước tính")
    
    # Nội dung
    content_type: str = Field(..., description="text|video|mixed")
    text_content: Optional[str] = Field(None, description="Nội dung HTML/Markdown")
    video_info: Optional[VideoInfo] = Field(None, description="Thông tin video nếu có")
    attachments: List[AttachmentFile] = Field(default_factory=list, description="Tài liệu đính kèm")
    
    # Navigation
    previous_lesson_id: Optional[str] = Field(None, description="UUID lesson trước")
    next_lesson_id: Optional[str] = Field(None, description="UUID lesson tiếp theo")
    is_next_locked: bool = Field(False, description="Lesson tiếp bị khóa do chưa pass quiz")
    
    # Tracking thông tin của user
    is_completed: bool = Field(False, description="User đã hoàn thành chưa")
    last_accessed_at: Optional[datetime] = Field(None, description="Lần truy cập cuối")
    time_spent_seconds: int = Field(0, description="Tổng thời gian đã học (giây)")
    video_progress_seconds: int = Field(0, description="Tiến độ xem video (giây)")
    
    # Quiz liên kết
    quiz_id: Optional[str] = Field(None, description="UUID quiz kèm theo (nếu có)")
    quiz_passed: bool = Field(False, description="Đã pass quiz chưa")
    quiz_required: bool = Field(True, description="Có bắt buộc phải pass quiz không")
    
    # Message
    message: Optional[str] = Field(None, description="Thông báo cho user, vd: 'Bạn cần hoàn thành quiz để mở lesson tiếp theo'")


# ============================================================================
# ADDITIONAL ENDPOINTS (Notes trong ENDPOINTS.md)
# ============================================================================

class ModuleListItem(BaseModel):
    """Item trong danh sách modules"""
    id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tiêu đề module")
    difficulty: str = Field(..., description="Basic|Intermediate|Advanced")
    order: int = Field(..., description="Thứ tự")
    lesson_count: int = Field(..., description="Số lượng lessons")
    estimated_hours: float = Field(..., description="Thời lượng ước tính")
    progress_percent: float = Field(0.0, description="% hoàn thành của user")
    is_locked: bool = Field(False, description="Bị khóa do chưa hoàn thành module trước")


class CourseModulesResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/modules
    Lấy danh sách tất cả modules trong khóa học
    """
    course_id: str = Field(..., description="UUID")
    course_title: str = Field(..., description="Tên khóa học")
    modules: List[ModuleListItem] = Field(..., description="Danh sách modules")
    total_modules: int = Field(..., description="Tổng số modules")
    completed_modules: int = Field(0, description="Số modules đã hoàn thành")


class ModuleOutcomesResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/modules/{module_id}/outcomes
    Lấy chi tiết learning outcomes của module
    """
    module_id: str = Field(..., description="UUID")
    module_title: str = Field(..., description="Tên module")
    learning_outcomes: List[LearningOutcome] = Field(..., description="Danh sách outcomes")
    total_outcomes: int = Field(..., description="Tổng số outcomes")
    achieved_outcomes: int = Field(0, description="Số outcomes đã đạt được")


class ModuleResourcesResponse(BaseModel):
    """
    Response cho GET /api/v1/courses/{course_id}/modules/{module_id}/resources
    Lấy tất cả tài nguyên học tập của module
    """
    module_id: str = Field(..., description="UUID")
    module_title: str = Field(..., description="Tên module")
    resources: List[ResourceItem] = Field(..., description="Danh sách tài nguyên")
    total_resources: int = Field(..., description="Tổng số tài nguyên")
    resources_by_type: dict = Field(..., description="Số lượng theo từng type")


class ModuleAssessmentGenerateRequest(BaseModel):
    """
    Request cho POST /api/v1/courses/{course_id}/modules/{module_id}/assessments/generate
    Sinh quiz đánh giá tự động cho module
    """
    difficulty: str = Field("medium", description="easy|medium|hard")
    question_count: int = Field(10, ge=5, le=30, description="Số câu hỏi muốn sinh")
    include_mandatory: bool = Field(True, description="Có bao gồm câu điểm liệt không")
    focus_outcomes: Optional[List[str]] = Field(None, description="Danh sách outcome IDs cần tập trung")


class ModuleAssessmentGenerateResponse(BaseModel):
    """Response cho endpoint sinh quiz module"""
    quiz_id: str = Field(..., description="UUID quiz vừa tạo")
    module_id: str = Field(..., description="UUID module")
    question_count: int = Field(..., description="Số câu hỏi đã sinh")
    difficulty: str = Field(..., description="Độ khó")
    estimated_time_minutes: int = Field(..., description="Thời gian làm bài ước tính")
    message: str = Field(..., description="Thông báo")
