"""
Module Assessment Review Schemas
Request/Response schemas cho tính năng review lessons sau module assessment
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict


class LessonToReview(BaseModel):
    """Thông tin lesson cần review"""
    lesson_id: str = Field(..., description="UUID của lesson")
    lesson_title: str = Field(..., description="Tiêu đề lesson")
    module_id: str = Field(..., description="UUID của module")
    skill_gaps: List[str] = Field(..., description="Danh sách skill tags bị thiếu")
    wrong_questions: List[str] = Field(..., description="Danh sách question IDs làm sai")
    reason: str = Field(..., description="Lý do cần review")


class SkillGapInfo(BaseModel):
    """Thông tin lỗ hổng kiến thức cho một skill"""
    wrong_count: int = Field(..., description="Số câu làm sai")
    total_count: int = Field(..., description="Tổng số câu về skill này")
    proficiency: float = Field(..., description="Độ thành thạo (0-100)")


class LessonsToReviewResponse(BaseModel):
    """Response cho GET /enrollments/{id}/lessons-to-review"""
    total_count: int = Field(..., description="Tổng số lessons cần review")
    pending_count: int = Field(..., description="Số lessons chưa review")
    reviewed_count: int = Field(..., description="Số lessons đã review")
    lessons: List[Dict] = Field(..., description="Danh sách lessons cần review")


class MarkReviewedResponse(BaseModel):
    """Response cho POST /enrollments/{id}/lessons/{lesson_id}/mark-reviewed"""
    success: bool = Field(..., description="Thành công hay không")
    message: str = Field(..., description="Thông báo")
    remaining_lessons: int = Field(..., description="Số lessons còn lại cần review")


class ModuleAssessmentAnalysis(BaseModel):
    """Kết quả phân tích module assessment (thêm vào QuizAttemptResponse)"""
    lessons_to_review: List[LessonToReview] = Field(
        default_factory=list,
        description="Danh sách lessons cần xem lại"
    )
    skill_gaps_summary: Dict[str, SkillGapInfo] = Field(
        default_factory=dict,
        description="Tóm tắt lỗ hổng kiến thức theo skill"
    )

