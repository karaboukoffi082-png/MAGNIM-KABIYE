from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["nom", "email", "sujet", "lu", "created_at"]
    list_filter = ["lu"]
    list_editable = ["lu"]
    search_fields = ["nom", "email", "sujet"]
    readonly_fields = ["created_at"]
