# app/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
import uuid
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.main import app
from app.db.models.user import User, Role
from app.core.security import get_password_hash, create_access_token
from app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database setup fixture
@pytest.fixture(scope="function")
def test_db():
    # Create in-memory SQLite engine
    engine = create_engine("sqlite:///:memory:")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    # Create a test session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after each test
        Base.metadata.drop_all(bind=engine)

# Create a test client with test database
@pytest.fixture(scope="module")
def test_app():
    # Create a new FastAPI app instance for testing
    from app.main import app
    
    # Create in-memory SQLite engine
    engine = create_engine("sqlite:///:memory:")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    # Define get_db function
    def get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Override the get_db dependency
    app.dependency_overrides[get_db] = get_db
    
    yield TestClient(app)
    
    # Clean up
    app.dependency_overrides = {}

# Mock data
test_user_data = {
    "email": "test@example.com",
    "password": "Password123!"
}

test_admin_data = {
    "email": "admin@example.com",
    "password": "AdminPass123!",
    "role": "admin"
}

# Test user object
@pytest.fixture
def test_user():
    user = User(
        id=str(uuid.uuid4()),
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        is_active=True,
        role="user",
        created_at=datetime.utcnow()
    )
    return user

# Auth header fixture
@pytest.fixture
def auth_header(test_user):
    token = create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {token}"}

# Test admin user object
@pytest.fixture
def test_admin():
    admin = User(
        id=str(uuid.uuid4()),
        email=test_admin_data["email"],
        hashed_password=get_password_hash(test_admin_data["password"]),
        is_active=True,
        role="admin",
        created_at=datetime.utcnow()
    )
    return admin

# Admin auth header fixture
@pytest.fixture
def admin_auth_header(test_admin):
    token = create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {token}"}

# Test role object
@pytest.fixture
def test_role():
    return Role(
        id=str(uuid.uuid4()),
        name="test_role",
        description="Test role description",
        permissions=["read", "write"],
        created_at=datetime.utcnow()
    )

class TestRegistration:
    def test_register_user_success(self, test_app, test_db):
        # Generate unique test data
        unique_email = f"test{uuid.uuid4()}@example.com"
        test_data = {
            "email": unique_email,
            "password": "Password123!"
        }
        
        # Make the API request
        response = test_app.post("/auth/register", json=test_data)
        
        # Assert the response
        assert response.status_code == 200, f"Response: {response.json()}"
        assert response.json()["email"] == unique_email
        assert "id" in response.json()
        assert response.json()["role"] == "user"
        assert response.json()["is_active"] == True
        assert "created_at" in response.json()

    def test_register_existing_user(self, test_app, test_db, test_user):
        # Make the API request with existing user's email
        response = test_app.post("/auth/register", json={
            "email": test_user.email,
            "password": "Password123!"
        })
        
        # Assert the response
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]


class TestLogin:
    def test_login_success(self, test_app, test_db, test_user):
        # Add user to database
        test_db.add(test_user)
        test_db.commit()
        
        # Create form data for login
        form_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        # Make the API request
        response = test_app.post("/auth/login", data=form_data)
        
        # Assert the response
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_invalid_email(self, test_app, test_db):
        # Create form data for login with invalid email
        form_data = {
            "username": "invalid@example.com",
            "password": "Password123!"
        }
        
        # Make the API request
        response = test_app.post("/auth/login", data=form_data)
        
        # Assert the response
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_invalid_password(self, test_app, test_db, test_user):
        # Add user to database
        test_db.add(test_user)
        test_db.commit()
        
        # Create form data for login with wrong password
        form_data = {
            "username": test_user_data["email"],
            "password": "WrongPassword"
        }
        
        # Make the API request
        response = test_app.post("/auth/login", data=form_data)
        
        # Assert the response
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]