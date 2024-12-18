from rest_framework import serializers
from accounts.models import ResultatExamen , ExamenBiologique , ExamenRadiologique

class ExamenRadiologiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenRadiologique
        fields = ['id', 'date', 'technicien', 'image', 'compte_rendu', 'terminaison', 'dossier_patient']

class ExamenBiologiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenBiologique
        fields = ['id', 'date', 'technicien', 'terminaison', 'dossier_patient']

class ResultatExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultatExamen
        fields = ['id', 'parametre', 'valeur', 'unite', 'commentaire', 'examen_biologique']
