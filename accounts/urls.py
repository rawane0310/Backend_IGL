from .views import TechnicianSearchByRoleView , TechnicianSearchByIDView
# urls.py (app-level)

from django.urls import path
from .views import UserView , TechnicianView , PatientView , AdminView ,AdministratifView
from .views import RegisterUserView , LoginView , TokenRefreshView , LogoutAPIView, login_view, create_patient_account , create_patient_profile
from . import views
 

urlpatterns = [
   #path('users/', UserView.as_view()),  # pour la creation (user)
    path('users/<int:pk>/', UserView.as_view()),  # pour put et delete (user)

    path('technicians/', TechnicianView.as_view()),  # For POST (creation)
    path('technicians/<int:pk>/', TechnicianView.as_view()),  # For PUT and DELETE (modification & deletion)
    
    path('administratif/', AdministratifView.as_view()), # For POST (creation)
    path('administratif/<int:pk>/', AdministratifView.as_view()), # For PUT and DELETE (modification & deletion)

    path('admin/', AdminView.as_view()),  # For creating and listing admins
    path('admin/<int:pk>/', AdminView.as_view()),  # For retrieving, updating, and deleting a specific admin
    path('patient/' , PatientView.as_view() ),
    path('patient/<int:patient_id>/', PatientView.as_view()),  # For PUT and DELETE


    #technicien search 
    path('technician-by-role/', TechnicianSearchByRoleView.as_view() ) ,
    path('technician-by-id/', TechnicianSearchByIDView.as_view() ) ,

    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'), # first documenttion 
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),


    #pour test fonctionel
    path('loginTest/', login_view, name='loginTest'),
    path('create-account/', create_patient_account, name='create_patient_account'),
    path('create-profile/', create_patient_profile, name='create_patient_profile'),
    path('patientT/<int:patient_id>/', views.patient_profile, name='patient_profile'),

]