# urls.py (app-level)
from django.urls import path

# An empty urlpatterns list
urlpatterns = []

from django.urls import path
from .views import CreatePatientView , CreateUserView, CreateDossierPatientView, CreateMedicamentView , CreateOrdonnanceView, CreateSoinInfermierView
from .views import DeleteSoinInfermierView , DeleteMedicamentView
urlpatterns = [
    path('patients/', CreatePatientView.as_view()),  # Endpoint pour l'ahout d'un patient
    path('users/', CreateUserView.as_view(), name='create-user'),  # Create user endpoint
    path('dossierpatients/', CreateDossierPatientView.as_view(), name='create-dossierpatient' ),
    path('medicaments/', CreateMedicamentView.as_view(), name='create-medicament'),
    path('ordonances/', CreateOrdonnanceView.as_view(), name='create-ordonance'),
    path('soininfermiers/', CreateSoinInfermierView.as_view(), name='create-soininfermier'),
    path('soin-infirmier/delete/<int:pk>/', DeleteSoinInfermierView.as_view(), name='delete_soin_infirmier'),
     path('medicament/delete/<int:pk>/', DeleteMedicamentView.as_view(), name='delete_medicament'),
]
