"""
Intervention Service
Hệ thống can thiệp tự động khi phát hiện xu hướng xấu
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from models.models import User, Course
from services.trend_analysis_service import analyze_student_trends


# ============================================================================
# INTERVENTION TRIGGERS
# ============================================================================

async def check_and_trigger_interventions(
    user_id: str,
    course_id: str
) -> Dict[str, Any]:
    """
    Kiểm tra và trigger interventions nếu cần
    
    Returns:
        {
            "interventions_triggered": bool,
            "alerts": [...],
            "notifications_sent": [...],
            "escalations": [...]
        }
    """
    # Analyze trends
    trend_analysis = await analyze_student_trends(user_id, course_id)
    
    if not trend_analysis.get("intervention_needed", False):
        return {
            "interventions_triggered": False,
            "message": "No intervention needed"
        }
    
    alerts = trend_analysis.get("intervention_alerts", [])
    
    # Process each alert
    notifications_sent = []
    escalations = []
    
    for alert in alerts:
        # 1. Send notification to student
        notification = await _send_student_notification(user_id, alert)
        notifications_sent.append(notification)
        
        # 2. Escalate to instructor if needed
        if alert.get("escalate_to_instructor", False):
            escalation = await _escalate_to_instructor(user_id, course_id, alert)
            escalations.append(escalation)
    
    return {
        "interventions_triggered": True,
        "alerts": alerts,
        "notifications_sent": notifications_sent,
        "escalations": escalations,
        "triggered_at": datetime.utcnow()
    }


async def _send_student_notification(
    user_id: str,
    alert: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send notification to student
    
    In production, this would:
    - Create in-app notification
    - Send email
    - Send push notification
    """
    # TODO: Implement actual notification sending
    # For now, just return notification data
    
    return {
        "user_id": user_id,
        "type": "intervention_alert",
        "severity": alert.get("severity", "medium"),
        "title": alert.get("title", ""),
        "message": alert.get("message", ""),
        "recommended_actions": alert.get("recommended_actions", []),
        "sent_at": datetime.utcnow(),
        "status": "pending"  # In production: "sent"|"failed"
    }


