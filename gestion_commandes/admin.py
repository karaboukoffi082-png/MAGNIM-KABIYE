from django.contrib import admin
from .models import Commande, LigneCommande


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ["sous_total"]


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ["numero", "client", "statut", "total", "created_at"]
    list_filter = ["statut"]
    search_fields = ["numero", "client__username", "client__email"]
    list_editable = ["statut"]
    inlines = [LigneCommandeInline]
    readonly_fields = ["numero", "created_at", "updated_at"]
