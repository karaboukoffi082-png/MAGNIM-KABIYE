from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_admin, name="dashboard_admin"),
    path("livres/", views.admin_livres, name="admin_livres"),
    path("livres/ajouter/", views.admin_ajouter_livre, name="admin_ajouter_livre"),
    path("livres/<int:pk>/modifier/", views.admin_modifier_livre, name="admin_modifier_livre"),
    path("livres/<int:pk>/supprimer/", views.admin_supprimer_livre, name="admin_supprimer_livre"),
    path("commandes/", views.admin_commandes, name="admin_commandes"),
    path("commandes/<str:numero>/", views.admin_detail_commande, name="admin_detail_commande"),
    path("utilisateurs/", views.admin_utilisateurs, name="admin_utilisateurs"),
    path("categories/", views.admin_categories, name="admin_categories"),
    path("messages/", views.admin_messages_contact, name="admin_messages_contact"),
]
