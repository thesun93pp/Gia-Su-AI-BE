"""
Admin Controller
Xử lý requests cho admin management endpoints
Section 4.1-4.3
"""

from typing import Dict, Optional
from fastapi import HTTPException, status

from schemas.admin import (
    AdminUserListResponse,
    AdminUserDetailResponse,
    AdminCreateUserRequest,
    AdminCreateUserResponse,
    AdminUpdateUserRequest,
    AdminUpdateUserResponse,
    AdminDeleteUserResponse,
    AdminChangeRoleRequest,
    AdminChangeRoleResponse,
    AdminResetPasswordRequest,
    AdminResetPasswordResponse,
    
    AdminCourseDetailResponse,
    AdminCourseCreateRequest,
    AdminCourseCreateResponse,
    AdminCourseUpdateRequest,
    AdminCourseUpdateResponse,
    AdminDeleteCourseResponse,

    AdminModuleCreateRequest,
    AdminModuleCreateResponse,
    AdminLessonCreateRequest,
    AdminCreateLessonResponse,
    AdminClassListResponse,
    AdminClassDetailResponse,
    AdminCourseListResponse
)
from services import admin_service, course_service


# ============================================================================
# Section 4.1: QUẢN LÝ NGƯỜI DÙNG
# ============================================================================

async def handle_list_users_admin(
    role: Optional[str] = None,
    status_filter: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    created_from: Optional[str] = None,
    created_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: Dict = None
) -> AdminUserListResponse:
    """
    4.1.1: Xem danh sách người dùng với filter, search, sort
    
    Flow:
    1. Validate admin permission
    2. Gọi admin_service.get_users_list với filters
    3. Return paginated list với autocomplete search
    
    Args:
        role: Lọc theo vai trò (student|instructor|admin)
        status_filter: Lọc theo trạng thái (active|inactive)
        keyword: Tìm kiếm theo tên hoặc email
        sort_by: Sắp xếp theo cột (full_name|email|created_at|role)
        sort_order: Thứ tự (asc|desc)
        created_from: Lọc từ ngày tạo (ISO 8601)
        created_to: Lọc đến ngày tạo (ISO 8601)
        skip: Pagination offset
        limit: Pagination limit (max 100)
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminUserListResponse với data, total, pagination info
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 400: Invalid filter parameters
        HTTPException 500: Lỗi server
    """
    try:
        # Validate admin role
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem danh sách người dùng"
            )
        
        # Validate limit
        if limit > 100:
            limit = 100
            
        # Convert skip to page for admin service
        page = (skip // limit) + 1 if limit > 0 else 1
            
        users_data = await admin_service.get_users_list_admin(
            page=page,
            limit=limit,
            search=keyword,
            role_filter=role,
            status_filter=status_filter,
            sort_by=sort_by,
            sort_order=sort_order,
            created_from=created_from,
            created_to=created_to
        )
        
        return AdminUserListResponse(**users_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách người dùng: {str(e)}"
        )


async def handle_get_user_detail_admin(
    user_id: str,
    current_user: Dict
) -> AdminUserDetailResponse:
    """
    4.1.2: Xem hồ sơ người dùng chi tiết
    
    Flow:
    1. Validate admin permission
    2. Gọi admin_service.get_user_detail với user_id
    3. Return thông tin đầy đủ với statistics
    
    Args:
        user_id: UUID của người dùng cần xem
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminUserDetailResponse với thông tin chi tiết
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem chi tiết người dùng"
            )
        
        user_detail = await admin_service.get_user_detail_admin(user_id)
        return AdminUserDetailResponse(**user_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy chi tiết người dùng: {str(e)}"
        )


async def handle_create_user_admin(
    user_data: AdminCreateUserRequest,
    current_user: Dict
) -> AdminCreateUserResponse:
    """
    4.1.3: Tạo tài khoản người dùng mới
    
    Flow:
    1. Validate admin permission
    2. Validate email unique
    3. Gọi admin_service.create_user
    
    Args:
        user_data: Thông tin tạo user mới
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCreateUserResponse với thông tin user mới tạo
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 400: Email đã tồn tại hoặc validation error
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền tạo tài khoản"
            )
        
        created_user = await admin_service.create_user_admin(user_data.dict())
        return AdminCreateUserResponse(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo tài khoản: {str(e)}"
        )


