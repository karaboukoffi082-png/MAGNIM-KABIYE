from django.db import models
from django.utils import timezone
from gestion_commandes.models import Commande


class Paiement(models.Model):
    METHODE_CHOICES = [
        ("flooz", "Flooz (Moov Africa)"),
        ("tmoney", "T-Money (Togocom)"),
        ("carte", "Carte Bancaire"),
        ("especes", "Espèces à la livraison"),
    ]
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("initie", "Initié"),
        ("en_cours", "En cours de traitement"),
        ("valide", "Validé"),
        ("echoue", "Échoué"),
        ("expire", "Expiré"),
        ("annule", "Annulé"),
        ("rembourse", "Remboursé"),
    ]

    commande = models.OneToOneField(
        Commande, on_delete=models.CASCADE, related_name="paiement"
    )
    methode = models.CharField(max_length=20, choices=METHODE_CHOICES)
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="en_attente"
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True, null=True, unique=True)
    telephone = models.CharField(max_length=20, blank=True)

    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="Identifiant de transaction chez l'opérateur",
    )
    code_ussd = models.CharField(
        max_length=100, blank=True, help_text="Code USSD à composer"
    )
    tentatives = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    callback_data = models.JSONField(
        null=True, blank=True, help_text="Données brutes reçues du webhook opérateur"
    )
    message_operateur = models.CharField(
        max_length=500,
        blank=True,
        help_text="Message retourné par l'opérateur",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Paiement {self.commande.numero} — "
            f"{self.get_methode_display()} — {self.get_statut_display()}"
        )

    def est_expire(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def secondes_restantes(self):
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return max(0, int(delta.total_seconds()))
        return 0

    def est_valide(self):
        return self.statut == "valide"

    def peut_reessayer(self):
        return self.statut in ("echoue", "expire") and self.tentatives < 3

    @property
    def couleur_statut(self):
        return {
            "en_attente": "secondary",
            "initie": "info",
            "en_cours": "warning",
            "valide": "success",
            "echoue": "danger",
            "expire": "secondary",
            "annule": "secondary",
            "rembourse": "primary",
        }.get(self.statut, "secondary")
