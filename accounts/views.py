from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer ,TechnicianSerializer , PatientSerializer , AdminSerializer ,AdminstratifSerializer
from .models import User , Technician , Patient , Admin , Administratif , DossierPatient


from datetime import timedelta
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer ,LogoutUserSerializer
#from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.exceptions import APIException
from .mixin import CheckUserRoleMixin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RegisterUserView(APIView, CheckUserRoleMixin):
    """
    API view to register a new user. Only accessible to users with the 'admin' role.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Registers a new user. Only accessible to users with the 'admin' role.",
        responses={
            201: openapi.Response('User registered successfully'),
            400: 'Bad request - invalid data.',
            403: 'Forbidden - You do not have permission to create this resource.',
        },
        request_body=UserRegistrationSerializer,
    )
    def post(self, request):

        serializer = UserRegistrationSerializer(data=request.data)

        # Validate the serializer
        if serializer.is_valid():

            user = serializer.save()
            user_data = UserRegistrationSerializer(user).data
            return Response(user_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###########################################################################################################################################

# Custom Login View
class LoginView(TokenObtainPairView, CheckUserRoleMixin):
    """
    Custom login view that returns JWT access and refresh tokens along with the user's role.
    The refresh token is stored in an HttpOnly cookie for secure client-side access.
    """

    serializer_class = CustomTokenObtainPairSerializer  # Custom serializer for login

    @swagger_auto_schema(
        operation_description="Login and obtain JWT tokens along with user role and DossierPatient ID (if user is a patient).",
        responses={
            200: openapi.Response(
                description="Login successful, JWT access and refresh tokens are returned.",
                examples={
                    "application/json": {
                        "access": "access_token_example",
                        "role": "patient",
                        "dossier_id": 1,
                    }
                },
            ),
            401: "Unauthorized, invalid credentials",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user login.

        This method authenticates the user, generates access and refresh tokens,
        and sets the refresh token as an HttpOnly cookie.
        """
        # Call the original post method to get the tokens (access and refresh)
        response = super().post(request, *args, **kwargs)
        access_token = response.data.get('access')
        refresh_token = response.data.get('refresh')
        user = self.get_user_from_request(request)
        role = user.role if user else None

        response.data['nom'] = user.first_name
        response.data['prenom'] = user.last_name
        response.data['userID'] = user.id


        # Add role to the response data
        response.data['role'] = role
        if role == 'technicien':
            # Retrieve and include the technician role
            try:
                technician = Technician.objects.get(user=user)
                response.data['technician_role'] = technician.role
            except Technician.DoesNotExist:
                response.data['technician_role'] = None 



        if role == 'patient':
            try:
                patient = Patient.objects.get(user=user)
                dossier = DossierPatient.objects.get(patient=patient)
                response.data['dossier_id'] = dossier.id  
            except Patient.DoesNotExist:
                response.data['dossier_id'] = None  #
            except DossierPatient.DoesNotExist:
                response.data['dossier_id'] = None 

        # Set the refresh token as a cookie
        response.set_cookie(
            'refreshToken',
            refresh_token,
            max_age=timedelta(days=7),  # Set cookie expiration
            httponly=True,  # Prevent JavaScript access
            secure=True,  # Only send the cookie over HTTPS
            samesite='Strict',  # Strict mode to prevent CSRF issues
        )
        # Return the response with the access token in the body
        return response

    def get_user_from_request(self, request):
        """
        Retrieve user from the request data and validate it.

        This method uses the custom serializer to validate the user credentials.
        """
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        return ser.user

###########################################################################################################################################


