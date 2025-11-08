"""
AI Service - Tích hợp Google Gemini API
Sử dụng: google-generativeai library
Tuân thủ: CHUCNANG.md Section 2.2 (Assessment), 2.6 (Chatbot)
"""

import json
from typing import List, Dict, Optional
import google.generativeai as genai
from config.config import get_settings
from models.models import Course, Lesson


# ============================================================================
# GEMINI API CONFIGURATION
# ============================================================================

settings = get_settings()
genai.configure(api_key=settings.google_api_key)
model = genai.GenerativeModel(settings.gemini_model)


# ============================================================================
# ASSESSMENT QUESTION GENERATION (Section 2.2.1-2.2.2)
# ============================================================================

async def generate_assessment_questions(
    category: str,
    subject: str,
    level: str,
    count: int = 10,
    focus_areas: Optional[List[str]] = None
) -> List[Dict]:
    """
    Tạo câu hỏi đánh giá năng lực sử dụng Google Gemini
    Tuân thủ CHUCNANG.md Section 2.2.1-2.2.2
    
    Phân bổ độ khó theo mức độ:
    - Beginner (15 câu): 3 Easy (20%) + 8 Medium (53%) + 4 Hard (27%)
    - Intermediate (25 câu): 5 Easy (20%) + 13 Medium (52%) + 7 Hard (28%)
    - Advanced (35 câu): 7 Easy (20%) + 18 Medium (51%) + 10 Hard (29%)
    
    Args:
        category: Danh mục (Programming, Math, Business, Languages)
        subject: Chủ đề cụ thể (Python, Calculus, Marketing, etc.)
        level: Mức độ (Beginner, Intermediate, Advanced)
        count: Số lượng câu hỏi (mặc định 10, thực tế theo level)
        focus_areas: Các chủ đề con cần tập trung (optional)
        
    Returns:
        List các câu hỏi với cấu trúc đầy đủ theo CHUCNANG.md
    """
    # Xác định số câu và phân bổ độ khó theo mức độ
    if level == "Beginner":
        total_questions = 15
        easy_count = 3
        medium_count = 8
        hard_count = 4
    elif level == "Intermediate":
        total_questions = 25
        easy_count = 5
        medium_count = 13
        hard_count = 7
    elif level == "Advanced":
        total_questions = 35
        easy_count = 7
        medium_count = 18
        hard_count = 10
    else:
        total_questions = count
        easy_count = int(count * 0.2)
        medium_count = int(count * 0.5)
        hard_count = count - easy_count - medium_count
    
    focus_areas_str = f"\n- Tập trung vào: {', '.join(focus_areas)}" if focus_areas else ""
    
    prompt = f"""
Tạo {total_questions} câu hỏi đánh giá năng lực cho:
- Danh mục: {category}
- Chủ đề: {subject}
- Mức độ: {level}{focus_areas_str}

Phân bổ độ khó CHÍNH XÁC:
- {easy_count} câu EASY (20%): Kiến thức nền tảng cơ bản
- {medium_count} câu MEDIUM (50-53%): Áp dụng kiến thức thực tế
- {hard_count} câu HARD (27-30%): Tư duy phản biện và giải quyết vấn đề phức tạp

Yêu cầu format JSON chính xác (sắp xếp từ dễ đến khó):
[
    {{
        "question_id": "q1",
        "question_text": "Câu hỏi rõ ràng, súc tích với ngữ cảnh thực tế...",
        "question_type": "multiple_choice",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option B",
        "explanation": "Giải thích chi tiết: Tại sao B đúng, tại sao A/C/D sai...",
        "difficulty": "easy",
        "skill_tag": "python-syntax",
        "points": 1
    }},
    {{
        "question_id": "q2",
        "question_text": "Câu hỏi...",
        "question_type": "fill_in_blank",
        "options": null,
        "correct_answer": "đáp án chính xác",
        "explanation": "Giải thích...",
        "difficulty": "medium",
        "skill_tag": "algorithm-basics",
        "points": 2
    }}
]

Lưu ý:
- Sắp xếp câu hỏi từ DỄ → KHÓ
- question_type: multiple_choice, fill_in_blank, drag_and_drop
- difficulty: easy, medium, hard
- points: easy=1, medium=2, hard=3
- skill_tag: Gắn nhãn kỹ năng cụ thể (ví dụ: python-syntax, data-structures-array)
- options: null nếu không phải multiple_choice
- PHẢI trả về JSON array hợp lệ, không thêm text khác
"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Loại bỏ markdown code blocks nếu có
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        questions = json.loads(response_text)
        
        return questions
    
    except json.JSONDecodeError as e:
        # Fallback: tạo câu hỏi mẫu nếu parse JSON thất bại
        print(f"JSON parse error: {str(e)}")
        if level == "Beginner":
            return _generate_fallback_questions(category, subject, level, 15)
        elif level == "Intermediate":
            return _generate_fallback_questions(category, subject, level, 25)
        elif level == "Advanced":
            return _generate_fallback_questions(category, subject, level, 35)
        return _generate_fallback_questions(category, subject, level, count)
    
    except Exception as e:
        # Log error và trả về fallback
        print(f"Error generating questions: {str(e)}")
        if level == "Beginner":
            return _generate_fallback_questions(category, subject, level, 15)
        elif level == "Intermediate":
            return _generate_fallback_questions(category, subject, level, 25)
        elif level == "Advanced":
            return _generate_fallback_questions(category, subject, level, 35)
        return _generate_fallback_questions(category, subject, level, count)


def _generate_fallback_questions(
    category: str,
    subject: str,
    level: str,
    count: int
) -> List[Dict]:
    """
    Tạo câu hỏi fallback khi Gemini API thất bại
    Tuân thủ phân bổ độ khó theo CHUCNANG.md
    
    Returns:
        List câu hỏi mẫu với phân bổ đúng easy/medium/hard
    """
    # Phân bổ độ khó
    if count == 15:  # Beginner
        easy_count, medium_count, hard_count = 3, 8, 4
    elif count == 25:  # Intermediate
        easy_count, medium_count, hard_count = 5, 13, 7
    elif count == 35:  # Advanced
        easy_count, medium_count, hard_count = 7, 18, 10
    else:
        easy_count = int(count * 0.2)
        medium_count = int(count * 0.5)
        hard_count = count - easy_count - medium_count
    
    questions = []
    question_num = 1
    
    # Tạo câu dễ
    for i in range(easy_count):
        questions.append({
            "question_id": f"q{question_num}",
            "question_text": f"[Fallback] Câu hỏi cơ bản về {subject} - câu {question_num}",
            "question_type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": f"Đáp án A đúng cho câu hỏi cơ bản này về {subject}",
            "difficulty": "easy",
            "skill_tag": f"{subject.lower()}-basics",
            "points": 1
        })
        question_num += 1
    
    # Tạo câu trung bình
    for i in range(medium_count):
        questions.append({
            "question_id": f"q{question_num}",
            "question_text": f"[Fallback] Câu hỏi áp dụng về {subject} - câu {question_num}",
            "question_type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option B",
            "explanation": f"Đáp án B đúng, đây là câu hỏi áp dụng kiến thức {subject}",
            "difficulty": "medium",
            "skill_tag": f"{subject.lower()}-application",
            "points": 2
        })
        question_num += 1
    
    # Tạo câu khó
    for i in range(hard_count):
        questions.append({
            "question_id": f"q{question_num}",
            "question_text": f"[Fallback] Câu hỏi phức tạp về {subject} - câu {question_num}",
            "question_type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option C",
            "explanation": f"Đáp án C đúng, đây là câu hỏi đòi hỏi tư duy cao về {subject}",
            "difficulty": "hard",
            "skill_tag": f"{subject.lower()}-advanced",
            "points": 3
        })
        question_num += 1
    
    return questions


# ============================================================================
# ASSESSMENT EVALUATION (Section 2.2.3)
# ============================================================================

async def evaluate_assessment_answers(
    questions: List[Dict],
    answers: List[Dict],
    category: str,
    subject: str
) -> Dict:
    """
    Đánh giá kết quả assessment và phân tích năng lực
    Tuân thủ CHUCNANG.md Section 2.2.3
    
    Tính điểm có trọng số: easy=1, medium=2, hard=3
    Phân tích theo 4 khía cạnh:
    1. Điểm tổng thể (0-100)
    2. Phân loại trình độ (Beginner < 60, Intermediate 60-80, Advanced > 80)
    3. Điểm mạnh/yếu theo skill tag
    4. Lỗ hổng kiến thức cần khắc phục
    
    Args:
        questions: List câu hỏi
        answers: List câu trả lời của user
        category: Danh mục
        subject: Chủ đề
        
    Returns:
        Dict chứa kết quả phân tích đầy đủ
    """
    # Tính điểm có trọng số
    total_weighted_score = 0
    max_weighted_score = 0
    correct_count = 0
    total_count = len(questions)
    
    # Phân tích theo độ khó
    easy_correct = easy_total = 0
    medium_correct = medium_total = 0
    hard_correct = hard_total = 0
    
    # Phân tích theo skill tag
    skill_stats = {}
    
    answer_map = {ans.get("question_id"): ans.get("answer_content", ans.get("answer", "")) for ans in answers}
    
    for question in questions:
        q_id = question["question_id"]
        user_answer = answer_map.get(q_id, "").strip()
        correct_answer = question.get("correct_answer", "").strip()
        difficulty = question.get("difficulty", "medium").lower()
        skill_tag = question.get("skill_tag", "general")
        points = question.get("points", 2)
        
        # Cập nhật max score
        max_weighted_score += points
        
        # Kiểm tra đáp án đúng
        is_correct = False
        if user_answer.lower() == correct_answer.lower():
            is_correct = True
            correct_count += 1
            total_weighted_score += points
        
        # Thống kê theo độ khó
        if difficulty == "easy":
            easy_total += 1
            if is_correct:
                easy_correct += 1
        elif difficulty == "hard":
            hard_total += 1
            if is_correct:
                hard_correct += 1
        else:  # medium
            medium_total += 1
            if is_correct:
                medium_correct += 1
        
        # Thống kê theo skill tag
        if skill_tag not in skill_stats:
            skill_stats[skill_tag] = {"total": 0, "correct": 0}
        skill_stats[skill_tag]["total"] += 1
        if is_correct:
            skill_stats[skill_tag]["correct"] += 1
    
    # Tính điểm tổng thể (0-100)
    overall_score = (total_weighted_score / max_weighted_score * 100) if max_weighted_score > 0 else 0
    
    # Xác định proficiency level theo ngưỡng
    if overall_score >= 80:
        proficiency_level = "Advanced"
    elif overall_score >= 60:
        proficiency_level = "Intermediate"
    else:
        proficiency_level = "Beginner"
    
    # Chuẩn bị dữ liệu cho Gemini phân tích
    skill_summary = []
    for skill, stats in skill_stats.items():
        percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        skill_summary.append({
            "skill": skill,
            "correct": stats["correct"],
            "total": stats["total"],
            "percentage": percentage
        })
    
    # Sử dụng Gemini để phân tích chi tiết
    analysis_prompt = f"""
