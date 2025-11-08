"""
Progress Controller - Xử lý requests progress tracking
Tuân thủ: CHUCNANG.md Section 2.4.9, ENDPOINTS.md progress_router

Controller này xử lý 1 endpoint:
- GET /progress/course/{id} - Xem tiến độ học tập
"""

from typing import Dict
from fastapi import HTTPException, status

# Import schemas
from schemas.progress import ProgressCourseResponse

# Import services
from services import enrollment_service, course_service
from models.models import Progress


# ============================================================================
# Section 2.4.9: THEO DÕI TIẾN ĐỘ HỌC TẬP
# ============================================================================

async def handle_get_course_progress(
    course_id: str,
    current_user: Dict
) -> ProgressCourseResponse:
    """
    2.4.9: Xem tiến độ học tập chi tiết của course
    
    Hiển thị:
    - Overall progress percent (0-100)
    - Chi tiết progress từng module
    - Chi tiết progress từng lesson trong module
    - Thời gian học tổng (total_time_spent_minutes)
    - Thời gian ước tính còn lại (estimated_hours_remaining)
    - Streak days (học liên tục bao nhiêu ngày)
    - Average quiz score
    
    Args:
        course_id: ID của course
        current_user: User hiện tại
        
    Returns:
        ProgressCourseResponse
        
    Raises:
        404: Course không tồn tại
        403: Chưa đăng ký course
        
    Endpoint: GET /api/v1/progress/course/{id}
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra course tồn tại
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra enrollment
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học để xem tiến độ"
        )
    
    # Lấy progress record
    progress = await Progress.find_one(
        Progress.user_id == user_id,
        Progress.course_id == course_id
    )
    
    if not progress:
        # Nếu chưa có progress, tạo mới
        progress = Progress(
            user_id=user_id,
            course_id=course_id,
            overall_progress_percent=0.0,
            modules=[],
            total_time_spent_minutes=0,
            last_activity_date=None
        )
        await progress.insert()
    
    # Tính toán modules progress
    modules_progress = []
    total_modules = len(course.modules) if hasattr(course, 'modules') else 0
    completed_modules = 0
    
    for module in (course.modules or []):
        # Count lessons in module
        total_lessons = len(module.lessons) if hasattr(module, 'lessons') else 0
        completed_lessons = 0
        
        lessons_progress = []
        for lesson in (module.lessons or []):
            # Check if lesson completed
            is_completed = lesson.id in (enrollment.completed_lessons or [])
            if is_completed:
                completed_lessons += 1
            
            # Find lesson progress for time tracking
            lesson_prog = next(
                (lp for lp in (progress.lessons_progress or []) if lp.lesson_id == lesson.id),
                None
            )
            
            lessons_progress.append({
                "lesson_id": lesson.id,
                "lesson_title": lesson.title,
                "status": "completed" if is_completed else "not-started",
                "time_spent_minutes": lesson_prog.time_spent_minutes if lesson_prog else 0,
                "video_progress_seconds": lesson_prog.video_progress_seconds if lesson_prog else 0
            })
        
        # Calculate module progress
        module_progress_percent = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0
        if module_progress_percent == 100:
            completed_modules += 1
        
        modules_progress.append({
            "module_id": module.id,
            "module_title": module.title,
            "progress_percent": module_progress_percent,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "lessons": lessons_progress
        })
    
    # Calculate overall progress
    overall_progress = (completed_modules / total_modules * 100) if total_modules > 0 else 0.0
    
    # Update progress record
    progress.overall_progress_percent = overall_progress
    progress.modules = modules_progress
    await progress.save()
    
    # Calculate estimated hours remaining
    total_duration = sum(
        module.estimated_hours for module in (course.modules or [])
        if hasattr(module, 'estimated_hours')
    )
    completed_duration = total_duration * (overall_progress / 100)
    estimated_hours_remaining = max(0, total_duration - completed_duration)
    
    # Calculate study streak (TODO: implement proper logic)
    study_streak_days = 0  # Placeholder
    
    # Calculate average quiz score (TODO: implement)
    avg_quiz_score = 0.0  # Placeholder
    
    return ProgressCourseResponse(
        course_id=course_id,
        course_title=course.title,
        overall_progress_percent=overall_progress,
        total_time_spent_minutes=progress.total_time_spent_minutes,
        estimated_hours_remaining=estimated_hours_remaining,
        study_streak_days=study_streak_days,
        avg_quiz_score=avg_quiz_score,
        completed_modules=completed_modules,
        total_modules=total_modules,
        modules=modules_progress,
        last_activity_date=progress.last_activity_date
    )
