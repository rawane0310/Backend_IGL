from django.urls import path
from .views import (
    CertificatView,
)

urlpatterns = [
    path('certificats/', CertificatView.as_view(), name='certificats-list'),
    path('certificat/<int:pk>/', CertificatView.as_view(), name='certificat-detail'),
]
