from django.db import models
from gestion_utilisateurs.models import Utilisateur
from gestion_livres.models import Livre


class Commande(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("confirmee", "Confirmée"),
        ("payee", "Payée"),
        ("en_preparation", "En préparation"),
        ("expediee", "Expédiée"),
        ("livree", "Livrée"),
        ("annulee", "Annulée"),
    ]

    client = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="commandes")
    numero = models.CharField(max_length=20, unique=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
    adresse_livraison = models.TextField()
    ville_livraison = models.CharField(max_length=100)
    pays_livraison = models.CharField(max_length=100, default="Togo")
    frais_livraison = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.numero:
            import uuid
            self.numero = f"KB-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.numero} - {self.client}"

    def total_articles(self):
        return sum(ligne.sous_total() for ligne in self.lignes.all())

    def total(self):
        return self.total_articles() + self.frais_livraison

    def statut_label(self):
        return dict(self.STATUT_CHOICES).get(self.statut, self.statut)


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes")
    livre = models.ForeignKey(Livre, on_delete=models.SET_NULL, null=True)
    titre_livre = models.CharField(max_length=300)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField(default=1)

    def sous_total(self):
        return self.prix_unitaire * self.quantite
