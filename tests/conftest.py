import os
from dotenv import load_dotenv
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database.schema import Base, Users, URL
from database.db import get_db
from dependencies.context import current_user_context

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=True,
)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

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

@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

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