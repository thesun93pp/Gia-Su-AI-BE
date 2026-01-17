"""
Module Assessment Review Service
Phân tích kết quả module assessment và xác định lessons cần review
"""

from datetime import datetime
from typing import List, Dict, Optional
from models.models import Quiz, QuizAttempt, Enrollment, Lesson, Module
from beanie import PydanticObjectId


async def analyze_module_assessment_result(
    quiz_attempt_id: str,
    enrollment_id: str
) -> Dict:
    """
    Phân tích kết quả module assessment và xác định lessons cần review
    
    Flow:
    1. Lấy quiz attempt
    2. Lấy danh sách câu sai (wrong_answers)
    3. Lấy skill_tag của từng câu sai
    4. Tìm lessons có learning_objectives chứa skill_tag đó
    5. Group lessons theo skill_gaps
    6. Return danh sách lessons cần review
    
    Args:
        quiz_attempt_id: ID của quiz attempt
        enrollment_id: ID của enrollment
        
    Returns:
        {
            "passed": bool,
            "lessons_to_review": [
                {
                    "lesson_id": "...",
                    "lesson_title": "...",
                    "module_id": "...",
                    "skill_gaps": ["..."],
                    "wrong_questions": ["q1", "q2"],
                    "reason": "Bạn làm sai 2 câu hỏi về ..."
                }
            ],
            "skill_gaps_summary": {
                "skill_tag": {
                    "wrong_count": 2,
                    "total_count": 3,
                    "proficiency": 33.3
                }
            }
        }
    """
    # 1. Lấy quiz attempt
    attempt = await QuizAttempt.get(quiz_attempt_id)
    if not attempt:
        return {
            "passed": True,
            "lessons_to_review": [],
            "skill_gaps_summary": {}
        }
    
    # 2. Lấy quiz để có thông tin câu hỏi
    quiz = await Quiz.get(attempt.quiz_id)
    if not quiz or not quiz.module_id:
        return {
            "passed": attempt.passed,
            "lessons_to_review": [],
            "skill_gaps_summary": {}
        }
    
    # 3. Nếu pass thì không cần review
    if attempt.passed:
        return {
            "passed": True,
            "lessons_to_review": [],
            "skill_gaps_summary": {}
        }
    
    # 4. Lấy danh sách câu sai
    wrong_question_ids = attempt.wrong_answers or []
    if not wrong_question_ids:
        return {
            "passed": False,
            "lessons_to_review": [],
            "skill_gaps_summary": {}
        }
    
    # 5. Phân tích skill gaps từ câu sai
    skill_gaps_map = {}  # {skill_tag: {wrong_count, total_count, question_ids}}
    
    for question in quiz.questions:
        question_id = question.get("question_id")
        skill_tag = question.get("skill_tag")
        
        if not skill_tag:
            continue
        
        # Initialize skill_tag entry
        if skill_tag not in skill_gaps_map:
            skill_gaps_map[skill_tag] = {
                "wrong_count": 0,
                "total_count": 0,
                "wrong_question_ids": []
            }
        
        skill_gaps_map[skill_tag]["total_count"] += 1
        
        # Nếu câu này sai
        if question_id in wrong_question_ids:
            skill_gaps_map[skill_tag]["wrong_count"] += 1
            skill_gaps_map[skill_tag]["wrong_question_ids"].append(question_id)
    
    # 6. Tìm lessons liên quan đến skill_gaps
    lessons_to_review_map = {}  # {lesson_id: lesson_info}
    
    # Lấy tất cả lessons trong module
    lessons = await Lesson.find(Lesson.module_id == quiz.module_id).to_list()
    
    for lesson in lessons:
        if not lesson.learning_objectives:
            continue
        
        # Check xem lesson này có skill_tag nào bị sai không
        lesson_skill_gaps = []
        lesson_wrong_questions = []
        
        for skill_tag, skill_info in skill_gaps_map.items():
            if skill_tag in lesson.learning_objectives and skill_info["wrong_count"] > 0:
                lesson_skill_gaps.append(skill_tag)
                lesson_wrong_questions.extend(skill_info["wrong_question_ids"])
        
        # Nếu lesson này có skill gaps
        if lesson_skill_gaps:
            lessons_to_review_map[str(lesson.id)] = {
                "lesson_id": str(lesson.id),
                "lesson_title": lesson.title,
                "module_id": quiz.module_id,
                "skill_gaps": lesson_skill_gaps,
                "wrong_questions": list(set(lesson_wrong_questions)),  # Remove duplicates
                "reason": f"Bạn làm sai {len(set(lesson_wrong_questions))} câu hỏi liên quan đến lesson này"
            }

    # 7. Tính skill_gaps_summary
    skill_gaps_summary = {}
    for skill_tag, skill_info in skill_gaps_map.items():
        if skill_info["wrong_count"] > 0:
            proficiency = ((skill_info["total_count"] - skill_info["wrong_count"]) / skill_info["total_count"]) * 100
            skill_gaps_summary[skill_tag] = {
                "wrong_count": skill_info["wrong_count"],
                "total_count": skill_info["total_count"],
                "proficiency": round(proficiency, 1)
            }

    # 8. Convert to list
    lessons_to_review = list(lessons_to_review_map.values())

    # 9. Đánh dấu lessons cần review trong enrollment
    if lessons_to_review:
        await mark_lessons_for_review(enrollment_id, lessons_to_review)

    return {
        "passed": False,
        "lessons_to_review": lessons_to_review,
        "skill_gaps_summary": skill_gaps_summary
    }


