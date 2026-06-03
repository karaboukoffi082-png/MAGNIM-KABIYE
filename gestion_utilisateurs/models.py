from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, default="Togo")
    photo_profil = models.ImageField(upload_to="profils/", blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    is_admin_boutique = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.get_full_name() or self.username}"
