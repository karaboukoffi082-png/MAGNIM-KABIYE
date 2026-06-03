from django.db import models
from gestion_utilisateurs.models import Utilisateur


class Notification(models.Model):
    TYPE_CHOICES = [
        ("commande", "Commande"),
        ("paiement", "Paiement"),
        ("livraison", "Livraison"),
        ("info", "Information"),
        ("promo", "Promotion"),
    ]

    utilisateur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="info")
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lue = models.BooleanField(default=False)
    lien = models.CharField(max_length=500, blank=True, help_text="URL de redirection optionnelle")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.utilisateur} — {self.titre}"


class SmsLog(models.Model):
    STATUT_CHOICES = [
        ("envoye", "Envoyé"),
        ("echec", "Échec"),
        ("simule", "Simulé (dev)"),
    ]

    telephone = models.CharField(max_length=20)
    message = models.TextField()
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default="simule")
    reponse = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "SMS envoyé"
        verbose_name_plural = "SMS envoyés"
        ordering = ["-created_at"]

    def __str__(self):
        return f"SMS → {self.telephone} [{self.statut}]"
