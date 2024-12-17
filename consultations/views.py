from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Consultation , Ordonnance , Technician , DossierPatient
from .serializers import ConsultationSerializer , OrdonnanceSerializer 



class OrdonnanceCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrdonnanceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()  # Sauvegarde l'ordonnance
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ConsultationCreateView(APIView):
    """
    Vue pour créer une consultation avec validations dans la vue.
    """

    def post(self, request, *args, **kwargs):
        data = request.data

        # Vérifier si le médecin existe
        medecin_id = data.get('medecin')
        if medecin_id and not Technician.objects.filter(id=medecin_id).exists():
            return Response(
                {"error": f"Le médecin avec l'ID {medecin_id} n'existe pas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si le dossier existe
        dossier_id = data.get('dossier')
        if not dossier_id or not DossierPatient.objects.filter(id=dossier_id).exists():
            return Response(
                {"error": f"Le dossier patient avec l'ID {dossier_id} n'existe pas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si l'ordonnance existe si elle est fournie
        ordonnance_id = data.get('ordonnance')
        if ordonnance_id and not Ordonnance.objects.filter(id=ordonnance_id).exists():
            return Response(
                {"error": f"L'ordonnance avec l'ID {ordonnance_id} n'existe pas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Sérialisation et sauvegarde
        serializer = ConsultationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    



class SupprimerConsultationAPIView(APIView):
    def delete(self, request, consultation_id):
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': 'Consultation introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        consultation.delete()
        return Response(
            {'message': 'Consultation supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )

class SupprimerOrdonnanceAPIView(APIView):
    def delete(self, request, ordonnance_id):
        try:
            ordonnance = Ordonnance.objects.get(id=ordonnance_id)
        except Ordonnance.DoesNotExist:
            return Response(
                {'error': 'ordonnance introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        ordonnance.delete()
        return Response(
            {'message': 'ordonnance supprimée avec succès.'},
            status=status.HTTP_204_NO_CONTENT
        )
    


class ModifierOrdonnanceAPIV(APIView):
    

    def put(self, request, ordonnance_id):
        
        return self.update_ordonnance(request, ordonnance_id, partial=False)

    def patch(self, request, ordonnance_id):
        
        return self.update_ordonnance(request, ordonnance_id, partial=True)

    def update_ordonnance(self, request, ordonnance_id, partial):
        
        try:
            ordonnance = Ordonnance.objects.get(id=ordonnance_id)
        except Ordonnance.DoesNotExist:
            return Response(
                {'error': 'ordonnance  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrdonnanceSerializer(ordonnance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
    

class ModifierConsultationAPIV(APIView):
    

    def put(self, request, consultation_id):
        
        return self.update_consultation(request, consultation_id, partial=False)

    def patch(self, request, consultation_id):
        
        return self.update_consultation(request, consultation_id, partial=True)

    def update_consultation(self, request, consultation_id, partial):
        
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': 'consultation  introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConsultationSerializer(consultation, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        




class ConsultationSearchByDateView(APIView) : 
    def get( self , request , *args ,**kwargs ) : 
        date  = request.GET.get ('date' , None)

        if not date :  
            return Response({"details " : "date is required"} , status=status.HTTP_400_BAD_REQUEST)
        
        try : 
            consultation = Consultation.objects.filter(date=date)
            if not consultation : 
                return Response ({"details" : "noconsultation found with this date "}, status=status.HTTP_404_NOT_FOUND)
            
            cons_ser=ConsultationSerializer(consultation , many = True )

            return Response (cons_ser.data)
        except Exception as e : 
            return Response ({"details" : str(e) }, status=status.HTTP_400_BAD_REQUEST)
        

            

class ConsultationSearchByDpiView (APIView ) : 
    def get (self , request , *args , **kwargs ) : 
        dpi = request.GET.get('dpi' , None) 

        if not dpi : 
            return Response ({"details" : " dpi required "} , status=status.HTTP_400_BAD_REQUEST)
        
        try : 
            consultation = Consultation.objects.filter (dossier = dpi )
            if not consultation : 
                return Response ({"details" : "no consultation with this dpi "} , status=status.HTTP_404_NOT_FOUND)

            consult_ser = ConsultationSerializer(consultation , many = True) 
            return Response (consult_ser.data) 
        
        except Exception as e :
            return Response ({"details" : str(e)} , status=status.HTTP_400_BAD_REQUEST ) 



class ConsultationSearchByTechnicienView (APIView) : 
    def get (self , request , *args , **kwargs ) : 
        tech = request.GET.get('tech' , None) 

        if not tech : 
            return Response ({"details" : " technicien required "} , status=status.HTTP_400_BAD_REQUEST)
        
        try : 
            consultation = Consultation.objects.filter (medecin = tech)
            if not consultation : 
                return Response ({"details" : "no consultation with this technicien "} , status=status.HTTP_404_NOT_FOUND)

            consult_ser = ConsultationSerializer(consultation , many = True) 
            return Response (consult_ser.data) 
        
        except Exception as e :
            return Response ({"details" : str(e)} , status=status.HTTP_400_BAD_REQUEST ) 
