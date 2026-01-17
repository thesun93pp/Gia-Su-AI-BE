"""
AI Insights Service
Sử dụng AI để generate insights và recommendations dựa trên skill gaps
"""

from typing import Dict, Any, List
from datetime import datetime


# ============================================================================
# AI INSIGHTS GENERATION
# ============================================================================

async def generate_skill_gaps_insights(
    dashboard_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate AI insights dựa trên skill gaps dashboard data
    
    Args:
        dashboard_data: Output từ get_skill_gaps_dashboard()
        
    Returns:
        {
            "insights": [
                {
                    "type": "warning|info|success",
                    "title": str,
                    "message": str,
                    "action": str
                }
            ],
            "recommendations": [
                {
                    "priority": "high|medium|low",
                    "title": str,
                    "description": str,
                    "action_items": [str]
                }
            ],
            "learning_path_suggestions": [...]
        }
    """
    overview = dashboard_data.get("overview", {})
    top_weaknesses = dashboard_data.get("top_weaknesses", [])
    recent_improvements = dashboard_data.get("recent_improvements", [])
    
    insights = []
    recommendations = []
    
    # 1. Analyze overall performance
    avg_proficiency = overview.get("average_proficiency", 0)
    weak_count = overview.get("weak_skills_count", 0)
    improvement_rate = overview.get("improvement_rate", 0)
    
    if avg_proficiency < 50:
        insights.append({
            "type": "warning",
            "title": "Proficiency thấp",
            "message": f"Proficiency trung bình của bạn là {avg_proficiency:.1f}%, thấp hơn mức khuyến nghị (60%).",
            "action": "Cần tập trung ôn tập các skills yếu"
        })
    elif avg_proficiency >= 80:
        insights.append({
            "type": "success",
            "title": "Xuất sắc!",
            "message": f"Proficiency trung bình của bạn là {avg_proficiency:.1f}%, rất tốt!",
            "action": "Tiếp tục duy trì và thử thách bản thân với nội dung nâng cao"
        })
    
    # 2. Analyze improvement trend
    if improvement_rate > 5:
        insights.append({
            "type": "success",
            "title": "Tiến bộ tốt",
            "message": f"Bạn đang cải thiện với tốc độ {improvement_rate:.1f}%/tuần.",
            "action": "Tiếp tục duy trì nhịp độ học tập hiện tại"
        })
    elif improvement_rate < -5:
        insights.append({
            "type": "warning",
            "title": "Cần chú ý",
            "message": f"Proficiency của bạn đang giảm ({improvement_rate:.1f}%/tuần).",
            "action": "Cần review lại các bài học và làm thêm quiz"
        })
    
    # 3. Analyze chronic weaknesses
    chronic_weaknesses = [w for w in top_weaknesses if w.get("is_chronic", False)]
    if chronic_weaknesses:
        chronic_skills = [w["skill_tag"] for w in chronic_weaknesses[:3]]
        insights.append({
            "type": "warning",
            "title": "Phát hiện điểm yếu mãn tính",
            "message": f"Bạn gặp khó khăn lâu dài với: {', '.join(chronic_skills)}",
            "action": "Nên tìm kiếm sự hỗ trợ từ instructor hoặc học nhóm"
        })
        
        # Add recommendation for chronic weaknesses
        recommendations.append({
            "priority": "high",
            "title": "Khắc phục điểm yếu mãn tính",
            "description": f"Các skills {', '.join(chronic_skills)} cần được ưu tiên cao nhất",
            "action_items": [
                "Review lại các bài học cơ bản",
                "Làm thêm bài tập thực hành",
                "Tham gia study group hoặc tìm mentor",
                "Đặt câu hỏi với instructor"
            ]
        })
    
    # 4. Analyze recent improvements
    if recent_improvements:
        improved_skills = [s["skill_tag"] for s in recent_improvements[:3]]
        insights.append({
            "type": "success",
            "title": "Cải thiện đáng kể",
            "message": f"Bạn đã cải thiện rõ rệt ở: {', '.join(improved_skills)}",
            "action": "Áp dụng phương pháp học tương tự cho các skills khác"
        })
    
    # 5. Generate learning path suggestions
    learning_path = _generate_learning_path(top_weaknesses, recent_improvements)
    
    # 6. Priority-based recommendations
    urgent_weaknesses = [w for w in top_weaknesses if w.get("priority") == "urgent"]
    if urgent_weaknesses:
        recommendations.append({
            "priority": "high",
            "title": "Xử lý các skills ưu tiên cao",
            "description": f"Có {len(urgent_weaknesses)} skills cần xử lý ngay",
            "action_items": [
                f"Ôn tập {w['skill_tag']}: cần cải thiện {w.get('improvement_needed', 0):.1f}%"
                for w in urgent_weaknesses[:3]
            ]
        })
    
    # 7. Study pattern analysis
    if weak_count > 5:
        recommendations.append({
            "priority": "medium",
            "title": "Tối ưu hóa thời gian học",
            "description": f"Bạn có {weak_count} skills yếu, cần phân bổ thời gian hợp lý",
            "action_items": [
                "Tập trung vào 2-3 skills mỗi tuần",
                "Dành 30-45 phút/ngày cho mỗi skill",
                "Làm quiz thường xuyên để đánh giá tiến độ",
                "Review lại sau 3-5 ngày để củng cố"
            ]
        })
    
    return {
        "insights": insights,
        "recommendations": recommendations,
        "learning_path_suggestions": learning_path,
        "generated_at": datetime.utcnow()
    }


def _generate_learning_path(
    weaknesses: List[Dict[str, Any]],
    improvements: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generate suggested learning path based on weaknesses and improvements"""
    path = []
    
    # Prioritize by urgency and proficiency
    sorted_weaknesses = sorted(
        weaknesses,
        key=lambda w: (
            0 if w.get("priority") == "urgent" else
            1 if w.get("priority") == "high" else
            2 if w.get("priority") == "medium" else 3,
            w.get("proficiency", 100)
        )
    )
    
    for i, weakness in enumerate(sorted_weaknesses[:5], 1):
        path.append({
            "step": i,
            "skill_tag": weakness["skill_tag"],
            "current_proficiency": weakness["proficiency"],
            "target_proficiency": 70.0,
            "estimated_time": _estimate_time_needed(weakness),
            "suggested_actions": [
                "Review lesson materials",
                "Complete practice exercises",
                "Take quiz to assess progress",
                "Review mistakes and retry"
            ]
        })
    
    return path


def _estimate_time_needed(weakness: Dict[str, Any]) -> str:
    """Estimate time needed to improve a skill"""
    proficiency = weakness.get("proficiency", 0)
    gap = 70 - proficiency  # Target is 70%
    
    if gap <= 10:
        return "1-2 days"
    elif gap <= 20:
        return "3-5 days"
    elif gap <= 30:
        return "1-2 weeks"
    else:
        return "2-4 weeks"

