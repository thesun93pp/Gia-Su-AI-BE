"""
Quiz Service - Xử lý quiz/bài kiểm tra trong lesson
Sử dụng: Beanie ODM, MongoDB
Tuân thủ: CHUCNANG.md Section 2.4.3-2.4.7
"""

from datetime import datetime
from typing import Optional, List, Dict
from models.models import Quiz, QuizAttempt, Class


# ============================================================================
# QUIZ CRUD
# ============================================================================

async def create_quiz(
    lesson_id: str,
    course_id: str,
    created_by: str,
    title: str,
    description: str,
    questions: List[Dict],
    time_limit_minutes: Optional[int] = None,
    passing_score: float = 70.0,
    max_attempts: int = 3
) -> Quiz:
    """
    Tạo quiz mới cho lesson
    
    Args:
        lesson_id: ID của lesson
        course_id: ID của course
        created_by: ID của người tạo
        title: Tiêu đề quiz
        description: Mô tả
        questions: List câu hỏi
        time_limit_minutes: Giới hạn thời gian
        passing_score: Điểm đạt
        max_attempts: Số lần thử tối đa
        
    Returns:
        Quiz document đã tạo
    """
    quiz = Quiz(
        lesson_id=lesson_id,
        course_id=course_id,
        created_by=created_by,
        title=title,
        description=description,
        questions=questions,
        time_limit_minutes=time_limit_minutes,
        passing_score=passing_score,
        max_attempts=max_attempts
    )
    
    await quiz.insert()
    return quiz


async def get_quiz_by_id(quiz_id: str) -> Optional[Quiz]:
    """
    Lấy quiz theo ID
    
    Args:
        quiz_id: ID của quiz
        
    Returns:
        Quiz document hoặc None
    """
    try:
        quiz = await Quiz.get(quiz_id)
        return quiz
    except Exception:
        return None


async def get_quizzes_by_lesson(lesson_id: str) -> List[Quiz]:
    """
    Lấy tất cả quizzes của một lesson
    
    Args:
        lesson_id: ID của lesson
        
    Returns:
        List Quiz documents
    """
    quizzes = await Quiz.find(Quiz.lesson_id == lesson_id).to_list()
    return quizzes


async def get_quizzes_by_course(
    course_id: str,
    skip: int = 0,
    limit: int = 50
) -> List[Quiz]:
    """
    Lấy tất cả quizzes của một course
    
    Args:
        course_id: ID của course
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        List Quiz documents
    """
    quizzes = await Quiz.find(
        Quiz.course_id == course_id
    ).skip(skip).limit(limit).to_list()
    
    return quizzes


async def update_quiz(
    quiz_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    questions: Optional[List[Dict]] = None,
    passing_score: Optional[float] = None
) -> Optional[Quiz]:
    """
    Cập nhật quiz
    
    Args:
        quiz_id: ID của quiz
        title, description, questions, passing_score: Fields cần update
        
    Returns:
        Quiz document đã update hoặc None
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        return None
    
    if title is not None:
        quiz.title = title
    
    if description is not None:
        quiz.description = description
    
    if questions is not None:
        quiz.questions = questions
    
    if passing_score is not None:
        quiz.passing_score = passing_score
    
    quiz.updated_at = datetime.utcnow()
    await quiz.save()
    return quiz


async def delete_quiz(quiz_id: str) -> bool:
    """
    Xóa quiz
    
    Args:
        quiz_id: ID của quiz
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        return False
    
    await quiz.delete()
    return True


# ============================================================================
# QUIZ ATTEMPT (Section 2.4.4-2.4.7)
# ============================================================================