async def mark_lessons_for_review(
    enrollment_id: str,
    lessons_to_review: List[Dict]
) -> None:
    """
    Đánh dấu lessons cần review trong enrollment

    Args:
        enrollment_id: ID của enrollment
        lessons_to_review: Danh sách lessons cần review
    """
    enrollment = await Enrollment.get(enrollment_id)
    if not enrollment:
        return

    # Lấy danh sách lesson_ids hiện tại đã được đánh dấu review
    existing_review_lesson_ids = {
        item["lesson_id"]
        for item in enrollment.lessons_need_review
        if not item.get("reviewed", False)
    }

    # Thêm lessons mới cần review (không trùng)
    for lesson_info in lessons_to_review:
        lesson_id = lesson_info["lesson_id"]

        # Nếu lesson này chưa được đánh dấu review (hoặc đã review xong)
        if lesson_id not in existing_review_lesson_ids:
            enrollment.lessons_need_review.append({
                "lesson_id": lesson_id,
                "lesson_title": lesson_info["lesson_title"],
                "module_id": lesson_info["module_id"],
                "skill_gaps": lesson_info["skill_gaps"],
                "wrong_questions": lesson_info["wrong_questions"],
                "marked_at": datetime.utcnow(),
                "reviewed": False,
                "reviewed_at": None
            })

    await enrollment.save()


async def mark_lesson_as_reviewed(
    enrollment_id: str,
    lesson_id: str
) -> Dict:
    """
    Đánh dấu lesson đã được review lại

    Args:
        enrollment_id: ID của enrollment
        lesson_id: ID của lesson

    Returns:
        {
            "success": bool,
            "message": str,
            "remaining_lessons": int
        }
    """
    enrollment = await Enrollment.get(enrollment_id)
    if not enrollment:
        return {
            "success": False,
            "message": "Enrollment không tồn tại",
            "remaining_lessons": 0
        }

    # Tìm và cập nhật lesson
    found = False
    for item in enrollment.lessons_need_review:
        if item["lesson_id"] == lesson_id and not item.get("reviewed", False):
            item["reviewed"] = True
            item["reviewed_at"] = datetime.utcnow()
            found = True
            break

    if not found:
        return {
            "success": False,
            "message": "Lesson không có trong danh sách cần review",
            "remaining_lessons": 0
        }

    await enrollment.save()

    # Đếm số lessons còn lại cần review
    remaining = sum(
        1 for item in enrollment.lessons_need_review
        if not item.get("reviewed", False)
    )

    return {
        "success": True,
        "message": "Lesson đã được đánh dấu đã review",
        "remaining_lessons": remaining
    }


async def get_lessons_need_review(
    enrollment_id: str,
    include_reviewed: bool = False
) -> Dict:
    """
    Lấy danh sách lessons cần review

    Args:
        enrollment_id: ID của enrollment
        include_reviewed: Có bao gồm lessons đã review không

    Returns:
        {
            "total_count": int,
            "pending_count": int,
            "reviewed_count": int,
            "lessons": [...]
        }
    """
    enrollment = await Enrollment.get(enrollment_id)
    if not enrollment:
        return {
            "total_count": 0,
            "pending_count": 0,
            "reviewed_count": 0,
            "lessons": []
        }

    lessons = enrollment.lessons_need_review or []

    # Filter
    if not include_reviewed:
        lessons = [item for item in lessons if not item.get("reviewed", False)]

    # Count
    total_count = len(enrollment.lessons_need_review)
    pending_count = sum(1 for item in enrollment.lessons_need_review if not item.get("reviewed", False))
    reviewed_count = total_count - pending_count

    return {
        "total_count": total_count,
        "pending_count": pending_count,
        "reviewed_count": reviewed_count,
        "lessons": lessons
    }


