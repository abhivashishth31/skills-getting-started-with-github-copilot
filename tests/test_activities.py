import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a deep copy of original activities for resetting
original_activities = copy.deepcopy(activities)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities(client):
    """Test GET /activities returns all activities with correct structure"""
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Should have 9 activities

    # Verify structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success(client):
    """Test successful signup for an activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity}" == data["message"]
    assert email in activities[activity]["participants"]


def test_signup_already_registered(client):
    """Test signup when student is already registered"""
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already registered" in data["detail"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistentActivity"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]


def test_delete_participant_success(client):
    """Test successful removal of a participant"""
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Removed {email} from {activity}" == data["message"]
    assert email not in activities[activity]["participants"]


def test_delete_participant_not_found(client):
    """Test deletion of non-existent participant"""
    # Arrange
    email = "nonexistent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Participant not found" == data["detail"]


def test_delete_activity_not_found(client):
    """Test deletion from non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistentActivity"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]