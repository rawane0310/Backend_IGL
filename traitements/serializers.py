from rest_framework import serializers
from accounts.models import Ordonnance, SoinInfermier , Medicament







class SoinInfermierSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoinInfermier
        fields = ['id', 'date', 'infirmier', 'observation', 'soin_realise', 'dossier']
        



class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ['id', 'nom', 'dose', 'frequence', 'duree', 'ordonnance', 'soin']

    

        


