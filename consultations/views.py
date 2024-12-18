from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Consultation , Ordonnance , Technician , DossierPatient
from .serializers import ConsultationSerializer , OrdonnanceSerializer



class OrdonnanceCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrdonnanceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()  # Sauvegarde l'ordonnance
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ConsultationCreateView(APIView):
    """
    Vue pour créer une consultation avec validations dans la vue.
    """

    def post(self, request, *args, **kwargs):
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

        # Sérialisation et sauvegarde
        serializer = ConsultationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    



class SupprimerConsultationAPIView(APIView):
    def delete(self, request, consultation_id):
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

class SupprimerOrdonnanceAPIView(APIView):
    def delete(self, request, ordonnance_id):
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
    


class ModifierOrdonnanceAPIV(APIView):
    

    def put(self, request, ordonnance_id):
        
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
    

class ModifierConsultationAPIV(APIView):
    

    def put(self, request, consultation_id):
        
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
        




class RechercheOrdonnanceAPIV(APIView):
    def get(self, request):
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


import random


class ValidationOrdonnance(APIView):
    def post(self, request, pk):
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

