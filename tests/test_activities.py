"""
API tests for the FastAPI activity management system.

Uses the AAA (Arrange-Act-Assert) pattern for test structure.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self):
        """
        Test that GET /activities returns all activities successfully.
        
        AAA Pattern:
        - Arrange: Create client (no special setup needed)
        - Act: Make GET request to /activities
        - Assert: Verify 200 status, correct structure, and all 9 activities present
        """
        # Arrange
        client = TestClient(app)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Tennis Team" in data
        assert "Basketball Club" in data
        assert "Art Studio" in data
        assert "Music Band" in data
        assert "Debate Society" in data
        assert "Science Club" in data

    def test_get_activities_response_structure(self):
        """
        Test that each activity has the correct response structure.
        
        AAA Pattern:
        - Arrange: Create client and get activities
        - Act: Retrieve activities data
        - Assert: Verify each activity has required fields
        """
        # Arrange
        client = TestClient(app)
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_details in activities_data.items():
            assert isinstance(activity_details, dict)
            assert set(activity_details.keys()) == required_fields
            assert isinstance(activity_details["description"], str)
            assert isinstance(activity_details["schedule"], str)
            assert isinstance(activity_details["max_participants"], int)
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, reset_activities):
        """
        Test successful signup for an activity.
        
        AAA Pattern:
        - Arrange: Set up test data (activity name and new email)
        - Act: POST request to signup endpoint
        - Assert: Verify 200 status, response message, and participant added
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
        assert new_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_multiple_activities_same_email(self, reset_activities):
        """
        Test that the same email can sign up for multiple activities.
        
        AAA Pattern:
        - Arrange: Choose an email and two different activities
        - Act: Sign up for first activity, then second activity
        - Assert: Verify both signups successful and email in both activities
        """
        # Arrange
        client = TestClient(app)
        email = "testuser@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act
        response1 = client.post(f"/activities/{activity1}/signup?email={email}")
        response2 = client.post(f"/activities/{activity2}/signup?email={email}")
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]

    def test_signup_already_registered(self, reset_activities):
        """
        Test that signing up a student already registered for an activity fails.
        
        AAA Pattern:
        - Arrange: Use an email already registered for the activity
        - Act: Attempt to signup with the same email
        - Assert: Verify 400 status and "Already signed up" error message
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Already signed up for this activity"

    def test_signup_nonexistent_activity(self, reset_activities):
        """
        Test that signing up for a non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Use an activity name that doesn't exist
        - Act: Attempt to signup for the non-existent activity
        - Assert: Verify 404 status and "Activity not found" error message
        """
        # Arrange
        client = TestClient(app)
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_activity_with_special_characters(self, reset_activities):
        """
        Test signup with email containing special characters.
        
        AAA Pattern:
        - Arrange: Use an email with dots, hyphens, and valid special chars
        - Act: Signup with the special character email
        - Assert: Verify successful signup and email correctly stored
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Chess Club"
        special_email = "test.student-2024@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={special_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert special_email in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_from_activity_success(self, reset_activities):
        """
        Test successful unregistration from an activity.
        
        AAA Pattern:
        - Arrange: Use an email already registered for the activity
        - Act: DELETE request to unregister
        - Assert: Verify 200 status, response message, and participant removed
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"  # Already in Chess Club
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email_to_remove} from {activity_name}"
        assert email_to_remove not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_not_registered(self, reset_activities):
        """
        Test that unregistering a student not registered fails.
        
        AAA Pattern:
        - Arrange: Use an email not registered for the activity
        - Act: Attempt to unregister the non-registered email
        - Assert: Verify 400 status and "Not registered" error message
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Chess Club"
        unregistered_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={unregistered_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Not registered for this activity"

    def test_unregister_nonexistent_activity(self, reset_activities):
        """
        Test that unregistering from a non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Use an activity name that doesn't exist
        - Act: Attempt to unregister from the non-existent activity
        - Assert: Verify 404 status and "Activity not found" error message
        """
        # Arrange
        client = TestClient(app)
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestDataIntegrity:
    """Tests to verify data integrity across multiple operations."""

    def test_participant_list_updates_correctly(self, reset_activities):
        """
        Test that participant lists update correctly with multiple operations.
        
        AAA Pattern:
        - Arrange: Choose an activity and multiple emails
        - Act: Sign up multiple times, verify list state
        - Assert: Verify list size, order preservation, no duplicates
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Tennis Team"
        emails = ["new1@mergington.edu", "new2@mergington.edu", "new3@mergington.edu"]
        
        # Act & Assert - Sign up new participants
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Assert - Verify all emails are in the list
        final_participants = activities[activity_name]["participants"]
        for email in emails:
            assert email in final_participants
        
        # Assert - Verify no duplicates
        assert len(final_participants) == len(set(final_participants))

    def test_state_persists_across_requests(self, reset_activities):
        """
        Test that signup state persists across subsequent requests.
        
        AAA Pattern:
        - Arrange: Sign up a participant
        - Act: Make a GET request to fetch activities
        - Assert: Verify the participant still appears in the activity
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Art Studio"
        new_email = "artist@mergington.edu"
        
        # Act - Sign up
        response1 = client.post(f"/activities/{activity_name}/signup?email={new_email}")
        assert response1.status_code == 200
        
        # Act - Fetch activities to verify state persists
        response2 = client.get("/activities")
        
        # Assert
        assert response2.status_code == 200
        activities_data = response2.json()
        assert new_email in activities_data[activity_name]["participants"]

    def test_unregister_state_persists_across_requests(self, reset_activities):
        """
        Test that unregister state persists across subsequent requests.
        
        AAA Pattern:
        - Arrange: Use a participant already registered
        - Act: Unregister, then GET activities
        - Assert: Verify participant no longer in activity
        """
        # Arrange
        client = TestClient(app)
        activity_name = "Gym Class"
        email_to_remove = "john@mergington.edu"  # Already registered
        
        # Act - Unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister?email={email_to_remove}"
        )
        assert response1.status_code == 200
        
        # Act - Fetch activities to verify state persists
        response2 = client.get("/activities")
        
        # Assert
        assert response2.status_code == 200
        activities_data = response2.json()
        assert email_to_remove not in activities_data[activity_name]["participants"]
