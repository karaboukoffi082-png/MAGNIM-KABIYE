from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("utilisateurs/", include("gestion_utilisateurs.urls")),
    path("livres/", include("gestion_livres.urls")),
    path("categories/", include("gestion_categories.urls")),
    path("panier/", include("panier.urls")),
    path("commandes/", include("gestion_commandes.urls")),
    path("paiements/", include("gestion_paiements.urls")),
    path("livraisons/", include("gestion_livraisons.urls")),
    path("notifications/", include("gestion_notifications.urls")),
    path("admin-dashboard/", include("main.admin_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
