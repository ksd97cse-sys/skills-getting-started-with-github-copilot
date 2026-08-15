"""Pytest configuration and fixtures for API tests"""
import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provides a TestClient with isolated activity data.
    
    This fixture uses a deep copy of the activities dict to ensure
    test isolation - changes made in one test don't affect other tests.
    """
    # Save original activities
    original_activities = copy.deepcopy(activities)
    
    # Yield the test client
    yield TestClient(app)
    
    # Restore original activities after test completes
    activities.clear()
    activities.update(original_activities)
