from django.urls import path
from .views import DossierPatientCreateView , SupprimerDpiAPIView, ModifierDossierAPIView

urlpatterns = [
    path('dossier/create/', DossierPatientCreateView.as_view(), name='create-dossier'),
    path('dossier/<int:dpi_id>/delete/', SupprimerDpiAPIView.as_view(), name='delete-dossier'),
    path('dossier/<int:dpi_id>/modify/', ModifierDossierAPIView.as_view(), name='modify-dossier'),
    
]
