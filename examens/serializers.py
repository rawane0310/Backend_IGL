from rest_framework import serializers
from accounts.models import ResultatExamen , ExamenBiologique , ExamenRadiologique , RadiologyImage



class RadiologyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadiologyImage
        fields = ['id','examen_radiologique','image','uploaded_at']


class ExamenRadiologiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenRadiologique
        fields = ['id', 'date', 'technicien', 'radiologue', 'compte_rendu','description', 'dossier_patient']

class ResultatExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultatExamen
        fields = ['id', 'parametre', 'valeur', 'unite', 'commentaire', 'examen_biologique']

class ExamenBiologiqueSerializer(serializers.ModelSerializer):
    resultats = ResultatExamenSerializer(many=True, read_only=True)   
    class Meta:
        model = ExamenBiologique
        fields = ['id', 'date', 'technicien', 'laborantin', 'description', 'dossier_patient','resultats']