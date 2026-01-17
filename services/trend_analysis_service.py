"""
Trend Analysis Service
Phân tích xu hướng học tập và phát hiện điểm cần can thiệp
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from models.models import SkillProficiencyTracking, QuizAttempt, LearningSession
from beanie.operators import GTE


# ============================================================================
# TREND DETECTION
# ============================================================================

async def analyze_student_trends(
    user_id: str,
    course_id: str,
    time_window_days: int = 30
) -> Dict[str, Any]:
    """
    Phân tích xu hướng học tập của student trong time window
    
    Args:
        user_id: UUID user
        course_id: UUID course
        time_window_days: Số ngày để phân tích (default 30)
        
    Returns:
        {
            "overall_trend": {
                "direction": "improving|declining|stable|fluctuating",
                "velocity": float,  # % change per week
                "confidence": float,  # 0-1
                "prediction_next_week": float
            },
            "skill_trends": [
                {
                    "skill_tag": str,
                    "trend": "improving|declining|stable",
                    "velocity": float,
                    "current_proficiency": float,
                    "predicted_proficiency_7d": float,
                    "risk_level": "high|medium|low|none"
                }
            ],
            "engagement_trend": {
                "direction": "increasing|decreasing|stable",
                "avg_sessions_per_week": float,
                "avg_quiz_attempts_per_week": float,
                "last_activity": datetime
            },
            "intervention_needed": bool,
            "intervention_alerts": [...]
        }
    """
    # Get cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
    
    # 1. Analyze skill proficiency trends
    skills = await SkillProficiencyTracking.find(
        SkillProficiencyTracking.user_id == user_id,
        SkillProficiencyTracking.course_id == course_id
    ).to_list()
    
    skill_trends = []
    declining_skills = []
    
    for skill in skills:
        trend_data = _analyze_skill_trend(skill)
        skill_trends.append(trend_data)
        
        if trend_data["trend"] == "declining" and trend_data["risk_level"] in ["high", "medium"]:
            declining_skills.append(trend_data)
    
    # 2. Calculate overall trend
    overall_trend = _calculate_overall_trend(skills)
    
    # 3. Analyze engagement trend
    engagement_trend = await _analyze_engagement_trend(user_id, course_id, cutoff_date)
    
    # 4. Determine if intervention needed
    intervention_needed = (
        overall_trend["direction"] == "declining" or
        len(declining_skills) >= 3 or
        engagement_trend["direction"] == "decreasing"
    )
    
    # 5. Generate intervention alerts
    intervention_alerts = []
    if intervention_needed:
        intervention_alerts = _generate_intervention_alerts(
            overall_trend,
            declining_skills,
            engagement_trend
        )
    
    return {
        "user_id": user_id,
        "course_id": course_id,
        "time_window_days": time_window_days,
        "overall_trend": overall_trend,
        "skill_trends": skill_trends,
        "engagement_trend": engagement_trend,
        "intervention_needed": intervention_needed,
        "intervention_alerts": intervention_alerts,
        "analyzed_at": datetime.utcnow()
    }


def _analyze_skill_trend(skill: SkillProficiencyTracking) -> Dict[str, Any]:
    """
    Phân tích trend của một skill dựa trên attempt history
    
    Uses linear regression to calculate trend velocity
    """
    history = skill.attempt_history
    
    if len(history) < 2:
        return {
            "skill_tag": skill.skill_tag,
            "trend": "insufficient_data",
            "velocity": 0.0,
            "current_proficiency": skill.current_proficiency,
            "predicted_proficiency_7d": skill.current_proficiency,
            "risk_level": "none"
        }
    
    # Calculate velocity using linear regression
    velocity = _calculate_velocity(history)
    
    # Predict proficiency in 7 days
    predicted_7d = skill.current_proficiency + (velocity * 7)
    predicted_7d = max(0, min(100, predicted_7d))  # Clamp to 0-100
    
    # Determine trend direction
    if velocity > 1.0:
        trend = "improving"
    elif velocity < -1.0:
        trend = "declining"
    else:
        trend = "stable"
    
    # Calculate risk level
    risk_level = _calculate_risk_level(
        skill.current_proficiency,
        velocity,
        skill.consecutive_fails
    )
    
    return {
        "skill_tag": skill.skill_tag,
        "trend": trend,
        "velocity": round(velocity, 2),
        "current_proficiency": round(skill.current_proficiency, 2),
        "predicted_proficiency_7d": round(predicted_7d, 2),
        "risk_level": risk_level,
        "consecutive_fails": skill.consecutive_fails,
        "total_attempts": skill.total_attempts
    }


def _calculate_velocity(history: List[Any]) -> float:
    """
    Calculate velocity (rate of change) using linear regression

    Returns: % change per day
    """
    if len(history) < 2:
        return 0.0

    # Sort by timestamp
    sorted_history = sorted(history, key=lambda h: h.timestamp)

    # Use last 10 attempts for trend calculation
    recent_history = sorted_history[-10:]

    if len(recent_history) < 2:
        return 0.0

    # Simple linear regression
    n = len(recent_history)

    # Convert timestamps to days from first attempt
    first_timestamp = recent_history[0].timestamp
    x_values = [(h.timestamp - first_timestamp).total_seconds() / 86400 for h in recent_history]
    y_values = [h.proficiency_after for h in recent_history]

    # Calculate slope (velocity)
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n

    numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
    denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return 0.0

    slope = numerator / denominator  # % change per day

    return slope


def _calculate_risk_level(
    current_proficiency: float,
    velocity: float,
    consecutive_fails: int
) -> str:
    """
    Calculate risk level based on proficiency, velocity, and fails

    Returns: "high"|"medium"|"low"|"none"
    """
    # High risk: declining + low proficiency + consecutive fails
    if velocity < -2.0 and current_proficiency < 50 and consecutive_fails >= 2:
        return "high"

    # Medium risk: declining + low proficiency OR many consecutive fails
    if (velocity < -1.0 and current_proficiency < 60) or consecutive_fails >= 3:
        return "medium"

    # Low risk: declining but still acceptable proficiency
    if velocity < -0.5 and current_proficiency < 70:
        return "low"

    return "none"


def _calculate_overall_trend(skills: List[SkillProficiencyTracking]) -> Dict[str, Any]:
    """
    Calculate overall trend across all skills
    """
    if not skills:
        return {
            "direction": "insufficient_data",
            "velocity": 0.0,
            "confidence": 0.0,
            "prediction_next_week": 0.0
        }

    # Calculate average proficiency trend
    velocities = []
    for skill in skills:
        if len(skill.attempt_history) >= 2:
            velocity = _calculate_velocity(skill.attempt_history)
            velocities.append(velocity)

    if not velocities:
        avg_velocity = 0.0
    else:
        avg_velocity = sum(velocities) / len(velocities)

    # Determine direction
    if avg_velocity > 1.0:
        direction = "improving"
    elif avg_velocity < -1.0:
        direction = "declining"
    elif abs(avg_velocity) < 0.5:
        direction = "stable"
    else:
        direction = "fluctuating"

    # Calculate confidence based on consistency
    if velocities:
        # Standard deviation of velocities
        mean_vel = sum(velocities) / len(velocities)
        variance = sum((v - mean_vel) ** 2 for v in velocities) / len(velocities)
        std_dev = variance ** 0.5

        # Lower std_dev = higher confidence
        confidence = max(0, min(1, 1 - (std_dev / 10)))
    else:
        confidence = 0.0

    # Predict average proficiency next week
    current_avg = sum(s.current_proficiency for s in skills) / len(skills)
    prediction_next_week = current_avg + (avg_velocity * 7)
    prediction_next_week = max(0, min(100, prediction_next_week))

    return {
        "direction": direction,
        "velocity": round(avg_velocity, 2),
        "confidence": round(confidence, 2),
        "prediction_next_week": round(prediction_next_week, 2),
        "current_average": round(current_avg, 2)
    }


async def _analyze_engagement_trend(
    user_id: str,
    course_id: str,
    cutoff_date: datetime
) -> Dict[str, Any]:
    """
    Analyze engagement trend (sessions, quiz attempts)
    """
    # Get learning sessions
    sessions = await LearningSession.find(
        LearningSession.user_id == user_id,
        LearningSession.course_id == course_id,
        LearningSession.started_at >= cutoff_date
    ).to_list()

    # Get quiz attempts
    quiz_attempts = await QuizAttempt.find(
        QuizAttempt.user_id == user_id,
        QuizAttempt.course_id == course_id,
        QuizAttempt.started_at >= cutoff_date
    ).to_list()

    # Calculate weekly averages
    days_in_window = (datetime.utcnow() - cutoff_date).days
    weeks = max(1, days_in_window / 7)

    avg_sessions_per_week = len(sessions) / weeks
    avg_quiz_attempts_per_week = len(quiz_attempts) / weeks

    # Determine trend direction
    # Compare first half vs second half
    mid_date = cutoff_date + timedelta(days=days_in_window / 2)

    first_half_sessions = len([s for s in sessions if s.started_at < mid_date])
    second_half_sessions = len([s for s in sessions if s.started_at >= mid_date])

    if second_half_sessions > first_half_sessions * 1.2:
        direction = "increasing"
    elif second_half_sessions < first_half_sessions * 0.8:
        direction = "decreasing"
    else:
        direction = "stable"

    # Get last activity
    last_activity = None
    if sessions:
        last_activity = max(s.started_at for s in sessions)
    if quiz_attempts:
        last_quiz = max(q.started_at for q in quiz_attempts)
        if last_activity is None or last_quiz > last_activity:
            last_activity = last_quiz

    # Calculate days since last activity
    days_since_last_activity = 0
    if last_activity:
        days_since_last_activity = (datetime.utcnow() - last_activity).days

    return {
        "direction": direction,
        "avg_sessions_per_week": round(avg_sessions_per_week, 2),
        "avg_quiz_attempts_per_week": round(avg_quiz_attempts_per_week, 2),
        "total_sessions": len(sessions),
        "total_quiz_attempts": len(quiz_attempts),
        "last_activity": last_activity,
        "days_since_last_activity": days_since_last_activity
    }


def _generate_intervention_alerts(
    overall_trend: Dict[str, Any],
    declining_skills: List[Dict[str, Any]],
    engagement_trend: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate intervention alerts based on trends
    """
    alerts = []

    # 1. Overall declining trend alert
    if overall_trend["direction"] == "declining":
        severity = "high" if overall_trend["velocity"] < -2.0 else "medium"
        alerts.append({
            "type": "overall_decline",
            "severity": severity,
            "title": "Xu hướng giảm tổng thể",
            "message": f"Proficiency trung bình đang giảm {abs(overall_trend['velocity']):.1f}%/ngày",
            "recommended_actions": [
                "Review lại các bài học gần đây",
                "Tăng thời gian ôn tập",
                "Tham gia study group",
                "Liên hệ instructor để được hỗ trợ"
            ],
            "escalate_to_instructor": severity == "high"
        })

    # 2. Multiple declining skills alert
    if len(declining_skills) >= 3:
        high_risk_skills = [s for s in declining_skills if s["risk_level"] == "high"]

        alerts.append({
            "type": "multiple_declining_skills",
            "severity": "high" if high_risk_skills else "medium",
            "title": f"{len(declining_skills)} skills đang giảm",
            "message": f"Phát hiện {len(declining_skills)} skills có xu hướng giảm",
            "affected_skills": [s["skill_tag"] for s in declining_skills[:5]],
            "recommended_actions": [
                "Tập trung vào skills ưu tiên cao nhất",
                "Làm thêm quiz để củng cố",
                "Review mistakes từ các quiz trước"
            ],
            "escalate_to_instructor": len(high_risk_skills) >= 2
        })

    # 3. Engagement decline alert
    if engagement_trend["direction"] == "decreasing":
        days_inactive = engagement_trend["days_since_last_activity"]

        if days_inactive >= 7:
            severity = "high"
            message = f"Không có hoạt động trong {days_inactive} ngày"
        elif days_inactive >= 3:
            severity = "medium"
            message = f"Hoạt động giảm, {days_inactive} ngày không học"
        else:
            severity = "low"
            message = "Hoạt động học tập đang giảm"

        alerts.append({
            "type": "engagement_decline",
            "severity": severity,
            "title": "Giảm tương tác",
            "message": message,
            "recommended_actions": [
                "Đặt lịch học cố định",
                "Bật notifications để nhắc nhở",
                "Tham gia challenges để tăng động lực"
            ],
            "escalate_to_instructor": days_inactive >= 7
        })

    # 4. High-risk skills alert
    high_risk_skills = [s for s in declining_skills if s["risk_level"] == "high"]
    if high_risk_skills:
        alerts.append({
            "type": "high_risk_skills",
            "severity": "urgent",
            "title": "Skills nguy cơ cao",
            "message": f"{len(high_risk_skills)} skills cần can thiệp ngay",
            "affected_skills": [
                {
                    "skill_tag": s["skill_tag"],
                    "current_proficiency": s["current_proficiency"],
                    "predicted_7d": s["predicted_proficiency_7d"],
                    "velocity": s["velocity"]
                }
                for s in high_risk_skills
            ],
            "recommended_actions": [
                "Dừng học nội dung mới, tập trung ôn tập",
                "Làm lại các quiz đã fail",
                "Đặt lịch 1-on-1 với instructor",
                "Tìm mentor hoặc study buddy"
            ],
            "escalate_to_instructor": True
        })

    return alerts


