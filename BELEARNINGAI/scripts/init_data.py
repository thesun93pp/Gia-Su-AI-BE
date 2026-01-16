"""
Script để khởi tạo dữ liệu mẫu cho toàn bộ hệ thống AI Learning Platform.
Tuân thủ 100% theo API_SCHEMA.md và models.py.
Dữ liệu được sinh ra có tính logic, thực tế và đa dạng.
"""
import asyncio
<<<<<<< HEAD
=======
import json
>>>>>>> origin/tasks/uploadImg
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from beanie import init_beanie, PydanticObjectId
from beanie.operators import In, NE, Eq, Set
from motor.motor_asyncio import AsyncIOMotorClient
from faker import Faker
import random

# Thêm đường dẫn gốc của dự án vào sys.path
import sys
<<<<<<< HEAD
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
=======
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
>>>>>>> origin/tasks/uploadImg


from config.config import get_settings
from models.models import (
    User,
    Course,
<<<<<<< HEAD
=======
    EmbeddedModule,
    EmbeddedLesson,
>>>>>>> origin/tasks/uploadImg
    Module,
    Lesson,
    Enrollment,
    AssessmentSession,
    Quiz,
    QuizAttempt,
    Progress,
<<<<<<< HEAD
=======
    LessonProgressItem,
>>>>>>> origin/tasks/uploadImg
    Conversation,
    Class,
    Recommendation,
    PasswordResetTokenDocument,
    RefreshToken
)
from utils.security import hash_password

# Khởi tạo Faker để sinh dữ liệu giả
fake = Faker('vi_VN')

async def init_db():
    """Khởi tạo kết nối database và Beanie."""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=client[settings.mongodb_database],
        document_models=[
            User,
            RefreshToken,
            PasswordResetTokenDocument,
            Course,
            Module,
            Lesson,
            Enrollment,
            Progress,
            AssessmentSession,
            Quiz,
            QuizAttempt,
            Class,
            Conversation,
            Recommendation,
        ]
    )
    print("🗑️ Đã xóa các collection cũ...")
    for collection in await client[settings.mongodb_database].list_collection_names():
        await client[settings.mongodb_database][collection].delete_many({})
    print("✅ Xóa dữ liệu cũ thành công.")


async def seed_users() -> Dict[str, List[str]]:
    """
    Tạo dữ liệu mẫu cho người dùng (User).
    - 1 Admin
    - 3 Giảng viên (Instructor)
    - 10 Học viên (Student)
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Users ---")
    
    users_to_create = []
    user_ids = {"admin": [], "instructor": [], "student": []}

    # 1. Tạo Admin
    admin_email = "admin.super@ailab.com.vn"
    admin_user = User(
        full_name="Quản Trị Viên Hệ Thống",
        email=admin_email,
        hashed_password=hash_password("Admin@12345"),
        role="admin",
        status="active",
        email_verified=True,
        bio="Quản trị viên cấp cao, chịu trách nhiệm vận hành hệ thống.",
        learning_preferences=["Programming", "Data Science"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    users_to_create.append(admin_user)
    print(f"👤 Đã chuẩn bị Admin: {admin_user.full_name} ({admin_user.email})")

    # 2. Tạo Giảng viên
    instructors_data = [
        {"full_name": "Nguyễn Ngọc Tuấn Anh", "email": "tuananh.nguyen@ailab.edu.vn", "bio": "Chuyên gia về AI và Machine Learning với 10 năm kinh nghiệm.", "prefs": ["Data Science", "AI Development"]},
        {"full_name": "Lê Thị Minh Tuyết", "email": "tuyet.le@ailab.edu.vn", "bio": "Giảng viên Lập trình Web Full-stack, đam mê chia sẻ kiến thức.", "prefs": ["Web Development", "Programming"]},
        {"full_name": "Trần Văn Hùng", "email": "hung.tran@ailab.edu.vn", "bio": "Nhà phân tích kinh doanh, chuyên áp dụng công nghệ vào quản trị.", "prefs": ["Business", "Productivity"]},
    ]
    for data in instructors_data:
        instructor = User(
            full_name=data["full_name"],
            email=data["email"],
            hashed_password=hash_password("Giangvien@123"),
            role="instructor",
            status="active",
            email_verified=True,
            bio=data["bio"],
            learning_preferences=data["prefs"],
            avatar_url=fake.image_url(),
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 90)),
            updated_at=datetime.now(timezone.utc)
        )
        users_to_create.append(instructor)
        print(f"👨‍🏫 Đã chuẩn bị Giảng viên: {instructor.full_name} ({instructor.email})")

<<<<<<< HEAD
    # 3. Tạo Học viên
    for i in range(10):
        full_name = fake.name()
        # Tạo email hợp lệ bằng cách sử dụng fake.email() hoặc tạo từ username đơn giản
=======
    # 3. Tạo Học viên TEST (với password cố định để dễ test)
    test_students = [
        {"full_name": "Nguyễn Văn Test", "email": "student.test1@example.com"},
        {"full_name": "Trần Thị Test", "email": "student.test2@example.com"},
        {"full_name": "Lê Văn Test", "email": "student.test3@example.com"},
    ]

    for student_data in test_students:
        student = User(
            full_name=student_data["full_name"],
            email=student_data["email"],
            hashed_password=hash_password("Student@2024"),  # ✅ Password cố định
            role="student",
            status="active",
            email_verified=True,
            bio="Tài khoản test cho Adaptive Learning",
            learning_preferences=["Programming", "Data Science"],
            avatar_url=fake.image_url(),
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
            updated_at=datetime.now(timezone.utc)
        )
        users_to_create.append(student)
        print(f"🎓 Đã chuẩn bị Học viên TEST: {student.full_name} ({student.email}) - Password: Student@2024")

    # 4. Tạo thêm học viên ngẫu nhiên
    for i in range(7):
        full_name = fake.name()
>>>>>>> origin/tasks/uploadImg
        email = fake.email()
        student = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password("Hocvien@123"),
            role="student",
            status=random.choice(["active", "inactive"]),
            email_verified=random.choice([True, False]),
            bio=f"Học viên đam mê lĩnh vực {', '.join(random.sample(['Lập trình', 'Toán học', 'Kinh doanh', 'Ngoại ngữ'], 2))}.",
            learning_preferences=random.sample(["Programming", "Math", "Business", "Languages", "Data Science"], random.randint(1, 3)),
            avatar_url=fake.image_url(),
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(5, 30)),
            updated_at=datetime.now(timezone.utc)
        )
        users_to_create.append(student)
        print(f"🎓 Đã chuẩn bị Học viên: {student.full_name} ({student.email})")

    await User.insert_many(users_to_create)
    
    # Lấy lại ID sau khi insert
    for user in users_to_create:
        user_ids[user.role].append(user.id)

    print(f"✅ Đã tạo thành công {len(users_to_create)} người dùng.")
    return user_ids

async def seed_courses(user_ids: Dict[str, List[str]]) -> Dict[str, str]:
    """
