from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import DossierPatient, Patient
from .serializers import DossierPatientSerializer , PatientSerializer
import qrcode

from django.shortcuts import get_object_or_404
import io
import base64

class DossierPatientCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            patient_id = request.data.get('patient')
            patient = Patient.objects.get(id=patient_id)

            # Vérifiez s'il existe déjà un dossier pour ce patient
            if DossierPatient.objects.filter(patient=patient).exists():
                return Response({"error": "Un dossier existe déjà pour ce patient."}, status=status.HTTP_400_BAD_REQUEST)

            # Génération du QR code
            qr_data = f"Patient: {patient.nom}, ID: {patient.id}"  # Ajoutez les infos nécessaires
            qr_image = qrcode.make(qr_data)
            buffer = io.BytesIO()
            qr_image.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()  # Encodage en base64
            buffer.close()

            # Création du dossier patient
            dossier = DossierPatient.objects.create(patient=patient, qr=qr_base64)
            serializer = DossierPatientSerializer(dossier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Patient.DoesNotExist:
            return Response({"error": "Patient introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SupprimerDpiAPIView(APIView):
    def delete(self, request, dpi_id):
        try:
            dpi = DossierPatient.objects.get(id=dpi_id)
        except DossierPatient.DoesNotExist:
            return Response(
                {'error': 'dpi introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        dpi.delete()
        return Response(
            {'message': 'dpi supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )
    

class ModifierDossierAPIView(APIView):
    

    def put(self, request, dpi_id):
        
        return self.update_dpi(request, dpi_id, partial=False)

    def patch(self, request, dpi_id):
        
        return self.update_dpi(request, dpi_id, partial=True)

    def update_dpi(self, request, dpi_id, partial):
        
        try:
            dpi = DossierPatient.objects.get(id=dpi_id)
        except DossierPatient.DoesNotExist:
            return Response(
                {'error': 'dpi  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DossierPatientSerializer(dpi, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
    




""""
class DossierPatientSearchView(APIView):
    def get(self, request, *args, **kwargs):
        # Get QR code content from the query parameters
        qr_code_content = request.GET.get('qr', None)
        
        if not qr_code_content:
            return Response({"detail": "QR code content is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Decode the QR code content
            decoded_content = base64.b64decode(qr_code_content).decode('utf-8').strip()
            
            # Check if the decoded content has exactly two parts (id and name)
            parts = decoded_content.split(' ')
            if len(parts) != 2:
                return Response({"detail": "Invalid QR code format. Expected 'patient_id patient_name'."}, status=status.HTTP_400_BAD_REQUEST)
            
            patient_id, patient_name = parts

            # Find the patient based on the decoded patient_id and patient_name
            patient = get_object_or_404(Patient, id=patient_id, nom=patient_name)
            
            # Get the DossierPatient associated with the patient
            dossier_patient = get_object_or_404(DossierPatient, patient=patient)
            
            # Serialize the patient and dossier details
            dossier_serializer = DossierPatientSerializer(dossier_patient)
            patient_serializer = PatientSerializer(patient)

            # Combine both serialized data
            response_data = {
                "dossier": dossier_serializer.data,
                "patient": patient_serializer.data,
            }

            return Response(response_data)
        
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

"""

class DossierPatientSearchView(APIView):
    def get(self, request, *args, **kwargs):
        # Get patient ID and name from the query parameters
        patient_id = request.GET.get('id', None)
        patient_name = request.GET.get('nom', None)

        if not patient_id or not patient_name:
            return Response({"detail": "Patient ID and name are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the patient based on the provided patient_id and patient_name
            patient = get_object_or_404(Patient, id=patient_id, nom=patient_name)
            
            # Get the DossierPatient associated with the patient
            dossier_patient = get_object_or_404(DossierPatient, patient=patient)

            # Serialize the patient and dossier details
            dossier_serializer = DossierPatientSerializer(dossier_patient)
            patient_serializer = PatientSerializer(patient)

            # Combine both serialized data
            response_data = {
                "dossier": dossier_serializer.data,
                "patient": patient_serializer.data,
            }

            return Response(response_data)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PatientSearchByNSSView(APIView):
    def get(self, request, *args, **kwargs):
        # Get 'nss' from query parameters
        nss = request.GET.get('nss', None)
        
        # Check if 'nss' is provided
        if not nss:
            return Response({"detail": "NSS is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Search for the patient by NSS
            patient = Patient.objects.get(nss=nss)
            
            # Serialize the patient data using the PatientSerializer
            patient_serializer = PatientSerializer(patient)
            
            # Return the patient data in the response
            return Response(patient_serializer.data)
        
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)