Phân tích kết quả assessment chi tiết:
- Danh mục: {category}
- Chủ đề: {subject}
- Điểm số: {overall_score:.1f}/100 (có trọng số)
- Số câu đúng: {correct_count}/{total_count}
- Phân loại: {proficiency_level}

Phân tích theo độ khó:
- Easy: {easy_correct}/{easy_total} đúng ({easy_correct/easy_total*100 if easy_total > 0 else 0:.1f}%)
- Medium: {medium_correct}/{medium_total} đúng ({medium_correct/medium_total*100 if medium_total > 0 else 0:.1f}%)
- Hard: {hard_correct}/{hard_total} đúng ({hard_correct/hard_total*100 if hard_total > 0 else 0:.1f}%)

Phân tích theo skill tag:
{json.dumps(skill_summary, indent=2, ensure_ascii=False)}

Hãy trả về JSON với format (theo CHUCNANG.md Section 2.2.3):
{{
    "skill_analysis": [
        {{
            "skill_tag": "python-syntax",
            "questions_count": 5,
            "correct_count": 4,
            "proficiency_percentage": 80.0,
            "strength_level": "Strong",
            "detailed_feedback": "Bạn nắm vững cú pháp Python cơ bản..."
        }}
    ],
    "knowledge_gaps": [
        {{
            "gap_area": "Algorithm Complexity",
            "description": "Chưa hiểu rõ về độ phức tạp thuật toán O(n), O(log n)",
            "importance": "High",
            "suggested_action": "Học lại Big O notation và phân tích thuật toán"
        }}
    ],
    "overall_feedback": "Nhận xét tổng quan chi tiết về năng lực..."
}}