async def handle_update_user_admin(
    user_id: str,
    user_data: AdminUpdateUserRequest,
    current_user: Dict
) -> AdminUpdateUserResponse:
    """
    4.1.4: Cập nhật thông tin người dùng
    
    Flow:
    1. Validate admin permission
    2. Validate email unique (nếu thay đổi)
    3. Gọi admin_service.update_user
    4. Return updated info
    
    Args:
        user_id: UUID của người dùng cần cập nhật
        user_data: Dữ liệu cập nhật (partial)
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminUpdateUserResponse với thông tin đã cập nhật
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 400: Email đã tồn tại
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền cập nhật thông tin người dùng"
            )
        
        updated_user = await admin_service.update_user_admin(user_id, user_data.dict(exclude_unset=True))
        return AdminUpdateUserResponse(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật thông tin: {str(e)}"
        )


async def handle_delete_user_admin(
    user_id: str,
    current_user: Dict
) -> AdminDeleteUserResponse:
    """
    4.1.5: Xóa người dùng vĩnh viễn
    
    Flow:
    1. Validate admin permission
    2. Kiểm tra dependencies (classes, enrollments, courses)
    3. Gọi admin_service.delete_user nếu không có dependencies
    4. Return confirmation
    
    Args:
        user_id: UUID của người dùng cần xóa
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminDeleteUserResponse với confirmation
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 400: Không thể xóa do có dependencies
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xóa người dùng"
            )
        
        deleted_info = await admin_service.delete_user_admin(user_id)
        return AdminDeleteUserResponse(**deleted_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa người dùng: {str(e)}"
        )


async def handle_change_user_role_admin(
    user_id: str,
    role_data: AdminChangeRoleRequest,
    current_user: Dict
) -> AdminChangeRoleResponse:
    """
    4.1.6: Thay đổi vai trò người dùng
    
    Flow:
    1. Validate admin permission
    2. Kiểm tra impact của việc thay đổi role
    3. Gọi admin_service.change_user_role
    4. Return impact analysis và confirmation
    
    Args:
        user_id: UUID của người dùng cần thay đổi role
        role_data: Vai trò mới
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminChangeRoleResponse với old/new role và impact
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 400: Không thể thay đổi role do ràng buộc
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền thay đổi vai trò"
            )
        
        role_change_result = await admin_service.change_user_role_admin(user_id, role_data.new_role)
        return AdminChangeRoleResponse(**role_change_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thay đổi vai trò: {str(e)}"
        )


async def handle_reset_user_password_admin(
    user_id: str,
    password_data: AdminResetPasswordRequest,
    current_user: Dict
) -> AdminResetPasswordResponse:
    """
    4.1.7: Reset mật khẩu người dùng
    
    Flow:
    1. Validate admin permission
    2. Validate password strength
    3. Gọi admin_service.reset_user_password
    4. Return confirmation
    
    Args:
        user_id: UUID của người dùng cần reset password
        password_data: Mật khẩu mới
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminResetPasswordResponse với confirmation
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy user
        HTTPException 400: Mật khẩu không hợp lệ
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền reset mật khẩu"
            )
        
        reset_result = await admin_service.reset_user_password_admin(user_id, password_data.new_password)
        return AdminResetPasswordResponse(**reset_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi reset mật khẩu: {str(e)}"
        )


# ============================================================================
# Section 4.2: QUẢN LÝ KHÓA HỌC (Admin Course Management)
# ============================================================================