async def create_quiz_attempt(
    quiz_id: str,
    user_id: str
) -> Optional[QuizAttempt]:
    """
    Tạo lần thử quiz mới
    
    Args:
        quiz_id: ID của quiz
        user_id: ID của user
        
    Returns:
        QuizAttempt document đã tạo hoặc None nếu đã hết lượt thử
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        return None
    
    # Kiểm tra số lần đã thử
    previous_attempts = await get_user_quiz_attempts(user_id, quiz_id)
    
    if len(previous_attempts) >= quiz.max_attempts:
        return None  # Đã hết lượt thử
    
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=user_id
    )
    
    await attempt.insert()
    return attempt


async def submit_quiz_attempt(
    attempt_id: str,
    answers: List[Dict]
) -> Optional[QuizAttempt]:
    """
    Submit câu trả lời quiz và tính điểm
    
    Args:
        attempt_id: ID của attempt
        answers: List câu trả lời dạng [{"question_id": "q1", "answer": "A"}, ...]
        
    Returns:
        QuizAttempt document đã đánh giá hoặc None
    """
    attempt = await get_quiz_attempt(attempt_id)
    
    if not attempt:
        return None
    
    if attempt.submitted_at:
        return None  # Đã submit rồi
    
    quiz = await get_quiz_by_id(attempt.quiz_id)
    
    if not quiz:
        return None
    
    # Tính điểm
    correct_count = 0
    total_count = len(quiz.questions)
    
    answer_map = {ans["question_id"]: ans["answer"] for ans in answers}
    
    for question in quiz.questions:
        q_id = question.get("question_id") or question.get("id")
        user_answer = answer_map.get(q_id)
        correct_answer = question.get("correct_answer")
        
        if user_answer == correct_answer:
            correct_count += 1
    
    score = (correct_count / total_count * 100) if total_count > 0 else 0
    passed = score >= quiz.passing_score
    
    # Lưu kết quả
    attempt.answers = answers
    attempt.score = score
    attempt.passed = passed
    attempt.submitted_at = datetime.utcnow()
    attempt.time_spent_seconds = int(
        (attempt.submitted_at - attempt.started_at).total_seconds()
    )
    
    await attempt.save()
    return attempt


async def get_quiz_attempt(attempt_id: str) -> Optional[QuizAttempt]:
    """
    Lấy quiz attempt theo ID
    
    Args:
        attempt_id: ID của attempt
        
    Returns:
        QuizAttempt document hoặc None
    """
    try:
        attempt = await QuizAttempt.get(attempt_id)
        return attempt
    except Exception:
        return None


async def get_user_quiz_attempts(
    user_id: str,
    quiz_id: str
) -> List[QuizAttempt]:
    """
    Lấy tất cả attempts của user cho quiz
    
    Args:
        user_id: ID của user
        quiz_id: ID của quiz
        
    Returns:
        List QuizAttempt documents
    """
    attempts = await QuizAttempt.find(
        QuizAttempt.user_id == user_id,
        QuizAttempt.quiz_id == quiz_id
    ).to_list()
    
    return attempts


async def get_best_quiz_score(user_id: str, quiz_id: str) -> Optional[float]:
    """
    Lấy điểm cao nhất của user cho quiz
    
    Args:
        user_id: ID của user
        quiz_id: ID của quiz
        
    Returns:
        Điểm cao nhất hoặc None nếu chưa làm
    """
    attempts = await get_user_quiz_attempts(user_id, quiz_id)
    
    if not attempts:
        return None
    
    # Lấy attempt có submitted_at (đã submit)
    submitted = [a for a in attempts if a.submitted_at]
    
    if not submitted:
        return None
    
    return max(a.score for a in submitted)


# ============================================================================
# QUIZ STATISTICS
# ============================================================================

async def get_quiz_stats(quiz_id: str) -> Dict:
    """
    Lấy thống kê cho quiz
    
    Args:
        quiz_id: ID của quiz
        
    Returns:
        Dict chứa thống kê
    """
    attempts = await QuizAttempt.find(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.submitted_at != None
    ).to_list()
    
    if not attempts:
        return {
            "total_attempts": 0,
            "average_score": 0,
            "pass_rate": 0,
            "avg_time_seconds": 0
        }
    
    total = len(attempts)
    avg_score = sum(a.score for a in attempts) / total
    passed = sum(1 for a in attempts if a.passed)
    pass_rate = (passed / total * 100)
    avg_time = sum(a.time_spent_seconds for a in attempts) / total
    
    return {
        "total_attempts": total,
        "average_score": avg_score,
        "pass_rate": pass_rate,
        "avg_time_seconds": int(avg_time)
    }


# ============================================================================
# INSTRUCTOR FEATURES (Section 3.3)
# ============================================================================

async def list_quizzes_with_filters(
    instructor_id: str,
    course_id: Optional[str] = None,
    class_id: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 20
) -> Dict:
    """
    3.3.2: List quizzes với filters cho instructor
    
    Business logic:
    - Filter by instructor (created_by), course_id, class_id
    - Search by title
    - Sort by created_at, title, question_count, pass_rate
    - Calculate stats for each quiz
    
    Args:
        instructor_id: ID của instructor
        course_id: Filter by course (optional)
        class_id: Filter by class (optional)
        search: Search trong title/description
        sort_by: Field sort
        sort_order: asc hoặc desc
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        Dict với data (list QuizListItem), total, skip, limit, has_next
    """
    from models.models import Lesson, Course, Class
    
    # Build query
    query_conditions = [Quiz.created_by == instructor_id]
    
    if course_id:
        query_conditions.append(Quiz.course_id == course_id)
    
    if search:
        # MongoDB text search - cần tạo text index trước
        # Tạm thời filter sau khi query
        pass
    
    # Get quizzes
    query = Quiz.find(*query_conditions)
    
    # Sort
    if sort_order == "desc":
        query = query.sort(f"-{sort_by}")
    else:
        query = query.sort(f"+{sort_by}")
    
    # Count total trước khi skip/limit
    total = await query.count()
    
    # Pagination
    quizzes = await query.skip(skip).limit(limit).to_list()
    
    # Search filter sau query (nếu có)
    if search:
        search_lower = search.lower()
        quizzes = [
            q for q in quizzes
            if search_lower in q.title.lower() or
            (q.description and search_lower in q.description.lower())
        ]
        total = len(quizzes)
    
    # Build response với stats
    quiz_items = []
    
    for quiz in quizzes:
        # Lấy lesson info
        lesson = await Lesson.get(quiz.lesson_id) if quiz.lesson_id else None
        lesson_title = lesson.title if lesson else "N/A"
        
        # Lấy course info
        course = await Course.get(quiz.course_id) if quiz.course_id else None
        course_title = course.title if course else "N/A"
        
        # Class info (nếu class_id filter)
        class_name = None
        if class_id:
            class_obj = await Class.get(class_id)
            class_name = class_obj.name if class_obj else None
        
        # Tính stats
        attempts = await QuizAttempt.find(
            QuizAttempt.quiz_id == str(quiz.id),
            QuizAttempt.submitted_at != None
        ).to_list()
        
        total_students = len(set(a.user_id for a in attempts))
        completed_count = len(attempts)
        pass_count = sum(1 for a in attempts if a.passed)
        pass_rate = (pass_count / completed_count * 100) if completed_count > 0 else 0
        avg_score = (sum(a.score for a in attempts) / completed_count) if completed_count > 0 else 0
        
        # Determine status
        status = "active"
        
        quiz_items.append({
            "quiz_id": str(quiz.id),
            "title": quiz.title,
            "description": quiz.description,
            "lesson_id": quiz.lesson_id,
            "lesson_title": lesson_title,
            "course_id": quiz.course_id,
            "course_title": course_title,
            "class_id": class_id,
            "class_name": class_name,
            "status": status,
            "question_count": len(quiz.questions),
            "time_limit": quiz.time_limit_minutes or 0,
            "pass_threshold": int(quiz.passing_score),
            "total_students": total_students,
            "completed_count": completed_count,
            "pass_count": pass_count,
            "pass_rate": round(pass_rate, 2),
            "average_score": round(avg_score, 2),
            "created_at": quiz.created_at,
            "updated_at": quiz.updated_at
        })
    
    has_next = (skip + limit) < total
    
    return {
        "data": quiz_items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": has_next
    }


async def check_quiz_attempts_count(quiz_id: str) -> int:
    """
    Kiểm tra số lượng attempts cho quiz
    
    Args:
        quiz_id: ID của quiz
        
    Returns:
        Số lượng attempts
    """
    attempts = await QuizAttempt.find(
        QuizAttempt.quiz_id == quiz_id
    ).to_list()
    
    return len(attempts)


async def update_quiz_instructor(
    quiz_id: str,
    instructor_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    time_limit_minutes: Optional[int] = None,
    passing_score: Optional[float] = None,
    max_attempts: Optional[int] = None,
    questions: Optional[List[Dict]] = None
) -> Dict:
    """
    3.3.3: Update quiz (instructor only)
    
    Business logic:
    - Check quiz ownership (created_by)
    - Count attempts - if > 0, add warning
    - Allow update but warn frontend to suggest new version
    - Update all provided fields
    
    Args:
        quiz_id: ID của quiz
        instructor_id: ID của instructor (verify ownership)
        title, description, time_limit_minutes, passing_score, max_attempts, questions: Fields to update
        
    Returns:
        Dict với quiz_id, title, question_count, has_attempts, attempts_count, warning, updated_at
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        return None
    
    # Verify ownership
    if quiz.created_by != instructor_id:
        raise Exception("Unauthorized: Not the creator of this quiz")
    
    # Count attempts
    attempts_count = await check_quiz_attempts_count(quiz_id)
    has_attempts = attempts_count > 0
    
    warning = None
    if has_attempts:
        warning = f"Cảnh báo: {attempts_count} học viên đã làm quiz này. Khuyến nghị tạo phiên bản mới thay vì sửa."
    
    # Update fields
    if title is not None:
        quiz.title = title
    
    if description is not None:
        quiz.description = description
    
    if time_limit_minutes is not None:
        quiz.time_limit_minutes = time_limit_minutes
    
    if passing_score is not None:
        quiz.passing_score = passing_score
    
    if max_attempts is not None:
        quiz.max_attempts = max_attempts
    
    if questions is not None:
        quiz.questions = questions
    
    quiz.updated_at = datetime.utcnow()
    await quiz.save()
    
    return {
        "quiz_id": str(quiz.id),
        "title": quiz.title,
        "question_count": len(quiz.questions),
        "total_points": sum(q.get("points", 0) for q in quiz.questions),
        "has_attempts": has_attempts,
        "attempts_count": attempts_count,
        "warning": warning,
        "updated_at": quiz.updated_at,
        "message": "Quiz đã được cập nhật thành công"
    }


