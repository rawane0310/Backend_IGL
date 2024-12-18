from rest_framework import serializers
from accounts.models import Certificat

class CertificatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificat
        fields = ['id', 'date', 'medecin', 'contenu', 'patient']
