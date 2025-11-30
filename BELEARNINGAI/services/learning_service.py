"""
Learning Service - Xử lý module & lesson content
Sử dụng: Beanie ODM, MongoDB
Tuân thủ: CHUCNANG.md Section 2.4.1-2.4.2, ENDPOINTS.md learning_router
"""

from datetime import datetime
from typing import Optional, List, Dict
from models.models import Course, Module, Lesson, Enrollment, Progress, Quiz


# ============================================================================
# MODULE OPERATIONS
# ============================================================================

async def get_module_detail(
    course_id: str,
    module_id: str,
    user_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Lấy thông tin chi tiết module
    Section 2.4.1
    
    Args:
        course_id: ID của course
        module_id: ID của module
        user_id: ID của user hiện tại (để tính progress)
        
    Returns:
        Dict chứa module detail hoặc None
    """
    # Lấy course
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    # Tìm module trong course
    module = None
    for m in course.modules:
        if m.id == module_id:
            module = m
            break
    
    if not module:
        return None
    
    # Tính progress của user (nếu có)
    completion_status = "not-started"
    completed_lessons_count = 0
    progress_percent = 0.0
    
    if user_id:
        # Lấy enrollment và progress
        from services.enrollment_service import get_user_enrollment
        enrollment = await get_user_enrollment(user_id, course_id)
        
        if enrollment:
            # Đếm số lessons đã hoàn thành trong module này
            completed_in_module = [
                lesson_id for lesson_id in enrollment.completed_lessons
                if any(lesson.id == lesson_id for lesson in module.lessons)
            ]
            completed_lessons_count = len(completed_in_module)
            
            total_lessons = len(module.lessons)
            if total_lessons > 0:
                progress_percent = (completed_lessons_count / total_lessons * 100)
            
            # Xác định completion_status
            if progress_percent == 100:
                completion_status = "completed"
            elif progress_percent > 0:
                completion_status = "in-progress"
    
    # Build response
    result = {
        "id": module.id,
        "title": module.title,
        "description": module.description,
        "difficulty": module.difficulty,
        "order": module.order,
        "lessons": [],
        "learning_outcomes": module.learning_outcomes,
        "estimated_hours": module.estimated_hours,
        "resources": module.resources if hasattr(module, 'resources') else [],  # Resources từ module schema
        "completion_status": completion_status,
        "completed_lessons_count": completed_lessons_count,
        "total_lessons_count": len(module.lessons),
        "progress_percent": progress_percent,
        "prerequisites": module.prerequisites if hasattr(module, 'prerequisites') else []  # Prerequisites từ module schema
    }
    
    # Build lessons list với completion status
    for lesson in module.lessons:
        is_completed = False
        is_locked = False
        
        if user_id:
            from services.enrollment_service import get_user_enrollment
            enrollment = await get_user_enrollment(user_id, course_id)
            if enrollment:
                is_completed = lesson.id in enrollment.completed_lessons
                
                # Check if locked (previous lesson not completed)
                if lesson.order > 1:
                    prev_lesson = next(
                        (l for l in module.lessons if l.order == lesson.order - 1),
                        None
                    )
                    if prev_lesson and prev_lesson.id not in enrollment.completed_lessons:
                        is_locked = True
        
        result["lessons"].append({
            "id": lesson.id,
            "title": lesson.title,
            "order": lesson.order,
            "duration_minutes": lesson.duration_minutes,
            "content_type": lesson.content_type,
            "is_completed": is_completed,
            "is_locked": is_locked
        })
    
    return result


async def get_lesson_content(
    course_id: str,
    lesson_id: str,
    user_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Lấy nội dung chi tiết của lesson
    Section 2.4.2
    
    Args:
        course_id: ID của course
        lesson_id: ID của lesson
        user_id: ID của user hiện tại
        
    Returns:
        Dict chứa lesson content hoặc None
    """
    # Lấy course
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    # Tìm lesson và module chứa lesson
    lesson = None
    module = None
    
    for m in course.modules:
        for l in m.lessons:
            if l.id == lesson_id:
                lesson = l
                module = m
                break
        if lesson:
            break
    
    if not lesson or not module:
        return None
    
    # Tìm lesson trước và sau
    previous_lesson_id = None
    next_lesson_id = None
    
    lessons_in_module = sorted(module.lessons, key=lambda x: x.order)
    for i, l in enumerate(lessons_in_module):
        if l.id == lesson_id:
            if i > 0:
                previous_lesson_id = lessons_in_module[i-1].id
            if i < len(lessons_in_module) - 1:
                next_lesson_id = lessons_in_module[i+1].id
            break
    
    # Tracking info của user
    is_completed = False
    last_accessed_at = None
    time_spent_seconds = 0
    video_progress_seconds = 0
    quiz_passed = False
    is_next_locked = False
    
    if user_id:
        # Lấy enrollment và progress
        from services.enrollment_service import get_user_enrollment
        enrollment = await get_user_enrollment(user_id, course_id)
        
        if enrollment:
            is_completed = lesson_id in enrollment.completed_lessons
            last_accessed_at = enrollment.last_accessed_at
            
            # Lấy progress detail
            progress = await Progress.find_one(
                Progress.user_id == user_id,
                Progress.course_id == course_id
            )
            
            if progress:
                # Tìm lesson progress
                for lp in progress.lessons_progress:
                    if lp.get("lesson_id") == lesson_id:
                        time_spent_seconds = lp.get("time_spent_seconds", 0)
                        video_progress_seconds = lp.get("video_progress_seconds", 0)
                        break
            
            # Check quiz status
            quiz = await Quiz.find_one(Quiz.lesson_id == lesson_id)
            if quiz:
                from services.quiz_service import get_user_quiz_attempts
                attempts = await get_user_quiz_attempts(user_id, quiz.id)
                if attempts:
                    # Check if passed any attempt
                    quiz_passed = any(attempt.passed for attempt in attempts)
            
            # Check if next lesson is locked
            if next_lesson_id and next_lesson_id not in enrollment.completed_lessons:
                # Next lesson locked if current not completed
                is_next_locked = not is_completed
    
    # Lấy quiz_id nếu có
    quiz = await Quiz.find_one(Quiz.lesson_id == lesson_id)
    quiz_id = quiz.id if quiz else None
    quiz_required = True  # Default, có thể config từ lesson/course settings
    
    # Parse attachments từ resources
    attachments = []
    for resource in lesson.resources:
        attachments.append({
            "id": resource.get("id", ""),
            "filename": resource.get("filename", ""),
            "file_type": resource.get("type", "other"),
            "url": resource.get("url", ""),
            "size_mb": resource.get("size_mb", 0)
        })
    
    # Parse video info
    video_info = None
    if lesson.video_url:
        video_info = {
            "url": lesson.video_url,
            "duration_seconds": lesson.duration_minutes * 60,
            "quality": ["360p", "720p", "1080p"]
        }
    
    # Build message
    message = None
    if not is_completed and quiz_required:
        message = "Bạn cần hoàn thành quiz để mở lesson tiếp theo"
    elif is_completed:
        message = "Bạn đã hoàn thành lesson này"
    
    result = {
        "id": lesson.id,
        "title": lesson.title,
        "module_id": module.id,
        "module_title": module.title,
        "order": lesson.order,
        "duration_minutes": lesson.duration_minutes,
        "content_type": lesson.content_type,
        "text_content": lesson.content,
        "video_info": video_info,
        "attachments": attachments,
        "previous_lesson_id": previous_lesson_id,
        "next_lesson_id": next_lesson_id,
        "is_next_locked": is_next_locked,
        "is_completed": is_completed,
        "last_accessed_at": last_accessed_at,
        "time_spent_seconds": time_spent_seconds,
        "video_progress_seconds": video_progress_seconds,
        "quiz_id": quiz_id,
        "quiz_passed": quiz_passed,
        "quiz_required": quiz_required,
        "message": message
    }
    
    # Update last_accessed_at
    if user_id:
        from services.enrollment_service import get_user_enrollment
        enrollment = await get_user_enrollment(user_id, course_id)
        if enrollment:
            enrollment.last_accessed_at = datetime.utcnow()
            await enrollment.save()
    
    return result


async def get_course_modules_list(
    course_id: str,
    user_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Lấy danh sách tất cả modules trong course
    
    Args:
        course_id: ID của course
        user_id: ID của user hiện tại
        
    Returns:
        Dict chứa modules list
    """
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return {
            "course_id": course.id,
            "course_title": course.title,
            "modules": [],
            "total_modules": 0,
            "completed_modules": 0
        }
    
    # Get enrollment nếu có user
    enrollment = None
    if user_id:
        from services.enrollment_service import get_user_enrollment
        enrollment = await get_user_enrollment(user_id, course_id)
    
    modules_list = []
    completed_modules = 0
    
    for module in course.modules:
        # Tính progress cho module
        progress_percent = 0.0
        is_locked = False
        
        if enrollment:
            # Đếm lessons completed trong module
            completed_in_module = [
                lesson_id for lesson_id in enrollment.completed_lessons
                if any(lesson.id == lesson_id for lesson in module.lessons)
            ]
            
            total_lessons = len(module.lessons)
            if total_lessons > 0:
                progress_percent = (len(completed_in_module) / total_lessons * 100)
            
            if progress_percent == 100:
                completed_modules += 1
            
            # Check if locked (previous module not completed)
            if module.order > 1:
                prev_module = next(
                    (m for m in course.modules if m.order == module.order - 1),
                    None
                )
                if prev_module:
                    # Check if prev module completed
                    prev_completed = [
                        lesson_id for lesson_id in enrollment.completed_lessons
                        if any(lesson.id == lesson_id for lesson in prev_module.lessons)
                    ]
                    if len(prev_completed) < len(prev_module.lessons):
                        is_locked = True
        
        modules_list.append({
            "id": module.id,
            "title": module.title,
            "difficulty": module.difficulty,
            "order": module.order,
            "lesson_count": len(module.lessons),
            "estimated_hours": module.estimated_hours,
            "progress_percent": progress_percent,
            "is_locked": is_locked
        })
    
    return {
        "course_id": course.id,
        "course_title": course.title,
        "modules": modules_list,
        "total_modules": len(course.modules),
        "completed_modules": completed_modules
    }


async def get_module_outcomes(
    course_id: str,
    module_id: str,
    user_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Lấy learning outcomes của module với trạng thái achieved
    
    Args:
        course_id: ID của course
        module_id: ID của module
        user_id: ID của user
        
    Returns:
        Dict chứa outcomes với achieved status
    """
    import logging
    from models.models import Progress
    
    logger = logging.getLogger(__name__)
    
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    module = None
    for m in course.modules:
        if m.id == module_id:
            module = m
            break
    
    if not module:
        return None
    
    # Tính achieved outcomes từ Progress
    achieved_outcomes_count = 0
    
    return {
        "module_id": module.id,
        "module_title": module.title,
        "learning_outcomes": module.learning_outcomes,
        "total_outcomes": len(module.learning_outcomes),
        "achieved_outcomes": achieved_outcomes_count
    }


async def get_module_resources(
    course_id: str,
    module_id: str
) -> Optional[Dict]:
    """
    Lấy tài nguyên học tập của module
    
    Args:
        course_id: ID của course
        module_id: ID của module
        
    Returns:
        Dict chứa resources
    """
    course = await Course.get(course_id)
    if not course:
        return None
    
    # Check if course has modules
    if not hasattr(course, 'modules') or not course.modules:
        return None
    
    module = None
    for m in course.modules:
        if m.id == module_id:
            module = m
            break
    
    if not module:
        return None
    
    # Collect resources từ tất cả lessons trong module
    resources = []
    resources_by_type = {}
    
    for lesson in module.lessons:
        for resource in lesson.resources:
            resource_type = resource.get("type", "other")
            resources.append(resource)
            
            resources_by_type[resource_type] = resources_by_type.get(resource_type, 0) + 1
    
    return {
        "module_id": module.id,
        "module_title": module.title,
        "resources": resources,
        "total_resources": len(resources),
        "resources_by_type": resources_by_type
    }