async def delete_quiz_instructor(quiz_id: str, instructor_id: str) -> Dict:
    """
    3.3.4: Delete quiz (instructor only)
    
    Business logic:
    - Check quiz ownership
    - Count attempts - if > 0, REJECT delete
    - Only allow delete if no attempts
    
    Args:
        quiz_id: ID của quiz
        instructor_id: ID của instructor
        
    Returns:
        Dict với quiz_id, message
        
    Raises:
        Exception: Nếu có attempts hoặc không phải owner
    """
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        raise Exception("Quiz không tồn tại")
    
    # Verify ownership
    if quiz.created_by != instructor_id:
        raise Exception("Unauthorized: Not the creator of this quiz")
    
    # Count attempts
    attempts_count = await check_quiz_attempts_count(quiz_id)
    
    if attempts_count > 0:
        raise Exception(
            f"Không thể xóa quiz: {attempts_count} học viên đã làm quiz này"
        )
    
    # Delete quiz
    await quiz.delete()
    
    return {
        "quiz_id": str(quiz_id),
        "message": "Quiz đã được xóa thành công"
    }


async def get_class_quiz_results(quiz_id: str, class_id: str) -> Dict:
    """
    3.3.5: Get quiz results for entire class
    
    Business logic:
    - Get all students in class (from enrollments)
    - Get all quiz attempts from those students
    - Calculate statistics: avg, median, highest, lowest, pass rate
    - Build histogram (score distribution)
    - Rank students by score
    - Find difficult questions (lowest correct rate)
    
    Args:
        quiz_id: ID của quiz
        class_id: ID của class
        
    Returns:
        Dict với statistics, score_distribution, student_ranking, difficult_questions
    """
    from models.models import Enrollment, User
    
    quiz = await get_quiz_by_id(quiz_id)
    
    if not quiz:
        raise Exception("Quiz không tồn tại")
    
    # Get students in class (enrolled in course with class_id)
    enrollments = await Enrollment.find(
        Enrollment.course_id == quiz.course_id,
        Enrollment.status == "active"
    ).to_list()
    
    student_ids = [e.user_id for e in enrollments]
    
    # Get quiz attempts from these students
    attempts = await QuizAttempt.find(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.submitted_at != None
    ).to_list()
    
    # Filter only students in class
    class_attempts = [a for a in attempts if a.user_id in student_ids]
    
    # Statistics
    total_students = len(student_ids)
    completed_count = len(class_attempts)
    completion_rate = (completed_count / total_students * 100) if total_students > 0 else 0
    
    pass_count = sum(1 for a in class_attempts if a.passed)
    fail_count = completed_count - pass_count
    pass_rate = (pass_count / completed_count * 100) if completed_count > 0 else 0
    
    scores = [a.score for a in class_attempts]
    avg_score = sum(scores) / len(scores) if scores else 0
    median_score = sorted(scores)[len(scores) // 2] if scores else 0
    highest_score = max(scores) if scores else 0
    lowest_score = min(scores) if scores else 0
    
    times = [a.time_spent_seconds / 60 for a in class_attempts]  # Convert to minutes
    avg_time = sum(times) / len(times) if times else 0
    
    statistics = {
        "total_students": total_students,
        "completed_count": completed_count,
        "completion_rate": round(completion_rate, 2),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": round(pass_rate, 2),
        "average_score": round(avg_score, 2),
        "median_score": round(median_score, 2),
        "highest_score": round(highest_score, 2),
        "lowest_score": round(lowest_score, 2),
        "average_time": int(avg_time)
    }
    
    # Score distribution (histogram)
    # Ranges: 0-10, 11-20, ..., 91-100
    score_distribution = []
    ranges = [(i, i + 10) for i in range(0, 100, 10)]
    
    for start, end in ranges:
        count = sum(1 for s in scores if start <= s < end)
        percentage = (count / len(scores) * 100) if scores else 0
        
        score_distribution.append({
            "range": f"{start}-{end-1}" if end < 100 else f"{start}-100",
            "count": count,
            "percentage": round(percentage, 2)
        })
    
    # Student ranking
    # Get best attempt per student
    student_best_attempts = {}
    for attempt in class_attempts:
        uid = attempt.user_id
        if uid not in student_best_attempts or attempt.score > student_best_attempts[uid].score:
            student_best_attempts[uid] = attempt
    
    # Sort by score descending
    ranked_attempts = sorted(
        student_best_attempts.values(),
        key=lambda a: (-a.score, a.time_spent_seconds)
    )
    
    student_ranking = []
    for rank, attempt in enumerate(ranked_attempts[:20], start=1):  # Top 20
        user = await User.get(attempt.user_id)
        
        # Count attempts
        user_attempts = [a for a in class_attempts if a.user_id == attempt.user_id]
        
        student_ranking.append({
            "rank": rank,
            "user_id": attempt.user_id,
            "full_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "avatar": user.avatar if user else None,
            "score": round(attempt.score, 2),
            "time_spent": int(attempt.time_spent_seconds / 60),
            "attempt_count": len(user_attempts),
            "status": "pass" if attempt.passed else "fail",
            "completed_at": attempt.submitted_at
        })
    
    # Difficult questions (lowest correct rate)
    # Analyze answers across all attempts
    question_stats = {}
    
    for attempt in class_attempts:
        answer_map = {ans["question_id"]: ans["answer"] for ans in attempt.answers}
        
        for question in quiz.questions:
            q_id = question.get("question_id") or question.get("id") or question.get("order")
            
            if q_id not in question_stats:
                question_stats[q_id] = {
                    "question_text": question.get("question_text", ""),
                    "correct_count": 0,
                    "total_count": 0
                }
            
            user_answer = answer_map.get(q_id)
            correct_answer = question.get("correct_answer")
            
            question_stats[q_id]["total_count"] += 1
            if user_answer == correct_answer:
                question_stats[q_id]["correct_count"] += 1
    
    # Calculate correct rate and find hardest questions
    difficult_questions = []
    
    for q_id, stats in question_stats.items():
        total = stats["total_count"]
        correct = stats["correct_count"]
        correct_rate = (correct / total * 100) if total > 0 else 0
        
        difficult_questions.append({
            "question_id": q_id,
            "question_text": stats["question_text"],
            "correct_rate": round(correct_rate, 2),
            "total_answers": total
        })
    
    # Sort by correct_rate ascending (hardest first)
    difficult_questions.sort(key=lambda q: q["correct_rate"])
    difficult_questions = difficult_questions[:3]  # Top 3 hardest
    
    # Get class name
    class_obj = await Class.get(class_id)
    class_name = class_obj.name if class_obj else f"Class {class_id}"
    
    return {
        "quiz_id": quiz_id,
        "quiz_title": quiz.title,
        "class_id": class_id,
        "class_name": class_name,
        "statistics": statistics,
        "score_distribution": score_distribution,
        "student_ranking": student_ranking,
        "difficult_questions": difficult_questions
    }
