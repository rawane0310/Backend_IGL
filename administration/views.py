from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Certificat
from .serializers import CertificatSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from accounts.mixin import CheckUserRoleMixin

class CertificatView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not self.check_user_role(request.user, ['technicien','patient'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        certificats = Certificat.objects.all()
        serializer = CertificatSerializer(certificats, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CertificatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            certificat = Certificat.objects.get(pk=pk)
        except Certificat.DoesNotExist:
            return Response({'error': 'Certificat non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CertificatSerializer(certificat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not self.check_user_role(request.user, ['technicien'],['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            certificat = Certificat.objects.get(pk=pk)
            certificat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Certificat.DoesNotExist:
            return Response({'error': 'Certificat non trouvé'}, status=status.HTTP_404_NOT_FOUND)

