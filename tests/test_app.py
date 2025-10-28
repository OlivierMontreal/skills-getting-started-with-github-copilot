from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_root():
    """Test that the root endpoint redirects to index.html"""
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307
    
def test_read_activities():
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Test structure of an activity
    activity = next(iter(activities.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    
    # Test successful signup
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify student was added
    activities = client.get("/activities").json()
    assert "newstudent@mergington.edu" in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test that a student cannot sign up twice"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/NonExistentClub/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    email = "tounregister@mergington.edu"
    
    # First sign up the student
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Test unregistration
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify student was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who isn't registered"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]