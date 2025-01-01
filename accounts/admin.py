from django.contrib import admin
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.admin import UserAdmin
from .models import User, Admin, CustomUserManager

from django.contrib.auth.models import BaseUserManager
# Register your models here.
from .models import RadiologyImage, ExamenRadiologique  # Modèles que tu veux enregistrer


class CustomUserAdmin(UserAdmin):
    # Spécifier les champs à afficher dans l'admin
    model = User
    list_display = ('email', 'role', 'is_staff', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_staff', 'is_active', 'role')
    search_fields = ('email',)
    ordering = ('-created_at',)

    # Définir les champs qui peuvent être modifiés lors de la création et de la modification
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'role', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )

    # Définir les champs qui doivent être affichés lors de la création d'un utilisateur
    add_form = CustomUserManager.create_user

# Enregistrer le modèle User avec l'admin personnalisé
admin.site.register(User, CustomUserAdmin)

# Enregistrer également le modèle Admin si vous le souhaitez dans l'admin
@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'user')
    search_fields = ('nom', 'prenom', 'user__email')

# Enregistrer tes modèles dans l'admin
admin.site.register(RadiologyImage)