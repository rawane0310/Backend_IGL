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

class SearchExamenBiologiqueView(APIView):
    def get(self, request, *args, **kwargs):
        technicien = request.GET.get('technicien', None)
        date = request.GET.get('date', None)
        dossier = request.GET.get('dossier', None)
        terminaison = request.GET.get('terminaison', None)

        try:
            examens_bio = ExamenBiologique.objects.all()
            if technicien:
                examens_bio = examens_bio.filter(technicien__nom__icontains=technicien)
            if date:
                examens_bio = examens_bio.filter(date=date)
            if dossier:
                examens_bio = examens_bio.filter(dossier__icontains=dossier)
            if terminaison:
                examens_bio = examens_bio.filter(terminaison__icontains=terminaison)

            examens_bio_serializer = ExamenBiologiqueSerializer(examens_bio, many=True)
            return Response(examens_bio_serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SearchExamenRadiologiqueView(APIView):
    def get(self, request, *args, **kwargs):
        technicien = request.GET.get('technicien', None)
        date = request.GET.get('date', None)
        dossier = request.GET.get('dossier', None)
        terminaison = request.GET.get('terminaison', None)

        try:
            examens_radio = ExamenRadiologique.objects.all()
            if technicien:
                examens_radio = examens_radio.filter(technicien__nom__icontains=technicien)
            if date:
                examens_radio = examens_radio.filter(date=date)
            if dossier:
                examens_radio = examens_radio.filter(dossier__icontains=dossier)
            if terminaison:
                examens_radio = examens_radio.filter(terminaison__icontains=terminaison)

            examens_radio_serializer = ExamenRadiologiqueSerializer(examens_radio, many=True)
            return Response(examens_radio_serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SearchResultatBiologiqueByIdView(APIView):
    def get(self, request, *args, **kwargs):
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
