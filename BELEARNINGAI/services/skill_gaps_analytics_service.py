"""
Skill Gaps Analytics Service
Xử lý analytics và visualization data cho skill gaps dashboard
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict
from models.models import SkillProficiencyTracking, Course


# ============================================================================
# DASHBOARD ANALYTICS
# ============================================================================

async def get_skill_gaps_dashboard(
    user_id: str,
    course_id: str
) -> Dict[str, Any]:
    """
    Tạo dashboard data cho skill gaps visualization
    
    Returns:
        {
            "overview": {
                "total_skills": int,
                "weak_skills_count": int,
                "strong_skills_count": int,
                "average_proficiency": float,
                "improvement_rate": float
            },
            "skill_distribution": {
                "labels": ["Strong", "Average", "Weak"],
                "values": [5, 3, 2],
                "percentages": [50, 30, 20]
            },
            "weakness_heatmap": [
                {
                    "skill_tag": "python-loops",
                    "proficiency": 45.0,
                    "priority": "urgent",
                    "attempts": 5,
                    "trend": "declining"
                }
            ],
            "improvement_trend": {
                "dates": ["2024-01-01", "2024-01-08", ...],
                "average_proficiency": [60, 62, 65, ...],
                "weak_skills_count": [5, 4, 3, ...]
            },
            "top_weaknesses": [...],
            "recent_improvements": [...]
        }
    """
    # 1. Get all skills
    skills = await SkillProficiencyTracking.find(
        SkillProficiencyTracking.user_id == user_id,
        SkillProficiencyTracking.course_id == course_id
    ).to_list()
    
    if not skills:
        return _empty_dashboard_response(user_id, course_id)
    
    # 2. Calculate overview
    overview = _calculate_overview(skills)
    
    # 3. Skill distribution (pie chart data)
    skill_distribution = _calculate_skill_distribution(skills)
    
    # 4. Weakness heatmap (top 10 weakest skills)
    weakness_heatmap = _generate_weakness_heatmap(skills)
    
    # 5. Improvement trend (line chart data - last 30 days)
    improvement_trend = await _calculate_improvement_trend(user_id, course_id, skills)
    
    # 6. Top weaknesses (detailed list)
    top_weaknesses = _get_top_weaknesses(skills, limit=5)
    
    # 7. Recent improvements (skills that improved recently)
    recent_improvements = _get_recent_improvements(skills, limit=5)
    
    return {
        "user_id": user_id,
        "course_id": course_id,
        "overview": overview,
        "skill_distribution": skill_distribution,
        "weakness_heatmap": weakness_heatmap,
        "improvement_trend": improvement_trend,
        "top_weaknesses": top_weaknesses,
        "recent_improvements": recent_improvements,
        "generated_at": datetime.utcnow()
    }


def _empty_dashboard_response(user_id: str, course_id: str) -> Dict[str, Any]:
    """Return empty dashboard when no data"""
    return {
        "user_id": user_id,
        "course_id": course_id,
        "overview": {
            "total_skills": 0,
            "weak_skills_count": 0,
            "strong_skills_count": 0,
            "average_proficiency": 0.0,
            "improvement_rate": 0.0
        },
        "skill_distribution": {
            "labels": ["Strong", "Average", "Weak"],
            "values": [0, 0, 0],
            "percentages": [0, 0, 0]
        },
        "weakness_heatmap": [],
        "improvement_trend": {
            "dates": [],
            "average_proficiency": [],
            "weak_skills_count": []
        },
        "top_weaknesses": [],
        "recent_improvements": [],
        "message": "Chưa có dữ liệu tracking",
        "generated_at": datetime.utcnow()
    }


def _calculate_overview(skills: List[SkillProficiencyTracking]) -> Dict[str, Any]:
    """Calculate overview statistics"""
    total_skills = len(skills)
    weak_skills = [s for s in skills if s.current_proficiency < 60]
    strong_skills = [s for s in skills if s.current_proficiency >= 80]
    
    total_proficiency = sum(s.current_proficiency for s in skills)
    average_proficiency = total_proficiency / total_skills if total_skills > 0 else 0.0
    
    # Calculate improvement rate (average trend_rate)
    improving_skills = [s for s in skills if s.trend == "improving"]
    improvement_rate = (
        sum(s.trend_rate for s in improving_skills) / len(improving_skills)
        if improving_skills else 0.0
    )
    
    return {
        "total_skills": total_skills,
        "weak_skills_count": len(weak_skills),
        "strong_skills_count": len(strong_skills),
        "average_proficiency": round(average_proficiency, 2),
        "improvement_rate": round(improvement_rate, 2)
    }


def _calculate_skill_distribution(skills: List[SkillProficiencyTracking]) -> Dict[str, Any]:
    """Calculate skill distribution for pie chart"""
    strong = len([s for s in skills if s.current_proficiency >= 80])
    average = len([s for s in skills if 60 <= s.current_proficiency < 80])
    weak = len([s for s in skills if s.current_proficiency < 60])

    total = len(skills)

    return {
        "labels": ["Strong (≥80%)", "Average (60-79%)", "Weak (<60%)"],
        "values": [strong, average, weak],
        "percentages": [
            round(strong / total * 100, 1) if total > 0 else 0,
            round(average / total * 100, 1) if total > 0 else 0,
            round(weak / total * 100, 1) if total > 0 else 0
        ],
        "colors": ["#10b981", "#f59e0b", "#ef4444"]  # green, yellow, red
    }


def _generate_weakness_heatmap(skills: List[SkillProficiencyTracking]) -> List[Dict[str, Any]]:
    """Generate heatmap data for weakest skills"""
    # Sort by proficiency (ascending) and priority
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}

    sorted_skills = sorted(
        skills,
        key=lambda s: (priority_order.get(s.priority_level, 4), s.current_proficiency)
    )

    # Take top 10 weakest
    heatmap = []
    for skill in sorted_skills[:10]:
        heatmap.append({
            "skill_tag": skill.skill_tag,
            "proficiency": round(skill.current_proficiency, 2),
            "priority": skill.priority_level,
            "attempts": skill.total_attempts,
            "trend": skill.trend,
            "consecutive_fails": skill.consecutive_fails,
            "last_attempt": skill.last_attempt_at
        })

    return heatmap


async def _calculate_improvement_trend(
    user_id: str,
    course_id: str,
    skills: List[SkillProficiencyTracking]
) -> Dict[str, Any]:
    """
    Calculate improvement trend over last 30 days
    Group by week to show trend
    """
    # Get date range (last 30 days, grouped by week)
    today = datetime.utcnow()
    dates = []
    average_proficiencies = []
    weak_counts = []

    # Generate 4 weeks of data
    for week in range(4, 0, -1):
        week_start = today - timedelta(days=week * 7)
        dates.append(week_start.strftime("%Y-%m-%d"))

        # Calculate average proficiency at that time
        # (simplified: use current data, in production would need historical snapshots)
        avg_prof = sum(s.current_proficiency for s in skills) / len(skills) if skills else 0
        average_proficiencies.append(round(avg_prof, 2))

        # Count weak skills
        weak_count = len([s for s in skills if s.current_proficiency < 60])
        weak_counts.append(weak_count)

    return {
        "dates": dates,
        "average_proficiency": average_proficiencies,
        "weak_skills_count": weak_counts,
        "chart_type": "line"
    }


def _get_top_weaknesses(
    skills: List[SkillProficiencyTracking],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Get top N weakest skills with details"""
    # Filter weak skills and sort by priority + proficiency
    weak_skills = [s for s in skills if s.current_proficiency < 60]

    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    sorted_weak = sorted(
        weak_skills,
        key=lambda s: (priority_order.get(s.priority_level, 4), s.current_proficiency)
    )

    result = []
    for skill in sorted_weak[:limit]:
        result.append({
            "skill_tag": skill.skill_tag,
            "proficiency": round(skill.current_proficiency, 2),
            "priority": skill.priority_level,
            "trend": skill.trend,
            "trend_rate": skill.trend_rate,
            "total_attempts": skill.total_attempts,
            "consecutive_fails": skill.consecutive_fails,
            "is_chronic": skill.is_chronic_weakness,
            "last_attempt": skill.last_attempt_at,
            "improvement_needed": round(60 - skill.current_proficiency, 2)
        })

    return result


