from django.urls import path
from . import views

urlpatterns = [
    path("<str:numero>/", views.payer_commande, name="payer_commande"),
    path("<str:numero>/initier/", views.initier_paiement, name="initier_paiement"),
    path("<str:numero>/attente/", views.attente_paiement, name="attente_paiement"),
    path("<str:numero>/statut/", views.statut_paiement_ajax, name="statut_paiement_ajax"),
    path("<str:numero>/succes/", views.succes_paiement, name="succes_paiement"),
    path("<str:numero>/simuler/", views.simuler_confirmation, name="simuler_confirmation"),
    path("webhooks/flooz/", views.webhook_flooz, name="webhook_flooz"),
    path("webhooks/tmoney/", views.webhook_tmoney, name="webhook_tmoney"),
]
