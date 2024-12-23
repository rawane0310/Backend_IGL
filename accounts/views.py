from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer ,TechnicianSerializer , PatientSerializer , AdminSerializer, AdminstratifSerializer
from .models import User , Technician , Patient , Admin 
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from .mixin import CheckUserRoleMixin

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
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
        if not self.check_user_role(request.user, ['admin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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

"""
from rest_framework import generics
from .models import Patient , DossierPatient, Medicament , Ordonnance , SoinInfermier
from .serializers import PatientSerializer, UserSerializer, DossierPatientSerializer , MedicamentSerializer , OrdonnanceSerializer , SoinInfermierSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import DestroyAPIView






class CreatePatientView(generics.CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer 

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_201_CREATED)


class CreateDossierPatientView(generics.CreateAPIView):
    serializer_class = DossierPatientSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_201_CREATED)
    
class CreateMedicamentView(generics.CreateAPIView):
    serializer_class = MedicamentSerializer

    def create(self, request, *args, **kwargs):
        # Utilise la logique par défaut pour créer l'objet
        response = super().create(request, *args, **kwargs)
        # Retourne une réponse avec les données du médicament inséré
        return Response(response.data, status=status.HTTP_201_CREATED)    

class CreateOrdonnanceView(generics.CreateAPIView):
    serializer_class = OrdonnanceSerializer

    def create(self, request, *args, **kwargs):
        # Appeler la logique par défaut de DRF
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_201_CREATED)

class CreateSoinInfermierView(generics.CreateAPIView):
    serializer_class = SoinInfermierSerializer

    def create(self, request, *args, **kwargs):
        # Utiliser la logique DRF par défaut et personnaliser la réponse
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_201_CREATED)
    
class DeleteSoinInfermierView(DestroyAPIView):
    queryset = SoinInfermier.objects.all()  # Définir le queryset pour trouver l'objet à supprimer
    serializer_class = SoinInfermierSerializer  # Le serializer utilisé pour la suppression

    def delete(self, request, *args, **kwargs):
        
        try:
            # Appel de la méthode générique de suppression
            return super().delete(request, *args, **kwargs)
        except SoinInfermier.DoesNotExist:
            return Response({"detail": "SoinInfirmier non trouvé"}, status=status.HTTP_404_NOT_FOUND)    

class DeleteMedicamentView(DestroyAPIView):
    queryset = Medicament.objects.all()  # Définir le queryset pour trouver l'objet à supprimer
    serializer_class = MedicamentSerializer  # Le serializer utilisé pour la suppression

    def delete(self, request, *args, **kwargs):
        
        try:
            # Appel de la méthode générique de suppression
            return super().delete(request, *args, **kwargs)
        except Medicament.DoesNotExist:
            return Response({"detail": "Medicament non trouvé"}, status=status.HTTP_404_NOT_FOUND)          
"""