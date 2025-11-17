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
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Creating recommendation from assessment - user: {user_id}, session: {assessment_session_id}")
    
    # Lấy assessment results
    assessment = await AssessmentSession.get(assessment_session_id)
    
    if not assessment:
        logger.error(f"Assessment session not found: {assessment_session_id}")
        raise ValueError("Assessment session không tồn tại")
    
    if assessment.status != "evaluated":
        logger.warning(f"Assessment not evaluated yet - session: {assessment_session_id}, status: {assessment.status}")
        raise ValueError("Assessment chưa được đánh giá")
    
    logger.info(f"Assessment found - category: {assessment.category}, level: {assessment.level}, score: {assessment.overall_score}")
    
    # Lấy lịch sử học tập
    enrollments = await Enrollment.find(
        Enrollment.user_id == user_id
    ).to_list()
    
    logger.info(f"Found {len(enrollments)} enrollments for user {user_id}")
    
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
    
    # Lấy available courses từ database TRƯỚC KHI gọi AI
    try:
        logger.info(f"Fetching available courses - category: {assessment.category}")
        available_courses = await _get_available_courses(
            category=assessment.category,
            proficiency_level=assessment.proficiency_level,
            limit=15
        )
        logger.info(f"Found {len(available_courses)} available courses to send to AI")
    except Exception as e:
        logger.error(f"Failed to fetch available courses: {str(e)}", exc_info=True)
        available_courses = []
    
    # Generate recommendations sử dụng AI với available courses
    try:
        logger.info("Generating AI recommendations with course context...")
        ai_recommendations = await generate_course_recommendations(
            user_learning_history=learning_history,
            assessment_results=assessment_results,
            available_courses=available_courses  # CRITICAL: Pass courses to AI
        )
        logger.info(f"AI recommendations generated - {len(ai_recommendations.get('recommended_courses', []))} courses")
    except Exception as e:
        logger.error(f"AI recommendation generation failed: {str(e)}", exc_info=True)
        ai_recommendations = {"recommended_courses": [], "learning_path": [], "ai_advice": "Không thể tạo lời khuyên từ AI"}
    
    # Build final recommended_courses list từ AI response + course details
    recommended_courses = []
    ai_course_recs = ai_recommendations.get("recommended_courses", [])
    
    for idx, rec in enumerate(ai_course_recs):
        course_id = rec.get("course_id")
        if not course_id:
            continue
        
        # Find course from available_courses
        course = next((c for c in available_courses if str(c.id) == str(course_id)), None)
        if not course:
            logger.warning(f"AI recommended course_id {course_id} not found in available courses")
            continue
        
        recommended_courses.append({
            "course_id": course.id,
            "title": course.title,
            "category": course.category,
            "level": course.level,
            "reason": rec.get("reason", "Khóa học phù hợp với trình độ"),
            "priority": rec.get("priority", idx + 1),
            "relevance_score": 85.0,  # Default score
            "addresses_gaps": []  # Filled from knowledge_gaps matching
        })
    
    # Fallback: Nếu AI không trả về courses, dùng matching logic cũ
    if not recommended_courses and available_courses:
        logger.info("AI returned no courses, using fallback matching...")
        recommended_courses = await _match_courses_to_recommendations(
            assessment.category,
            assessment.proficiency_level,
            assessment.knowledge_gaps,
            available_courses[:10]
        )
    
    logger.info(f"Final recommended courses count: {len(recommended_courses)}")
    
    # Tạo recommendation với field names đúng theo model
    recommendation = Recommendation(
        user_id=user_id,
        source="assessment",
        assessment_session_id=assessment_session_id,
        user_proficiency_level=assessment.proficiency_level or "Beginner",
        recommended_courses=recommended_courses,
        suggested_learning_order=ai_recommendations.get("learning_path", []),  # Fixed field name
        ai_personalized_advice=ai_recommendations.get("ai_advice", ""),  # Fixed field name
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    await recommendation.insert()
    logger.info(f"Recommendation created successfully - id: {recommendation.id}")
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
    
    # Lấy categories user đã học để fetch available courses
    categories = list(set(h["category"] for h in learning_history))
    primary_category = categories[0] if categories else "General"
    
    # Lấy available courses từ DB
    available_courses = await _get_available_courses(
        category=primary_category,
        proficiency_level="Intermediate",  # Default for history-based
        limit=15
    )
    
    # Generate recommendations với available courses
    ai_recommendations = await generate_course_recommendations(
        user_learning_history=learning_history,
        available_courses=available_courses
    )
    
    # Build recommended_courses từ AI response
    recommended_courses = []
    ai_course_recs = ai_recommendations.get("recommended_courses", [])
    
    for idx, rec in enumerate(ai_course_recs):
        course_id = rec.get("course_id")
        if not course_id:
            continue
        
        course = next((c for c in available_courses if str(c.id) == str(course_id)), None)
        if not course:
            continue
        
        # Check chưa enroll
        enrolled = any(h["course_id"] == str(course.id) for h in learning_history)
        if not enrolled:
            recommended_courses.append({
                "course_id": course.id,
                "title": course.title,
                "category": course.category,
                "level": course.level,
                "reason": rec.get("reason", f"Dựa trên kinh nghiệm học {course.category}"),
                "priority": idx + 1,
                "relevance_score": 80.0,
                "addresses_gaps": []
            })
    
    # Fallback: Nếu AI không trả về courses
    if not recommended_courses:
        for course in available_courses[:10]:
            enrolled = any(h["course_id"] == str(course.id) for h in learning_history)
            if not enrolled:
                recommended_courses.append({
                    "course_id": course.id,
                    "title": course.title,
                    "category": course.category,
                    "level": course.level,
                    "reason": f"Dựa trên kinh nghiệm học {course.category}",
                    "priority": len(recommended_courses) + 1,
                    "relevance_score": 70.0,
                    "addresses_gaps": []
                })
    
    recommendation = Recommendation(
        user_id=user_id,
        source="learning_history",
        recommended_courses=recommended_courses[:10],
        suggested_learning_order=ai_recommendations.get("learning_path", []),  # Fixed field name
        ai_personalized_advice=ai_recommendations.get("ai_advice", ""),  # Fixed field name
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


async def get_recommendation_by_assessment(
    user_id: str,
    assessment_session_id: str
) -> Optional[Recommendation]:
    """
    Lấy recommendation theo assessment session ID
    
    Args:
        user_id: ID của user
        assessment_session_id: ID của assessment session
        
    Returns:
        Recommendation document hoặc None
    """
    recommendation = await Recommendation.find_one(
        Recommendation.user_id == user_id,
        Recommendation.assessment_session_id == assessment_session_id
    )
    
    return recommendation


async def get_latest_recommendation(user_id: str) -> Optional[Recommendation]:
    """
    Lấy recommendation mới nhất chưa expired (alias cho get_active_recommendation)
    
    Args:
        user_id: ID của user
        
    Returns:
        Recommendation document hoặc None
    """
    return await get_active_recommendation(user_id)


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

async def _get_available_courses(
    category: str,
    proficiency_level: str,
    limit: int = 15
) -> List[Course]:
    """
    Lấy danh sách courses có sẵn để gửi cho AI
    
    Args:
        category: Danh mục
        proficiency_level: Mức độ năng lực hiện tại
        limit: Số lượng courses tối đa
        
    Returns:
        List Course documents
    """
    # Map proficiency level sang course level
    level_map = {
        "Beginner": ["Beginner", "Intermediate"],
        "Intermediate": ["Intermediate", "Advanced"],
        "Advanced": ["Advanced"]
    }
    
    target_levels = level_map.get(proficiency_level, ["Beginner"])
    
    # Tìm courses published trong category và level phù hợp
    courses = await Course.find(
        Course.category == category,
        Course.status == "published"
    ).to_list()
    
    # Filter theo level và limit
    filtered = [c for c in courses if c.level in target_levels][:limit]
    
    return filtered


async def _match_courses_to_recommendations(
    category: str,
    proficiency_level: str,
    knowledge_gaps: List[Dict],
    available_courses: List[Course] = None
) -> List[Dict]:
    """
    Tìm courses phù hợp với knowledge gaps (IMPROVED matching logic)
    
    Args:
        category: Danh mục
        proficiency_level: Mức độ năng lực hiện tại
        knowledge_gaps: Các khoảng trống kiến thức
        available_courses: Courses đã fetch (optional)
        
    Returns:
        List dict chứa course recommendations
    """
    # Nếu chưa có courses, fetch lại
    if not available_courses:
        available_courses = await _get_available_courses(category, proficiency_level, 10)
    
    # IMPROVED: Match courses với knowledge gaps bằng multiple fields
    recommendations = []
    for i, course in enumerate(available_courses):
        score = 0
        matched_gaps = []
        reason_parts = []
        
        # Match với knowledge gaps
        for gap in knowledge_gaps:
            gap_area = gap.get("gap_area", gap.get("topic", "")).lower()
            gap_desc = gap.get("description", "").lower()
            
            # Check title
            if gap_area in course.title.lower():
                score += 30
                matched_gaps.append(gap_area)
            
            # Check description
            if gap_area in course.description.lower() or gap_desc in course.description.lower():
                score += 20
                if gap_area not in matched_gaps:
                    matched_gaps.append(gap_area)
            
            # Check learning outcomes
            for outcome in course.learning_outcomes:
                outcome_text = outcome.get('description', '').lower()
                if gap_area in outcome_text or gap_desc in outcome_text:
                    score += 15
                    if gap_area not in matched_gaps:
                        matched_gaps.append(gap_area)
                    break
        
        # Build reason
        if matched_gaps:
            reason_parts.append(f"Giúp khắc phục lỗ hổng: {', '.join(matched_gaps[:2])}")
        else:
            reason_parts.append("Phù hợp với trình độ hiện tại")
        
        # Bonus score for exact level match
        if course.level == proficiency_level:
            score += 10
        
        recommendations.append({
            "course_id": course.id,
            "title": course.title,
            "category": course.category,
            "level": course.level,
            "reason": ". ".join(reason_parts),
            "priority": i + 1,
            "relevance_score": min(score, 100),
            "addresses_gaps": matched_gaps[:3]
        })
    
    # Sort by relevance score
    recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Re-assign priority after sorting
    for i, rec in enumerate(recommendations):
        rec["priority"] = i + 1
    
    return recommendations[:10]