class LogoutAPIView(APIView, CheckUserRoleMixin):
    """
    API view to handle user logout by blacklisting the refresh token.
    Requires an authenticated user with a valid refresh token.
    The access token should be included in the Authorization header.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutUserSerializer

    @swagger_auto_schema(
        operation_description="Logs out the user by blacklisting the refresh token. "
                              "The access token should be included in the Authorization header as a Bearer token.",
        responses={
            204: "Successfully logged out.",
            400: "Bad request - invalid or missing refresh token.",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='The refresh token to blacklist'),
            },
            required=['refresh'],
        ),
        security=[{'Bearer': []}],  # Indicating the use of Bearer token for authentication
    )
    def post(self, request, *args, **kwargs):
        """
        Logs out the user by invalidating the provided refresh token.
        """
        # Pass the incoming request data directly to the serializer
        serializer = self.serializer_class(data=request.data)

        # Validate the serializer
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If valid, save (perform logout logic)
        serializer.save()

        # Return a response indicating successful logout
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)

###########################################################################################################################################


class UserView(APIView, CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    # Create a new user (POST)
    """
    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
    # Update an existing user (PUT)
    @swagger_auto_schema(
        operation_description="Update an existing user's details. This action can be performed by an 'admin' or the user themselves.",
        responses={
            200: openapi.Response('User updated successfully', UserSerializer),
            400: 'Bad request - invalid data provided',
            403: 'Forbidden - You do not have permission to modify this resource',
            404: 'User not found',
        }
    )
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
    # Delete a user (DELETE)
    @swagger_auto_schema(
        operation_description="Delete a user. This action can only be performed by an 'admin'.",
        responses={
            200: 'User deleted successfully',
            403: 'Forbidden - You do not have permission to delete this resource',
            404: 'User not found',
        }
    )   
    def delete(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=kwargs.get('pk'))
            user.delete()
            return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        


###########################################################################################################################################


