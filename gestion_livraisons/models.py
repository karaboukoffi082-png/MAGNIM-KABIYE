from django.db import models
from gestion_commandes.models import Commande


class Livraison(models.Model):
    TYPE_CHOICES = [
        ("domicile", "Livraison à domicile"),
        ("nationale", "Livraison nationale"),
        ("internationale", "Livraison internationale"),
    ]
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("prepare", "En préparation"),
        ("expedie", "Expédié"),
        ("en_transit", "En transit"),
        ("en_livraison", "En cours de livraison"),
        ("livree", "Livrée"),
        ("echec", "Échec de livraison"),
    ]

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name="livraison")
    type_livraison = models.CharField(max_length=20, choices=TYPE_CHOICES, default="domicile")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
    numero_suivi = models.CharField(max_length=100, blank=True)
    transporteur = models.CharField(max_length=100, blank=True, default="KabiyèBooks Express")
    date_expedition = models.DateTimeField(null=True, blank=True)
    date_livraison_prevue = models.DateField(null=True, blank=True)
    date_livraison_reelle = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Livraison"

    def __str__(self):
        return f"Livraison {self.commande.numero}"

    def get_statut_display_label(self):
        return dict(self.STATUT_CHOICES).get(self.statut, self.statut)

    def progression(self):
        ordre = ["en_attente", "prepare", "expedie", "en_transit", "en_livraison", "livree"]
        try:
            idx = ordre.index(self.statut)
            return int((idx / (len(ordre) - 1)) * 100)
        except ValueError:
            return 0


class LivraisonEvenement(models.Model):
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE, related_name="evenements")
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=Livraison.STATUT_CHOICES)
    lieu = models.CharField(max_length=200, blank=True, default="Lomé, Togo")
    description = models.TextField()
    icone = models.CharField(max_length=50, default="bi-circle-fill")

    class Meta:
        verbose_name = "Événement de livraison"
        verbose_name_plural = "Événements de livraison"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.livraison} — {self.get_statut_display()} ({self.date:%d/%m/%Y})"