<<<<<<< HEAD
    Tạo dữ liệu mẫu cho các khóa học (Course).
    - 8 khóa học thuộc các lĩnh vực và cấp độ khác nhau.
    - Gán giảng viên ngẫu nhiên từ danh sách đã tạo.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Courses ---")
    
    courses_to_create = []
    course_ids = {}
    instructor_ids = user_ids["instructor"]

    courses_data = [
        {
            "title": "Nhập môn Khoa học Dữ liệu với Python",
            "description": "Khóa học cung cấp kiến thức nền tảng về Khoa học Dữ liệu, từ thu thập, xử lý đến trực quan hóa dữ liệu bằng Python và các thư viện phổ biến như Pandas, Matplotlib.",
            "category": "Data Science", "level": "Beginner",
            "outcomes": ["Sử dụng thành thạo Pandas để xử lý dữ liệu.", "Trực quan hóa dữ liệu với Matplotlib và Seaborn.", "Hiểu các khái niệm cơ bản về Machine Learning."],
            "prerequisites": ["Kiến thức cơ bản về lập trình Python."],
            "thumbnail_url": "https://i.imgur.com/6z6XqYk.png"
        },
        {
            "title": "Lập trình Web Full-stack với FastAPI và React",
            "description": "Xây dựng ứng dụng web hiện đại từ A-Z với FastAPI cho backend và React cho frontend. Học cách thiết kế API, quản lý state và triển khai ứng dụng.",
            "category": "Web Development", "level": "Intermediate",
            "outcomes": ["Xây dựng RESTful API hiệu năng cao với FastAPI.", "Phát triển giao diện người dùng linh hoạt với React.", "Kết nối backend và frontend, xử lý xác thực người dùng."],
            "prerequisites": ["Kiến thức về Python, JavaScript, HTML/CSS."],
            "thumbnail_url": "https://i.imgur.com/Jz8g2gB.png"
        },
        {
            "title": "Ứng dụng AI trong Marketing và Kinh doanh",
            "description": "Khám phá cách trí tuệ nhân tạo đang thay đổi ngành Marketing. Học cách sử dụng các công cụ AI để phân tích khách hàng, tối ưu hóa chiến dịch và tự động hóa.",
            "category": "Business", "level": "All Levels",
            "outcomes": ["Hiểu vai trò của AI trong Marketing hiện đại.", "Sử dụng công cụ AI để phân tích dữ liệu khách hàng.", "Tối ưu hóa chiến dịch quảng cáo bằng AI."],
            "prerequisites": ["Kiến thức cơ bản về Marketing."],
            "thumbnail_url": "https://i.imgur.com/sD9g0fC.png"
        },
        {
            "title": "Toán chuyên sâu cho Machine Learning",
            "description": "Đi sâu vào các khái niệm toán học cốt lõi phía sau các thuật toán Machine Learning, bao gồm Đại số tuyến tính, Giải tích và Xác suất thống kê.",
            "category": "Math", "level": "Advanced",
            "outcomes": ["Nắm vững Đại số tuyến tính cho các mô hình AI.", "Hiểu rõ Giải tích và ứng dụng trong tối ưu hóa mô hình.", "Áp dụng Xác suất thống kê để diễn giải kết quả."],
            "prerequisites": ["Kiến thức toán cơ bản, đam mê với các mô hình toán học."],
            "thumbnail_url": "https://i.imgur.com/hN7j8gD.png"
        },
        {
            "title": "Giao tiếp Tiếng Anh chuyên nghiệp cho IT",
            "description": "Cải thiện kỹ năng giao tiếp tiếng Anh trong môi trường làm việc IT, từ viết email, thuyết trình đến tham gia phỏng vấn.",
            "category": "Languages", "level": "Intermediate",
            "outcomes": ["Tự tin viết email và tài liệu kỹ thuật bằng tiếng Anh.", "Thuyết trình hiệu quả về các chủ đề công nghệ.", "Chuẩn bị tốt cho các buổi phỏng vấn chuyên ngành IT."],
            "prerequisites": ["Trình độ tiếng Anh cơ bản (A2 trở lên)."],
            "thumbnail_url": "https://i.imgur.com/rK5l4fE.png"
        },
        {
            "title": "Phát triển Kỹ năng Mềm cho Lãnh đạo Tương lai",
            "description": "Trang bị các kỹ năng mềm thiết yếu cho sự nghiệp như giao tiếp, làm việc nhóm, giải quyết vấn đề và tư duy phản biện.",
            "category": "Productivity", "level": "All Levels",
            "outcomes": ["Nâng cao kỹ năng giao tiếp và thuyết trình.", "Học cách làm việc nhóm và lãnh đạo hiệu quả.", "Phát triển tư duy phản biện và giải quyết xung đột."],
            "prerequisites": [],
            "thumbnail_url": "https://i.imgur.com/mP3o7gH.png"
        },
        {
            "title": "Thiết kế và Phát triển Game với Unity",
            "description": "Học cách tạo ra một trò chơi 2D và 3D hoàn chỉnh từ đầu bằng công cụ Unity và ngôn ngữ C#.",
            "category": "Programming", "level": "Intermediate",
            "outcomes": ["Sử dụng thành thạo Unity Editor.", "Lập trình game logic bằng C#.", "Thiết kế và triển khai một game đơn giản."],
            "prerequisites": ["Kiến thức cơ bản về lập trình C#."],
            "thumbnail_url": "https://i.imgur.com/tO9p8jI.png"
        },
        {
            "title": "Bảo mật hệ thống cho người mới bắt đầu",
            "description": "Tìm hiểu các khái niệm cơ bản về an ninh mạng, các loại tấn công phổ biến và cách phòng chống để bảo vệ hệ thống.",
            "category": "Programming", "level": "Beginner",
            "outcomes": ["Hiểu các nguyên tắc cơ bản của an ninh mạng.", "Nhận diện các lỗ hổng bảo mật phổ biến.", "Áp dụng các biện pháp phòng thủ cơ bản."],
            "prerequisites": ["Kiến thức cơ bản về mạng máy tính."],
            "thumbnail_url": "https://i.imgur.com/Wq9N7kJ.png"
        }
    ]

    for data in courses_data:
        instructor_id = random.choice(instructor_ids)
        instructor_info = await User.get(instructor_id)
        
        course = Course(
            title=data["title"],
            description=data["description"],
            category=data["category"],
            level=data["level"],
            thumbnail_url=data["thumbnail_url"],
            language="vi",
            status="published",
            owner_id=instructor_id,
            owner_type="instructor",
            instructor_id=instructor_id,
            instructor_name=instructor_info.full_name,
            instructor_avatar=instructor_info.avatar_url,
            learning_outcomes=[{"id": str(uuid.uuid4()), "description": out, "skill_tag": out.split(" ")[0].lower()} for out in data["outcomes"]],
            prerequisites=data["prerequisites"],
            enrollment_count=random.randint(50, 500),
            avg_rating=round(random.uniform(4.5, 5.0), 1),
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(10, 100)),
            updated_at=datetime.now(timezone.utc)
        )
        courses_to_create.append(course)
        print(f"📚 Đã chuẩn bị Khóa học: {course.title}")

    await Course.insert_many(courses_to_create)
    
    for course in courses_to_create:
        course_ids[course.title] = course.id

    print(f"✅ Đã tạo thành công {len(courses_to_create)} khóa học.")
    return course_ids

