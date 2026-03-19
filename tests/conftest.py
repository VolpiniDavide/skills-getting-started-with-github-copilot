"""Pytest configuration and shared fixtures for FastAPI tests."""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture providing TestClient for making HTTP requests to the FastAPI app.
    
    Returns:
        TestClient: A test client for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture to reset activities to their initial state after each test.
    
    This ensures test isolation by saving the activities state before the test
    and restoring it afterwards, preventing test pollution.
    
    Yields:
        None
    """
    # Arrange: Save the original activities state
    original = activities.copy()
    
    # Act: Run the test
    yield
    
    # Assert/Cleanup: Restore the original state
    activities.clear()
    activities.update(original)
