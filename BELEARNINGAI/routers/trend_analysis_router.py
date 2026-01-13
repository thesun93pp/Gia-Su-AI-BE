"""
Trend Analysis Router
Định nghĩa routes cho trend analysis và intervention endpoints
"""

from fastapi import APIRouter, Depends, Query, status
from middleware.auth import get_current_user
from schemas.trend_analysis import (
    TrendAnalysisResponse,
    TrendAnalysisRequest,
    InterventionPlan,
    InterventionTriggerResponse,
    InterventionCheckRequest,
    CourseTrendAnalysisResponse,
    BatchInterventionResponse
)


router = APIRouter(prefix="/analytics/trends", tags=["Trend Analysis"])


# ============================================================================
# STUDENT TREND ANALYSIS
# ============================================================================

@router.get(
    "/{course_id}",
    response_model=TrendAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Phân tích xu hướng học tập của student",
    description="""
    Phân tích xu hướng học tập trong time window:
    
    **Overall Trend:**
    - Direction: improving/declining/stable/fluctuating
    - Velocity: % change per day
    - Confidence level (0-1)
    - Prediction for next week
    
    **Skill Trends:**
    - Trend per skill (improving/declining/stable)
    - Current proficiency và predicted proficiency
    - Risk level (high/medium/low/none)
    
    **Engagement Trend:**
    - Sessions và quiz attempts per week
    - Last activity timestamp
    - Days since last activity
    
    **Intervention Alerts:**
    - Automatic alerts nếu phát hiện xu hướng xấu
    - Recommended actions
    - Escalation to instructor nếu cần
    """
)
async def get_student_trends(
    course_id: str,
    time_window_days: int = Query(
        default=30,
        ge=7,
        le=90,
        description="Time window in days (7-90)"
    ),
    current_user: dict = Depends(get_current_user)
):
    """Phân tích xu hướng học tập của student"""
    from services.trend_analysis_service import analyze_student_trends
    
    user_id = current_user["user_id"]
    
    result = await analyze_student_trends(
        user_id=user_id,
        course_id=course_id,
        time_window_days=time_window_days
    )
    
    return result


@router.get(
    "/intervention-plan/{course_id}",
    response_model=InterventionPlan,
    status_code=status.HTTP_200_OK,
    summary="Lấy intervention plan chi tiết",
    description="""
    Generate intervention plan dựa trên trend analysis:
    
    - Priority level (urgent/high/medium/low)
    - Timeline (immediate/this_week/this_month)
    - Step-by-step action plan
    - Success metrics để đo lường cải thiện
    
    Dùng để hướng dẫn student cách cải thiện khi có xu hướng xấu.
    """
)
async def get_intervention_plan(
    course_id: str,
    time_window_days: int = Query(default=30, ge=7, le=90),
    current_user: dict = Depends(get_current_user)
):
    """Generate intervention plan cho student"""
    from services.trend_analysis_service import analyze_student_trends
    from services.intervention_service import generate_intervention_plan
    
    user_id = current_user["user_id"]
    
    # Analyze trends first
    trend_analysis = await analyze_student_trends(
        user_id=user_id,
        course_id=course_id,
        time_window_days=time_window_days
    )
    
    # Generate intervention plan
    plan = generate_intervention_plan(trend_analysis)
    
    return plan


@router.post(
    "/check-intervention/{course_id}",
    response_model=InterventionTriggerResponse,
    status_code=status.HTTP_200_OK,
    summary="Kiểm tra và trigger interventions",
    description="""
    Kiểm tra xem có cần can thiệp không và trigger alerts:
    
    - Analyze trends
    - Trigger alerts nếu cần
    - Send notifications to student
    - Escalate to instructor nếu urgent
    
    Endpoint này có thể được gọi:
    - Manually bởi student/instructor
    - Automatically bởi scheduled jobs
    """
)
async def check_intervention(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Kiểm tra và trigger interventions nếu cần"""
    from services.intervention_service import check_and_trigger_interventions
    
    user_id = current_user["user_id"]
    
    result = await check_and_trigger_interventions(
        user_id=user_id,
        course_id=course_id
    )
    
    return result


# ============================================================================
# INSTRUCTOR/ADMIN TREND ANALYSIS
# ============================================================================

@router.get(
    "/course/{course_id}",
    response_model=CourseTrendAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Phân tích xu hướng toàn course (Instructor/Admin)",
    description="""
    Phân tích xu hướng của tất cả students trong course:

    **Students at Risk:**
    - List students có xu hướng declining
    - Risk level (high/medium/low)
    - Number of declining skills
    - Overall velocity

    **Course-wide Trends:**
    - Number of improving/declining/stable students
    - Percentages

    **Intervention Summary:**
    - Urgent interventions needed
    - High/medium priority interventions
    - Total students at risk

    Chỉ instructor/admin của course mới được xem.
    """
)
async def get_course_trends(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Phân tích xu hướng toàn course (instructor/admin only)"""
    from services.trend_analysis_service import analyze_course_trends
    from models.models import Course
    from fastapi import HTTPException

    # Check permission
    course = await Course.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    user_id = current_user["user_id"]
    user_role = current_user.get("role", "student")

    # Only instructor/admin can view course trends
    if user_role not in ["instructor", "admin"] and course.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructor/admin can view course trends"
        )

    result = await analyze_course_trends(course_id)

    return result


@router.post(
    "/batch-intervention/{course_id}",
    response_model=BatchInterventionResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch intervention check cho toàn course (Instructor/Admin)",
    description="""
    Run intervention check cho tất cả students at risk trong course:

    - Identify students at risk
    - Trigger interventions for each
    - Send notifications
    - Create escalations

    Dùng cho:
    - Scheduled jobs (daily/weekly checks)
    - Manual trigger by instructor

    Chỉ instructor/admin của course mới được trigger.
    """
)
async def batch_intervention_check(
    course_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Batch intervention check cho toàn course (instructor/admin only)"""
    from services.intervention_service import run_batch_intervention_check
    from models.models import Course
    from fastapi import HTTPException

    # Check permission
    course = await Course.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    user_id = current_user["user_id"]
    user_role = current_user.get("role", "student")

    # Only instructor/admin can trigger batch intervention
    if user_role not in ["instructor", "admin"] and course.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructor/admin can trigger batch intervention"
        )

    result = await run_batch_intervention_check(course_id)

    return result


