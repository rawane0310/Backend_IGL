# urls.py (app-level)

from django.urls import path
from .views import UserView , TechnicianView , PatientView , AdminView ,AdministratifView
from .views import RegisterUserView , LoginView , TokenRefreshView , LogoutAPIView



urlpatterns = [
    path('users/', UserView.as_view()),  # pour la creation (user)
    path('users/<int:pk>/', UserView.as_view()),  # pour put et delete (user)

    path('technicians/', TechnicianView.as_view()),  # For POST (creation)
    path('technicians/<int:pk>/', TechnicianView.as_view()),  # For PUT and DELETE (modification & deletion)
    
    path('administratif/', AdministratifView.as_view()), # For POST (creation)
    path('administratif/<int:pk>/', AdministratifView.as_view()), # For PUT and DELETE (modification & deletion)

    path('admin/', AdminView.as_view()),  # For creating and listing admins
    path('admin/<int:pk>/', AdminView.as_view()),  # For retrieving, updating, and deleting a specific admin
    path('patient/' , PatientView.as_view() ),
    path('patient/<int:patient_id>/', PatientView.as_view()),  # For PUT and DELETE

    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
]
