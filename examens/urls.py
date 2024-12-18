from django.urls import path
from .views import (
    ExamenRadiologiqueView,
    ExamenBiologiqueView,
    ResultatExamenView,
    SearchExamenBiologiqueView,
    SearchExamenRadiologiqueView,
    SearchResultatBiologiqueByIdView
)

urlpatterns = [
    path('examens_radiologiques/', ExamenRadiologiqueView.as_view(), name='examens-radiologiques-list'),
    path('examen_radiologique/<int:pk>/', ExamenRadiologiqueView.as_view(), name='examen-radiologique-detail'),
    path('examens_biologiques/', ExamenBiologiqueView.as_view(), name='examens-biologiques-list'),
    path('examen_biologique/<int:pk>/', ExamenBiologiqueView.as_view(), name='examen-biologique-detail'),
    path('resultats_examens/', ResultatExamenView.as_view(), name='resultats-examens-list'),
    path('resultat_examen/<int:pk>/', ResultatExamenView.as_view(), name='resultat-examen-detail'),
    path('search-examens-biologiques/', SearchExamenBiologiqueView.as_view(), name='search_examens_biologiques'),
    path('search-examens-radiologiques/', SearchExamenRadiologiqueView.as_view(), name='search_examens_radiologiques'),
    path('search-resultat-biologique/', SearchResultatBiologiqueByIdView.as_view(), name='search_resultat_biologique'),
]
