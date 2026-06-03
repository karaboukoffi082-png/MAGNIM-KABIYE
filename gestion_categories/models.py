from django.db import models
from django.utils.text import slugify


class Categorie(models.Model):
    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, default="bi-book")
    couleur = models.CharField(max_length=20, default="#2d8a47", help_text="Couleur hex ex: #2d8a47")
    ordre = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sous_categories",
        verbose_name="Catégorie parente",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["ordre", "nom"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.nom} › {self.nom}"
        return self.nom

    def nombre_livres(self):
        count = self.livres.filter(disponible=True).count()
        for sous in self.sous_categories.filter(active=True):
            count += sous.livres.filter(disponible=True).count()
        return count

    def est_principale(self):
        return self.parent is None

    @classmethod
    def principales(cls):
        return cls.objects.filter(active=True, parent__isnull=True).prefetch_related(
            "sous_categories"
        ).order_by("ordre", "nom")
