from rest_framework import serializers
from accounts.models import Consultation
from accounts.models import Technician, Ordonnance, DossierPatient  # Import des modèles associés



class OrdonnanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ordonnance
        fields = ['id', 'date', 'validation']  # Inclut tous les champs du modèle
        

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'

   


