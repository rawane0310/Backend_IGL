from django.shortcuts import render , redirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import DossierPatient, Patient , Technician
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


class SupprimerDpiAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete a patient's file (Dossier Patient)",
        operation_description="This endpoint allows authorized users (administratif or medecin) to delete a patient file (Dossier Patient) by its ID.",
        manual_parameters=[
            openapi.Parameter(
                'dpi_id', 
                openapi.IN_PATH, 
                description="The ID of the patient's file (Dossier Patient) to be deleted.", 
                type=openapi.TYPE_INTEGER, 
                required=True
            ),
        ],
        responses={
            204: openapi.Response(
                description="Patient file deleted successfully."
            ),
            403: openapi.Response(
                description="Forbidden. The user does not have permission to delete this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to delete this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Patient file not found.",
                examples={
                    "application/json": {
                        "error": "dpi introuvable."  
                    }
                }
            ),
        }
    )

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

    @swagger_auto_schema(
        operation_summary="Update a patient file (DossierPatient)",
        operation_description="This endpoint allows users with the `administratif` or `medecin` role to modify a patient's file (DossierPatient). The `dpi_id` is required to identify the record to be updated.",
        manual_parameters=[
            openapi.Parameter(
                'dpi_id', 
                openapi.IN_PATH,
                description="The unique identifier of the patient file (DossierPatient) to be updated.",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=DossierPatientSerializer,
        responses={
            200: openapi.Response(
                description="Patient file updated successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "patient": 1,
                        "qr": "media/qr_code/qr_patient_33.png"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided for updating the dossier.",
                examples={
                    "application/json": {
                        "patient": ["This field is integer."]
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to modify this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to modify this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="DossierPatient not found for the given `dpi_id`.",
                examples={
                    "application/json": {
                        "error": "dpi introuvable."
                    }
                }
            ),
        }
    )

    def put(self, request, dpi_id):
        if not self.check_user_role(request.user, ['administratif'],['medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        
        try:
            dpi = DossierPatient.objects.get(id=dpi_id)
        except DossierPatient.DoesNotExist:
            return Response(
                {'error': 'dpi  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DossierPatientSerializer(dpi, data=request.data, partial=True)
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
    #permission_classes=[IsAuthenticated]
    @action(methods=['POST'], detail=False)
    def post(self, request):
        #if not self.check_user_role(request.user,['administratif'],['medecin']):
            #return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
        



###################################### test fonctionel ###################################################
from rest_framework import serializers
from django.contrib import messages

def create_dpi(request):
    # Vérifie si la méthode de la requête est 'POST'
    if request.method == 'POST':
        # Initialise un formulaire 'DossierPatientForm' avec les données envoyées dans la requête
        form = DossierPatientForm(request.POST)

        # Si le formulaire est valide (tous les champs requis sont remplis correctement)
        if form.is_valid():
            # Récupère les données du formulaire pour créer un nouveau dossier patient

            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            adresse = form.cleaned_data['adresse']
            date_naissance = form.cleaned_data['date_naissance']
            tel = form.cleaned_data['tel']
            mutuelle = form.cleaned_data['mutuelle']
            medecin_traitant = form.cleaned_data['medecin_traitant']
            personne_a_contacter = form.cleaned_data['personne_a_contacter']
            nss = form.cleaned_data['nss']
            


            

            # Création d'un compte utilisateur (User) avec les données du formulaire 
            User = get_user_model()
            user=User.objects.create_user(email=email, password=password,role="patient")

        
        # Création d'un objet Patient avec les données recueillies et l'utilisateur créé
        patient = Patient.objects.create(
                nom=nom,
                prenom=prenom,
                adresse=adresse,
                date_naissance=date_naissance,
                tel=tel,
                mutuelle=mutuelle,
                medecin_traitant=medecin_traitant,
                personne_a_contacter=personne_a_contacter,
                nss=nss,
                user=user
            )
        

        
        
        # Génération du QR code
        qr_data = {"Patient": patient.nom, "ID": patient.id}  # Données à intégrer dans le QR code
        qr_data_str = json.dumps(qr_data)  # Convertit les données en chaîne JSON
        qr_image = qrcode.make(qr_data_str) # Crée l'image du QR code à partir des données
        buffer = io.BytesIO() # Crée un tampon en mémoire pour l'image
        qr_image.save(buffer, format="PNG")  # Sauvegarde l'image au format PNG dans le tampon
            
        buffer.seek(0) # Se positionne au début du tampon

            # Création du fichier image pour l'ImageField
        qr_file = ContentFile(buffer.read(), name=f"qr_patient_{patient.id}.png")
        buffer.close() # Ferme le tampon mémoire

        # Crée un objet DossierPatient avec le patient et l'image du QR code    
        dossier = DossierPatient.objects.create(patient=patient, qr=qr_file)
        
       
        # Ajout du message de succès
        messages.success(request, 'Dossier patient créé avec succès !')

        
    else:
        # Si la méthode de la requête n'est pas POST, crée un formulaire vide
        form = DossierPatientForm()

    # Rendu de la page avec le formulaire, qu'il soit pré-rempli (POST) ou vide (GET)
    return render(request, 'dpi.html', {'form': form})


            





