"""
Adaptive Learning Service
Xử lý logic cho 3 tính năng:
1. Auto-Skip Module Based on Assessment
2. Adaptive Learning Path
3. Continuous Adaptive Adjustment
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from beanie import PydanticObjectId

from models.models import (
    AssessmentSession, 
    Enrollment, 
    Progress, 
    Course, 
    Module,
    Lesson
)


class AdaptiveLearningService:
    """Service xử lý adaptive learning logic"""
    
    # ========================================================================
    # FEATURE 1: AUTO-SKIP MODULE BASED ON ASSESSMENT
    # ========================================================================
    
    async def apply_assessment_to_enrollment(
        self,
        assessment_session_id: str,
        course_id: str,
        enrollment_id: str,
        skip_threshold: float = 0.85,
        time_threshold: float = 0.50
    ) -> Dict[str, Any]:
        """
        Áp dụng kết quả assessment vào enrollment để auto-skip modules
        
        Args:
            assessment_session_id: ID của assessment session
            course_id: ID của khóa học
            enrollment_id: ID của enrollment
            skip_threshold: Ngưỡng điểm để skip (default 85%)
            time_threshold: Ngưỡng thời gian (default 50% time_limit)
            
        Returns:
            {
                "skipped_modules": [...],
                "recommended_start_module_id": "...",
                "new_progress_percent": 45.0,
                "time_saved_hours": 12.5,
                "message": "..."
            }
        """
        # 1. Lấy assessment results
        assessment = await AssessmentSession.get(assessment_session_id)
        if not assessment:
            raise ValueError(f"Assessment session {assessment_session_id} not found")
        
        # 2. Lấy course và modules
        course = await Course.get(course_id)
        if not course:
            raise ValueError(f"Course {course_id} not found")
        
        # 3. Lấy enrollment
        enrollment = await Enrollment.get(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {enrollment_id} not found")
        
        # 4. Phân tích assessment để quyết định skip modules nào
        skip_analysis = await self._analyze_modules_to_skip(
            assessment=assessment,
            course=course,
            skip_threshold=skip_threshold,
            time_threshold=time_threshold
        )
        
        # 5. Cập nhật enrollment với skipped modules
        skipped_modules_data = []
        total_lessons_skipped = 0
        time_saved_hours = 0.0
        
        for module_decision in skip_analysis["modules_to_skip"]:
            module_id = module_decision["module_id"]
            module = next((m for m in course.modules if str(m.id) == module_id), None)
            
            if module:
                # Đếm lessons trong module
                lessons_count = len(module.lessons)
                total_lessons_skipped += lessons_count
                
                # Tính thời gian tiết kiệm
                for lesson in module.lessons:
                    time_saved_hours += lesson.duration_minutes / 60.0
                
                # Lưu thông tin skip
                skipped_modules_data.append({
                    "module_id": module_id,
                    "module_title": module.title,
                    "skip_reason": module_decision["reason"],
                    "proficiency_score": module_decision["proficiency"],
                    "skipped_at": datetime.utcnow(),
                    "assessment_session_id": assessment_session_id,
                    "lessons_count": lessons_count
                })
        
        # 6. Cập nhật enrollment
        enrollment.adaptive_learning_enabled = True
        enrollment.skipped_modules = skipped_modules_data
        enrollment.recommended_start_module_id = skip_analysis["recommended_start_module_id"]
        
        # 7. Tính progress mới (giả sử skip = completed)
        total_lessons = sum(len(m.lessons) for m in course.modules)
        new_progress = (total_lessons_skipped / total_lessons * 100) if total_lessons > 0 else 0
        enrollment.progress_percent = new_progress
        enrollment.completion_rate = new_progress
        
        await enrollment.save()
        
        # 8. Cập nhật Progress để auto-complete lessons
        progress = await Progress.find_one(Progress.enrollment_id == enrollment_id)
        if progress:
            await self._auto_complete_skipped_lessons(
                progress=progress,
                skipped_modules=skipped_modules_data,
                course=course
            )
        
        return {
            "skipped_modules": skipped_modules_data,
            "recommended_start_module_id": skip_analysis["recommended_start_module_id"],
            "new_progress_percent": round(new_progress, 2),
            "time_saved_hours": round(time_saved_hours, 2),
            "total_lessons_skipped": total_lessons_skipped,
            "message": f"Đã skip {len(skipped_modules_data)} modules, tiết kiệm {round(time_saved_hours, 1)} giờ"
        }

    async def _analyze_modules_to_skip(
        self,
        assessment: AssessmentSession,
        course: Course,
        skip_threshold: float,
        time_threshold: float
    ) -> Dict[str, Any]:
        """
        Phân tích assessment để quyết định skip modules nào

        Logic:
        - Nếu overall_score >= skip_threshold (85%) VÀ time_ratio < time_threshold (50%)
          → Skip các modules Beginner/Easy
        - Tìm module đầu tiên có proficiency < skip_threshold làm recommended_start
        """
        # Kiểm tra điều kiện tổng thể
        overall_score = assessment.overall_score

        # Tính time ratio (nếu có)
        time_ratio = 1.0
        if hasattr(assessment, 'time_taken_seconds') and hasattr(assessment, 'time_limit_seconds'):
            if assessment.time_limit_seconds and assessment.time_limit_seconds > 0:
                time_ratio = assessment.time_taken_seconds / assessment.time_limit_seconds

        modules_to_skip = []
        recommended_start_module_id = None

        # Nếu đạt điều kiện skip
        if overall_score >= skip_threshold * 100 and time_ratio < time_threshold:
            # Phân tích từng module
            for module in course.modules:
                # Tính proficiency cho module này dựa trên skills
                module_proficiency = self._calculate_module_proficiency(
                    assessment=assessment,
                    module=module
                )

                # Quyết định skip hay không
                if module_proficiency >= skip_threshold * 100:
                    modules_to_skip.append({
                        "module_id": str(module.id),
                        "module_title": module.title,
                        "proficiency": module_proficiency,
                        "reason": f"Proficiency {module_proficiency:.0f}% - Đã thành thạo"
                    })
                else:
                    # Module đầu tiên không skip → recommended start
                    if not recommended_start_module_id:
                        recommended_start_module_id = str(module.id)

        # Nếu không có recommended start, lấy module đầu tiên
        if not recommended_start_module_id and course.modules:
            recommended_start_module_id = str(course.modules[0].id)

        return {
            "modules_to_skip": modules_to_skip,
            "recommended_start_module_id": recommended_start_module_id,
            "overall_score": overall_score,
            "time_ratio": time_ratio
        }

    def _calculate_module_proficiency(
        self,
        assessment: AssessmentSession,
        module: Module
    ) -> float:
        """
        Tính proficiency của user cho 1 module dựa trên assessment

        Logic đơn giản:
        - Nếu module có difficulty_level = "beginner" → dùng overall_score
        - Nếu module có difficulty_level = "intermediate" → overall_score * 0.8
        - Nếu module có difficulty_level = "advanced" → overall_score * 0.6

        TODO: Cải thiện bằng cách so sánh skills của module vs skill_analysis
        """
        overall_score = assessment.overall_score

        # Lấy difficulty level của module (nếu có)
        difficulty = getattr(module, 'difficulty_level', 'beginner').lower()

        if difficulty == 'beginner' or difficulty == 'easy':
            return overall_score
        elif difficulty == 'intermediate' or difficulty == 'medium':
            return overall_score * 0.8
        elif difficulty == 'advanced' or difficulty == 'hard':
            return overall_score * 0.6
        else:
            return overall_score

    async def _auto_complete_skipped_lessons(
        self,
        progress: Progress,
        skipped_modules: List[Dict],
        course: Course
    ) -> None:
        """
        Auto-complete tất cả lessons trong skipped modules
        """
        from models.models import LessonProgressItem

        skipped_lesson_ids = []

        for skipped_module in skipped_modules:
            module_id = skipped_module["module_id"]

            # Tìm module trong course
            module = next((m for m in course.modules if str(m.id) == module_id), None)
            if not module:
                continue

            # Auto-complete tất cả lessons trong module
            for lesson in module.lessons:
                lesson_id = str(lesson.id)
                skipped_lesson_ids.append(lesson_id)

                # Kiểm tra xem lesson đã có trong progress chưa
                existing = next(
                    (lp for lp in progress.lessons_progress if lp.lesson_id == lesson_id),
                    None
                )

                if not existing:
                    # Thêm lesson progress mới với status completed
                    progress.lessons_progress.append(LessonProgressItem(
                        lesson_id=lesson_id,
                        lesson_title=lesson.title,
                        status="completed",
                        progress_percent=100.0,
                        completion_date=datetime.utcnow(),
                        time_spent_minutes=0,  # Auto-skip nên không tính thời gian
                        quiz_score=None,  # Không có quiz score
                        last_accessed_at=datetime.utcnow()
                    ))

        # Cập nhật auto_skipped_lessons
        progress.auto_skipped_lessons = skipped_lesson_ids
        progress.learning_path_type = "adaptive"

        # Cập nhật counters
        progress.completed_lessons_count = len([
            lp for lp in progress.lessons_progress if lp.status == "completed"
        ])

        # Tính lại overall progress
        if progress.total_lessons_count > 0:
            progress.overall_progress_percent = (
                progress.completed_lessons_count / progress.total_lessons_count * 100
            )

        progress.updated_at = datetime.utcnow()
        await progress.save()

    # ========================================================================
    # FEATURE 2: ADAPTIVE LEARNING PATH
    # ========================================================================

    async def create_adaptive_path(
        self,
        enrollment_id: str,
        assessment_session_id: str
    ) -> Dict[str, Any]:
        """
        Tạo lộ trình học tập thích ứng với 5 loại quyết định:
        - SKIP: Proficiency >= 85%
        - REVIEW: Proficiency 70-84%
        - START: Proficiency < 70%
        - UNLOCK: User level >= Module level
        - LOCKED: Chưa đủ điều kiện

        Returns:
            {
                "adaptive_path": [
                    {
                        "module_id": "...",
                        "module_title": "...",
                        "decision": "SKIP|REVIEW|START|UNLOCK|LOCKED",
                        "reason": "...",
                        "proficiency_score": 95.0,
                        "estimated_time_hours": 2.5
                    }
                ]
            }
        """
        # 1. Lấy enrollment và assessment
        enrollment = await Enrollment.get(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {enrollment_id} not found")

        assessment = await AssessmentSession.get(assessment_session_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_session_id} not found")

        # 2. Lấy course
        course = await Course.get(enrollment.course_id)
        if not course:
            raise ValueError(f"Course {enrollment.course_id} not found")

        # 3. Tạo adaptive path cho từng module
        adaptive_path = []

        for idx, module in enumerate(course.modules):
            # Tính proficiency cho module
            proficiency = self._calculate_module_proficiency(assessment, module)

            # Quyết định decision
            decision, reason = self._make_module_decision(
                proficiency=proficiency,
                module=module,
                module_index=idx,
                assessment=assessment
            )

            # Tính estimated time
            estimated_hours = sum(
                lesson.duration_minutes for lesson in module.lessons
            ) / 60.0

            adaptive_path.append({
                "module_id": str(module.id),
                "module_title": module.title,
                "decision": decision,
                "reason": reason,
                "proficiency_score": round(proficiency, 2),
                "estimated_time_hours": round(estimated_hours, 2),
                "difficulty_level": getattr(module, 'difficulty_level', 'beginner')
            })

        # 4. Lưu vào enrollment
        enrollment.learning_path_decisions = adaptive_path
        await enrollment.save()

        return {
            "adaptive_path": adaptive_path,
            "total_modules": len(adaptive_path),
            "skip_count": len([p for p in adaptive_path if p["decision"] == "SKIP"]),
            "review_count": len([p for p in adaptive_path if p["decision"] == "REVIEW"]),
            "start_count": len([p for p in adaptive_path if p["decision"] == "START"]),
            "unlock_count": len([p for p in adaptive_path if p["decision"] == "UNLOCK"])
        }

    def _make_module_decision(
        self,
        proficiency: float,
        module: Module,
        module_index: int,
        assessment: AssessmentSession
    ) -> tuple[str, str]:
        """
        Quyết định SKIP | REVIEW | START | UNLOCK | LOCKED cho module

        Returns:
            (decision, reason)
        """
        # SKIP: Proficiency >= 85%
        if proficiency >= 85:
            return ("SKIP", f"Proficiency {proficiency:.0f}% - Đã thành thạo")

        # REVIEW: Proficiency 70-84%
        elif proficiency >= 70:
            return ("REVIEW", f"Proficiency {proficiency:.0f}% - Nên ôn tập nhanh")

        # START: Proficiency < 70%
        elif proficiency < 70:
            # Nếu là module đầu tiên có proficiency thấp → START HERE
            return ("START", f"Proficiency {proficiency:.0f}% - Cần học kỹ")

        # UNLOCK: Nếu user level cao, có thể unlock sớm
        # (Logic đơn giản: nếu overall_score > 80 thì unlock advanced modules)
        elif assessment.overall_score > 80:
            difficulty = getattr(module, 'difficulty_level', 'beginner').lower()
            if difficulty in ['advanced', 'hard']:
                return ("UNLOCK", "Trình độ phù hợp, mở khóa sớm")

        # LOCKED: Mặc định
        return ("LOCKED", "Cần hoàn thành modules trước")

    # ========================================================================
    # FEATURE 3: CONTINUOUS ADAPTIVE ADJUSTMENT
    # ========================================================================

    async def track_and_adjust(
        self,
        user_id: str,
        course_id: str,
        lesson_id: str,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Theo dõi lesson completion và đề xuất điều chỉnh real-time

        Args:
            completion_data: {
                "time_spent_seconds": 600,
                "quiz_score": 95,
                "attempts": 1,
                "completed_at": datetime
            }

        Returns:
            {
                "adjustment_needed": True/False,
                "adjustment_type": "SKIP" | "REVIEW" | "SCHEDULE" | "NONE",
                "suggestion": {...},
                "actions": [...]
            }
        """
        # 1. Lấy lesson info
        lesson = await Lesson.get(lesson_id)
        if not lesson:
            return {"adjustment_needed": False, "adjustment_type": "NONE"}

        # 2. Phân tích performance
        analysis = self._analyze_lesson_performance(lesson, completion_data)

        # 3. Lấy progress để check pattern
        progress = await Progress.find_one(
            Progress.user_id == user_id,
            Progress.course_id == course_id
        )

        if not progress:
            return {"adjustment_needed": False, "adjustment_type": "NONE"}

        # 4. Quyết định adjustment
        adjustment = await self._decide_adjustment(
            analysis=analysis,
            progress=progress,
            lesson=lesson,
            course_id=course_id
        )

        # 5. Lưu vào adjustment history
        if adjustment["adjustment_needed"]:
            progress.adjustment_history.append({
                "adjusted_at": datetime.utcnow(),
                "lesson_id": lesson_id,
                "adjustment_type": adjustment["adjustment_type"],
                "reason": adjustment.get("reason", ""),
                "user_accepted": None  # Sẽ update sau khi user chọn
            })
            await progress.save()

        return adjustment

    def _analyze_lesson_performance(
        self,
        lesson: Lesson,
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Phân tích performance của user trong 1 lesson
        """
        estimated_time = lesson.duration_minutes * 60  # Convert to seconds
        actual_time = completion_data.get("time_spent_seconds", 0)

        # Tính speed ratio
        speed_ratio = actual_time / estimated_time if estimated_time > 0 else 1.0

        return {
            "speed_ratio": speed_ratio,
            "quiz_score": completion_data.get("quiz_score", 0),
            "attempts": completion_data.get("attempts", 1),
            "completed_at": completion_data.get("completed_at", datetime.utcnow()),
            "is_fast": speed_ratio < 0.3,  # Nhanh hơn 3 lần
            "is_slow": speed_ratio > 2.0,  # Chậm hơn 2 lần
            "is_high_score": completion_data.get("quiz_score", 0) >= 90,
            "is_low_score": completion_data.get("quiz_score", 0) < 60,
            "is_struggling": completion_data.get("attempts", 1) >= 3
        }

    async def _decide_adjustment(
        self,
        analysis: Dict[str, Any],
        progress: Progress,
        lesson: Lesson,
        course_id: str
    ) -> Dict[str, Any]:
        """
        Quyết định loại adjustment dựa trên analysis

        5 loại adjustment:
        1. Speed-based: Học nhanh → Skip lessons tiếp
        2. Score-based: Điểm thấp → Review prerequisite
        3. Pattern-based: Học không đều → Tạo schedule
        4. Decay-based: Điểm giảm → Spaced repetition
        5. Difficulty-based: Làm đúng ngay → Tăng độ khó
        """

        # 1. SPEED-BASED: Học rất nhanh + điểm cao
        if analysis["is_fast"] and analysis["is_high_score"]:
            # Tìm 2-3 lessons tiếp theo để suggest skip
            next_lessons = await self._find_next_lessons(
                course_id=course_id,
                current_lesson_id=str(lesson.id),
                count=3
            )

            if next_lessons:
                return {
                    "adjustment_needed": True,
                    "adjustment_type": "SKIP",
                    "reason": f"Bạn hoàn thành trong {analysis['speed_ratio']*100:.0f}% thời gian dự kiến và đạt {analysis['quiz_score']}%",
                    "suggestion": {
                        "title": "🎉 Chúc mừng! Bạn học rất tốt!",
                        "message": f"Đề xuất bỏ qua {len(next_lessons)} lessons tiếp theo",
                        "lessons_to_skip": next_lessons,
                        "time_saved_hours": sum(l["estimated_hours"] for l in next_lessons)
                    },
                    "actions": ["skip_lessons", "update_progress"]
                }

        # 2. SCORE-BASED: Điểm thấp hoặc thử nhiều lần
        if analysis["is_low_score"] or analysis["is_struggling"]:
            return {
                "adjustment_needed": True,
                "adjustment_type": "REVIEW",
                "reason": f"Điểm {analysis['quiz_score']}% sau {analysis['attempts']} lần thử",
                "suggestion": {
                    "title": "⚠️ Cần hỗ trợ",
                    "message": "Bạn đang gặp khó khăn. Hãy review lại kiến thức nền tảng.",
                    "review_lessons": [],  # TODO: Tìm prerequisite lessons
                    "extra_resources": [
                        {"type": "video", "title": "Video hướng dẫn chi tiết"},
                        {"type": "practice", "title": "5 bài tập thực hành"}
                    ]
                },
                "actions": ["show_review_suggestion", "unlock_extra_resources"]
            }

        # 3. PATTERN-BASED: Kiểm tra learning pattern
        pattern = self._detect_learning_pattern(progress)
        if pattern == "inconsistent":
            return {
                "adjustment_needed": True,
                "adjustment_type": "SCHEDULE",
                "reason": "Học không đều đặn",
                "suggestion": {
                    "title": "📊 Đề xuất lịch học",
                    "message": "Học đều đặn 1 giờ/ngày sẽ hiệu quả hơn học dồn.",
                    "schedule": {
                        "daily_goal_minutes": 60,
                        "reminder_time": "19:00",
                        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
                    }
                },
                "actions": ["create_schedule", "enable_reminders"]
            }

        # Không cần adjustment
        return {
            "adjustment_needed": False,
            "adjustment_type": "NONE",
            "message": "Tiếp tục học tốt!"
        }

    async def _find_next_lessons(
        self,
        course_id: str,
        current_lesson_id: str,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Tìm N lessons tiếp theo sau current_lesson
        """
        course = await Course.get(course_id)
        if not course:
            return []

        # Flatten all lessons
        all_lessons = []
        for module in course.modules:
            for lesson in module.lessons:
                all_lessons.append({
                    "lesson_id": str(lesson.id),
                    "lesson_title": lesson.title,
                    "estimated_hours": lesson.duration_minutes / 60.0,
                    "module_title": module.title
                })

        # Tìm index của current lesson
        current_index = next(
            (i for i, l in enumerate(all_lessons) if l["lesson_id"] == current_lesson_id),
            -1
        )

        if current_index == -1:
            return []

        # Lấy N lessons tiếp theo
        next_lessons = all_lessons[current_index + 1 : current_index + 1 + count]
        return next_lessons

    def _detect_learning_pattern(self, progress: Progress) -> str:
        """
        Phát hiện pattern học tập

        Returns:
            "daily_learner" | "regular_learner" | "weekend_learner" | "inconsistent" | "new_learner"
        """
        if not progress.lessons_progress or len(progress.lessons_progress) < 5:
            return "new_learner"

        # Lấy timestamps của các lần học
        access_times = [
            lp.last_accessed_at
            for lp in progress.lessons_progress
            if lp.last_accessed_at
        ]

        if len(access_times) < 2:
            return "new_learner"

        # Sắp xếp theo thời gian
        access_times.sort()

        # Tính khoảng cách giữa các lần học
        gaps = []
        for i in range(1, len(access_times)):
            gap = (access_times[i] - access_times[i-1]).days
            gaps.append(gap)

        if not gaps:
            return "new_learner"

        avg_gap = sum(gaps) / len(gaps)

        # Phân loại
        if avg_gap <= 1:
            return "daily_learner"
        elif avg_gap <= 3:
            return "regular_learner"
        elif avg_gap <= 7:
            return "weekend_learner"
        else:
            return "inconsistent"


# Singleton instance
adaptive_learning_service = AdaptiveLearningService()

