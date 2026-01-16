"""
Skill Tracking Schemas
Request/Response schemas cho Cumulative Weakness Tracking endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class SkillAttemptHistoryItem(BaseModel):
    """Một lần attempt cho skill"""
    quiz_id: str = Field(..., description="UUID quiz")
    quiz_attempt_id: str = Field(..., description="UUID quiz attempt")
    quiz_title: Optional[str] = Field(None, description="Tên quiz")
    module_id: Optional[str] = Field(None, description="UUID module")
    lesson_id: Optional[str] = Field(None, description="UUID lesson")
    proficiency: float = Field(..., description="Proficiency % trong lần này (0-100)")
    questions_count: int = Field(..., description="Số câu hỏi về skill này")
    correct_count: int = Field(..., description="Số câu đúng")
    wrong_count: int = Field(..., description="Số câu sai")
    attempted_at: datetime = Field(..., description="Thời gian làm quiz")
    wrong_question_ids: List[str] = Field(default_factory=list, description="Danh sách question_id sai")


class WeakSkillItem(BaseModel):
    """Thông tin về một skill yếu"""
    skill_tag: str = Field(..., description="Skill tag (python-loops, python-functions, ...)")
    current_proficiency: float = Field(..., description="Proficiency hiện tại (0-100)")
    total_attempts: int = Field(..., description="Tổng số lần làm quiz có skill này")
    total_questions: int = Field(..., description="Tổng số câu hỏi")
    total_correct: int = Field(..., description="Tổng số câu đúng")
    total_wrong: int = Field(..., description="Tổng số câu sai")
    trend: str = Field(..., description="improving|declining|stable|fluctuating")
    trend_rate: float = Field(..., description="Tốc độ thay đổi proficiency (% change)")
    is_weak_skill: bool = Field(..., description="Có phải điểm yếu không")
    is_chronic_weakness: bool = Field(..., description="Điểm yếu kinh niên")
    consecutive_fails: int = Field(..., description="Số lần sai liên tiếp")
    priority_level: str = Field(..., description="urgent|high|medium|low")
    recommended_lessons: List[str] = Field(default_factory=list, description="Danh sách lesson_id đề xuất")
    last_attempt_at: Optional[datetime] = Field(None, description="Thời gian làm quiz gần nhất")
    improvement_needed: float = Field(..., description="% cần cải thiện để đạt threshold")


class WeakSkillsSummaryResponse(BaseModel):
    """Response cho GET /api/v1/progress/weak-skills"""
    user_id: str = Field(..., description="UUID user")
    course_id: str = Field(..., description="UUID course")
    weak_skills: List[WeakSkillItem] = Field(default_factory=list, description="Danh sách skills yếu")
    total_weak_skills: int = Field(..., description="Tổng số skills yếu")
    total_skills_tracked: int = Field(..., description="Tổng số skills đã track")
    overall_weak_percentage: float = Field(..., description="% skills yếu / tổng skills")
    urgent_count: int = Field(..., description="Số skills ở mức urgent")
    high_priority_count: int = Field(..., description="Số skills ở mức high priority")
    threshold: float = Field(..., description="Ngưỡng proficiency để coi là weak")


class SkillHistoryResponse(BaseModel):
    """Response cho GET /api/v1/progress/skill-history/{skill_tag}"""
    skill_tag: str = Field(..., description="Skill tag")
    current_proficiency: float = Field(..., description="Proficiency hiện tại (0-100)")
    trend: str = Field(..., description="improving|declining|stable|fluctuating")
    trend_rate: float = Field(..., description="Tốc độ thay đổi proficiency")
    total_attempts: int = Field(..., description="Tổng số lần làm quiz")
    total_questions: int = Field(..., description="Tổng số câu hỏi")
    total_correct: int = Field(..., description="Tổng số câu đúng")
    total_wrong: int = Field(..., description="Tổng số câu sai")
    history: List[SkillAttemptHistoryItem] = Field(default_factory=list, description="Lịch sử attempts")
    first_seen: datetime = Field(..., description="Lần đầu gặp skill này")
    last_attempt_at: Optional[datetime] = Field(None, description="Lần làm quiz gần nhất")
    improvement_rate: float = Field(..., description="Tốc độ cải thiện")
    is_improving: bool = Field(..., description="Có đang cải thiện không")
    is_weak_skill: bool = Field(..., description="Có phải điểm yếu không")
    is_chronic_weakness: bool = Field(..., description="Điểm yếu kinh niên")
    consecutive_fails: int = Field(..., description="Số lần sai liên tiếp")
    priority_level: str = Field(..., description="urgent|high|medium|low")


class SkillOverviewItem(BaseModel):
    """Thông tin tóm tắt về một skill"""
    skill_tag: str = Field(..., description="Skill tag")
    proficiency: float = Field(..., description="Proficiency (0-100)")
    trend: str = Field(..., description="improving|declining|stable|fluctuating")
    attempts: int = Field(..., description="Số lần làm quiz")


class SkillsOverviewResponse(BaseModel):
    """Response cho GET /api/v1/progress/skills-overview"""
    user_id: str = Field(..., description="UUID user")
    course_id: str = Field(..., description="UUID course")
    total_skills: int = Field(..., description="Tổng số skills đã track")
    strong_skills: List[SkillOverviewItem] = Field(default_factory=list, description="Skills giỏi (>= 80%)")
    average_skills: List[SkillOverviewItem] = Field(default_factory=list, description="Skills trung bình (60-79%)")
    weak_skills: List[SkillOverviewItem] = Field(default_factory=list, description="Skills yếu (< 60%)")
    strong_count: int = Field(..., description="Số skills giỏi")
    average_count: int = Field(..., description="Số skills trung bình")
    weak_count: int = Field(..., description="Số skills yếu")
    overall_proficiency: float = Field(..., description="Proficiency trung bình tất cả skills")


# ============================================================================
# REQUEST SCHEMAS (if needed for future features)
# ============================================================================

class SkillTrackingFilterRequest(BaseModel):
    """Request filter cho skill tracking queries"""
    threshold: Optional[float] = Field(60.0, description="Ngưỡng proficiency để coi là weak", ge=0, le=100)
    include_all: Optional[bool] = Field(False, description="Include tất cả skills hay chỉ weak skills")
    priority_filter: Optional[str] = Field(None, description="Filter theo priority: urgent|high|medium|low")
    trend_filter: Optional[str] = Field(None, description="Filter theo trend: improving|declining|stable|fluctuating")

