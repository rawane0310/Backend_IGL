from django.shortcuts import render , redirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import DossierPatient, Patient
from .serializers import DossierPatientSerializer , PatientSerializer, UserPatientSerializer
import qrcode
import io
import json
import base64
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from accounts.mixin import CheckUserRoleMixin

from django.core.files.base import ContentFile

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

################ test fonctionel######################
from django.http import JsonResponse
from .forms import DossierPatientForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


class DossierPatientCreateView(APIView,CheckUserRoleMixin):
    #permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
       # if not self.check_user_role(request.user, ['administratif'],['medecin']):
            #return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            patient_id = request.data.get('patient')
            patient = Patient.objects.get(id=patient_id)

            # Vérifiez s'il existe déjà un dossier pour ce patient
            if DossierPatient.objects.filter(patient=patient).exists():
                return Response({"error": "Un dossier existe déjà pour ce patient."}, status=status.HTTP_400_BAD_REQUEST)

            # Génération du QR code
            qr_data = {"Patient": patient.nom, "ID": patient.id}  # Dictionnaire valide
            qr_data_str = json.dumps(qr_data)  # Conversion en chaîne JSON
            qr_image = qrcode.make(qr_data_str)
            buffer = io.BytesIO()
            qr_image.save(buffer, format="PNG")
            
            buffer.seek(0)

            # Création du fichier image pour l'ImageField
            qr_file = ContentFile(buffer.read(), name=f"qr_patient_{patient.id}.png")
            buffer.close()

            # Création du dossier patient
            dossier = DossierPatient.objects.create(patient=patient, qr=qr_file)
            serializer = DossierPatientSerializer(dossier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Patient.DoesNotExist:
            return Response({"error": "Patient introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###########################################################################################################################################
class SupprimerDpiAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def delete(self, request, dpi_id):
        if not self.check_user_role(request.user, ['administratif'],['medecin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
    

###########################################################################################################################################

class ModifierDossierAPIView(APIView,CheckUserRoleMixin):
    
    permission_classes = [IsAuthenticated]
    def put(self, request, dpi_id):
        if not self.check_user_role(request.user, ['administratif'],['medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        return self.update_dpi(request, dpi_id, partial=False)

    def patch(self, request, dpi_id):
        if not self.check_user_role(request.user, ['administratif'],['medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        return self.update_dpi(request, dpi_id, partial=True)

    def update_dpi(self, request, dpi_id, partial):
        if not self.check_user_role(request.user, ['administratif'],['medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

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

###########################################################################################################################################


class DossierPatientSearchView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Search for a patient dossier by ID and name. This action can be performed by 'administratif', 'patient', or 'technicien'.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="The ID of the patient.", type=openapi.TYPE_STRING),
            openapi.Parameter('nom', openapi.IN_QUERY, description="The name of the patient.", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response('Patient dossier found', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER)})),
            400: 'Bad request - Patient ID and name are required or invalid data provided',
            403: 'Forbidden - You do not have permission to search for this resource',
            404: 'Patient or Dossier not found',
        }
    )

    def get(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['administratif','patient','technicien']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

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

            # Return the dossier patient id in the response
            return Response({"id": dossier_patient.id}, status=status.HTTP_200_OK)
            

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)



###########################################################################################################################################

class PatientSearchByNSSView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Search for a patient dossier using their NSS (National Security Number). This action can be performed by 'administratif', 'patient', or 'technicien'.",
        manual_parameters=[
            openapi.Parameter('nss', openapi.IN_QUERY, description="The NSS (National Security Number) of the patient.", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response('Patient dossier found', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER)})),
            400: 'Bad request - NSS is required or invalid data provided',
            403: 'Forbidden - You do not have permission to search for this resource',
            404: 'Patient not found',
        }
    )

    def get(self, request, *args, **kwargs):
        
        if not self.check_user_role(request.user,['administratif','patient','technicien']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Get 'nss' from query parameters
        nss = request.GET.get('nss', None)
        
        # Check if 'nss' is provided
        if not nss:
            return Response({"detail": "NSS is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Search for the patient by NSS
            patient = Patient.objects.get(nss=nss)
            
            # Get the DossierPatient associated with the patient
            dossier_patient = get_object_or_404(DossierPatient, patient=patient)

            
            
            # Return the dossier patient id in the response
            return Response({"id": dossier_patient.id}, status=status.HTTP_200_OK)
        
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:

            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        



## retrun patitn object by id 
@login_required
def search_patient_by_dossier(request, dossier_id):
    
    # Try to retrieve the dossier and associated patient
    dossier = get_object_or_404(DossierPatient, id=dossier_id)
    patient = dossier.patient

    # Construire l'URL absolue pour le QR code
    qr_url = request.build_absolute_uri(dossier.qr.url) if dossier.qr else None
    # Return patient details in JSON format
    response_data = {
        'qr': qr_url,
        'id': patient.id,
        'nom': patient.nom,
        'prenom': patient.prenom,
        'date_naissance': patient.date_naissance.strftime('%Y-%m-%d'),
        'adresse': patient.adresse,
        'tel': patient.tel,
        'mutuelle': patient.mutuelle,
        'medecin_traitant': patient.medecin_traitant.id if patient.medecin_traitant else None,
        'personne_a_contacter': patient.personne_a_contacter,
        'nss': patient.nss,
    }
    return JsonResponse(response_data)

from rest_framework.decorators import action

from django.contrib.auth import get_user_model


class creatuserPatientView(APIView,CheckUserRoleMixin):
    permission_classes=[IsAuthenticated]
    @action(methods=['POST'], detail=False)
    def post(self, request):
        if not self.check_user_role(request.user,['administratif'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserPatientSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Get the custom User model
            User = get_user_model() 

            user = User.objects.create_user(
                email=email, 
                password=password, 
                role="patient" 
            )

            patient_data = {
                'user': user,
                'nom': serializer.validated_data['nom'],
                'prenom': serializer.validated_data['prenom'],
                'date_naissance': serializer.validated_data['date_naissance'],
                'adresse': serializer.validated_data['adresse'],
                'tel': serializer.validated_data['tel'],
                'mutuelle': serializer.validated_data['mutuelle'],
                'medecin_traitant': serializer.validated_data['medecin_traitant'],
                'personne_a_contacter': serializer.validated_data['personne_a_contacter'],
                'nss': serializer.validated_data['nss'] , 
            }
            patient = Patient.objects.create(**patient_data)

            # Génération du QR code
            qr_data = {"Patient": patient.nom, "ID": patient.id}  # Dictionnaire valide
            qr_data_str = json.dumps(qr_data)  # Conversion en chaîne JSON
            qr_image = qrcode.make(qr_data_str)
            buffer = io.BytesIO()
            qr_image.save(buffer, format="PNG")
            
            buffer.seek(0)

            # Création du fichier image pour l'ImageField
            qr_file = ContentFile(buffer.read(), name=f"qr_patient_{patient.id}.png")
            buffer.close()
             
            dossier = DossierPatient.objects.create(patient=patient, qr=qr_file)



            return Response({'message': 'Patient registered successfully , and dossier created successfully'}, status=status.HTTP_201_CREATED)
        else : 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



# test fonctionel

def create_dpi(request):
    if request.method == 'POST':
        form = DossierPatientForm(request.POST)
        if form.is_valid():

            patient_id = form.cleaned_data['patient_id']
        # Simuler la création du DPI

        patient = Patient.objects.get(id=patient_id)
        # Vérifiez s'il existe déjà un dossier pour ce patient
        if DossierPatient.objects.filter(patient=patient).exists():
                return Response({"error": "Un dossier existe déjà pour ce patient."}, status=status.HTTP_400_BAD_REQUEST)

        # Génération du QR code
        qr_data = {"Patient": patient.nom, "ID": patient.id}  # Dictionnaire valide
        qr_data_str = json.dumps(qr_data)  # Conversion en chaîne JSON
        qr_image = qrcode.make(qr_data_str)
        buffer = io.BytesIO()
        qr_image.save(buffer, format="PNG")
            
        buffer.seek(0)

        # Création du fichier image pour l'ImageField
        qr_file = ContentFile(buffer.read(), name=f"qr_patient_{patient.id}.png")
        buffer.close()
        dpi = DossierPatient.objects.create(patient=patient, qr=qr_file)
        return JsonResponse({"status": "success", "message": "DPI created", "dpi_id": dpi.id})
    else:
        form = DossierPatientForm()

    return render(request, 'dpi.html', {'form': form})


            





