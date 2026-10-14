"""End-to-end tests for the auth flow, via the HTTP layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import User
from app.security import verify_password
from tests.conftest import TEST_USER


async def test_register_creates_user_logs_in_and_hashes_password(
    client, session_factory: async_sessionmaker[AsyncSession]
):
    response = await client.post("/register", data=TEST_USER)

    assert response.status_code == 303
    assert response.headers["location"] == "/notes"
    assert "notes_session" in client.cookies

    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.email == TEST_USER["email"]))

    assert user is not None
    assert user.hashed_password != TEST_USER["password"]
    assert verify_password(TEST_USER["password"], user.hashed_password)


async def test_register_rejects_duplicate_email(client):
    await client.post("/register", data=TEST_USER)

    response = await client.post("/register", data=TEST_USER)

    assert response.status_code == 200
    assert "already registered" in response.text


async def test_login_with_correct_password(client):
    await client.post("/register", data=TEST_USER)
    await client.post("/logout")

    response = await client.post("/login", data=TEST_USER)

    assert response.status_code == 303
    assert response.headers["location"] == "/notes"


async def test_login_with_wrong_password(client):
    await client.post("/register", data=TEST_USER)
    await client.post("/logout")

    response = await client.post("/login", data={"email": TEST_USER["email"], "password": "wrong"})

    assert response.status_code == 200
    assert "Invalid email or password" in response.text


async def test_login_with_unknown_email(client):
    response = await client.post(
        "/login", data={"email": "nobody@example.com", "password": "whatever"}
    )

    assert response.status_code == 200
    assert "Invalid email or password" in response.text


async def test_logout_clears_the_session(auth_client):
    response = await auth_client.post("/logout")

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    # Logged out again -> the login page renders instead of redirecting.
    login_page = await auth_client.get("/login")
    assert login_page.status_code == 200


async def test_login_page_redirects_when_authenticated(auth_client):
    response = await auth_client.get("/login")

    assert response.status_code == 303
    assert response.headers["location"] == "/notes"


async def test_home_redirects_to_login_when_anonymous(client):
    response = await client.get("/")

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


async def test_home_redirects_to_notes_when_authenticated(auth_client):
    response = await auth_client.get("/")

    assert response.status_code == 303
    assert response.headers["location"] == "/notes"
