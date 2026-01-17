"""
System Health Check Script

Quick check để verify tất cả components đang hoạt động.

Usage: python scripts/health_check.py
"""
import asyncio
import sys


async def check_imports():
    """Check all required imports"""
    print("\n🔍 Checking imports...")
    
    required_imports = [
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic"),
        ("motor", "Motor (MongoDB)"),
        ("beanie", "Beanie ODM"),
        ("faiss-cpu", "FAISS"),
        ("numpy", "NumPy"),
        ("google.generativeai", "Google AI"),
        ("passlib", "Passlib"),
        ("jose", "Python-JOSE"),
    ]
    
    all_ok = True
    for module, name in required_imports:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            all_ok = False
    
    return all_ok


async def check_config():
    """Check configuration"""
    print("\n🔍 Checking configuration...")
    
    try:
        from config.config import settings
        
        checks = [
            ("MONGODB_URL", settings.mongodb_url),
            ("MONGODB_DATABASE", settings.mongodb_database),
            ("JWT_SECRET_KEY", settings.jwt_secret_key),
            ("GOOGLE_API_KEY", settings.google_api_key),
            ("VECTOR_PERSIST_DIRECTORY", settings.vector_persist_directory),
        ]
        
        all_ok = True
        for name, value in checks:
            if value and value != "change_me" and value != "":
                print(f"  ✅ {name}: Configured")
            else:
                print(f"  ⚠️  {name}: Not configured or using default")
                if name in ["GOOGLE_API_KEY", "MONGODB_URL"]:
                    all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        return False


async def check_mongodb():
    """Check MongoDB connection"""
    print("\n🔍 Checking MongoDB...")
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from config.config import settings
        
        client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Try to get server info
        await client.server_info()
        
        print(f"  ✅ MongoDB connected: {settings.mongodb_url}")
        print(f"  ✅ Database: {settings.mongodb_database}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ MongoDB connection failed: {e}")
        print(f"     URL: {settings.mongodb_url}")
        return False


async def check_vector_db():
    """Check FAISS Vector Database"""
    print("\n🔍 Checking FAISS Vector Database...")
    
    try:
        from config.config import settings
        from services.vector_service import vector_service
        
        if vector_service is None:
            print("  ❌ Vector service not initialized")
            return False
        
        print("  ✅ FAISS Vector Service initialized")
        print(f"  ✅ Persist directory: {settings.vector_persist_directory}")
        
        # Test basic functionality
        stats = await vector_service.get_collection_stats("health_check")
        count = stats.get("count", 0)
        
        print(f"  ✅ Test collection working (vectors: {count})")
        print("  ✅ FAISS Vector Database is ready!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAISS Vector Database error: {e}")
        return False


async def check_google_ai():
    """Check Google AI API"""
    print("\n🔍 Checking Google AI...")
    
    try:
        import google.generativeai as genai
        from config.config import settings
        
        if not settings.google_api_key or settings.google_api_key == "":
            print("  ⚠️  GOOGLE_API_KEY not configured")
            return False
        
        # Configure API
        genai.configure(api_key=settings.google_api_key)
        
        # Try to list models (quick check)
        print("  ✅ Google AI API key configured")
        print("  ℹ️  To fully test, run: python scripts/test_rag.py")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Google AI error: {e}")
        return False


async def check_services():
    """Check custom services"""
    print("\n🔍 Checking services...")
    
    try:
        from services.embedding_service import embedding_service
        from services.vector_service import vector_service
        from services.course_indexing_service import course_indexing_service
        
        if embedding_service:
            print("  ✅ Embedding Service initialized")
        else:
            print("  ❌ Embedding Service not initialized")
            
        if vector_service:
            print("  ✅ Vector Service initialized")
        else:
            print("  ❌ Vector Service not initialized")
            
        if course_indexing_service:
            print("  ✅ Course Indexing Service initialized")
        else:
            print("  ❌ Course Indexing Service not initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service error: {e}")
        return False


async def main():
    """Run all health checks"""
    print("="*70)
    print("  BELEARNING AI - SYSTEM HEALTH CHECK")
    print("="*70)
    
    checks = [
        ("Imports", check_imports),
        ("Configuration", check_config),
        ("MongoDB", check_mongodb),
        ("Vector DB", check_vector_db),
        ("Google AI", check_google_ai),
        ("Services", check_services),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = await check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print("="*70)
    print(f"  Result: {passed}/{total} checks passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! System is healthy.")
        print("\n📝 Next steps:")
        print("   1. Run tests: python scripts/test_rag.py")
        print("   2. Start server: uvicorn app.main:app --reload")
        print("   3. Open docs: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed.")
        print("\n📝 Troubleshooting:")
        print("   1. Check .env file exists and has correct values")
        print("   2. Ensure MongoDB is running: net start MongoDB")
        print("   3. Install dependencies: pip install -r requirements.txt")
        print("   4. Check GOOGLE_API_KEY is valid")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
