"""
User Service - Xử lý CRUD operations cho User
Sử dụng: Beanie ODM async methods, MongoDB
Tuân thủ: CHUCNANG.md Section 2.1, 4.1 (User Management)
"""

from datetime import datetime
from typing import Optional, List
from models.models import User
from services.auth_service import hash_password
from beanie import PydanticObjectId


# ============================================================================
# USER CREATION
# ============================================================================

async def create_user(
    email: str,
    password: str,
    full_name: str,
    role: str = "student"
) -> User:
    """
    Tạo user mới với password đã hash
    
    Args:
        email: Email của user (unique)
        password: Plain text password (sẽ được hash)
        full_name: Họ tên đầy đủ
        role: Role của user (student, instructor, admin)
        
    Returns:
        User document đã tạo
        
    Raises:
        ValueError: Nếu email đã tồn tại
    """
    # Kiểm tra email đã tồn tại chưa
    existing_user = await User.find_one(User.email == email)
    if existing_user:
        raise ValueError(f"Email {email} đã được sử dụng")
    
    # Hash password
    hashed_pwd = hash_password(password)
    
    # Tạo user mới
    user = User(
        email=email,
        hashed_password=hashed_pwd,
        full_name=full_name,
        role=role,
        status="active"
    )
    
    await user.insert()
    return user


# ============================================================================
# USER RETRIEVAL
# ============================================================================

async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Lấy user theo ID
    
    Args:
        user_id: ID của user
        
    Returns:
        User document hoặc None nếu không tìm thấy
    """
    try:
        user = await User.get(user_id)
        return user
    except Exception:
        return None


async def get_user_by_email(email: str) -> Optional[User]:
    """
    Lấy user theo email
    
    Args:
        email: Email của user
        
    Returns:
        User document hoặc None nếu không tìm thấy
    """
    user = await User.find_one(User.email == email)
    return user


async def get_users_list(
    role: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[User]:
    """
    Lấy danh sách users với filter và pagination
    
    Args:
        role: Filter theo role (student, instructor, admin)
        status: Filter theo status (active, inactive, suspended)
        skip: Số lượng records bỏ qua (pagination)
        limit: Số lượng records tối đa trả về
        
    Returns:
        List các User documents
    """
    query = User.find()
    
    if role:
        query = query.find(User.role == role)
    
    if status:
        query = query.find(User.status == status)
    
    users = await query.skip(skip).limit(limit).to_list()
    return users


async def count_users(
    role: Optional[str] = None,
    status: Optional[str] = None
) -> int:
    """
    Đếm số lượng users theo filter
    
    Args:
        role: Filter theo role
        status: Filter theo status
        
    Returns:
        Số lượng users
    """
    query = User.find()
    
    if role:
        query = query.find(User.role == role)
    
    if status:
        query = query.find(User.status == status)
    
    count = await query.count()
    return count


# ============================================================================
# USER UPDATE
# ============================================================================

async def update_user_profile(
    user_id: str,
    full_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    bio: Optional[str] = None,
    contact_info: Optional[str] = None,
    learning_preferences: Optional[List[str]] = None
) -> Optional[User]:
    """
    Cập nhật thông tin profile của user
    
    Args:
        user_id: ID của user
        full_name: Họ tên mới (optional)
        avatar_url: URL avatar mới (optional)
        bio: Bio mới (optional)
        contact_info: Thông tin liên hệ mới (optional)
        learning_preferences: Sở thích học tập mới (optional)
        
    Returns:
        User document đã update hoặc None nếu không tìm thấy
    """
    user = await get_user_by_id(user_id)
    
    if not user:
        return None
    
    # Cập nhật các fields được cung cấp
    if full_name is not None:
        user.full_name = full_name
    
    if avatar_url is not None:
        user.avatar_url = avatar_url
    
    if bio is not None:
        user.bio = bio
    
    if contact_info is not None:
        user.contact_info = contact_info
    
    if learning_preferences is not None:
        user.learning_preferences = learning_preferences
    
    # Cập nhật timestamp
    user.updated_at = datetime.utcnow()
    
    await user.save()
    return user


async def update_user_status(user_id: str, status: str) -> Optional[User]:
    """
    Cập nhật status của user (admin only)
    
    Args:
        user_id: ID của user
        status: Status mới (active, inactive, suspended)
        
    Returns:
        User document đã update hoặc None nếu không tìm thấy
    """
    user = await get_user_by_id(user_id)
    
    if not user:
        return None
    
    user.status = status
    user.updated_at = datetime.utcnow()
    
    await user.save()
    return user


async def change_user_password(user_id: str, new_password: str) -> Optional[User]:
    """
    Đổi password của user
    
    Args:
        user_id: ID của user
        new_password: Password mới (plain text, sẽ được hash)
        
    Returns:
        User document đã update hoặc None nếu không tìm thấy
    """
    user = await get_user_by_id(user_id)
    
    if not user:
        return None
    
    # Hash password mới
    user.hashed_password = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    
    await user.save()
    return user


# ============================================================================
# USER DELETION
# ============================================================================

async def delete_user(user_id: str) -> bool:
    """
    Xóa user khỏi database (hard delete)
    
    Args:
        user_id: ID của user
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    user = await get_user_by_id(user_id)
    
    if not user:
        return False
    
    await user.delete()
    return True


