from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models  import ExamenRadiologique , ExamenBiologique , ResultatExamen, Technician
from .serializers import ExamenRadiologiqueSerializer , ExamenBiologiqueSerializer , ResultatExamenSerializer
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from accounts.mixin import CheckUserRoleMixin

class ResultatExamenView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not self.check_user_role(request.user, ['patient'],['laborantin','medecin']):
            return Response({'error': 'You do not have permission to get this resource.'}, status=status.HTTP_403_FORBIDDEN)

        resultats = ResultatExamen.objects.all()
        serializer = ResultatExamenSerializer(resultats, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not self.check_user_role(request.user,['laborantin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ResultatExamenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not self.check_user_role(request.user,['laborantin','medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            resultat = ResultatExamen.objects.get(pk=pk)
        except ResultatExamen.DoesNotExist:
            return Response({'error': 'Résultat d\'examen non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResultatExamenSerializer(resultat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not self.check_user_role(request.user,['laborantin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            resultat = ResultatExamen.objects.get(pk=pk)
            resultat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ResultatExamen.DoesNotExist:
            return Response({'error': 'Résultat d\'examen non trouvé'}, status=status.HTTP_404_NOT_FOUND)

class ExamenBiologiqueView(APIView):
    permission_classes = [IsAuthenticated]

    def check_user_role(self, user, allowed_roles=None):
        """
        Check if the authenticated user has a role of 'technicien' and if their technician role matches allowed roles.
        """
        if user.role != 'technicien':  # Only 'technicien' users are allowed
            return False

        # Check if the user has a related 'Technician' instance
        try:
            technician = user.technician  # Access the related 'Technician' model
            if allowed_roles and technician.role in allowed_roles:
                return True  # User's technician role matches allowed roles
            return False  # User's technician role does not match allowed roles
        except Technician.DoesNotExist:
            return False  # No related Technician instance
        

    def get(self, request):
        
        examens = ExamenBiologique.objects.all()
        serializer = ExamenBiologiqueSerializer(examens, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not self.check_user_role(request.user, allowed_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ExamenBiologiqueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not self.check_user_role(request.user, allowed_roles=['medecin', 'laborantin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            examen = ExamenBiologique.objects.get(pk=pk)
        except ExamenBiologique.DoesNotExist:
            return Response({'error': 'Examen Biologique non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExamenBiologiqueSerializer(examen, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not self.check_user_role(request.user, allowed_roles=['medecin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            examen = ExamenBiologique.objects.get(pk=pk)
            examen.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ExamenBiologique.DoesNotExist:
            return Response({'error': 'Examen Biologique non trouvé'}, status=status.HTTP_404_NOT_FOUND)

class ExamenRadiologiqueView(APIView):
    permission_classes = [IsAuthenticated]


    def check_user_role(self, user,allowed_roles=None):
        """
        Check if the authenticated user has a role of 'technicien' and, if so, if their related 'Technician' role is 'medecin'.
        """
        # First, check if the user has a role of 'technicien'
        if user.role != 'technicien':
            return False  # User is not a 'technicien', return False
        
        # Now check if the user has a related 'Technician' and if the role is 'medecin'
        try:
            technician = user.technician  # Access the related 'Technician' model
            if allowed_roles and technician.role in allowed_roles:
                return True  # User's technician role matches allowed roles
            return False  # User's technician role does not match allowed roles
        except Technician.DoesNotExist:
            return False  # No related Technician instance


    def get(self, request):
        
        examens = ExamenRadiologique.objects.all()
        serializer = ExamenRadiologiqueSerializer(examens, many=True)
        return Response(serializer.data)

    def post(self, request):
        
        if not self.check_user_role(request.user, allowed_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ExamenRadiologiqueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not self.check_user_role(request.user, allowed_roles=['medecin', 'radiologue']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            examen = ExamenRadiologique.objects.get(pk=pk)
        except ExamenRadiologique.DoesNotExist:
            return Response({'error': 'Examen Radiologique non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExamenRadiologiqueSerializer(examen, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not self.check_user_role(request.user, allowed_roles=['medecin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            examen = ExamenRadiologique.objects.get(pk=pk)
            examen.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ExamenRadiologique.DoesNotExist:
            return Response({'error': 'Examen Radiologique non trouvé'}, status=status.HTTP_404_NOT_FOUND)


class SearchExamenBiologiqueView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['patient'],['laborantin','medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        technicien = request.GET.get('technicien', None)
        date = request.GET.get('date', None)
        dossier = request.GET.get('dossier', None)
        description = request.GET.get('description', None)

        try:
            examens_bio = ExamenBiologique.objects.all()
            if technicien:
                examens_bio = examens_bio.filter(technicien__nom__icontains=technicien)
            if date:
                examens_bio = examens_bio.filter(date=date)
            if dossier:
                examens_bio = examens_bio.filter(dossier__icontains=dossier)
            if description:
                examens_bio = examens_bio.filter(description__icontains=description)

            examens_bio_serializer = ExamenBiologiqueSerializer(examens_bio, many=True)
            return Response(examens_bio_serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SearchExamenRadiologiqueView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['patient'],['radiologue','medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        technicien = request.GET.get('technicien', None)
        date = request.GET.get('date', None)
        dossier = request.GET.get('dossier', None)
        description = request.GET.get('description', None)

        try:
            examens_radio = ExamenRadiologique.objects.all()
            if technicien:
                examens_radio = examens_radio.filter(technicien__nom__icontains=technicien)
            if date:
                examens_radio = examens_radio.filter(date=date)
            if dossier:
                examens_radio = examens_radio.filter(dossier__icontains=dossier)
            if description:
                examens_radio = examens_radio.filter(description__icontains=description)

            examens_radio_serializer = ExamenRadiologiqueSerializer(examens_radio, many=True)
            return Response(examens_radio_serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SearchResultatBiologiqueByIdView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['patient'],['laborantin','medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        id_examen_bio = request.GET.get('idExamenBio', None)

        if not id_examen_bio:
            return Response({"detail": "idExamenBio is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resultat = ResultatExamen.objects.get(examen_biologique__id=id_examen_bio)

            if not resultat:
                return Response({"detail": "No result found for the given idExamenBio."}, status=status.HTTP_404_NOT_FOUND)

            resultat_serializer = ResultatExamenSerializer(resultat)
            return Response(resultat_serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class GraphiquePatientView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, patient_id):
        if not self.check_user_role(request.user,['laborantin','medecin']):
            return Response({'error': 'You do not have permission to see this resource.'}, status=status.HTTP_403_FORBIDDEN)

        examens = ExamenBiologique.objects.filter(dossier_patient_id=patient_id)

        if not examens:
            return Response({"detail": "Aucun examen trouvé pour ce patient"}, status=status.HTTP_404_NOT_FOUND)

        data = {}

        for examen in examens:
            resultats = ResultatExamen.objects.filter(examen_biologique=examen)

            for resultat in resultats:
                if resultat.parametre not in data:
                    data[resultat.parametre] = {
                        "dates": [],
                        "valeurs": [],
                        "unites": []
                    }
                data[resultat.parametre]["dates"].append(examen.date)
                data[resultat.parametre]["valeurs"].append(resultat.valeur)
                data[resultat.parametre]["unites"].append(resultat.unite)

        return Response(data, status=status.HTTP_200_OK)