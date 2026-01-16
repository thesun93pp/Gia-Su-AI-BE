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
from schemas.skill_gaps_dashboard import (
    SkillGapsDashboardResponse,
    CourseSkillGapsAnalyticsResponse,
    StudentClassComparisonResponse
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


# ============================================================================
# ANALYTICS & DASHBOARD ENDPOINTS
# ============================================================================

@router.get(
    "/dashboard/skill-gaps/{course_id}",
    response_model=SkillGapsDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Dashboard tổng quan skill gaps",
    description="""
    Dashboard trực quan về điểm mạnh/yếu của học viên:
    - Overview stats (total skills, weak/strong count, average proficiency)
    - Skill distribution (pie chart data)
    - Weakness heatmap (top 10 weakest skills)
    - Improvement trend (line chart - last 30 days)
    - Top weaknesses (detailed list)
    - Recent improvements

    Dùng để hiển thị dashboard với charts và visualizations.
    """
)
async def get_skill_gaps_dashboard(
    course_id: str,
    include_ai_insights: bool = Query(default=True, description="Include AI-generated insights"),
    current_user: dict = Depends(get_current_user)
):
    """Dashboard tổng quan về skill gaps của user"""
    from services.skill_gaps_analytics_service import get_skill_gaps_dashboard
    from services.ai_insights_service import generate_skill_gaps_insights

    user_id = current_user["user_id"]

    result = await get_skill_gaps_dashboard(
        user_id=user_id,
        course_id=course_id
    )

    # Add AI insights if requested
    if include_ai_insights and result.get("overview", {}).get("total_skills", 0) > 0:
        ai_insights = await generate_skill_gaps_insights(result)
        result["ai_insights"] = ai_insights

    return result


@router.get(
    "/analytics/course-skill-gaps/{course_id}",
    response_model=CourseSkillGapsAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Analytics skill gaps cho toàn course (instructor/admin)",
    description="""
    Analytics cho instructor/admin xem tổng quan skill gaps của tất cả students:
    - Total students
    - Student distribution (struggling/average/excelling)
    - Most common weaknesses
    - Skill difficulty ranking (hardest skills in course)

    Chỉ instructor/admin của course mới được xem.
    """
)
async def get_course_skill_gaps_analytics(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Analytics skill gaps cho toàn course (instructor/admin only)"""
    from services.skill_gaps_analytics_service import get_course_skill_gaps_analytics

    # TODO: Add permission check (instructor/admin only)
    # For now, allow all users

    result = await get_course_skill_gaps_analytics(course_id=course_id)

    return result


@router.get(
    "/analytics/compare-with-class/{course_id}",
    response_model=StudentClassComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="So sánh proficiency với class average",
    description="""
    So sánh proficiency của student với class average:
    - Comparison từng skill (user vs class average)
    - Overall comparison (rank, percentile)
    - Identify skills mà user yếu hơn class

    Giúp student biết mình đứng ở đâu so với các bạn khác.
    """
)
async def compare_with_class(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """So sánh proficiency của user với class average"""
    from services.skill_gaps_analytics_service import compare_student_with_class_average

    user_id = current_user["user_id"]

    result = await compare_student_with_class_average(
        user_id=user_id,
        course_id=course_id
    )

    return result

