from django.urls import path
from . import views

urlpatterns = [
    path("", views.voir_panier, name="voir_panier"),
    path("ajouter/<int:livre_id>/", views.ajouter_au_panier, name="ajouter_au_panier"),
    path("modifier/<int:ligne_id>/", views.modifier_quantite, name="modifier_quantite"),
    path("supprimer/<int:ligne_id>/", views.supprimer_du_panier, name="supprimer_du_panier"),
    path("vider/", views.vider_panier, name="vider_panier"),
]
