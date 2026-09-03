# import pytest


# @pytest.fixture
# def sample_user():
#     return {"id": 1, "name": "Ada Lovelace", "role": "admin"}


# def test_user_is_admin(sample_user):
#     assert sample_user["role"] == "admin"


# def test_user_has_name(sample_user):
#     assert sample_user["name"] == "Ada Lovelace"

import os

# IMPORTANT:
# Set test DB before importing application/database modules.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database.schema import Base, Users, URL
from database.db import get_db
from dependencies.context import current_user_context


# --------------------------------------------------
# TEST DATABASE
# --------------------------------------------------

TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=True,
)


# --------------------------------------------------
# CREATE TEST TABLES
# --------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


# --------------------------------------------------
# DATABASE SESSION
# --------------------------------------------------

@pytest.fixture
def db():
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()

        # Clean tables after every test
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())

        session.commit()
        session.close()


# --------------------------------------------------
# OVERRIDE FASTAPI DB
# --------------------------------------------------

@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# --------------------------------------------------
# TEST USER
# --------------------------------------------------

@pytest.fixture
def test_user(db):
    user = Users(
        username="pytest_user",
        email="pytest@example.com",
        hashed_password="test_password",
        user_role="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# --------------------------------------------------
# CURRENT USER CONTEXT
# --------------------------------------------------

@pytest.fixture
def authenticated_client(db, test_user):

    def override_current_user_context():
        return {
            "db": db,
            "current_user": test_user,
        }

    app.dependency_overrides[
        current_user_context
    ] = override_current_user_context

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# --------------------------------------------------
# CREATE URL DIRECTLY
# --------------------------------------------------

@pytest.fixture
def created_url(db, test_user):
    url = URL(
        url="https://example.com",
        short_link="TEST1",
        owner_id=test_user.userid,
        total_clicks=0,
    )

    db.add(url)
    db.commit()
    db.refresh(url)

    return url