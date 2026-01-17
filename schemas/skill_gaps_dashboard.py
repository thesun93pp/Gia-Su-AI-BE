"""
Skill Gaps Dashboard Schemas
Request/Response schemas cho analytics & dashboard endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


# ============================================================================
# DASHBOARD COMPONENTS
# ============================================================================

class OverviewStats(BaseModel):
    """Thống kê tổng quan"""
    total_skills: int = Field(..., description="Tổng số skills đã track")
    weak_skills_count: int = Field(..., description="Số skills yếu")
    strong_skills_count: int = Field(..., description="Số skills mạnh")
    average_proficiency: float = Field(..., description="Proficiency trung bình")
    improvement_rate: float = Field(..., description="Tốc độ cải thiện (%)")


class SkillDistribution(BaseModel):
    """Phân bố skills cho pie chart"""
    labels: List[str] = Field(..., description="Labels: Strong, Average, Weak")
    values: List[int] = Field(..., description="Số lượng skills trong mỗi category")
    percentages: List[float] = Field(..., description="Phần trăm")
    colors: List[str] = Field(..., description="Màu sắc cho chart")


class WeaknessHeatmapItem(BaseModel):
    """Một item trong weakness heatmap"""
    skill_tag: str = Field(..., description="Skill tag")
    proficiency: float = Field(..., description="Proficiency (0-100)")
    priority: str = Field(..., description="urgent|high|medium|low")
    attempts: int = Field(..., description="Số lần làm quiz")
    trend: str = Field(..., description="improving|declining|stable|fluctuating")
    consecutive_fails: int = Field(..., description="Số lần sai liên tiếp")
    last_attempt: Optional[datetime] = Field(None, description="Lần làm quiz gần nhất")


class ImprovementTrend(BaseModel):
    """Trend data cho line chart"""
    dates: List[str] = Field(..., description="Danh sách dates (YYYY-MM-DD)")
    average_proficiency: List[float] = Field(..., description="Proficiency trung bình theo thời gian")
    weak_skills_count: List[int] = Field(..., description="Số skills yếu theo thời gian")
    chart_type: str = Field(default="line", description="Loại chart")


class TopWeaknessItem(BaseModel):
    """Chi tiết về một weakness"""
    skill_tag: str = Field(..., description="Skill tag")
    proficiency: float = Field(..., description="Proficiency hiện tại")
    priority: str = Field(..., description="urgent|high|medium|low")
    trend: str = Field(..., description="improving|declining|stable|fluctuating")
    trend_rate: float = Field(..., description="Tốc độ thay đổi")
    total_attempts: int = Field(..., description="Tổng số attempts")
    consecutive_fails: int = Field(..., description="Số lần sai liên tiếp")
    is_chronic: bool = Field(..., description="Có phải chronic weakness không")
    last_attempt: Optional[datetime] = Field(None, description="Lần làm quiz gần nhất")
    improvement_needed: float = Field(..., description="% cần cải thiện để đạt 60%")


class RecentImprovementItem(BaseModel):
    """Skill đã cải thiện gần đây"""
    skill_tag: str = Field(..., description="Skill tag")
    proficiency: float = Field(..., description="Proficiency hiện tại")
    trend_rate: float = Field(..., description="Tốc độ cải thiện")
    total_attempts: int = Field(..., description="Tổng số attempts")
    last_attempt: Optional[datetime] = Field(None, description="Lần làm quiz gần nhất")


# ============================================================================
# MAIN DASHBOARD RESPONSE
# ============================================================================

class SkillGapsDashboardResponse(BaseModel):
    """Response cho GET /api/v1/dashboard/skill-gaps"""
    user_id: str = Field(..., description="UUID user")
    course_id: str = Field(..., description="UUID course")
    overview: OverviewStats = Field(..., description="Thống kê tổng quan")
    skill_distribution: SkillDistribution = Field(..., description="Phân bố skills (pie chart)")
    weakness_heatmap: List[WeaknessHeatmapItem] = Field(
        default_factory=list,
        description="Top 10 skills yếu nhất (heatmap)"
    )
    improvement_trend: ImprovementTrend = Field(..., description="Xu hướng cải thiện (line chart)")
    top_weaknesses: List[TopWeaknessItem] = Field(
        default_factory=list,
        description="Top 5 weaknesses chi tiết"
    )
    recent_improvements: List[RecentImprovementItem] = Field(
        default_factory=list,
        description="Top 5 skills cải thiện gần đây"
    )
    message: Optional[str] = Field(None, description="Message nếu không có data")
    generated_at: datetime = Field(..., description="Thời gian generate dashboard")


# ============================================================================
# COURSE-LEVEL ANALYTICS SCHEMAS
# ============================================================================

class SkillDifficultyItem(BaseModel):
    """Độ khó của một skill trong course"""
    skill_tag: str = Field(..., description="Skill tag")
    average_proficiency: float = Field(..., description="Proficiency trung bình của tất cả students")
    students_struggling: int = Field(..., description="Số students đang gặp khó khăn")
    total_students_attempted: int = Field(..., description="Tổng số students đã làm")
    difficulty_score: float = Field(..., description="Điểm độ khó (0-10, cao = khó)")


class CommonWeaknessItem(BaseModel):
    """Weakness phổ biến trong course"""
    skill_tag: str = Field(..., description="Skill tag")
    students_affected: int = Field(..., description="Số students bị ảnh hưởng")
    average_proficiency: float = Field(..., description="Proficiency trung bình")


class SkillsOverview(BaseModel):
    """Tổng quan skills trong course"""
    total_unique_skills: int = Field(..., description="Tổng số skills unique")
    most_common_weaknesses: List[CommonWeaknessItem] = Field(
        default_factory=list,
        description="Top 10 weaknesses phổ biến nhất"
    )


class StudentDistribution(BaseModel):
    """Phân bố students theo performance"""
    struggling_students: int = Field(..., description="Students đang gặp khó khăn (>50% weak skills)")
    average_students: int = Field(..., description="Students trung bình")
    excelling_students: int = Field(..., description="Students xuất sắc (>70% strong skills)")
    percentages: dict = Field(..., description="Phần trăm từng category")


class CourseSkillGapsAnalyticsResponse(BaseModel):
    """Response cho GET /api/v1/analytics/course-skill-gaps/{course_id}"""
    course_id: str = Field(..., description="UUID course")
    total_students: int = Field(..., description="Tổng số students")
    skills_overview: SkillsOverview = Field(..., description="Tổng quan skills")
    student_distribution: StudentDistribution = Field(..., description="Phân bố students")
    skill_difficulty_ranking: List[SkillDifficultyItem] = Field(
        default_factory=list,
        description="Top 20 skills khó nhất"
    )
    message: Optional[str] = Field(None, description="Message nếu không có data")
    generated_at: datetime = Field(..., description="Thời gian generate")


# ============================================================================
# COMPARISON SCHEMAS
# ============================================================================

class SkillComparisonItem(BaseModel):
    """So sánh một skill với class average"""
    skill_tag: str = Field(..., description="Skill tag")
    user_proficiency: float = Field(..., description="Proficiency của user")
    class_average: float = Field(..., description="Proficiency trung bình của class")
    difference: float = Field(..., description="Chênh lệch (user - class)")
    percentile: int = Field(..., description="Percentile của user (0-100)")
    status: str = Field(..., description="above_average|below_average")


class OverallComparison(BaseModel):
    """So sánh tổng thể với class"""
    user_average: float = Field(..., description="Proficiency trung bình của user")
    class_average: float = Field(..., description="Proficiency trung bình của class")
    difference: float = Field(..., description="Chênh lệch")
    rank: int = Field(..., description="Xếp hạng trong class (1 = cao nhất)")
    total_students: int = Field(..., description="Tổng số students")


class StudentClassComparisonResponse(BaseModel):
    """Response cho GET /api/v1/analytics/compare-with-class"""
    user_id: str = Field(..., description="UUID user")
    course_id: str = Field(..., description="UUID course")
    comparison: List[SkillComparisonItem] = Field(
        default_factory=list,
        description="So sánh từng skill"
    )
    overall_comparison: OverallComparison = Field(..., description="So sánh tổng thể")
    message: Optional[str] = Field(None, description="Message nếu không có data")
    generated_at: datetime = Field(..., description="Thời gian generate")

