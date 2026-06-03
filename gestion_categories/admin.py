from django.contrib import admin
from django.db.models import Count
from .models import Categorie


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    # Ajout et configuration des colonnes d'affichage
    list_display = ["nom", "parent", "slug", "ordre", "active", "nombre_livres"]
    list_editable = ["ordre", "active"]
    list_filter = ["active", "parent"]
    prepopulated_fields = {"slug": ("nom",)}
    search_fields = ["nom"]
    raw_id_fields = ["parent"]  # Ajouté ici pour éviter de charger une liste géante si tu as beaucoup de catégories

    def get_queryset(self, request):
        """
        Optimisation : On charge le parent en une seule requête (select_related)
        ET on calcule le nombre de livres associés à chaque catégorie (annotate)
        """
        return (
            super()
            .get_queryset(request)
            .select_related("parent")
            .annotate(_nombre_livres=Count("livres"))  # 'livres' doit correspondre au related_name dans ton modèle Livre
        )

    # Création de la méthode pour afficher le compteur dans le tableau
    @admin.display(ordering="_nombre_livres", description="Nombre de livres")
    def nombre_livres(self, obj):
        # Récupère la valeur calculée dans le get_queryset ou retourne 0 par défaut
        return getattr(obj, "_nombre_livres", 0)