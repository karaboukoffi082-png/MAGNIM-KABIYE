from django.urls import path
from . import views

urlpatterns = [
    path("", views.mes_notifications, name="mes_notifications"),
    path("<int:pk>/lire/", views.marquer_lue, name="marquer_notification_lue"),
    path("tout-lire/", views.marquer_toutes_lues, name="marquer_toutes_lues"),
    path("api/count/", views.count_non_lues, name="notifications_count"),
]