async def _escalate_to_instructor(
    user_id: str,
    course_id: str,
    alert: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Escalate alert to instructor
    
    In production, this would:
    - Notify instructor via email/dashboard
    - Create task for instructor to follow up
    - Log escalation for tracking
    """
    # Get course to find instructor
    course = await Course.get(course_id)
    
    if not course:
        return {
            "status": "failed",
            "reason": "Course not found"
        }
    
    # Get user info
    user = await User.get(user_id)
    
    # TODO: Implement actual escalation
    # For now, just return escalation data
    
    return {
        "user_id": user_id,
        "user_name": user.full_name if user else "Unknown",
        "course_id": course_id,
        "course_title": course.title,
        "instructor_id": course.owner_id,
        "alert_type": alert.get("type", ""),
        "severity": alert.get("severity", ""),
        "message": alert.get("message", ""),
        "affected_skills": alert.get("affected_skills", []),
        "escalated_at": datetime.utcnow(),
        "status": "pending"  # In production: "notified"|"acknowledged"|"resolved"
    }


# ============================================================================
# INTERVENTION RECOMMENDATIONS
# ============================================================================

def generate_intervention_plan(
    trend_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate detailed intervention plan based on trend analysis
    
    Returns:
        {
            "priority": "urgent|high|medium|low",
            "timeline": "immediate|this_week|this_month",
            "action_plan": [
                {
                    "step": int,
                    "action": str,
                    "description": str,
                    "estimated_time": str,
                    "resources": [...]
                }
            ],
            "success_metrics": [...]
        }
    """
    alerts = trend_analysis.get("intervention_alerts", [])
    
    if not alerts:
        return {
            "priority": "none",
            "message": "No intervention needed"
        }
    
    # Determine overall priority
    severities = [a.get("severity", "low") for a in alerts]
    if "urgent" in severities:
        priority = "urgent"
        timeline = "immediate"
    elif "high" in severities:
        priority = "high"
        timeline = "this_week"
    else:
        priority = "medium"
        timeline = "this_month"
    
    # Build action plan
    action_plan = _build_action_plan(alerts, priority)
    
    # Define success metrics
    success_metrics = _define_success_metrics(trend_analysis)
    
    return {
        "priority": priority,
        "timeline": timeline,
        "action_plan": action_plan,
        "success_metrics": success_metrics,
        "generated_at": datetime.utcnow()
    }


def _build_action_plan(
    alerts: List[Dict[str, Any]],
    priority: str
) -> List[Dict[str, Any]]:
    """Build step-by-step action plan"""
    action_plan = []
    step = 1

    # Step 1: Immediate assessment
    action_plan.append({
        "step": step,
        "action": "Đánh giá tình hình hiện tại",
        "description": "Review lại các quiz và bài học gần đây để xác định vấn đề cụ thể",
        "estimated_time": "30 phút",
        "resources": [
            "Quiz history",
            "Lesson completion records",
            "Skill proficiency dashboard"
        ]
    })
    step += 1

    # Step 2: Address high-risk skills
    high_risk_alerts = [a for a in alerts if a.get("type") == "high_risk_skills"]
    if high_risk_alerts:
        affected_skills = []
        for alert in high_risk_alerts:
            affected_skills.extend(alert.get("affected_skills", []))

        action_plan.append({
            "step": step,
            "action": "Ôn tập skills ưu tiên cao",
            "description": f"Tập trung vào: {', '.join([s.get('skill_tag', '') for s in affected_skills[:3]])}",
            "estimated_time": "2-3 giờ/ngày trong 1 tuần",
            "resources": [
                "Review lesson materials",
                "Practice exercises",
                "Quiz retakes"
            ]
        })
        step += 1

    # Step 3: Increase engagement if needed
    engagement_alerts = [a for a in alerts if a.get("type") == "engagement_decline"]
    if engagement_alerts:
        action_plan.append({
            "step": step,
            "action": "Tăng cường tương tác",
            "description": "Đặt lịch học cố định và tham gia study group",
            "estimated_time": "1 giờ/ngày",
            "resources": [
                "Study schedule template",
                "Study group finder",
                "Learning reminders"
            ]
        })
        step += 1

    # Step 4: Seek help if urgent
    if priority == "urgent":
        action_plan.append({
            "step": step,
            "action": "Tìm kiếm hỗ trợ",
            "description": "Đặt lịch 1-on-1 với instructor hoặc tìm mentor",
            "estimated_time": "1 giờ",
            "resources": [
                "Instructor office hours",
                "Mentor matching system",
                "Q&A forum"
            ]
        })
        step += 1

    # Step 5: Monitor progress
    action_plan.append({
        "step": step,
        "action": "Theo dõi tiến độ",
        "description": "Làm quiz định kỳ để đánh giá cải thiện",
        "estimated_time": "30 phút/tuần",
        "resources": [
            "Progress dashboard",
            "Weekly quiz",
            "Skill tracking"
        ]
    })

    return action_plan


def _define_success_metrics(trend_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Define success metrics for intervention"""
    overall_trend = trend_analysis.get("overall_trend", {})
    current_avg = overall_trend.get("current_average", 0)

    metrics = []

    # Metric 1: Improve overall proficiency
    target_proficiency = min(current_avg + 15, 80)
    metrics.append({
        "metric": "Overall Proficiency",
        "current": round(current_avg, 2),
        "target": round(target_proficiency, 2),
        "timeframe": "2 weeks",
        "measurement": "Average proficiency across all skills"
    })

    # Metric 2: Reduce weak skills count
    weak_count = overall_trend.get("weak_skills_count", 0)
    if isinstance(weak_count, list):
        weak_count = weak_count[-1] if weak_count else 0

    target_weak_count = max(0, weak_count - 2)
    metrics.append({
        "metric": "Weak Skills Count",
        "current": weak_count,
        "target": target_weak_count,
        "timeframe": "2 weeks",
        "measurement": "Number of skills with proficiency < 60%"
    })

    # Metric 3: Positive trend velocity
    metrics.append({
        "metric": "Trend Velocity",
        "current": overall_trend.get("velocity", 0),
        "target": 1.0,
        "timeframe": "1 week",
        "measurement": "% change per day (should be positive)"
    })

    # Metric 4: Engagement
    engagement = trend_analysis.get("engagement_trend", {})
    current_sessions = engagement.get("avg_sessions_per_week", 0)
    target_sessions = max(current_sessions + 2, 5)

    metrics.append({
        "metric": "Weekly Engagement",
        "current": round(current_sessions, 1),
        "target": round(target_sessions, 1),
        "timeframe": "1 week",
        "measurement": "Average sessions per week"
    })

    return metrics


# ============================================================================
# BATCH INTERVENTION CHECKS (for automated jobs)
# ============================================================================

async def run_batch_intervention_check(course_id: str) -> Dict[str, Any]:
    """
    Run intervention check for all students in course
    Used by scheduled jobs to proactively identify at-risk students

    Returns:
        {
            "course_id": str,
            "students_checked": int,
            "interventions_triggered": int,
            "escalations_created": int,
            "summary": [...]
        }
    """
    from services.trend_analysis_service import analyze_course_trends

    # Analyze course trends
    course_trends = await analyze_course_trends(course_id)

    students_at_risk = course_trends.get("students_at_risk", [])

    interventions_triggered = 0
    escalations_created = 0
    summary = []

    # Process each at-risk student
    for student in students_at_risk:
        user_id = student["user_id"]

        # Trigger intervention
        result = await check_and_trigger_interventions(user_id, course_id)

        if result.get("interventions_triggered", False):
            interventions_triggered += 1
            escalations_created += len(result.get("escalations", []))

            summary.append({
                "user_id": user_id,
                "risk_level": student["risk_level"],
                "alerts_count": len(result.get("alerts", [])),
                "escalated": len(result.get("escalations", [])) > 0
            })

    return {
        "course_id": course_id,
        "students_checked": len(students_at_risk),
        "interventions_triggered": interventions_triggered,
        "escalations_created": escalations_created,
        "summary": summary,
        "checked_at": datetime.utcnow()
    }


