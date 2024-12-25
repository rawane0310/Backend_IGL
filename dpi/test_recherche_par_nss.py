import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Patient, Technician, User

# Fixture to create a user, technician and patient
@pytest.fixture
def create_patient_and_technician():
    # Create a user for technician (doctor)
    technician_user = User.objects.create_user(email='doctor@example.com', password='password123', role='medecin')

    # Create a Technician and associate it with the user
    technician = Technician.objects.create(
        user=technician_user,  # Associate the technician with the created user
        nom='Amira',
        prenom='Mmr',
        role='medecin',
        specialite='Cardiology',  
    )
    
    # Create a user for patient
    patient_user = User.objects.create_user(email='patient@example.com', password='password123', role='patient')

    # Create a Patient and associate it with the user and the technician (doctor)
    patient = Patient.objects.create(
        user=patient_user,  # Associate the patient with the created user
        nom='Jane',
        prenom='Smith',
        date_naissance='1990-01-01',
        adresse='123 Street',
        tel='0123456789',
        mutuelle='Mutuelle A',
        medecin_traitant=technician,
        personne_a_contacter='Contact Person',
        nss='123456789012345'
    )
    
    return patient, technician

@pytest.fixture
def api_client():
    return APIClient()

# Test when the NSS is provided correctly
@pytest.mark.django_db
def test_register_patient_by_nss_success(api_client, create_patient_and_technician):
    patient, technician = create_patient_and_technician
    
    # Send GET request to search  the patient by NSS
    response = api_client.get(f'/dpi/search_by_nss/?nss={patient.nss}', format='json')

    # Check the response status code if it's 200
    assert response.status_code == status.HTTP_200_OK

    # Check if the returned data contains the expected fields
    assert 'nom' in response.data
    assert 'prenom' in response.data
    assert 'medecin_traitant' in response.data
    assert 'nom' in response.data['medecin_traitant']  # Doctor's name
    assert 'prenom' in response.data['medecin_traitant']  # Doctor's surname

    # Verify the doctor’s name is correct
    assert response.data['medecin_traitant']['nom'] == technician.nom
    assert response.data['medecin_traitant']['prenom'] == technician.prenom

# Test when NSS is missing from the request
@pytest.mark.django_db
def test_register_patient_by_nss_missing_nss(api_client):
    # Send GET request without NSS
    response = api_client.get('/dpi/search_by_nss/', format='json')

    # Check the response status code
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Check if the response contains the correct error message
    assert response.data['detail'] == "NSS is required."

# Test when the patient is not found by NSS
@pytest.mark.django_db
def test_register_patient_by_nss_not_found(api_client):
    # Send GET request with a non-existent NSS
    response = api_client.get('/dpi/search_by_nss/?nss=nonexistentnss', format='json')

    # Check the response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Check if the response contains the correct error message
    assert response.data['detail'] == "Patient not found."

# Test for unexpected errors (e.g., invalid NSS format)
