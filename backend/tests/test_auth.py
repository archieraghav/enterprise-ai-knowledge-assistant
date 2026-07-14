import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_creates_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "password": "securepass123",
            "full_name": "Alice Smith",
            "organization_name": "Test Org",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["full_name"] == "Alice Smith"
    assert body["is_superuser"] is True


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "email": "bob@example.com",
        "password": "securepass123",
        "full_name": "Bob Jones",
        "organization_name": "Another Org",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 422


@pytest.mark.asyncio
async def test_login_with_correct_credentials(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "carol@example.com",
            "password": "securepass123",
            "full_name": "Carol White",
            "organization_name": "Carol Org",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "carol@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dave@example.com",
            "password": "correctpass123",
            "full_name": "Dave Black",
            "organization_name": "Dave Org",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "dave@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_valid_token(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "erin@example.com",
            "password": "securepass123",
            "full_name": "Erin Green",
            "organization_name": "Erin Org",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "erin@example.com", "password": "securepass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "erin@example.com"