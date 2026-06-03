from django.urls import path
from . import views

urlpatterns = [
    path("passer/", views.passer_commande, name="passer_commande"),
    path("<str:numero>/", views.detail_commande, name="detail_commande"),
    path("<str:numero>/annuler/", views.annuler_commande, name="annuler_commande"),
]
