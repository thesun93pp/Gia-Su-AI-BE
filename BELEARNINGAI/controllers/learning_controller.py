"""
Learning Controller - Xử lý requests module & lesson
Tuân thủ: CHUCNANG.md Section 2.4.1-2.4.2, ENDPOINTS.md learning_router

Controller này xử lý 6 endpoints:
- GET /courses/{course_id}/modules/{module_id} - Chi tiết module
- GET /courses/{course_id}/lessons/{lesson_id} - Nội dung lesson
- GET /courses/{course_id}/modules - Danh sách modules
- GET /courses/{course_id}/modules/{module_id}/outcomes - Learning outcomes
- GET /courses/{course_id}/modules/{module_id}/resources - Tài nguyên
- POST /courses/{course_id}/modules/{module_id}/assessments/generate - Sinh quiz module
"""

import logging
from typing import Dict, Optional
from fastapi import HTTPException, status
from datetime import datetime

# Import schemas
from schemas.learning import (
    ModuleDetailResponse,
    LessonContentResponse,
    CourseModulesResponse,
    ModuleOutcomesResponse,
    ModuleResourcesResponse,
    ModuleAssessmentGenerateRequest,
    ModuleAssessmentGenerateResponse
)

# Import models
from models.models import Quiz, generate_uuid

# Import services
from services import learning_service, enrollment_service, course_service
from services.ai_service import generate_module_quiz

# Setup logger
logger = logging.getLogger(__name__)


# ============================================================================
# Section 2.4.1: XEM THÔNG TIN MODULE
# ============================================================================

async def handle_get_module_detail(
    course_id: str,
    module_id: str,
    current_user: Dict
) -> ModuleDetailResponse:
    """
    2.4.1: Lấy thông tin chi tiết module
    
    Hiển thị:
    - Tiêu đề và mô tả module
    - Cấp độ khó (Basic/Intermediate/Advanced)
    - Danh sách lessons theo thứ tự
    - Mục tiêu học tập (Learning Outcomes)
    - Thời lượng học ước tính
    - Tài nguyên đính kèm
    - Trạng thái hoàn thành của từng lesson
    
    Args:
        course_id: ID của course
        module_id: ID của module
        current_user: User hiện tại
        
    Returns:
        ModuleDetailResponse
        
    Raises:
        404: Course hoặc module không tồn tại
        403: Chưa đăng ký course
        
    Endpoint: GET /api/v1/courses/{course_id}/modules/{module_id}
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra course tồn tại
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Kiểm tra user đã đăng ký course chưa
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học để xem module"
        )
    
    # Lấy module detail
    module_data = await learning_service.get_module_detail(
        course_id=course_id,
        module_id=module_id,
        user_id=user_id
    )
    
    if not module_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module không tồn tại"
        )
    
    return ModuleDetailResponse(**module_data)


# ============================================================================
# Section 2.4.2: XEM NỘI DUNG BÀI HỌC
# ============================================================================

async def handle_get_lesson_content(
    course_id: str,
    lesson_id: str,
    current_user: Dict
) -> LessonContentResponse:
    """
    2.4.2: Lấy nội dung chi tiết lesson
    
    Hiển thị:
    - Nội dung text/HTML
    - Video bài giảng (nếu có)
    - Tài liệu đính kèm
    - Tracking tự động: thời gian học, phần đã xem
    - Thông tin quiz kèm theo
    - Navigation (lesson trước/sau)
    
    Args:
        course_id: ID của course
        lesson_id: ID của lesson
        current_user: User hiện tại
        
    Returns:
        LessonContentResponse
        
    Raises:
        404: Course hoặc lesson không tồn tại
        403: Chưa đăng ký course hoặc lesson bị khóa
        
    Endpoint: GET /api/v1/courses/{course_id}/lessons/{lesson_id}
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
            detail="Bạn cần đăng ký khóa học để xem lesson"
        )
    
    # Lấy lesson content
    lesson_data = await learning_service.get_lesson_content(
        course_id=course_id,
        lesson_id=lesson_id,
        user_id=user_id
    )
    
    if not lesson_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson không tồn tại"
        )
    
    # Check if lesson is locked
    if lesson_data.get("is_next_locked") and not lesson_data.get("is_completed"):
        # Check nếu đây là lesson bị khóa do chưa hoàn thành trước đó
        # Logic đã xử lý trong service
        pass
    
    return LessonContentResponse(**lesson_data)


# ============================================================================
# ADDITIONAL ENDPOINTS (Notes trong ENDPOINTS.md)
# ============================================================================

async def handle_get_course_modules(
    course_id: str,
    current_user: Dict
) -> CourseModulesResponse:
    """
    Lấy danh sách tất cả modules trong course
    
    Args:
        course_id: ID của course
        current_user: User hiện tại
        
    Returns:
        CourseModulesResponse
        
    Endpoint: GET /api/v1/courses/{course_id}/modules
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
            detail="Bạn cần đăng ký khóa học"
        )
    
    # Lấy modules list
    modules_data = await learning_service.get_course_modules_list(
        course_id=course_id,
        user_id=user_id
    )
    
    if not modules_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy modules"
        )
    
    return CourseModulesResponse(**modules_data)


async def handle_get_module_outcomes(
    course_id: str,
    module_id: str,
    current_user: Dict
) -> ModuleOutcomesResponse:
    """
    Lấy learning outcomes của module
    
    Args:
        course_id: ID của course
        module_id: ID của module
        current_user: User hiện tại
        
    Returns:
        ModuleOutcomesResponse
        
    Endpoint: GET /api/v1/courses/{course_id}/modules/{module_id}/outcomes
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra enrollment
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học"
        )
    
    # Lấy outcomes
    outcomes_data = await learning_service.get_module_outcomes(
        course_id=course_id,
        module_id=module_id,
        user_id=user_id
    )
    
    if not outcomes_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module không tồn tại"
        )
    
    return ModuleOutcomesResponse(**outcomes_data)


