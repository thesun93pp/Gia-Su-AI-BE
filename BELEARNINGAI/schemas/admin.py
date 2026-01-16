"""
Admin Schemas
Định nghĩa request/response schemas cho admin endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class AdminUserListItem(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    avatar: Optional[str] = None
    role: str = Field(..., description="student|instructor|admin")
    status: str = Field(..., description="active|inactive|banned")
    created_at: datetime
    last_login_at: Optional[datetime] = None
    courses_enrolled: Optional[int] = Field(None, description="For student only")
    classes_created: Optional[int] = Field(None, description="For instructor only")


class UserSummary(BaseModel):
    total_users: int
    active_users: int
    new_users_this_month: int


class AdminUserListResponse(BaseModel):
    summary: Optional[str] = None
    data: List[AdminUserListItem]
    total: int
    skip: int
    limit: int
    


class UserStatistics(BaseModel):
    enrolled_courses: Optional[int] = None
    completed_courses: Optional[int] = None
    average_score: Optional[float] = Field(None, description="0-100 for student")
    classes_teaching: Optional[int] = None
    students_taught: Optional[int] = None
    quizzes_created: Optional[int] = None


class CurrentEnrollment(BaseModel):
    course_id: str = Field(..., description="UUID")
    course_title: str
    progress: float = Field(..., description="0-100")
    enrolled_at: datetime
    status: str = Field(..., description="in-progress|completed|cancelled")


class TeachingClass(BaseModel):
    class_id: str = Field(..., description="UUID")
    class_name: str
    course_title: str
    student_count: int
    created_at: datetime


class AdminUserDetailResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    role: str = Field(..., description="student|instructor|admin")
    status: str = Field(..., description="active|inactive")
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    statistics: UserStatistics
    current_enrollments: Optional[List[CurrentEnrollment]] = None
    teaching_classes: Optional[List[TeachingClass]] = None


class AdminCreateUserRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="Unique email")
    role: str = Field(..., description="student|instructor|admin")
    password: Optional[str] = Field(None, min_length=8, description="Required for instructor/admin")
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = None


class AdminCreateUserResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    role: str
    status: str = Field(..., description="active for instructor/admin, pending for student")
    created_at: datetime
    message: str


class AdminUpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[str] = Field(None, description="active|inactive")


class AdminUpdateUserResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    updated_at: datetime
    message: str


class AdminDeleteUserResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    message: str


class RoleChangeImpact(BaseModel):
    description: str
    affected_classes: Optional[int] = None
    affected_enrollments: Optional[int] = None


class AdminChangeRoleRequest(BaseModel):
    new_role: str = Field(..., description="student|instructor|admin")


class AdminChangeRoleResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    old_role: str
    new_role: str
    impact: RoleChangeImpact
    updated_at: datetime
    message: str


class AdminResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)


class AdminResetPasswordResponse(BaseModel):
    user_id: str = Field(..., description="UUID")
    message: str
    note: str


class UsersByRole(BaseModel):
    student: int
    instructor: int
    admin: int


class CoursesStats(BaseModel):
    published: int
    draft: int


class AdminDashboardResponse(BaseModel):
    total_users: int
    users_by_role: UsersByRole
    total_courses: int
    courses_stats: CoursesStats
    total_classes: int
    active_classes: int
    total_enrollments: int


# ============================================================================
# ADMIN COURSE MANAGEMENT SCHEMAS (Section 4.2)
# ============================================================================

class CourseAuthor(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    role: str = Field(..., description="admin|instructor|student")


class AdminCourseListItem(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    thumbnail_url: Optional[str] = None
    author: CourseAuthor
    course_type: str = Field(..., description="public|personal")
    enrollment_count: int
    status: str = Field(..., description="draft|published|archived")
    category: str
    level: str = Field(..., description="Beginner|Intermediate|Advanced")
    created_at: datetime
    updated_at: datetime


class AdminCourseListResponse(BaseModel):
    data: List[AdminCourseListItem]
    total: int
    skip: int
    limit: int
    has_next: bool


class ModuleSummary(BaseModel):
    module_id: str = Field(..., description="UUID")
    title: str
    order: int
    lesson_count: int
    estimated_hours: float


class CourseAnalytics(BaseModel):
    enrollment_count: int
    completion_rate: float = Field(..., description="0-100")
    avg_rating: Optional[float] = Field(None, description="0-5")
    total_students_active: int


class AdminCourseDetailResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    category: str
    level: str
    language: str
    status: str = Field(..., description="draft|published|archived")
    course_type: str = Field(..., description="public|personal")
    author: CourseAuthor
    modules: List[ModuleSummary]
    total_duration_minutes: int
    prerequisites: List[str]
    learning_outcomes: List[dict]
    analytics: CourseAnalytics
    created_at: datetime
    updated_at: datetime


class AdminCourseCreateRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    category: str
    level: str = Field(..., description="Beginner|Intermediate|Advanced")
    language: str = Field(default="vi")
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)
    learning_outcomes: List[dict] = Field(default_factory=list)
    status: str = Field(default="draft", description="draft|published")


class AdminCourseCreateResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    status: str
    course_type: str = Field(default="public")
    created_by: str = Field(..., description="Admin user_id")
    created_at: datetime
    message: str


class AdminCourseUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    category: Optional[str] = None
    level: Optional[str] = None
    language: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    prerequisites: Optional[List[str]] = None
    learning_outcomes: Optional[List[dict]] = None
    status: Optional[str] = Field(None, description="draft|published|archived")


class AdminCourseUpdateResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    status: str
    updated_at: datetime
    message: str


class CourseDeleteImpact(BaseModel):
    enrolled_students: int
    active_classes: int
    personal_courses_derived: int
    warning: str


class AdminDeleteCourseResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str
    impact: CourseDeleteImpact
    message: str


# ============================================================================
# ADMIN CLASSES SCHEMAS (Section 4.3.1-4.3.2)
# ============================================================================

class AdminClassListItem(BaseModel):
    """Schema cho danh sách lớp học trong admin panel"""
    class_id: str = Field(..., description="UUID lớp học")
    class_name: str = Field(..., description="Tên lớp học")
    instructor_name: str = Field(..., description="Tên giảng viên")
    instructor_email: str = Field(..., description="Email giảng viên")
    course_title: str = Field(..., description="Khóa học gốc")
    student_count: int = Field(..., description="Số học viên hiện tại")
    max_students: int = Field(..., description="Số học viên tối đa")
    status: str = Field(..., description="preparing|active|completed")
    start_date: datetime = Field(..., description="Thời gian bắt đầu")
    end_date: datetime = Field(..., description="Thời gian kết thúc")
    created_at: datetime = Field(..., description="Ngày tạo lớp")


class AdminClassListResponse(BaseModel):
    """Response cho GET /api/v1/admin/classes"""
    data: List[AdminClassListItem]
    total: int = Field(..., description="Tổng số lớp học")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
    has_next: bool = Field(..., description="Còn trang tiếp theo không")


class AdminClassStudentItem(BaseModel):
    """Schema cho học viên trong lớp (admin view)"""
    student_id: str = Field(..., description="UUID học viên")
    student_name: str = Field(..., description="Tên học viên")
    student_email: str = Field(..., description="Email học viên")
    avatar_url: Optional[str] = Field(None, description="URL avatar")
    progress: float = Field(..., description="Tiến độ học tập (0-100)")
    lessons_completed: int = Field(..., description="Số bài học đã hoàn thành")
    avg_quiz_score: float = Field(..., description="Điểm quiz trung bình (0-100)")
    last_activity: Optional[datetime] = Field(None, description="Lần hoạt động cuối")
    joined_at: datetime = Field(..., description="Ngày tham gia lớp")
    enrollment_status: str = Field(..., description="enrolled|completed|dropped")


class AdminClassStats(BaseModel):
    """Thống kê tổng quan lớp học"""
    total_students: int = Field(..., description="Tổng số học viên")
    active_students: int = Field(..., description="Số học viên còn hoạt động")
    avg_progress: float = Field(..., description="Tiến độ trung bình (0-100)")
    avg_quiz_score: float = Field(..., description="Điểm quiz trung bình (0-100)")
    completion_rate: float = Field(..., description="Tỷ lệ hoàn thành (0-100)")
    total_lessons: int = Field(..., description="Tổng số bài học trong khóa")
    total_quizzes: int = Field(..., description="Tổng số quiz")


class AdminClassInstructorInfo(BaseModel):
    """Thông tin giảng viên của lớp"""
    instructor_id: str = Field(..., description="UUID giảng viên")
    instructor_name: str = Field(..., description="Tên giảng viên")
    instructor_email: str = Field(..., description="Email giảng viên")
    instructor_avatar: Optional[str] = Field(None, description="Avatar giảng viên")
    bio: Optional[str] = Field(None, description="Tiểu sử giảng viên")
    total_classes: int = Field(..., description="Tổng số lớp đang dạy")
    total_students_taught: int = Field(..., description="Tổng số học viên đã dạy")


class AdminClassDetailResponse(BaseModel):
    """Response cho GET /api/v1/admin/classes/{class_id}"""
    class_id: str = Field(..., description="UUID lớp học")
    class_name: str = Field(..., description="Tên lớp học")
    description: str = Field(..., description="Mô tả lớp học")
    course_id: str = Field(..., description="UUID khóa học gốc")
    course_title: str = Field(..., description="Tên khóa học gốc")
    invite_code: str = Field(..., description="Mã mời tham gia")
    status: str = Field(..., description="preparing|active|completed")
    start_date: datetime = Field(..., description="Thời gian bắt đầu")
    end_date: datetime = Field(..., description="Thời gian kết thúc")
    max_students: int = Field(..., description="Số học viên tối đa")
    created_at: datetime = Field(..., description="Ngày tạo lớp")
    instructor_info: AdminClassInstructorInfo = Field(..., description="Thông tin giảng viên")
    students: List[AdminClassStudentItem] = Field(..., description="Danh sách học viên")
    stats: AdminClassStats = Field(..., description="Thống kê lớp học")
