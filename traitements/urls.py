from django.urls import path
from .views import  SoinInfermierCreateView , MedicamentCreateView , SupprimerMedicamentAPIView , SupprimerSoinAPIView
from .views import ModifierSoinInfermierAPIView , ModifierMedicamentAPIView , RechercheMedicamentAPIView , RechercheSoinInfermierAPIView
urlpatterns = [
    
    path('soin-infermier/create/', SoinInfermierCreateView.as_view(), name='create-soin-infermier'),
    path('medicament/create/', MedicamentCreateView.as_view(), name='create-medicament'),
    path('medicament/<int:medicament_id>/delete/', SupprimerMedicamentAPIView.as_view(), name='delete-medicament'),
    path('soin-infermier/<int:soin_id>/delete/', SupprimerSoinAPIView.as_view(), name='delete-soin-infermier'),
    path('soin-infirmier/<int:soin_id>/modify/', ModifierSoinInfermierAPIView.as_view(), name='modify_soin_infirmier'),
    path('medicament/<int:medicament_id>/modify/', ModifierMedicamentAPIView.as_view(), name='modify-medicament'),
    path('medicament/search/',RechercheMedicamentAPIView.as_view() , name='search-medicament'),
    path('soin-infirmier/search/', RechercheSoinInfermierAPIView.as_view(), name='search-soin-infermier'),
]
