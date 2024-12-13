from django.urls import path
from .views import (
    ExamenRadiologiqueView,
    ExamenBiologiqueView,
    ResultatExamenView,
)

urlpatterns = [
    path('examens_radiologiques/', ExamenRadiologiqueView.as_view(), name='examens-radiologiques-list'),
    path('examen_radiologique/<int:pk>/', ExamenRadiologiqueView.as_view(), name='examen-radiologique-detail'),
    path('examens_biologiques/', ExamenBiologiqueView.as_view(), name='examens-biologiques-list'),
    path('examen_biologique/<int:pk>/', ExamenBiologiqueView.as_view(), name='examen-biologique-detail'),
    path('resultats_examens/', ResultatExamenView.as_view(), name='resultats-examens-list'),
    path('resultat_examen/<int:pk>/', ResultatExamenView.as_view(), name='resultat-examen-detail'),
]