Lưu ý:
- strength_level: Strong (>80%), Average (60-80%), Weak (<60%)
- importance: High, Medium, Low
- PHẢI trả về JSON hợp lệ, không thêm text khác
"""
    
    try:
        response = model.generate_content(analysis_prompt)
        response_text = response.text.strip()
        
        # Loại bỏ markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        analysis = json.loads(response_text)
        
        return {
            "overall_score": round(overall_score, 1),
            "proficiency_level": proficiency_level,
            "skill_analysis": analysis.get("skill_analysis", []),
            "knowledge_gaps": analysis.get("knowledge_gaps", []),
            "overall_feedback": analysis.get("overall_feedback", ""),
            "score_breakdown": {
                "easy": {"correct": easy_correct, "total": easy_total},
                "medium": {"correct": medium_correct, "total": medium_total},
                "hard": {"correct": hard_correct, "total": hard_total}
            }
        }
    
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        # Fallback analysis với logic đơn giản
        skill_analysis_list = []
        knowledge_gaps_list = []
        
        for skill, stats in skill_stats.items():
            percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            if percentage >= 80:
                strength_level = "Strong"
            elif percentage >= 60:
                strength_level = "Average"
            else:
                strength_level = "Weak"
                # Nếu yếu, thêm vào knowledge gaps
                knowledge_gaps_list.append({
                    "gap_area": skill,
                    "description": f"Chỉ đạt {percentage:.1f}% ở kỹ năng {skill}",
                    "importance": "High" if percentage < 40 else "Medium",
                    "suggested_action": f"Cần ôn luyện thêm về {skill}"
                })
            
            skill_analysis_list.append({
                "skill_tag": skill,
                "questions_count": stats["total"],
                "correct_count": stats["correct"],
                "proficiency_percentage": round(percentage, 1),
                "strength_level": strength_level,
                "detailed_feedback": f"Bạn đạt {percentage:.1f}% ở kỹ năng {skill}"
            })
        
        return {
            "overall_score": round(overall_score, 1),
            "proficiency_level": proficiency_level,
            "skill_analysis": skill_analysis_list,
            "knowledge_gaps": knowledge_gaps_list,
            "overall_feedback": f"Bạn đạt {overall_score:.1f}% - mức {proficiency_level}. Tổng {correct_count}/{total_count} câu đúng.",
            "score_breakdown": {
                "easy": {"correct": easy_correct, "total": easy_total},
                "medium": {"correct": medium_correct, "total": medium_total},
                "hard": {"correct": hard_correct, "total": hard_total}
            }
        }


# ============================================================================
# CHATBOT với Course Context (Section 2.6)
# ============================================================================

async def chat_with_course_context(
    course_id: str,
    user_message: str,
    conversation_history: Optional[List[Dict]] = None
) -> str:
    """
    Chatbot trả lời câu hỏi dựa trên context của khóa học
    
    Args:
        course_id: ID của khóa học
        user_message: Tin nhắn từ user
        conversation_history: Lịch sử chat trước đó (optional)
        
    Returns:
        Câu trả lời từ AI
    """
    # Lấy thông tin khóa học từ database
    course = await Course.get(course_id)
    
    if not course:
        return "Không tìm thấy thông tin khóa học."
    
    # Tạo context từ khóa học
    course_context = _build_course_context(course)
    
    # Tạo conversation context
    history_text = ""
    if conversation_history:
        for msg in conversation_history[-5:]:  # Lấy 5 tin nhắn gần nhất
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"
    
    # Tạo prompt
    prompt = f"""
