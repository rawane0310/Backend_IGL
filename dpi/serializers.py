from rest_framework import serializers
from accounts.models import DossierPatient

class DossierPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierPatient
        fields = ['id', 'patient', 'qr']
        read_only_fields = ['qr']  # QR sera généré automatiquement
