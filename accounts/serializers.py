
from rest_framework import serializers
from .models import Patient, User, DossierPatient, Technician , SoinInfermier, ExamenBiologique, ExamenRadiologique , Medicament , Ordonnance , OrdonnanceMedicament, Consultation

class PatientSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Patient
        fields = [
            'user', 'nom', 'prenom', 'date_naissance', 'adresse', 
            'tel', 'mutuelle', 'medecin_traitant', 'personne_a_contacter', 
            'qr', 'nss'
        ]
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        patient = Patient.objects.create(user=user, **validated_data)
        return patient

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hashing the password
        user.save()  # Save the user to the database
        return user


class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ['nom', 'dose', 'frequence', 'duree']

    def create(self, validated_data):
        # Crée un objet Medicament et le sauvegarde dans la base de données
        return Medicament.objects.create(**validated_data)

class DossierPatientSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    historiqueConsultation = serializers.PrimaryKeyRelatedField(
        queryset=Consultation.objects.all(),
        many=True,
        required=False
    )
    soins_infirmiers = serializers.PrimaryKeyRelatedField(
        queryset=SoinInfermier.objects.all(),
        many=True,
        required=False
    )
    examen_bio = serializers.PrimaryKeyRelatedField(
        queryset=ExamenBiologique.objects.all(),
        many=True,
        required=False
    )
    examen_radio = serializers.PrimaryKeyRelatedField(
        queryset=ExamenRadiologique.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = DossierPatient
        fields = ['patient', 'soins_infirmiers', 'examen_bio', 'examen_radio']

    def create(self, validated_data):
        soins_infirmiers = validated_data.pop('soins_infirmiers', [])
        examens_bio = validated_data.pop('examen_bio', [])
        examens_radio = validated_data.pop('examen_radio', [])

        # Création de l'instance du DossierPatient
        dossier = DossierPatient.objects.create(**validated_data)

        # Ajout des relations Many-to-Many
        dossier.soins_infirmiers.set(soins_infirmiers)
        dossier.examen_bio.set(examens_bio)
        dossier.examen_radio.set(examens_radio)

        return dossier
    
class OrdonnanceMedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdonnanceMedicament
        fields = ['ordonnance', 'medicament']

class OrdonnanceSerializer(serializers.ModelSerializer):
    medicaments = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = Ordonnance
        fields = ['date', 'medicaments', 'validation']

    def create(self, validated_data):
        # Extraire la liste des médicaments
        medicaments_ids = validated_data.pop('medicaments', [])
        ordonnance = Ordonnance.objects.create(**validated_data)

        # Associer les médicaments via le modèle intermédiaire
        for medicament_id in medicaments_ids:
            medicament = Medicament.objects.get(id=medicament_id)
            OrdonnanceMedicament.objects.create(
                ordonnance=ordonnance,
                medicament=medicament
            )

        return ordonnance

class SoinInfermierSerializer(serializers.ModelSerializer):
    infirmier = serializers.PrimaryKeyRelatedField(queryset=Technician.objects.all())
    medicament_administré = serializers.PrimaryKeyRelatedField(queryset=Medicament.objects.all(), many=True)

    class Meta:
        model = SoinInfermier
        fields = ['date', 'infirmier', 'medicament_administré', 'observation', 'soin_realise']

    def create(self, validated_data):
        medicaments_data = validated_data.pop('medicament_administré', [])
        soin_infirmier = SoinInfermier.objects.create(**validated_data)
        soin_infirmier.medicament_administré.set(medicaments_data)
        return soin_infirmier