async def seed_modules_and_lessons(course_ids: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Tạo dữ liệu mẫu cho các module và bài học (Lesson).
    - Mỗi khóa học có từ 3-5 module.
    - Mỗi module có từ 4-8 bài học.
    - Nội dung, thời lượng, và loại bài học đa dạng.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Modules và Lessons ---")
    
    modules_to_create = []
    lessons_to_create = []
    all_lesson_ids = {} # Dict[course_id, List[lesson_id]]
    
    # Cấu trúc mẫu cho modules và lessons theo từng khóa học
    course_content_structure = {
        "Nhập môn Khoa học Dữ liệu với Python": [
            {"title": "Giới thiệu và Cài đặt Môi trường", "lessons": ["Tổng quan về Khoa học Dữ liệu", "Cài đặt Python và Jupyter Notebook", "Làm quen với Pandas và Numpy"]},
            {"title": "Xử lý và Phân tích Dữ liệu", "lessons": ["Đọc và ghi dữ liệu với Pandas", "Làm sạch dữ liệu (Missing Data)", "Gom nhóm và tổng hợp dữ liệu (Grouping)", "Kết hợp các bộ dữ liệu (Merging & Joining)"]},
            {"title": "Trực quan hóa Dữ liệu", "lessons": ["Giới thiệu Matplotlib", "Vẽ các biểu đồ cơ bản", "Tùy chỉnh biểu đồ", "Khám phá với Seaborn"]},
            {"title": "Giới thiệu Machine Learning", "lessons": ["Các khái niệm cơ bản", "Hồi quy tuyến tính (Linear Regression)", "Phân loại (Classification)", "Đánh giá mô hình"]},
        ],
        "Lập trình Web Full-stack với FastAPI và React": [
            {"title": "Backend với FastAPI", "lessons": ["Giới thiệu FastAPI", "Routing và Path Parameters", "Request Body và Pydantic Models", "Xử lý lỗi và Dependencies"]},
            {"title": "Frontend với React", "lessons": ["Cài đặt React và JSX", "Components và Props", "State và Lifecycle", "Xử lý sự kiện và Form"]},
            {"title": "Kết nối Backend-Frontend", "lessons": ["Sử dụng `fetch` và `axios`", "CORS và Middleware", "Xác thực với JWT Token", "Hiển thị dữ liệu từ API"]},
            {"title": "Triển khai Ứng dụng", "lessons": ["Docker hóa FastAPI", "Docker hóa React", "Sử dụng Docker Compose", "Triển khai lên dịch vụ cloud"]},
        ],
        "Ứng dụng AI trong Marketing và Kinh doanh": [
            {"title": "Tổng quan về AI trong Kinh doanh", "lessons": ["AI là gì và tại sao quan trọng?", "Các ứng dụng phổ biến của AI", "Đạo đức trong việc sử dụng AI"]},
            {"title": "Phân tích Khách hàng bằng AI", "lessons": ["Thu thập dữ liệu khách hàng", "Phân khúc khách hàng (Clustering)", "Dự đoán hành vi khách hàng"]},
            {"title": "Tối ưu hóa Chiến dịch Marketing", "lessons": ["Cá nhân hóa nội dung với AI", "Tối ưu giá và khuyến mãi", "Sử dụng AI cho SEO và Content Marketing"]},
        ],
        # Các khóa học khác có thể thêm cấu trúc tương tự
    }

    for course_title, course_id in course_ids.items():
        print(f"  - Đang xử lý khóa học: {course_title}")
        all_lesson_ids[course_id] = []
        modules_data = course_content_structure.get(course_title, [
            {"title": "Module 1: Giới thiệu", "lessons": ["Bài 1.1", "Bài 1.2"]},
            {"title": "Module 2: Nội dung chính", "lessons": ["Bài 2.1", "Bài 2.2", "Bài 2.3"]},
            {"title": "Module 3: Nâng cao", "lessons": ["Bài 3.1"]},
        ])
        
        total_course_lessons = 0
        total_course_duration = 0

        for module_order, module_data in enumerate(modules_data, 1):
            module_id = str(uuid.uuid4())
            module = Module(
                id=module_id,
                course_id=course_id,
                title=module_data["title"],
                description=f"Mô tả chi tiết cho module '{module_data['title']}' thuộc khóa học '{course_title}'.",
                order=module_order,
                difficulty=random.choice(["Basic", "Intermediate", "Advanced"]),
                estimated_hours=round(random.uniform(1.5, 4.0), 1),
                learning_outcomes=[{"id": str(uuid.uuid4()), "outcome": fake.sentence(nb_words=10), "skill_tag": "general"}],
            )
            
            total_module_lessons = 0
            total_module_duration = 0

            for lesson_order, lesson_title in enumerate(module_data["lessons"], 1):
                duration = random.randint(5, 25)
                content_type = random.choice(["text", "video", "mixed"])
                lesson_id = str(uuid.uuid4())
                lesson = Lesson(
                    id=lesson_id,
                    module_id=module_id,
                    course_id=course_id,
                    title=lesson_title,
                    description=f"Nội dung chi tiết cho bài học '{lesson_title}'.",
                    order=lesson_order,
                    content=fake.paragraph(nb_sentences=15),
                    content_type=content_type,
                    duration_minutes=duration,
                    video_url="https://youtu.be/dQw4w9WgXcQ" if content_type in ["video", "mixed"] else None,
                    resources=[{
                        "id": str(uuid.uuid4()), "title": f"Tài liệu cho {lesson_title}", 
                        "type": "pdf", "url": fake.url()
                    }],
                    is_published=True,
                )
                lessons_to_create.append(lesson)
                all_lesson_ids[course_id].append(lesson_id)
                
                total_module_lessons += 1
                total_module_duration += duration
            
            module.total_lessons = total_module_lessons
            module.total_duration_minutes = total_module_duration
            modules_to_create.append(module)
            
            total_course_lessons += total_module_lessons
            total_course_duration += total_module_duration
            print(f"    + Module '{module.title}' với {module.total_lessons} bài học.")

        # Cập nhật lại thông tin cho khóa học
        await Course.find_one(Eq(Course.id, course_id)).update(
            Set({
                "total_modules": len(modules_data),
                "total_lessons": total_course_lessons,
                "total_duration_minutes": total_course_duration
            })
        )

    await Module.insert_many(modules_to_create)
    await Lesson.insert_many(lessons_to_create)

    print(f"✅ Đã tạo thành công {len(modules_to_create)} modules và {len(lessons_to_create)} lessons.")
=======
    Tạo 6 khóa học admin published với đầy đủ cấu trúc:
    - 1 khóa Python siêu chi tiết (như cũ)
    - 5 khóa khác với 2 modules mỗi khóa
    """
    print("\n--- Bắt đầu tạo KHÓA HỌC CHI TIẾT ---")
    
    # Lấy admin và instructor IDs
    admin_ids = user_ids.get("admin", [])
    instructor_ids = user_ids.get("instructor", [])
    
    admin_id = admin_ids[0] if admin_ids else None
    instructor_id = instructor_ids[0] if instructor_ids else None
    instructor_name = "Nguyễn Văn Minh"
    
    course_ids_map = {}
    
    # ========== COURSE 1: Python (Siêu chi tiết - giữ nguyên) ==========
    course_id = str(uuid.uuid4())
    course = Course(
        id=course_id,
        title="Lập trình Python từ Cơ bản đến Nâng cao",
        description="""
Khóa học toàn diện về lập trình Python, từ cơ bản đến nâng cao. 
Học viên sẽ được học từ cú pháp cơ bản, lập trình hướng đối tượng, 
xử lý dữ liệu với Pandas, phát triển web với FastAPI, đến machine learning cơ bản.

Khóa học bao gồm:
- ✅ 8 modules với 32 bài học chi tiết
- ✅ Video bài giảng HD với slide
- ✅ Bài tập thực hành sau mỗi lesson
- ✅ Project cuối khóa: Xây dựng API backend hoàn chỉnh
- ✅ Certificate hoàn thành khóa học
- ✅ Hỗ trợ 1-1 với instructor

Phù hợp cho: Người mới bắt đầu lập trình, sinh viên IT, developer muốn học Python
        """.strip(),
        category="Programming",
        level="Beginner",
        thumbnail_url="https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=450",
        preview_video_url="https://www.youtube.com/watch?v=rfscVS0vtbw",
        language="vi",
        status="published",
        owner_id=admin_id,
        owner_type="admin",
        instructor_id=instructor_id,
        instructor_name=instructor_name,
        instructor_avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150",
        instructor_bio="Giảng viên Python với 10 năm kinh nghiệm, chuyên gia về Machine Learning và Backend Development. Đã đào tạo hơn 5000 học viên thành công.",
        learning_outcomes=[
            {
                "id": str(uuid.uuid4()),
                "description": "Nắm vững cú pháp Python cơ bản: biến, vòng lặp, hàm, exception handling",
                "skill_tag": "python-basics"
            },
            {
                "id": str(uuid.uuid4()),
                "description": "Lập trình hướng đối tượng: class, inheritance, polymorphism",
                "skill_tag": "python-oop"
            },
            {
                "id": str(uuid.uuid4()),
                "description": "Xử lý dữ liệu với Pandas: đọc CSV, cleaning, analysis, visualization",
                "skill_tag": "python-pandas"
            },
            {
                "id": str(uuid.uuid4()),
                "description": "Phát triển REST API với FastAPI: endpoints, validation, database",
                "skill_tag": "python-fastapi"
            },
            {
                "id": str(uuid.uuid4()),
                "description": "Machine Learning cơ bản với scikit-learn: regression, classification",
                "skill_tag": "python-ml"
            }
        ],
        prerequisites=[
            "Kiến thức máy tính cơ bản",
            "Không cần kinh nghiệm lập trình trước đó",
            "Máy tính cài đặt Python 3.8+ và VS Code"
        ],
        modules=[],
        total_duration_minutes=0,
        total_modules=0,
        total_lessons=0,
        enrollment_count=0,
        avg_rating=4.8,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    await course.insert()
    course_ids_map[course.title] = course_id
    print(f"✅ Đã tạo Course 1: {course.title}")
    
    # ========== COURSE 2-6: Các khóa học khác (Published) ==========
    additional_courses = [
        {
            "title": "JavaScript Modern - ES6+ và React",
            "description": "Học JavaScript hiện đại với ES6+, async/await, và React framework. Xây dựng ứng dụng web động với React Hooks, Context API, và Redux.",
            "category": "Programming",
            "level": "Intermediate",
            "thumbnail_url": "https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?w=800&h=450",
            "skill_tags": ["javascript-es6", "react-basics", "react-hooks", "redux"]
        },
        {
            "title": "Data Science với Python và Pandas",
            "description": "Phân tích dữ liệu chuyên sâu với Python, Pandas, NumPy và Matplotlib. Học cách làm sạch, xử lý và visualize dữ liệu thực tế.",
            "category": "Data Science",
            "level": "Intermediate",
            "thumbnail_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=450",
            "skill_tags": ["pandas-dataframe", "numpy-arrays", "data-visualization", "data-cleaning"]
        },
        {
            "title": "Machine Learning Cơ bản",
            "description": "Khóa học Machine Learning từ cơ bản đến nâng cao với scikit-learn. Học các thuật toán: Linear Regression, Decision Trees, Random Forest, Neural Networks.",
            "category": "Data Science",
            "level": "Advanced",
            "thumbnail_url": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=450",
            "skill_tags": ["ml-regression", "ml-classification", "scikit-learn", "neural-networks"]
        },
        {
            "title": "Web Development Full-stack với MERN",
            "description": "Xây dựng ứng dụng web full-stack với MongoDB, Express, React và Node.js. Từ database design đến deployment trên cloud.",
            "category": "Programming",
            "level": "Advanced",
            "thumbnail_url": "https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=800&h=450",
            "skill_tags": ["mongodb", "express-js", "react", "nodejs"]
        },
        {
            "title": "SQL và Database Design",
            "description": "Học SQL từ cơ bản đến nâng cao: queries, joins, subqueries, indexes. Thiết kế database với normalization và optimization.",
            "category": "Programming",
            "level": "Beginner",
            "thumbnail_url": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=800&h=450",
            "skill_tags": ["sql-basics", "database-design", "sql-joins", "query-optimization"]
        },
        {
            "title": "Business Analytics và Excel nâng cao",
            "description": "Phân tích kinh doanh với Excel: Pivot Tables, VLOOKUP, Power Query, Dashboard. Học cách ra quyết định dựa trên dữ liệu.",
            "category": "Business",
            "level": "Beginner",
            "thumbnail_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=450",
            "skill_tags": ["excel-pivot", "excel-formulas", "business-analytics", "data-dashboard"]
        }
    ]
    
    for idx, course_data in enumerate(additional_courses, start=2):
        course_id = str(uuid.uuid4())
        
        # Tạo learning outcomes từ skill_tags
        learning_outcomes = [
            {
                "id": str(uuid.uuid4()),
                "description": f"Nắm vững {tag.replace('-', ' ')}",
                "skill_tag": tag
            }
            for tag in course_data["skill_tags"]
        ]
        
        course = Course(
            id=course_id,
            title=course_data["title"],
            description=course_data["description"],
            category=course_data["category"],
            level=course_data["level"],
            thumbnail_url=course_data["thumbnail_url"],
            preview_video_url="https://www.youtube.com/watch?v=rfscVS0vtbw",
            language="vi",
            status="published",  # ✅ Tất cả đều published
            owner_id=admin_id,
            owner_type="admin",
            instructor_id=instructor_id,
            instructor_name=instructor_name,
            instructor_avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150",
            instructor_bio="Giảng viên chuyên nghiệp với nhiều năm kinh nghiệm giảng dạy và thực chiến.",
            learning_outcomes=learning_outcomes,
            prerequisites=["Kiến thức cơ bản về máy tính", "Đam mê học hỏi"],
            modules=[],  # Sẽ được fill sau nếu cần
            total_duration_minutes=0,
            total_modules=0,
            total_lessons=0,
            enrollment_count=0,
            avg_rating=4.5 + (idx * 0.1),  # 4.6, 4.7, 4.8...
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await course.insert()
        course_ids_map[course.title] = course_id
        print(f"✅ Đã tạo Course {idx}: {course.title}")
    
    print(f"\n🎉 Đã tạo tổng cộng {len(course_ids_map)} khóa học admin (tất cả published)")
    return course_ids_map

async def seed_modules_and_lessons(course_ids: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Tạo cấu trúc HYBRID siêu chi tiết cho khóa học Python:
    - Course với embedded modules/lessons + Separate Module/Lesson collections
    - Đầy đủ content, resources, quiz cho từng lesson
    """
    print("\n--- Bắt đầu tạo HYBRID STRUCTURE cho Python Course ---")
    
    all_lesson_ids = {}
    # Lấy course_id từ dict với tên đầy đủ
    course_title = "Lập trình Python từ Cơ bản đến Nâng cao"
    course_id = course_ids[course_title]
    
    # 2 MODULES SIÊU CHI TIẾT CHO KHÓA HỌC PYTHON (có thể mở rộng thành 8)
    python_modules_data = [
        {
            "title": "Module 1: Python Cơ bản và Cài đặt Môi trường",
            "description": "Học cú pháp cơ bản của Python, cài đặt môi trường phát triển và làm quen với IDE",
            "difficulty": "Basic",
            "learning_outcomes": [
                {"description": "Cài đặt và cấu hình Python, pip, virtual environment", "skill_tag": "python-setup"},
                {"description": "Hiểu cú pháp cơ bản: biến, kiểu dữ liệu, operators", "skill_tag": "python-syntax"},
                {"description": "Sử dụng thành thạo VS Code cho Python development", "skill_tag": "python-ide"},
                {"description": "Debug code Python cơ bản và fix common errors", "skill_tag": "python-debugging"}
            ],
            "lessons": [
                {
                    "title": "Cài đặt Python và VS Code",
                    "description": "Hướng dẫn chi tiết cài đặt Python 3.11, pip, VS Code và Python extensions",
                    "content_type": "mixed",
                    "duration_minutes": 35,
                    "learning_objectives": ["Download Python từ python.org", "Cài extensions Python cho VS Code", "Tạo virtual environment đầu tiên"],
                    "has_quiz": True,
                    "detailed_content": """
                    <h2>Cài đặt Python trên Windows</h2>
                    <p>Python là ngôn ngữ lập trình mạnh mẽ và dễ học. Trong bài này chúng ta sẽ:</p>
                    <ul>
                        <li>Download Python 3.11 từ python.org</li>
                        <li>Cài đặt với option "Add to PATH"</li>
                        <li>Kiểm tra cài đặt bằng command line</li>
                        <li>Cài đặt pip package manager</li>
                    </ul>
                    <h3>VS Code Setup</h3>
                    <p>VS Code là IDE tốt nhất cho Python development với nhiều extensions hữu ích...</p>
                    <pre><code class="bash">
# Kiểm tra Python đã cài đặt
python --version
pip --version

# Tạo virtual environment
python -m venv myenv
myenv\\Scripts\\activate
                    </code></pre>
                    """
                },
                {
                    "title": "Biến và Kiểu dữ liệu cơ bản",
                    "description": "Học cách khai báo biến, làm việc với string, number, boolean trong Python",
                    "content_type": "code",
                    "duration_minutes": 40,
                    "learning_objectives": ["Khai báo biến với naming convention", "Sử dụng string methods", "Type conversion và checking"],
                    "has_quiz": True,
                    "detailed_content": """
                    <h2>Python Variables</h2>
                    <pre><code class="python">
# Khai báo biến
name = "Nguyễn Văn A"
age = 25
height = 1.75
is_student = True

# String formatting
greeting = f"Xin chào {name}, bạn {age} tuổi"
print(greeting)

# Type checking
print(type(name))    # <class 'str'>
print(type(age))     # <class 'int'>
print(type(height))  # <class 'float'>
                    </code></pre>
                    <p>Python sử dụng dynamic typing - không cần khai báo kiểu dữ liệu rõ ràng...</p>
                    """
                },
                {
                    "title": "Input/Output và String Manipulation",
                    "description": "Tương tác với user qua input/print, xử lý chuỗi với string methods",
                    "content_type": "mixed",
                    "duration_minutes": 30,
                    "learning_objectives": ["Sử dụng input() và print()", "String slicing và indexing", "String methods: upper(), lower(), split()"],
                    "has_quiz": False,
                    "detailed_content": """
                    <h2>User Input & String Processing</h2>
                    <pre><code class="python">
# Nhập dữ liệu từ user
name = input("Nhập tên của bạn: ")
age = int(input("Nhập tuổi: "))

# String methods
formatted_name = name.title().strip()
print(f"Xin chào {formatted_name}!")

# String slicing
text = "Python Programming"
print(text[0:6])    # "Python"
print(text[-11:])   # "Programming"
                    </code></pre>
                    """
                },
                {
                    "title": "Operators và Expressions",
                    "description": "Các phép toán số học, so sánh, logic và bitwise trong Python",
                    "content_type": "code",
                    "duration_minutes": 35,
                    "learning_objectives": ["Arithmetic operators (+, -, *, /, //, %)", "Comparison operators (==, !=, <, >)", "Logic operators (and, or, not)"],
                    "has_quiz": True,
                    "detailed_content": """
                    <h2>Python Operators</h2>
                    <pre><code class="python">
# Arithmetic
a = 10
b = 3
print(a + b)  # 13
print(a / b)   # 3.333...
print(a // b)  # 3 (floor division)
print(a % b)   # 1 (modulo)

# Logic
is_adult = age >= 18
has_license = True
can_drive = is_adult and has_license

# Comparison
x = 5
y = 10
print(x > y)  # False
print(x != y) # True
                    </code></pre>
                    """
                }
            ]
        },
        {
            "title": "Module 2: Control Flow - Điều kiện và Vòng lặp",
            "description": "Học cách điều khiển luồng chương trình với if/else, for/while loops",
            "difficulty": "Basic",
            "learning_outcomes": [
                {"description": "Sử dụng if/elif/else cho decision making", "skill_tag": "python-conditionals"},
                {"description": "Viết for loops để iterate qua data structures", "skill_tag": "python-loops"},
                {"description": "Sử dụng while loops và break/continue", "skill_tag": "python-while"},
                {"description": "Nested loops và complex logic", "skill_tag": "python-nested"}
            ],
            "lessons": [
                {
                    "title": "If/Elif/Else Statements",
                    "description": "Học cách tạo decision making logic với conditional statements",
                    "content_type": "code",
                    "duration_minutes": 30,
                    "learning_objectives": ["If/else syntax", "Multiple conditions với elif", "Nested if statements"],
                    "has_quiz": True,
                    "detailed_content": """
                    <h2>Conditional Statements</h2>
                    <pre><code class="python">
# Basic if statement
age = 18
if age >= 18:
    print("Bạn đã đủ tuổi")
else:
    print("Bạn chưa đủ tuổi")

# Multiple conditions
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

print(f"Điểm của bạn: {grade}")
                    </code></pre>
                    """
                },
                {
                    "title": "For Loops và Range",
                    "description": "Iteration với for loops, sử dụng range() function cho number sequences",
                    "content_type": "code",
                    "duration_minutes": 40,
                    "learning_objectives": ["For loop syntax", "Range function parameters", "Iterate qua lists và strings"],
                    "has_quiz": True,
                    "detailed_content": """
                    <h2>For Loops in Python</h2>
                    <pre><code class="python">
# Basic for loop
for i in range(5):
    print(f"Số {i}")

# Loop qua list
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(f"Tôi thích {fruit}")

# Loop với index
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# Range với start, stop, step
for i in range(2, 10, 2):
    print(i)  # 2, 4, 6, 8
                    </code></pre>
                    """
                },
                {
                    "title": "While Loops và Break/Continue",
                    "description": "Vòng lặp while, điều khiển loop flow với break và continue",
                    "content_type": "mixed",
                    "duration_minutes": 35,
                    "learning_objectives": ["While loop syntax", "Break để thoát loop", "Continue để skip iteration"],
                    "has_quiz": False,
                    "detailed_content": """
                    <h2>While Loops</h2>
                    <pre><code class="python">
# Basic while loop
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1

# Break và continue
numbers = [1, 2, 3, 4, 5]
for num in numbers:
    if num == 3:
        continue  # Skip 3
    if num == 5:
        break     # Exit loop
    print(num)   # Prints: 1, 2, 4
                    </code></pre>
                    """
                },
                {
                    "title": "Nested Loops và Pattern Printing",
                    "description": "Vòng lặp lồng nhau, tạo patterns và xử lý 2D data structures",
                    "content_type": "code",
                    "duration_minutes": 45,
                    "learning_objectives": ["Nested loop concepts", "Print star patterns", "Process 2D lists"],
                    "has_quiz": True,
                    "detailed_content": """
                    <h2>Nested Loops</h2>
                    <pre><code class="python">
# Star pattern
for i in range(5):
    for j in range(i + 1):
        print("*", end="")
    print()

# Output:
# *
# **
# ***
# ****
# *****

# 2D list processing
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
for row in matrix:
    for element in row:
        print(element, end=" ")
    print()
                    </code></pre>
                    """
                }
            ]
        }
    ]
    
    print(f"  - Đang xử lý khóa học: Lập trình Python từ Cơ bản đến Nâng cao")
    all_lesson_ids[course_id] = []
    
    total_course_lessons = 0
    total_course_duration = 0

    # Tạo cả embedded structure VÀ separate collections (HYBRID ARCHITECTURE)
    course_modules = []  # Embedded modules cho course
    separate_modules = []  # Separate Module documents
    separate_lessons = []  # Separate Lesson documents
    
    for module_order, module_data in enumerate(python_modules_data, 1):
        module_id = str(uuid.uuid4())  # Cùng ID cho cả embedded và separate
        
        # Tạo embedded lessons cho module VÀ separate lesson documents
        module_lessons = []  # Embedded lessons
        module_lesson_documents = []  # Separate lesson documents
        total_module_duration = 0
        
        for lesson_order, lesson_info in enumerate(module_data["lessons"], 1):
            lesson_id = str(uuid.uuid4())  # Cùng ID cho cả embedded và separate
            quiz_id = str(uuid.uuid4()) if lesson_info.get("has_quiz", False) else None
            
            # Danh sách video Python thực tế từ YouTube (miễn phí, public)
            demo_videos = [
                "https://www.youtube.com/watch?v=rfscVS0vtbw",  # Learn Python - Full Course for Beginners
                "https://www.youtube.com/watch?v=_uQrJ0TkZlc",  # Python Tutorial
                "https://www.youtube.com/watch?v=kqtD5dpn9C8",  # Python for Beginners
                "https://www.youtube.com/watch?v=8ext9G7xspg",  # Python Full Course
                "https://www.youtube.com/watch?v=t8pPdKYpowI",  # Python Crash Course
            ]
            
            # Chọn video dựa trên lesson_order
            video_url = demo_videos[(lesson_order + module_order) % len(demo_videos)]
            video_id = video_url.split("watch?v=")[1] if "watch?v=" in video_url else "rfscVS0vtbw"
            
            # Tạo rich content structure với video thực tế
            lesson_content = {
                "html_content": lesson_info.get("detailed_content", f"<p>Nội dung chi tiết cho {lesson_info['title']}</p>"),
                "video_url": video_url,  # Video YouTube thực tế
                "video_duration": lesson_info["duration_minutes"] * 60,
                "video_thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",  # Thumbnail thực tế
                "code_snippets": [
                    {
                        "language": "python",
                        "code": f"# Code example for {lesson_info['title']}\\nprint('Hello from lesson {lesson_order} module {module_order}')",
                        "description": f"Example code for {lesson_info['title']}"
                    }
                ]
            }
            
            # Tạo resources chi tiết (bao gồm audio)
            lesson_resources = [
                {
                    "id": str(uuid.uuid4()),
                    "type": "pdf",
                    "title": f"Slide - {lesson_info['title']}",
                    "description": f"PDF slides cho bài {lesson_info['title']}",
                    "url": f"https://docs.course.com/python/module_{module_order}/lesson_{lesson_order}.pdf",
                    "file_size_bytes": random.randint(2000000, 8000000),
                    "is_downloadable": True
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "code",
                    "title": f"Code Examples - {lesson_info['title']}",
                    "description": "File Python với code examples và exercises",
                    "url": f"https://github.com/python-course/module_{module_order}/lesson_{lesson_order}.py",
                    "file_size_bytes": random.randint(5000, 50000),
                    "is_downloadable": True
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "audio",
                    "title": f"Audio Lecture - {lesson_info['title']}",
                    "description": "Bản ghi âm bài giảng dạng MP3",
                    "url": f"https://www.soundhelix.com/examples/mp3/SoundHelix-Song-{(lesson_order % 16) + 1}.mp3",  # Demo audio công khai
                    "file_size_bytes": random.randint(5000000, 15000000),  # 5-15MB
                    "audio_format": "mp3",
                    "duration_seconds": lesson_info["duration_minutes"] * 60,
                    "is_downloadable": True
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "external_link",
                    "title": "Python Official Documentation",
                    "description": "Link tới tài liệu chính thức của Python",
                    "url": "https://docs.python.org/3/tutorial/",
                    "file_size_bytes": None,
                    "is_downloadable": False
                }
            ]
            
            # 1. Tạo EmbeddedLesson cho Course.modules[]
            embedded_lesson = EmbeddedLesson(
                id=lesson_id,  # Explicit ID
                title=lesson_info["title"],
                description=lesson_info["description"],
                order=lesson_order,
                content=json.dumps(lesson_content),  # Store as JSON string
                content_type=lesson_info["content_type"],
                duration_minutes=lesson_info["duration_minutes"],
                video_url=lesson_content["video_url"],  # YouTube video thực tế
                audio_url=f"https://www.soundhelix.com/examples/mp3/SoundHelix-Song-{(lesson_order % 16) + 1}.mp3" if lesson_order % 2 == 0 else None,  # Demo audio công khai
                resources=lesson_resources,
                learning_objectives=lesson_info.get("learning_objectives", []),
                quiz_id=quiz_id,
                is_published=True
            )
            
            # 2. Tạo separate Lesson document cho lessons collection
            separate_lesson = Lesson(
                id=lesson_id,  # Cùng ID với embedded
                module_id=module_id,  # Link tới Module
                course_id=course_id,  # Denormalized link
                title=lesson_info["title"],
                description=lesson_info["description"],
                order=lesson_order,
                content=json.dumps(lesson_content),  # Full content
                content_type=lesson_info["content_type"],
                duration_minutes=lesson_info["duration_minutes"],
                video_url=lesson_content["video_url"],  # YouTube video thực tế
                audio_url=f"https://www.soundhelix.com/examples/mp3/SoundHelix-Song-{(lesson_order % 16) + 1}.mp3" if lesson_order % 2 == 0 else None,  # Demo audio công khai
                resources=lesson_resources,
                learning_objectives=lesson_info.get("learning_objectives", []),
                quiz_id=quiz_id,
                is_published=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            module_lessons.append(embedded_lesson)  # Add to embedded list
            module_lesson_documents.append(separate_lesson)  # Add to separate list
            total_module_duration += lesson_info["duration_minutes"]
        
        # 1. Tạo EmbeddedModule cho Course.modules[]
        embedded_module = EmbeddedModule(
            id=module_id,  # Explicit ID
            title=module_data["title"],
            description=module_data["description"],
            order=module_order,
            difficulty=module_data["difficulty"],
            estimated_hours=round(total_module_duration / 60, 1),
            learning_outcomes=module_data["learning_outcomes"],
            lessons=module_lessons,  # Embedded lessons
            total_lessons=len(module_lessons),
            total_duration_minutes=total_module_duration
        )
        
        # 2. Tạo separate Module document cho modules collection
        separate_module = Module(
            id=module_id,  # Cùng ID với embedded
            course_id=course_id,  # Link tới Course
            title=module_data["title"],
            description=module_data["description"],
            order=module_order,
            difficulty=module_data["difficulty"],
            estimated_hours=round(total_module_duration / 60, 1),
            learning_outcomes=module_data["learning_outcomes"],
            total_lessons=len(module_lessons),
            total_duration_minutes=total_module_duration,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        course_modules.append(embedded_module)  # Add to embedded list
        separate_modules.append(separate_module)  # Add to separate list
        separate_lessons.extend(module_lesson_documents)  # Add lessons to separate list
        total_course_lessons += len(module_lessons)
        total_course_duration += total_module_duration
        print(f"    + Module '{embedded_module.title}' với {embedded_module.total_lessons} bài học (embedded + separate)")

    # 1. Cập nhật Course với embedded modules
    await Course.find_one(Eq(Course.id, course_id)).update(
        Set({
            "modules": [module.model_dump() for module in course_modules],
            "total_modules": len(course_modules),
            "total_lessons": total_course_lessons,
            "total_duration_minutes": total_course_duration
        })
    )
    
    # 2. Lưu separate Module documents vào modules collection
    if separate_modules:
        await Module.insert_many(separate_modules)
        print(f"    ✅ Đã lưu {len(separate_modules)} separate modules vào database")
    
    # 3. Lưu separate Lesson documents vào lessons collection
    if separate_lessons:
        await Lesson.insert_many(separate_lessons)
        print(f"    ✅ Đã lưu {len(separate_lessons)} separate lessons vào database")
    
    # 4. Lưu lesson IDs cho các functions khác
    all_lesson_ids[course_id] = []
    for module in course_modules:
        for lesson in module.lessons:
            all_lesson_ids[course_id].append(lesson.id)
    
    print(f"    🎯 Course 'Python Mastery' hoàn thành với HYBRID ARCHITECTURE")
    print(f"      - Embedded: {len(course_modules)} modules, {total_course_lessons} lessons")
    print(f"      - Separate: {len(separate_modules)} modules, {len(separate_lessons)} lessons")

    print(f"✅ Đã tạo thành công HYBRID ARCHITECTURE cho Python Course:")
    print(f"   🔹 Course document với embedded modules/lessons (cho navigation)")
    print(f"   🔹 Separate Module documents (cho detailed access)")  
    print(f"   🔹 Separate Lesson documents (cho full content)")
    print(f"   🔗 Linking: Course.modules[].id === Module.id === Lesson.module_id")
>>>>>>> origin/tasks/uploadImg
    return all_lesson_ids

async def seed_enrollments(user_ids: Dict[str, List[str]], course_ids: Dict[str, str]) -> List[str]:
    """
    Tạo dữ liệu mẫu cho việc đăng ký khóa học (Enrollment).
<<<<<<< HEAD
    - Mỗi học viên sẽ đăng ký từ 2-5 khóa học ngẫu nhiên.
=======
    - Mỗi học viên sẽ đăng ký vào khóa học Python duy nhất.
>>>>>>> origin/tasks/uploadImg
    - Trạng thái và tiến độ đăng ký sẽ được sinh ngẫu nhiên.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Enrollments ---")
    
    enrollments_to_create = []
    enrollment_ids = []
    student_ids = user_ids["student"]
<<<<<<< HEAD
    course_id_list = list(course_ids.values())

    for student_id in student_ids:
        num_enrollments = random.randint(2, 5)
        enrolled_courses = random.sample(course_id_list, num_enrollments)
=======
    # Chỉ có 1 khóa học Python duy nhất
    python_course_id = course_ids["Lập trình Python từ Cơ bản đến Nâng cao"]

    for student_id in student_ids:
        # Mỗi student enroll vào khóa Python duy nhất
        enrolled_courses = [python_course_id]
>>>>>>> origin/tasks/uploadImg
        
        for course_id in enrolled_courses:
            status = random.choice(["active", "completed", "cancelled"])
            progress = 0.0
            completed_at = None
            if status == "completed":
                progress = 100.0
                completed_at = datetime.now(timezone.utc) - timedelta(days=random.randint(5, 30))
            elif status == "active":
                progress = round(random.uniform(10.0, 90.0), 2)

            enrollment = Enrollment(
                user_id=student_id,
                course_id=course_id,
                status=status,
                progress_percent=progress,
                avg_quiz_score=round(random.uniform(65.0, 95.0), 2) if status != "cancelled" else None,
                total_time_spent_minutes=random.randint(60, 1200),
                enrolled_at=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 180)),
                last_accessed_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 29)),
                completed_at=completed_at,
            )
            enrollments_to_create.append(enrollment)
            enrollment_ids.append(enrollment.id)
            
    await Enrollment.insert_many(enrollments_to_create)
    print(f"✅ Đã tạo thành công {len(enrollments_to_create)} lượt đăng ký khóa học.")
    return enrollment_ids

async def seed_quizzes_and_attempts(user_ids: Dict[str, List[str]], lesson_ids: Dict[str, List[str]]):
    """
    Tạo dữ liệu mẫu cho Quizzes và QuizAttempts.
    - Tạo quiz cho một số bài học ngẫu nhiên.
    - Tạo các lượt làm bài của học viên cho các quiz đó.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Quizzes và Quiz Attempts ---")
    
    quizzes_to_create = []
    attempts_to_create = []
    student_ids = user_ids["student"]
    instructor_ids = user_ids["instructor"]

    for course_id, lessons in lesson_ids.items():
        if not lessons:
            continue
        
        # Chọn 2-3 bài học trong mỗi khóa để tạo quiz
        lessons_for_quiz = random.sample(lessons, min(len(lessons), random.randint(2, 3)))
        
        for lesson_id in lessons_for_quiz:
            question_count = random.randint(5, 10)
            questions = []
            total_points = 0
            for i in range(question_count):
                points = random.randint(1, 2)
                question = {
                    "id": str(uuid.uuid4()),
                    "type": "multiple_choice",
                    "question_text": f"Đây là câu hỏi {i+1} cho bài học? {fake.sentence(nb_words=8)}",
                    "options": [fake.sentence(nb_words=3) for _ in range(4)],
                    "correct_answer": "0", # Giả sử đáp án A luôn đúng
                    "explanation": "Giải thích chi tiết cho đáp án đúng.",
                    "points": points,
                    "is_mandatory": random.choice([True, False]),
                    "order": i + 1
                }
                questions.append(question)
                total_points += points

            quiz = Quiz(
                lesson_id=lesson_id,
                course_id=course_id,
                title=f"Bài kiểm tra cuối bài học",
                description="Kiểm tra kiến thức đã học trong bài.",
                time_limit_minutes=random.randint(10, 20),
                passing_score=70.0,
                max_attempts=3,
                questions=questions,
                question_count=question_count,
                total_points=total_points,
                created_by=random.choice(instructor_ids),
            )
            quizzes_to_create.append(quiz)
            print(f"    📝 Đã chuẩn bị Quiz cho Lesson ID: {lesson_id}")

            # Tạo các lượt làm bài (QuizAttempt) cho quiz này
            for student_id in random.sample(student_ids, random.randint(3, 7)):
                score = round(random.uniform(50.0, 100.0), 2)
                passed = score >= quiz.passing_score
                
                attempt = QuizAttempt(
                    quiz_id=quiz.id,
                    user_id=student_id,
                    score=score,
                    status="Pass" if passed else "Fail",
                    passed=passed,
                    attempt_number=random.randint(1, quiz.max_attempts),
                    correct_answers=int(quiz.question_count * (score / 100)),
                    total_questions=quiz.question_count,
                    started_at=datetime.now(timezone.utc) - timedelta(minutes=30),
                    submitted_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(5, 25)),
                    time_spent_seconds=random.randint(300, 1200)
                )
                attempts_to_create.append(attempt)

    await Quiz.insert_many(quizzes_to_create)
    await QuizAttempt.insert_many(attempts_to_create)
    
    print(f"✅ Đã tạo thành công {len(quizzes_to_create)} quizzes và {len(attempts_to_create)} quiz attempts.")

async def seed_progress(enrollment_ids: List[str]):
    """
    Tạo dữ liệu mẫu cho tiến độ học tập (Progress).
    - Tạo một bản ghi Progress cho mỗi Enrollment 'active' hoặc 'completed'.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Progress ---")
    
    progress_to_create = []
    
    enrollments = await Enrollment.find(
        In(Enrollment.id, enrollment_ids),
        NE(Enrollment.status, "cancelled")
    ).to_list()

    for enrollment in enrollments:
        course = await Course.get(enrollment.course_id)
        if not course:
            continue
            
        lessons = await Lesson.find(Lesson.course_id == course.id).to_list()
        total_lessons_count = len(lessons)
        
        completed_lessons_count = int(total_lessons_count * (enrollment.progress_percent / 100))
        completed_lessons = random.sample(lessons, completed_lessons_count)

        lessons_progress = []
        for lesson in lessons:
            status = "not-started"
            completion_date = None
            if lesson.id in [l.id for l in completed_lessons]:
                status = "completed"
                completion_date = enrollment.enrolled_at + timedelta(days=random.randint(1, 20))
            
<<<<<<< HEAD
            lessons_progress.append({
                "lesson_id": lesson.id,
                "lesson_title": lesson.title,
                "status": status,
                "completion_date": completion_date,
                "time_spent_minutes": random.randint(5, 60) if status == "completed" else 0
            })
=======
            lessons_progress.append(LessonProgressItem(
                lesson_id=str(lesson.id),
                lesson_title=lesson.title,
                status=status,
                completion_date=completion_date,
                time_spent_minutes=random.randint(5, 60) if status == "completed" else 0,
                video_progress_seconds=random.randint(0, 1800) if status in ["in-progress", "completed"] else 0
            ))
>>>>>>> origin/tasks/uploadImg

        progress = Progress(
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            enrollment_id=enrollment.id,
            overall_progress_percent=enrollment.progress_percent,
            completed_lessons_count=completed_lessons_count,
            total_lessons_count=total_lessons_count,
            lessons_progress=lessons_progress,
            total_time_spent_minutes=enrollment.total_time_spent_minutes,
            study_streak_days=random.randint(0, 25),
            avg_quiz_score=enrollment.avg_quiz_score,
            last_accessed_at=enrollment.last_accessed_at
        )
        progress_to_create.append(progress)

    if progress_to_create:
        await Progress.insert_many(progress_to_create)
    
    print(f"✅ Đã tạo thành công {len(progress_to_create)} bản ghi tiến độ học tập.")

<<<<<<< HEAD
async def seed_assessment_sessions(user_ids: Dict[str, List[str]]):
    """
    Tạo dữ liệu mẫu cho các phiên đánh giá năng lực (AssessmentSession).
    - Tạo 5-7 phiên đánh giá cho các học viên ngẫu nhiên.
    - Một số phiên đã hoàn thành và được chấm điểm, một số đang chờ.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Assessment Sessions ---")
    
    sessions_to_create = []
    student_ids = user_ids["student"]
    
    categories = ["Programming", "Data Science", "Business", "Math"]
    subjects = {
        "Programming": ["Python", "JavaScript", "Bảo mật"],
        "Data Science": ["Pandas", "Machine Learning"],
        "Business": ["Marketing", "Quản trị"],
        "Math": ["Đại số", "Giải tích"]
    }

    for _ in range(random.randint(5, 7)):
        student_id = random.choice(student_ids)
        category = random.choice(categories)
        subject = random.choice(subjects[category])
        level = random.choice(["Beginner", "Intermediate", "Advanced"])
        status = random.choice(["evaluated", "submitted", "pending"])
        
        question_count = {"Beginner": 15, "Intermediate": 25, "Advanced": 35}[level]
        time_limit = {"Beginner": 15, "Intermediate": 22, "Advanced": 30}[level]
        
        questions = []
        for i in range(question_count):
            questions.append({
                "question_id": str(uuid.uuid4()),
                "question_text": f"Câu hỏi về {subject} ở mức độ {level} số {i+1}?",
                "question_type": "multiple_choice",
                "difficulty": random.choice(["easy", "medium", "hard"]),
                "skill_tag": f"{subject.lower()}-skill-{random.randint(1,3)}",
                "points": random.randint(1, 3),
                "options": [fake.word() for _ in range(4)]
            })

        session = AssessmentSession(
            user_id=student_id,
            category=category,
            subject=subject,
            level=level,
            total_questions=question_count,
            time_limit_minutes=time_limit,
            questions=questions,
            status=status,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 15)),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
        )

        if status in ["submitted", "evaluated"]:
            session.submitted_at = session.created_at + timedelta(minutes=random.randint(10, time_limit))
            answers = []
            for q in questions:
                answers.append({
                    "question_id": q["question_id"],
                    "answer_content": "0",
                    "time_taken_seconds": random.randint(20, 60)
                })
            session.answers = answers

        if status == "evaluated":
            score = round(random.uniform(40.0, 98.0), 2)
            session.evaluated_at = session.submitted_at + timedelta(seconds=random.randint(30, 90))
            session.overall_score = score
            session.proficiency_level = "Beginner" if score < 50 else ("Intermediate" if score < 80 else "Advanced")
            session.skill_analysis = {
                "skill_tag": "python-syntax", "questions_count": 5, "correct_count": 3,
                "proficiency_percentage": 60.0, "strength_level": "Average",
                "detailed_feedback": "Bạn cần cải thiện thêm về cú pháp Python."
            }
            session.knowledge_gaps = [{
                "gap_area": "Decorators", "description": "Chưa hiểu rõ về decorators.",
                "importance": "Medium", "suggested_action": "Xem lại bài học về Decorators."
            }]
        
        sessions_to_create.append(session)

    if sessions_to_create:
        await AssessmentSession.insert_many(sessions_to_create)
        
    print(f"✅ Đã tạo thành công {len(sessions_to_create)} phiên đánh giá năng lực.")
