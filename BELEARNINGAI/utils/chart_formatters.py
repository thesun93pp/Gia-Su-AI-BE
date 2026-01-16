"""
Chart Formatters
Utilities để format data cho các charting libraries (Chart.js, Recharts, etc.)
"""

from typing import Dict, Any, List


# ============================================================================
# CHART.JS FORMATTERS
# ============================================================================

def format_pie_chart(distribution: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format cho pie chart (skill distribution)
    
    Chart.js format:
    {
        "labels": ["Strong", "Average", "Weak"],
        "datasets": [{
            "data": [5, 3, 2],
            "backgroundColor": ["#10b981", "#f59e0b", "#ef4444"]
        }]
    }
    """
    return {
        "type": "pie",
        "labels": distribution.get("labels", []),
        "datasets": [{
            "label": "Skill Distribution",
            "data": distribution.get("values", []),
            "backgroundColor": distribution.get("colors", []),
            "borderWidth": 1
        }],
        "options": {
            "responsive": True,
            "plugins": {
                "legend": {
                    "position": "bottom"
                },
                "title": {
                    "display": True,
                    "text": "Phân bố Skills"
                }
            }
        }
    }


def format_line_chart(trend: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format cho line chart (improvement trend)
    
    Chart.js format với 2 lines:
    - Average proficiency over time
    - Weak skills count over time
    """
    return {
        "type": "line",
        "labels": trend.get("dates", []),
        "datasets": [
            {
                "label": "Average Proficiency (%)",
                "data": trend.get("average_proficiency", []),
                "borderColor": "#3b82f6",
                "backgroundColor": "rgba(59, 130, 246, 0.1)",
                "tension": 0.4,
                "yAxisID": "y"
            },
            {
                "label": "Weak Skills Count",
                "data": trend.get("weak_skills_count", []),
                "borderColor": "#ef4444",
                "backgroundColor": "rgba(239, 68, 68, 0.1)",
                "tension": 0.4,
                "yAxisID": "y1"
            }
        ],
        "options": {
            "responsive": True,
            "interaction": {
                "mode": "index",
                "intersect": False
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Xu hướng cải thiện (30 ngày)"
                }
            },
            "scales": {
                "y": {
                    "type": "linear",
                    "display": True,
                    "position": "left",
                    "title": {
                        "display": True,
                        "text": "Proficiency (%)"
                    }
                },
                "y1": {
                    "type": "linear",
                    "display": True,
                    "position": "right",
                    "title": {
                        "display": True,
                        "text": "Weak Skills Count"
                    },
                    "grid": {
                        "drawOnChartArea": False
                    }
                }
            }
        }
    }


def format_bar_chart(weaknesses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format cho bar chart (top weaknesses)
    Horizontal bar chart showing proficiency of weakest skills
    """
    skill_tags = [w.get("skill_tag", "") for w in weaknesses]
    proficiencies = [w.get("proficiency", 0) for w in weaknesses]
    
    # Color based on priority
    colors = []
    for w in weaknesses:
        priority = w.get("priority", "low")
        if priority == "urgent":
            colors.append("#dc2626")  # red-600
        elif priority == "high":
            colors.append("#f59e0b")  # amber-500
        elif priority == "medium":
            colors.append("#eab308")  # yellow-500
        else:
            colors.append("#84cc16")  # lime-500
    
    return {
        "type": "bar",
        "labels": skill_tags,
        "datasets": [{
            "label": "Proficiency (%)",
            "data": proficiencies,
            "backgroundColor": colors,
            "borderWidth": 1
        }],
        "options": {
            "indexAxis": "y",  # Horizontal bar
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Top Weaknesses"
                },
                "legend": {
                    "display": False
                }
            }
        }
    }


def format_heatmap(heatmap_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format cho heatmap (weakness heatmap)

    Returns data structure for heatmap libraries (e.g., react-heatmap-grid)
    Each cell represents a skill with color intensity based on proficiency
    """
    # Group by priority for better visualization
    priority_groups = {
        "urgent": [],
        "high": [],
        "medium": [],
        "low": []
    }

    for item in heatmap_data:
        priority = item.get("priority", "low")
        priority_groups[priority].append(item)

    # Build heatmap matrix
    matrix = []
    labels_y = []

    for priority in ["urgent", "high", "medium", "low"]:
        items = priority_groups[priority]
        if items:
            for item in items:
                labels_y.append(item.get("skill_tag", ""))
                proficiency = item.get("proficiency", 0)

                # Create row with proficiency value
                # Color intensity will be based on proficiency (0-100)
                matrix.append({
                    "skill": item.get("skill_tag", ""),
                    "proficiency": proficiency,
                    "priority": priority,
                    "attempts": item.get("attempts", 0),
                    "trend": item.get("trend", "stable"),
                    "color_intensity": proficiency / 100  # 0-1 scale
                })

    return {
        "type": "heatmap",
        "data": matrix,
        "labels_y": labels_y,
        "labels_x": ["Proficiency"],
        "color_scale": {
            "min": 0,
            "max": 100,
            "colors": ["#dc2626", "#f59e0b", "#eab308", "#10b981"]  # red to green
        }
    }


# ============================================================================
# RECHARTS FORMATTERS (for React apps)
# ============================================================================

def format_for_recharts_pie(distribution: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format for Recharts PieChart

    Returns:
        [
            {"name": "Strong", "value": 5, "fill": "#10b981"},
            {"name": "Average", "value": 3, "fill": "#f59e0b"},
            ...
        ]
    """
    labels = distribution.get("labels", [])
    values = distribution.get("values", [])
    colors = distribution.get("colors", [])

    return [
        {
            "name": labels[i],
            "value": values[i],
            "fill": colors[i]
        }
        for i in range(len(labels))
    ]


def format_for_recharts_line(trend: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format for Recharts LineChart

    Returns:
        [
            {"date": "2024-01-01", "proficiency": 60, "weakCount": 5},
            {"date": "2024-01-08", "proficiency": 62, "weakCount": 4},
            ...
        ]
    """
    dates = trend.get("dates", [])
    proficiencies = trend.get("average_proficiency", [])
    weak_counts = trend.get("weak_skills_count", [])

    return [
        {
            "date": dates[i],
            "proficiency": proficiencies[i],
            "weakCount": weak_counts[i]
        }
        for i in range(len(dates))
    ]


def format_for_recharts_bar(weaknesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format for Recharts BarChart

    Returns:
        [
            {"skill": "python-loops", "proficiency": 45, "fill": "#dc2626"},
            ...
        ]
    """
    result = []
    for w in weaknesses:
        priority = w.get("priority", "low")

        # Determine color based on priority
        if priority == "urgent":
            fill = "#dc2626"
        elif priority == "high":
            fill = "#f59e0b"
        elif priority == "medium":
            fill = "#eab308"
        else:
            fill = "#84cc16"

        result.append({
            "skill": w.get("skill_tag", ""),
            "proficiency": w.get("proficiency", 0),
            "fill": fill,
            "priority": priority
        })

    return result


