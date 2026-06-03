from django.contrib import admin
from django.utils.html import format_html
from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = [
        "commande_lien",
        "methode_badge",
        "statut_badge",
        "montant_fcfa",
        "telephone",
        "reference",
        "tentatives",
        "created_at",
    ]
    list_filter = ["statut", "methode", "created_at"]
    search_fields = [
        "commande__numero",
        "reference",
        "telephone",
        "transaction_id",
    ]
    readonly_fields = [
        "reference",
        "transaction_id",
        "code_ussd",
        "tentatives",
        "expires_at",
        "callback_data",
        "message_operateur",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            "Informations générales",
            {
                "fields": (
                    "commande",
                    "methode",
                    "statut",
                    "montant",
                    "telephone",
                )
            },
        ),
        (
            "Détails opérateur",
            {
                "fields": (
                    "reference",
                    "transaction_id",
                    "code_ussd",
                    "tentatives",
                    "expires_at",
                    "message_operateur",
                )
            },
        ),
        (
            "Données webhook",
            {
                "classes": ("collapse",),
                "fields": ("callback_data",),
            },
        ),
        (
            "Horodatage",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
    ordering = ["-created_at"]

    @admin.display(description="Commande")
    def commande_lien(self, obj):
        return format_html(
            '<a href="/admin/gestion_commandes/commande/{}/change/">{}</a>',
            obj.commande.pk,
            obj.commande.numero,
        )

    @admin.display(description="Méthode")
    def methode_badge(self, obj):
        couleurs = {
            "flooz": "#0066CC",
            "tmoney": "#009900",
            "carte": "#333",
            "especes": "#8B4513",
        }
        couleur = couleurs.get(obj.methode, "#666")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:12px">{}</span>',
            couleur,
            obj.get_methode_display(),
        )

    @admin.display(description="Statut")
    def statut_badge(self, obj):
        couleurs = {
            "en_attente": "#6c757d",
            "initie": "#17a2b8",
            "en_cours": "#ffc107",
            "valide": "#28a745",
            "echoue": "#dc3545",
            "expire": "#6c757d",
            "annule": "#6c757d",
            "rembourse": "#007bff",
        }
        couleur = couleurs.get(obj.statut, "#666")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:4px;font-size:12px">{}</span>',
            couleur,
            obj.get_statut_display(),
        )

    @admin.display(description="Montant")
    def montant_fcfa(self, obj):
        return format_html("<strong>{:,.0f} FCFA</strong>", obj.montant)

    actions = ["marquer_valide", "marquer_echoue"]

    @admin.action(description="Marquer comme validé")
    def marquer_valide(self, request, queryset):
        for paiement in queryset:
            paiement.statut = "valide"
            paiement.save()
            paiement.commande.statut = "payee"
            paiement.commande.save(update_fields=["statut", "updated_at"])
        self.message_user(request, f"{queryset.count()} paiement(s) validé(s).")

    @admin.action(description="Marquer comme échoué")
    def marquer_echoue(self, request, queryset):
        queryset.update(statut="echoue")
        self.message_user(request, f"{queryset.count()} paiement(s) marqués échoués.")
