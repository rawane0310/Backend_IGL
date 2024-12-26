from django.urls import path
from .views import DossierPatientCreateView , SupprimerDpiAPIView, ModifierDossierAPIView, DossierPatientSearchView,PatientSearchByNSSView
from .views import create_dpi


urlpatterns = [
    path('dossier/create/', DossierPatientCreateView.as_view(), name='create-dossier'),
    path('dossier/<int:dpi_id>/delete/', SupprimerDpiAPIView.as_view(), name='delete-dossier'),
    path('dossier/<int:dpi_id>/modify/', ModifierDossierAPIView.as_view(), name='modify-dossier'),
    path('search-by-qr/', DossierPatientSearchView.as_view(), name='dossier-patient-search'),
    path('search_by_nss/', PatientSearchByNSSView.as_view(), name='dossier-patient-search-by-nss'),
    path('search-patient/<int:dossier_id>/', views.search_patient_by_dossier, name='search_patient_by_dossier'),

    #pour test fonctionel
    path('create-dpi/', create_dpi, name='create_dpi'),

    


    
]