async def handle_get_course_detail_admin(
    course_id: str,
    current_user: Dict
) -> AdminCourseDetailResponse:
    """
    4.2.2: Xem chi tiết khóa học với preview capability
    
    Args:
        course_id: UUID khóa học
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCourseDetailResponse với thông tin đầy đủ
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem chi tiết khóa học"
            )
        
        from services import course_service
        course_detail = await course_service.get_course_detail(course_id, current_user.get("user_id"))
        return AdminCourseDetailResponse(**course_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy chi tiết khóa học: {str(e)}"
        )


async def handle_create_course_admin(
    course_data: AdminCourseCreateRequest,
    current_user: Dict
) -> AdminCourseCreateResponse:
    """

    4.2.3: Tạo khóa học chính thức (public course)

    Args:
        course_data: Dữ liệu khóa học mới
        current_user: Dict chứa thông tin admin từ JWT

    Returns:
        AdminCourseCreateResponse với thông tin khóa học mới
    """
    try:
        # Validate admin
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create courses"
            )
        
        # ✅ Convert learning_outcomes objects to list of dicts
        learning_outcomes_data = []
        if course_data.learning_outcomes:
            for outcome in course_data.learning_outcomes:
                if hasattr(outcome, 'dict'):
                    learning_outcomes_data.append(outcome.dict())
                elif isinstance(outcome, dict):
                    learning_outcomes_data.append(outcome)
                else:
                    learning_outcomes_data.append({'text': str(outcome)})
        
        # Tạo khóa học
        result = await course_service.create_course_admin(
            admin_id=current_user.get("user_id"),
            title=course_data.title,
            description=course_data.description,
            category=course_data.category,
            level=course_data.level,
            language=course_data.language,  # ✅ Add language            
            thumbnail_url=course_data.thumbnail_url,
            preview_video_url=course_data.preview_video_url,
            prerequisites=course_data.prerequisites,
            learning_outcomes=course_data.learning_outcomes,
            status=course_data.status
        )
        return AdminCourseCreateResponse(**created_course)

               
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in handle_create_course_admin: {str(e)}")  # Log to terminal
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           

            detail=f"Lỗi khi tạo khóa học: {str(e)}"
        )


async def handle_update_course_admin(
    course_id: str,
    course_data: AdminCourseUpdateRequest,
    current_user: Dict
) -> AdminCourseUpdateResponse:
    """
    4.2.4: Chỉnh sửa bất kỳ khóa học nào (kể cả personal)
    
    Args:
        course_id: UUID khóa học cần cập nhật
        course_data: Dữ liệu cập nhật
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCourseUpdateResponse với thông tin đã cập nhật
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền chỉnh sửa khóa học"
            )
        
        update_data = course_data.dict(exclude_unset=True)

        updated_course = await admin_service.update_course_admin(course_id, update_data)

        updated_course = await admin_service.update_course_admin(course_id, course_data.dict(exclude_unset=True))
        return AdminCourseUpdateResponse(**updated_course)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật khóa học: {str(e)}"
        )


