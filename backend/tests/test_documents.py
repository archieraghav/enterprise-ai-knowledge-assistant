import io

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "securepass123",
            "full_name": "Doc Tester",
            "organization_name": "Doc Test Org",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "securepass123"},
    )
    return login_response.json()["access_token"]


@pytest.mark.asyncio
async def test_upload_document_success(client: AsyncClient) -> None:
    token = await _register_and_login(client, "upload1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("report.txt", io.BytesIO(b"Some report content"), "text/plain")}
    response = await client.post("/api/v1/documents/upload", headers=headers, files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "report.txt"
    assert body["file_type"] == "txt"
    assert body["status"] == "uploaded"


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_file_type(client: AsyncClient) -> None:
    token = await _register_and_login(client, "upload2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("malware.exe", io.BytesIO(b"fake binary"), "application/octet-stream")}
    response = await client.post("/api/v1/documents/upload", headers=headers, files=files)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file(client: AsyncClient) -> None:
    token = await _register_and_login(client, "upload3@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    oversized_content = b"x" * (26 * 1024 * 1024)  # 26MB, exceeds 25MB default limit
    files = {"file": ("big.txt", io.BytesIO(oversized_content), "text/plain")}
    response = await client.post("/api/v1/documents/upload", headers=headers, files=files)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_documents_scoped_to_organization(client: AsyncClient) -> None:
    token_a = await _register_and_login(client, "orga@example.com")
    token_b = await _register_and_login(client, "orgb@example.com")

    files = {"file": ("only_a.txt", io.BytesIO(b"belongs to org A"), "text/plain")}
    await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files=files,
    )

    response_b = await client.get(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response_b.status_code == 200
    assert response_b.json()["total"] == 0

    response_a = await client.get(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert response_a.json()["total"] == 1


@pytest.mark.asyncio
async def test_delete_document_soft_deletes(client: AsyncClient) -> None:
    token = await _register_and_login(client, "upload4@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("to_delete.txt", io.BytesIO(b"temporary content"), "text/plain")}
    upload_response = await client.post("/api/v1/documents/upload", headers=headers, files=files)
    document_id = upload_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/documents/{document_id}", headers=headers)
    assert delete_response.status_code == 204

    list_response = await client.get("/api/v1/documents", headers=headers)
    assert list_response.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_nonexistent_document_returns_404(client: AsyncClient) -> None:
    token = await _register_and_login(client, "upload5@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/documents/{fake_id}", headers=headers)
    assert response.status_code == 404