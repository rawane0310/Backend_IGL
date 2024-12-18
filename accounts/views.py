"""
from rest_framework import generics
from .models import Patient , DossierPatient, Medicament , Ordonnance , SoinInfermier
from .serializers import PatientSerializer, UserSerializer, DossierPatientSerializer , MedicamentSerializer , OrdonnanceSerializer , SoinInfermierSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import DestroyAPIView






class CreatePatientView(generics.CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer 

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_201_CREATED)


class CreateDossierPatientView(generics.CreateAPIView):
    serializer_class = DossierPatientSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_201_CREATED)
    
class CreateMedicamentView(generics.CreateAPIView):
    serializer_class = MedicamentSerializer

    def create(self, request, *args, **kwargs):
        # Utilise la logique par défaut pour créer l'objet
        response = super().create(request, *args, **kwargs)
        # Retourne une réponse avec les données du médicament inséré
        return Response(response.data, status=status.HTTP_201_CREATED)    

class CreateOrdonnanceView(generics.CreateAPIView):
    serializer_class = OrdonnanceSerializer

    def create(self, request, *args, **kwargs):
        # Appeler la logique par défaut de DRF
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_201_CREATED)

class CreateSoinInfermierView(generics.CreateAPIView):
    serializer_class = SoinInfermierSerializer

    def create(self, request, *args, **kwargs):
        # Utiliser la logique DRF par défaut et personnaliser la réponse
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_201_CREATED)
    
class DeleteSoinInfermierView(DestroyAPIView):
    queryset = SoinInfermier.objects.all()  # Définir le queryset pour trouver l'objet à supprimer
    serializer_class = SoinInfermierSerializer  # Le serializer utilisé pour la suppression

    def delete(self, request, *args, **kwargs):
        
        try:
            # Appel de la méthode générique de suppression
            return super().delete(request, *args, **kwargs)
        except SoinInfermier.DoesNotExist:
            return Response({"detail": "SoinInfirmier non trouvé"}, status=status.HTTP_404_NOT_FOUND)    

class DeleteMedicamentView(DestroyAPIView):
    queryset = Medicament.objects.all()  # Définir le queryset pour trouver l'objet à supprimer
    serializer_class = MedicamentSerializer  # Le serializer utilisé pour la suppression

    def delete(self, request, *args, **kwargs):
        
        try:
            # Appel de la méthode générique de suppression
            return super().delete(request, *args, **kwargs)
        except Medicament.DoesNotExist:
            return Response({"detail": "Medicament non trouvé"}, status=status.HTTP_404_NOT_FOUND)          
"""