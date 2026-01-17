"""
Trend Analysis Schemas
Request/Response schemas cho trend analysis endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


# ============================================================================
# TREND COMPONENTS
# ============================================================================

class OverallTrend(BaseModel):
    """Xu hướng tổng thể"""
    direction: str = Field(..., description="improving|declining|stable|fluctuating")
    velocity: float = Field(..., description="% change per day")
    confidence: float = Field(..., description="Confidence level (0-1)")
    prediction_next_week: float = Field(..., description="Predicted proficiency in 7 days")
    current_average: float = Field(..., description="Current average proficiency")


class SkillTrend(BaseModel):
    """Xu hướng của một skill"""
    skill_tag: str = Field(..., description="Skill tag")
    trend: str = Field(..., description="improving|declining|stable|insufficient_data")
    velocity: float = Field(..., description="% change per day")
    current_proficiency: float = Field(..., description="Current proficiency")
    predicted_proficiency_7d: float = Field(..., description="Predicted proficiency in 7 days")
    risk_level: str = Field(..., description="high|medium|low|none")
    consecutive_fails: int = Field(..., description="Consecutive fails count")
    total_attempts: int = Field(..., description="Total attempts")


class EngagementTrend(BaseModel):
    """Xu hướng tương tác"""
    direction: str = Field(..., description="increasing|decreasing|stable")
    avg_sessions_per_week: float = Field(..., description="Average sessions per week")
    avg_quiz_attempts_per_week: float = Field(..., description="Average quiz attempts per week")
    total_sessions: int = Field(..., description="Total sessions in time window")
    total_quiz_attempts: int = Field(..., description="Total quiz attempts in time window")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    days_since_last_activity: int = Field(..., description="Days since last activity")


class InterventionAlert(BaseModel):
    """Alert can thiệp"""
    type: str = Field(..., description="overall_decline|multiple_declining_skills|engagement_decline|high_risk_skills")
    severity: str = Field(..., description="urgent|high|medium|low")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    affected_skills: Optional[List[str]] = Field(None, description="Affected skills (if applicable)")
    escalate_to_instructor: bool = Field(..., description="Should escalate to instructor")


# ============================================================================
# MAIN TREND ANALYSIS RESPONSE
# ============================================================================

class TrendAnalysisResponse(BaseModel):
    """Response cho GET /api/v1/analytics/trends/{course_id}"""
    user_id: str = Field(..., description="UUID user")
    course_id: str = Field(..., description="UUID course")
    time_window_days: int = Field(..., description="Time window analyzed (days)")
    overall_trend: OverallTrend = Field(..., description="Overall trend")
    skill_trends: List[SkillTrend] = Field(default_factory=list, description="Trends per skill")
    engagement_trend: EngagementTrend = Field(..., description="Engagement trend")
    intervention_needed: bool = Field(..., description="Is intervention needed?")
    intervention_alerts: List[InterventionAlert] = Field(
        default_factory=list,
        description="Intervention alerts"
    )
    analyzed_at: datetime = Field(..., description="Analysis timestamp")


# ============================================================================
# INTERVENTION SCHEMAS
# ============================================================================

class ActionPlanStep(BaseModel):
    """Một bước trong action plan"""
    step: int = Field(..., description="Step number")
    action: str = Field(..., description="Action title")
    description: str = Field(..., description="Action description")
    estimated_time: str = Field(..., description="Estimated time needed")
    resources: List[str] = Field(default_factory=list, description="Required resources")


class SuccessMetric(BaseModel):
    """Success metric"""
    metric: str = Field(..., description="Metric name")
    current: float = Field(..., description="Current value")
    target: float = Field(..., description="Target value")
    timeframe: str = Field(..., description="Timeframe to achieve")
    measurement: str = Field(..., description="How to measure")


class InterventionPlan(BaseModel):
    """Intervention plan"""
    priority: str = Field(..., description="urgent|high|medium|low|none")
    timeline: str = Field(..., description="immediate|this_week|this_month")
    action_plan: List[ActionPlanStep] = Field(default_factory=list, description="Step-by-step plan")
    success_metrics: List[SuccessMetric] = Field(default_factory=list, description="Success metrics")
    message: Optional[str] = Field(None, description="Message if no intervention needed")
    generated_at: datetime = Field(..., description="Generation timestamp")


class InterventionNotification(BaseModel):
    """Notification sent to student"""
    user_id: str = Field(..., description="UUID user")
    type: str = Field(..., description="Notification type")
    severity: str = Field(..., description="urgent|high|medium|low")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    sent_at: datetime = Field(..., description="Sent timestamp")
    status: str = Field(..., description="pending|sent|failed")


class InterventionEscalation(BaseModel):
    """Escalation to instructor"""
    user_id: str = Field(..., description="UUID user")
    user_name: str = Field(..., description="User name")
    course_id: str = Field(..., description="UUID course")
    course_title: str = Field(..., description="Course title")
    instructor_id: str = Field(..., description="UUID instructor")
    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="urgent|high|medium|low")
    message: str = Field(..., description="Escalation message")
    affected_skills: List[str] = Field(default_factory=list, description="Affected skills")
    escalated_at: datetime = Field(..., description="Escalation timestamp")
    status: str = Field(..., description="pending|notified|acknowledged|resolved")


class InterventionTriggerResponse(BaseModel):
    """Response cho intervention trigger"""
    interventions_triggered: bool = Field(..., description="Were interventions triggered?")
    alerts: List[InterventionAlert] = Field(default_factory=list, description="Alerts")
    notifications_sent: List[InterventionNotification] = Field(
        default_factory=list,
        description="Notifications sent"
    )
    escalations: List[InterventionEscalation] = Field(
        default_factory=list,
        description="Escalations created"
    )
    message: Optional[str] = Field(None, description="Message if no intervention")
    triggered_at: Optional[datetime] = Field(None, description="Trigger timestamp")


# ============================================================================
# COURSE-LEVEL TREND SCHEMAS
# ============================================================================

class StudentAtRisk(BaseModel):
    """Student at risk"""
    user_id: str = Field(..., description="UUID user")
    risk_level: str = Field(..., description="high|medium|low")
    declining_skills_count: int = Field(..., description="Number of declining skills")
    high_risk_skills_count: int = Field(..., description="Number of high-risk skills")
    overall_velocity: float = Field(..., description="Overall velocity")
    current_average: float = Field(..., description="Current average proficiency")


class CourseWideTrends(BaseModel):
    """Course-wide trends"""
    improving_students: int = Field(..., description="Number of improving students")
    declining_students: int = Field(..., description="Number of declining students")
    stable_students: int = Field(..., description="Number of stable students")
    percentages: dict = Field(..., description="Percentages of each category")


class InterventionSummary(BaseModel):
    """Intervention summary"""
    urgent_interventions: int = Field(..., description="Urgent interventions needed")
    high_priority: int = Field(..., description="High priority interventions")
    medium_priority: int = Field(..., description="Medium priority interventions")
    total_at_risk: int = Field(..., description="Total students at risk")


class CourseTrendAnalysisResponse(BaseModel):
    """Response cho GET /api/v1/analytics/trends/course/{course_id}"""
    course_id: str = Field(..., description="UUID course")
    total_students: int = Field(..., description="Total students in course")
    students_at_risk: List[StudentAtRisk] = Field(
        default_factory=list,
        description="Students at risk"
    )
    course_wide_trends: CourseWideTrends = Field(..., description="Course-wide trends")
    intervention_summary: InterventionSummary = Field(..., description="Intervention summary")
    message: Optional[str] = Field(None, description="Message if no data")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")


# ============================================================================
# BATCH INTERVENTION SCHEMAS
# ============================================================================

class BatchInterventionSummary(BaseModel):
    """Summary of batch intervention check"""
    user_id: str = Field(..., description="UUID user")
    risk_level: str = Field(..., description="high|medium|low")
    alerts_count: int = Field(..., description="Number of alerts")
    escalated: bool = Field(..., description="Was escalated to instructor?")


class BatchInterventionResponse(BaseModel):
    """Response cho batch intervention check"""
    course_id: str = Field(..., description="UUID course")
    students_checked: int = Field(..., description="Number of students checked")
    interventions_triggered: int = Field(..., description="Number of interventions triggered")
    escalations_created: int = Field(..., description="Number of escalations created")
    summary: List[BatchInterventionSummary] = Field(
        default_factory=list,
        description="Summary per student"
    )
    checked_at: datetime = Field(..., description="Check timestamp")


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class TrendAnalysisRequest(BaseModel):
    """Request parameters for trend analysis"""
    time_window_days: int = Field(
        default=30,
        ge=7,
        le=90,
        description="Time window in days (7-90)"
    )


class InterventionCheckRequest(BaseModel):
    """Request to check and trigger interventions"""
    force_check: bool = Field(
        default=False,
        description="Force check even if recently checked"
    )


