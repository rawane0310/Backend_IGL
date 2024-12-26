from rest_framework import serializers
from accounts.models import DossierPatient , Patient ,Technician , User

class DossierPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierPatient
        fields = ['id', 'patient', 'qr']
        read_only_fields = ['qr']  # QR sera généré automatiquement


# had serializer ela jal bach ki tdir recherche par nss w truturni le patient ,
#  fi la partie te3 medecin traitant t'afficher le nom et le prenom de medecin au lieu de id te3 technicein 

class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = ['id','nom', 'prenom'] 






# par nss + par qr code bach yruturni le nom et le prenom de medecin traitent au lieu de id 
class PatientSerializer(serializers.ModelSerializer):
    # Nested serializer for medecin_traitant
    medecin_traitant = TechnicianSerializer()

    class Meta:
        model = Patient
        # Exclude the 'user' field and include the necessary fields
        fields = ['id','nom', 'prenom', 'date_naissance', 'adresse', 'tel', 'mutuelle', 
                  'medecin_traitant', 'personne_a_contacter', 'nss']
        # 'user' field is not included, so it will not appear in the serialized response



class PatientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Patient
        fields = '__all__' 
        extra_kwargs = {
            'user': {'write_only': True}, 
        }

    def create(self, validated_data):
        # Remove password from validated_data before creating Patient instance
        password = validated_data.pop('password')
        user = User.objects.create_user(
            email=validated_data['user'].email, 
            password=password, 
            role='patient'
        )
        validated_data['user'] = user
        return Patient.objects.create(**validated_data)
    


class UserPatientSerializer (serializers.ModelSerializer) : 
    email = serializers.EmailField(write_only=True)  # Add a field for user email
    password = serializers.CharField(write_only=True)  # Keep write_only=True

    class Meta : 
        model = Patient 
        fields =  [
            'nom', 'prenom', 'date_naissance', 'adresse', 'tel', 'mutuelle', 
            'password', 'personne_a_contacter', 'nss', 'email' , 'medecin_traitant'
        ]  


