# 📚 HƯỚNG DẪN TEST API - AI LEARNING PLATFORM

> **URL Swagger UI**: http://localhost:8000/docs  
> **Tổng số API**: **84 endpoints**  
> **Ngày tạo**: 04/12/2025  
> **Cơ sở dữ liệu**: MongoDB với dữ liệu mẫu từ `scripts/init_data.py`

---

## 🚀 BƯỚC CHUẨN BỊ

### 1. Khởi động Server
```bash
cd BELEARNINGAI
uvicorn app.main:app --reload
```

### 2. Khởi tạo Dữ liệu Mẫu
```bash
python -m scripts.init_data
```

### 3. Truy cập Swagger UI
- **URL**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 👥 TÀI KHOẢN TEST CÓ SẴN

### 🔑 Admin Account
```json
{
  "email": "admin.super@ailab.com.vn",
  "password": "Admin@12345",
  "role": "admin"
}
```

### 👨‍🏫 Instructor Accounts
```json
{
  "email": "tuananh.nguyen@ailab.edu.vn",
  "password": "Giangvien@123",
  "role": "instructor"
}
{
  "email": "tuyet.le@ailab.edu.vn", 
  "password": "Giangvien@123",
  "role": "instructor"
}
{
  "email": "hung.tran@ailab.edu.vn",
  "password": "Giangvien@123", 
  "role": "instructor"
}
```

### 🎓 Student Accounts
```json
{
  "email": "student1@example.com",
  "password": "Hocvien@123",
  "role": "student"
}
```
> **Lưu ý**: Script tạo 10 tài khoản học viên với email ngẫu nhiên và password `Hocvien@123`. 

### 🔍 Cách tìm các ID cần thiết để test:
1. **Course IDs**: GET `/api/v1/courses/public` hoặc search "Python" 
2. **User IDs**: GET `/api/v1/admin/users` (admin only)
3. **Lesson IDs**: GET `/api/v1/courses/{course_id}/detail` 
4. **Class IDs**: GET `/api/v1/classes` (instructor only)
5. **Quiz IDs**: Từ lesson detail có `quiz_id` field

---

## 🔐 CÁCH SỬ DỤNG AUTHENTICATION

### Bước 1: Đăng nhập
1. Mở Swagger UI → Tìm section **Authentication**
2. Click **POST /api/v1/auth/login**
3. Click **Try it out**
4. Nhập dữ liệu:
```json
{
  "email": "admin.super@ailab.com.vn",
  "password": "Admin@12345",
  "remember_me": true
}
```
5. Click **Execute**
6. **Copy `access_token`** từ response

### Bước 2: Authorize
1. Click nút **🔒 Authorize** ở đầu trang Swagger
2. Nhập: `Bearer <your_access_token>`
3. Click **Authorize**
4. Bây giờ có thể test các API protected!

---

## 📖 TEST CASES CHO TỪNG NHÓM API

## 1️⃣ AUTHENTICATION & USER MANAGEMENT (Section 2.1)

### 🆕 POST /api/v1/auth/register - Đăng ký tài khoản mới
```json
{
  "full_name": "Nguyễn Văn Test",
  "email": "testuser@example.com",
  "password": "TestPassword@123"
}
```
**Expected**: 201 Created với thông tin user mới

### 🔑 POST /api/v1/auth/login - Đăng nhập
```json
{
  "email": "admin.super@ailab.com.vn",
  "password": "Admin@12345",
  "remember_me": true
}
```
**Expected**: 200 OK với access_token và refresh_token

### 🚪 POST /api/v1/auth/logout - Đăng xuất
**Headers**: Authorization: Bearer <token>
```json
{}
```
**Expected**: 200 OK với message thành công

### 👤 GET /api/v1/users/me - Xem thông tin cá nhân
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thông tin user đang đăng nhập

### ✏️ PATCH /api/v1/users/me - Cập nhật thông tin
**Headers**: Authorization: Bearer <token>
```json
{
  "full_name": "Nguyễn Văn Test Updated",
  "bio": "Tôi là một lập trình viên đam mê học hỏi",
  "learning_preferences": ["Programming", "Data Science"],
  "contact_info": "Phone: 0987654321"
}
```
**Expected**: 200 OK với thông tin đã cập nhật

---

## 2️⃣ AI ASSESSMENT (Section 2.2)

### 🧠 POST /api/v1/assessments/generate - Tạo bộ câu hỏi đánh giá
**Headers**: Authorization: Bearer <token>
```json
{
  "category": "Programming",
  "subject": "Python",
  "level": "Beginner",
  "focus_areas": ["python-syntax", "python-basics"]
}
```
**Expected**: 201 Created với `session_id` và danh sách câu hỏi
**Lưu ý**: Lưu `session_id` để test bước tiếp theo

