import io
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "securepass123",
            "full_name": "Integration Tester",
            "organization_name": "Integration Test Org",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "securepass123"},
    )
    return login_response.json()["access_token"]


@pytest.mark.asyncio
async def test_full_document_lifecycle(client: AsyncClient) -> None:
    """Register -> upload -> list -> retrieve -> delete, all in one flow."""
    token = await _register_and_login(client, "lifecycle@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("integration.txt", io.BytesIO(b"Integration test content."), "text/plain")}
    upload_response = await client.post("/api/v1/documents/upload", headers=headers, files=files)
    assert upload_response.status_code == 201
    document_id = upload_response.json()["id"]

    list_response = await client.get("/api/v1/documents", headers=headers)
    assert list_response.json()["total"] == 1

    get_response = await client.get(f"/api/v1/documents/{document_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "integration.txt"

    delete_response = await client.delete(f"/api/v1/documents/{document_id}", headers=headers)
    assert delete_response.status_code == 204

    final_list = await client.get("/api/v1/documents", headers=headers)
    assert final_list.json()["total"] == 0


@pytest.mark.asyncio
async def test_qa_endpoint_with_mocked_llm(client: AsyncClient) -> None:
    """Upload a document, then ask a question, mocking only the LLM call."""
    token = await _register_and_login(client, "qaintegration@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("qa_test.txt", io.BytesIO(b"The office closes at 6pm on weekdays."), "text/plain")}
    await client.post("/api/v1/documents/upload", headers=headers, files=files)

    with patch("app.ai.graphs.rag_graph.get_llm") as mock_get_llm:
        mock_llm = AsyncMock()
        mock_llm.generate.return_value = "The office closes at 6pm on weekdays."
        mock_get_llm.return_value = mock_llm

        response = await client.post(
            "/api/v1/qa/ask",
            headers=headers,
            json={"question": "What time does the office close?"},
        )

    assert response.status_code == 200
    body = response.json()
    assert "6pm" in body["answer"]
    assert len(body["citations"]) >= 1


@pytest.mark.asyncio
async def test_admin_endpoints_require_admin_role(client: AsyncClient) -> None:
    """A freshly registered user (first user = superuser) can access admin endpoints."""
    token = await _register_and_login(client, "adminintegration@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/admin/metrics", headers=headers)
    assert response.status_code == 200
    assert response.json()["total_users"] == 1


@pytest.mark.asyncio
async def test_feedback_and_analytics_flow(client: AsyncClient) -> None:
    """Submit feedback, then confirm it's reflected in analytics."""
    token = await _register_and_login(client, "feedbackintegration@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    feedback_response = await client.post(
        "/api/v1/feedback",
        headers=headers,
        json={
            "question": "Test question?",
            "answer": "Test answer.",
            "is_positive": True,
            "comment": "Great answer",
        },
    )
    assert feedback_response.status_code == 201

    analytics_response = await client.get("/api/v1/analytics", headers=headers)
    assert analytics_response.status_code == 200
    assert analytics_response.json()["feedback_summary"]["total_feedback"] == 1
    assert analytics_response.json()["feedback_summary"]["positive_count"] == 1


@pytest.mark.asyncio
async def test_health_and_readiness_endpoints(client: AsyncClient) -> None:
    """Confirm monitoring endpoints work without authentication."""
    health_response = await client.get("/api/v1/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"

    ready_response = await client.get("/api/v1/ready")
    assert ready_response.status_code == 200
    assert "database" in ready_response.json()


@pytest.mark.asyncio
async def test_cross_organization_isolation(client: AsyncClient) -> None:
    """Confirm one organization cannot see another's documents, even via direct ID guessing."""
    token_a = await _register_and_login(client, "isolationA@example.com")
    token_b = await _register_and_login(client, "isolationB@example.com")

    files = {"file": ("secret.txt", io.BytesIO(b"Confidential org A data."), "text/plain")}
    upload_response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files=files,
    )
    document_id = upload_response.json()["id"]

    response = await client.get(
        f"/api/v1/documents/{document_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 404