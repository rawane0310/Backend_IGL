# urls.py
from django.urls import path
from .views import ConsultationCreateView , OrdonnanceCreateView , SupprimerOrdonnanceAPIView , SupprimerConsultationAPIView , ModifierOrdonnanceAPIV , ModifierConsultationAPIV
from .views import ConsultationSearchByDateView , ConsultationSearchByDpiView , ConsultationSearchByTechnicienView

from .views import RechercheOrdonnanceAPIV , ValidationOrdonnance , RechercheResume,ModifierResumeAPIV,SupprimerResumeAPIView,ResumeCreateView


urlpatterns = [
    path('ordonnance/create/', OrdonnanceCreateView.as_view(), name='create-ordonnance'),
    path('consultation/create/', ConsultationCreateView.as_view(), name='create-consultation'),
    path('ordonnance/<int:ordonnance_id>/delete/', SupprimerOrdonnanceAPIView.as_view(), name='delete-ordonnance'),
    path('consultation/<int:consultation_id>/delete/', SupprimerConsultationAPIView.as_view(), name='delete-consultation'),
    path('ordonnance/<int:ordonnance_id>/modify/', ModifierOrdonnanceAPIV.as_view(), name='modify-ordonnance'),
    path('consultation/<int:consultation_id>/modify/', ModifierConsultationAPIV.as_view(), name='modify-consultation'),

    path('consultation_by_date/', ConsultationSearchByDateView.as_view() ) , 
    path('consultation_by_dpi/', ConsultationSearchByDpiView.as_view() ) , 
    path('consultation_by_tech/', ConsultationSearchByTechnicienView.as_view() ) , 



    path('ordonnance/search/',RechercheOrdonnanceAPIV.as_view(), name='search-ordonnance'),
    path('ordonnance/validation/<int:pk>/', ValidationOrdonnance.as_view(), name='validation-ordonnance'),
    path('resume/create/', ResumeCreateView.as_view(), name='create-resume'),
    path('resume/<int:resume_id>/delete/', SupprimerResumeAPIView.as_view(), name='delete-resume'),
    path('resume/<int:resume_id>/modify/', ModifierResumeAPIV.as_view(), name='modify-resume'),
    path('resume/search/',RechercheResume.as_view(), name='search-resume'),
    
]
