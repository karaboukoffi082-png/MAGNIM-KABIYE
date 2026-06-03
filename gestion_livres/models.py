from django.db import models
from django.utils.text import slugify
from django.db.models import Avg
from gestion_categories.models import Categorie
from gestion_utilisateurs.models import Utilisateur


class Langue(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    class Meta:
        verbose_name = "Langue"

    def __str__(self):
        return self.nom


class Livre(models.Model):
    TYPE_VENTE_CHOICES = [
        ("physique", "Livre physique uniquement"),
        ("numerique", "Livre numérique (PDF) uniquement"),
        ("les_deux", "Physique + PDF"),
    ]

    titre = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True, max_length=350)
    auteur = models.CharField(max_length=200)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name="livres")
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    type_vente = models.CharField(max_length=20, choices=TYPE_VENTE_CHOICES, default="physique")
    fichier_pdf = models.FileField(upload_to="livres/pdf/", blank=True, null=True)
    prix_pdf = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                   help_text="Laisser vide pour utiliser le même prix que le livre physique")
    langue = models.ForeignKey(Langue, on_delete=models.SET_NULL, null=True, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    nombre_pages = models.PositiveIntegerField(null=True, blank=True)
    maison_edition = models.CharField(max_length=200, blank=True)
    date_publication = models.DateField(null=True, blank=True)
    quantite_stock = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    en_vedette = models.BooleanField(default=False)
    image_principale = models.ImageField(upload_to="livres/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Livre"
        verbose_name_plural = "Livres"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    def prix_actuel(self):
        return self.prix_promo if self.prix_promo else self.prix

    def prix_pdf_actuel(self):
        if self.prix_pdf:
            return self.prix_pdf
        return self.prix_actuel()

    def note_moyenne(self):
        avg = self.avis.aggregate(avg=Avg("note"))["avg"]
        return round(avg, 1) if avg else 0

    def en_stock(self):
        return self.quantite_stock > 0

    def est_numerique(self):
        return self.type_vente in ("numerique", "les_deux")

    def est_physique(self):
        return self.type_vente in ("physique", "les_deux")


class TelechargementPDF(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="telechargements")
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name="telechargements")
    commande = models.ForeignKey("gestion_commandes.Commande", on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name="telechargements")
    date = models.DateTimeField(auto_now_add=True)
    nombre_telechargements = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ["utilisateur", "livre"]
        verbose_name = "Téléchargement PDF"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.utilisateur} — {self.livre}"


class ImageLivre(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="livres/galerie/")
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre"]


class AvisLivre(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name="avis")
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    note = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    commentaire = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ["livre", "auteur"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.auteur} - {self.livre} ({self.note}/5)"


class Favori(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="favoris")
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name="favoris")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["utilisateur", "livre"]
