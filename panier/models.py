from django.db import models
from gestion_utilisateurs.models import Utilisateur
from gestion_livres.models import Livre


class Panier(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name="panier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"

    def total(self):
        return sum(item.sous_total() for item in self.items.all())

    def nombre_articles(self):
        return sum(item.quantite for item in self.items.all())


class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name="items")
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["panier", "livre"]

    def sous_total(self):
        return self.livre.prix_actuel() * self.quantite
