from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "is_admin_boutique", "is_staff", "date_joined"]
    list_filter = ["is_admin_boutique", "is_staff", "is_active"]
    fieldsets = UserAdmin.fieldsets + (
        ("Informations Supplémentaires", {
            "fields": ("telephone", "adresse", "ville", "pays", "photo_profil", "date_naissance", "is_admin_boutique")
        }),
    )
