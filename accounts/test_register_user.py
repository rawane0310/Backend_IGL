import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user():
    # Create an admin user for authentication
    return User.objects.create_user(email='admin@example.com', password='adminpassword', role='admin')

@pytest.fixture
def valid_user_data():
    return {
        'email': 'testuser@example.com',
        'password': 'testpassword123',
        'role': 'user',  # Adjust this based on your role setup
    }

def test_settings_loaded():
    assert hasattr(settings, 'REST_FRAMEWORK'), "REST_FRAMEWORK is not configured."


    
@pytest.mark.django_db
def test_register_user_success(api_client, admin_user, valid_user_data):
    # Authenticate as admin
    api_client.force_authenticate(user=admin_user)

    # Send the POST request
    response = api_client.post('/accounts/register/', valid_user_data, format='json')

    # Check if the response status is 201 Created
    assert response.status_code == status.HTTP_201_CREATED

    # Check if the user data is returned
    assert response.data['email'] == valid_user_data['email']

    # Check if the user is created in the database
    user = User.objects.get(email=valid_user_data['email'])
    assert user.email == valid_user_data['email']
    assert user.check_password(valid_user_data['password'])  # Check if the password is hashed

@pytest.mark.django_db
def test_register_user_failure_missing_email(api_client, admin_user):
    # Authenticate as admin
    api_client.force_authenticate(user=admin_user)

    # Test with missing email
    response = api_client.post('/accounts/register/', {'password': 'testpassword123'}, format='json')

    # Check if the response status is 400 Bad Request
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check if the response contains the correct error for missing email
    assert 'email' in response.data, f"Expected 'email' error, but got {response.data}"

@pytest.mark.django_db
def test_register_user_failure_missing_password(api_client, admin_user):
    # Authenticate as admin
    api_client.force_authenticate(user=admin_user)

    # Test with missing password
    response = api_client.post('/accounts/register/', {'email': 'test@example.com'}, format='json')

    # Check if the response status is 400 Bad Request
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check if the response contains the correct error for missing password
    assert 'password' in response.data, f"Expected 'password' error, but got {response.data}"
