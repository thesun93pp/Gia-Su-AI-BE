"""
Recommendation Controller
Xử lý requests cho recommendation endpoints
Section 2.2.4, 2.7.4
"""

from typing import Dict
from fastapi import HTTPException, status

from schemas.recommendation import (
    AssessmentRecommendationResponse,
    RecommendationResponse
)
from services import recommendation_service
from models.models import Course


# ============================================================================
# Section 2.2.4: ĐỀ XUẤT KHÓA HỌC TỪ ASSESSMENT
# ============================================================================

async def handle_get_assessment_recommendations(
    assessment_session_id: str,
    current_user: Dict
) -> AssessmentRecommendationResponse:
    """
    2.2.4: Lấy đề xuất khóa học từ kết quả assessment
    
    Flow:
    1. Extract user_id từ current_user
    2. Tìm recommendation theo assessment_session_id
    3. Nếu không có, tạo recommendation mới
    4. Format response theo schema
    
    Args:
        assessment_session_id: ID của assessment session
        current_user: Dict chứa thông tin user từ JWT
        
    Returns:
        AssessmentRecommendationResponse với recommended courses, learning path
        
    Raises:
        HTTPException 404: Assessment không tồn tại
        HTTPException 500: Lỗi khi tạo recommendations
    """
    user_id = current_user.get("user_id")
    
    try:
        # Tìm recommendation hiện có
        recommendation = await recommendation_service.get_recommendation_by_assessment(
            user_id=user_id,
            assessment_session_id=assessment_session_id
        )
        
        # Nếu chưa có, tạo mới
        if not recommendation:
            recommendation = await recommendation_service.create_recommendation_from_assessment(
                user_id=user_id,
                assessment_session_id=assessment_session_id
            )
        
        # Format response
        recommended_courses = []
        for course_data in recommendation.recommended_courses:
            # Get full course info
            course = await Course.get(course_data["course_id"])
            if not course:
                continue
            
            recommended_courses.append({
                "course_id": course.id,
                "title": course.title,
                "description": course.description,
                "category": course.category,
                "level": course.level,
                "thumbnail_url": course.thumbnail_url,
                "priority_rank": course_data.get("priority_rank", 1),
                "relevance_score": course_data.get("relevance_score", 80.0),
                "reason": course_data.get("reason", "Phù hợp với kết quả đánh giá của bạn"),
                "addresses_gaps": course_data.get("addresses_gaps", []),
                "estimated_completion_days": course.estimated_duration_hours * 7 // 2 if course.estimated_duration_hours else 30
            })
        
        # Format learning path
        suggested_learning_order = []
        for idx, step in enumerate(recommendation.learning_path, start=1):
            suggested_learning_order.append({
                "step": idx,
                "course_id": step.get("course_id", ""),
                "focus_modules": step.get("focus_modules", []),
                "why_this_order": step.get("why_this_order", "")
            })
        
        # Practice exercises (giả sử có trong recommendation)
        practice_exercises = []
        if hasattr(recommendation, 'practice_exercises'):
            practice_exercises = recommendation.practice_exercises
        
        return AssessmentRecommendationResponse(
            assessment_session_id=assessment_session_id,
            user_proficiency_level=recommendation.proficiency_level if hasattr(recommendation, 'proficiency_level') else "Beginner",
            recommended_courses=recommended_courses,
            suggested_learning_order=suggested_learning_order,
            practice_exercises=practice_exercises,
            total_estimated_hours=sum(c["estimated_completion_days"] * 2 for c in recommended_courses),
            ai_personalized_advice=recommendation.ai_advice
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy đề xuất: {str(e)}"
        )


# ============================================================================
# Section 2.7.4: ĐỀ XUẤT KHÓA HỌC THÔNG MINH
# ============================================================================

async def handle_get_recommendations(current_user: Dict) -> RecommendationResponse:
    """
    2.7.4: Lấy đề xuất khóa học thông minh dựa trên lịch sử học tập
    
    Flow:
    1. Extract user_id từ current_user
    2. Tìm recommendation hiện có (chưa expired)
    3. Nếu không có, tạo mới từ learning history
    4. Return danh sách 5-10 courses với reasons
    
    Args:
        current_user: Dict chứa thông tin user từ JWT
        
    Returns:
        RecommendationResponse với recommended_courses
        
    Raises:
        HTTPException 500: Lỗi khi tạo recommendations
    """
    user_id = current_user.get("user_id")
    
    try:
        # Tìm recommendation mới nhất chưa expired
        recommendation = await recommendation_service.get_latest_recommendation(user_id)
        
        # Nếu không có hoặc đã expired, tạo mới
        if not recommendation:
            recommendation = await recommendation_service.create_recommendation_from_history(user_id)
        
        # Format response
        recommended_courses = []
        for course_data in recommendation.recommended_courses[:10]:  # Limit 10
            # Get full course info
            course = await Course.get(course_data["course_id"])
            if not course:
                continue
            
            recommended_courses.append({
                "course_id": course.id,
                "title": course.title,
                "reason": course_data.get("reason", "Phù hợp với sở thích và lịch sử học tập"),
                "relevance_score": course_data.get("relevance_score", 75.0)
            })
        
        return RecommendationResponse(
            recommended_courses=recommended_courses
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy đề xuất: {str(e)}"
        )