# ============================================================================
# SEARCH & FILTER
# ============================================================================

async def search_users_by_name(
    search_term: str,
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[User]:
    """
    Tìm kiếm users theo tên
    
    Args:
        search_term: Từ khóa tìm kiếm (tìm trong full_name)
        role: Filter theo role (optional)
        skip: Số lượng records bỏ qua
        limit: Số lượng records tối đa
        
    Returns:
        List các User documents matching search
    """
    query = User.find(User.full_name.regex(search_term, "i"))
    
    if role:
        query = query.find(User.role == role)
    
    users = await query.skip(skip).limit(limit).to_list()
    return users


async def get_instructors() -> List[User]:
    """
    Lấy tất cả instructors active
    
    Returns:
        List các User documents có role=instructor và status=active
    """
    instructors = await User.find(
        User.role == "instructor",
        User.status == "active"
    ).to_list()
    
    return instructors


async def get_students() -> List[User]:
    """
    Lấy tất cả students active
    
    Returns:
        List các User documents có role=student và status=active
    """
    students = await User.find(
        User.role == "student",
        User.status == "active"
    ).to_list()
    
    return students


# ============================================================================
# ADMIN USER MANAGEMENT (Section 4.1)
# ============================================================================

async def list_users_admin(
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    skip: int = 0,
    limit: int = 50
) -> dict:
    """
    4.1.1: Xem danh sách người dùng (Admin)
    
    Business logic:
    - List tất cả users với filter và search
    - Filter: role, status, created_at range
    - Search: tên hoặc email (autocomplete)
    - Sort: theo các cột
    - Pagination
    
    Args:
        role: Filter theo role (student|instructor|admin)
        status: Filter theo status (active|inactive)
        search: Search text (tên hoặc email)
        sort_by: Field sort
        sort_order: asc hoặc desc
        skip: Pagination skip
        limit: Pagination limit
        
    Returns:
        Dict với data, total, skip, limit, has_next
    """
    from models.models import Enrollment, Class
    
    # Build query
    query_conditions = []
    
    if role:
        query_conditions.append(User.role == role)
    
    if status:
        query_conditions.append(User.status == status)
    
    # Get users
    if query_conditions:
        query = User.find(*query_conditions)
    else:
        query = User.find()
    
    # Sort
    if sort_order == "desc":
        query = query.sort(f"-{sort_by}")
    else:
        query = query.sort(f"+{sort_by}")
    
    # Count total trước khi skip/limit
    total = await query.count()
    
    # Pagination
    users = await query.skip(skip).limit(limit).to_list()
    
    # Search filter sau query (nếu có)
    if search:
        search_lower = search.lower()
        users = [
            u for u in users
            if search_lower in u.full_name.lower() or search_lower in u.email.lower()
        ]
        total = len(users)
    
    # Build response với extra stats
    user_items = []
    
    for user in users:
        item = {
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "avatar": user.avatar_url,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at
        }
        
        # Add role-specific stats
        if user.role == "student":
            enrollment_count = await Enrollment.find(
                Enrollment.user_id == str(user.id)
            ).count()
            item["enrollment_count"] = enrollment_count
        elif user.role == "instructor":
            class_count = await Class.find(
                Class.instructor_id == str(user.id)
            ).count()
            item["class_count"] = class_count
        
        user_items.append(item)
    
    has_next = (skip + limit) < total
    
    return {
        "data": user_items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": has_next
    }


async def get_user_detail_admin(user_id: str) -> dict:
    """
    4.1.2: Xem hồ sơ người dùng chi tiết (Admin)
    
    Business logic:
    - Xem thông tin đầy đủ của user
    - Thống kê: courses/classes, điểm TB
    - Current enrollments hoặc teaching classes
    
    Args:
        user_id: ID của user
        
    Returns:
        Dict với user info, statistics, current activities
        
    Raises:
        Exception: Nếu user không tồn tại
    """
    from models.models import Enrollment, Class, QuizAttempt, Course
    
    user = await get_user_by_id(user_id)
    
    if not user:
        raise Exception("User không tồn tại")
    
    # Build statistics based on role
    statistics = {}
    
    if user.role == "student":
        # Student stats
        enrollments = await Enrollment.find(
            Enrollment.user_id == user_id
        ).to_list()
        
        enrolled_count = len(enrollments)
        completed_count = sum(1 for e in enrollments if e.status == "completed")
        
        # Calculate avg quiz score
        quiz_attempts = await QuizAttempt.find(
            QuizAttempt.user_id == user_id,
            QuizAttempt.submitted_at != None
        ).to_list()
        
        avg_score = sum(a.score for a in quiz_attempts) / len(quiz_attempts) if quiz_attempts else 0
        
        statistics = {
            "enrolled_courses": enrolled_count,
            "completed_courses": completed_count,
            "average_score": round(avg_score, 2)
        }
        
        # Get current enrollments
        current_enrollments = []
        for enrollment in enrollments:
            if enrollment.status in ["active", "in-progress"]:
                course = await Course.get(enrollment.course_id)
                if course:
                    current_enrollments.append({
                        "course_id": enrollment.course_id,
                        "course_title": course.title,
                        "progress": enrollment.progress_percent,
                        "enrolled_at": enrollment.enrolled_at,
                        "status": enrollment.status
                    })
        
        return {
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "avatar": user.avatar_url,
            "bio": user.bio,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at if user.last_login_at else None,
            "statistics": statistics,
            "current_enrollments": current_enrollments
        }
    
    elif user.role == "instructor":
        # Instructor stats
        classes = await Class.find(
            Class.instructor_id == user_id
        ).to_list()
        
        # Count total students across all classes
        total_students = 0
        for cls in classes:
            enrollments = await Enrollment.find(
                Enrollment.course_id == cls.course_id,
                Enrollment.status == "active"
            ).count()
            total_students += enrollments
        
        from models.models import Quiz
        quizzes_created = await Quiz.find(
            Quiz.created_by == user_id
        ).count()
        
        statistics = {
            "classes_teaching": len(classes),
            "students_taught": total_students,
            "quizzes_created": quizzes_created
        }
        
        # Get teaching classes
        teaching_classes = []
        for cls in classes:
            course = await Course.get(cls.course_id) if cls.course_id else None
            student_count = await Enrollment.find(
                Enrollment.course_id == cls.course_id,
                Enrollment.status == "active"
            ).count()
            
            teaching_classes.append({
                "class_id": str(cls.id),
                "class_name": cls.name,
                "course_title": course.title if course else "N/A",
                "student_count": student_count,
                "created_at": cls.created_at
            })
        
        return {
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "avatar": user.avatar_url,
            "bio": user.bio,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at if user.last_login_at else None,
            "statistics": statistics,
            "teaching_classes": teaching_classes
        }
    
    else:
        # Admin - minimal stats
        return {
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "avatar": user.avatar_url,
            "bio": user.bio,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at if user.last_login_at else None,
            "statistics": {}
        }


async def create_user_admin(
    full_name: str,
    email: str,
    role: str,
    password: Optional[str] = None,
    bio: Optional[str] = None,
    avatar: Optional[str] = None
) -> dict:
    """
    4.1.3: Tạo tài khoản người dùng (Admin)
    
    Business logic:
    - Admin tạo trực tiếp user
    - Nếu Student: status=pending (admin manually activate later)
    - Nếu Instructor/Admin: nhập password (status=active)
    
    Args:
        full_name: Tên đầy đủ
        email: Email (unique)
        role: student|instructor|admin
        password: Required cho instructor/admin
        bio: Bio (optional)
        avatar: Avatar URL (optional)
        
    Returns:
        Dict với user_id, status, message
        
    Raises:
        Exception: Nếu email đã tồn tại hoặc validation failed
    """
    # Check email exists
    existing = await get_user_by_email(email)
    if existing:
        raise Exception(f"Email {email} đã được sử dụng")
    
    # Validate password cho instructor/admin
    if role in ["instructor", "admin"] and not password:
        raise Exception(f"Password là bắt buộc khi tạo tài khoản {role}")
    
    # Create user
    if role == "student":
        # Student: status=pending, admin will manually activate
        import secrets
        temp_password = secrets.token_urlsafe(12)
        hashed_pwd = hash_password(temp_password)
        
        user = User(
            full_name=full_name,
            email=email,
            hashed_password=hashed_pwd,
            role=role,
            status="pending",  # Admin manually activate later
            bio=bio,
            avatar_url=avatar
        )
        await user.insert()
        
        return {
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at,
            "message": "Tài khoản student đã được tạo với status pending. Admin cần manually activate."
        }
    
    else:
        # Instructor/Admin: status=active
        hashed_pwd = hash_password(password)
        
        user = User(
            full_name=full_name,
            email=email,
            hashed_password=hashed_pwd,
            role=role,
            status="active",
            bio=bio,
            avatar_url=avatar
        )
        await user.insert()
        
        return {
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at,
            "message": f"Tài khoản {role} đã được tạo thành công."
        }


async def update_user_admin(
    user_id: str,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    bio: Optional[str] = None,
    avatar: Optional[str] = None,
    status: Optional[str] = None
) -> dict:
    """
    4.1.4: Cập nhật thông tin người dùng (Admin)
    
    Business logic:
    - Admin có thể update bất kỳ field nào
    - Validate email không trùng
    - Frontend preview trước khi submit
    
    Args:
        user_id: ID của user
        full_name, email, bio, avatar, status: Fields cần update
        
    Returns:
        Dict với user_id, updated fields, message
        
    Raises:
        Exception: Nếu user không tồn tại hoặc email trùng
    """
    user = await get_user_by_id(user_id)
    
    if not user:
        raise Exception("User không tồn tại")
    
    # Check email uniqueness if changing
    if email and email != user.email:
        existing = await get_user_by_email(email)
        if existing:
            raise Exception(f"Email {email} đã được sử dụng bởi user khác")
    
    # Update fields
    if full_name:
        user.full_name = full_name
    
    if email:
        user.email = email
    
    if bio is not None:
        user.bio = bio
    
    if avatar is not None:
        user.avatar_url = avatar
    
    if status:
        user.status = status
    
    user.updated_at = datetime.utcnow()
    await user.save()
    
    return {
        "user_id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "updated_at": user.updated_at,
        "message": "Thông tin user đã được cập nhật thành công"
    }


async def delete_user_admin(user_id: str) -> dict:
    """
    4.1.5: Xóa người dùng (Admin)
    
    Business logic:
    - Kiểm tra dependencies:
      * Instructor: có lớp đang dạy không?
      * Student: có enrollment active không?
      * Có personal courses không?
    - Cảnh báo impact trước khi xóa
    - Xóa vĩnh viễn (không thể khôi phục)
    
    Args:
        user_id: ID của user
        
    Returns:
        Dict với user_id, message
        
    Raises:
        Exception: Nếu có dependencies blocking deletion
    """
    from models.models import Enrollment, Class, Course
    
    user = await get_user_by_id(user_id)
    
    if not user:
        raise Exception("User không tồn tại")
    
    # Check dependencies
    if user.role == "instructor":
        # Check active classes
        active_classes = await Class.find(
            Class.instructor_id == user_id,
            Class.status == "active"
        ).count()
        
        if active_classes > 0:
            raise Exception(
                f"Không thể xóa instructor: Đang dạy {active_classes} lớp học active. "
                "Vui lòng chuyển lớp cho instructor khác hoặc hoàn thành lớp trước."
            )
    
    elif user.role == "student":
        # Check active enrollments
        active_enrollments = await Enrollment.find(
            Enrollment.user_id == user_id,
            Enrollment.status == "active"
        ).count()
        
        if active_enrollments > 0:
            raise Exception(
                f"Không thể xóa student: Đang tham gia {active_enrollments} khóa học. "
                "Vui lòng hủy đăng ký trước."
            )
    
    # Check personal courses
    personal_courses = await Course.find(
        Course.owner_id == user_id,
        Course.owner_type != "admin"
    ).count()
    
    if personal_courses > 0:
        raise Exception(
            f"Không thể xóa user: Có {personal_courses} khóa học cá nhân. "
            "Vui lòng xóa khóa học trước."
        )
    
    # Delete user
    await user.delete()
    
    return {
        "user_id": str(user_id),
        "message": "User đã được xóa vĩnh viễn khỏi hệ thống"
    }


async def change_user_role_admin(user_id: str, new_role: str) -> dict:
    """
    4.1.6: Thay đổi vai trò người dùng (Admin)
    
    Business logic:
    - Student ↔ Instructor ↔ Admin
    - Kiểm tra impact:
      * Hạ Instructor → Student: ảnh hưởng lớp học
      * Nâng Student → Instructor: OK
    - Cảnh báo chi tiết về impact
    
    Args:
        user_id: ID của user
        new_role: student|instructor|admin
        
    Returns:
        Dict với user_id, old_role, new_role, impact, message
        
    Raises:
        Exception: Nếu có blocking dependencies
    """
    from models.models import Class, Enrollment
    
    user = await get_user_by_id(user_id)
    
    if not user:
        raise Exception("User không tồn tại")
    
    old_role = user.role
    
    if old_role == new_role:
        raise Exception(f"User đã có role {new_role}")
    
    # Check impact
    impact = {
        "description": f"Thay đổi role từ {old_role} thành {new_role}",
        "affected_classes": None,
        "affected_enrollments": None
    }
    
    if old_role == "instructor" and new_role == "student":
        # Hạ Instructor → Student: check classes
        active_classes = await Class.find(
            Class.instructor_id == user_id,
            Class.status == "active"
        ).count()
        
        if active_classes > 0:
            raise Exception(
                f"Không thể hạ instructor xuống student: Đang dạy {active_classes} lớp active. "
                "Vui lòng chuyển lớp cho instructor khác trước."
            )
        
        # Count all classes (including completed)
        total_classes = await Class.find(
            Class.instructor_id == user_id
        ).count()
        
        impact["affected_classes"] = total_classes
        impact["description"] += f". {total_classes} lớp đã dạy sẽ vẫn giữ nguyên."
    
    elif old_role == "student" and new_role == "instructor":
        # Nâng Student → Instructor: OK, giữ enrollments
        enrollments = await Enrollment.find(
            Enrollment.user_id == user_id
        ).count()
        
        impact["affected_enrollments"] = enrollments
        impact["description"] += f". {enrollments} enrollment sẽ vẫn được giữ."
    
    # Change role
    user.role = new_role
    user.updated_at = datetime.utcnow()
    await user.save()
    
    return {
        "user_id": str(user.id),
        "old_role": old_role,
        "new_role": new_role,
        "impact": impact,
        "updated_at": user.updated_at,
        "message": f"Role đã được thay đổi từ {old_role} thành {new_role} thành công"
    }


async def reset_user_password_admin(user_id: str, new_password: str) -> dict:
    """
    4.1.7: Reset mật khẩu người dùng (Admin)
    
    Business logic:
    - Force reset password
    - Admin gửi password mới qua kênh khác (không qua hệ thống)
    - Use cases: quên password, tài khoản bị khóa
    
    Args:
        user_id: ID của user
        new_password: Password mới (plain text, sẽ hash)
        
    Returns:
        Dict với user_id, message, note
        
    Raises:
        Exception: Nếu user không tồn tại
    """
    user = await change_user_password(user_id, new_password)
    
    if not user:
        raise Exception("User không tồn tại")
    
    return {
        "user_id": str(user.id),
        "message": "Mật khẩu đã được reset thành công",
        "note": "Admin vui lòng gửi mật khẩu mới cho user qua email/điện thoại riêng"
    }

