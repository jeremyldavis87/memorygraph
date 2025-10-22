import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.note import Note
from app.models.category import Category
from app.models.entity import Entity
from app.utils.security import get_password_hash

# Test database - use PostgreSQL in CI, SQLite locally
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgresql://"):
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after test - only drop tables, don't recreate
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(setup_database):
    db = TestingSessionLocal()
    try:
        # Clean up any existing test user first
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("testpassword"),
            full_name="Test User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        yield user
    finally:
        # Clean up
        try:
            db.delete(user)
            db.commit()
        except:
            pass
        db.close()
