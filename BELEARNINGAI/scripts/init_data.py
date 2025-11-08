"""
Script để khởi tạo dữ liệu mẫu cho toàn bộ hệ thống AI Learning Platform.
Tuân thủ 100% theo API_SCHEMA.md và models.py.
Dữ liệu được sinh ra có tính logic, thực tế và đa dạng.
"""
import asyncio
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
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from config.config import get_settings
from models.models import (
    User,
    Course,
    Module,
    Lesson,
    Enrollment,
    AssessmentSession,
    Quiz,
    QuizAttempt,
    Progress,
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

    # 3. Tạo Học viên
    for i in range(10):
        full_name = fake.name()
        # Tạo email hợp lệ bằng cách sử dụng fake.email() hoặc tạo từ username đơn giản
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
    return all_lesson_ids

async def seed_enrollments(user_ids: Dict[str, List[str]], course_ids: Dict[str, str]) -> List[str]:
    """
    Tạo dữ liệu mẫu cho việc đăng ký khóa học (Enrollment).
    - Mỗi học viên sẽ đăng ký từ 2-5 khóa học ngẫu nhiên.
    - Trạng thái và tiến độ đăng ký sẽ được sinh ngẫu nhiên.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Enrollments ---")
    
    enrollments_to_create = []
    enrollment_ids = []
    student_ids = user_ids["student"]
    course_id_list = list(course_ids.values())

    for student_id in student_ids:
        num_enrollments = random.randint(2, 5)
        enrolled_courses = random.sample(course_id_list, num_enrollments)
        
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
            
            lessons_progress.append({
                "lesson_id": lesson.id,
                "lesson_title": lesson.title,
                "status": status,
                "completion_date": completion_date,
                "time_spent_minutes": random.randint(5, 60) if status == "completed" else 0
            })

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
    - Mỗi giảng viên tạo 1-2 lớp học cho các khóa học khác nhau.
    """
    print("\n--- Bắt đầu tạo dữ liệu cho Classes ---")
    
    classes_to_create = []
    instructor_ids = user_ids["instructor"]
    student_ids = user_ids["student"]
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
                course_id=course_id,
                instructor_id=instructor_id,
                max_students=random.randint(20, 50),
                start_date=start_date,
                end_date=start_date + timedelta(days=random.randint(30, 60)),
                status=random.choice(["preparing", "active"]),
                student_ids=random.sample(student_ids, k=num_students)
            )
            classes_to_create.append(class_item)
            print(f"    🏫 Đã chuẩn bị Lớp học: {class_item.name}")

    if classes_to_create:
        await Class.insert_many(classes_to_create)
        
    print(f"✅ Đã tạo thành công {len(classes_to_create)} lớp học.")

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
            created_at=session.evaluated_at + timedelta(seconds=random.randint(60, 120))
        )
        recommendations_to_create.append(recommendation)

    if recommendations_to_create:
        await Recommendation.insert_many(recommendations_to_create)
        
    print(f"✅ Đã tạo thành công {len(recommendations_to_create)} đề xuất học tập.")


async def main():
    """Hàm chính để chạy script."""
    await init_db()
    user_ids = await seed_users()
    course_ids = await seed_courses(user_ids)
    lesson_ids = await seed_modules_and_lessons(course_ids)
    enrollment_ids = await seed_enrollments(user_ids, course_ids)
    await seed_quizzes_and_attempts(user_ids, lesson_ids)
    await seed_progress(enrollment_ids)
    await seed_assessment_sessions(user_ids)
    await seed_conversations(user_ids, course_ids)
    await seed_classes(user_ids, course_ids)
    await seed_recommendations(user_ids)
    # Các hàm seed khác sẽ được gọi ở đây
    print("\n🎉 Hoàn tất quá trình khởi tạo dữ liệu mẫu!")

if __name__ == "__main__":
    asyncio.run(main())
