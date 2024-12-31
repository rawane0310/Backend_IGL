from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models  import ExamenRadiologique , ExamenBiologique , ResultatExamen, Technician, RadiologyImage
from .serializers import ExamenRadiologiqueSerializer , ExamenBiologiqueSerializer , ResultatExamenSerializer, RadiologyImageSerializer
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from accounts.mixin import CheckUserRoleMixin
from django.shortcuts import get_object_or_404


class ResultatExamenView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not self.check_user_role(request.user, ['patient'],['laborantin','medecin']):
            return Response({'error': 'You do not have permission to get this resource.'}, status=status.HTTP_403_FORBIDDEN)

        resultats = ResultatExamen.objects.all()
        serializer = ResultatExamenSerializer(resultats, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not self.check_user_role(request.user,technician_roles=['laborantin']):
            return Response({'error': 'You do not have permission to create this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ResultatExamenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not self.check_user_role(request.user,technician_roles=['laborantin','medecin']):
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
        if not self.check_user_role(request.user,technician_roles=['laborantin']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            resultat = ResultatExamen.objects.get(pk=pk)
            resultat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ResultatExamen.DoesNotExist:
            return Response({'error': 'Résultat d\'examen non trouvé'}, status=status.HTTP_404_NOT_FOUND)



###########################################################################################################################################
 

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
        

###########################################################################################################################################


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
        
###########################################################################################################################################



class RadiologyImageAPIView(APIView,CheckUserRoleMixin):
    """
    API pour gérer les opérations CRUD et la recherche sur RadiologyImage.
    """
    permission_classes=[IsAuthenticated]

    def post(self, request):
        
        """
        Créer une nouvelle image radiologique.
        """
        if not self.check_user_role(request.user,technician_roles=['radiologue']):
            return Response({'error': 'You do not have permission to creta this resource.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RadiologyImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        
        """
        Modifier une image radiologique existante.
        """
        if not self.check_user_role(request.user,technician_roles=['radiologue']):
            return Response({'error': 'You do not have permission to modify this resource.'}, status=status.HTTP_403_FORBIDDEN)

        image = get_object_or_404(RadiologyImage, pk=pk)
        serializer = RadiologyImageSerializer(image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        
        """
        Supprimer une image radiologique.
        """
        if not self.check_user_role(request.user,technician_roles=['radiologue']):
            return Response({'error': 'You do not have permission to delete this resource.'}, status=status.HTTP_403_FORBIDDEN)


        image = get_object_or_404(RadiologyImage, pk=pk)
        image.delete()
        return Response({'message': 'Image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    def get(self, request):
        """
        Rechercher des images radiologiques par ID, image ou date.
        """
        if not self.check_user_role(request.user,['patient'],['radiologue','medecin']):
            return Response({'error': 'You do not have permission to get this resource.'}, status=status.HTTP_403_FORBIDDEN)

        image_id = request.GET.get('id')
        image_path = request.GET.get('image')
        date_uploaded = request.GET.get('date')
        image_examen = request.GET.get('examen')
        titre = request.GET.get('titre')

        # Filtrage
        images = RadiologyImage.objects.all()
        if image_id:
            images = images.filter(id=image_id)
        if image_path:
            images = images.filter(image__icontains=image_path)
        if date_uploaded:
            images = images.filter(uploaded_at__date=date_uploaded)
        if image_examen:
            images = images.filter(examen_radiologique=image_examen)
        if titre : 
            images = images.filter(titre=titre)    

        serializer = RadiologyImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



###########################################################################################################################################
class SearchExamenBiologiqueView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['patient'],['laborantin','medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        id = request.GET.get('id',None)
        technicien = request.GET.get('technicien', None)
        date = request.GET.get('date', None)
        dossier = request.GET.get('dossier', None)
        description = request.GET.get('description', None)
        laborantin = request.GET.get('laborantin',None)

        try:
            examens_bio = ExamenBiologique.objects.all()

            if id:
                examens_bio = examens_bio.filter(id=id)
            if technicien:
                examens_bio = examens_bio.filter(technicien__nom__icontains=technicien)
            if date:
                examens_bio = examens_bio.filter(date=date)
            if dossier:
                examens_bio = examens_bio.filter(dossier_patient__id=dossier)
            if description:
                examens_bio = examens_bio.filter(description__icontains=description)
            if laborantin:
                examens_bio = examens_bio.filter(laborantin__nom__icontains=laborantin)


            # Construction de la réponse avec les objets et les informations du technicien
            result = []
            for examen in examens_bio:
                result.append({
                    'id': examen.id,
                    'date': examen.date,
                    'description': examen.description,
                    'dossier_patient': examen.dossier_patient.id,
                    'technicien':examen.technicien.id,
                    'nom_medecin': examen.technicien.nom,
                    'prenom_medecin': examen.technicien.prenom,
                    'laborantin': examen.laborantin.id if examen.laborantin else None,
                    'nom_lab': examen.laborantin.nom if examen.laborantin else None,
                    'prenom_lab': examen.laborantin.prenom if examen.laborantin else None
                   
                })

            return Response(result, status=status.HTTP_200_OK)
        
        except ExamenBiologique.DoesNotExist:
            return Response(
                {"error": "No biological exams found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        

###########################################################################################################################################
 

class SearchExamenRadiologiqueView(APIView,CheckUserRoleMixin):
    #permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        #if not self.check_user_role(request.user, ['patient'],['radiologue','medecin']):
         #   return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        id = request.GET.get('id',None)
        technicien = request.GET.get('technicien', None)
        date = request.GET.get('date', None)
        radiologue = request.GET.get('radiologue',None)
        compte_rendu = request.GET.get('compte_rendu',None)
        dossier = request.GET.get('dossier', None)
        description = request.GET.get('description', None)

        try:
            examens_radio = ExamenRadiologique.objects.all()
            if id:
                examens_radio = examens_radio.filter(id=id)
            if technicien:
                examens_radio = examens_radio.filter(technicien__nom__icontains=technicien)
            if date:
                examens_radio = examens_radio.filter(date=date)
            if radiologue:
                examens_radio = examens_radio.filter(radiologue__nom__icontains=radiologue)
            if compte_rendu:
                examens_radio = examens_radio.filter(compte_rendu__icontains=compte_rendu)       
            if dossier:
                examens_radio = examens_radio.filter(dossier__icontains=dossier)
            if description:
                examens_radio = examens_radio.filter(description__icontains=description)

            # Construction de la réponse avec les objets et les informations du technicien
            result = []
            for examen in examens_radio:
                result.append({
                    'id': examen.id,
                    'date': examen.date,
                    'description': examen.description,
                    'dossier_patient': examen.dossier_patient.id,
                    'compte_rendu' : examen.compte_rendu,
                    'technicien':examen.technicien.id,
                    'nom_medecin': examen.technicien.nom,
                    'prenom_medecin': examen.technicien.prenom,
                    'radiologue': examen.radiologue.id if examen.radiologue else None,
                    'nom_radiologue': examen.radiologue.nom if examen.radiologue else None,
                    'prenom_radiologue': examen.radiologue.prenom if examen.radiologue else None
                   
                })

            return Response(result, status=status.HTTP_200_OK)
        
        except ExamenRadiologique.DoesNotExist:
            return Response(
                {"error": "No radiological exams found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        

###########################################################################################################################################



class SearchResultatBiologiqueByIdView(APIView,CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not self.check_user_role(request.user, ['patient'],['laborantin','medecin']):
            return Response({'error': 'You do not have permission to search for this resource.'}, status=status.HTTP_403_FORBIDDEN)

        id_examen_bio = request.GET.get('idExamenBio', None)
        parametre = request.GET.get('parametre',None)

        if not id_examen_bio:
            return Response({"detail": "idExamenBio is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resultat = ResultatExamen.objects.filter(examen_biologique__id=id_examen_bio)

            if not resultat:
                return Response({"detail": "No result found for the given idExamenBio."}, status=status.HTTP_404_NOT_FOUND)

            if parametre:
                resultat = resultat.filter(parametre=parametre)

            resultat_serializer = ResultatExamenSerializer(resultat, many=True)
            return Response(resultat_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


###########################################################################################################################################


class GraphiquePatientView(APIView, CheckUserRoleMixin):
    permission_classes = [IsAuthenticated]

    def generate_data_array(self,result, labels):
        data = []
        for label in labels:
            parametre, unite = label.split(' (')
            unite = unite[:-1]  # Remove the closing parenthesis

            # Find matching result in combined_results
            if result.parametre == parametre and result.unite == unite:
                data.append(float(result.valeur))
            else:
                data.append(0)
        
        return data


    def get(self, request, pk):
        if not self.check_user_role(request.user, technician_roles=['laborantin', 'medecin']):
            return Response({'error': 'You do not have permission to see this resource.'}, status=status.HTTP_403_FORBIDDEN)

        examen_actuel = ExamenBiologique.objects.filter(id=pk).first()

        if not examen_actuel:
            return Response({"detail": "Examen non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        examen_precedent = ExamenBiologique.objects.filter(
            dossier_patient_id=examen_actuel.dossier_patient_id,
            date__lt=examen_actuel.date
        ).order_by('-date').first()

        resultats_actuel = ResultatExamen.objects.filter(examen_biologique=examen_actuel)
        resultats_precedent = []

        if examen_precedent:
            resultats_precedent = ResultatExamen.objects.filter(examen_biologique=examen_precedent)

        # Combine both arrays
        combined_results = list(resultats_actuel) + list(resultats_precedent)

        # Create labels and ensure no duplicates
        labels = list(set([f"{result.parametre} ({result.unite})" for result in combined_results]))

        data1 =[self.generate_data_array(result, labels) for result in resultats_actuel]
        data2 = [self.generate_data_array(result, labels) for result in resultats_precedent]
        
        data = {
            "labels:": labels,
            "datasets": [
                {
                    "data": [sum(elements) for elements in zip(*data1)],
                
                },
                {
                    "data": [sum(elements) for elements in zip(*data2)],
                }
            ]
        }

        # for resultat in resultats_actuel:
        #     data["examen_actuel"][resultat.parametre] = {
        #         "valeur": resultat.valeur,
        #         "unite": resultat.unite
        #     }

        # for resultat in resultats_precedent:
        #     data["examen_precedent"][resultat.parametre] = {
        #         "valeur": resultat.valeur,
        #         "unite": resultat.unite
        #     }

        return Response(data, status=status.HTTP_200_OK)