async def handle_delete_course_admin(
    course_id: str,
    current_user: Dict
) -> AdminDeleteCourseResponse:
    """
    4.2.5: Xóa khóa học với impact analysis
    
    Args:
        course_id: UUID khóa học cần xóa
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminDeleteCourseResponse với impact analysis
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xóa khóa học"
            )
        
        delete_result = await admin_service.delete_course_admin(course_id)
        return AdminDeleteCourseResponse(**delete_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa khóa học: {str(e)}"
        )

async def handle_create_module_admin(
    course_id: str,
    module_data: AdminModuleCreateRequest,
    current_user: Dict
) -> AdminModuleCreateResponse:
    """
    4.2.6: Create a new module in a course (Admin)
    
    Args:
        course_id: ID of the course
        module_data: New module information
        current_user: Admin user
        
    Returns:
        AdminModuleCreateResponse
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create modules"
            )
        
        learning_outcomes_data = [outcome.dict() for outcome in module_data.learning_outcomes] if module_data.learning_outcomes else []
        resource_data = [res.dict() for res in module_data.resource] if module_data.resource else []
        
        course = await course_service.add_module_to_course(
            course_id=course_id,
            title=module_data.title,
            description=module_data.description,
            order=module_data.order,
            difficulty=module_data.difficulty,
            estimated_hours=module_data.estimated_hours,
            learning_outcomes=learning_outcomes_data,
            prerequisites=module_data.prerequisites,
            resource=resource_data
        )
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID '{course_id}' not found. Cannot create module."
            )
            
        new_module = course.modules[-1]
        
        return AdminModuleCreateResponse(
            module_id=new_module.id,
            course_id=course_id,
            title=new_module.title,
            description=new_module.description,
            order=new_module.order,
            difficulty=new_module.difficulty,
            estimated_hours=new_module.estimated_hours,
            learning_outcomes=new_module.learning_outcomes,
            prerequisites=new_module.prerequisites,
            resource=new_module.resources,
            message=f"Module '{new_module.title}' created successfully in course '{course.title}'."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def handle_create_lesson_admin(
    course_id: str,
    module_id: str,
    lesson_data: AdminLessonCreateRequest,
    current_user: Dict
) -> AdminCreateLessonResponse:
    """
    Creates a new lesson in a module for a given course.
    
    Args:
        course_id: The ID of the course.
        module_id: The ID of the module.
        lesson_data: The lesson data.
        current_user: The current admin user.
        
    Returns:
        The created lesson data.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create lessons"
        )

    new_lesson_data = await course_service.add_lesson_to_module(
        course_id=course_id,
        module_id=module_id,
        lesson_data=lesson_data
    )

    if not new_lesson_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create lesson. The provided course or module may not exist, or the lesson data may be invalid."
        )

    return AdminCreateLessonResponse(
        **new_lesson_data,
        message=f"Lesson '{new_lesson_data['title']}' created successfully."
    )


async def handle_list_courses_admin(
    status: Optional[str] = None,
    creator_id: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 20,
    current_user: Dict = None
) -> AdminCourseListResponse:
    """
    4.2.1: Xem danh sách khóa học (tất cả - public + personal)
    
    Flow:
    1. Validate admin permission
    2. Gọi admin_service.get_courses_list_admin với filters
    3. Return paginated list
    
    Args:
        status: Lọc theo trạng thái (active|draft|archived)
        creator_id: Lọc theo người tạo (UUID)
        category: Lọc theo danh mục
        sort_by: Sắp xếp (created_at|enrollment_count|title)
        order: Thứ tự (asc|desc)
        skip: Pagination offset
        limit: Pagination limit (max 100)
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminCourseListResponse với data, total, pagination info
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 400: Invalid parameters
        HTTPException 500: Lỗi server
    """
    try:
        # ✅ Validate admin role
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem danh sách khóa học"
            )
        
        # ✅ Validate limit
        if limit > 100:
            limit = 100
        
        if limit < 1:
            limit = 20
        
        # ✅ Validate sort_by
        valid_sort_fields = ["created_at", "enrollment_count", "title"]
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"
        
        # ✅ Validate order
        if order not in ["asc", "desc"]:
            order = "desc"
        
        # ✅ Call service
        courses_data = await admin_service.get_courses_list_admin(
            status=status,
            creator_id=creator_id,
            category=category,
            sort_by=sort_by,
            order=order,
            skip=skip,
            limit=limit
        )
        
        # ✅ Return response
        return AdminCourseListResponse(
            data=courses_data.get('data', []),
            total=courses_data.get('total', 0),
            skip=courses_data.get('skip', skip),
            limit=courses_data.get('limit', limit)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách khóa học: {str(e)}"
        )


# ============================================================================
# Section 4.3: GIÁM SÁT LỚP HỌC
# ============================================================================

async def handle_list_classes_admin(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    instructor_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: Dict = None
) -> AdminClassListResponse:
    """
    4.3.1: Xem tất cả lớp học từ mọi giảng viên
    
    Flow:
    1. Validate admin permission
    2. Gọi admin_service.get_classes_list với filters
    3. Return thông tin lớp học với instructor và course info
    
    Args:
        instructor_id: Lọc theo giảng viên (UUID)
        course_id: Lọc theo khóa học gốc (UUID)
        status: Lọc theo trạng thái (preparing|active|completed)
        skip: Pagination offset
        limit: Pagination limit
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminClassListResponse với danh sách lớp học
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem tất cả lớp học"
            )
        
        classes_data = await admin_service.get_classes_list_admin(
            page=page,
            limit=limit,
            search=search,
            instructor_filter=instructor_filter,
            status_filter=status_filter,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return AdminClassListResponse(**classes_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách lớp học: {str(e)}"
        )


async def handle_get_class_detail_admin(
    class_id: str,
    current_user: Dict
) -> AdminClassDetailResponse:
    """
    4.3.2: Xem chi tiết lớp học (bất kỳ lớp nào)
    
    Flow:
    1. Validate admin permission
    2. Gọi admin_service.get_class_detail với class_id
    3. Return thông tin đầy đủ về lớp, instructor, students và stats
    
    Args:
        class_id: UUID lớp học cần xem
        current_user: Dict chứa thông tin admin từ JWT
        
    Returns:
        AdminClassDetailResponse với thông tin chi tiết
        
    Raises:
        HTTPException 403: Không phải admin
        HTTPException 404: Không tìm thấy lớp học
        HTTPException 500: Lỗi server
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ admin mới có quyền xem chi tiết lớp học"
            )
        
        class_detail = await admin_service.get_class_detail_admin(class_id)
        return AdminClassDetailResponse(**class_detail)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy chi tiết lớp học: {str(e)}"
        )