### 📝 POST /api/v1/assessments/{session_id}/submit - Nộp bài đánh giá
**Path**: Thay `{session_id}` bằng ID từ bước trước
**Headers**: Authorization: Bearer <token>
```json
{
  "answers": [
    {
      "question_id": "question-uuid-1",
      "answer_content": "list = []",
      "selected_option": 1,
      "time_taken_seconds": 45
    },
    {
      "question_id": "question-uuid-2", 
      "answer_content": "def my_function():",
      "time_taken_seconds": 60
    }
  ],
  "total_time_seconds": 900,
  "submitted_at": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với status submitted

### 📊 GET /api/v1/assessments/{session_id}/results - Xem kết quả đánh giá
**Path**: Thay `{session_id}` bằng ID từ bước generate
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với điểm số, phân tích skill, knowledge gaps

### 💡 GET /api/v1/recommendations/from-assessment - Lộ trình học tập từ đánh giá
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách khóa học được đề xuất

### 🧠 POST /api/v1/courses/{course_id}/modules/{module_id}/assessments/generate - Tạo quiz từ module
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <token>
```json
{
  "difficulty": "medium",
  "question_count": 15,
  "include_mandatory": true,
  "focus_outcomes": ["python-syntax", "python-functions"]
}
```
**Expected**: 201 Created với quiz được AI tạo từ module content

---

## 🔟 DASHBOARD & RECOMMENDATIONS (Section 2.7) - 4 endpoints

### 📊 GET /api/v1/dashboard/student - Dashboard học viên
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Danh sách khóa học đang học (progress %)
- Quiz pending cần làm
- Achievements gần đây
- Study streak (chuỗi học liên tục)
- Thống kê tổng quan (lessons completed, avg quiz score)

### 👨‍🏫 GET /api/v1/dashboard/instructor - Dashboard giảng viên
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với:
- Số lớp học đang dạy
- Tổng số học viên
- Quiz đã tạo
- Tỷ lệ hoàn thành trung bình
- Quick actions (tạo quiz, xem progress)

### 🛠️ GET /api/v1/dashboard/admin - Dashboard admin
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với:
- Tổng users/courses/classes
- Thống kê theo role
- Hoạt động hệ thống (enrollments mới, quiz completed)
- System health metrics

### 💡 GET /api/v1/recommendations - Đề xuất khóa học
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `type`: "similar_courses" hoặc "based_on_progress" hoặc "popular"
- `category`: "Programming" (optional)
- `limit`: 5

**Expected**: 200 OK với danh sách khóa học đề xuất dựa trên AI analysis

---

## 3️⃣ COURSE DISCOVERY (Section 2.3)

### 🔍 GET /api/v1/courses/search - Tìm kiếm khóa học
**Query Parameters**:
- `keyword`: "Python" 
- `category`: "Programming"
- `level`: "Beginner"
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách khóa học Python

### 📚 GET /api/v1/courses/public - Danh sách khóa học công khai
**Query Parameters**:
- `skip`: 0
- `limit`: 10
- `sort_by`: "created_at"
- `order`: "desc"

**Expected**: 200 OK với danh sách tất cả khóa học

### 📖 GET /api/v1/courses/{course_id}/detail - Chi tiết khóa học
**Path**: Thay `{course_id}` bằng ID khóa học Python từ search
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thông tin đầy đủ khóa học, modules, lessons

### ✅ GET /api/v1/courses/{course_id}/enrollment-status - Trạng thái đăng ký
**Path**: Thay `{course_id}` bằng ID khóa học
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với trạng thái enrolled/not_enrolled

---

## 4️⃣ ENROLLMENT (Section 2.3)

### 📝 POST /api/v1/enrollments - Đăng ký khóa học
**Headers**: Authorization: Bearer <token>
```json
{
  "course_id": "course-uuid-from-search"
}
```
**Expected**: 201 Created với enrollment record

### 📋 GET /api/v1/enrollments/my-courses - Danh sách khóa học đã đăng ký
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `status`: "active"
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách khóa học đã enroll

### 📊 GET /api/v1/enrollments/{enrollment_id}/detail - Chi tiết enrollment
**Path**: Thay `{enrollment_id}` bằng ID từ my-courses
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thông tin chi tiết enrollment

### ❌ DELETE /api/v1/enrollments/{enrollment_id} - Hủy đăng ký
**Path**: Thay `{enrollment_id}` bằng ID enrollment
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với message hủy thành công

---

## 5️⃣ LEARNING PROGRESS (Section 2.4)

### 📚 GET /api/v1/learning/courses - Khóa học đang học
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách khóa học + progress

### 📖 GET /api/v1/learning/courses/{course_id} - Chi tiết học tập khóa học
**Path**: Thay `{course_id}` bằng ID khóa học đã enroll
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với modules, lessons, progress từng lesson

### ▶️ POST /api/v1/learning/lessons/{lesson_id}/start - Bắt đầu học bài
**Path**: Thay `{lesson_id}` bằng ID lesson từ course detail
**Headers**: Authorization: Bearer <token>
```json
{
  "started_at": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với session bắt đầu học

### ✅ POST /api/v1/learning/lessons/{lesson_id}/complete - Hoàn thành bài học
**Path**: Thay `{lesson_id}` bằng ID lesson đã start
**Headers**: Authorization: Bearer <token>
```json
{
  "completed_at": "2025-12-04T11:00:00Z",
  "time_spent_minutes": 30,
  "completion_percentage": 100,
  "notes": "Đã hiểu về cú pháp Python cơ bản"
}
```
**Expected**: 200 OK với progress updated

---

## 6️⃣ QUIZ SYSTEM (Section 2.4)

### 📝 GET /api/v1/quiz/{quiz_id}/detail - Chi tiết quiz
**Path**: Thay `{quiz_id}` bằng ID quiz từ lesson
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với câu hỏi quiz

### ✍️ POST /api/v1/quiz/{quiz_id}/attempt - Làm bài quiz
**Path**: Thay `{quiz_id}` bằng ID quiz
**Headers**: Authorization: Bearer <token>
```json
{
  "answers": [
    {
      "question_id": "quiz-question-1",
      "selected_answer": "A",
      "time_taken_seconds": 30
    },
    {
      "question_id": "quiz-question-2",
      "selected_answer": "C", 
      "time_taken_seconds": 45
    }
  ],
  "total_time_seconds": 300
}
```
**Expected**: 200 OK với attempt_id

### 📊 GET /api/v1/quiz/{quiz_id}/results/{attempt_id} - Kết quả quiz
**Path**: Thay `{quiz_id}` và `{attempt_id}` bằng ID tương ứng
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với điểm số và giải thích

### 🔄 POST /api/v1/quiz/{quiz_id}/retake - Làm lại quiz
**Path**: Thay `{quiz_id}` bằng ID quiz
**Headers**: Authorization: Bearer <token>
```json
{
  "reason": "Muốn cải thiện điểm số"
}
```
**Expected**: 200 OK cho phép làm lại

---

## 7️⃣ PROGRESS TRACKING (Section 2.4)

### 📈 GET /api/v1/progress/overall - Tổng quan tiến độ học tập
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với tổng quan progress tất cả khóa học

### 📊 GET /api/v1/progress/courses/{course_id} - Tiến độ khóa học cụ thể
**Path**: Thay `{course_id}` bằng ID khóa học
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với progress chi tiết từng module/lesson

### 📝 GET /api/v1/progress/courses/{course_id}/analytics - Phân tích học tập
**Path**: Thay `{course_id}` bằng ID khóa học
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thống kê thời gian học, performance

### ⏱️ POST /api/v1/progress/time-tracking - Ghi nhận thời gian học
**Headers**: Authorization: Bearer <token>
```json
{
  "course_id": "course-uuid",
  "lesson_id": "lesson-uuid", 
  "session_start": "2025-12-04T10:00:00Z",
  "session_end": "2025-12-04T10:30:00Z",
  "activity_type": "reading"
}
```
**Expected**: 200 OK với time tracking updated

---

## 8️⃣ PERSONAL COURSES (Section 2.5) - 5 endpoints

### 🤖 POST /api/v1/personal-courses/ai-generate - Tạo khóa học từ AI prompt
**Headers**: Authorization: Bearer <token>
```json
{
  "prompt": "Tôi muốn học lập trình Python từ cơ bản đến nâng cao, bao gồm web development và machine learning",
  "category": "Programming",
  "level": "Intermediate"
}
```
**Expected**: 201 Created với khóa học được AI tạo tự động (modules + lessons)

### 📚 GET /api/v1/personal-courses - Khóa học cá nhân
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `status`: "draft" hoặc "published" hoặc "archived"
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách khóa học cá nhân + thống kê

### ➕ POST /api/v1/personal-courses - Tạo khóa học thủ công
**Headers**: Authorization: Bearer <token>
```json
{
  "title": "Khóa học Python cá nhân của tôi",
  "description": "Tự học Python theo lộ trình cá nhân, từ syntax cơ bản đến ứng dụng thực tế",
  "category": "Programming",
  "level": "Beginner",
  "thumbnail_url": "https://example.com/python-thumb.jpg",
  "language": "vi"
}
```
**Expected**: 201 Created với khóa học mới (trạng thái draft)

### ✏️ PUT /api/v1/personal-courses/{course_id} - Cập nhật khóa học
**Path**: Thay `{course_id}` bằng ID personal course
**Headers**: Authorization: Bearer <token>
```json
{
  "title": "Khóa học Python nâng cao",
  "description": "Cập nhật mô tả khóa học với nội dung chi tiết hơn",
  "status": "published",
  "modules": [
    {
      "title": "Module 1: Python Cơ bản",
      "description": "Học syntax và concepts cơ bản",
      "order": 1,
      "difficulty": "Basic",
      "estimated_hours": 10,
      "learning_outcomes": ["Hiểu cú pháp Python", "Viết được functions"],
      "lessons": [
        {
          "title": "Biến và Kiểu dữ liệu",
          "order": 1,
          "content": "<h2>Variables trong Python</h2><p>Python hỗ trợ nhiều kiểu dữ liệu...</p>",
          "content_type": "text",
          "duration_minutes": 30
        }
      ]
    }
  ]
}
```
**Expected**: 200 OK với khóa học và modules đã cập nhật

### 🗑️ DELETE /api/v1/personal-courses/{course_id} - Xóa khóa học
**Path**: Thay `{course_id}` bằng ID personal course
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với message xóa thành công

### 📊 GET /api/v1/personal-courses/{course_id}/progress - Tiến độ khóa học cá nhân
**Path**: Thay `{course_id}` bằng ID personal course
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với thống kê progress

---

## 9️⃣ AI CHATBOT (Section 2.6)

### 💬 GET /api/v1/chat/conversations - Danh sách cuộc trò chuyện
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách conversations

### 🆕 POST /api/v1/chat/conversations - Tạo cuộc trò chuyện mới
**Headers**: Authorization: Bearer <token>
```json
{
  "title": "Hỏi về Python cơ bản",
  "context": "Tôi đang học Python và cần hỗ trợ"
}
```
**Expected**: 201 Created với conversation mới

### 📤 POST /api/v1/chat/conversations/{conversation_id}/message - Gửi tin nhắn
**Path**: Thay `{conversation_id}` bằng ID conversation
**Headers**: Authorization: Bearer <token>
```json
{
  "message": "Làm thế nào để khai báo list trong Python?",
  "message_type": "question"
}
```
**Expected**: 200 OK với phản hồi từ AI

### 📜 GET /api/v1/chat/conversations/{conversation_id}/history - Lịch sử trò chuyện
**Path**: Thay `{conversation_id}` bằng ID conversation
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với toàn bộ lịch sử chat

### 🗑️ DELETE /api/v1/chat/conversations/{conversation_id} - Xóa cuộc trò chuyện
**Path**: Thay `{conversation_id}` bằng ID conversation
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với message xóa thành công

---

## 🔟 DASHBOARD & RECOMMENDATIONS (Section 2.7)

### 📊 GET /api/v1/dashboard/student - Dashboard học viên
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với tổng quan stats học viên

### 💡 GET /api/v1/recommendations - Đề xuất khóa học
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `type`: "similar_courses"
- `limit`: 5

**Expected**: 200 OK với danh sách khóa học đề xuất

### 📈 GET /api/v1/analytics/learning-time - Thống kê thời gian học
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `period`: "last_30_days"

**Expected**: 200 OK với biểu đồ thời gian học

### 🏆 GET /api/v1/analytics/achievements - Thành tích học tập
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách achievements

---

## 1️⃣1️⃣ INSTRUCTOR FEATURES (Section 3.x) - 10 endpoints

### 📚 POST /api/v1/classes - Tạo lớp học mới (Instructor)
**Headers**: Authorization: Bearer <instructor_token>
```json
{
  "name": "Lớp Python Cơ bản Tháng 12",
  "description": "Lớp học Python dành cho người mới bắt đầu",
  "course_id": "course-uuid-from-search-python",
  "max_students": 30,
  "start_date": "2025-12-15T09:00:00Z",
  "end_date": "2026-02-15T17:00:00Z"
}
```
**Expected**: 201 Created với class mới và invite_code

### 👥 GET /api/v1/classes - Danh sách lớp học
**Headers**: Authorization: Bearer <instructor_token>
**Query Parameters**:
- `status`: "active" 
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách lớp do giảng viên quản lý

### 📖 GET /api/v1/classes/{class_id} - Chi tiết lớp học
**Path**: Thay `{class_id}` bằng ID từ danh sách classes
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với thông tin chi tiết lớp học

### ✏️ PUT /api/v1/classes/{class_id} - Cập nhật lớp học
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
```json
{
  "name": "Lớp Python Nâng cao",
  "description": "Cập nhật mô tả lớp học",
  "max_students": 25
}
```
**Expected**: 200 OK với thông tin đã cập nhật

### 🗑️ DELETE /api/v1/classes/{class_id} - Xóa lớp học
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với message xóa thành công

### ➕ POST /api/v1/classes/{class_id}/students - Thêm học viên vào lớp
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
```json
{
  "user_id": "student-uuid",
  "enrollment_method": "invite_code"
}
```
**Expected**: 201 Created với enrollment thành công

### 👥 GET /api/v1/classes/{class_id}/students - Danh sách học viên trong lớp
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với danh sách students + progress

### 📊 GET /api/v1/classes/{class_id}/student/{student_id} - Chi tiết học viên
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với progress chi tiết của học viên

### 🚫 DELETE /api/v1/classes/{class_id}/students/{student_id} - Xóa học viên khỏi lớp
**Path**: Thay các ID tương ứng  
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với message xóa thành công

### 📈 GET /api/v1/classes/{class_id}/analytics - Analytics lớp học
**Path**: Thay `{class_id}` bằng ID class
**Headers**: Authorization: Bearer <instructor_token>
**Expected**: 200 OK với thống kê chi tiết về lớp học

---

## 1️⃣2️⃣ ADMIN FEATURES (Section 4.x) - 18 endpoints

### 📊 GET /api/v1/admin/dashboard - Dashboard admin tổng quan
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thống kê chi tiết:
```json
{
  "total_users": 15,
  "users_by_role": {
    "student": 10,
    "instructor": 4,
    "admin": 1
  },
  "total_courses": 5,
  "courses_stats": {
    "published": 3,
    "draft": 2
  },
  "total_classes": 8,
  "active_classes": 5,
  "total_enrollments": 25
}
```

### 👥 GET /api/v1/admin/users - Quản lý người dùng (Admin)
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `role`: "student" hoặc "instructor" hoặc "admin"
- `status`: "active" hoặc "inactive"
- `search`: "tên user hoặc email" (tìm kiếm)
- `skip`: 0, `limit`: 10

**Expected**: 200 OK với danh sách users:
```json
{
  "data": [
    {
      "user_id": "uuid",
      "full_name": "Nguyễn Văn A",
      "email": "student1@example.com",
      "avatar": "https://...",
      "role": "student",
      "status": "active",
      "created_at": "2025-01-01T00:00:00Z",
      "last_login": "2025-01-03T15:30:00Z",
      "enrollment_count": 3
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 10,
  "has_next": true
}
```

### 🔍 GET /api/v1/admin/users/{user_id} - Chi tiết người dùng
**Path**: Thay `{user_id}` bằng UUID user
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thông tin chi tiết:
```json
{
  "user_id": "uuid",
  "full_name": "Nguyễn Văn A",
  "email": "student1@example.com",
  "role": "student",
  "status": "active",
  "statistics": {
    "enrolled_courses": 3,
    "completed_courses": 1,
    "average_score": 85.5
  },
  "current_enrollments": [
    {
      "course_id": "course-uuid",
      "course_title": "Python Cơ Bản",
      "progress": 75.0,
      "status": "in-progress"
    }
  ]
}
```

### ➕ POST /api/v1/admin/users - Tạo người dùng mới
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "full_name": "Giảng Viên Mới",
  "email": "newteacher@ailab.edu.vn", 
  "password": "TempPassword@123",
  "role": "instructor",
  "bio": "Giảng viên chuyên về AI"
}
```
**Expected**: 201 Created với user mới

### ✏️ PUT /api/v1/admin/users/{user_id} - Cập nhật thông tin user
**Path**: Thay `{user_id}` bằng UUID user
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "full_name": "Tên mới", 
  "bio": "Bio mới",
  "status": "inactive"
}
```
**Expected**: 200 OK với user đã cập nhật