class PatientView(APIView, CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new patient. Only accessible to users with 'administratif' or 'technicien' roles,'medecin'.",
        operation_summary="Create a new patient",
        responses={
            201: openapi.Response('Patient created successfully', PatientSerializer),
            400: 'Bad request - invalid data provided',
            403: 'Forbidden - You do not have permission to create this resource'
        },
        request_body=PatientSerializer,
    )
    def post(self, request, *args, **kwargs):

        if not self.check_user_role(request.user, ['administratif'],['medecin']):

            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Create a new patient
        patient = PatientSerializer(data=request.data)
        if patient.is_valid():
            patient.save()
            return Response(patient.data, status=status.HTTP_201_CREATED)
        return Response(patient.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Update an existing patient. Only accessible to users with 'administratif' or  'medecin'.",
        operation_summary="Update an existing patient",
        responses={
            200: openapi.Response('Patient updated successfully', PatientSerializer),
            400: 'Bad request - invalid data provided',
            403: 'Forbidden - You do not have permission to modify this resource',
            404: 'Patient not found'
        },
        request_body=PatientSerializer,
    )
    def put(self, request, *args, **kwargs):

        if not self.check_user_role(request.user, ['administratif'],['medecin']):

            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Update an existing patient
        try:
            # Retrieve patient by patient_id from URL
            patient = Patient.objects.get(id=kwargs['patient_id'])
        except Patient.DoesNotExist:
            return Response({'detail': 'Patient not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the new data from the request
        patient_data = request.data
        
        # Process patient data as needed (similar to original code)
        # ...

        # Save the updated patient
        patient.save()
        return Response(PatientSerializer(patient).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete a patient. Only accessible to users with 'administratif' or 'medecin'.",
        operation_summary="Delete a patient",
        responses={
            204: 'Patient deleted successfully',
            403: 'Forbidden - You do not have permission to delete this resource',
            404: 'Patient not found'
        }
    )
    def delete(self, request, *args, **kwargs):

        if not self.check_user_role(request.user, ['administratif'],['medecin']):

            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Delete an existing patient
        try:
            # Retrieve patient by patient_id from URL
            patient = Patient.objects.get(id=kwargs['patient_id'])
            patient.delete()
            return Response({'detail': 'Patient deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Patient.DoesNotExist:
            return Response({'detail': 'Patient not found.'}, status=status.HTTP_404_NOT_FOUND)

###########################################################################################################################################







class TechnicianView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

     # Create a new technician (POST)
    # Create a new technician (POST)
    @swagger_auto_schema(
        operation_description="Create a new technician. This action can only be performed by an 'admin'.",
        responses={
            201: openapi.Response('Technician created successfully', TechnicianSerializer),
            400: 'Bad request - invalid data provided',
            403: 'Forbidden - You do not have permission to create this resource',
        }
    )
    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TechnicianSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update an existing technician (PUT)
     # Update an existing technician (PUT)
    # Update an existing technician (PUT)
    @swagger_auto_schema(
        operation_description="Update an existing technician. This action can only be performed by a 'technicien' (medecin, laborantin, infermier, radiologue).",
        responses={
            200: openapi.Response('Technician updated successfully', TechnicianSerializer),
            400: 'Bad request - invalid data provided',
            403: 'Forbidden - You do not have permission to modify this resource',
            404: 'Technician not found',
        }
    )
    def put(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['technicien']):
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
    @swagger_auto_schema(
        operation_description="Delete a technician. This action can only be performed by an 'admin'.",
        responses={
            200: 'Technician deleted successfully',
            403: 'Forbidden - You do not have permission to delete this resource',
            404: 'Technician not found',
        }
    )

    def delete(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            technician = Technician.objects.get(id=kwargs.get('pk'))
            technician.delete()
            return Response({"message": "Technician deleted successfully."}, status=status.HTTP_200_OK)
        except Technician.DoesNotExist:
            return Response({"error": "Technician not found."}, status=status.HTTP_404_NOT_FOUND)
        


###########################################################################################################################################


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


###########################################################################################################################################






class AdminView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

     # Create a new admin (POST)
    @swagger_auto_schema(
        operation_description="Create a new admin. This action can only be performed by an 'admin'.",
        request_body=AdminSerializer,
        responses={
            201: openapi.Response('Admin created successfully', AdminSerializer),
            400: 'Bad request - invalid data provided',
            403: 'Forbidden - You do not have permission to create this resource',
        }
)

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


    # Get a specific admin or list of admins (GET)
    @swagger_auto_schema(
        operation_description="Get a specific admin or a list of admins. This action can only be performed by an 'admin'.",
        responses={
            200: openapi.Response('Admin details', AdminSerializer),
            404: 'Admin not found',
            403: 'Forbidden - You do not have permission to view this resource',
        }
    )
   
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
    

    @swagger_auto_schema(
        operation_description="Update an existing admin. This action can only be performed by an 'admin'.",
        request_body=AdminSerializer,
        responses={
            200: openapi.Response('Admin updated successfully', AdminSerializer),
            400: 'Bad request - invalid data provided',
            403: 'Forbidden - You do not have permission to modify this resource',
            404: 'Admin not found',
        }
    )

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
    
    @swagger_auto_schema(
        operation_description="Delete an existing admin. This action can only be performed by an 'admin'.",
        responses={
            204: 'Admin deleted successfully',
            403: 'Forbidden - You do not have permission to delete this resource',
            404: 'Admin not found',
        }
    )

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



###########################################################################################################################################



class TechnicianSearchByRoleView(APIView):
    """
    API endpoint to search for technicians by role.
    """

    @swagger_auto_schema(
        operation_description="Search technicians by role.",
        manual_parameters=[
            openapi.Parameter(
                name="role",
                in_=openapi.IN_QUERY,
                description="The role to search for (e.g., 'medecin', 'infermier').",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="List of technicians matching the specified role.",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "name": "Amira Mmr",
                            "role": "medecon",
                            "email": "amira.mmr@example.com"
                        },
                        {
                            "id": 2,
                            "name": "Amani Mmr",
                            "role": "infermier",
                            "email": "amani.mmrh@example.com"
                        }
                    ]
                }
            ),
            400: openapi.Response(
                description="Invalid or missing 'role' parameter.",
                examples={
                    "application/json": {
                        "detail": "Role is required."
                    }
                }
            ),
            404: openapi.Response(
                description="No technicians found for the specified role.",
                examples={
                    "application/json": {
                        "detail": "No technicians found with the specified role."
                    }
                }
            ),
            500: openapi.Response(
                description="An internal server error occurred.",
                examples={
                    "application/json": {
                        "detail": "An error occurred."
                    }
                }
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        # Get 'role' from query parameters
        role = request.GET.get('role', None)
        
        # Check if 'role' is provided
        if not role:
            return Response({"detail": "Role is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Search for technicians by role
            technicians = Technician.objects.filter(role__icontains=role)  # Use icontains for case-insensitive search
            
            if not technicians:
                return Response({"detail": "No technicians found with the specified role."}, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize the technicians data
            technician_serializer = TechnicianSerializer(technicians, many=True) # many since multiple objects are returned
            
            # Return the technician data in the response
            return Response(technician_serializer.data)
        
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

###########################################################################################################################################


class TechnicianSearchByIDView(APIView):
    """
    API endpoint to search for a technician by ID.
    """

    @swagger_auto_schema(
        operation_description="Search for a technician by their unique ID.",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_QUERY,
                description="The unique ID of the technician to search for.",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Technician details for the specified ID.",
                examples={
                    "application/json":  {
                            "id": 1,
                            "name": "Amira Mmr",
                            "role": "medecon",
                            "email": "amira.mmr@example.com"
                        },
                }
                
            ),
            400: openapi.Response(
                description="Invalid or missing 'id' parameter.",
                examples={
                    "application/json": {
                        "details": "ID is required"
                    }
                }
            ),
            404: openapi.Response(
                description="No technician found for the specified ID.",
                examples={
                    "application/json": {
                        "details": "No technician found with this id"
                    }
                }
            ),
            500: openapi.Response(
                description="An internal server error occurred.",
                examples={
                    "application/json": {
                        "details": "An error occurred."
                    }
                }
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        # Get 'id' from query parameters
        id = request.GET.get('id', None)

        # Case when 'id' is not provided
        if not id:
            return Response({"details": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Search for the technician with the provided ID
            technician = Technician.objects.get(id=id)

            # Serialize the technician object
            technician_ser = TechnicianSerializer(technician)   
             # Return the technician object in the response
            return Response(technician_ser.data)
        except Technician.DoesNotExist:
            return Response({"details": "No technician found with this id"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

 

 ## accounts : 

 
 # test fonctionel
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from rest_framework import serializers
from  .forms import LoginForm,PatientAccountForm,PatientProfileForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            login(request, user)
            return JsonResponse({"status": "success", "message": "Login successful"})
           
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


           


def create_patient_account(request):
    if request.method == 'POST':
        form = PatientAccountForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user=User.objects.create (email=email, password=password,role="patient")
            return JsonResponse({"status": "success", "message": "Account created", "email": email})
    else:
        form = PatientAccountForm()
    return render(request, 'register.html', {'form': form})



def create_patient_profile(request):
    if request.method == 'POST':
        form = PatientProfileForm(request.POST)

        if form.is_valid():
            # Récupérer les données du formulaire
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            adresse = form.cleaned_data['adresse']
            date_naissance = form.cleaned_data['date_naissance']
            tel = form.cleaned_data['tel']
            mutuelle = form.cleaned_data['mutuelle']
            medecin_traitant_email = form.cleaned_data['medecin_traitant_email']
            personne_a_contacter = form.cleaned_data['personne_a_contacter']
            nss = form.cleaned_data['nss']
            user_email = form.cleaned_data['user_email']

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

        # Enregistrer le patient dans la base de données
        patient = Patient.objects.create(
                nom=nom,
                prenom=prenom,
                adresse=adresse,
                date_naissance=date_naissance,
                tel=tel,
                mutuelle=mutuelle,
                medecin_traitant=medecin_traitant,
                personne_a_contacter=personne_a_contacter,
                nss=nss,
                user=user
            )

        return redirect(f"/accounts/patientT/{patient.id}/")

        #return JsonResponse({"status": "success", "message": "Profile created", "patient_id": patient.id})
    else:
        form = PatientProfileForm()
    return render(request, 'patient.html', {'form': form})


def patient_profile(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'patient_profile.html', {'patient': patient})

