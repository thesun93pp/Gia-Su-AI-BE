"""
Recommendation Service - Xử lý đề xuất khóa học
Sử dụng: Beanie ODM, Google Gemini (via ai_service)
Tuân thủ: CHUCNANG.md Section 2.2.4, 2.7.4
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from models.models import Recommendation, AssessmentSession, Enrollment, Course
from services.ai_service import generate_course_recommendations


# ============================================================================
# RECOMMENDATION CRUD
# ============================================================================

async def create_recommendation_from_assessment(
    user_id: str,
    assessment_session_id: str
) -> Recommendation:
    """
    Tạo đề xuất từ kết quả assessment
    
    Args:
        user_id: ID của user
        assessment_session_id: ID của assessment session
        
    Returns:
        Recommendation document đã tạo
    """
    # Lấy assessment results
    assessment = await AssessmentSession.get(assessment_session_id)
    
    if not assessment or assessment.status != "evaluated":
        raise ValueError("Assessment chưa được đánh giá")
    
    # Lấy lịch sử học tập
    enrollments = await Enrollment.find(
        Enrollment.user_id == user_id
    ).to_list()
    
    learning_history = [
        {
            "course_id": e.course_id,
            "progress_percent": e.progress_percent,
            "status": e.status
        }
        for e in enrollments
    ]
    
    # Lấy assessment results
    assessment_results = {
        "category": assessment.category,
        "subject": assessment.subject,
        "level": assessment.level,
        "overall_score": assessment.overall_score,
        "proficiency_level": assessment.proficiency_level,
        "knowledge_gaps": assessment.knowledge_gaps
    }
    
    # Generate recommendations sử dụng AI
    ai_recommendations = await generate_course_recommendations(
        user_learning_history=learning_history,
        assessment_results=assessment_results
    )
    
    # Lấy các courses phù hợp từ database
    recommended_courses = await _match_courses_to_recommendations(
        assessment.category,
        assessment.proficiency_level,
        assessment.knowledge_gaps
    )
    
    # Tạo recommendation
    recommendation = Recommendation(
        user_id=user_id,
        source="assessment",
        assessment_session_id=assessment_session_id,
        recommended_courses=recommended_courses,
        learning_path=ai_recommendations.get("learning_path", []),
        ai_advice=ai_recommendations.get("ai_advice", ""),
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    await recommendation.insert()
    return recommendation


async def create_recommendation_from_history(user_id: str) -> Recommendation:
    """
    Tạo đề xuất dựa trên lịch sử học tập
    
    Args:
        user_id: ID của user
        
    Returns:
        Recommendation document đã tạo
    """
    # Lấy lịch sử học tập
    enrollments = await Enrollment.find(
        Enrollment.user_id == user_id
    ).to_list()
    
    learning_history = []
    for e in enrollments:
        course = await Course.get(e.course_id)
        if course:
            learning_history.append({
                "course_id": e.course_id,
                "course_title": course.title,
                "category": course.category,
                "level": course.level,
                "progress_percent": e.progress_percent,
                "status": e.status
            })
    
    # Generate recommendations
    ai_recommendations = await generate_course_recommendations(
        user_learning_history=learning_history
    )
    
    # Lấy courses từ các categories user đã học
    categories = list(set(h["category"] for h in learning_history))
    recommended_courses = []
    
    for category in categories:
        courses = await Course.find(
            Course.category == category,
            Course.status == "published"
        ).limit(5).to_list()
        
        for course in courses:
            # Kiểm tra chưa enroll
            enrolled = any(h["course_id"] == course.id for h in learning_history)
            if not enrolled:
                recommended_courses.append({
                    "course_id": course.id,
                    "title": course.title,
                    "category": course.category,
                    "level": course.level,
                    "reason": f"Dựa trên kinh nghiệm học {category}",
                    "priority": 1
                })
    
    recommendation = Recommendation(
        user_id=user_id,
        source="learning_history",
        recommended_courses=recommended_courses[:10],
        learning_path=ai_recommendations.get("learning_path", []),
        ai_advice=ai_recommendations.get("ai_advice", ""),
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    await recommendation.insert()
    return recommendation


async def get_recommendation_by_id(recommendation_id: str) -> Optional[Recommendation]:
    """
    Lấy recommendation theo ID
    
    Args:
        recommendation_id: ID của recommendation
        
    Returns:
        Recommendation document hoặc None
    """
    try:
        recommendation = await Recommendation.get(recommendation_id)
        return recommendation
    except Exception:
        return None


async def get_user_recommendations(
    user_id: str,
    skip: int = 0,
    limit: int = 50
) -> List[Recommendation]:
    """
    Lấy danh sách recommendations của user
    
    Args:
        user_id: ID của user
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Recommendation documents
    """
    recommendations = await Recommendation.find(
        Recommendation.user_id == user_id
    ).skip(skip).limit(limit).to_list()
    
    return recommendations


async def get_active_recommendation(user_id: str) -> Optional[Recommendation]:
    """
    Lấy recommendation active gần nhất (chưa expired)
    
    Args:
        user_id: ID của user
        
    Returns:
        Recommendation document hoặc None
    """
    now = datetime.utcnow()
    
    recommendation = await Recommendation.find_one(
        Recommendation.user_id == user_id,
        Recommendation.expires_at > now
    )
    
    return recommendation


async def delete_recommendation(recommendation_id: str) -> bool:
    """
    Xóa recommendation
    
    Args:
        recommendation_id: ID của recommendation
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    recommendation = await get_recommendation_by_id(recommendation_id)
    
    if not recommendation:
        return False
    
    await recommendation.delete()
    return True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _match_courses_to_recommendations(
    category: str,
    proficiency_level: str,
    knowledge_gaps: List[Dict]
) -> List[Dict]:
    """
    Tìm courses phù hợp với knowledge gaps
    
    Args:
        category: Danh mục
        proficiency_level: Mức độ năng lực hiện tại
        knowledge_gaps: Các khoảng trống kiến thức
        
    Returns:
        List dict chứa course recommendations
    """
    # Map proficiency level sang course level
    level_map = {
        "Beginner": ["Beginner", "Intermediate"],
        "Intermediate": ["Intermediate", "Advanced"],
        "Advanced": ["Advanced"]
    }
    
    target_levels = level_map.get(proficiency_level, ["Beginner"])
    
    # Tìm courses
    courses = await Course.find(
        Course.category == category,
        Course.status == "published"
    ).to_list()
    
    # Filter theo level
    filtered = [c for c in courses if c.level in target_levels]
    
    # Tạo recommendations
    recommendations = []
    for i, course in enumerate(filtered[:10]):
        # Tìm knowledge gap liên quan
        related_gap = None
        for gap in knowledge_gaps:
            if gap.get("topic", "").lower() in course.title.lower():
                related_gap = gap
                break
        
        reason = "Khóa học phù hợp với trình độ hiện tại"
        if related_gap:
            reason = f"Giúp bổ sung kiến thức về {related_gap.get('topic')}"
        
        recommendations.append({
            "course_id": course.id,
            "title": course.title,
            "category": course.category,
            "level": course.level,
            "reason": reason,
            "priority": i + 1
        })
    
    return recommendations
