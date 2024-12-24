from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer ,TechnicianSerializer , PatientSerializer , AdminSerializer, AdminstratifSerializer
from .models import User , Technician , Patient , Admin ,Administratif
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer ,LogoutUserSerializer
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.exceptions import APIException
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from .mixin import CheckUserRoleMixin





class RegisterUserView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Custom Login View
class LoginView(TokenObtainPairView,CheckUserRoleMixin):
    
    serializer_class = CustomTokenObtainPairSerializer  # Your custom serializer
    
    def post(self, request, *args, **kwargs):
        # Call the original post method to get the tokens (access and refresh)
        response = super().post(request, *args, **kwargs)
        # Extract the access and refresh tokens from the response data
        access_token = response.data.get('access')
        refresh_token = response.data.get('refresh')
        user = self.get_user_from_request(request)
        role = user.role if user else None

        # Add role to the response data
        response.data['role'] = role
        
        # Set the refresh token as a cookie
        response.set_cookie(
            'refreshToken', 
            refresh_token, 
            max_age=timedelta(days=7),  # Set cookie expiration
            httponly=True,  # Prevent JavaScript access
            secure=True,    # Only send the cookie over HTTPS
            samesite='Strict'  # Strict mode to prevent CSRF issues
        )
        # Return the response with the access token in the body
        return response
    
    def get_user_from_request(self , request ) : 
        ser = self.get_serializer(data = request.data) 
        ser.is_valid(raise_exception=True)
        return ser.user


class LogoutAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutUserSerializer
    def post(self, request, *args, **kwargs):
        # Pass the incoming request data directly to the serializer
        serializer = self.serializer_class(data=request.data)
        
        # Validate the serializer
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # If valid, save (perform logout logic)
        serializer.save()
        # Return a response indicating successful logout
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)


class UserView(APIView, CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    # Create a new user (POST)
    
    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update an existing user (PUT)
    def put(self, request, *args, **kwargs):
       
        try:
            user = User.objects.get(id=kwargs.get('pk'))
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)  # `partial=True` for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a user (DELETE)
    def delete(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=kwargs.get('pk'))
            user.delete()
            return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class PatientView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['administratif','technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Create a new patient
        patient = PatientSerializer(data=request.data)
        if patient.is_valid():
            patient.save()
            return Response(patient.data, status=status.HTTP_201_CREATED)
        return Response(patient.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['administratif','technicien'],['medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Update an existing patient
        try:
            # Retrieve patient by patient_id from URL
            patient = Patient.objects.get(id=kwargs['patient_id'])
        except Patient.DoesNotExist:
            return Response({'detail': 'Patient not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the new data from the request
        patient_data = request.data
        
        # search for the user and the doctor based on their email addresses
        if 'user_email' in patient_data:
            try:
                # Look for user by email
                user = User.objects.get(email=patient_data['user_email'])
                patient.user = user
            except User.DoesNotExist:
                return Response({'detail': f'User with email {patient_data["user_email"]} not found.'}, 
                                status=status.HTTP_400_BAD_REQUEST)

        if 'medecin_traitant_email' in patient_data:
            try:
                # Look for technician by email
                technicien_user = User.objects.get(email=patient_data['medecin_traitant_email'])
                medecin_traitant = technicien_user.technician  # Access the Technician object
                patient.medecin_traitant = medecin_traitant
            except User.DoesNotExist:
                return Response({'detail': f'Technician with email {patient_data["medecin_traitant_email"]} not found.'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            except Technician.DoesNotExist:
                return Response({'detail': 'The user is not a technician.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update other patient fields (only if provided in the request)
        patient.nom = patient_data.get('nom', patient.nom)
        patient.prenom = patient_data.get('prenom', patient.prenom)
        patient.date_naissance = patient_data.get('date_naissance', patient.date_naissance)
        patient.adresse = patient_data.get('adresse', patient.adresse)
        patient.tel = patient_data.get('tel', patient.tel)
        patient.mutuelle = patient_data.get('mutuelle', patient.mutuelle)
        patient.personne_a_contacter = patient_data.get('personne_a_contacter', patient.personne_a_contacter)
        patient.nss = patient_data.get('nss', patient.nss)
        
        # Save the updated patient
        patient.save()
        return Response(PatientSerializer(patient).data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['administratif','technicien'],['medecin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Delete an existing patient
        try:
            # Retrieve patient by patient_id from URL
            patient = Patient.objects.get(id=kwargs['patient_id'])
            patient.delete()
            return Response({'detail': 'Patient deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Patient.DoesNotExist:
            return Response({'detail': 'Patient not found.'}, status=status.HTTP_404_NOT_FOUND)






class TechnicianView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    # Create a new technician (POST)
    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TechnicianSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update an existing technician (PUT)
    def put(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['technicien'],['medecin','laborantin','infermier','radiologue']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            technician = Technician.objects.get(id=kwargs.get('pk'))
        except Technician.DoesNotExist:
            return Response({"error": "Technician not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TechnicianSerializer(technician, data=request.data, partial=True)  # `partial=True` for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a technician (DELETE)
    def delete(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            technician = Technician.objects.get(id=kwargs.get('pk'))
            technician.delete()
            return Response({"message": "Technician deleted successfully."}, status=status.HTTP_200_OK)
        except Technician.DoesNotExist:
            return Response({"error": "Technician not found."}, status=status.HTTP_404_NOT_FOUND)
        
class AdministratifView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        """
        Create a new admin using the user's email.
        """
        serializer = AdminstratifSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new admin
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
     # Update an existing administratif (PUT)
    def put(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['administratif']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            administratif = Administratif.objects.get(id=kwargs.get('pk'))
        except Administratif.DoesNotExist:
            return Response({"error": "Administratif not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminstratifSerializer(administratif, data=request.data, partial=True)  # `partial=True` for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete an administratif (DELETE)
    def delete(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['administratif']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            administratif = Administratif.objects.get(id=kwargs.get('pk'))
            administratif.delete()
            return Response({"message": "administratif deleted successfully."}, status=status.HTTP_200_OK)
        except Administratif.DoesNotExist:
            return Response({"error": "Administratif not found."}, status=status.HTTP_404_NOT_FOUND)

class AdminView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        """
        Create a new admin using the user's email.
        """
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new admin
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        """
        Get a specific admin or a list of admins.
        """
        if 'pk' in kwargs:  # If a pk is provided in the URL (GET /admin/<pk>/)
            try:
                admin_instance = Admin.objects.get(pk=kwargs['pk'])
            except Admin.DoesNotExist:
                return Response({'detail': 'Admin not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = AdminSerializer(admin_instance)
            return Response(serializer.data)

        # If no pk is provided, return a list of all admins
        admins = Admin.objects.all()
        serializer = AdminSerializer(admins, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        """
        Update an existing admin using the user's email.
        """
        try:
            admin_instance = Admin.objects.get(pk=kwargs['pk'])
        except Admin.DoesNotExist:
            return Response({'detail': 'Admin not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the data and validate using the serializer
        serializer = AdminSerializer(admin_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated admin
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        """
        Delete an existing admin.
        """
        try:
            admin_instance = Admin.objects.get(pk=kwargs['pk'])
        except Admin.DoesNotExist:
            return Response({'detail': 'Admin not found.'}, status=status.HTTP_404_NOT_FOUND)

        admin_instance.delete()
        return Response({'detail': 'Admin deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)






