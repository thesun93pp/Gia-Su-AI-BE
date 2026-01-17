"""
Script tạo indexes cho MongoDB collections.
Chạy script này sau khi setup database để tối ưu performance.

Usage:
    python scripts/create_indexes.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from config.config import get_settings


async def safe_create_index(collection, keys, index_name="", **kwargs):
    """
    Tạo index an toàn, bỏ qua nếu index đã tồn tại với tên khác.
    
    Args:
        collection: MongoDB collection
        keys: Index keys (string hoặc list of tuples)
        index_name: Tên index để hiển thị
        **kwargs: Các options khác (name, unique, etc.)
    """
    try:
        await collection.create_index(keys, **kwargs)
        print(f"  ✓ {index_name}")
    except Exception as e:
        if "already exists" in str(e).lower():
            # Index đã tồn tại, bỏ qua
            print(f"  ⊙ {index_name} (đã tồn tại)")
        else:
            # Lỗi khác, raise lên
            print(f"  ✗ {index_name} - Lỗi: {str(e)}")
            raise


async def create_indexes():
    """Tạo tất cả indexes cần thiết cho MongoDB."""
    
    settings = get_settings()
    print("🔗 Đang kết nối MongoDB...")
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    
    print(f"📊 Database: {settings.mongodb_database}\n")
    
    # ========================================
    # USERS COLLECTION
    # ========================================
    print("👤 Tạo indexes cho collection 'users'...")
    
    await safe_create_index(db.users, "email", index_name="email (unique)", unique=True, name="idx_users_email")
    await safe_create_index(db.users, "role", index_name="role", name="idx_users_role")
    await safe_create_index(db.users, "status", index_name="status", name="idx_users_status")
    await safe_create_index(db.users, "created_at", index_name="created_at", name="idx_users_created_at")
    await safe_create_index(db.users, "last_login_at", index_name="last_login_at", name="idx_users_last_login_at")

    # ========================================
    # REFRESH TOKENS COLLECTION
    # ========================================
    print("\n🔑 Tạo indexes cho collection 'refresh_tokens'...")
    await safe_create_index(db.refresh_tokens, "user_id", index_name="user_id", name="idx_refresh_tokens_user_id")
    await safe_create_index(db.refresh_tokens, "token", index_name="token", name="idx_refresh_tokens_token")
    await safe_create_index(db.refresh_tokens, "expires_at", index_name="expires_at", name="idx_refresh_tokens_expires_at")

    # ========================================
    # COURSES COLLECTION
    # ========================================
    print("\n📚 Tạo indexes cho collection 'courses'...")
    
    await safe_create_index(db.courses, "owner_id", index_name="owner_id", name="idx_courses_owner_id")
    await safe_create_index(db.courses, "instructor_id", index_name="instructor_id", name="idx_courses_instructor")
    await safe_create_index(db.courses, "category", index_name="category", name="idx_courses_category")
    await safe_create_index(db.courses, "level", index_name="level", name="idx_courses_level")
    await safe_create_index(db.courses, "status", index_name="status", name="idx_courses_status")
    await safe_create_index(db.courses, "created_at", index_name="created_at", name="idx_courses_created_at")

    # Text search index
    await safe_create_index(db.courses, 
        [("title", "text"), ("description", "text")],
        index_name="title + description (text search)",
        name="idx_courses_text_search",
        default_language="none"
    )
    
    # Compound indexes
    await safe_create_index(db.courses, [("category", 1), ("level", 1)], index_name="category + level", name="idx_courses_category_level")
    await safe_create_index(db.courses, [("status", 1), ("created_at", -1)], index_name="status + created_at", name="idx_courses_status_created_at")
    await safe_create_index(db.courses, [("category", 1), ("status", 1)], index_name="category + status", name="idx_courses_category_status")
    await safe_create_index(db.courses, [("instructor_id", 1), ("status", 1)], index_name="instructor + status", name="idx_courses_instructor_status")

    # ========================================
    # MODULES COLLECTION
    # ========================================
    print("\n🧩 Tạo indexes cho collection 'modules'...")
    await safe_create_index(db.modules, "course_id", index_name="course_id", name="idx_modules_course_id")
    await safe_create_index(db.modules, [("course_id", 1), ("order", 1)], index_name="course_id + order", name="idx_modules_course_order")

    # ========================================
    # LESSONS COLLECTION
    # ========================================
    print("\n📖 Tạo indexes cho collection 'lessons'...")
    await safe_create_index(db.lessons, "module_id", index_name="module_id", name="idx_lessons_module_id")
    await safe_create_index(db.lessons, "course_id", index_name="course_id", name="idx_lessons_course_id")
    await safe_create_index(db.lessons, "quiz_id", index_name="quiz_id", name="idx_lessons_quiz_id")
    await safe_create_index(db.lessons, [("module_id", 1), ("order", 1)], index_name="module_id + order", name="idx_lessons_module_order")
    await safe_create_index(db.lessons, [("course_id", 1), ("is_published", 1)], index_name="course_id + is_published", name="idx_lessons_course_published")

    # ========================================
    # ENROLLMENTS COLLECTION
    # ========================================
    print("\n📝 Tạo indexes cho collection 'enrollments'...")
    
    await safe_create_index(db.enrollments, [("user_id", 1), ("course_id", 1)], index_name="user_id + course_id (unique)", unique=True, name="idx_enrollments_user_course")
    await safe_create_index(db.enrollments, "user_id", index_name="user_id", name="idx_enrollments_user")
    await safe_create_index(db.enrollments, "course_id", index_name="course_id", name="idx_enrollments_course")
    await safe_create_index(db.enrollments, "status", index_name="status", name="idx_enrollments_status")
    await safe_create_index(db.enrollments, "enrolled_at", index_name="enrolled_at", name="idx_enrollments_enrolled_at")
    await safe_create_index(db.enrollments, "last_accessed_at", index_name="last_accessed_at", name="idx_enrollments_last_accessed")
    await safe_create_index(db.enrollments, [("user_id", 1), ("status", 1)], index_name="user_id + status", name="idx_enrollments_user_status")
    await safe_create_index(db.enrollments, [("course_id", 1), ("status", 1)], index_name="course_id + status", name="idx_enrollments_course_status")

    # ========================================
    # CLASSES COLLECTION
    # ========================================
    print("\n🏫 Tạo indexes cho collection 'classes'...")
    
    await safe_create_index(db.classes, "instructor_id", index_name="instructor_id", name="idx_classes_instructor")
    await safe_create_index(db.classes, "course_id", index_name="course_id", name="idx_classes_course")
    await safe_create_index(db.classes, "invite_code", index_name="invite_code (unique)", unique=True, name="idx_classes_invite_code")
    await safe_create_index(db.classes, "status", index_name="status", name="idx_classes_status")
    
    # ========================================
    # QUIZZES COLLECTION
    # ========================================
    print("\n📋 Tạo indexes cho collection 'quizzes'...")
    
    await safe_create_index(db.quizzes, "lesson_id", index_name="lesson_id", name="idx_quizzes_lesson")
    await safe_create_index(db.quizzes, "course_id", index_name="course_id", name="idx_quizzes_course")
    await safe_create_index(db.quizzes, "created_by", index_name="created_by", name="idx_quizzes_created_by")
    await safe_create_index(db.quizzes, "is_draft", index_name="is_draft", name="idx_quizzes_is_draft")
    await safe_create_index(db.quizzes, "created_at", index_name="created_at", name="idx_quizzes_created_at")
    await safe_create_index(db.quizzes, [("course_id", 1), ("is_draft", 1)], index_name="course_id + is_draft", name="idx_quizzes_course_draft")
    await safe_create_index(db.quizzes, [("lesson_id", 1), ("is_draft", 1)], index_name="lesson_id + is_draft", name="idx_quizzes_lesson_draft")

    # ========================================
    # QUIZ ATTEMPTS COLLECTION
    # ========================================
    print("\n✍️ Tạo indexes cho collection 'quiz_attempts'...")
    
    await safe_create_index(db.quiz_attempts, "quiz_id", index_name="quiz_id", name="idx_attempts_quiz")
    await safe_create_index(db.quiz_attempts, "user_id", index_name="user_id", name="idx_attempts_user")
    await safe_create_index(db.quiz_attempts, "started_at", index_name="started_at", name="idx_attempts_started_at")
    await safe_create_index(db.quiz_attempts, "submitted_at", index_name="submitted_at", name="idx_attempts_submitted_at")
    await safe_create_index(db.quiz_attempts, "status", index_name="status", name="idx_attempts_status")
    await safe_create_index(db.quiz_attempts, [("user_id", 1), ("quiz_id", 1)], index_name="user_id + quiz_id", name="idx_attempts_user_quiz")
    await safe_create_index(db.quiz_attempts, [("user_id", 1), ("quiz_id", 1), ("attempt_number", 1)], index_name="user_id + quiz_id + attempt", name="idx_attempts_user_quiz_attempt")
    await safe_create_index(db.quiz_attempts, [("quiz_id", 1), ("submitted_at", -1)], index_name="quiz_id + submitted_at", name="idx_attempts_quiz_submitted")

    # ========================================
    # ASSESSMENT SESSIONS COLLECTION
    # ========================================
    print("\n🎯 Tạo indexes cho collection 'assessment_sessions'...")
    
    await safe_create_index(db.assessment_sessions, "user_id", index_name="user_id", name="idx_assessments_user")
    await safe_create_index(db.assessment_sessions, "status", index_name="status", name="idx_assessments_status")
    await safe_create_index(db.assessment_sessions, "category", index_name="category", name="idx_assessments_category")
    await safe_create_index(db.assessment_sessions, "subject", index_name="subject", name="idx_assessments_subject")
    await safe_create_index(db.assessment_sessions, "level", index_name="level", name="idx_assessments_level")
    await safe_create_index(db.assessment_sessions, "created_at", index_name="created_at", name="idx_assessments_created_at")
    await safe_create_index(db.assessment_sessions, "expires_at", index_name="expires_at", name="idx_assessments_expires_at")
    await safe_create_index(db.assessment_sessions, [("user_id", 1), ("created_at", -1)], index_name="user_id + created_at", name="idx_assessments_user_date")

    # ========================================
    # CONVERSATIONS COLLECTION
    # ========================================
    print("\n� Tạo indexes cho collection 'conversations'...")
    
    await safe_create_index(db.conversations, "user_id", index_name="user_id", name="idx_conversations_user")
    await safe_create_index(db.conversations, "course_id", index_name="course_id", name="idx_conversations_course")
    await safe_create_index(db.conversations, "created_at", index_name="created_at", name="idx_conversations_created_at")
    await safe_create_index(db.conversations, "last_message_at", index_name="last_message_at", name="idx_conversations_last_message_at")
    await safe_create_index(db.conversations, [("user_id", 1), ("course_id", 1)], index_name="user_id + course_id", name="idx_conversations_user_course")
    await safe_create_index(db.conversations, [("user_id", 1), ("last_message_at", -1)], index_name="user_id + last_message_at", name="idx_conversations_user_last_message")

    # ========================================
    # PROGRESS COLLECTION
    # ========================================
    print("\n� Tạo indexes cho collection 'progress'...")
    
    await safe_create_index(db.progress, [("user_id", 1), ("course_id", 1)], unique=True, index_name="user_id + course_id (unique)", name="idx_progress_user_course")
    await safe_create_index(db.progress, "user_id", index_name="user_id", name="idx_progress_user")
    await safe_create_index(db.progress, "course_id", index_name="course_id", name="idx_progress_course")
    await safe_create_index(db.progress, "enrollment_id", index_name="enrollment_id", name="idx_progress_enrollment")

    # ========================================
    # RECOMMENDATIONS COLLECTION
    # ========================================
    print("\n� Tạo indexes cho collection 'recommendations'...")
    await safe_create_index(db.recommendations, "user_id", index_name="user_id", name="idx_recommendations_user_id")
    await safe_create_index(db.recommendations, "assessment_session_id", index_name="assessment_session_id", name="idx_recommendations_assessment_id")
    await safe_create_index(db.recommendations, "created_at", index_name="created_at", name="idx_recommendations_created_at")

    # ========================================
    # PASSWORD RESET TOKENS COLLECTION
    # ========================================
    print("\n� Tạo indexes cho collection 'password_reset_tokens'...")
    await safe_create_index(db.password_reset_tokens, "user_id", index_name="user_id", name="idx_password_reset_tokens_user_id")
    await safe_create_index(db.password_reset_tokens, "token", index_name="token", name="idx_password_reset_tokens_token")
    await safe_create_index(db.password_reset_tokens, "expires_at", index_name="expires_at", name="idx_password_reset_tokens_expires_at")

    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*60)
    print("✅ Đã tạo thành công tất cả indexes!")
    print("="*60)
    
    # List all collections with index count
    print("\n📋 Tóm tắt indexes theo collection:\n")
    collections = [
        "users", "refresh_tokens", "password_reset_tokens",
        "courses", "modules", "lessons",
        "enrollments", "progress",
        "assessment_sessions",
        "quizzes", "quiz_attempts",
        "classes", "conversations",
        "recommendations"
    ]
    
    total_indexes = 0
    for collection_name in sorted(collections):
        try:
            indexes = await db[collection_name].list_indexes().to_list(length=None)
            index_count = len(indexes)
            total_indexes += index_count
            print(f"  {collection_name:25} : {index_count:2} indexes")
        except Exception:
            print(f"  {collection_name:25} : (collection không tồn tại)")

    print("-" * 40)
    print(f"  {'TOTAL':25} : {total_indexes:2} indexes")
    print("\n✨ Database đã sẵn sàng cho production!")
    
    client.close()


async def drop_all_indexes():
    """Drop tất cả indexes (dùng khi cần recreate)."""
    
    print("⚠️  CẢNH BÁO: Đang xóa tất cả indexes...")
    
    response = input("Bạn có chắc chắn muốn xóa tất cả indexes? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Đã hủy.")
        return
    
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    
    collections = await db.list_collection_names()
    
    for collection_name in collections:
        if collection_name.startswith("system."):
            continue
        # Keep _id_ index (default)
        try:
            indexes = await db[collection_name].list_indexes().to_list(length=None)
            for index in indexes:
                if index["name"] != "_id_":
                    await db[collection_name].drop_index(index["name"])
                    print(f"  ✓ Đã xóa {collection_name}.{index['name']}")
        except Exception as e:
            print(f"  ✗ Lỗi khi xóa index của collection {collection_name}: {e}")

    print("\n✅ Đã xóa tất cả custom indexes.")
    client.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MongoDB Indexes Management")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all custom indexes before creating new ones"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        asyncio.run(drop_all_indexes())
    
    asyncio.run(create_indexes())