Bạn là trợ lý AI hỗ trợ học tập cho khóa học sau:

THÔNG TIN KHÓA HỌC:
{course_context}

LỊCH SỬ HỘI THOẠI:
{history_text}

CÂU HỎI MỚI TỪ HỌC VIÊN:
{user_message}

Hãy trả lời câu hỏi dựa trên thông tin khóa học. Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu.
Nếu câu hỏi không liên quan đến khóa học, hãy lịch sự nhắc nhở học viên tập trung vào nội dung khóa học.
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        return "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau."


def _build_course_context(course: Course) -> str:
    """
    Tạo text context từ Course document
    
    Args:
        course: Course document
        
    Returns:
        String chứa thông tin khóa học
    """
    context = f"""
Tên khóa học: {course.title}
Mô tả: {course.description}
Danh mục: {course.category}
Mức độ: {course.level}

Kết quả học tập:
"""
    
    for outcome in course.learning_outcomes:
        context += f"- {outcome.get('description', '')}\n"
    
    context += "\nNội dung khóa học:\n"
    
    for module in course.modules:
        context += f"\n## Module: {module.title}\n"
        context += f"{module.description}\n"
        
        for lesson in module.lessons:
            context += f"  - Bài {lesson.order}: {lesson.title}\n"
    
    return context


# ============================================================================
# COURSE RECOMMENDATION (Section 2.7.4)
# ============================================================================