# ============================================================================
# BATCH TREND ANALYSIS (for instructors/admins)
# ============================================================================

async def analyze_course_trends(course_id: str) -> Dict[str, Any]:
    """
    Phân tích xu hướng của tất cả students trong course
    Dùng cho instructor/admin dashboard

    Returns:
        {
            "course_id": str,
            "total_students": int,
            "students_at_risk": [
                {
                    "user_id": str,
                    "risk_level": "high|medium|low",
                    "declining_skills_count": int,
                    "overall_velocity": float,
                    "days_inactive": int
                }
            ],
            "course_wide_trends": {
                "avg_velocity": float,
                "improving_students": int,
                "declining_students": int,
                "stable_students": int
            },
            "intervention_summary": {
                "urgent_interventions": int,
                "high_priority": int,
                "medium_priority": int
            }
        }
    """
    # Get all students in course
    all_skills = await SkillProficiencyTracking.find(
        SkillProficiencyTracking.course_id == course_id
    ).to_list()

    if not all_skills:
        return {
            "course_id": course_id,
            "total_students": 0,
            "message": "Chưa có dữ liệu tracking"
        }

    # Group by user
    students_skills = defaultdict(list)
    for skill in all_skills:
        students_skills[skill.user_id].append(skill)

    # Analyze each student
    students_at_risk = []
    improving_count = 0
    declining_count = 0
    stable_count = 0

    urgent_interventions = 0
    high_priority = 0
    medium_priority = 0

    for user_id, skills in students_skills.items():
        # Calculate student's overall trend
        overall_trend = _calculate_overall_trend(skills)

        # Count declining skills
        declining_skills = []
        for skill in skills:
            trend_data = _analyze_skill_trend(skill)
            if trend_data["trend"] == "declining":
                declining_skills.append(trend_data)

        # Categorize student
        if overall_trend["direction"] == "improving":
            improving_count += 1
        elif overall_trend["direction"] == "declining":
            declining_count += 1
        else:
            stable_count += 1

        # Check if at risk
        high_risk_skills = [s for s in declining_skills if s["risk_level"] == "high"]

        if high_risk_skills or len(declining_skills) >= 3:
            risk_level = "high" if high_risk_skills else "medium"

            students_at_risk.append({
                "user_id": user_id,
                "risk_level": risk_level,
                "declining_skills_count": len(declining_skills),
                "high_risk_skills_count": len(high_risk_skills),
                "overall_velocity": overall_trend["velocity"],
                "current_average": overall_trend["current_average"]
            })

            if risk_level == "high":
                urgent_interventions += 1
            else:
                high_priority += 1

    # Sort students at risk by severity
    students_at_risk.sort(
        key=lambda s: (
            0 if s["risk_level"] == "high" else 1,
            s["declining_skills_count"]
        ),
        reverse=True
    )

    return {
        "course_id": course_id,
        "total_students": len(students_skills),
        "students_at_risk": students_at_risk,
        "course_wide_trends": {
            "improving_students": improving_count,
            "declining_students": declining_count,
            "stable_students": stable_count,
            "percentages": {
                "improving": round(improving_count / len(students_skills) * 100, 1),
                "declining": round(declining_count / len(students_skills) * 100, 1),
                "stable": round(stable_count / len(students_skills) * 100, 1)
            }
        },
        "intervention_summary": {
            "urgent_interventions": urgent_interventions,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "total_at_risk": len(students_at_risk)
        },
        "analyzed_at": datetime.utcnow()
    }



