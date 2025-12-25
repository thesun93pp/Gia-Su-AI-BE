"""
Adaptive Learning Router
API endpoints cho 3 tính năng adaptive learning
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.adaptive_learning_service import adaptive_learning_service
from routers.auth_router import get_current_user
from models.models import User

router = APIRouter(prefix="/api/v1/adaptive-learning", tags=["Adaptive Learning"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class ApplyAssessmentRequest(BaseModel):
    """Request để áp dụng assessment vào enrollment"""
    assessment_session_id: str = Field(
        ...,
        description="ID của assessment session (lấy từ response của POST /api/v1/assessments/generate)",
        examples=["674d1a2b3c4d5e6f7a8b9c0d"]
    )
    course_id: str = Field(
        ...,
        description="ID của khóa học (lấy từ GET /api/v1/courses)",
        examples=["674b8e9f8a7c6d5e4f3a2b1c"]
    )
    enrollment_id: str = Field(
        ...,
        description="ID của enrollment (lấy từ POST /api/v1/enrollments)",
        examples=["674c9f1a2b3c4d5e6f7a8b9c"]
    )
    skip_threshold: float = Field(
        0.85,
        description="Ngưỡng điểm để skip (0-1). Mặc định: 0.85 = 85%",
        ge=0,
        le=1,
        examples=[0.85]
    )
    time_threshold: float = Field(
        0.50,
        description="Ngưỡng thời gian (0-1). Mặc định: 0.50 = 50%",
        ge=0,
        le=1,
        examples=[0.50]
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "assessment_session_id": "674d1a2b3c4d5e6f7a8b9c0d",
                    "course_id": "674b8e9f8a7c6d5e4f3a2b1c",
                    "enrollment_id": "674c9f1a2b3c4d5e6f7a8b9c",
                    "skip_threshold": 0.85,
                    "time_threshold": 0.50
                }
            ]
        }


class ApplyAssessmentResponse(BaseModel):
    """Response sau khi apply assessment"""
    success: bool
    message: str
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Đã skip 2 modules, tiết kiệm 8.5 giờ",
                "data": {
                    "skipped_modules": [
                        {
                            "module_id": "module-1",
                            "module_title": "Python Basics",
                            "skip_reason": "assessment_proficiency_high",
                            "proficiency_score": 95.0,
                            "estimated_time_hours": 4.0
                        }
                    ],
                    "recommended_start_module_id": "module-3",
                    "new_progress_percent": 35.5,
                    "time_saved_hours": 8.5,
                    "total_lessons_skipped": 12
                }
            }
        }


class AdaptivePathRequest(BaseModel):
    """Request để tạo adaptive path"""
    enrollment_id: str = Field(
        ...,
        description="ID của enrollment (lấy từ POST /api/v1/enrollments)",
        examples=["674c9f1a2b3c4d5e6f7a8b9c"]
    )
    assessment_session_id: str = Field(
        ...,
        description="ID của assessment session (lấy từ POST /api/v1/assessments/generate)",
        examples=["674d1a2b3c4d5e6f7a8b9c0d"]
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "enrollment_id": "674c9f1a2b3c4d5e6f7a8b9c",
                    "assessment_session_id": "674d1a2b3c4d5e6f7a8b9c0d"
                }
            ]
        }


class AdaptivePathResponse(BaseModel):
    """Response chứa adaptive path"""
    success: bool
    adaptive_path: List[Dict[str, Any]]
    summary: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "adaptive_path": [
                    {
                        "module_id": "module-1",
                        "module_title": "Python Basics",
                        "decision": "SKIP",
                        "reason": "Proficiency 95% - Đã thành thạo",
                        "proficiency_score": 95.0,
                        "estimated_time_hours": 4.0
                    },
                    {
                        "module_id": "module-2",
                        "module_title": "Control Flow",
                        "decision": "REVIEW",
                        "reason": "Proficiency 75% - Nên ôn lại",
                        "proficiency_score": 75.0,
                        "estimated_time_hours": 2.0
                    },
                    {
                        "module_id": "module-3",
                        "module_title": "OOP Advanced",
                        "decision": "START",
                        "reason": "Proficiency 45% - Lỗ hổng kiến thức",
                        "proficiency_score": 45.0,
                        "estimated_time_hours": 6.0
                    }
                ],
                "summary": {
                    "total_modules": 5,
                    "skip_count": 1,
                    "review_count": 1,
                    "start_count": 2,
                    "unlock_count": 1
                }
            }
        }


class TrackCompletionRequest(BaseModel):
    """Request để track lesson completion"""
    course_id: str = Field(
        ...,
        description="ID của khóa học (lấy từ GET /api/v1/courses)",
        examples=["674b8e9f8a7c6d5e4f3a2b1c"]
    )
    lesson_id: str = Field(
        ...,
        description="ID của lesson vừa hoàn thành",
        examples=["674e1a2b3c4d5e6f7a8b9c0d"]
    )
    time_spent_seconds: int = Field(
        ...,
        description="Thời gian học (giây). VD: 600 = 10 phút (fast), 7200 = 2 giờ (slow)",
        examples=[600]
    )
    quiz_score: Optional[float] = Field(
        None,
        description="Điểm quiz (0-100). VD: 95 = cao, 55 = thấp",
        examples=[95.0]
    )
    attempts: int = Field(
        1,
        description="Số lần thử. VD: 1 = pass ngay, 3 = nhiều lần",
        examples=[1]
    )
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "course_id": "674b8e9f8a7c6d5e4f3a2b1c",
                    "lesson_id": "674e1a2b3c4d5e6f7a8b9c0d",
                    "time_spent_seconds": 600,
                    "quiz_score": 95.0,
                    "attempts": 1
                },
                {
                    "course_id": "674b8e9f8a7c6d5e4f3a2b1c",
                    "lesson_id": "674e1a2b3c4d5e6f7a8b9c0d",
                    "time_spent_seconds": 7200,
                    "quiz_score": 55.0,
                    "attempts": 3
                }
            ]
        }


class TrackCompletionResponse(BaseModel):
    """Response sau khi track completion"""
    success: bool
    adjustment: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "adjustment": {
                    "adjustment_needed": True,
                    "adjustment_type": "SKIP",
                    "reason": "Học nhanh hơn dự kiến 70%",
                    "suggestion": {
                        "title": "🎉 Bạn học rất tốt!",
                        "message": "Bạn hoàn thành nhanh hơn 70% so với dự kiến. Đề xuất bỏ qua 2-3 lessons tiếp theo.",
                        "lessons_to_skip": ["lesson-2", "lesson-3"],
                        "time_saved_hours": 4.0
                    },
                    "actions": ["skip_next_lessons", "unlock_advanced_content"]
                }
            }
        }


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "/apply-assessment",
    response_model=ApplyAssessmentResponse,
    summary="[Feature 1] Áp dụng assessment để auto-skip modules",
    description="""
    Sau khi user làm assessment, áp dụng kết quả để:
    - Auto-skip modules đã thành thạo
    - Đề xuất module bắt đầu học
    - Cập nhật progress ngay lập tức
    
    Điều kiện skip:
    - Assessment score >= skip_threshold (default 85%)
    - Time taken < time_threshold (default 50% time limit)
    """
)
async def apply_assessment_to_enrollment(
    request: ApplyAssessmentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Feature 1: Auto-Skip Module Based on Assessment
    """
    try:
        result = await adaptive_learning_service.apply_assessment_to_enrollment(
            assessment_session_id=request.assessment_session_id,
            course_id=request.course_id,
            enrollment_id=request.enrollment_id,
            skip_threshold=request.skip_threshold,
            time_threshold=request.time_threshold
        )
        
        return ApplyAssessmentResponse(
            success=True,
            message=result["message"],
            data=result
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying assessment: {str(e)}"
        )


