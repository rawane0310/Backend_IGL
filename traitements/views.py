from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Ordonnance , DossierPatient, Technician , Medicament, SoinInfermier
from .serializers import  SoinInfermierSerializer, MedicamentSerializer




class SoinInfermierCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SoinInfermierSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Vérifiez si le dossier patient existe
                dossier_id = serializer.validated_data['dossier'].id
                DossierPatient.objects.get(id=dossier_id)

                # Vérifiez si le technicien (infirmier) existe (si fourni)
                infirmier = serializer.validated_data.get('infirmier')
                if infirmier is not None:
                    Technician.objects.get(id=infirmier.id)

                # Sauvegarde du soin infirmier
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except DossierPatient.DoesNotExist:
                return Response({"error": "Le dossier patient spécifié est introuvable."}, status=status.HTTP_404_NOT_FOUND)

            except Technician.DoesNotExist:
                return Response({"error": "L'infirmier spécifié est introuvable."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class MedicamentCreateView(APIView):
   

    def post(self, request, *args, **kwargs):
        data = request.data
        ordonnance_id = data.get('ordonnance')
        soin_id = data.get('soin')

        # Vérifiez que l'un des deux champs est fourni
        if not ordonnance_id and not soin_id:
            return Response(
                {"error": "Vous devez fournir soit une ordonnance, soit un soin infirmier."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifiez que les deux ne sont pas fournis en même temps
        if ordonnance_id and soin_id:
            return Response(
                {"error": "Un médicament ne peut pas être associé à une ordonnance et à un soin infirmier en même temps."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifiez que l'ordonnance existe si elle est fournie
        if ordonnance_id and not Ordonnance.objects.filter(id=ordonnance_id).exists():
            return Response(
                {"error": f"L'ordonnance avec l'ID {ordonnance_id} est introuvable."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Vérifiez que le soin infirmier existe si il est fourni
        if soin_id and not SoinInfermier.objects.filter(id=soin_id).exists():
            return Response(
                {"error": f"Le soin infirmier avec l'ID {soin_id} est introuvable."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Passez à la sérialisation et sauvegarde
        serializer = MedicamentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SupprimerMedicamentAPIView(APIView):
    def delete(self, request, medicament_id):
        try:
            medicament = Medicament.objects.get(id=medicament_id)
        except Medicament.DoesNotExist:
            return Response(
                {'error': 'Medicament introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        medicament.delete()
        return Response(
            {'message': 'Medicament supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )
    

class SupprimerSoinAPIView(APIView):
    def delete(self, request, soin_id):
        try:
            soin = SoinInfermier.objects.get(id=soin_id)
        except SoinInfermier.DoesNotExist:
            return Response(
                {'error': 'Soin introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        soin.delete()
        return Response(
            {'message': 'Soin supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )    
    

class ModifierSoinInfermierAPIView(APIView):
    

    def put(self, request, soin_id):
        
        return self.update_soin(request, soin_id, partial=False)

    def patch(self, request, soin_id):
        
        return self.update_soin(request, soin_id, partial=True)

    def update_soin(self, request, soin_id, partial):
        
        try:
            soin = SoinInfermier.objects.get(id=soin_id)
        except SoinInfermier.DoesNotExist:
            return Response(
                {'error': 'Soin infirmier introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SoinInfermierSerializer(soin, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


class ModifierMedicamentAPIView(APIView):
    

    def put(self, request, medicament_id):
        
        return self.update_medicament(request, medicament_id, partial=False)

    def patch(self, request, medicament_id):
        
        return self.update_medicament(request, medicament_id, partial=True)

    def update_medicament(self, request, medicament_id, partial):
        
        try:
            medicament = Medicament.objects.get(id=medicament_id)
        except Medicament.DoesNotExist:
            return Response(
                {'error': 'medicament  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MedicamentSerializer(medicament, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        