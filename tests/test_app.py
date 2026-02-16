import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_and_unregister():
    activity = "Chess Club"
    email = "testuser@mergington.edu"
    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)
    # Signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    # Duplicate signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 400
    # Unregister
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]
    # Unregister non-existent
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert response.status_code == 404

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert response.status_code == 404

def test_signup_activity_full():
    activity = "Math Olympiad"
    # Fill up the activity
    activities[activity]["participants"] = [f"user{i}@mergington.edu" for i in range(activities[activity]["max_participants"])]
    response = client.post(f"/activities/{activity}/signup", params={"email": "overflow@mergington.edu"})
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()
    # Clean up
    activities[activity]["participants"] = []
