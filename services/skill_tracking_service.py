"""
Skill Tracking Service - Cumulative Weakness Tracking
Theo dõi điểm yếu tích lũy của học viên qua nhiều quiz attempts
Tuân thủ: models.py SkillProficiencyTracking
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from models.models import (
    SkillProficiencyTracking,
    SkillAttemptHistory,
    Quiz,
    QuizAttempt,
    Lesson
)


# ============================================================================
# CORE TRACKING FUNCTIONS
# ============================================================================

async def update_skill_proficiency(
    user_id: str,
    course_id: str,
    quiz_attempt_id: str
) -> Dict[str, Any]:
    """
    Cập nhật skill proficiency sau khi user làm quiz
    
    Flow:
    1. Lấy quiz attempt và quiz
    2. Extract skill_tags từ câu hỏi
    3. Tính proficiency cho từng skill trong quiz này
    4. Update hoặc create SkillProficiencyTracking document
    5. Tính trend và phát hiện weakness
    
    Args:
        user_id: UUID user
        course_id: UUID course
        quiz_attempt_id: UUID quiz attempt
        
    Returns:
        {
            "updated_skills": ["python-loops", "python-functions"],
            "weak_skills_detected": ["python-loops"],
            "chronic_weaknesses": []
        }
    """
    # 1. Lấy quiz attempt
    attempt = await QuizAttempt.get(quiz_attempt_id)
    if not attempt:
        return {"error": "Quiz attempt not found"}
    
    # 2. Lấy quiz để có questions với skill_tag
    quiz = await Quiz.get(attempt.quiz_id)
    if not quiz:
        return {"error": "Quiz not found"}
    
    # 3. Group questions by skill_tag
    skill_stats = {}  # {skill_tag: {correct: int, total: int, wrong_question_ids: []}}
    
    for question in quiz.questions:
        skill_tag = question.get("skill_tag")
        if not skill_tag:
            continue  # Skip questions without skill_tag
        
        if skill_tag not in skill_stats:
            skill_stats[skill_tag] = {
                "correct": 0,
                "total": 0,
                "wrong_question_ids": []
            }
        
        skill_stats[skill_tag]["total"] += 1
        
        # Check if user answered correctly
        question_id = question.get("id")
        is_correct = False
        
        for answer in attempt.answers:
            if answer.get("question_id") == question_id:
                is_correct = answer.get("is_correct", False)
                break
        
        if is_correct:
            skill_stats[skill_tag]["correct"] += 1
        else:
            skill_stats[skill_tag]["wrong_question_ids"].append(question_id)
    
    # 4. Update SkillProficiencyTracking cho từng skill
    updated_skills = []
    weak_skills_detected = []
    chronic_weaknesses = []
    
    for skill_tag, stats in skill_stats.items():
        result = await _update_single_skill_tracking(
            user_id=user_id,
            course_id=course_id,
            skill_tag=skill_tag,
            quiz_id=str(quiz.id),
            quiz_attempt_id=quiz_attempt_id,
            quiz_title=quiz.title,
            module_id=quiz.module_id,
            lesson_id=quiz.lesson_id,
            questions_count=stats["total"],
            correct_count=stats["correct"],
            wrong_question_ids=stats["wrong_question_ids"],
            attempted_at=attempt.submitted_at or datetime.utcnow()
        )
        
        updated_skills.append(skill_tag)
        
        if result.get("is_weak_skill"):
            weak_skills_detected.append(skill_tag)
        
        if result.get("is_chronic_weakness"):
            chronic_weaknesses.append(skill_tag)
    
    return {
        "updated_skills": updated_skills,
        "weak_skills_detected": weak_skills_detected,
        "chronic_weaknesses": chronic_weaknesses,
        "total_skills_tracked": len(updated_skills)
    }


async def _update_single_skill_tracking(
    user_id: str,
    course_id: str,
    skill_tag: str,
    quiz_id: str,
    quiz_attempt_id: str,
    quiz_title: Optional[str],
    module_id: Optional[str],
    lesson_id: Optional[str],
    questions_count: int,
    correct_count: int,
    wrong_question_ids: List[str],
    attempted_at: datetime
) -> Dict[str, Any]:
    """
    Update tracking cho 1 skill cụ thể

    Returns:
        {
            "skill_tag": str,
            "current_proficiency": float,
            "is_weak_skill": bool,
            "is_chronic_weakness": bool,
            "trend": str
        }
    """
    # Tìm hoặc tạo mới SkillProficiencyTracking
    tracking = await SkillProficiencyTracking.find_one(
        SkillProficiencyTracking.user_id == user_id,
        SkillProficiencyTracking.course_id == course_id,
        SkillProficiencyTracking.skill_tag == skill_tag
    )

    if not tracking:
        # Tạo mới
        tracking = SkillProficiencyTracking(
            user_id=user_id,
            course_id=course_id,
            skill_tag=skill_tag,
            first_seen=attempted_at
        )

    # Tính proficiency cho lần này
    wrong_count = questions_count - correct_count
    proficiency = (correct_count / questions_count * 100) if questions_count > 0 else 0.0

    # Tạo attempt history entry
    attempt_entry = SkillAttemptHistory(
        quiz_id=quiz_id,
        quiz_attempt_id=quiz_attempt_id,
        quiz_title=quiz_title,
        module_id=module_id,
        lesson_id=lesson_id,
        questions_count=questions_count,
        correct_count=correct_count,
        wrong_count=wrong_count,
        proficiency=proficiency,
        attempted_at=attempted_at,
        wrong_question_ids=wrong_question_ids
    )

    # Thêm vào history (insert at beginning để sort DESC)
    tracking.attempt_history.insert(0, attempt_entry)

    # Giới hạn history size (keep last 20 attempts)
    if len(tracking.attempt_history) > 20:
        tracking.attempt_history = tracking.attempt_history[:20]

    # Update cumulative stats
    tracking.total_questions += questions_count
    tracking.total_correct += correct_count
    tracking.total_wrong += wrong_count
    tracking.total_attempts += 1
    tracking.current_proficiency = (
        tracking.total_correct / tracking.total_questions * 100
    ) if tracking.total_questions > 0 else 0.0

    # Calculate trend
    trend_data = _calculate_trend(tracking.attempt_history)
    tracking.trend = trend_data["trend"]
    tracking.trend_rate = trend_data["trend_rate"]
    tracking.last_3_attempts_avg = trend_data["last_3_avg"]

    # Detect weakness
    tracking.is_weak_skill = (
        tracking.current_proficiency < 60.0 and tracking.total_attempts >= 2
    )
    tracking.is_chronic_weakness = (
        tracking.current_proficiency < 60.0 and tracking.total_attempts >= 3
    )

    # Calculate consecutive fails
    consecutive_fails = 0
    for attempt in tracking.attempt_history:
        if attempt.proficiency < 60.0:
            consecutive_fails += 1
        else:
            break
    tracking.consecutive_fails = consecutive_fails

    # Determine priority level
    if tracking.is_chronic_weakness and tracking.consecutive_fails >= 3:
        tracking.priority_level = "urgent"
    elif tracking.is_chronic_weakness:
        tracking.priority_level = "high"
    elif tracking.is_weak_skill:
        tracking.priority_level = "medium"
    else:
        tracking.priority_level = "low"

    # Update timestamps
    tracking.last_updated = datetime.utcnow()
    tracking.last_attempt_at = attempted_at

    # Save
    await tracking.save()

    return {
        "skill_tag": skill_tag,
        "current_proficiency": tracking.current_proficiency,
        "is_weak_skill": tracking.is_weak_skill,
        "is_chronic_weakness": tracking.is_chronic_weakness,
        "trend": tracking.trend,
        "priority_level": tracking.priority_level
    }


def _calculate_trend(attempt_history: List[SkillAttemptHistory]) -> Dict[str, Any]:
    """
    Tính trend dựa trên attempt history

    Returns:
        {
            "trend": "improving|declining|stable|fluctuating",
            "trend_rate": float,  # % change per attempt
            "last_3_avg": float
        }
    """
    if len(attempt_history) < 2:
        return {
            "trend": "stable",
            "trend_rate": 0.0,
            "last_3_avg": attempt_history[0].proficiency if attempt_history else 0.0
        }

    # Get last 3 attempts (already sorted DESC)
    last_3 = attempt_history[:3]
    last_3_avg = sum(a.proficiency for a in last_3) / len(last_3)

    # Calculate trend rate (compare first vs last in history)
    # Note: history[0] = newest, history[-1] = oldest
    if len(attempt_history) >= 3:
        newest = attempt_history[0].proficiency
        oldest = attempt_history[min(2, len(attempt_history)-1)].proficiency

        if oldest > 0:
            trend_rate = ((newest - oldest) / oldest) * 100
        else:
            trend_rate = 0.0
    else:
        newest = attempt_history[0].proficiency
        oldest = attempt_history[-1].proficiency
        trend_rate = newest - oldest

    # Determine trend
    if abs(trend_rate) < 5:
        trend = "stable"
    elif trend_rate > 10:
        trend = "improving"
    elif trend_rate < -10:
        trend = "declining"
    else:
        # Check fluctuation
        proficiencies = [a.proficiency for a in last_3]
        variance = max(proficiencies) - min(proficiencies)
        if variance > 20:
            trend = "fluctuating"
        else:
            trend = "stable"

    return {
        "trend": trend,
        "trend_rate": round(trend_rate, 2),
        "last_3_avg": round(last_3_avg, 2)
    }


# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

async def get_weak_skills_summary(
    user_id: str,
    course_id: str,
    threshold: float = 60.0,
    include_all: bool = False
) -> Dict[str, Any]:
    """
    Lấy tổng hợp điểm yếu của user trong course

    Args:
        user_id: UUID user
        course_id: UUID course
        threshold: Proficiency threshold để coi là weak (default 60%)
        include_all: Nếu True, return tất cả skills (không chỉ weak skills)

    Returns:
        {
            "user_id": str,
            "course_id": str,
            "weak_skills": [
                {
                    "skill_tag": "python-loops",
                    "current_proficiency": 45.0,
                    "total_attempts": 5,
                    "trend": "declining",
                    "trend_rate": -5.2,
                    "is_chronic_weakness": True,
                    "consecutive_fails": 3,
                    "priority_level": "urgent",
                    "recommended_lessons": ["lesson-2", "lesson-5"],
                    "last_attempt_at": datetime,
                    "improvement_needed": 15.0  # % to reach threshold
                }
            ],
            "total_weak_skills": 3,
            "total_skills_tracked": 10,
            "overall_weak_percentage": 30.0,
            "urgent_count": 1,
            "high_priority_count": 2
        }
    """
    # Query skills
    if include_all:
        query = SkillProficiencyTracking.find(
            SkillProficiencyTracking.user_id == user_id,
            SkillProficiencyTracking.course_id == course_id
        )
    else:
        query = SkillProficiencyTracking.find(
            SkillProficiencyTracking.user_id == user_id,
            SkillProficiencyTracking.course_id == course_id,
            SkillProficiencyTracking.current_proficiency < threshold
        )

    skills = await query.to_list()

    # Build weak skills list
    weak_skills = []
    urgent_count = 0
    high_priority_count = 0

    for skill in skills:
        # Get recommended lessons for this skill
        recommended_lessons = await _get_recommended_lessons_for_skill(
            course_id=course_id,
            skill_tag=skill.skill_tag
        )

        skill_data = {
            "skill_tag": skill.skill_tag,
            "current_proficiency": round(skill.current_proficiency, 2),
            "total_attempts": skill.total_attempts,
            "total_questions": skill.total_questions,
            "total_correct": skill.total_correct,
            "total_wrong": skill.total_wrong,
            "trend": skill.trend,
            "trend_rate": skill.trend_rate,
            "is_weak_skill": skill.is_weak_skill,
            "is_chronic_weakness": skill.is_chronic_weakness,
            "consecutive_fails": skill.consecutive_fails,
            "priority_level": skill.priority_level,
            "recommended_lessons": recommended_lessons,
            "last_attempt_at": skill.last_attempt_at,
            "improvement_needed": max(0, threshold - skill.current_proficiency)
        }

        weak_skills.append(skill_data)

        if skill.priority_level == "urgent":
            urgent_count += 1
        elif skill.priority_level == "high":
            high_priority_count += 1

    # Sort by priority: urgent > high > medium > low
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    weak_skills.sort(key=lambda x: (
        priority_order.get(x["priority_level"], 4),
        x["current_proficiency"]  # Secondary sort by proficiency (lower first)
    ))

    # Get total skills tracked
    total_skills_tracked = await SkillProficiencyTracking.find(
        SkillProficiencyTracking.user_id == user_id,
        SkillProficiencyTracking.course_id == course_id
    ).count()

    return {
        "user_id": user_id,
        "course_id": course_id,
        "weak_skills": weak_skills,
        "total_weak_skills": len(weak_skills),
        "total_skills_tracked": total_skills_tracked,
        "overall_weak_percentage": (
            len(weak_skills) / total_skills_tracked * 100
        ) if total_skills_tracked > 0 else 0.0,
        "urgent_count": urgent_count,
        "high_priority_count": high_priority_count,
        "threshold": threshold
    }


async def _get_recommended_lessons_for_skill(
    course_id: str,
    skill_tag: str
) -> List[str]:
    """
    Tìm lessons có learning_objectives chứa skill_tag

    Returns:
        List of lesson_ids
    """
    # Query lessons có learning_objectives chứa skill_tag
    lessons = await Lesson.find(
        Lesson.course_id == course_id,
        Lesson.learning_objectives == {"$regex": skill_tag, "$options": "i"}
    ).to_list()

    return [str(lesson.id) for lesson in lessons]


async def get_skill_history(
    user_id: str,
    course_id: str,
    skill_tag: str
) -> Dict[str, Any]:
    """
    Lấy lịch sử proficiency của 1 skill cụ thể

    Args:
        user_id: UUID user
        course_id: UUID course
        skill_tag: Skill tag cần xem lịch sử

    Returns:
        {
            "skill_tag": "python-loops",
            "current_proficiency": 45.0,
            "trend": "declining",
            "trend_rate": -5.2,
            "total_attempts": 5,
            "history": [
                {
                    "quiz_id": "...",
                    "quiz_title": "Module 1 Assessment",
                    "proficiency": 40.0,
                    "questions_count": 5,
                    "correct_count": 2,
                    "wrong_count": 3,
                    "attempted_at": datetime,
                    "wrong_question_ids": ["q1", "q3", "q5"]
                }
            ],
            "first_seen": datetime,
            "last_attempt_at": datetime,
            "improvement_rate": -5.2,
            "is_improving": False
        }
    """
    # Find skill tracking
    tracking = await SkillProficiencyTracking.find_one(
        SkillProficiencyTracking.user_id == user_id,
        SkillProficiencyTracking.course_id == course_id,
        SkillProficiencyTracking.skill_tag == skill_tag
    )

    if not tracking:
        return {
            "error": "Skill not found",
            "skill_tag": skill_tag,
            "message": "Chưa có dữ liệu tracking cho skill này"
        }

    # Build history
    history = []
    for attempt in tracking.attempt_history:
        history.append({
            "quiz_id": attempt.quiz_id,
            "quiz_attempt_id": attempt.quiz_attempt_id,
            "quiz_title": attempt.quiz_title,
            "module_id": attempt.module_id,
            "lesson_id": attempt.lesson_id,
            "proficiency": round(attempt.proficiency, 2),
            "questions_count": attempt.questions_count,
            "correct_count": attempt.correct_count,
            "wrong_count": attempt.wrong_count,
            "attempted_at": attempt.attempted_at,
            "wrong_question_ids": attempt.wrong_question_ids
        })

    return {
        "skill_tag": tracking.skill_tag,
        "current_proficiency": round(tracking.current_proficiency, 2),
        "trend": tracking.trend,
        "trend_rate": tracking.trend_rate,
        "total_attempts": tracking.total_attempts,
        "total_questions": tracking.total_questions,
        "total_correct": tracking.total_correct,
        "total_wrong": tracking.total_wrong,
        "history": history,
        "first_seen": tracking.first_seen,
        "last_attempt_at": tracking.last_attempt_at,
        "improvement_rate": tracking.trend_rate,
        "is_improving": tracking.trend == "improving",
        "is_weak_skill": tracking.is_weak_skill,
        "is_chronic_weakness": tracking.is_chronic_weakness,
        "consecutive_fails": tracking.consecutive_fails,
        "priority_level": tracking.priority_level
    }


async def get_all_skills_overview(
    user_id: str,
    course_id: str
) -> Dict[str, Any]:
    """
    Lấy overview tất cả skills của user trong course

    Returns:
        {
            "user_id": str,
            "course_id": str,
            "total_skills": 10,
            "strong_skills": [...],  # proficiency >= 80%
            "average_skills": [...],  # 60% <= proficiency < 80%
            "weak_skills": [...],  # proficiency < 60%
            "overall_proficiency": 68.5,
            "skills_by_category": {...}
        }
    """
    # Get all skills
    skills = await SkillProficiencyTracking.find(
        SkillProficiencyTracking.user_id == user_id,
        SkillProficiencyTracking.course_id == course_id
    ).to_list()

    if not skills:
        return {
            "user_id": user_id,
            "course_id": course_id,
            "total_skills": 0,
            "message": "Chưa có dữ liệu tracking"
        }

    # Categorize skills
    strong_skills = []
    average_skills = []
    weak_skills = []

    total_proficiency = 0.0

    for skill in skills:
        skill_data = {
            "skill_tag": skill.skill_tag,
            "proficiency": round(skill.current_proficiency, 2),
            "trend": skill.trend,
            "attempts": skill.total_attempts
        }

        total_proficiency += skill.current_proficiency

        if skill.current_proficiency >= 80:
            strong_skills.append(skill_data)
        elif skill.current_proficiency >= 60:
            average_skills.append(skill_data)
        else:
            weak_skills.append(skill_data)

    # Sort each category by proficiency
    strong_skills.sort(key=lambda x: x["proficiency"], reverse=True)
    average_skills.sort(key=lambda x: x["proficiency"], reverse=True)
    weak_skills.sort(key=lambda x: x["proficiency"])

    return {
        "user_id": user_id,
        "course_id": course_id,
        "total_skills": len(skills),
        "strong_skills": strong_skills,
        "average_skills": average_skills,
        "weak_skills": weak_skills,
        "strong_count": len(strong_skills),
        "average_count": len(average_skills),
        "weak_count": len(weak_skills),
        "overall_proficiency": round(total_proficiency / len(skills), 2) if skills else 0.0
    }




