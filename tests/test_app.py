import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "description" in data["Basketball Team"]
    assert "participants" in data["Basketball Team"]


def test_signup_success():
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    assert "Signed up test@example.com for Basketball Team" == response.json()["message"]


def test_signup_already_signed():
    # First signup
    client.post("/activities/Tennis%20Club/signup?email=test2@example.com")
    # Second attempt
    response = client.post("/activities/Tennis%20Club/signup?email=test2@example.com")
    assert response.status_code == 400
    assert "Student already signed up for this activity" == response.json()["detail"]


def test_signup_activity_full():
    # Fill up an activity with small max_participants
    activity = "Tennis Club"  # max 10
    for i in range(8):  # Already has 1, so add 8 more to reach 9, then 10th will fail
        client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email=fill{i}@example.com")
    # Now try to add one more
    response = client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email=fill10@example.com")
    assert response.status_code == 400
    assert "Activity is full" == response.json()["detail"]


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    assert "Activity not found" == response.json()["detail"]


def test_unregister_success():
    # First signup
    client.post("/activities/Drama%20Club/signup?email=test3@example.com")
    # Then unregister
    response = client.delete("/activities/Drama%20Club/signup?email=test3@example.com")
    assert response.status_code == 200
    assert "Unregistered test3@example.com from Drama Club" == response.json()["message"]


def test_unregister_not_signed():
    response = client.delete("/activities/Drama%20Club/signup?email=notsigned@example.com")
    assert response.status_code == 400
    assert "Student not signed up for this activity" == response.json()["detail"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    assert "Activity not found" == response.json()["detail"]


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200  # RedirectResponse, but TestClient follows redirects
    # Since it redirects to /static/index.html, but static is mounted, it should work
    # Actually, TestClient might not serve static files, but since it's redirect, and we don't have index.html in test, perhaps skip or check status.
    # For simplicity, assert it's a redirect
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307  # Redirect