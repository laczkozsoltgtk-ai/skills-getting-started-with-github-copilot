import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data, dict)
    assert data["Gym Class"]["max_participants"] == 30


def test_signup_for_activity_succeeds():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity_returns_404():
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_when_already_signed_up_returns_400():
    email = "john@mergington.edu"
    response = client.post("/activities/Gym%20Class/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_succeeds():
    email = "chloe@mergington.edu"
    response = client.delete(f"/activities/Drama%20Club/participants/{email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Drama Club"}
    assert email not in activities["Drama Club"]["participants"]


def test_remove_participant_from_nonexistent_activity_returns_404():
    response = client.delete("/activities/Unknown%20Club/participants/student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_nonexistent_participant_returns_404():
    response = client.delete("/activities/Tennis%20Club/participants/notregistered@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
