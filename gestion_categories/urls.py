from django.urls import path
from . import views

urlpatterns = [
    path("", views.liste_categories, name="categories"),
    path("<slug:slug>/", views.livres_par_categorie, name="livres_par_categorie"),
]
