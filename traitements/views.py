from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Ordonnance , DossierPatient, Technician , Medicament, SoinInfermier
from .serializers import  SoinInfermierSerializer, MedicamentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from accounts.mixin import CheckUserRoleMixin



class SoinInfermierCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user,['infermier']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
    

###########################################################################################################################################
 

class MedicamentCreateView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not self.check_user_role(request.user,['infermier','medecin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
    
###########################################################################################################################################
 

class SupprimerMedicamentAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def delete(self, request, medicament_id):
        if not self.check_user_role(request.user,['infermier','medecin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
    
###########################################################################################################################################
 

class SupprimerSoinAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def delete(self, request, soin_id):
        if not self.check_user_role(request.user,['infermier']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
    
###########################################################################################################################################
 

class ModifierSoinInfermierAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def put(self, request, soin_id):
        if not self.check_user_role(request.user,['infermier']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        return self.update_soin(request, soin_id, partial=False)

    def patch(self, request, soin_id):
        if not self.check_user_role(request.user,['infermier']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        return self.update_soin(request, soin_id, partial=True)

    def update_soin(self, request, soin_id, partial):
        if not self.check_user_role(request.user,['infermier']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

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


###########################################################################################################################################
 

class ModifierMedicamentAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def put(self, request, medicament_id):
        if not self.check_user_role(request.user,['infermier','medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        return self.update_medicament(request, medicament_id, partial=False)

    def patch(self, request, medicament_id):
        if not self.check_user_role(request.user,['infermier','medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        return self.update_medicament(request, medicament_id, partial=True)

    def update_medicament(self, request, medicament_id, partial):
        if not self.check_user_role(request.user,['infermier','medecin']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

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
    
###########################################################################################################################################
 


class RechercheMedicamentAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not self.check_user_role(request.user, ['patient'],['infermier','medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Récupérer les paramètres de recherche depuis la requête GET
        id_ = request.GET.get('id')
        nom = request.GET.get('nom')
        dose = request.GET.get('dose')
        frequence = request.GET.get('frequence')
        duree = request.GET.get('duree')
        ordonnance_id = request.GET.get('ordonnance')  # ID de l'ordonnance
        soin_id = request.GET.get('soin')  # ID du soin infirmier
        
        # Initialiser une requête pour récupérer tous les médicaments
        medicaments = Medicament.objects.all()
        
        # Appliquer les filtres selon les paramètres fournis
        if id_:
            medicaments = medicaments.filter(id=id_)
        if nom:
            medicaments = medicaments.filter(nom__icontains=nom)  # Recherche partielle
        if dose:
            medicaments = medicaments.filter(dose__icontains=dose)
        if frequence:
            medicaments = medicaments.filter(frequence__icontains=frequence)
        if duree:
            medicaments = medicaments.filter(duree__icontains=duree)
        if ordonnance_id:
            medicaments = medicaments.filter(ordonnance_id=ordonnance_id)
        if soin_id:
            medicaments = medicaments.filter(soin_id=soin_id)
        
        # Préparer les résultats au format JSON
        resultats = list(medicaments.values())
        return Response(resultats)

###########################################################################################################################################
 
 
class RechercheSoinInfermierAPIView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not self.check_user_role(request.user, ['patient'],['infermier','medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        # Récupération des paramètres de recherche
        id_ = request.GET.get('id')  # ID du soin
        date = request.GET.get('date')  # Format attendu : yyyy-mm-dd
        infirmier_id = request.GET.get('infirmier')  # ID de l'infirmier
        heure=request.GET.get('heure') #l'heure du soins
        observation = request.GET.get('observation')  # Texte dans observation
        soin_realise = request.GET.get('soin_realise')  # Texte dans soin réalisé
        dossier_id = request.GET.get('dossier')  # ID du dossier patient
        
        # Initialiser une requête pour récupérer tous les soins
        soins = SoinInfermier.objects.all()
        
        # Appliquer les filtres si les paramètres sont fournis
        if id_:
            soins = soins.filter(id=id_)
        if date:
            soins = soins.filter(date=date)
        if infirmier_id:
            soins = soins.filter(infirmier_id=infirmier_id)
        if heure:
            heure = soins.filter(heure=heure)    
        if observation:
            soins = soins.filter(observation__icontains=observation)  # Recherche partielle
        if soin_realise:
            soins = soins.filter(soin_realise__icontains=soin_realise)  # Recherche partielle
        if dossier_id:
            soins = soins.filter(dossier_id=dossier_id)
        
        # Préparer la réponse au format JSON
        resultats = list(soins.values())
        return Response(resultats)
