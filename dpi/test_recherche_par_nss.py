import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import Patient, Technician, User, DossierPatient
import json
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


# Fixture to create a patient, technician, and dossier_patient
@pytest.fixture
def create_patient_and_technician():
    # Create a user for technician (medecin)
    technician_user = User.objects.create_user(email='doctor@example.com', password='password123', role='medecin')

    # Create a Technician and associate it with the user
    technician = Technician.objects.create(
        user=technician_user,  # Associate the technician with the created user
        nom='Amira',
        prenom='Mmr',
        role='medecin',
        specialite='Cardiology',
        outils={"stethoscope": True, "ECG_machine": False}  # JSON data for tools
    )

    
    # Create a user for patient
    patient_user = User.objects.create_user(email='patient@example.com', password='password123', role='patient')

    # Create a Patient and associate it with the user and the medecin
    patient = Patient.objects.create(
        user=patient_user,  # Associate the patient with the created user
        nom='Rofieda',
        prenom='Mmr',
        date_naissance='2005-09-13',
        adresse='kouba',
        tel='0123456789',
        mutuelle='Mutuelle A',
        medecin_traitant=technician,
        personne_a_contacter='Contact Person',
        nss='123456789012345'
    )

    # Create a DossierPatient associated with the patient
    qr_data = {"Patient": patient.nom, "ID": patient.id}
    qr_data_str = json.dumps(qr_data)
    qr_image = qrcode.make(qr_data_str)
    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)
    qr_file = ContentFile(buffer.read(), name=f"qr_patient_{patient.id}.png")
    buffer.close()
    
    dossier_patient = DossierPatient.objects.create(patient=patient, qr=qr_file)

    return patient, technician, dossier_patient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_search_patient_by_nss_success(api_client, create_patient_and_technician):
    patient, technician, dossier_patient = create_patient_and_technician

    # Login to get the access token for the patient
    login_data = {'email': 'patient@example.com', 'password': 'password123'}
    login_response = api_client.post('/accounts/login/', login_data, format='json')
    
    # Extract the access token from the login response
    access_token = login_response.data.get('access')

    # Set the authorization header with the access token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Send GET request to search the patient by NSS
    response = api_client.get(f'/dpi/search_by_nss/?nss={patient.nss}', format='json')

    # Assert the response status code is 200 (OK)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_search_patient_by_nss_missing_nss(api_client, create_patient_and_technician):
    # Create a patient and technician
    patient, technician, dossier_patient = create_patient_and_technician

    # Login to get the access token for the patient
    login_data = {'email': 'patient@example.com', 'password': 'password123'}
    login_response = api_client.post('/accounts/login/', login_data, format='json')

    # Extract the access token from the login response
    access_token = login_response.data.get('access')

    # Set the authorization header with the access token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Send GET request without NSS
    response = api_client.get('/dpi/search_by_nss/', format='json')

    # Check the response status code
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "NSS is required."  #  error message






@pytest.mark.django_db
def test_search_patient_by_nss_not_found(api_client, create_patient_and_technician):
    # Create a patient and dossier (but not login)
    patient, technician, dossier_patient = create_patient_and_technician

    # Login to get the access token for the patient
    login_data = {'email': 'patient@example.com', 'password': 'password123'}
    login_response = api_client.post('/accounts/login/', login_data, format='json')
    
    # Extract the access token from the login response
    access_token = login_response.data.get('access')

    # Set the authorization header with the access token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Send GET request with a non-existent NSS
    response = api_client.get('/dpi/search_by_nss/?nss=nonexistentnss', format='json')

    # Check the response status code
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == "Patient not found."



