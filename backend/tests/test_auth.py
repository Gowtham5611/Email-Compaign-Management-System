import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_register_and_login():
    email = "testuser@example.com"
    password = "secretpassword123"

    # Register
    res = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": email,
        "password": password
    })
    assert res.status_code in (201, 400) # 201 or 400 if already exists

    # Login
    res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Me protected endpoint
    token = data["access_token"]
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["email"] == email

