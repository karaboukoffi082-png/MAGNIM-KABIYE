from django.contrib import admin
from .models import Panier, LignePanier


class LignePanierInline(admin.TabularInline):
    model = LignePanier
    extra = 0


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ["utilisateur", "nombre_articles", "total", "updated_at"]
    inlines = [LignePanierInline]
