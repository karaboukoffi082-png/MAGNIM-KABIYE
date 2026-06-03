from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["utilisateur", "type", "titre", "lue", "created_at"]
    list_filter = ["type", "lue"]
