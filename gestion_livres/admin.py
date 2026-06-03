from django.contrib import admin
from .models import Livre, Langue, ImageLivre, AvisLivre, Favori


class ImageLivreInline(admin.TabularInline):
    model = ImageLivre
    extra = 2


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ["titre", "auteur", "categorie", "prix", "quantite_stock", "disponible", "en_vedette", "created_at"]
    list_filter = ["disponible", "en_vedette", "categorie", "langue"]
    list_editable = ["disponible", "en_vedette", "quantite_stock"]
    search_fields = ["titre", "auteur", "isbn"]
    prepopulated_fields = {"slug": ("titre",)}
    inlines = [ImageLivreInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Langue)
class LangueAdmin(admin.ModelAdmin):
    list_display = ["nom", "code"]


@admin.register(AvisLivre)
class AvisLivreAdmin(admin.ModelAdmin):
    list_display = ["livre", "auteur", "note", "created_at"]
    list_filter = ["note"]