@router.post(
    "/create-adaptive-path",
    response_model=AdaptivePathResponse,
    summary="[Feature 2] Tạo lộ trình học tập thích ứng",
    description="""
    Tạo lộ trình cá nhân hóa với 5 loại quyết định:
    - SKIP: Proficiency >= 85% - Auto-complete module
    - REVIEW: Proficiency 70-84% - Đề xuất ôn tập (optional)
    - START: Proficiency < 70% - Bắt buộc học kỹ
    - UNLOCK: User level cao - Mở khóa sớm
    - LOCKED: Chưa đủ điều kiện
    """
)
async def create_adaptive_path(
    request: AdaptivePathRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Feature 2: Adaptive Learning Path
    """
    try:
        result = await adaptive_learning_service.create_adaptive_path(
            enrollment_id=request.enrollment_id,
            assessment_session_id=request.assessment_session_id
        )
        
        return AdaptivePathResponse(
            success=True,
            adaptive_path=result["adaptive_path"],
            summary={
                "total_modules": result["total_modules"],
                "skip_count": result["skip_count"],
                "review_count": result["review_count"],
                "start_count": result["start_count"],
                "unlock_count": result["unlock_count"]
            }
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating adaptive path: {str(e)}"
        )


@router.post(
    "/track-completion",
    response_model=TrackCompletionResponse,
    summary="[Feature 3] Theo dõi và điều chỉnh real-time",
    description="""
    Theo dõi khi user hoàn thành lesson và đề xuất điều chỉnh:

    5 loại điều chỉnh:
    - Speed-based: Học nhanh → Đề xuất skip lessons tiếp
    - Score-based: Điểm thấp → Đề xuất review
    - Pattern-based: Học không đều → Tạo lịch học
    - Decay-based: Điểm giảm → Spaced repetition
    - Difficulty-based: Làm đúng ngay → Tăng độ khó
    """
)
async def track_lesson_completion(
    request: TrackCompletionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Feature 3: Continuous Adaptive Adjustment
    """
    try:
        completion_data = {
            "time_spent_seconds": request.time_spent_seconds,
            "quiz_score": request.quiz_score,
            "attempts": request.attempts,
            "completed_at": request.completed_at or datetime.utcnow()
        }

        adjustment = await adaptive_learning_service.track_and_adjust(
            user_id=str(current_user.id),
            course_id=request.course_id,
            lesson_id=request.lesson_id,
            completion_data=completion_data
        )

        return TrackCompletionResponse(
            success=True,
            adjustment=adjustment
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking completion: {str(e)}"
        )


@router.post(
    "/accept-adjustment/{enrollment_id}",
    summary="User chấp nhận đề xuất điều chỉnh"
)
async def accept_adjustment(
    enrollment_id: str,
    adjustment_type: str,
    accepted: bool,
    current_user: User = Depends(get_current_user)
):
    """Cập nhật khi user accept/reject adjustment"""
    try:
        from models.models import Progress

        progress = await Progress.find_one(Progress.enrollment_id == enrollment_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")

        if progress.adjustment_history:
            last_adjustment = progress.adjustment_history[-1]
            if last_adjustment.get("adjustment_type") == adjustment_type:
                last_adjustment["user_accepted"] = accepted
                last_adjustment["accepted_at"] = datetime.utcnow()
                await progress.save()

        return {"success": True, "message": "Đã cập nhật"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/enrollment/{enrollment_id}/adaptive-info",
    summary="Lấy thông tin adaptive learning"
)
async def get_adaptive_info(
    enrollment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Xem thông tin adaptive learning của enrollment"""
    try:
        from models.models import Enrollment, Progress

        enrollment = await Enrollment.get(enrollment_id)
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        progress = await Progress.find_one(Progress.enrollment_id == enrollment_id)

        return {
            "success": True,
            "data": {
                "adaptive_learning_enabled": enrollment.adaptive_learning_enabled,
                "skipped_modules": enrollment.skipped_modules,
                "recommended_start_module_id": enrollment.recommended_start_module_id,
                "learning_path_decisions": enrollment.learning_path_decisions,
                "learning_path_type": progress.learning_path_type if progress else "sequential",
                "auto_skipped_lessons": progress.auto_skipped_lessons if progress else [],
                "adjustment_history": progress.adjustment_history if progress else []
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

