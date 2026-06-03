from django.urls import path
from . import views

urlpatterns = [
    path("suivi/<str:numero_commande>/", views.suivi_livraison, name="suivi_livraison"),
]