### 🔄 PUT /api/v1/admin/users/{user_id}/role - Thay đổi role user
**Path**: Thay `{user_id}` bằng UUID user
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "new_role": "instructor"
}
```
**Expected**: 200 OK với thông tin impact (ảnh hưởng đến classes, enrollments)

### 🔑 POST /api/v1/admin/users/{user_id}/reset-password - Reset mật khẩu
**Path**: Thay `{user_id}` bằng UUID user
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "new_password": "NewTempPassword@123"
}
```
**Expected**: 200 OK với message confirm

### 🗑️ DELETE /api/v1/admin/users/{user_id} - Xóa người dùng
**Path**: Thay `{user_id}` bằng UUID user (test với user không có enrollment)
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với message confirm deletion

### 📚 GET /api/v1/admin/courses - Quản lý khóa học
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `status`: "published" hoặc "draft"
- `course_type`: "public" hoặc "personal"
- `author_id`: UUID của tác giả
- `skip`: 0, `limit`: 10

**Expected**: 200 OK với tất cả khóa học trong hệ thống

### 🔍 GET /api/v1/admin/courses/{course_id} - Chi tiết khóa học (Admin)
**Path**: Thay `{course_id}` bằng UUID course
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với chi tiết đầy đủ course + analytics

### ➕ POST /api/v1/admin/courses - Tạo khóa học mới (Admin)
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "title": "Khóa học AI cơ bản",
  "description": "Khóa học về AI dành cho người mới bắt đầu...",
  "category": "Technology",
  "level": "Beginner",
  "language": "vi",
  "thumbnail_url": "https://example.com/thumb.jpg",
  "prerequisites": ["Kiến thức máy tính cơ bản"],
  "learning_outcomes": [
    {"description": "Hiểu được AI là gì"}
  ],
  "status": "published"
}
```
**Expected**: 201 Created với course mới

### ✏️ PUT /api/v1/admin/courses/{course_id} - Cập nhật khóa học
**Path**: Thay `{course_id}` bằng UUID course
**Headers**: Authorization: Bearer <admin_token>
```json
{
  "title": "Tiêu đề mới",
  "description": "Mô tả mới...",
  "status": "archived"
}
```
**Expected**: 200 OK với thông tin đã update

### 🗑️ DELETE /api/v1/admin/courses/{course_id} - Xóa khóa học
**Path**: Thay `{course_id}` bằng UUID course (test với course ít ảnh hưởng)
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thông tin impact và confirm deletion

### 🏫 GET /api/v1/admin/classes - Quản lý lớp học admin
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `status`: "preparing", "active", "completed"
- `instructor_id`: UUID giảng viên
- `skip`: 0, `limit`: 10

**Expected**: 200 OK với danh sách classes:
```json
{
  "data": [
    {
      "class_id": "uuid",
      "class_name": "Lớp Python Cơ Bản - Batch 1",
      "instructor_name": "Nguyễn Văn Giảng",
      "instructor_email": "instructor@example.com",
      "course_title": "Python Cơ Bản",
      "student_count": 15,
      "max_students": 20,
      "status": "active",
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-03-01T00:00:00Z",
      "created_at": "2024-12-15T00:00:00Z"
    }
  ],
  "total": 8,
  "has_next": false
}
```

### 🏫 GET /api/v1/admin/classes/{class_id} - Chi tiết lớp học admin
**Path**: Thay `{class_id}` bằng UUID lớp học
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thông tin chi tiết:
```json
{
  "class_id": "uuid",
  "class_name": "Lớp Python Cơ Bản - Batch 1",
  "description": "Lớp học dành cho người mới bắt đầu",
  "course_id": "course-uuid",
  "course_title": "Python Cơ Bản",
  "invite_code": "PYTHON2025",
  "status": "active",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-03-01T00:00:00Z",
  "max_students": 20,
  "instructor_info": {
    "instructor_id": "instructor-uuid",
    "instructor_name": "Nguyễn Văn Giảng",
    "instructor_email": "instructor@example.com",
    "total_classes": 3,
    "total_students_taught": 45
  },
  "students": [
    {
      "student_id": "student-uuid",
      "student_name": "Nguyễn Văn A",
      "student_email": "student1@example.com",
      "progress": 75.0,
      "lessons_completed": 15,
      "avg_quiz_score": 85.5,
      "last_activity": "2025-01-03T15:30:00Z",
      "joined_at": "2025-01-01T00:00:00Z",
      "enrollment_status": "enrolled"
    }
  ],
  "stats": {
    "total_students": 15,
    "active_students": 14,
    "avg_progress": 68.5,
    "avg_quiz_score": 82.3,
    "completion_rate": 75.0,
    "total_lessons": 20,
    "total_quizzes": 10
  }
}
```

### 📈 GET /api/v1/admin/system/users-growth - Thống kê tăng trưởng users
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `period`: "last_30_days" hoặc "last_90_days" hoặc "last_year"

**Expected**: 200 OK với biểu đồ tăng trưởng users

### 📊 GET /api/v1/admin/system/course-analytics - Phân tích khóa học
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thống kê về các khóa học

### ⚡ GET /api/v1/admin/system/health - Tình trạng hệ thống
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với health metrics hệ thống

---

## 1️⃣3️⃣ ANALYTICS FEATURES (Section 2.7, 3.4, 4.4) - 8 endpoints

### 📊 GET /api/v1/analytics/learning-stats - Thống kê học tập chi tiết (Student)
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với metrics học tập của student

### 📈 GET /api/v1/analytics/progress-chart - Biểu đồ tiến độ (Student)
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `period`: "last_30_days"
- `course_id`: "course-uuid" (optional)

**Expected**: 200 OK với dữ liệu biểu đồ tiến độ

### 👨‍🏫 GET /api/v1/analytics/instructor/class-stats - Thống kê lớp học (Instructor)
**Headers**: Authorization: Bearer <instructor_token>
**Query Parameters**:
- `class_id`: "class-uuid" (optional)

**Expected**: 200 OK với thống kê các lớp dạy

### 📊 GET /api/v1/analytics/instructor/progress-chart - Biểu đồ tiến độ lớp (Instructor)
**Headers**: Authorization: Bearer <instructor_token>
**Query Parameters**:
- `class_id`: "class-uuid"
- `period`: "last_30_days"

**Expected**: 200 OK với dữ liệu tiến độ học viên

### 📝 GET /api/v1/analytics/instructor/quiz-performance - Hiệu suất quiz (Instructor)
**Headers**: Authorization: Bearer <instructor_token>
**Query Parameters**:
- `class_id`: "class-uuid"

**Expected**: 200 OK với phân tích hiệu suất quiz

### 🏢 GET /api/v1/analytics/admin/users-growth - Tăng trưởng users (Admin)
**Headers**: Authorization: Bearer <admin_token>
**Query Parameters**:
- `period`: "last_90_days"

**Expected**: 200 OK với dữ liệu tăng trưởng

### 📚 GET /api/v1/analytics/admin/course-analytics - Phân tích khóa học (Admin)
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với thống kê toàn bộ khóa học

### ⚡ GET /api/v1/analytics/admin/system-health - Sức khỏe hệ thống (Admin)
**Headers**: Authorization: Bearer <admin_token>
**Expected**: 200 OK với metrics hệ thống

---

## 1️⃣4️⃣ CHAT AI FEATURES (Section 2.6) - 5 endpoints

### 💬 POST /api/v1/chat/course/{course_id} - Gửi câu hỏi cho AI
**Path**: Thay `{course_id}` bằng UUID course đã enroll
**Headers**: Authorization: Bearer <token>
```json
{
  "question": "Làm thế nào để khai báo list trong Python?",
  "conversation_id": null
}
```
**Expected**: 201 Created với câu trả lời từ AI + sources từ lessons

### 📜 GET /api/v1/chat/history - Lịch sử conversations
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `course_id`: "course-uuid" (optional filter)
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với danh sách conversations

### 🔍 GET /api/v1/chat/conversations/{conversation_id} - Chi tiết conversation
**Path**: Thay `{conversation_id}` bằng ID từ history
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với toàn bộ messages trong conversation

### 🗑️ DELETE /api/v1/chat/conversations - Xóa toàn bộ lịch sử
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với số lượng conversations đã xóa

### 🗑️ DELETE /api/v1/chat/history/{conversation_id} - Xóa một conversation
**Path**: Thay `{conversation_id}` bằng ID conversation
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với message xóa thành công

---

## 1️⃣5️⃣ SEARCH FEATURES (Section 5.1) - 4 endpoints

### 🔍 GET /api/v1/search/global - Tìm kiếm toàn hệ thống
**Query Parameters**:
- `q`: "Python"
- `type`: "all"
- `skip`: 0
- `limit`: 10

**Expected**: 200 OK với kết quả mixed (courses, lessons, users)

### 🔍 GET /api/v1/search/courses - Tìm kiếm khóa học
**Query Parameters**:
- `q`: "machine learning"
- `category`: "Programming"

**Expected**: 200 OK với danh sách khóa học liên quan

### 📝 GET /api/v1/search/suggestions - Gợi ý tìm kiếm
**Query Parameters**:
- `partial`: "pytho"

**Expected**: 200 OK với danh sách gợi ý từ khóa

### 📜 GET /api/v1/search/history - Lịch sử tìm kiếm
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với lịch sử searches của user

---

## 1️⃣6️⃣ PROGRESS TRACKING EXTENDED (Section 2.4) - 4 endpoints

### 📊 GET /api/v1/progress/courses/{course_id}/analytics - Phân tích học tập chi tiết
**Path**: Thay `{course_id}` bằng ID khóa học đã enroll
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `period`: "last_30_days" hoặc "all_time"

**Expected**: 200 OK với:
- Biểu đồ thời gian học theo ngày/tuần
- Performance trends (quiz scores theo thời gian)
- Thống kê study habits (thời gian học mỗi ngày)
- So sánh với học viên khác (anonymous)

### ⏱️ POST /api/v1/progress/time-tracking - Ghi nhận thời gian học
**Headers**: Authorization: Bearer <token>
```json
{
  "course_id": "course-uuid", 
  "lesson_id": "lesson-uuid",
  "session_start": "2025-12-04T10:00:00Z",
  "session_end": "2025-12-04T10:30:00Z",
  "activity_type": "reading"
}
```
**Expected**: 200 OK với time tracking updated

### 📈 GET /api/v1/progress/overall/analytics - Analytics tổng quan tất cả khóa học
**Headers**: Authorization: Bearer <token>
**Query Parameters**:
- `time_range`: "last_7_days" hoặc "last_30_days" hoặc "last_90_days"

**Expected**: 200 OK với analytics tổng hợp tất cả khóa học

### 🏆 GET /api/v1/progress/achievements - Thành tích và badges
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách achievements đã đạt được

---

## 1️⃣7️⃣ LEARNING EXTENDED FEATURES (Section 2.4) - 6 endpoints

### 📚 GET /api/v1/courses/{course_id}/modules - Danh sách modules
**Path**: Thay `{course_id}` bằng ID khóa học đã enroll
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách modules + progress cho mỗi module

### 🎯 GET /api/v1/courses/{course_id}/modules/{module_id} - Chi tiết module
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Thông tin module (title, description, difficulty, estimated_hours)
- Danh sách lessons với trạng thái hoàn thành
- Learning outcomes và progress
- Resources và attachments
- Prerequisites modules

### 📖 GET /api/v1/courses/{course_id}/lessons/{lesson_id} - Chi tiết bài học
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Nội dung lesson (text_content, video_info, attachments)
- Navigation (previous/next lesson IDs)
- Progress tracking (thời gian học, video progress)
- Quiz liên kết (quiz_id, quiz_passed status)
- Trạng thái khóa lesson tiếp theo

### 📎 GET /api/v1/courses/{course_id}/modules/{module_id}/resources - Tài nguyên module
**Path**: Thay các ID tương ứng
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Danh sách files, PDFs, links
- Phân loại theo type (pdf, video, code, slide)
- Kích thước files và links download

### 🎯 GET /api/v1/courses/{course_id}/modules/{module_id}/outcomes - Learning outcomes
**Path**: Thay các ID tương ứng 
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với:
- Chi tiết từng learning outcome
- Skill tags để tracking
- Trạng thái đạt được của từng outcome
- Mandatory vs optional outcomes

### 📖 GET /api/v1/learning/lessons/{lesson_id}/resources - Tài nguyên bài học
**Path**: Thay `{lesson_id}` bằng ID lesson
**Headers**: Authorization: Bearer <token>
**Expected**: 200 OK với danh sách files, links, materials

### ▶️ POST /api/v1/learning/lessons/{lesson_id}/start - Bắt đầu học bài
**Path**: Thay `{lesson_id}` bằng ID lesson
**Headers**: Authorization: Bearer <token>
```json
{
  "started_at": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với session bắt đầu học

### ✅ POST /api/v1/learning/lessons/{lesson_id}/complete - Hoàn thành bài học
**Path**: Thay `{lesson_id}` bằng ID lesson đã start
**Headers**: Authorization: Bearer <token>
```json
{
  "completed_at": "2025-12-04T11:00:00Z",
  "time_spent_minutes": 30,
  "completion_percentage": 100,
  "notes": "Đã hiểu về cú pháp Python cơ bản"
}
```
**Expected**: 200 OK với progress updated

### ▶️ POST /api/v1/learning/lessons/{lesson_id}/start - Bắt đầu học bài
**Path**: Thay `{lesson_id}` bằng ID lesson
**Headers**: Authorization: Bearer <token>
```json
{
  "started_at": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với session bắt đầu học

### ✅ POST /api/v1/learning/lessons/{lesson_id}/complete - Hoàn thành bài học
**Path**: Thay `{lesson_id}` bằng ID lesson đã start
**Headers**: Authorization: Bearer <token>
```json
{
  "completed_at": "2025-12-04T11:00:00Z",
  "time_spent_minutes": 30,
  "completion_percentage": 100,
  "notes": "Đã hiểu về cú pháp Python cơ bản",
  "video_progress_seconds": 1200
}
```
**Expected**: 200 OK với progress updated và lesson unlocked tiếp theo

### ⏰ POST /api/v1/learning/time-tracking - Tracking thời gian học
**Headers**: Authorization: Bearer <token>
```json
{
  "course_id": "course-uuid",
  "lesson_id": "lesson-uuid",
  "session_duration_seconds": 1800,
  "activity_type": "video_watching",
  "timestamp": "2025-12-04T10:30:00Z"
}
```
**Expected**: 200 OK với time tracking recorded

---

## ⚠️ DANH SÁCH ĐẦY ĐỦ 84 API ENDPOINTS

### 🔐 Authentication (3 endpoints)
1. POST /api/v1/auth/register
2. POST /api/v1/auth/login  
3. POST /api/v1/auth/logout

### 👤 User Management (2 endpoints)
4. GET /api/v1/users/me
5. PATCH /api/v1/users/me

### 🧠 AI Assessment (3 endpoints)  
6. POST /api/v1/assessments/generate
7. POST /api/v1/assessments/{session_id}/submit
8. GET /api/v1/assessments/{session_id}/results

### 📚 Courses (4 endpoints)
9. GET /api/v1/courses/search
10. GET /api/v1/courses/public
11. GET /api/v1/courses/{course_id}/detail
12. GET /api/v1/courses/{course_id}/enrollment-status

### 📝 Enrollments (4 endpoints)
13. POST /api/v1/enrollments
14. GET /api/v1/enrollments/my-courses
15. GET /api/v1/enrollments/{enrollment_id}/detail  
16. DELETE /api/v1/enrollments/{enrollment_id}

### 📖 Learning (6 endpoints)
17. GET /api/v1/learning/courses
18. GET /api/v1/learning/courses/{course_id}
19. GET /api/v1/learning/lessons/{lesson_id}
20. GET /api/v1/learning/modules/{module_id}
21. GET /api/v1/learning/lessons/{lesson_id}/resources
22. POST /api/v1/learning/time-tracking

### 📝 Quizzes (10 endpoints)  
23. GET /api/v1/quiz/{quiz_id}/detail
24. POST /api/v1/quiz/{quiz_id}/attempt
25. GET /api/v1/quiz/{quiz_id}/results/{attempt_id}
26. POST /api/v1/quiz/{quiz_id}/retake
27. POST /api/v1/quiz/create  
28. GET /api/v1/quiz/instructor
29. PUT /api/v1/quiz/{quiz_id}
30. DELETE /api/v1/quiz/{quiz_id}
31. GET /api/v1/quiz/{quiz_id}/attempts
32. GET /api/v1/quiz/{quiz_id}/analytics

### 📊 Progress (4 endpoints)
33. GET /api/v1/progress/overall
34. GET /api/v1/progress/courses/{course_id}
35. GET /api/v1/progress/courses/{course_id}/analytics
36. GET /api/v1/progress/achievements

### 🎓 Personal Courses (5 endpoints)
37. GET /api/v1/personal-courses
38. POST /api/v1/personal-courses
39. GET /api/v1/personal-courses/{course_id}/progress
40. PUT /api/v1/personal-courses/{course_id}
41. DELETE /api/v1/personal-courses/{course_id}

### 💬 AI Chat (5 endpoints)
42. POST /api/v1/chat/course/{course_id}
43. GET /api/v1/chat/history
44. GET /api/v1/chat/conversations/{conversation_id}
45. DELETE /api/v1/chat/conversations
46. DELETE /api/v1/chat/history/{conversation_id}

### 💡 Recommendations (2 endpoints)
47. GET /api/v1/recommendations
48. GET /api/v1/recommendations/from-assessment

### 📊 Dashboard (3 endpoints)
49. GET /api/v1/dashboard/student
50. GET /api/v1/dashboard/instructor  
51. GET /api/v1/dashboard/admin

### 🔍 Search (4 endpoints)
52. GET /api/v1/search/global
53. GET /api/v1/search/courses
54. GET /api/v1/search/suggestions
55. GET /api/v1/search/history

### 🏫 Classes - Instructor (10 endpoints)
56. POST /api/v1/classes
57. GET /api/v1/classes
58. GET /api/v1/classes/{class_id}
59. PUT /api/v1/classes/{class_id}
60. DELETE /api/v1/classes/{class_id}
61. POST /api/v1/classes/{class_id}/students
62. GET /api/v1/classes/{class_id}/students
63. GET /api/v1/classes/{class_id}/student/{student_id}
64. DELETE /api/v1/classes/{class_id}/students/{student_id}
65. GET /api/v1/classes/{class_id}/analytics

### 📊 Analytics (8 endpoints)
66. GET /api/v1/analytics/learning-stats
67. GET /api/v1/analytics/progress-chart
68. GET /api/v1/analytics/instructor/class-stats
69. GET /api/v1/analytics/instructor/progress-chart
70. GET /api/v1/analytics/instructor/quiz-performance
71. GET /api/v1/analytics/admin/users-growth
72. GET /api/v1/analytics/admin/course-analytics
73. GET /api/v1/analytics/admin/system-health

### 🛠️ Admin Management (18 endpoints)
74. GET /api/v1/admin/users
75. GET /api/v1/admin/users/{user_id}
76. POST /api/v1/admin/users
77. PUT /api/v1/admin/users/{user_id}
78. DELETE /api/v1/admin/users/{user_id}
79. PUT /api/v1/admin/users/{user_id}/role
80. POST /api/v1/admin/users/{user_id}/reset-password
81. GET /api/v1/admin/courses
82. GET /api/v1/admin/courses/{course_id}
83. POST /api/v1/admin/courses
84. PUT /api/v1/admin/courses/{course_id}
85. DELETE /api/v1/admin/courses/{course_id}
86. GET /api/v1/admin/classes
87. GET /api/v1/admin/classes/{class_id}

> **Lưu ý**: Có thể có sự chênh lệch nhỏ do cách đếm, nhưng đây là danh sách đầy đủ các endpoints có trong hệ thống.

## ⚠️ LƯU Ý QUAN TRỌNG

### 🔑 Authentication Token
- Access token có thời hạn **15 phút**
- Nếu token hết hạn → Error 401 → Đăng nhập lại
- Refresh token có thời hạn **7 ngày** (remember_me=true)

### 🚫 Common Error Codes
- **400**: Bad Request (validation error, missing fields)
- **401**: Unauthorized (token không hợp lệ/hết hạn)  
- **403**: Forbidden (không có quyền)
- **404**: Not Found (resource không tồn tại)
- **500**: Internal Server Error

### 📊 Dữ Liệu Test Có Sẵn
- **1 Admin**: admin.super@ailab.com.vn / Admin@12345
- **3 Instructors**: tuananh.nguyen@, tuyet.le@, hung.tran@ / Giangvien@123  
- **~10 Students**: random emails / Hocvien@123
- **Khóa học Python**: "Lập trình Python từ Cơ bản đến Nâng cao"
- **2 Modules**: Python Cơ bản + Cấu trúc dữ liệu
- **6+ Lessons**: Từng module có 3+ lessons với content chi tiết
- **Quiz data**: Mỗi lesson có quiz với câu hỏi mẫu
- **AI Assessment**: Tự động sinh câu hỏi với Google Gemini

### 🔍 Cách Lấy Dữ Liệu Cần Thiết
1. **Course IDs**: Sau khi init data, search "Python" hoặc GET /courses/public
2. **User IDs**: Admin có thể GET /admin/users để lấy user IDs
3. **Lesson IDs**: GET course detail sẽ có embedded lessons với IDs
4. **Quiz IDs**: Từ lesson detail, trường `quiz_id` nếu lesson có quiz  
5. **Module IDs**: Từ course detail, embedded modules có IDs
6. **Class IDs**: Instructor có thể GET /classes sau khi tạo class
7. **Enrollment IDs**: GET /enrollments/my-courses sau khi enroll
8. **Assessment Session IDs**: Tạo mới bằng POST /assessments/generate

### 🔄 Reset Dữ Liệu
```bash
# Chạy lại script này để reset toàn bộ database
python -m scripts.init_data
```

### 🎯 Tips Test Hiệu Quả
1. **Test theo workflow**: Auth → Enroll → Learn → Quiz → Progress
2. **Sử dụng nhiều role**: Test với admin, instructor, student
3. **Kiểm tra permissions**: API chỉ accessible với đúng role
4. **Copy IDs từ response**: Lưu các UUIDs để test endpoints khác
5. **Test error cases**: Thử với token hết hạn, invalid IDs
6. **Verify data flow**: Đảm bảo progress update, enrollment tracking hoạt động

---

## 📝 QUY TRÌNH TEST HOÀN CHỈNH

1. **Khởi động**: Server + Init data
2. **Đăng nhập**: Admin/Instructor/Student  
3. **Test Authentication**: Register → Login → Profile
4. **Test Assessment**: Generate → Submit → Results → Recommendations
5. **Test Learning**: Search Course → Enroll → Learn → Progress → Quiz
6. **Test Personal**: Create Personal Course → Update → Track Progress
7. **Test AI Chat**: Create Conversation → Send Messages → History
8. **Test Admin**: Manage Users → Courses → Analytics (admin only)

**🎯 Kết quả mong đợi**: Tất cả API trả về đúng status code và data structure theo schema định nghĩa!