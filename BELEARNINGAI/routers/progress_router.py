"""
Progress Router
Định nghĩa routes cho progress tracking endpoints
Section 2.4.9 + Cumulative Weakness Tracking
"""

from fastapi import APIRouter, Depends, Query, status
from middleware.auth import get_current_user
from controllers.progress_controller import handle_get_course_progress
from schemas.progress import ProgressCourseResponse
from schemas.skill_tracking import (
    WeakSkillsSummaryResponse,
    SkillHistoryResponse,
    SkillsOverviewResponse
)


router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get(
    "/course/{course_id}",
    response_model=ProgressCourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem tiến độ học tập chi tiết",
    description="""
    Hiển thị tiến độ học tập theo course với thông tin:
    - Overall progress percent (0-100)
    - Chi tiết progress từng module và lesson
    - Thời gian học tổng (total_time_spent_minutes)
    - Thời gian ước tính còn lại (estimated_hours_remaining)
    - Streak days (học liên tục)
    - Điểm quiz trung bình (avg_quiz_score)
    """
)
async def get_course_progress(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Section 2.4.9 - Xem tiến độ học tập theo khóa học"""
    return await handle_get_course_progress(course_id, current_user)


# ============================================================================
# CUMULATIVE WEAKNESS TRACKING ENDPOINTS
# ============================================================================

@router.get(
    "/weak-skills/{course_id}",
    response_model=WeakSkillsSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy tổng hợp điểm yếu tích lũy",
    description="""
    Lấy danh sách skills yếu của user trong course, được track qua nhiều quiz attempts.

    **Features:**
    - Tự động track proficiency cho từng skill qua các quiz
    - Phát hiện điểm yếu kinh niên (chronic weakness)
    - Tính trend (improving/declining/stable/fluctuating)
    - Phân loại priority (urgent/high/medium/low)
    - Đề xuất lessons cần review

    **Query Parameters:**
    - `threshold`: Ngưỡng proficiency để coi là weak (default 60%)
    - `include_all`: True để lấy tất cả skills, False chỉ lấy weak skills
    """
)
async def get_weak_skills_summary(
    course_id: str,
    threshold: float = Query(60.0, ge=0, le=100, description="Ngưỡng proficiency để coi là weak"),
    include_all: bool = Query(False, description="Include tất cả skills hay chỉ weak skills"),
    current_user: dict = Depends(get_current_user)
):
    """Lấy tổng hợp điểm yếu tích lũy của user trong course"""
    from services.skill_tracking_service import get_weak_skills_summary

    user_id = current_user["user_id"]

    result = await get_weak_skills_summary(
        user_id=user_id,
        course_id=course_id,
        threshold=threshold,
        include_all=include_all
    )

    return result


@router.get(
    "/skill-history/{course_id}/{skill_tag}",
    response_model=SkillHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy lịch sử proficiency của một skill",
    description="""
    Xem chi tiết lịch sử proficiency của một skill cụ thể qua các quiz attempts.

    **Thông tin trả về:**
    - Current proficiency và trend
    - Lịch sử tất cả attempts (quiz nào, đúng bao nhiêu câu, sai câu nào)
    - Tốc độ cải thiện (improvement rate)
    - Priority level và consecutive fails
    """
)
async def get_skill_history(
    course_id: str,
    skill_tag: str,
    current_user: dict = Depends(get_current_user)
):
    """Lấy lịch sử proficiency của một skill cụ thể"""
    from services.skill_tracking_service import get_skill_history

    user_id = current_user["user_id"]

    result = await get_skill_history(
        user_id=user_id,
        course_id=course_id,
        skill_tag=skill_tag
    )

    return result


@router.get(
    "/skills-overview/{course_id}",
    response_model=SkillsOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy overview tất cả skills",
    description="""
    Xem tổng quan tất cả skills của user trong course, phân loại theo proficiency.

    **Phân loại:**
    - Strong skills: proficiency >= 80%
    - Average skills: 60% <= proficiency < 80%
    - Weak skills: proficiency < 60%

    **Thông tin trả về:**
    - Danh sách skills theo từng category
    - Overall proficiency trung bình
    - Số lượng skills trong mỗi category
    """
)
async def get_skills_overview(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Lấy overview tất cả skills của user trong course"""
    from services.skill_tracking_service import get_all_skills_overview

    user_id = current_user["user_id"]

    result = await get_all_skills_overview(
        user_id=user_id,
        course_id=course_id
    )

    return result