async def handle_get_module_resources(
    course_id: str,
    module_id: str,
    current_user: Dict
) -> ModuleResourcesResponse:
    """
    Lấy tài nguyên học tập của module
    
    Args:
        course_id: ID của course
        module_id: ID của module
        current_user: User hiện tại
        
    Returns:
        ModuleResourcesResponse
        
    Endpoint: GET /api/v1/courses/{course_id}/modules/{module_id}/resources
    """
    user_id = current_user.get("user_id")
    
    # Kiểm tra enrollment
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học"
        )
    
    # Lấy resources
    resources_data = await learning_service.get_module_resources(
        course_id=course_id,
        module_id=module_id
    )
    
    if not resources_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module không tồn tại"
        )
    
    return ModuleResourcesResponse(**resources_data)


async def handle_generate_module_assessment(
    course_id: str,
    module_id: str,
    request: ModuleAssessmentGenerateRequest,
    current_user: Dict
) -> ModuleAssessmentGenerateResponse:
    """
    Sinh quiz đánh giá tự động cho module
    
    Sử dụng AI để sinh quiz dựa trên:
    - Learning outcomes của module
    - Độ khó yêu cầu
    - Số lượng câu hỏi
    
    Args:
        course_id: ID của course
        module_id: ID của module
        request: ModuleAssessmentGenerateRequest
        current_user: User hiện tại
        
    Returns:
        ModuleAssessmentGenerateResponse
        
    Endpoint: POST /api/v1/courses/{course_id}/modules/{module_id}/assessments/generate
    """
    user_id = current_user.get("user_id")
    
    logger.info(f"Generating module assessment - user: {user_id}, course: {course_id}, module: {module_id}")
    
    # Kiểm tra enrollment
    enrollment = await enrollment_service.get_user_enrollment(user_id, course_id)
    if not enrollment or enrollment.status == "cancelled":
        logger.warning(f"User {user_id} not enrolled in course {course_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn cần đăng ký khóa học"
        )
    
    # Lấy course
    course = await course_service.get_course_by_id(course_id)
    if not course:
        logger.error(f"Course not found: {course_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khóa học không tồn tại"
        )
    
    # Tìm module trong course
    module_data = None
    for m in course.get("modules", []):
        if m.get("id") == module_id:
            module_data = m
            break
    
    if not module_data:
        logger.error(f"Module not found: {module_id} in course {course_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module không tồn tại"
        )
    
    # Extract learning outcomes
    learning_outcomes = module_data.get("learning_outcomes", [])
    if not learning_outcomes:
        logger.warning(f"Module {module_id} has no learning outcomes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module không có learning outcomes để sinh quiz"
        )
    
    logger.info(f"Module has {len(learning_outcomes)} learning outcomes")
    
    # Generate quiz using AI
    try:
        ai_result = await generate_module_quiz(
            module_title=module_data.get("title", ""),
            module_description=module_data.get("description", ""),
            learning_outcomes=learning_outcomes,
            difficulty=request.difficulty,
            question_count=request.question_count,
            focus_outcomes=request.focus_outcomes
        )
        
        logger.info(f"AI quiz generated - {len(ai_result['questions'])} questions, {ai_result['total_points']} points")
    
    except ValueError as e:
        logger.error(f"AI quiz generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể sinh quiz: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in quiz generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi hệ thống khi sinh quiz"
        )
    
    # Create Quiz document in DB
    try:
        quiz = Quiz(
            id=generate_uuid(),
            lesson_id="module-assessment",  # Special marker for module-level quiz
            course_id=course_id,
            title=f"Quiz đánh giá - {module_data.get('title')}",
            description=f"Quiz tự động sinh bởi AI để đánh giá module {module_data.get('title')}",
            time_limit_minutes=ai_result["estimated_time_minutes"],
            passing_score=70.0,
            max_attempts=999,  # Unlimited retries
            deadline=None,
            is_draft=False,
            questions=ai_result["questions"],
            question_count=len(ai_result["questions"]),
            total_points=ai_result["total_points"],
            mandatory_question_count=ai_result["mandatory_count"],
            created_by=user_id
        )
        
        await quiz.insert()
        logger.info(f"Quiz created successfully - id: {quiz.id}")
    
    except Exception as e:
        logger.error(f"Failed to save quiz to DB: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lưu quiz vào database"
        )
    
    return ModuleAssessmentGenerateResponse(
        quiz_id=quiz.id,
        module_id=module_id,
        question_count=len(ai_result["questions"]),
        difficulty=request.difficulty,
        estimated_time_minutes=ai_result["estimated_time_minutes"],
        message=f"Quiz đánh giá cho module đã được tạo với {len(ai_result['questions'])} câu hỏi (trong đó {ai_result['mandatory_count']} câu bắt buộc)"
    )
