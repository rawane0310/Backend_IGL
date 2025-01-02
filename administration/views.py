from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Certificat
from .serializers import CertificatSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from accounts.mixin import CheckUserRoleMixin

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CertificatView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Retrieve all certificates",
        operation_description="This endpoint allows users with the role of  'medecin' to retrieve all certificates.",
        responses={
            200: openapi.Response(
                description="Certificates retrieved successfully.",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "date": "2024-12-31",
                            "medecin": 1,
                            "contenu": "Medical certificate content.",
                            "patient": 12
                        }
                    ]
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to get this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to get this resource."
                    }
                }
            )
        }
    )

    def get(self, request):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to get this resource.'}, status=status.HTTP_403_FORBIDDEN)

        certificats = Certificat.objects.all()
        serializer = CertificatSerializer(certificats, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new certificate",
        operation_description="This endpoint allows users with the role of 'medecin' to create a new certificate by providing necessary details.",
        request_body=CertificatSerializer,
        responses={
            201: openapi.Response(
                description="Certificate created successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "date": "2024-12-31",
                        "medecin": 1,
                        "contenu": "Medical certificate content.",
                        "patient": 12
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "date": ["This field is required."],
                        "contenu": ["This field is required."]
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to create this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to create this resource."
                    }
                }
            )
        }
    )

    def post(self, request):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CertificatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Update an existing certificate",
        operation_description="This endpoint allows users with the role of 'medecin' to update an existing certificate by providing its ID and new details.",
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="Primary key of the certificate to update", type=openapi.TYPE_INTEGER,required=True)
        ],
        request_body=CertificatSerializer,
        responses={
            200: openapi.Response(
                description="Certificate updated successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "date": "2024-12-31",
                        "medecin": 1,
                        "contenu": "Updated medical certificate content.",
                        "patient": 12
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid data provided.",
                examples={
                    "application/json": {
                        "contenu": ["This field is required."]
                    }
                }
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to update this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to modify this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Certificate not found.",
                examples={
                    "application/json": {
                        "error": "Certificate not found."
                    }
                }
            )
        }
    )

    def put(self, request, pk):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            certificat = Certificat.objects.get(pk=pk)
        except Certificat.DoesNotExist:
            return Response({'error': 'Certificat non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CertificatSerializer(certificat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete an existing certificate",
        operation_description="This endpoint allows users with the role of 'medecin' to delete an existing certificate by providing its ID.",
        manual_parameters=[
            openapi.Parameter('pk', openapi.IN_PATH, description="Primary key of the certificate to delete", type=openapi.TYPE_INTEGER,required=True)
        ],
        responses={
            204: openapi.Response(
                description="No content, certificate successfully deleted."
            ),
            403: openapi.Response(
                description="Access denied. You do not have permission to delete this resource.",
                examples={
                    "application/json": {
                        "error": "You do not have permission to delete this resource."
                    }
                }
            ),
            404: openapi.Response(
                description="Certificate not found.",
                examples={
                    "application/json": {
                        "error": "Certificate not found."
                    }
                }
            )
        }
    )

    def delete(self, request, pk):
        if not self.check_user_role(request.user,technician_roles=['medecin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            certificat = Certificat.objects.get(pk=pk)
            certificat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Certificat.DoesNotExist:
            return Response({'error': 'Certificat non trouvé'}, status=status.HTTP_404_NOT_FOUND)

