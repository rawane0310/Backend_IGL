from rest_framework import serializers
from .models import User ,Technician , Patient ,Admin ,Administratif

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import User

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from rest_framework_simplejwt.exceptions import TokenError


# ****************************************** auth ********************************************************

# Custom serializer to include user role in the JWT payload
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  # Add custom claims
        return token

# User Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# Serializer for logging out the user



class LogoutUserSerializer(serializers.Serializer):
    refresh = serializers.CharField()  # Expecting refresh token in the request body

    default_error_messages = {
        'bad_token': 'Token is expired or invalid.'
    }

    def validate(self, attrs):
        refresh = attrs.get('refresh')
        if not refresh:
            raise ValidationError({"refresh": "This field is required."})
        self.token = refresh
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()  # Blacklist the token (requires blacklisting enabled in SimpleJWT)
        except TokenError:
            raise ValidationError(self.default_error_messages['bad_token'])





class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},  #  password is write-only
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'patient')  
        )
        return user



class TechnicianSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Technician
        fields = ['nom', 'prenom', 'role', 'specialite', 'outils', 'user_email']

    def create(self, validated_data):
        # Extract the user_email and create the relation with the user
        email = validated_data.pop('user_email')
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError(f"No user found with email {email}")
        validated_data['user'] = user
        return Technician.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Extract the user_email from validated data
        user_email = validated_data.pop('user_email', None)

        if user_email:
            # If user_email is provided, update the user relation
            user = User.objects.filter(email=user_email).first()
            if not user:
                raise serializers.ValidationError(f"No user found with email {user_email}")
            instance.user = user

        # Update the other fields of Technician
        instance.nom = validated_data.get('nom', instance.nom)
        instance.prenom = validated_data.get('prenom', instance.prenom)
        instance.role = validated_data.get('role', instance.role)
        instance.specialite = validated_data.get('specialite', instance.specialite)
        instance.outils = validated_data.get('outils', instance.outils)

        instance.save()
        return instance
    
class AdminstratifSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)  # the email field to create/update admin

    class Meta:
        model = Administratif
        fields = ['id', 'nom', 'prenom', 'user_email']  # Include user_email instead of user

    def create(self, validated_data):
        #  User object by the provided email
        user_email = validated_data.pop('user_email')  # Extract user_email
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with email {user_email} not found.")
        
        # Create a new Admin object
        return Administratif.objects.create(user=user, **validated_data)



class AdminSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)  # the email field to create/update admin

    class Meta:
        model = Admin
        fields = ['id', 'nom', 'prenom', 'user_email']  # Include user_email instead of user

    def create(self, validated_data):
        #  User object by the provided email
        user_email = validated_data.pop('user_email')  # Extract user_email
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with email {user_email} not found.")
        
        # Create a new Admin object
        return Admin.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        # User object by the provided email for updates
        user_email = validated_data.pop('user_email', None)  # Extract user_email
        if user_email:
            try:
                user = User.objects.get(email=user_email)
                instance.user = user
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with email {user_email} not found.")

        # Update the admin fields
        instance.nom = validated_data.get('nom', instance.nom)
        instance.prenom = validated_data.get('prenom', instance.prenom)
        instance.save()
        return instance

"""""
class PatientSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)  # Add a field for user email
    medecin_traitant_email = serializers.EmailField(write_only=True)  # Add a field for the medecin_traitant email

    class Meta:
        model = Patient
        fields = [
            'nom', 'prenom', 'date_naissance', 'adresse', 'tel', 'mutuelle', 
            'medecin_traitant_email', 'personne_a_contacter', 'nss', 'user_email'
        ]  # Include medecin_traitant_email and user_email in the fields

    def create(self, validated_data):
        # Extract the user emails from the validated data
        user_email = validated_data.pop('user_email')
        medecin_traitant_email = validated_data.pop('medecin_traitant_email')
        
        # Fetch the User object for the patient using the provided email
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"No user found with email {user_email}")
        
        # Fetch the User object for the medecin_traitant (Technician) using the provided email
        try:
            technicien_user = User.objects.get(email=medecin_traitant_email)
            medecin_traitant = technicien_user.technician  # Access the Technician instance related to the User
        except User.DoesNotExist:
            raise serializers.ValidationError(f"No technician found with email {medecin_traitant_email}")
        except Technician.DoesNotExist:
            raise serializers.ValidationError(f"The user with email {medecin_traitant_email} is not a technician")

        # including the user and medecin_traitant in the validated data and create the patient
        patient = Patient.objects.create(
            user=user, 
            medecin_traitant=medecin_traitant, 
            **validated_data
        )
        return patient
    

"""
class PatientSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)  # Accept user_id instead of user_email
    medecin_traitant_id = serializers.IntegerField(write_only=True)  # Accept medecin_traitant_id instead of medecin_traitant_email
    class Meta:
        model = Patient
        fields = [
            'nom', 'prenom', 'date_naissance', 'adresse', 'tel', 'mutuelle', 
            'medecin_traitant_id', 'personne_a_contacter', 'nss', 'user_id'
        ]  # Include medecin_traitant_id and user_id in the fields
    def create(self, validated_data):
        # Extract the user and medecin_traitant ids from the validated data
        user_id = validated_data.pop('user_id')
        medecin_traitant_id = validated_data.pop('medecin_traitant_id')
        
        # Fetch the User object for the patient using the provided user_id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"No user found with ID {user_id}")
        
        # Fetch the Technician object for the medecin_traitant using the provided medecin_traitant_id
        try:
            medecin_traitant = Technician.objects.get(id=medecin_traitant_id)
        except Technician.DoesNotExist:
            raise serializers.ValidationError(f"No technician found with ID {medecin_traitant_id}")
        # Create the patient and include the user and medecin_traitant in the validated data
        patient = Patient.objects.create(
            user=user, 
            medecin_traitant=medecin_traitant, 
            **validated_data
        )
        return patient




#pour rechercher tech par role _ id 
class TechnicianSerializerSearch(serializers.ModelSerializer):
   # user_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Technician
        fields = "__all__"