=======
async def seed_assessment_sessions(user_ids: Dict[str, List[str]], course_ids: Dict[str, str]):
    """
    Tạo dữ liệu mẫu cho các phiên đánh giá năng lực (AssessmentSession).
    - Tạo assessment sessions cho khóa Python với module_scores chi tiết
    - Tạo cả high-score và low-score sessions để test Adaptive Learning
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Assessment Sessions (Adaptive Learning Ready) ---")

    sessions_to_create = []
    student_ids = user_ids["student"]

    # Lấy Python course để tạo assessment
    python_course_id = course_ids.get("Lập trình Python từ Cơ bản đến Nâng cao")
    if not python_course_id:
        print("⚠️ Không tìm thấy Python course, skip assessment sessions")
        return

    # Lấy course và modules
    python_course = await Course.get(python_course_id)
    if not python_course or not python_course.modules:
        print("⚠️ Python course không có modules, skip assessment sessions")
        return

    print(f"  📚 Tạo assessment cho course: {python_course.title}")
    print(f"  📦 Course có {len(python_course.modules)} modules")

    # Tạo 3 assessment sessions với điểm khác nhau
    assessment_scenarios = [
        {
            "name": "High Performer (Auto-Skip Ready)",
            "score_range": (85, 95),
            "session_type": "placement",
            "proficiency_level": "Advanced",
            "description": "Học viên giỏi, có thể skip modules"
        },
        {
            "name": "Average Performer (Review Needed)",
            "score_range": (65, 75),
            "session_type": "placement",
            "proficiency_level": "Intermediate",
            "description": "Học viên trung bình, cần review"
        },
        {
            "name": "Beginner (Start from Scratch)",
            "score_range": (40, 55),
            "session_type": "placement",
            "proficiency_level": "Beginner",
            "description": "Học viên mới, cần học từ đầu"
        }
    ]

    for scenario in assessment_scenarios:
        student_id = random.choice(student_ids)

        # Tạo questions cho từng module
        questions = []
        module_scores = {}
        question_id_counter = 0

        for module in python_course.modules:
            module_id = str(module.id)
            questions_per_module = 5  # 5 câu hỏi mỗi module

            # Tạo questions cho module này
            module_questions = []
            for i in range(questions_per_module):
                question_id_counter += 1
                question = {
                    "question_id": str(uuid.uuid4()),
                    "module_id": module_id,
                    "question_text": f"Câu hỏi {question_id_counter} về {module.title}?",
                    "question_type": "multiple_choice",
                    "difficulty": random.choice(["easy", "medium", "hard"]),
                    "skill_tag": f"python-module-{module.order}",
                    "points": 1,
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "0",
                    "time_spent_seconds": random.randint(30, 90)
                }
                module_questions.append(question)
                questions.append(question)

            # Tính điểm cho module dựa trên scenario
            base_score = random.uniform(*scenario["score_range"])
            variation = random.uniform(-5, 5)  # Thêm variation
            module_score = max(0, min(100, base_score + variation))

            # Tính số câu đúng
            correct_count = int(questions_per_module * (module_score / 100))

            # Xác định proficiency level
            if module_score >= 85:
                proficiency = "advanced"
            elif module_score >= 65:
                proficiency = "intermediate"
            else:
                proficiency = "beginner"

            module_scores[module_id] = {
                "module_title": module.title,
                "score": round(module_score, 2),
                "proficiency_level": proficiency,
                "questions_count": questions_per_module,
                "correct_count": correct_count,
                "time_spent_seconds": sum(q["time_spent_seconds"] for q in module_questions)
            }

        # Tính overall score
        overall_score = round(sum(ms["score"] for ms in module_scores.values()) / len(module_scores), 2)
        total_questions = len(questions)
        correct_answers = sum(ms["correct_count"] for ms in module_scores.values())

        # Tạo AssessmentSession
        session = AssessmentSession(
            user_id=str(student_id),

            # Required fields
            category="Programming",
            subject="Python",
            level="Beginner",
            total_questions=total_questions,
            time_limit_minutes=30,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),

            # Status
            status="evaluated",  # ✅ evaluated để có kết quả

            # Results - use correct field names
            overall_score=overall_score,  # ✅ Correct field name
            proficiency_level=scenario["proficiency_level"],  # ✅ Set proficiency level

            # Timestamps
            submitted_at=datetime.now(timezone.utc) - timedelta(hours=1),
            evaluated_at=datetime.now(timezone.utc) - timedelta(minutes=30),

            # Data
            questions=questions,

            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 5))
        )

        sessions_to_create.append(session)
        print(f"  ✅ {scenario['name']}: Score {overall_score}% ({correct_answers}/{total_questions} correct)")

    if sessions_to_create:
        await AssessmentSession.insert_many(sessions_to_create)

    print(f"✅ Đã tạo thành công {len(sessions_to_create)} assessment sessions cho Adaptive Learning")
>>>>>>> origin/tasks/uploadImg

async def seed_conversations(user_ids: Dict[str, List[str]], course_ids: Dict[str, str]):
    """
    Tạo dữ liệu mẫu cho các cuộc trò chuyện (Conversation).
    - Tạo một vài cuộc trò chuyện cho học viên trong các khóa học họ đã đăng ký.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Conversations ---")
    
    conversations_to_create = []
    student_ids = user_ids["student"]
    
    enrollments = await Enrollment.find(
        In(Enrollment.user_id, student_ids),
        Eq(Enrollment.status, "active")
    ).to_list()
    
    if not enrollments:
        print("⚠️ Không có enrollment nào đang active để tạo conversation.")
        return

    for _ in range(min(len(enrollments), 10)): # Tạo tối đa 10 conversations
        enrollment = random.choice(enrollments)
        course = await Course.get(enrollment.course_id)
        if not course:
            continue

        messages = []
        last_message_time = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 5))
        for i in range(random.randint(2, 5)): # 2-5 cặp tin nhắn
            user_time = last_message_time + timedelta(minutes=i*10)
            assistant_time = user_time + timedelta(minutes=1)
            
            messages.append({
                "id": str(uuid.uuid4()), "role": "user",
                "content": f"Em có câu hỏi về {course.title}: {fake.sentence(nb_words=10)}",
                "created_at": user_time
            })
            messages.append({
                "id": str(uuid.uuid4()), "role": "assistant",
                "content": f"Chào bạn, đây là câu trả lời: {fake.paragraph(nb_sentences=2)}",
                "created_at": assistant_time
            })
            last_message_time = assistant_time

        conversation = Conversation(
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            title=f"Thảo luận về {course.title}",
            summary=f"Tóm tắt cuộc trò chuyện về {course.title}.",
            course_title=course.title,
            messages=messages,
            total_messages=len(messages),
            last_message_at=messages[-1]["created_at"]
        )
        conversations_to_create.append(conversation)

    if conversations_to_create:
        await Conversation.insert_many(conversations_to_create)
        
    print(f"✅ Đã tạo thành công {len(conversations_to_create)} cuộc trò chuyện.")

