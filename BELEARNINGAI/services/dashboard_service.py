"""
Dashboard Service - Xử lý dashboard và analytics cho student
Sử dụng: Beanie ODM
Tuân thủ: CHUCNANG.md Section 2.7
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models.models import (
    Enrollment, Course, Progress, QuizAttempt, User, Quiz, Class
)


# ============================================================================
# Section 2.7.1: DASHBOARD TỔNG QUAN HỌC VIÊN
# ============================================================================

async def get_student_dashboard(user_id: str) -> Dict:
    """
    Lấy thông tin dashboard tổng quan cho student
    
    Business Logic:
    1. Lấy 3-5 khóa học đang học gần đây nhất (status="active")
    2. Lấy các quiz chưa hoàn thành hoặc sắp đến hạn
    3. Tính progress cho mỗi khóa học
    4. Sort theo last_accessed_at
    
    Args:
        user_id: ID của user
        
    Returns:
        Dict chứa in_progress_courses và pending_quizzes
    """
    # Lấy các enrollment đang active, sort theo last_accessed
    enrollments = await Enrollment.find(
        Enrollment.user_id == user_id,
        Enrollment.status == "active"
    ).sort(-Enrollment.updated_at).limit(5).to_list()
    
    in_progress_courses = []
    for enrollment in enrollments:
        # Lấy course info
        course = await Course.get(enrollment.course_id)
        if not course:
            continue
            
        # Lấy progress
        progress = await Progress.find_one(
            Progress.user_id == user_id,
            Progress.course_id == enrollment.course_id
        )
        
        in_progress_courses.append({
            "course_id": enrollment.course_id,
            "title": course.title,
            "progress": progress.overall_progress_percent if progress else 0.0,
            "last_accessed": progress.last_accessed_at if progress else enrollment.updated_at
        })
    
    # Lấy pending quizzes (chưa hoàn thành hoặc failed)
    # Query quiz attempts với status != "passed"
    pending_quizzes = []
    
    # Lấy tất cả courses user đang enroll
    enrolled_course_ids = [e.course_id for e in enrollments]
    
    for course_id in enrolled_course_ids:
        course = await Course.get(course_id)
        if not course:
            continue
        
        # Check if course has modules
        if not hasattr(course, 'modules') or not course.modules:
            continue
        
        # Iterate qua modules để tìm quiz
        for module in course.modules:
            if module.default_quiz_id:
                # Kiểm tra xem user đã pass quiz này chưa
                latest_attempt = await QuizAttempt.find(
                    QuizAttempt.user_id == user_id,
                    QuizAttempt.quiz_id == module.default_quiz_id
                ).sort(-QuizAttempt.created_at).first_or_none()
                
                # Nếu chưa attempt hoặc chưa pass
                if not latest_attempt or latest_attempt.status != "passed":
                    pending_quizzes.append({
                        "quiz_id": module.default_quiz_id,
                        "title": f"Quiz {module.title}",
                        "course_title": course.title,
                        "due_at": None  # Có thể thêm logic due date nếu cần
                    })
    
    return {
        "in_progress_courses": in_progress_courses,
        "pending_quizzes": pending_quizzes[:10]  # Limit 10 pending quizzes
    }


# ============================================================================
# Section 2.7.2: THỐNG KÊ HỌC TẬP CHI TIẾT
# ============================================================================

async def get_learning_stats(user_id: str) -> Dict:
    """
    Lấy thống kê học tập chi tiết
    
    Business Logic:
    1. Tính tổng lessons đã hoàn thành từ Progress
    2. Đếm quizzes passed/failed từ QuizAttempt
    3. Tính điểm trung bình quiz
    4. Đếm courses theo status (completed/active/cancelled)
    5. Breakdown stats theo từng course
    
    Args:
        user_id: ID của user
        
    Returns:
        Dict chứa các metrics học tập
    """
    # Lấy tất cả enrollments
    enrollments = await Enrollment.find(
        Enrollment.user_id == user_id
    ).to_list()
    
    # Đếm courses theo status
    completed_courses = sum(1 for e in enrollments if e.status == "completed")
    in_progress_courses = sum(1 for e in enrollments if e.status == "active")
    cancelled_courses = sum(1 for e in enrollments if e.status == "cancelled")
    
    # Tính tổng lessons completed
    total_lessons_completed = 0
    course_stats_list = []
    
    for enrollment in enrollments:
        progress = await Progress.find_one(
            Progress.user_id == user_id,
            Progress.course_id == enrollment.course_id
        )
        
        if progress:
            total_lessons_completed += progress.completed_lessons_count
            
            # Get course
            course = await Course.get(enrollment.course_id)
            
            # Get quiz score for this course
            quiz_attempts = await QuizAttempt.find(
                QuizAttempt.user_id == user_id,
                QuizAttempt.course_id == enrollment.course_id
            ).to_list()
            
            # Tính điểm trung bình quiz của course này
            if quiz_attempts:
                course_quiz_score = sum(a.score for a in quiz_attempts) / len(quiz_attempts)
            else:
                course_quiz_score = 0.0
            
            course_stats_list.append({
                "course_id": enrollment.course_id,
                "course_title": course.title if course else "Unknown",
                "lessons_completed": progress.completed_lessons_count,
                "quiz_score": round(course_quiz_score, 2),
                "status": enrollment.status
            })
    
    # Lấy tất cả quiz attempts
    all_quiz_attempts = await QuizAttempt.find(
        QuizAttempt.user_id == user_id
    ).to_list()
    
    # Đếm passed/failed
    quizzes_passed = sum(1 for a in all_quiz_attempts if a.status == "passed")
    quizzes_failed = sum(1 for a in all_quiz_attempts if a.status == "failed")
    
    # Tính điểm trung bình tất cả quiz
    if all_quiz_attempts:
        avg_quiz_score = sum(a.score for a in all_quiz_attempts) / len(all_quiz_attempts)
    else:
        avg_quiz_score = 0.0
    
    return {
        "lessons_completed": total_lessons_completed,
        "quizzes_passed": quizzes_passed,
        "quizzes_failed": quizzes_failed,
        "avg_quiz_score": round(avg_quiz_score, 2),
        "completed_courses": completed_courses,
        "in_progress_courses": in_progress_courses,
        "cancelled_courses": cancelled_courses,
        "by_course": course_stats_list
    }


# ============================================================================
# Section 2.7.3: BIỂU ĐỒ TIẾN ĐỘ THEO THỜI GIAN
# ============================================================================

async def get_progress_chart(
    user_id: str,
    time_range: str = "week",
    course_id: Optional[str] = None
) -> Dict:
    """
    Lấy dữ liệu biểu đồ tiến độ theo thời gian
    
    Business Logic:
    1. Query Progress với time filter
    2. Group data theo ngày/tuần/tháng
    3. Tính lessons completed và hours spent per time unit
    4. Tạo chart data points
    5. Tính summary statistics
    
    Args:
        user_id: ID của user
        time_range: "day" (7 days), "week" (4 weeks), "month" (6 months)
        course_id: Optional filter theo course cụ thể
        
    Returns:
        Dict chứa chart_data và summary
    """
    # Xác định time range
    if time_range == "day":
        days_back = 7
        date_format = "%Y-%m-%d"
    elif time_range == "week":
        days_back = 28  # 4 weeks
        date_format = "%Y-W%W"
    else:  # month
        days_back = 180  # 6 months
        date_format = "%Y-%m"
    
    start_date = datetime.utcnow() - timedelta(days=days_back)
    
    # Query enrollments
    query_filter = {
        "user_id": user_id,
        "updated_at": {"$gte": start_date}
    }
    
    if course_id:
        query_filter["course_id"] = course_id
    
    enrollments = await Enrollment.find(query_filter).to_list()
    
    # Lấy progress cho các enrollments
    course_ids = [e.course_id for e in enrollments]
    
    progress_list = await Progress.find(
        Progress.user_id == user_id,
        Progress.course_id.in_(course_ids),
        Progress.updated_at >= start_date
    ).to_list()
    
    # Group data theo date
    # Vì không có history chi tiết lessons completed theo ngày,
    # ta ước tính dựa trên updated_at và lessons_progress
    date_map = {}
    
    for progress in progress_list:
        # Parse date
        date_key = progress.updated_at.strftime(date_format)
        
        if date_key not in date_map:
            date_map[date_key] = {
                "lessons_completed": 0,
                "hours_spent": 0.0
            }
        
        # Tính lessons completed trong khoảng thời gian
        # (Giả sử progress.completed_lessons_count là cumulative)
        date_map[date_key]["lessons_completed"] += progress.completed_lessons_count
        date_map[date_key]["hours_spent"] += progress.total_time_spent_minutes / 60.0
    
    # Tạo chart data points
    chart_data = []
    total_lessons = 0
    total_hours = 0.0
    
    # Generate dates trong range
    current_date = start_date
    while current_date <= datetime.utcnow():
        date_key = current_date.strftime(date_format)
        
        data = date_map.get(date_key, {"lessons_completed": 0, "hours_spent": 0.0})
        
        chart_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "lessons_completed": data["lessons_completed"],
            "hours_spent": round(data["hours_spent"], 2)
        })
        
        total_lessons += data["lessons_completed"]
        total_hours += data["hours_spent"]
        
        # Increment date
        if time_range == "day":
            current_date += timedelta(days=1)
        elif time_range == "week":
            current_date += timedelta(weeks=1)
        else:  # month
            # Approximate month increment
            current_date += timedelta(days=30)
    
    # Tính summary
    num_periods = len([d for d in chart_data if d["lessons_completed"] > 0])
    avg_per_day = total_lessons / num_periods if num_periods > 0 else 0.0
    
    summary = {
        "total_lessons": total_lessons,
        "total_hours": round(total_hours, 2),
        "avg_per_day": round(avg_per_day, 2)
    }
    
    return {
        "chart_data": chart_data,
        "summary": summary
    }


# ============================================================================
# INSTRUCTOR DASHBOARD (Section 3.4)
# ============================================================================

async def get_instructor_dashboard(instructor_id: str) -> Dict:
    """
    3.4.1: Instructor Dashboard Overview
    
    Business logic:
    - Count active classes (created by instructor)
    - Sum total students across all classes
    - Count quizzes created
    - Calculate avg completion rate across classes
    - Get 3 recent active classes
    - Quick actions
    
    Args:
        instructor_id: ID của instructor
        
    Returns:
        Dict với active_classes_count, total_students, quizzes_created_count, avg_completion_rate, recent_classes, quick_actions
    """
    from models.models import Class, Quiz
    
    # Get instructor's classes
    classes = await Class.find(Class.instructor_id == instructor_id).to_list()
    
    active_classes = [c for c in classes if c.status == "active"]
    active_classes_count = len(active_classes)
    
    # Count total students (enrolled in instructor's courses with classes)
    total_students = 0
    completion_rates = []
    
    for cls in active_classes:
        # Count enrollments for this class
        enrollments = await Enrollment.find(
            Enrollment.course_id == cls.course_id,
            Enrollment.status == "active"
        ).to_list()
        
        total_students += len(enrollments)
        
        # Calculate completion rate for this class
        if enrollments:
            completed = sum(1 for e in enrollments if e.completion_rate >= 100)
            completion_rate = (completed / len(enrollments) * 100)
            completion_rates.append(completion_rate)
    
    avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
    
    # Count quizzes created by instructor
    quizzes = await Quiz.find(Quiz.created_by == instructor_id).to_list()
    quizzes_created_count = len(quizzes)
    
    # Get 3 recent active classes
    recent_classes = sorted(
        active_classes,
        key=lambda c: c.created_at,
        reverse=True
    )[:3]
    
    recent_classes_data = []
    for c in recent_classes:
        # Get actual course title
        course = await Course.get(c.course_id)
        course_title = course.title if course else f"Course {c.course_id}"
        
        recent_classes_data.append({
            "class_id": str(c.id),
            "class_name": c.name,
            "course_title": course_title,
            "student_count": len(await Enrollment.find(
                Enrollment.course_id == c.course_id,
                Enrollment.status == "active"
            ).to_list()),
            "created_at": c.created_at
        })
    
    # Quick actions
    quick_actions = [
        {
            "action_type": "create_quiz",
            "label": "Tạo Quiz Mới",
            "link": "/instructor/quizzes/create",
            "icon": "quiz_icon"
        },
        {
            "action_type": "view_progress",
            "label": "Xem Tiến Độ Lớp",
            "link": "/instructor/analytics/classes",
            "icon": "chart_icon"
        },
        {
            "action_type": "check_attendance",
            "label": "Kiểm Tra Điểm Danh",
            "link": "/instructor/classes/attendance",
            "icon": "attendance_icon"
        }
    ]
    
    return {
        "active_classes_count": active_classes_count,
        "total_students": total_students,
        "quizzes_created_count": quizzes_created_count,
        "avg_completion_rate": round(avg_completion_rate, 2),
        "recent_classes": recent_classes_data,
        "quick_actions": quick_actions
    }


async def get_instructor_class_stats(
    instructor_id: str,
    class_id: Optional[str] = None
) -> Dict:
    """
    3.4.2: Instructor Class Stats
    
    Business logic:
    - List all instructor's classes or filter by class_id
    - For each class: student_count, attendance_rate, avg_progress, quiz_completion
    - Calculate active_students (last 7 days)
    - Aggregate totals
    
    Args:
        instructor_id: ID của instructor
        class_id: Optional filter by specific class
        
    Returns:
        Dict với classes, total_classes, total_students, avg_attendance, avg_completion
    """
    from models.models import Class
    
    # Get instructor's classes
    query_conditions = [Class.instructor_id == instructor_id]
    
    if class_id:
        query_conditions.append(Class.id == class_id)
    
    classes = await Class.find(*query_conditions).to_list()
    
    class_stats = []
    total_students = 0
    all_attendance_rates = []
    all_completion_rates = []
    
    for cls in classes:
        # Get enrollments
        enrollments = await Enrollment.find(
            Enrollment.course_id == cls.course_id,
            Enrollment.status == "active"
        ).to_list()
        
        student_count = len(enrollments)
        total_students += student_count
        
        # Calculate attendance rate (approx from progress updates)
        # Attendance = students with progress updated in last 7 days / total students
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        active_students = 0
        for enrollment in enrollments:
            progress = await Progress.find_one(
                Progress.user_id == enrollment.user_id,
                Progress.course_id == cls.course_id,
                Progress.updated_at >= seven_days_ago
            )
            if progress:
                active_students += 1
        
        attendance_rate = (active_students / student_count * 100) if student_count > 0 else 0
        all_attendance_rates.append(attendance_rate)
        
        # Calculate avg progress
        progress_list = await Progress.find(
            Progress.course_id == cls.course_id
        ).to_list()
        
        avg_progress = sum(p.overall_progress_percent for p in progress_list) / len(progress_list) if progress_list else 0
        all_completion_rates.append(avg_progress)
        
        # Quiz completion rate
        # Get quizzes for this course
        quizzes = await Quiz.find(Quiz.course_id == cls.course_id).to_list()
        
        quiz_completion = 0
        if quizzes and enrollments:
            from models.models import QuizAttempt
            
            total_expected_attempts = len(quizzes) * len(enrollments)
            
            # Count actual completed attempts
            completed_attempts = 0
            for quiz in quizzes:
                attempts = await QuizAttempt.find(
                    QuizAttempt.quiz_id == str(quiz.id),
                    QuizAttempt.submitted_at != None
                ).to_list()
                
                # Count unique students
                unique_students = set(a.user_id for a in attempts)
                completed_attempts += len(unique_students)
            
            quiz_completion = (completed_attempts / total_expected_attempts * 100) if total_expected_attempts > 0 else 0
        
        # Last activity
        last_activity = cls.updated_at
        
        class_stats.append({
            "class_id": str(cls.id),
            "class_name": cls.name,
            "student_count": student_count,
            "attendance_rate": round(attendance_rate, 2),
            "avg_progress": round(avg_progress, 2),
            "quiz_completion_rate": round(quiz_completion, 2),
            "active_students": active_students,
            "last_activity": last_activity
        })
    
    # Aggregates
    avg_attendance = sum(all_attendance_rates) / len(all_attendance_rates) if all_attendance_rates else 0
    avg_completion = sum(all_completion_rates) / len(all_completion_rates) if all_completion_rates else 0
    
    return {
        "classes": class_stats,
        "total_classes": len(classes),
        "total_students": total_students,
        "avg_attendance": round(avg_attendance, 2),
        "avg_completion": round(avg_completion, 2)
    }


async def get_instructor_progress_chart(
    instructor_id: str,
    time_range: str = "week",
    class_id: Optional[str] = None
) -> Dict:
    """
    3.4.3: Instructor Progress Chart
    
    Business logic:
    - Get progress data across instructor's classes
    - Filter by time_range: day (7 days), week (4 weeks), month (6 months)
    - Filter by class_id if provided
    - Track: lessons_completed, quizzes_completed, active_students per time period
    - Create chart_data points
    
    Args:
        instructor_id: ID của instructor
        time_range: "day"|"week"|"month"
        class_id: Optional filter by class
        
    Returns:
        Dict với chart_type, time_range, chart_data, summary
    """
    from models.models import Class, QuizAttempt
    
    # Determine time range
    if time_range == "day":
        days_back = 7
        date_format = "%Y-%m-%d"
    elif time_range == "week":
        days_back = 28
        date_format = "%Y-W%W"
    else:  # month
        days_back = 180
        date_format = "%Y-%m"
    
    start_date = datetime.utcnow() - timedelta(days=days_back)
    
    # Get instructor's classes
    query_conditions = [Class.instructor_id == instructor_id]
    
    if class_id:
        query_conditions.append(Class.id == class_id)
    
    classes = await Class.find(*query_conditions).to_list()
    
    course_ids = [c.course_id for c in classes]
    
    # Get progress data
    progress_list = await Progress.find(
        Progress.course_id.in_(course_ids),
        Progress.updated_at >= start_date
    ).to_list()
    
    # Get quiz attempts
    quizzes = await Quiz.find(
        Quiz.course_id.in_(course_ids)
    ).to_list()
    
    quiz_ids = [str(q.id) for q in quizzes]
    
    quiz_attempts = await QuizAttempt.find(
        QuizAttempt.quiz_id.in_(quiz_ids),
        QuizAttempt.submitted_at >= start_date
    ).to_list()
    
    # Group data by date
    date_map = {}
    
    # Track lessons completed
    for progress in progress_list:
        date_key = progress.updated_at.strftime(date_format)
        
        if date_key not in date_map:
            date_map[date_key] = {
                "lessons_completed": 0,
                "quizzes_completed": 0,
                "active_students": set()
            }
        
        date_map[date_key]["lessons_completed"] += progress.completed_lessons_count
        date_map[date_key]["active_students"].add(progress.user_id)
    
    # Track quiz attempts
    for attempt in quiz_attempts:
        date_key = attempt.submitted_at.strftime(date_format)
        
        if date_key not in date_map:
            date_map[date_key] = {
                "lessons_completed": 0,
                "quizzes_completed": 0,
                "active_students": set()
            }
        
        date_map[date_key]["quizzes_completed"] += 1
        date_map[date_key]["active_students"].add(attempt.user_id)
    
    # Create chart data
    chart_data = []
    total_lessons = 0
    total_quizzes = 0
    all_students = set()
    
    current_date = start_date
    while current_date <= datetime.utcnow():
        date_key = current_date.strftime(date_format)
        
        data = date_map.get(date_key, {
            "lessons_completed": 0,
            "quizzes_completed": 0,
            "active_students": set()
        })
        
        chart_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "class_id": class_id,
            "class_name": classes[0].name if class_id and classes else None,
            "lessons_completed": data["lessons_completed"],
            "quizzes_completed": data["quizzes_completed"],
            "active_students": len(data["active_students"])
        })
        
        total_lessons += data["lessons_completed"]
        total_quizzes += data["quizzes_completed"]
        all_students.update(data["active_students"])
        
        # Increment date
        if time_range == "day":
            current_date += timedelta(days=1)
        elif time_range == "week":
            current_date += timedelta(weeks=1)
        else:
            current_date += timedelta(days=30)
    
    summary = {
        "total_lessons": total_lessons,
        "total_quizzes": total_quizzes,
        "total_students": len(all_students)
    }
    
    return {
        "chart_type": "line",
        "time_range": time_range,
        "chart_data": chart_data,
        "summary": summary
    }


async def get_instructor_quiz_performance(instructor_id: str) -> Dict:
    """
    3.4.4: Instructor Quiz Performance Analytics
    
    Business logic:
    - Get all quizzes created by instructor
    - For each quiz: calculate total_attempts, pass_count, fail_count, pass_rate, avg_score, avg_time
    - Find hardest questions (top 3 lowest correct rate)
    - Calculate overall statistics
    - Build score distribution
    
    Args:
        instructor_id: ID của instructor
        
    Returns:
        Dict với quizzes, total_quizzes, total_attempts, overall_pass_rate, avg_score, score_distribution
    """
    from models.models import Quiz, QuizAttempt, Course
    
    # Get instructor's quizzes
    quizzes = await Quiz.find(Quiz.created_by == instructor_id).to_list()
    
    quiz_performance_items = []
    total_attempts = 0
    all_scores = []
    all_pass_count = 0
    
    for quiz in quizzes:
        # Get quiz attempts
        attempts = await QuizAttempt.find(
            QuizAttempt.quiz_id == str(quiz.id),
            QuizAttempt.submitted_at != None
        ).to_list()
        
        quiz_total_attempts = len(attempts)
        total_attempts += quiz_total_attempts
        
        if quiz_total_attempts == 0:
            continue
        
        pass_count = sum(1 for a in attempts if a.passed)
        fail_count = quiz_total_attempts - pass_count
        pass_rate = (pass_count / quiz_total_attempts * 100)
        
        all_pass_count += pass_count
        
        scores = [a.score for a in attempts]
        avg_score = sum(scores) / len(scores)
        all_scores.extend(scores)
        
        times = [a.time_spent_seconds / 60 for a in attempts]
        avg_time_minutes = sum(times) / len(times)
        
        # Find hardest questions
        question_stats = {}
        
        for attempt in attempts:
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
        
        hardest_questions = []
        for q_id, stats in question_stats.items():
            total = stats["total_count"]
            correct = stats["correct_count"]
            correct_rate = (correct / total * 100) if total > 0 else 0
            
            hardest_questions.append({
                "question_id": q_id,
                "question_text": stats["question_text"],
                "correct_rate": round(correct_rate, 2)
            })
        
        hardest_questions.sort(key=lambda q: q["correct_rate"])
        hardest_questions = hardest_questions[:3]
        
        # Get course title and class name if available
        course = await Course.get(quiz.course_id) if quiz.course_id else None
        course_title = course.title if course else "N/A"
        
        # Try to get class name from quiz's course
        class_obj = None
        if quiz.course_id:
            class_obj = await Class.find_one(Class.course_id == quiz.course_id)
        class_name = class_obj.name if class_obj else None
        
        quiz_performance_items.append({
            "quiz_id": str(quiz.id),
            "quiz_title": quiz.title,
            "course_title": course_title,
            "class_name": class_name,
            "total_attempts": quiz_total_attempts,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": round(pass_rate, 2),
            "avg_score": round(avg_score, 2),
            "avg_time_minutes": round(avg_time_minutes, 2),
            "hardest_questions": hardest_questions,
            "created_at": quiz.created_at
        })
    
    # Overall statistics
    overall_pass_rate = (all_pass_count / total_attempts * 100) if total_attempts > 0 else 0
    overall_avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # Score distribution
    score_distribution = []
    ranges = [(i, i + 10) for i in range(0, 100, 10)]
    
    for start, end in ranges:
        count = sum(1 for s in all_scores if start <= s < end)
        percentage = (count / len(all_scores) * 100) if all_scores else 0
        
        score_distribution.append({
            "range": f"{start}-{end-1}" if end < 100 else f"{start}-100",
            "count": count,
            "percentage": round(percentage, 2)
        })
    
    return {
        "quizzes": quiz_performance_items,
        "total_quizzes": len(quizzes),
        "total_attempts": total_attempts,
        "overall_pass_rate": round(overall_pass_rate, 2),
        "avg_score": round(overall_avg_score, 2),
        "score_distribution": score_distribution
    }


# ============================================================================
# Section 4.4: ADMIN DASHBOARD & ANALYTICS
# ============================================================================

async def get_admin_system_dashboard() -> Dict:
    """
    Lấy dashboard tổng quan hệ thống cho admin
    
    Business Logic:
    1. Count users theo từng role (student, instructor, admin)
    2. Count courses theo status (active, draft, archived)
    3. Count enrollments trong 30 ngày gần đây
    4. Tính metrics quan trọng: completion rate, active users
    
    Returns:
        Dict chứa system dashboard data
    """
    # Users breakdown by role
    total_users = await User.count()
    students_count = await User.find(User.role == "student").count()
    instructors_count = await User.find(User.role == "instructor").count() 
    admins_count = await User.find(User.role == "admin").count()
    
    # Courses breakdown by status
    total_courses = await Course.count()
    active_courses = await Course.find(Course.status == "published").count()
    draft_courses = await Course.find(Course.status == "draft").count()
    
    # Enrollments in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_enrollments = await Enrollment.find(
        Enrollment.created_at >= thirty_days_ago
    ).count()
    
    # Active users (có activity trong 7 ngày gần đây)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = await User.find(
        User.last_login >= seven_days_ago
    ).count()
    
    # Course completion rate (tính trung bình)
    all_enrollments = await Enrollment.find().to_list()
    completed_enrollments = len([e for e in all_enrollments if e.status == "completed"])
    completion_rate = (completed_enrollments / len(all_enrollments) * 100) if all_enrollments else 0
    
    return {
        "total_users": total_users,
        "users_by_role": {
            "students": students_count,
            "instructors": instructors_count,
            "admins": admins_count
        },
        "total_courses": total_courses,
        "courses_by_status": {
            "active": active_courses,
            "draft": draft_courses
        },
        "recent_enrollments": recent_enrollments,
        "active_users_7d": active_users,
        "completion_rate": round(completion_rate, 2),
        "generated_at": datetime.utcnow().isoformat()
    }


async def get_users_growth_analytics(time_range: str, role_filter: Optional[str] = None) -> Dict:
    """
    Thống kê tăng trưởng người dùng theo thời gian
    
    Business Logic:
    1. Tạo time series data cho khoảng thời gian được chọn
    2. Group users theo ngày tạo tài khoản
    3. Breakdown theo role nếu có filter
    4. Tính growth rate và tổng users
    
    Args:
        time_range: "7d", "30d", "90d"
        role_filter: Optional role filter
        
    Returns:
        Dict chứa chart data và statistics
    """
    # Calculate date range
    days = {"7d": 7, "30d": 30, "90d": 90}[time_range]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Base filter query
    query_filter = {"created_at": {"$gte": start_date}}
    if role_filter:
        query_filter["role"] = role_filter
    
    # Aggregate users by date
    pipeline = [
        {"$match": query_filter},
        {
            "$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "role": "$role" if not role_filter else None
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.date": 1}}
    ]
    
    # Remove None values from grouping if role_filter is provided
    if role_filter:
        pipeline[1]["$group"]["_id"] = {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}}
    
    users_data = await User.aggregate(pipeline).to_list()
    
    # Process chart data
    chart_data = []
    total_new_users = 0
    
    # Create data points for each day
    for user_data in users_data:
        date = user_data["_id"]["date"]
        count = user_data["count"]
        total_new_users += count
        
        chart_data.append({
            "date": date,
            "users": count,
            "role": user_data["_id"].get("role") if not role_filter else role_filter
        })
    
    # Calculate growth rate (compare with previous period)
    prev_start_date = start_date - timedelta(days=days)
    prev_query = {"created_at": {"$gte": prev_start_date, "$lt": start_date}}
    if role_filter:
        prev_query["role"] = role_filter
    
    prev_period_users = await User.find(prev_query).count()
    growth_rate = ((total_new_users - prev_period_users) / prev_period_users * 100) if prev_period_users > 0 else 0
    
    return {
        "chart_data": chart_data,
        "statistics": {
            "total_new_users": total_new_users,
            "growth_rate": round(growth_rate, 2),
            "period": time_range,
            "role_filter": role_filter
        },
        "generated_at": datetime.utcnow().isoformat()
    }


async def get_course_analytics(time_range: str, category_filter: Optional[str] = None) -> Dict:
    """
    Phân tích khóa học chuyên sâu
    
    Business Logic:
    1. Top courses theo enrollment count
    2. Completion rates của các khóa học
    3. Trends tạo khóa học mới
    4. Performance metrics
    
    Args:
        time_range: "7d", "30d", "90d"
        category_filter: Optional category filter
        
    Returns:
        Dict chứa course analytics data
    """
    # Calculate date range
    days = {"7d": 7, "30d": 30, "90d": 90}[time_range]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Base query
    course_query = {"created_at": {"$gte": start_date}}
    if category_filter:
        course_query["category"] = category_filter
    
    # Get top courses by enrollment
    enrollment_pipeline = [
        {"$match": {"created_at": {"$gte": start_date}}},
        {"$group": {"_id": "$course_id", "enrollments": {"$sum": 1}}},
        {"$sort": {"enrollments": -1}},
        {"$limit": 10}
    ]
    
    top_enrollments = await Enrollment.aggregate(enrollment_pipeline).to_list()
    
    top_courses = []
    for enrollment_data in top_enrollments:
        course = await Course.get(enrollment_data["_id"])
        if course and (not category_filter or course.category == category_filter):
            # Calculate completion rate for this course
            course_enrollments = await Enrollment.find(
                Enrollment.course_id == enrollment_data["_id"]
            ).to_list()
            completed = len([e for e in course_enrollments if e.status == "completed"])
            completion_rate = (completed / len(course_enrollments) * 100) if course_enrollments else 0
            
            top_courses.append({
                "course_id": str(course.id),
                "title": course.title,
                "instructor_name": course.instructor_name,
                "category": course.category,
                "enrollments": enrollment_data["enrollments"],
                "completion_rate": round(completion_rate, 2)
            })
    
    # Course creation trends
    creation_pipeline = [
        {"$match": course_query},
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "courses_created": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    creation_trends = await Course.aggregate(creation_pipeline).to_list()
    creation_chart = [{"date": item["_id"], "courses": item["courses_created"]} for item in creation_trends]
    
    # Overall statistics
    total_courses_period = await Course.find(course_query).count()
    
    # Calculate average completion rate
    all_courses = await Course.find(course_query).to_list()
    total_completion_rate = 0
    course_count = 0
    
    for course in all_courses:
        course_enrollments = await Enrollment.find(Enrollment.course_id == course.id).to_list()
        if course_enrollments:
            completed = len([e for e in course_enrollments if e.status == "completed"])
            completion_rate = completed / len(course_enrollments) * 100
            total_completion_rate += completion_rate
            course_count += 1
    
    avg_completion_rate = (total_completion_rate / course_count) if course_count > 0 else 0
    
    return {
        "top_courses": top_courses,
        "creation_trends": creation_chart,
        "statistics": {
            "total_courses_created": total_courses_period,
            "avg_completion_rate": round(avg_completion_rate, 2),
            "period": time_range,
            "category_filter": category_filter
        },
        "generated_at": datetime.utcnow().isoformat()
    }


async def get_system_health() -> Dict:
    """
    Giám sát sức khỏe hệ thống
    
    Business Logic:
    1. Database metrics (collection counts, recent activity)
    2. Performance metrics (average response times)
    3. Alert conditions (low activity, failed operations)
    4. System utilization
    
    Returns:
        Dict chứa system health metrics
    """
    # Database metrics
    users_count = await User.count()
    courses_count = await Course.count()
    enrollments_count = await Enrollment.count()
    quizzes_count = await Quiz.count()
    
    # Recent activity (last 24 hours)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_users = await User.find(User.created_at >= last_24h).count()
    recent_enrollments = await Enrollment.find(Enrollment.created_at >= last_24h).count()
    recent_quiz_attempts = await QuizAttempt.find(QuizAttempt.created_at >= last_24h).count()
    
    # Active users (last 7 days)
    last_7d = datetime.utcnow() - timedelta(days=7)
    active_users = await User.find(User.last_login >= last_7d).count()
    
    # Calculate health scores (0-100)
    user_activity_score = min((active_users / users_count * 100) if users_count > 0 else 0, 100)
    course_utilization = min((enrollments_count / courses_count * 10) if courses_count > 0 else 0, 100)
    
    # System alerts
    alerts = []
    
    if user_activity_score < 20:
        alerts.append({
            "level": "warning",
            "message": "Tỷ lệ người dùng hoạt động thấp",
            "metric": "user_activity",
            "value": round(user_activity_score, 2)
        })
    
    if recent_enrollments < 5:
        alerts.append({
            "level": "info", 
            "message": "Số lượng đăng ký mới trong 24h thấp",
            "metric": "enrollments_24h",
            "value": recent_enrollments
        })
    
    if course_utilization < 50:
        alerts.append({
            "level": "warning",
            "message": "Tỷ lệ sử dụng khóa học thấp",
            "metric": "course_utilization",
            "value": round(course_utilization, 2)
        })
    
    # Overall health score
    overall_health = (user_activity_score + course_utilization) / 2
    
    return {
        "database_metrics": {
            "users": users_count,
            "courses": courses_count,
            "enrollments": enrollments_count,
            "quizzes": quizzes_count
        },
        "activity_metrics": {
            "new_users_24h": recent_users,
            "new_enrollments_24h": recent_enrollments,
            "quiz_attempts_24h": recent_quiz_attempts,
            "active_users_7d": active_users
        },
        "health_scores": {
            "user_activity": round(user_activity_score, 2),
            "course_utilization": round(course_utilization, 2),
            "overall": round(overall_health, 2)
        },
        "alerts": alerts,
        "status": "healthy" if overall_health >= 70 else "warning" if overall_health >= 40 else "critical",
        "generated_at": datetime.utcnow().isoformat()
    }
