from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ExamenBiologique, Technician, DossierPatient
from datetime import date

class ExamenBiologiqueTests(APITestCase):

    def setUp(self):
        self.technician = Technician.objects.create(name="Technicien 1", role="Biologiste")
        self.dossier_patient = DossierPatient.objects.create(name="Patient 1", age=25)

    def test_create_examen_biologique(self):
        data = {
            "date": str(date.today()),
            "technicien": self.technician.id,
            "terminaison": "Analyse complète",
            "dossier_patient": self.dossier_patient.id,
        }

        response = self.client.post('/api/examen_biologique/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['terminaison'], "Analyse complète")
        self.assertEqual(response.data['technicien'], self.technician.id)
        self.assertEqual(response.data['dossier_patient'], self.dossier_patient.id)

class ResultatExamenTests(APITestCase):

    def setUp(self):
        self.technician = Technician.objects.create(name="Technicien 1", role="Biologiste")
        self.dossier_patient = DossierPatient.objects.create(name="Patient 1", age=25)
        self.examen = ExamenBiologique.objects.create(
            date=str(date.today()),
            technicien=self.technician,
            terminaison="Analyse complète",
            dossier_patient=self.dossier_patient
        )

    def test_create_resultat_examen(self):
        data = {
            "parametre": "Glycémie",
            "valeur": "100",
            "unite": "mg/dL",
            "commentaire": "Normal",
            "examen_biologique": self.examen.id
        }

        response = self.client.post('/api/resultat_examen/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['parametre'], "Glycémie")
        self.assertEqual(response.data['valeur'], "100")
        self.assertEqual(response.data['examen_biologique'], self.examen.id)

