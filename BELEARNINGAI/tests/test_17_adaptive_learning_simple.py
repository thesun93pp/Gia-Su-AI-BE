"""
Simple Test for Adaptive Learning Features
Test basic functionality without complex setup
"""

import pytest


# ============================================================================
# IMPORT TESTS - Verify all components can be imported
# ============================================================================

@pytest.mark.asyncio
async def test_service_import():
    """Test that adaptive learning service can be imported"""
    try:
        from services.adaptive_learning_service import adaptive_learning_service
        assert adaptive_learning_service is not None
        print("\n✅ Adaptive learning service imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import adaptive learning service: {e}")


@pytest.mark.asyncio
async def test_router_import():
    """Test that adaptive learning router can be imported"""
    try:
        from routers.adaptive_learning_router import router
        assert router is not None
        print("\n✅ Adaptive learning router imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import adaptive learning router: {e}")


@pytest.mark.asyncio
async def test_models_have_adaptive_fields():
    """Test that Enrollment and Progress models have adaptive learning fields"""
    from models.models import Enrollment, Progress

    # Check Enrollment model
    enrollment_fields = Enrollment.model_fields.keys()
    assert "adaptive_learning_enabled" in enrollment_fields
    assert "skipped_modules" in enrollment_fields
    assert "recommended_start_module_id" in enrollment_fields
    assert "learning_path_decisions" in enrollment_fields
    print("\n✅ Enrollment model has adaptive learning fields")

    # Check Progress model
    progress_fields = Progress.model_fields.keys()
    assert "auto_skipped_lessons" in progress_fields
    assert "learning_path_type" in progress_fields
    assert "adjustment_history" in progress_fields
    assert "learning_behavior_metrics" in progress_fields
    print("✅ Progress model has adaptive learning fields")


# ============================================================================
# API ENDPOINT TESTS - Verify endpoints are registered and working
# ============================================================================

@pytest.mark.asyncio
async def test_swagger_docs(client):
    """Test that Swagger docs include adaptive learning endpoints"""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    openapi_spec = response.json()
    paths = openapi_spec.get("paths", {})

    # Check if adaptive learning endpoints are in OpenAPI spec
    adaptive_endpoints = [
        "/api/v1/adaptive-learning/apply-assessment",
        "/api/v1/adaptive-learning/create-adaptive-path",
        "/api/v1/adaptive-learning/track-completion",
        "/api/v1/adaptive-learning/enrollment/{enrollment_id}/adaptive-info",
        "/api/v1/adaptive-learning/enrollment/{enrollment_id}/accept-adjustment",
    ]

    for endpoint in adaptive_endpoints:
        assert endpoint in paths, f"Endpoint {endpoint} not in OpenAPI spec"
        print(f"✅ Swagger docs include: {endpoint}")

    print("\n✅ All adaptive learning endpoints are documented in Swagger")


@pytest.mark.asyncio
async def test_auth_required(client):
    """Test that endpoints require authentication"""
    # Try without auth header
    response = await client.post(
        "/api/v1/adaptive-learning/apply-assessment",
        json={}
    )

    # Should return 401 Unauthorized
    assert response.status_code == 401
    print("\n✅ Authentication is required")


@pytest.mark.asyncio
async def test_get_adaptive_info_endpoint(client, test_users, test_enrollment):
    """Test GET adaptive info endpoint"""
    student = test_users["student1"]
    headers = {"Authorization": f"Bearer {student['token']}"}
    enrollment_id = test_enrollment["enrollment_id"]

    response = await client.get(
        f"/api/v1/adaptive-learning/enrollment/{enrollment_id}/adaptive-info",
        headers=headers
    )

    # Should return 200 with data
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data
    print(f"\n✅ Get adaptive info works")
    print(f"   Adaptive enabled: {data['data'].get('adaptive_learning_enabled', False)}")


if __name__ == "__main__":
    print("Run with: pytest tests/test_17_adaptive_learning_simple.py -v -s")

