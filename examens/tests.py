import pytest
from rest_framework import status
from datetime import date
from accounts.models import ExamenBiologique, Technician, DossierPatient
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()
       
@pytest.mark.django_db
class TestExamenBiologiqueAPI:

    @pytest.fixture
    def technician(self):
        return Technician.objects.create(name="Technician 1", role="technicien")

    @pytest.fixture
    def dossier_patient(self):
        return DossierPatient.objects.create(name="Patient 1", age=25)

    @pytest.fixture
    def examen_biologique(self, technician, dossier_patient):
        return ExamenBiologique.objects.create(
            date=date.today(),
            technicien=technician,
            laborantin=technician,
            description="Initial description",
            dossier_patient=dossier_patient
        )
    
    def test_create_examen_biologique(self, api_client, technician, dossier_patient):
        data = {
            "date": str(date.today()),
            "technicien": technician.id,
            "laborantin": technician.id,
            "description": "Test description",
            "dossier_patient": dossier_patient.id
        }

        response = api_client.post('/api/examen_biologique/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['description'] == "Test description"
        assert response.data['technicien'] == technician.id
        assert response.data['dossier_patient'] == dossier_patient.id

    def test_read_examen_biologique(self, api_client, examen_biologique):
        response = api_client.get(f'/api/examen_biologique/{examen_biologique.id}/', format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == "Initial description"

    def test_update_examen_biologique(self, api_client, examen_biologique):
        update_data = {
            "description": "Updated description"
        }
        response = api_client.patch(f'/api/examen_biologique/{examen_biologique.id}/', update_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == "Updated description"

    def test_delete_examen_biologique(self, api_client, examen_biologique):
        response = api_client.delete(f'/api/examen_biologique/{examen_biologique.id}/', format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Ensure the object is deleted from the database
        with pytest.raises(ExamenBiologique.DoesNotExist):
            ExamenBiologique.objects.get(id=examen_biologique.id)
