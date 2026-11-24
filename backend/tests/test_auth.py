import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.authentication.jwt import (
    hash_password,
    verify_password,
    create_jwt_token,
    decode_jwt_token,
)
from app.models.user import User, Role


def test_password_hashing():
    """
    Tests password encryption and verification logic.
    """
    pw = "super_secure_password"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_token_sign_and_verify():
    """
    Tests signing and decoding JSON Web Tokens.
    """
    data = {"sub": "test_analyst"}
    token = create_jwt_token(data, token_type="access")
    payload = decode_jwt_token(token)
    assert payload.get("sub") == "test_analyst"
    assert payload.get("type") == "access"


@pytest.mark.asyncio
async def test_api_login_incorrect_credentials(client: AsyncClient):
    """
    Verifies that calling the login API with bad credentials fails.
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "fake_user", "password": "bad_password"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json().get("detail")


@pytest.mark.asyncio
async def test_api_login_success(client: AsyncClient, db_session: AsyncSession):
    """
    Seeds a mock role and user, and tests successful authentication.
    """
    # 1. Seed Role
    role = Role(
        role_id=10,
        name="viewer",
        description="Read-only viewer",
        is_active=True
    )
    db_session.add(role)
    await db_session.flush()

    # 2. Seed User
    user = User(
        email="test_user@covidanalytics.com",
        username="test_user",
        password_hash=hash_password("admin_test_pass"),
        role_id=10,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    # 3. Call API Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "test_user", "password": "admin_test_pass"}
    )
    
    assert response.status_code == 200
    res_data = response.json()
    assert "access_token" in res_data
    assert res_data["token_type"] == "bearer"
    assert res_data["user"]["username"] == "test_user"
