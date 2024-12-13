from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models  import ExamenRadiologique , ExamenBiologique , ResultatExamen
from .serializers import ExamenRadiologiqueSerializer , ExamenBiologiqueSerializer , ResultatExamenSerializer


class ResultatExamenView(APIView):

    def get(self, request):
        resultats = ResultatExamen.objects.all()
        serializer = ResultatExamenSerializer(resultats, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ResultatExamenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
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
        try:
            resultat = ResultatExamen.objects.get(pk=pk)
            resultat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ResultatExamen.DoesNotExist:
            return Response({'error': 'Résultat d\'examen non trouvé'}, status=status.HTTP_404_NOT_FOUND)

class ExamenBiologiqueView(APIView):

    def get(self, request):
        examens = ExamenBiologique.objects.all()
        serializer = ExamenBiologiqueSerializer(examens, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExamenBiologiqueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
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
        try:
            examen = ExamenBiologique.objects.get(pk=pk)
            examen.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ExamenBiologique.DoesNotExist:
            return Response({'error': 'Examen Biologique non trouvé'}, status=status.HTTP_404_NOT_FOUND)

class ExamenRadiologiqueView(APIView):

    def get(self, request):
        examens = ExamenRadiologique.objects.all()
        serializer = ExamenRadiologiqueSerializer(examens, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExamenRadiologiqueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
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
        try:
            examen = ExamenRadiologique.objects.get(pk=pk)
            examen.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ExamenRadiologique.DoesNotExist:
            return Response({'error': 'Examen Radiologique non trouvé'}, status=status.HTTP_404_NOT_FOUND)