async def seed_classes(user_ids: Dict[str, List[str]], course_ids: Dict[str, str]):
    """
    Tạo dữ liệu mẫu cho các lớp học (Class).
<<<<<<< HEAD
    - Mỗi giảng viên tạo 1-2 lớp học cho các khóa học khác nhau.
=======
    - Mỗi giảng viên tạo 2-3 lớp học cho các khóa học khác nhau
    - Mỗi lớp có 5-15 học viên
    - Status: preparing, active, hoặc completed
>>>>>>> origin/tasks/uploadImg
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Classes ---")
    
    classes_to_create = []
    instructor_ids = user_ids["instructor"]
    student_ids = user_ids["student"]
<<<<<<< HEAD
    course_id_list = list(course_ids.values())

    for instructor_id in instructor_ids:
        num_classes = random.randint(1, 2)
        courses_for_class = random.sample(course_id_list, num_classes)
        
        for course_id in courses_for_class:
            course_info = await Course.get(course_id)
            start_date = datetime.now(timezone.utc) + timedelta(days=random.randint(1, 15))
            
            # Đảm bảo số học viên được chọn không vượt quá tổng số học viên có sẵn
            num_students = min(len(student_ids), random.randint(5, 15))
            
            class_item = Class(
                name=f"Lớp {course_info.title} - K{random.randint(1, 5)}",
                description=f"Lớp học chuyên sâu về {course_info.title} do giảng viên hướng dẫn.",
=======
    
    # Lấy danh sách courses (chỉ admin courses, không lấy personal)
    available_courses = list(course_ids.items())
    
    if not available_courses:
        print("⚠️ Không có khóa học nào để tạo lớp.")
        return
    
    # Mỗi instructor tạo 2-3 classes
    for instructor_id in instructor_ids:
        num_classes = random.randint(2, 3)
        
        # Random chọn courses cho instructor này
        selected_courses = random.sample(available_courses, k=min(len(available_courses), num_classes))
        
        for course_title, course_id in selected_courses:
            course_info = await Course.get(course_id)
            if not course_info:
                continue
            
            # Random start date (một số đã bắt đầu, một số sắp bắt đầu)
            days_offset = random.randint(-30, 15)  # -30 = đã bắt đầu 30 ngày trước
            start_date = datetime.now(timezone.utc) + timedelta(days=days_offset)
            duration_days = random.randint(30, 90)
            end_date = start_date + timedelta(days=duration_days)
            
            # Determine status based on dates
            now = datetime.now(timezone.utc)
            if start_date > now:
                status = "preparing"
            elif end_date < now:
                status = "completed"
            else:
                status = "active"
            
            # Random số học viên (5-15)
            num_students = min(len(student_ids), random.randint(5, 15))
            selected_students = random.sample(student_ids, k=num_students)
            
            # Tạo tên lớp đẹp
            class_number = random.randint(1, 20)
            semester = random.choice(["K1", "K2", "K3", "K4", "K5"])
            
            class_item = Class(
                name=f"Lớp {course_info.title[:30]}... - {semester}.{class_number}",
                description=f"Lớp học chuyên sâu về {course_info.title}. Giảng viên sẽ hướng dẫn chi tiết từng bài học, hỗ trợ 1-1 và review bài tập. Lớp học online qua Zoom với lịch cố định.",
>>>>>>> origin/tasks/uploadImg
                course_id=course_id,
                instructor_id=instructor_id,
                max_students=random.randint(20, 50),
                start_date=start_date,
<<<<<<< HEAD
                end_date=start_date + timedelta(days=random.randint(30, 60)),
                status=random.choice(["preparing", "active"]),
                student_ids=random.sample(student_ids, k=num_students)
            )
            classes_to_create.append(class_item)
            print(f"    🏫 Đã chuẩn bị Lớp học: {class_item.name}")

    if classes_to_create:
        await Class.insert_many(classes_to_create)
        
    print(f"✅ Đã tạo thành công {len(classes_to_create)} lớp học.")
=======
                end_date=end_date,
                status=status,
                student_ids=selected_students,
                created_at=start_date - timedelta(days=random.randint(7, 30)),  # Tạo trước khi bắt đầu
                updated_at=datetime.now(timezone.utc)
            )
            classes_to_create.append(class_item)
            print(f"    🏫 Đã chuẩn bị Lớp: {class_item.name} ({status}, {num_students} students)")
    
    if classes_to_create:
        await Class.insert_many(classes_to_create)
        
    # Thống kê
    active_count = sum(1 for c in classes_to_create if c.status == "active")
    preparing_count = sum(1 for c in classes_to_create if c.status == "preparing")
    completed_count = sum(1 for c in classes_to_create if c.status == "completed")
    
    print(f"✅ Đã tạo thành công {len(classes_to_create)} lớp học:")
    print(f"   - Active: {active_count}")
    print(f"   - Preparing: {preparing_count}")
    print(f"   - Completed: {completed_count}")
>>>>>>> origin/tasks/uploadImg

async def seed_recommendations(user_ids: Dict[str, List[str]]):
    """
    Tạo dữ liệu mẫu cho các đề xuất học tập (Recommendation).
    - Tạo đề xuất dựa trên các phiên đánh giá đã hoàn thành.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Recommendations ---")
    
    recommendations_to_create = []
    
    evaluated_sessions = await AssessmentSession.find(Eq(AssessmentSession.status, "evaluated")).to_list()
    all_courses = await Course.find(Eq(Course.status, "published")).to_list()

    if not all_courses:
        print("⚠️ Không có khóa học nào để tạo đề xuất.")
        return

    for session in evaluated_sessions:
        recommended_courses = []
        # Đề xuất 2-3 khóa học phù hợp
        for course in random.sample(all_courses, k=min(len(all_courses), random.randint(2, 3))):
            recommended_courses.append({
                "course_id": course.id,
                "title": course.title,
                "description": course.description,
                "category": course.category,
                "level": course.level,
                "priority_rank": random.randint(1, 3),
                "relevance_score": round(random.uniform(70, 95), 2),
                "reason": f"Dựa trên kết quả đánh giá về {session.subject}, khóa học này sẽ giúp bạn cải thiện kỹ năng.",
                "addresses_gaps": [gap["gap_area"] for gap in session.knowledge_gaps] if session.knowledge_gaps else []
            })

        recommendation = Recommendation(
            user_id=session.user_id,
            source="assessment",
            assessment_session_id=session.id,
            user_proficiency_level=session.proficiency_level,
            recommended_courses=recommended_courses,
            ai_personalized_advice="Để phát triển tốt nhất, bạn nên tập trung vào các khóa học được đề xuất và hoàn thành các bài tập thực hành.",
<<<<<<< HEAD
            created_at=session.evaluated_at + timedelta(seconds=random.randint(60, 120))
=======
            created_at=(session.evaluated_at or datetime.now(timezone.utc)) + timedelta(seconds=random.randint(60, 120))
>>>>>>> origin/tasks/uploadImg
        )
        recommendations_to_create.append(recommendation)

    if recommendations_to_create:
        await Recommendation.insert_many(recommendations_to_create)
        
    print(f"✅ Đã tạo thành công {len(recommendations_to_create)} đề xuất học tập.")


