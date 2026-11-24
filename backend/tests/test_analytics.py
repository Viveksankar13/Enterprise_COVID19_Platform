import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.authentication.jwt import hash_password, create_jwt_token
from app.models.user import User, Role
from app.models.country import Country
from app.models.daily_metric import DailyMetric
from datetime import date


@pytest.fixture
async def auth_headers(db_session: AsyncSession) -> dict[str, str]:
    """
    Seeds a test admin user and returns authorization headers.
    """
    # Create Admin Role
    role = Role(
        role_id=1,
        name="admin",
        description="System Administrator",
        is_active=True
    )
    db_session.add(role)
    await db_session.flush()

    # Create User
    user = User(
        email="admin_tester@covidanalytics.com",
        username="admin_tester",
        password_hash=hash_password("admin_pass"),
        role_id=1,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    # Generate token
    token = create_jwt_token(data={"sub": "admin_tester"}, token_type="access")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_countries_authenticated(client: AsyncClient, db_session: AsyncSession, auth_headers: dict[str, str]):
    """
    Seeds country metadata, calls list countries, and asserts outputs.
    """
    # Seed Countries
    country1 = Country(
        iso_code="TST",
        continent="Test Continent",
        location="Test Land",
        income_group="High income",
        is_aggregate=False,
        is_active=True,
        data_source="OWID"
    )
    db_session.add(country1)
    await db_session.commit()

    response = await client.get("/api/v1/countries", headers=auth_headers)
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) >= 1
    assert res_data[0]["iso_code"] == "TST"
    assert res_data[0]["location"] == "Test Land"


@pytest.mark.asyncio
async def test_get_historical_trends_unauthenticated(client: AsyncClient):
    """
    Verifies that calling analytics endpoints without authorization headers fails.
    """
    response = await client.get("/api/v1/analytics/trends/historical?iso_code=USA")
    assert response.status_code == 401
