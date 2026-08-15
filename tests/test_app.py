"""API endpoint tests for Mergington High School Activities API"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirect(self, client):
        """
        Test that GET / redirects to /static/index.html
        
        Arrange: TestClient is ready
        Act: Make GET request to /
        Assert: Verify redirect status code and location header
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers.get("location", "")


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities(self, client):
        """
        Test that GET /activities returns all activities
        
        Arrange: Activities fixture contains sample data
        Act: Make GET request to /activities
        Assert: Verify response contains expected activities
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) > 0
    
    def test_get_activities_structure(self, client):
        """
        Test that activities have correct data structure
        
        Arrange: Activities fixture contains sample data
        Act: Make GET request to /activities and examine structure
        Assert: Verify each activity has required fields
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """
        Test successful signup for an activity
        
        Arrange: Activity exists with known participants
        Act: POST signup request with new email
        Assert: Verify success response and participant added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "netstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_email(self, client):
        """
        Test that duplicate signup is rejected
        
        Arrange: Activity has existing participant
        Act: POST signup request with already-registered email
        Assert: Verify error response and participant not duplicated
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
        assert len(activities[activity_name]["participants"]) == initial_count
    
    def test_signup_invalid_activity(self, client):
        """
        Test that signup to non-existent activity is rejected
        
        Arrange: Activity name does not exist
        Act: POST signup request to invalid activity
        Assert: Verify 404 error response
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRemoveEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_remove_success(self, client):
        """
        Test successful removal of participant from activity
        
        Arrange: Activity has existing participant
        Act: DELETE request with registered email
        Assert: Verify success response and participant removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_remove_not_signed_up(self, client):
        """
        Test that removing non-registered email is rejected
        
        Arrange: Activity does not have this participant
        Act: DELETE request with unregistered email
        Assert: Verify error response and no changes made
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"  # Not registered
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
        assert len(activities[activity_name]["participants"]) == initial_count
    
    def test_remove_invalid_activity(self, client):
        """
        Test that removal from non-existent activity is rejected
        
        Arrange: Activity name does not exist
        Act: DELETE request to invalid activity
        Assert: Verify 404 error response
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
