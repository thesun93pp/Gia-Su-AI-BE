"""
Admin Schemas
Định nghĩa request/response schemas cho admin endpoints
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal


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


class ProfileInfo(BaseModel):
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    


class ActivitySummary(BaseModel):
    courses_enrolled: int
    classes_created: int
    total_study_hours: int
    login_streak_days: int


class AdminUserDetailResponse(BaseModel):
    """Response cho GET /api/v1/admin/users/{user_id}"""
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str    
    role: str = Field(..., description="student|instructor|admin")
    status: str = Field(..., description="active|inactive|banned")
    created_at: datetime
    last_login_at: Optional[datetime] = None
    profile: ProfileInfo
    activity_summary: ActivitySummary = Field(default_factory=ActivitySummary)
    


class AdminCreateUserRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="Unique email")
    role: str = Field(..., description="student|instructor|admin")
    password: str = Field(..., min_length=8, description="Password required for all roles")
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = None

class AdminCreateLessonResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    module_id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tiêu đề lesson")
    description: str = Field(..., description="Mô tả lesson")
    order: int
    content: str = Field(..., description="Nội dung lesson")
    content_type: str = Field(..., description="video|article|quiz|simulation|text|mixed")
    duration_minutes: int
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    resource: Optional[List['AdminResourceCreate']] = None
    learning_objectives: List[str] = Field(default_factory=list)
    simulation_html: Optional[str] = Field(None, description="Nội dung HTML của simulation/mô phỏng thực hành")
    quiz_id: Optional[str] = Field(None, description="UUID của quiz nếu content_type là quiz")
    is_published: bool = Field(..., description="Bài học đã được xuất bản hay chưa")
    message: str = Field(..., description="Thông báo tạo thành công")
    
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
    # full_name: str
    # email: str
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

class LearningOutcome(BaseModel):
    description: str = Field(..., min_length=5, max_length=500)
    skill_tag: Optional[str] = Field(None, description="Skill category: Problem Solving, Critical Thinking, etc.")

class AdminModuleCreateResponse(BaseModel):
    course_id: str = Field(..., description="UUID")
    title: str = Field(..., description="Tiêu đề module")
    description: str = Field(..., description="Mô tả module")
    order: int
    difficulty: str = Field(..., description="easy|medium|hard")
    estimated_hours: float
    learning_outcomes: List[dict] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    resource: Optional[List['AdminResourceCreate']] = None
    message: str = Field(..., description="Thông báo tạo thành công")



class AdminModuleCreateRequest(BaseModel):
    title: str = Field(..., description="Tiêu đề module")
    description: str = Field(..., description="Mô tả module")
    order: int
    difficulty: str = Field(..., description="easy|medium|hard")
    estimated_hours: float
    learning_outcomes: List[LearningOutcome] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    resource: Optional[List['AdminResourceCreate']] = None
    
    


class AdminLessonCreateRequest(BaseModel):
    title: str = Field(..., description="Tiêu đề bài học")
    description: str = Field(..., description="Mô tả bài học")
    order: int
    content: str = Field(..., description="Nội dung bài học")
    content_type: str = Field(..., description="video|article|quiz")
    duration_minutes: int
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    simulation_html: Optional[str] = Field(None, description="Nội dung HTML của simulation/mô phỏng thực hành")
    resource: Optional[List['AdminResourceCreate']] = None
    learning_objectives: List[str] = Field(default_factory=list)
    quiz_id: Optional[str] = Field(None, description="UUID của quiz nếu content_type là quiz")
    is_published: bool = Field(..., description="Bài học đã được xuất bản hay chưa")

class AdminResourceCreate(BaseModel):
    type: str = Field(..., description="pdf|link|video")
    title: str = Field(..., description="Tiêu đề tài liệu")
    description: Optional[str] = None
    url: Optional[str] = Field(None, description="URL tài liệu") 
    file_size_byte: Optional[float] = None
    is_dowloadable: bool = Field(..., description="Có thể tải về hay không")


class CourseAuthor(BaseModel):
    user_id: str = Field(..., description="UUID")
    full_name: str
    email: str
    role: str = Field(..., description="admin|instructor|student")


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
    learning_outcomes: List[LearningOutcome]
    analytics: CourseAnalytics
    created_at: datetime
    updated_at: datetime


class AdminCourseCreateRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=5, max_length=2000)
    category: str
    level: str = Field(..., description="Beginner|Intermediate|Advanced")
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    language: str = Field(default="vi", description="vi|en")
    status: str = Field(default="published", description="draft|published")
    learning_outcomes: List[LearningOutcome] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    
    
    


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
    learning_outcomes: List[LearningOutcome] = Field(default_factory=list)
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


class AdminCourseListItem(BaseModel):
    """Schema cho danh sách khóa học trong admin panel"""
    course_id: str = Field(..., description="UUID khóa học")
    title: str = Field(..., description="Tên khóa học")
    category: str = Field(..., description="Danh mục khóa học")
    level: str = Field(..., description="Beginner|Intermediate|Advanced")
    status: str = Field(..., description="draft|published|archived")
    course_type: str = Field(..., description="public|personal")
    created_by: str = Field(..., description="UUID người tạo")
    enrollment_count: int = Field(default=0, description="Số người đã đăng ký")
    created_at: datetime = Field(..., description="Ngày tạo")


class AdminCourseListResponse(BaseModel):
    """Response cho GET /api/v1/admin/courses"""
    data: List[AdminCourseListItem]
    total: int = Field(..., description="Tổng số khóa học")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")


# ============================================================================
# ADMIN CLASSES SCHEMAS (Section 4.3.1-4.3.2)
# ============================================================================

class AdminClassListItem(BaseModel):
    """Schema cho danh sách lớp học trong admin panel - API_SCHEMA Section 9.13"""
    class_id: str = Field(..., description="UUID lớp học")
    class_name: str = Field(..., description="Tên lớp học")
    course_title: str = Field(..., description="Khóa học gốc")
    instructor_name: str = Field(..., description="Tên giảng viên")
    student_count: int = Field(..., description="Số học viên hiện tại")
    status: str = Field(..., description="active|completed")
    created_at: datetime = Field(..., description="Ngày tạo lớp")


class AdminClassListResponse(BaseModel):
    """Response cho GET /api/v1/admin/classes"""
    data: List[AdminClassListItem]
    total: int = Field(..., description="Tổng số lớp học")
    skip: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")


class AdminCourseInfo(BaseModel):
    """Thông tin khóa học trong admin class detail"""
    course_id: str = Field(..., description="UUID khóa học")
    title: str = Field(..., description="Tên khóa học")
    category: str = Field(..., description="Danh mục khóa học")


class AdminInstructorInfo(BaseModel):
    """Thông tin giảng viên trong admin class detail"""
    user_id: str = Field(..., description="UUID giảng viên")
    full_name: str = Field(..., description="Tên giảng viên")
    email: str = Field(..., description="Email giảng viên")


class AdminClassStats(BaseModel):
    """Thống kê lớp học trong admin class detail"""
    average_progress: float = Field(..., description="Tiến độ trung bình (0-100)")
    completion_rate: float = Field(..., description="Tỷ lệ hoàn thành (0-100)")
    active_students_today: int = Field(..., description="Số học viên hoạt động hôm nay")


class AdminClassDetailResponse(BaseModel):
    """Response cho GET /api/v1/admin/classes/{class_id}"""
    class_id: str = Field(..., description="UUID lớp học")
    class_name: str = Field(..., description="Tên lớp học")
    course: AdminCourseInfo = Field(..., description="Thông tin khóa học")
    instructor: AdminInstructorInfo = Field(..., description="Thông tin giảng viên")
    student_count: int = Field(..., description="Số học viên hiện tại")
    invite_code: str = Field(..., description="Mã mời tham gia")
    status: str = Field(..., description="preparing|active|completed")
    class_stats: AdminClassStats = Field(..., description="Thống kê lớp học")
    created_at: datetime = Field(..., description="Ngày tạo lớp")
    start_date: datetime = Field(..., description="Thời gian bắt đầu")
    end_date: datetime = Field(..., description="Thời gian kết thúc")


