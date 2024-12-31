from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Ordonnance , DossierPatient, Technician , Medicament, SoinInfermier
from .serializers import  SoinInfermierSerializer, MedicamentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from accounts.mixin import CheckUserRoleMixin

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SoinInfermierCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create a nursing care record (Soin Infirmier)",
        operation_description="This endpoint allows nurses to create a nursing care record by providing necessary details.",
        
        request_body=SoinInfermierSerializer,
        responses={
            201: openapi.Response(
                description="Nursing care record created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "date": "2024-12-31",
                        "infirmier": 1,
                        "heure": "15:00",
                        "observation": "Patient in good condition.",
                        "soin_realise": "Administered medication.",
                        "dossier": 12
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "date": ["This field is required."],
                        "soin_realise": ["This field is required."]
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to create this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to create this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Not found error, either the patient file or nurse is not found.",
                examples={
                    "application/json": {
                        "error": "The specified patient file does not exist."
                    }
                }
            ),
        }
    )

    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user,technician_roles=['infermier']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = SoinInfermierSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Vérifiez si le dossier patient existe
                dossier_id = serializer.validated_data['dossier'].id
                DossierPatient.objects.get(id=dossier_id)

                # Vérifiez si le technicien (infirmier) existe (si fourni)
                infirmier = serializer.validated_data.get('infirmier')
                if infirmier is not None:
                    Technician.objects.get(id=infirmier.id)

                # Sauvegarde du soin infirmier
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except DossierPatient.DoesNotExist:
                return Response({"error": "Le dossier patient spécifié est introuvable."}, status=status.HTTP_404_NOT_FOUND)

            except Technician.DoesNotExist:
                return Response({"error": "L'infirmier spécifié est introuvable."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

###########################################################################################################################################
 

class MedicamentCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create a new Medicament",
        operation_description="This endpoint allows authenticated nurses or doctors to create a new medicament associated with either an ordonnance (prescription) or a soin infirmier (nursing care). Both fields cannot be provided simultaneously.",
        manual_parameters=[
            openapi.Parameter('ordonnance', openapi.IN_BODY, description="ID of the ordonnance (prescription) associated with the medicament.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('soin', openapi.IN_BODY, description="ID of the soin infirmier (nursing care) associated with the medicament.", type=openapi.TYPE_INTEGER),
        ],
        request_body=MedicamentSerializer,
        responses={
            201: openapi.Response(
                description="Medicament created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "nom": "Paracetamol",
                        "dose": "500mg",
                        "frequence": "Once a day",
                        "duree": "7 days",
                        "ordonnance": 1,
                        "soin": None,
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "error": "You must provide either an ordonnance or a soin infirmier, not both."
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to create this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to create this resource."
                    }
                }
            ),
        }
    )

    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user,technician_roles=['infermier','medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        ordonnance_id = data.get('ordonnance')
        soin_id = data.get('soin')

        # Vérifiez que l'un des deux champs est fourni
        if not ordonnance_id and not soin_id:
            return Response(
                {"error": "Vous devez fournir soit une ordonnance, soit un soin infirmier."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifiez que les deux ne sont pas fournis en même temps
        if ordonnance_id and soin_id:
            return Response(
                {"error": "Un médicament ne peut pas être associé à une ordonnance et à un soin infirmier en même temps."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifiez que l'ordonnance existe si elle est fournie
        if ordonnance_id and not Ordonnance.objects.filter(id=ordonnance_id).exists():
            return Response(
                {"error": f"L'ordonnance avec l'ID {ordonnance_id} est introuvable."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifiez que le soin infirmier existe si il est fourni
        if soin_id and not SoinInfermier.objects.filter(id=soin_id).exists():
            return Response(
                {"error": f"Le soin infirmier avec l'ID {soin_id} est introuvable."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Passez à la sérialisation et sauvegarde
        serializer = MedicamentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
###########################################################################################################################################
 

class SupprimerMedicamentAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete a medicament",
        operation_description="This endpoint allows authorized users ('infermier' or 'medecin') to delete a medicament by its unique ID.",
        manual_parameters=[
            openapi.Parameter(
                'medicament_id', 
                openapi.IN_PATH, 
                description="ID of the medicament to be deleted", 
                type=openapi.TYPE_INTEGER, 
                required=True
            ),
        ],
        responses={
            204: openapi.Response(
                description="Medicament successfully deleted.",
                examples={
                    "application/json": {
                        "message": "Medicament deleted successfully."
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden. User does not have permission to delete the resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to delete this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Medicament not found.",
                examples={
                    "application/json": {
                        "error": "Medicament not found."
                    }
                }
            ),
        }
    )

    def delete(self, request, medicament_id):
        if not self.check_user_role(request.user,technician_roles=['infermier','medecin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            medicament = Medicament.objects.get(id=medicament_id)
        except Medicament.DoesNotExist:
            return Response(
                {'error': 'Medicament introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        medicament.delete()
        return Response(
            {'message': 'Medicament supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )
    
###########################################################################################################################################
 

class SupprimerSoinAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete a care record",
        operation_description="This endpoint allows a nurse to delete a care record by its ID.",
        manual_parameters=[
            openapi.Parameter(
                'soin_id',
                openapi.IN_PATH,
                description="The ID of the care record to delete.",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: openapi.Response(
                description="Successfully deleted the care record.",
                examples={
                    "application/json": {
                        "message": "Soin supprimée avec succès."
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to delete this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to delete this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Care record not found.",
                examples={
                    "application/json": {
                        "error": "Soin introuvable."
                    }
                }
            ),
        }
    )

    def delete(self, request, soin_id):
        if not self.check_user_role(request.user,technician_roles=['infermier']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            soin = SoinInfermier.objects.get(id=soin_id)
        except SoinInfermier.DoesNotExist:
            return Response(
                {'error': 'Soin introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        soin.delete()
        return Response(
            {'message': 'Soin supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )    
    
###########################################################################################################################################
 

class ModifierSoinInfermierAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update a nursing care record",
        operation_description="This endpoint allows a nurse to modify an existing nursing care record. Only authorized nurses can modify the record.",
        manual_parameters=[
            openapi.Parameter(
                'soin_id', 
                openapi.IN_PATH, 
                description="The ID of the nursing care record (soin infirmier) to update.", 
                type=openapi.TYPE_INTEGER, 
                required=True
            )
        ],
        request_body=SoinInfermierSerializer,
        responses={
            200: openapi.Response(
                description="Successfully updated the nursing care record.",
                examples={
                    "application/json": {
                        "id": 1,
                        "date": "2024-12-31",
                        "infirmier": 2,
                        "heure": "15:00",
                        "observation": "Patient showing improvement.",
                        "soin_realise": "Wound dressing.",
                        "dossier": 1
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "observation": ["This field may not be blank."]
                    }
                }
            ),
            403: openapi.Response(
                description="Permission denied. You do not have the required role to update this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to modify this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Nursing care record not found.",
                examples={
                    "application/json": {
                        "error": "Soin infirmier introuvable."
                    }
                }
            ),
        }
    )

    def put(self, request, soin_id):
        if not self.check_user_role(request.user,technician_roles=['infermier']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        
        try:
            soin = SoinInfermier.objects.get(id=soin_id)
        except SoinInfermier.DoesNotExist:
            return Response(
                {'error': 'Soin infirmier introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SoinInfermierSerializer(soin, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


###########################################################################################################################################
 

class ModifierMedicamentAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Modify an existing medication",
        operation_description="This endpoint allows authorized users (infermier , medecin) to update the details of an existing medication by providing the medication ID and the data to be updated.",
        manual_parameters=[
            openapi.Parameter(
                'medicament_id', 
                openapi.IN_PATH, 
                description="The ID of the medication to be updated.", 
                type=openapi.TYPE_INTEGER, 
                required=True
            ),
        ],
        request_body=MedicamentSerializer,
        responses={
            200: openapi.Response(
                description="Medication successfully updated.",
                examples={
                    "application/json": {
                        "id": 1,
                        "nom": "Paracetamol",
                        "dose": "500mg",
                        "frequence": "Every 6 hours",
                        "duree": "5 days",
                        "ordonnance": 2,
                        "soin": None
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "dose": ["This field is required."]
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
                description="The specified medication was not found.",
                examples={
                    "application/json": {
                        "error": "medicament introuvable."
                    }
                }
            ),
        }
    )

    def put(self, request, medicament_id):
        if not self.check_user_role(request.user,technician_roles=['infermier','medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        
        try:
            medicament = Medicament.objects.get(id=medicament_id)
        except Medicament.DoesNotExist:
            return Response(
                {'error': 'medicament  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MedicamentSerializer(medicament, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
    
###########################################################################################################################################
 


class RechercheMedicamentAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Search for medications",
        operation_description="This endpoint allows patients, or nursers, or doctors to search for medications using various filters. It can filter by medication ID, name, dose, frequency, duration, prescription ID, and care ID.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="Filter by medication ID.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('nom', openapi.IN_QUERY, description="Filter by medication name (partial match).", type=openapi.TYPE_STRING),
            openapi.Parameter('dose', openapi.IN_QUERY, description="Filter by medication dose (partial match).", type=openapi.TYPE_STRING),
            openapi.Parameter('frequence', openapi.IN_QUERY, description="Filter by medication frequency (partial match).", type=openapi.TYPE_STRING),
            openapi.Parameter('duree', openapi.IN_QUERY, description="Filter by medication duration (partial match).", type=openapi.TYPE_STRING),
            openapi.Parameter('ordonnance', openapi.IN_QUERY, description="Filter by prescription ID.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('soin', openapi.IN_QUERY, description="Filter by care ID.", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="List of medications matching the search criteria.",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "nom": "Paracetamol",
                            "dose": "500mg",
                            "frequence": "3 times a day",
                            "duree": "7 days",
                            "ordonnance_id": 1,
                            "soin_id": None
                        },
                        {
                            "id": 2,
                            "nom": "Ibuprofen",
                            "dose": "200mg",
                            "frequence": "2 times a day",
                            "duree": "5 days",
                            "ordonnance_id": None,
                            "soin_id": 3
                        }
                    ]
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to search for this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to search for this resource."
                    }
                }
            )
        }
    )

    def get(self, request):
        if not self.check_user_role(request.user, ['patient'],['infermier','medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Récupérer les paramètres de recherche depuis la requête GET
        id_ = request.GET.get('id')
        nom = request.GET.get('nom')
        dose = request.GET.get('dose')
        frequence = request.GET.get('frequence')
        duree = request.GET.get('duree')
        ordonnance_id = request.GET.get('ordonnance')  # ID de l'ordonnance
        soin_id = request.GET.get('soin')  # ID du soin infirmier
        
        # Initialiser une requête pour récupérer tous les médicaments
        medicaments = Medicament.objects.all()
        
        # Appliquer les filtres selon les paramètres fournis
        if id_:
            medicaments = medicaments.filter(id=id_)
        if nom:
            medicaments = medicaments.filter(nom__icontains=nom)  # Recherche partielle
        if dose:
            medicaments = medicaments.filter(dose__icontains=dose)
        if frequence:
            medicaments = medicaments.filter(frequence__icontains=frequence)
        if duree:
            medicaments = medicaments.filter(duree__icontains=duree)
        if ordonnance_id:
            medicaments = medicaments.filter(ordonnance_id=ordonnance_id)
        if soin_id:
            medicaments = medicaments.filter(soin_id=soin_id)
        
        # Préparer les résultats au format JSON
        resultats = list(medicaments.values())
        return Response(resultats)

###########################################################################################################################################
 
 
class RechercheSoinInfermierAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Search for nursing care",
        operation_description="This endpoint allows patients,nursers or doctors to search for nursing care records based on various filters, including ID, date, nurse, observation, and more.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the nursing care", type=openapi.TYPE_INTEGER),
            openapi.Parameter('date', openapi.IN_QUERY, description="Date of the nursing care (format: 'yyyy-mm-dd')", type=openapi.TYPE_STRING),
            openapi.Parameter('infirmier', openapi.IN_QUERY, description="ID of the nurse", type=openapi.TYPE_INTEGER),
            openapi.Parameter('heure', openapi.IN_QUERY, description="Time of the nursing care", type=openapi.TYPE_STRING),
            openapi.Parameter('observation', openapi.IN_QUERY, description="Text within the observation field", type=openapi.TYPE_STRING),
            openapi.Parameter('soin_realise', openapi.IN_QUERY, description="Text within the performed care field", type=openapi.TYPE_STRING),
            openapi.Parameter('dossier', openapi.IN_QUERY, description="Patient dossier ID", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved the nursing care records.",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "date": "2024-12-31",
                            "heure": "08:00",
                            "observation": "Patient in stable condition",
                            "soin_realise": "Administered medication",
                            "dossier_id": 15,
                            "infirmier_id": 11,
                            "infirmier_nom": "John",
                            "infirmier_prenom": "Doe"
                        }
                    ]
                }
            ),
            403: openapi.Response(
                description="Forbidden access. The user does not have the required permissions to search.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to search for this resource."
                    }
                }
            ),
        }
    )

    def get(self, request):
        if not self.check_user_role(request.user, ['patient'],['infermier','medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Récupération des paramètres de recherche
        id_ = request.GET.get('id')  # ID du soin
        date = request.GET.get('date')  # Format attendu : yyyy-mm-dd
        infirmier_id = request.GET.get('infirmier')  # ID de l'infirmier
        heure=request.GET.get('heure') #l'heure du soins
        observation = request.GET.get('observation')  # Texte dans observation
        soin_realise = request.GET.get('soin_realise')  # Texte dans soin réalisé
        dossier_id = request.GET.get('dossier')  # ID du dossier patient
        
        # Initialiser une requête pour récupérer tous les soins
        soins = SoinInfermier.objects.all()
        
        # Appliquer les filtres si les paramètres sont fournis
        if id_:
            soins = soins.filter(id=id_)
        if date:
            soins = soins.filter(date=date)
        if infirmier_id:
            soins = soins.filter(infirmier_id=infirmier_id)
        if heure:
            heure = soins.filter(heure=heure)    
        if observation:
            soins = soins.filter(observation__icontains=observation)  # Recherche partielle
        if soin_realise:
            soins = soins.filter(soin_realise__icontains=soin_realise)  # Recherche partielle
        if dossier_id:
            soins = soins.filter(dossier_id=dossier_id)
        
        # Préparer les données pour inclure nom et prénom de l'infirmier
        resultats = []
        for soin in soins:
            resultats.append({
                'id': soin.id,
                'date': soin.date,
                'heure': soin.heure,
                'observation': soin.observation,
                'soin_realise': soin.soin_realise,
                'dossier_id': soin.dossier_id,
                'infirmier_id': soin.infirmier_id,
                'infirmier_nom': soin.infirmier.nom if soin.infirmier else None,
                'infirmier_prenom': soin.infirmier.prenom if soin.infirmier else None,
            })

        return Response(resultats)
