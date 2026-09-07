import os

os.environ["DATABASE_URL"] = "mysql+pymysql://root:mysql@localhost:3306/test_url_db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database.schema import Base, Users, URL
from database.db import get_db
from dependencies.context import current_user_context
import operations.tasks as tasks

TEST_DATABASE_URL = "mysql+pymysql://root:mysql@localhost:3306/test_url_db"

test_engine = create_engine(
    TEST_DATABASE_URL,
   )

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=True,
)

@pytest.fixture
def db(monkeypatch):
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()

    monkeypatch.setattr(tasks, "SessionLocal", TestingSessionLocal)

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=test_engine)

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
        url="https://example.com/page",
        short_link="TEST1",
        owner_id=test_user.userid,
        total_clicks=0,
    )

    db.add(url)
    db.commit()
    db.refresh(url)

    return url

    