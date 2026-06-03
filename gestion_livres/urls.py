from django.urls import path
from . import views

urlpatterns = [
    path("", views.boutique, name="boutique"),
    path("kabiye/", views.livres_kabiye, name="livres_kabiye"),
    path("favoris/", views.mes_favoris, name="mes_favoris"),
    path("telechargements/", views.mes_telechargements, name="mes_telechargements"),
    path("<slug:slug>/", views.detail_livre, name="detail_livre"),
    path("<slug:slug>/favori/", views.toggle_favori, name="toggle_favori"),
    path("<slug:slug>/telecharger/", views.telecharger_pdf, name="telecharger_pdf"),
]
