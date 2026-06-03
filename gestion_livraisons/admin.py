from django.contrib import admin
from .models import Livraison, LivraisonEvenement


class LivraisonEvenementInline(admin.TabularInline):
    model = LivraisonEvenement
    extra = 1
    fields = ["statut", "lieu", "description", "icone"]


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ["commande", "type_livraison", "statut", "numero_suivi", "transporteur", "date_livraison_prevue"]
    list_filter = ["statut", "type_livraison"]
    list_editable = ["statut"]
    search_fields = ["commande__numero", "numero_suivi", "transporteur"]
    inlines = [LivraisonEvenementInline]
    readonly_fields = ["created_at"]


@admin.register(LivraisonEvenement)
class LivraisonEvenementAdmin(admin.ModelAdmin):
    list_display = ["livraison", "statut", "lieu", "date"]
    list_filter = ["statut"]
