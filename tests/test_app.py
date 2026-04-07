"""
Tests for the Mergington High School Activities API.
Uses AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest


def test_get_activities(client, sample_activity):
    """Test GET /activities returns all activities."""
    # Arrange
    expected_keys = ["Chess Club", "Programming Class", "Gym Class", "Soccer Team",
                     "Basketball Club", "Drama Club", "Art Workshop", "Robotics Club", "Science Olympiad"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9
    for key in expected_keys:
        assert key in data
        assert "description" in data[key]
        assert "schedule" in data[key]
        assert "max_participants" in data[key]
        assert "participants" in data[key]
        assert isinstance(data[key]["participants"], list)


def test_get_root_redirect(client):
    """Test GET / redirects to static HTML."""
    # Arrange
    # No special setup needed

    # Act
    response = client.get("/", allow_redirects=False)

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_signup_valid(client, test_email):
    """Test POST /activities/{name}/signup with valid data."""
    # Arrange
    activity_name = "Chess Club"
    initial_response = client.get("/activities")
    initial_participants = len(initial_response.json()[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]
    assert activity_name in data["message"]

    # Verify participant was added
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    assert len(updated_participants) == initial_participants + 1
    assert test_email in updated_participants


def test_signup_duplicate(client, test_email):
    """Test POST /activities/{name}/signup with duplicate email."""
    # Arrange
    activity_name = "Chess Club"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={test_email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity(client, test_email):
    """Test POST /activities/{name}/signup with non-existent activity."""
    # Arrange
    invalid_activity = "NonExistent Club"

    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={test_email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_valid(client, test_email):
    """Test DELETE /activities/{name}/unregister with valid data."""
    # Arrange
    activity_name = "Programming Class"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={test_email}")
    initial_response = client.get("/activities")
    initial_participants = len(initial_response.json()[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]
    assert activity_name in data["message"]

    # Verify participant was removed
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    assert len(updated_participants) == initial_participants - 1
    assert test_email not in updated_participants


def test_unregister_not_signed_up(client, test_email):
    """Test DELETE /activities/{name}/unregister when email not signed up."""
    # Arrange
    activity_name = "Gym Class"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_unregister_invalid_activity(client, test_email):
    """Test DELETE /activities/{name}/unregister with non-existent activity."""
    # Arrange
    invalid_activity = "Invalid Club"

    # Act
    response = client.delete(f"/activities/{invalid_activity}/unregister?email={test_email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]