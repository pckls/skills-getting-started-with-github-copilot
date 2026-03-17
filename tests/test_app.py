import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its original state after each test."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_all_activities():
    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert len(data) == len(app_module.activities)
    assert "Chess Club" in data


def test_get_activities_have_required_fields():
    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_participant_appears_in_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    data = client.get("/activities").json()
    assert email in data[activity_name]["participants"]


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = "test@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_signup_duplicate_returns_400():
    # Arrange — michael is already in Chess Club
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange — michael is already in Chess Club
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200


def test_unregister_participant_removed_from_activity():
    # Arrange — michael is already in Chess Club
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    data = client.get("/activities").json()
    assert email not in data[activity_name]["participants"]


def test_unregister_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = "test@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_unregister_not_signed_up_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "nothere@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
