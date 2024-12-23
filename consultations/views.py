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

class OrdonnanceCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrdonnanceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()  # Sauvegarde l'ordonnance
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ConsultationCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    """
    Vue pour créer une consultation avec validations dans la vue.
    """

    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
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

    
class ResumeCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ResumerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()  # Sauvegarde l'ordonnance
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class SupprimerConsultationAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def delete(self, request, consultation_id):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
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

class SupprimerOrdonnanceAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def delete(self, request, ordonnance_id):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
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
    

class SupprimerResumeAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def delete(self, request, resume_id):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
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
    
class ModifierOrdonnanceAPIV(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def put(self, request, ordonnance_id):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        return self.update_ordonnance(request, ordonnance_id, partial=False)

    def patch(self, request, ordonnance_id):
        
        return self.update_ordonnance(request, ordonnance_id, partial=True)

    def update_ordonnance(self, request, ordonnance_id, partial):
        
        try:
            ordonnance = Ordonnance.objects.get(id=ordonnance_id)
        except Ordonnance.DoesNotExist:
            return Response(
                {'error': 'ordonnance  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrdonnanceSerializer(ordonnance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
    

class ModifierConsultationAPIV(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def put(self, request, consultation_id):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)
 
        return self.update_consultation(request, consultation_id, partial=False)

    def patch(self, request, consultation_id):
        
        return self.update_consultation(request, consultation_id, partial=True)

    def update_consultation(self, request, consultation_id, partial):
        
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': 'consultation  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConsultationSerializer(consultation, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        


class ModifierResumeAPIV(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def put(self, request, resume_id):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        return self.update_resume(request, resume_id, partial=False)

    def patch(self, request, resume_id):
        
        return self.update_resume(request, resume_id, partial=True)

    def update_resume(self, request, resume_id, partial):
        
        try:
            resume = Resume.objects.get(id=resume_id)
        except Resume.DoesNotExist:
            return Response(
                {'error': 'Resume  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ResumerSerializer(resume, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        


class RechercheOrdonnanceAPIV(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not self.check_user_role(request.user, ['technicien','patient'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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


class RechercheResume(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        if not self.check_user_role(request.user, ['technicien','patient'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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


class ValidationOrdonnance(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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