async def generate_course_recommendations(
    user_learning_history: List[Dict],
    assessment_results: Optional[Dict] = None,
    available_courses: Optional[List[Course]] = None
) -> Dict:
    """
    Tạo đề xuất khóa học dựa trên lịch sử học tập và kết quả assessment
    
    Args:
        user_learning_history: Lịch sử học tập của user
        assessment_results: Kết quả assessment (optional)
        available_courses: Danh sách khóa học có sẵn (optional)
        
    Returns:
        Dict chứa:
        {
            "recommended_courses": [
                {
                    "course_id": "...",
                    "title": "...",
                    "reason": "...",
                    "priority": 1
                }
            ],
            "learning_path": [...],
            "ai_advice": "..."
        }
    """
    # Tạo prompt cho Gemini
    prompt = f"""
Dựa trên thông tin học viên:

LỊCH SỬ HỌC TẬP:
{json.dumps(user_learning_history, indent=2, ensure_ascii=False)}

KẾT QUẢ ASSESSMENT:
{json.dumps(assessment_results, indent=2, ensure_ascii=False) if assessment_results else "Chưa có"}

Hãy đề xuất lộ trình học tập và các khóa học phù hợp.

Trả về JSON format:
{{
    "recommended_topics": ["Topic 1", "Topic 2"],
    "learning_sequence": ["Học A trước", "Sau đó học B", "Cuối cùng học C"],
    "ai_advice": "Lời khuyên chi tiết cho học viên"
}}

PHẢI trả về JSON hợp lệ.
"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Loại bỏ markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        recommendations = json.loads(response_text)
        
        return {
            "recommended_courses": [],
            "learning_path": recommendations.get("learning_sequence", []),
            "ai_advice": recommendations.get("ai_advice", "")
        }
    
    except Exception as e:
        return {
            "recommended_courses": [],
            "learning_path": [],
            "ai_advice": "Hãy tiếp tục học tập và hoàn thành các khóa học hiện tại."
        }


# ============================================================================
# PERSONAL COURSE GENERATION
# ============================================================================

async def generate_course_from_prompt(
    prompt: str,
    user_preferences: Optional[List[str]] = None,
    difficulty: str = "Beginner"
) -> Dict[str, any]:
    """
    Generate a complete course structure from a text prompt using AI.
    
    Args:
        prompt: User's description of desired course
        user_preferences: User's learning preferences
        difficulty: Course difficulty level
        
    Returns:
        Dict containing course structure (title, description, modules, lessons)
    """
    try:
        # Build prompt for AI
        system_prompt = f"""Bạn là một chuyên gia thiết kế khóa học. 
Nhiệm vụ: Tạo cấu trúc khóa học hoàn chỉnh dựa trên yêu cầu của người dùng.
Cấp độ: {difficulty}
Sở thích người dùng: {', '.join(user_preferences) if user_preferences else 'Không có'}

Trả về JSON với cấu trúc:
{{
    "title": "Tên khóa học",
    "description": "Mô tả chi tiết",
    "category": "Programming|Data Science|Business|...",
    "level": "{difficulty}",
    "estimated_duration": 30,
    "modules": [
        {{
            "title": "Tên module",
            "description": "Mô tả module",
            "order": 1,
            "lessons": [
                {{
                    "title": "Tên bài học",
                    "description": "Mô tả bài học",
                    "content": "Nội dung chi tiết",
                    "duration_minutes": 15,
                    "order": 1
                }}
            ]
        }}
    ]
}}"""

        user_prompt = f"Yêu cầu khóa học: {prompt}"
        
        # Generate course structure
        response = model.generate_content(
            [system_prompt, user_prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000
            )
        )
        
        # Parse response
        response_text = response.text.strip()
        
        # Extract JSON from markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        course_data = json.loads(response_text)
        return course_data
        
    except Exception as e:
        # Fallback structure
        return {
            "title": f"Khóa học về {prompt[:50]}",
            "description": f"Khóa học được tạo tự động dựa trên yêu cầu: {prompt}",
            "category": "General",
            "level": difficulty,
            "estimated_duration": 20,
            "modules": [
                {
                    "title": "Module 1: Giới thiệu",
                    "description": "Module giới thiệu khóa học",
                    "order": 1,
                    "lessons": [
                        {
                            "title": "Bài 1: Tổng quan",
                            "description": "Giới thiệu tổng quan về khóa học",
                            "content": f"Nội dung về {prompt}",
                            "duration_minutes": 20,
                            "order": 1
                        }
                    ]
                }
            ]
        }
