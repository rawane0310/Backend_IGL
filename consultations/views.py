from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from accounts.models import Consultation , Ordonnance , Technician , DossierPatient, Resume
from .serializers import ConsultationSerializer , OrdonnanceSerializer, ResumerSerializer
import random
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from accounts.mixin import CheckUserRoleMixin

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class OrdonnanceCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
   
    @swagger_auto_schema(
        operation_summary="Create a prescription",
        operation_description="This endpoint allows doctors to create a medical prescription by providing the necessary details.",
        request_body=OrdonnanceSerializer,
        responses={
            201: openapi.Response(
                description="Prescription created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "date": "2024-12-31",
                        "validation": False
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "validation": ["This field must be a boolean."]
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
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrdonnanceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()  # Sauvegarde l'ordonnance
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

###########################################################################################################################################


class ConsultationCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    """
    Vue pour créer une consultation avec validations dans la vue.
    """

    @swagger_auto_schema(
        operation_summary="Create a consultation",
        operation_description="This endpoint allows authorized users (doctors) to create a new medical consultation.",
        request_body=ConsultationSerializer,
        responses={
            201: openapi.Response(
                description="Consultation created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "medecin": 2,
                        "dossier": 3,
                        "ordonnance": None, 
                        "resume": None, 
                        "date": "2024-12-31",
                        "diagnosticStatut": False
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided or resource not found.",
                examples={
                    "application/json": {
                        "error": "The doctor with ID 5 does not exist."
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
            )
        }
    )

    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        # Vérifier si le médecin existe
        medecin_id = data.get('medecin')
        if medecin_id and not Technician.objects.filter(id=medecin_id).exists():
            return Response(
                {"error": f"Le médecin avec l'ID {medecin_id} n'existe pas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si le dossier existe
        dossier_id = data.get('dossier')
        if not dossier_id or not DossierPatient.objects.filter(id=dossier_id).exists():
            return Response(
                {"error": f"Le dossier patient avec l'ID {dossier_id} n'existe pas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si l'ordonnance existe si elle est fournie
        ordonnance_id = data.get('ordonnance')
        if ordonnance_id and not Ordonnance.objects.filter(id=ordonnance_id).exists():
            return Response(
                {"error": f"L'ordonnance avec l'ID {ordonnance_id} n'existe pas."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Vérifier si le resume existe s'il est fourni
        resume_id = data.get('resume')
        if resume_id and not Resume.objects.filter(id=resume_id).exists():
            return Response(
                {"error": f"Le resume avec l'ID {resume_id} n'existe pas."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sérialisation et sauvegarde
        serializer = ConsultationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"error": f"Le resume avec l'ID {resume_id} n'existe pas."},serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###########################################################################################################################################

class ResumeCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create a medical resume",
        operation_description="This endpoint allows doctors to create a medical resume containing diagnostic, symptoms, measures taken, and the date of the next consultation.",
        request_body=ResumerSerializer,
        responses={
            201: openapi.Response(
                description="Resume created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "diagnostic": "Hypertension diagnosis",
                        "symptomes": "Headache, dizziness",
                        "mesures_prises": "Blood pressure medications",
                        "date_prochaine_consultation": "2024-12-31"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "diagnostic": ["This field may not be null."]
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
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ResumerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()  # Sauvegarde l'ordonnance
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


###########################################################################################################################################
 

class SupprimerConsultationAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete a consultation",
        operation_description="This endpoint allows doctors to delete a specific consultation by providing the consultation ID.",
        manual_parameters=[
            openapi.Parameter(
                'consultation_id', openapi.IN_PATH, 
                description="ID of the consultation to be deleted", 
                type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            204: openapi.Response(
                description="Consultation deleted successfully.",
                examples={
                    "application/json": {
                        "message": "Consultation supprimée avec succès."
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden: The user does not have permission to delete this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to create this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Not Found: The specified consultation does not exist.",
                examples={
                    "application/json": {
                        "error": "Consultation introuvable."
                    }
                }
            ),
        }
    )

    def delete(self, request, consultation_id):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)
 
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': 'Consultation introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        consultation.delete()
        return Response(
            {'message': 'Consultation supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )

###########################################################################################################################################



class SupprimerOrdonnanceAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete a prescription",
        operation_description="This endpoint allows doctors to delete a specific prescription by providing the ordonnance ID.",
        manual_parameters=[
            openapi.Parameter(
                'ordonnance_id', openapi.IN_PATH, 
                description="ID of the ordonnance to be deleted", 
                type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            204: openapi.Response(
                description="Prescription deleted successfully.",
                examples={
                    "application/json": {
                        "message": "ordonnance supprimée avec succès."
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden: The user does not have permission to delete this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to create this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Not Found: The specified prescription does not exist.",
                examples={
                    "application/json": {
                        "error": "ordonnance introuvable."
                    }
                }
            ),
        }
    )

    def delete(self, request, ordonnance_id):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)
 
        try:
            ordonnance = Ordonnance.objects.get(id=ordonnance_id)
        except Ordonnance.DoesNotExist:
            return Response(
                {'error': 'ordonnance introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        ordonnance.delete()
        return Response(
            {'message': 'ordonnance supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )
    
###########################################################################################################################################
 


class SupprimerResumeAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Delete a resume",
        operation_description="This endpoint allows doctors to delete a specific resume by providing the resume ID.",
        manual_parameters=[
            openapi.Parameter(
                'resume_id', openapi.IN_PATH, 
                description="ID of the resume to be deleted", 
                type=openapi.TYPE_INTEGER, required=True
            )
        ],
        responses={
            204: openapi.Response(
                description="Resume deleted successfully.",
                examples={
                    "application/json": {
                        "message": "Resume supprimée avec succès."
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden: The user does not have permission to delete this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to create this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Not Found: The specified resume does not exist.",
                examples={
                    "application/json": {
                        "error": "Resume introuvable."
                    }
                }
            ),
        }
    )

    def delete(self, request, resume_id):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            resume = Resume.objects.get(id=resume_id)
        except Resume.DoesNotExist:
            return Response(
                {'error': 'Resume introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        resume.delete()
        return Response(
            {'message': 'Resume supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )
###########################################################################################################################################



class ModifierOrdonnanceAPIV(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Modify a prescription",
        operation_description="This endpoint allows doctors to update the details of an existing ordonnance (prescription).",
        manual_parameters=[
            openapi.Parameter(
                'ordonnance_id',
                openapi.IN_PATH,
                description="The ID of the ordonnance to be modified.",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        request_body=OrdonnanceSerializer,
        responses={
            200: openapi.Response(
                description="Prescription updated successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "date": "2024-12-31",
                        "validation": True
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "validation": ["This field must be a boolean."]
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
                description="Prescription not found.",
                examples={
                    "application/json": {
                        "error": "ordonnance introuvable."
                    }
                }
            ),
        }
        
    )


    def put(self, request, ordonnance_id):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        
        try:
            ordonnance = Ordonnance.objects.get(id=ordonnance_id)
        except Ordonnance.DoesNotExist:
            return Response(
                {'error': 'ordonnance  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrdonnanceSerializer(ordonnance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
    
###########################################################################################################################################
 

class ModifierConsultationAPIV(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
  
    @swagger_auto_schema(
        operation_summary="Modify a consultation",
        operation_description="This endpoint allows doctors to update the details of an existing consultation.",
         manual_parameters=[
            openapi.Parameter(
                'consultation_id',
                openapi.IN_PATH,
                description="The ID of the consultation to be modified.",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        request_body=ConsultationSerializer,
        responses={
            200: openapi.Response(
                description="Consultation updated successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "medecin": 2,
                        "dossier": 3,
                        "ordonnance": 1, 
                        "resume": 1, 
                        "date": "2024-12-31",
                        "diagnosticStatut": True
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "date": ["This field must be a valid date."]
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
                description="Consultation not found.",
                examples={
                    "application/json": {
                        "error": "consultation introuvable."
                    }
                }
            ),
        }
       
    )


    def put(self, request, consultation_id):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)
 
        
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': 'consultation  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConsultationSerializer(consultation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        

###########################################################################################################################################
 


class ConsultationSearchByDateView(APIView,CheckUserRoleMixin) : 
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Search consultations by date",
        operation_description="This endpoint allows the patient or the doctor to search for consultations by the specified date.",
        manual_parameters=[
            openapi.Parameter(
                'date', openapi.IN_QUERY, description="Date of the consultation (format: 'YYYY-MM-DD')", type=openapi.TYPE_STRING, required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful search results.",
                examples={
                    "application/json": [
                        {
                            "id": 10,
                            "date": "2024-12-31",
                            "medecin": 5,
                            "diagnosticStatut": True,
                            "resume": 10,
                            "ordonnance": 10,
                            "dossier": 15
                        }
                    ]
                }
            ),
            400: openapi.Response(
                description="Invalid or missing date parameter.",
                examples={
                    "application/json": {
                        "details": "date is required"
                    }
                }
            ),
            404: openapi.Response(
                description="No consultations found with the provided date.",
                examples={
                    "application/json": {
                        "details": "no consultation found with this date"
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to access this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to search for this resource."
                    }
                }
            ),
        }
    )

    def get( self , request , *args ,**kwargs ) : 
        if not self.check_user_role(request.user,['patient'],['medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)
 
        date  = request.GET.get ('date' , None)

        if not date :  
            return Response({"details " : "date is required"} , status=status.HTTP_400_BAD_REQUEST)
        
        try : 
            consultation = Consultation.objects.filter(date=date)
            if not consultation : 
                return Response ({"details" : "no consultation found with this date "}, status=status.HTTP_404_NOT_FOUND)
            
            cons_ser=ConsultationSerializer(consultation , many = True )

            return Response (cons_ser.data)
        except Exception as e : 
            return Response ({"details" : str(e) }, status=status.HTTP_400_BAD_REQUEST)
        

###########################################################################################################################################


class ConsultationSearchByDpiView (APIView,CheckUserRoleMixin ) : 
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Search consultations by DPI",
        operation_description="This endpoint allows the patient or doctor to search for consultations by the specified DPI.",
        manual_parameters=[
            openapi.Parameter(
                'dpi', openapi.IN_QUERY, description="Patient's DPI (Dossier Patient ID)", type=openapi.TYPE_STRING, required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful search results.",
                examples={
                    "application/json": [
                        {
                            "id": 10,
                            "date": "2024-12-31",
                            "medecin": 5,
                            "diagnosticStatut": True,
                            "resume": 10,
                            "ordonnance": 10,
                            "dossier": 15
                        }
                    ]
                }
            ),
            400: openapi.Response(
                description="Invalid or missing DPI parameter.",
                examples={
                    "application/json": {
                        "details": "dpi required"
                    }
                }
            ),
            404: openapi.Response(
                description="No consultations found with the provided DPI.",
                examples={
                    "application/json": {
                        "details": "no consultation with this dpi"
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to access this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to search for this resource."
                    }
                }
            ),
        }
    )


    def get (self , request , *args , **kwargs ) : 
        if not self.check_user_role(request.user,['patient'],['medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)
 
        dpi = request.GET.get('dpi' , None) 

        if not dpi : 
            return Response ({"details" : " dpi required "} , status=status.HTTP_400_BAD_REQUEST)
        
        try : 
            consultation = Consultation.objects.filter (dossier = dpi )
            if not consultation : 
                return Response ({"details" : "no consultation with this dpi "} , status=status.HTTP_404_NOT_FOUND)

            consult_ser = ConsultationSerializer(consultation , many = True) 
            return Response (consult_ser.data) 
        
        except Exception as e :
            return Response ({"details" : str(e)} , status=status.HTTP_400_BAD_REQUEST ) 

###########################################################################################################################################


class ConsultationSearchByTechnicienView (APIView,CheckUserRoleMixin) : 
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Search consultations by technician",
        operation_description="This endpoint allows the patient or the doctor to search for consultations by the specified technician (doctor).",
        manual_parameters=[
            openapi.Parameter(
                'tech', openapi.IN_QUERY, description="Technician's ID (doctor)", type=openapi.TYPE_STRING, required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful search results.",
                examples={
                    "application/json": [
                        {
                            "id": 10,
                            "date": "2024-12-31",
                            "medecin": 5,
                            "diagnosticStatut": True,
                            "resume": 10,
                            "ordonnance": 10,
                            "dossier": 15
                        }
                    ]
                }
            ),
            400: openapi.Response(
                description="Invalid or missing technician parameter.",
                examples={
                    "application/json": {
                        "details": "technicien required"
                    }
                }
            ),
            404: openapi.Response(
                description="No consultations found with the provided technician.",
                examples={
                    "application/json": {
                        "details": "no consultation with this technicien"
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to access this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to search for this resource."
                    }
                }
            ),
        }
    )

    def get (self , request , *args , **kwargs ) : 
        if not self.check_user_role(request.user,['patient'],['medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)
 
        tech = request.GET.get('tech' , None) 

        if not tech : 
            return Response ({"details" : " technicien required "} , status=status.HTTP_400_BAD_REQUEST)
        
        try : 
            consultation = Consultation.objects.filter (medecin = tech)
            if not consultation : 
                return Response ({"details" : "no consultation with this technicien "} , status=status.HTTP_404_NOT_FOUND)

            consult_ser = ConsultationSerializer(consultation , many = True) 
            return Response (consult_ser.data) 
        
        except Exception as e :
            return Response ({"details" : str(e)} , status=status.HTTP_400_BAD_REQUEST ) 
        
###########################################################################################################################################
 

class ModifierResumeAPIV(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
 
    @swagger_auto_schema(
        operation_summary="Update a consultation's resume",
        operation_description="This endpoint allows doctors to modify the details of an existing resume, such as diagnostic, symptoms, measures taken, and next consultation date.",
        manual_parameters=[
            openapi.Parameter(
                'resume_id', 
                openapi.IN_PATH, 
                description="The ID of the resume to be modified.", 
                type=openapi.TYPE_INTEGER, 
                required=True,
            )
            
        ],
        request_body=ResumerSerializer,
        responses={
            200: openapi.Response(
                description="Resume updated successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "diagnostic": "Updated diagnostic",
                        "symptomes": "Updated symptoms",
                        "mesures_prises": "Updated measures",
                        "date_prochaine_consultation": "2025-01-10"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "diagnostic": ["This field must be a string."]
                       
                    }
                }
            ),
            403: openapi.Response(
                description="Permission denied. You do not have permission to modify this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to modify this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Resume not found.",
                examples={
                    "application/json": {
                        "error": "Resume not found."
                    }
                }
            )
        }
    )

    def put(self, request, resume_id):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        
        try:
            resume = Resume.objects.get(id=resume_id)
        except Resume.DoesNotExist:
            return Response(
                {'error': 'Resume  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResumerSerializer(resume, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        
###########################################################################################################################################
 

class RechercheOrdonnanceAPIV(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Search prescriptions",
        operation_description="Allows the patient or the doctor to search for prescriptions (ordonnances) using different filters such as ID, date, and validation status.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="Prescription ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('date', openapi.IN_QUERY, description="Date of the prescription (format: 'YYYY-MM-DD')", type=openapi.TYPE_STRING),
            openapi.Parameter('validation', openapi.IN_QUERY, description="Validation status ('true' or 'false')", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="List of prescriptions matching the filters.",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "date": "2024-12-31",
                            "validation": False
                        },
                        {
                            "id": 2,
                            "date": "2024-12-30",
                            "validation": True
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
            ),
        }
    )


    def get(self, request):
        if not self.check_user_role(request.user, ['patient'],['medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Récupérer les paramètres de requête
        id_ = request.GET.get('id')
        date = request.GET.get('date')  # Format attendu : "yyyy-mm-dd"
        validation = request.GET.get('validation')  # "true" ou "false"
        
        # Filtrer les ordonnances
        ordonnances = Ordonnance.objects.all()
        
        if id_:
            ordonnances = ordonnances.filter(id=id_)
        if date:
            ordonnances = ordonnances.filter(date=date)
        if validation is not None:
            validation_bool = validation.lower() == 'true'
            ordonnances = ordonnances.filter(validation=validation_bool)
        
        # Préparer la réponse
        resultats = list(ordonnances.values())
        return Response(resultats)

###########################################################################################################################################
 

class RechercheResume(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Search medical summaries",
        operation_description="Allows the patient or the doctor to search for medical summaries (resumes) using different filters such as ID, diagnostic, symptoms, and next consultation date.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="Summary ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('diagnostic', openapi.IN_QUERY, description="Medical diagnosis", type=openapi.TYPE_STRING),
            openapi.Parameter('symptomes', openapi.IN_QUERY, description="Symptoms reported by the patient", type=openapi.TYPE_STRING),
            openapi.Parameter('mesures_prises', openapi.IN_QUERY, description="Measures taken for the patient", type=openapi.TYPE_STRING),
            openapi.Parameter('date_prochaine_consultation', openapi.IN_QUERY, description="Date of the next consultation (format: 'YYYY-MM-DD')", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="List of medical summaries matching the filters.",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "diagnostic": "Flu",
                            "symptomes": "Fever, Cough",
                            "mesures_prises": "Rest, Hydration",
                            "date_prochaine_consultation": "2025-01-10"
                        }
                    ]
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to create this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to search for this resource."
                    }
                }
            ),
        }
    )

    def get(self,request):
        if not self.check_user_role(request.user, ['patient'],['medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Récupérer les paramètres de requête
        id_ = request.GET.get('id')
        diagnostic = request.GET.get('diagnostic')
        symptomes =request.GET.get('symptomes')
        mesures_prises = request.GET.get('mesures_prises')
        date_prochaine_consultation =request.GET.get('date_prochaine_consultation')

        resumes = Resume.objects.all()
        if id_ :
            resumes = resumes.filter(id=id_)
        if diagnostic is not None:
            resumes = resumes.filter(diagnostic=diagnostic) 
        if symptomes is not None:
            resumes = resumes.filter(symptomes=symptomes)
        if  mesures_prises is not None:
            resumes = resumes.filter(mesures_prises=mesures_prises)
        if  date_prochaine_consultation is not None:
            resumes = resumes.filter(date_prochaine_consultation=date_prochaine_consultation)
        # Préparer la réponse
        resultats = list(resumes.values())
        return Response(resultats)                 

###########################################################################################################################################
 
 
class ValidationOrdonnance(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Validate a prescription",
        operation_description="This endpoint validates a prescription by ID. The validation result is random (True or False).",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH, description="The ID of the prescription to validate", type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description="Prescription validation result",
                examples={
                    "application/json": {
                        "message": "Ordonnance validée avec succès.",
                        "validation": True
                    }
                }
            ),
            404: openapi.Response(
                description="Prescription not found",
                examples={
                    "application/json": {
                        "error": "Ordonnance non trouvée."
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to validate this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to validate this resource."
                    }
                }
            ),
        }
    )

    def post(self, request, pk):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to validate this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Récupérer l'ordonnance par ID
            ordonnance = Ordonnance.objects.get(pk=pk)
            
            # Validation aléatoire (vrai ou faux)
            validation_random = random.choice([True, False])
            ordonnance.validation = validation_random
            ordonnance.save()

            # Réponse selon l'état de validation
            if validation_random:
                return Response({"message": "Ordonnance validée avec succès.", "validation": True}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Ordonnance rejetée.", "validation": False}, status=status.HTTP_200_OK)
        except Ordonnance.DoesNotExist:
            return Response({"error": "Ordonnance non trouvée."}, status=status.HTTP_404_NOT_FOUND)

