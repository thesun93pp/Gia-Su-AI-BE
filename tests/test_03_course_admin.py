
import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_schema
from tests.test_variables import TestVariables

class TestAdminCourseManagement:
    """Test cases for Admin Course Management (Section 4.2)."""

    @pytest.mark.asyncio
    async def test_create_module_with_prerequisites_and_resources(
        self, client: AsyncClient, test_vars: TestVariables
    ):
        """Test creating a module with prerequisites and resources."""
        admin_headers = test_vars.get_headers("admin")
        
        # First, create a course to add a module to
        course_payload = {
            "title": "Course for Module Test",
            "description": "A test course for modules.",
            "category": "Science",
            "level": "Intermediate",
            "status": "published",
        }
        
        response = await client.post("/api/v1/admin/courses/", headers=admin_headers, json=course_payload)
        assert response.status_code == 200
        course_data = response.json()
        course_id = course_data["course_id"]
        test_vars.set("course_id_for_module_test", course_id)

        # Now, create the module with prerequisites and resources
        module_payload = {
            "title": "Module with Prerequisites",
            "description": "A module with special requirements.",
            "order": 1,
            "difficulty": "medium",
            "estimated_hours": 3,
            "learning_outcomes": [{"description": "Master advanced topics", "skill_tag": "advanced"}],
            "prerequisites": ["Basic algebra"],
            "resource": [{"type": "pdf", "title": "Advanced Reading", "is_dowloadable": True, "url": "http://example.com/reading.pdf"}]
        }

        response = await client.post(f"/api/v1/admin/courses/{course_id}/modules/", headers=admin_headers, json=module_payload)
        
        assert response.status_code == 200
        data = response.json()

        # Check response schema
        required_fields = ["course_id", "title", "description", "order", "difficulty", "estimated_hours", "learning_outcomes", "prerequisites", "resource", "message"]
        assert_response_schema(data, required_fields)

        # Check values
        assert data["title"] == module_payload["title"]
        assert data["prerequisites"] == module_payload["prerequisites"]
        assert len(data["resource"]) == 1
        assert data["resource"][0]["title"] == "Advanced Reading"
        
        # Verify by fetching the course detail
        response = await client.get(f"/api/v1/admin/courses/{course_id}", headers=admin_headers)
        assert response.status_code == 200
        course_detail = response.json()
        
        assert len(course_detail["modules"]) == 1
        module_summary = course_detail["modules"][0]
        assert module_summary["title"] == module_payload["title"]

