from django.urls import path
from .views import (
    ExamenRadiologiqueView,
    ExamenBiologiqueView,
    ResultatExamenView,
    SearchExamenBiologiqueView,
    SearchExamenRadiologiqueView,
    SearchResultatBiologiqueByIdView,
    GraphiquePatientView,
    RadiologyImageAPIView
)

urlpatterns = [
    path('examens_radiologiques/', ExamenRadiologiqueView.as_view(), name='examens-radiologiques-list'), #post
    path('examen_radiologique/<int:pk>/', ExamenRadiologiqueView.as_view(), name='examen-radiologique-detail'), #put, delete

    path('examens_biologiques/', ExamenBiologiqueView.as_view(), name='examens-biologiques-list'),#post
    path('examen_biologique/<int:pk>/', ExamenBiologiqueView.as_view(), name='examen-biologique-detail'), #put, delete

    path('resultats_examens/', ResultatExamenView.as_view(), name='resultats-examens-list'), #post
    path('resultat_examen/<int:pk>/', ResultatExamenView.as_view(), name='resultat-examen-detail'), #put, delete

    path('radiology-images/', RadiologyImageAPIView.as_view(), name='radiology_image_list'),  # GET (recherche), POST
    path('radiology-images/<int:pk>/', RadiologyImageAPIView.as_view(), name='radiology_image_detail'),  # PUT, DELETE

    path('search-examens-biologiques/', SearchExamenBiologiqueView.as_view(), name='search_examens_biologiques'), #recherche
    path('search-examens-radiologiques/', SearchExamenRadiologiqueView.as_view(), name='search_examens_radiologiques'), #recherche
    path('search-resultat-biologique/', SearchResultatBiologiqueByIdView.as_view(), name='search_resultat_biologique'), #recherche

    path('graphique-patient/<int:pk>/', GraphiquePatientView.as_view(), name='graphique-patient'), #graphe , id_examen
]