def _get_recent_improvements(
    skills: List[SkillProficiencyTracking],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Get skills that improved recently"""
    # Filter improving skills
    improving = [s for s in skills if s.trend == "improving"]

    # Sort by trend_rate (descending)
    sorted_improving = sorted(
        improving,
        key=lambda s: s.trend_rate,
        reverse=True
    )

    result = []
    for skill in sorted_improving[:limit]:
        result.append({
            "skill_tag": skill.skill_tag,
            "proficiency": round(skill.current_proficiency, 2),
            "trend_rate": skill.trend_rate,
            "total_attempts": skill.total_attempts,
            "last_attempt": skill.last_attempt_at
        })

    return result


# ============================================================================
# COURSE-LEVEL ANALYTICS (for instructors/admins)
# ============================================================================

async def get_course_skill_gaps_analytics(course_id: str) -> Dict[str, Any]:
    """
    Analytics cho tất cả students trong course
    Dùng cho instructor/admin dashboard

    Returns:
        {
            "course_id": str,
            "total_students": int,
            "skills_overview": {
                "total_unique_skills": int,
                "most_common_weaknesses": [...]
            },
            "student_distribution": {
                "struggling_students": int,  # >50% weak skills
                "average_students": int,
                "excelling_students": int  # >70% strong skills
            },
            "skill_difficulty_ranking": [
                {
                    "skill_tag": "python-loops",
                    "average_proficiency": 45.0,
                    "students_struggling": 15,
                    "difficulty_score": 8.5
                }
            ]
        }
    """
    # Get all skill tracking for this course
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

    total_students = len(students_skills)

    # Calculate student distribution
    struggling = 0
    average_students = 0
    excelling = 0

    for user_skills in students_skills.values():
        weak_count = len([s for s in user_skills if s.current_proficiency < 60])
        strong_count = len([s for s in user_skills if s.current_proficiency >= 80])
        total_count = len(user_skills)

        weak_percentage = weak_count / total_count * 100 if total_count > 0 else 0
        strong_percentage = strong_count / total_count * 100 if total_count > 0 else 0

        if weak_percentage > 50:
            struggling += 1
        elif strong_percentage > 70:
            excelling += 1
        else:
            average_students += 1

    # Calculate skill difficulty ranking
    skill_stats = defaultdict(lambda: {"proficiencies": [], "struggling_count": 0})

    for skill in all_skills:
        skill_stats[skill.skill_tag]["proficiencies"].append(skill.current_proficiency)
        if skill.current_proficiency < 60:
            skill_stats[skill.skill_tag]["struggling_count"] += 1

    skill_difficulty_ranking = []
    for skill_tag, stats in skill_stats.items():
        avg_prof = sum(stats["proficiencies"]) / len(stats["proficiencies"])
        difficulty_score = (100 - avg_prof) / 10  # 0-10 scale

        skill_difficulty_ranking.append({
            "skill_tag": skill_tag,
            "average_proficiency": round(avg_prof, 2),
            "students_struggling": stats["struggling_count"],
            "total_students_attempted": len(stats["proficiencies"]),
            "difficulty_score": round(difficulty_score, 2)
        })

    # Sort by difficulty (hardest first)
    skill_difficulty_ranking.sort(key=lambda x: x["difficulty_score"], reverse=True)

    # Get most common weaknesses (top 10)
    most_common_weaknesses = [
        {
            "skill_tag": s["skill_tag"],
            "students_affected": s["students_struggling"],
            "average_proficiency": s["average_proficiency"]
        }
        for s in skill_difficulty_ranking[:10]
        if s["students_struggling"] > 0
    ]

    return {
        "course_id": course_id,
        "total_students": total_students,
        "skills_overview": {
            "total_unique_skills": len(skill_stats),
            "most_common_weaknesses": most_common_weaknesses
        },
        "student_distribution": {
            "struggling_students": struggling,
            "average_students": average_students,
            "excelling_students": excelling,
            "percentages": {
                "struggling": round(struggling / total_students * 100, 1) if total_students > 0 else 0,
                "average": round(average_students / total_students * 100, 1) if total_students > 0 else 0,
                "excelling": round(excelling / total_students * 100, 1) if total_students > 0 else 0
            }
        },
        "skill_difficulty_ranking": skill_difficulty_ranking[:20],  # Top 20 hardest skills
        "generated_at": datetime.utcnow()
    }


# ============================================================================
# COMPARISON ANALYTICS
# ============================================================================

async def compare_student_with_class_average(
    user_id: str,
    course_id: str
) -> Dict[str, Any]:
    """
    So sánh proficiency của student với class average

    Returns:
        {
            "user_id": str,
            "course_id": str,
            "comparison": [
                {
                    "skill_tag": "python-loops",
                    "user_proficiency": 45.0,
                    "class_average": 65.0,
                    "difference": -20.0,
                    "percentile": 25  # User ở top 25% (lower is worse)
                }
            ],
            "overall_comparison": {
                "user_average": 55.0,
                "class_average": 68.0,
                "difference": -13.0,
                "rank": 15,
                "total_students": 30
            }
        }
    """
    # Get user's skills
    user_skills = await SkillProficiencyTracking.find(
        SkillProficiencyTracking.user_id == user_id,
        SkillProficiencyTracking.course_id == course_id
    ).to_list()

    # Get all skills in course
    all_skills = await SkillProficiencyTracking.find(
        SkillProficiencyTracking.course_id == course_id
    ).to_list()

    if not user_skills or not all_skills:
        return {
            "user_id": user_id,
            "course_id": course_id,
            "message": "Chưa đủ dữ liệu để so sánh"
        }

    # Calculate class averages by skill
    skill_class_averages = defaultdict(list)
    for skill in all_skills:
        skill_class_averages[skill.skill_tag].append(skill.current_proficiency)

    # Build comparison
    comparison = []
    for user_skill in user_skills:
        class_proficiencies = skill_class_averages.get(user_skill.skill_tag, [])
        if not class_proficiencies:
            continue

        class_avg = sum(class_proficiencies) / len(class_proficiencies)
        difference = user_skill.current_proficiency - class_avg

        # Calculate percentile
        better_than = len([p for p in class_proficiencies if user_skill.current_proficiency > p])
        percentile = round(better_than / len(class_proficiencies) * 100)

        comparison.append({
            "skill_tag": user_skill.skill_tag,
            "user_proficiency": round(user_skill.current_proficiency, 2),
            "class_average": round(class_avg, 2),
            "difference": round(difference, 2),
            "percentile": percentile,
            "status": "above_average" if difference > 0 else "below_average"
        })

    # Overall comparison
    user_avg = sum(s.current_proficiency for s in user_skills) / len(user_skills)

    # Calculate user's rank
    student_averages = defaultdict(list)
    for skill in all_skills:
        student_averages[skill.user_id].append(skill.current_proficiency)

    student_avg_scores = {
        uid: sum(profs) / len(profs)
        for uid, profs in student_averages.items()
    }

    sorted_students = sorted(student_avg_scores.items(), key=lambda x: x[1], reverse=True)
    rank = next((i + 1 for i, (uid, _) in enumerate(sorted_students) if uid == user_id), 0)

    class_avg = sum(student_avg_scores.values()) / len(student_avg_scores)

    return {
        "user_id": user_id,
        "course_id": course_id,
        "comparison": comparison,
        "overall_comparison": {
            "user_average": round(user_avg, 2),
            "class_average": round(class_avg, 2),
            "difference": round(user_avg - class_avg, 2),
            "rank": rank,
            "total_students": len(student_averages)
        },
        "generated_at": datetime.utcnow()
    }