<<<<<<< HEAD
=======
async def seed_personal_courses(user_ids: Dict[str, List[str]]) -> List[str]:
    """
    Tạo Personal Courses (Khóa học cá nhân) do STUDENT tự tạo.
    Section 2.5 - CHUCNANG.md
    - 3-5 khóa học cá nhân từ các student khác nhau
    - Mỗi khóa có modules và lessons tự định nghĩa
    """
    print("\n--- Bắt đầu tạo Personal Courses (Student tự tạo) ---")
    
    personal_courses_to_create = []
    personal_course_ids = []
    student_ids = user_ids.get("student", [])
    
    if not student_ids:
        print("⚠️ Không có student để tạo personal courses.")
        return []
    
    # Lấy 2-3 students ngẫu nhiên để tạo khóa học cá nhân (giảm từ 3-5)
    selected_students = random.sample(student_ids, k=min(len(student_ids), random.randint(2, 3)))
    
    personal_course_templates = [
        {
            "title": "Lộ trình học Machine Learning của tôi",
            "description": "Khóa học cá nhân tổng hợp kiến thức ML từ cơ bản đến nâng cao mà tôi đã học và nghiên cứu",
            "category": "Data Science",
            "level": "Intermediate"
        },
        {
            "title": "Tự học Web Development Full-stack",
            "description": "Khóa học cá nhân về phát triển web từ HTML/CSS đến React và Node.js",
            "category": "Programming",
            "level": "Beginner"
        },
        {
            "title": "Chinh phục Tiếng Anh IELTS",
            "description": "Lộ trình cá nhân ôn luyện IELTS 7.0+ với tài liệu và bài tập tự tổng hợp",
            "category": "Languages",
            "level": "Intermediate"
        },
        {
            "title": "Toán học cho Data Science",
            "description": "Tổng hợp kiến thức toán cần thiết cho Data Science: Linear Algebra, Calculus, Statistics",
            "category": "Math",
            "level": "Advanced"
        },
        {
            "title": "Khởi nghiệp và Quản lý Startup",
            "description": "Khóa học tự tổng hợp về khởi nghiệp, từ ý tưởng đến MVP và fundraising",
            "category": "Business",
            "level": "Beginner"
        }
    ]
    
    for idx, student_id in enumerate(selected_students):
        template = personal_course_templates[idx % len(personal_course_templates)]
        
        # Lấy thông tin student
        student = await User.get(student_id)
        
        course_id = str(uuid.uuid4())
        
        # Tạo modules cho personal course
        personal_modules = []
        for mod_idx in range(random.randint(2, 4)):
            module_id = str(uuid.uuid4())
            
            # Tạo lessons cho module
            module_lessons = []
            for lesson_idx in range(random.randint(2, 5)):
                lesson_id = str(uuid.uuid4())
                
                embedded_lesson = EmbeddedLesson(
                    id=lesson_id,
                    title=f"Bài {lesson_idx + 1}: {fake.catch_phrase()}",
                    description=f"Nội dung bài học số {lesson_idx + 1} trong module {mod_idx + 1}",
                    order=lesson_idx + 1,
                    content_type=random.choice(["text", "video", "mixed"]),
                    duration_minutes=random.randint(15, 45),
                    learning_objectives=[f"Hiểu {fake.word()}", f"Thực hành {fake.word()}"],
                    is_published=random.choice([True, False]),
                    video_url=f"https://youtu.be/personal_{course_id}_{lesson_id}" if random.choice([True, False]) else None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                module_lessons.append(embedded_lesson)
            
            embedded_module = EmbeddedModule(
                id=module_id,
                title=f"Module {mod_idx + 1}: {fake.bs().title()}",
                description=f"Mô tả chi tiết cho module {mod_idx + 1}",
                order=mod_idx + 1,
                difficulty=random.choice(["Basic", "Intermediate", "Advanced"]),
                lessons=module_lessons,
                is_published=random.choice([True, False]),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            personal_modules.append(embedded_module)
        
        # Tính toán tổng duration
        total_duration = sum(
            lesson.duration_minutes 
            for module in personal_modules 
            for lesson in module.lessons
        )
        
        total_lessons = sum(len(module.lessons) for module in personal_modules)
        
        personal_course = Course(
            id=course_id,
            title=template["title"],
            description=template["description"],
            category=template["category"],
            level=template["level"],
            thumbnail_url=f"https://images.unsplash.com/photo-{random.randint(1500000000000, 1600000000000)}?w=800&h=450",
            language="vi",
            status=random.choices(["published", "draft"], weights=[80, 20])[0],  # 80% published, 20% draft
            owner_id=student_id,
            owner_type="student",  # ✅ Student là owner
            instructor_id=None,  # Personal course không có instructor
            instructor_name=None,
            instructor_avatar=None,
            instructor_bio=None,  # Personal course không có instructor bio
            learning_outcomes=[
                {
                    "id": str(uuid.uuid4()),
                    "description": f"Đạt được kỹ năng về {template['category']}",
                    "skill_tag": f"{template['category'].lower()}-personal"
                }
            ],
            prerequisites=[
                "Tự học, tự nghiên cứu",
                "Đam mê và kiên trì"
            ],
            modules=personal_modules,
            total_duration_minutes=total_duration,
            total_modules=len(personal_modules),
            total_lessons=total_lessons,
            enrollment_count=0,
            avg_rating=0.0,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.utcnow()
        )
        
        personal_courses_to_create.append(personal_course)
        personal_course_ids.append(course_id)
        print(f"    📚 Đã chuẩn bị Personal Course: {personal_course.title} (bởi {student.full_name})")
    
    if personal_courses_to_create:
        await Course.insert_many(personal_courses_to_create)
    
    print(f"✅ Đã tạo thành công {len(personal_courses_to_create)} khóa học cá nhân (Personal Courses).")
    return personal_course_ids


>>>>>>> origin/tasks/uploadImg
async def main():
    """Hàm chính để chạy script."""
    await init_db()
    user_ids = await seed_users()
    course_ids = await seed_courses(user_ids)
    lesson_ids = await seed_modules_and_lessons(course_ids)
    enrollment_ids = await seed_enrollments(user_ids, course_ids)
    await seed_quizzes_and_attempts(user_ids, lesson_ids)
    await seed_progress(enrollment_ids)
<<<<<<< HEAD
    await seed_assessment_sessions(user_ids)
    await seed_conversations(user_ids, course_ids)
    await seed_classes(user_ids, course_ids)
    await seed_recommendations(user_ids)
    # Các hàm seed khác sẽ được gọi ở đây
    print("\n🎉 Hoàn tất quá trình khởi tạo dữ liệu mẫu!")
=======
    await seed_assessment_sessions(user_ids, course_ids)  # ✅ Pass course_ids
    await seed_conversations(user_ids, course_ids)
    await seed_classes(user_ids, course_ids)
    await seed_recommendations(user_ids)
    await seed_personal_courses(user_ids)
    print("\n🎉 Hoàn tất quá trình khởi tạo dữ liệu mẫu!")
    print("\n📊 THỐNG KÊ DỮ LIỆU:")
    print(f"  👥 Users: {await User.count()}")
    print(f"  📚 Courses (Admin): {await Course.find({'owner_type': 'admin'}).count()}")
    print(f"  📖 Personal Courses (Student): {await Course.find({'owner_type': 'student'}).count()}")
    print(f"  📝 Enrollments: {await Enrollment.count()}")
    print(f"  🎯 Assessment Sessions: {await AssessmentSession.count()}")
    print(f"  💬 Conversations: {await Conversation.count()}")
    print(f"  🏫 Classes: {await Class.count()}")
    print(f"  🎓 Progress Records: {await Progress.count()}")
    print(f"  📊 Quiz Attempts: {await QuizAttempt.count()}")
    print(f"  💡 Recommendations: {await Recommendation.count()}")

    # ✅ In ra thông tin để test Adaptive Learning
    print("\n" + "="*80)
    print("🎯 ADAPTIVE LEARNING TEST DATA")
    print("="*80)

    # Lấy Python course
    python_course = await Course.find_one({"title": "Lập trình Python từ Cơ bản đến Nâng cao"})
    if python_course:
        print(f"\n📚 Course: {python_course.title}")
        print(f"   🆔 Course ID: {python_course.id}")
        print(f"   📦 Modules: {python_course.total_modules}")
        print(f"   📝 Lessons: {python_course.total_lessons}")

        # Lấy enrollments cho course này
        enrollments = await Enrollment.find({"course_id": str(python_course.id)}).to_list()
        if enrollments:
            print(f"\n📋 Enrollments ({len(enrollments)}):")
            for enr in enrollments[:3]:  # Show first 3
                user = await User.get(enr.user_id)
                print(f"   - {user.full_name if user else 'Unknown'}: {enr.id}")

        # Lấy assessment sessions
        all_assessments = await AssessmentSession.find_all().to_list()

        if all_assessments:
            print(f"\n🎯 Assessment Sessions ({len(all_assessments)}):")
            for assess in all_assessments:
                user = await User.get(assess.user_id)
                print(f"   - {user.full_name if user else 'Unknown'}: Score {assess.overall_score}%")
                print(f"     🆔 Assessment ID: {assess.id}")
                print(f"     📊 Subject: {assess.subject} | Level: {assess.level}")
                print(f"     ✅ Status: {assess.status} | Proficiency: {assess.proficiency_level}")

                # Tìm enrollment cho Python course
                enrollment = await Enrollment.find_one({
                    "user_id": assess.user_id,
                    "course_id": str(python_course.id)
                })
                if enrollment:
                    print(f"     📋 Enrollment ID (Python Course): {enrollment.id}")
                print()


>>>>>>> origin/tasks/uploadImg

if __name__ == "__main__":
    asyncio.run(main())
