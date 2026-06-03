from django.urls import path
from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("a-propos/", views.a_propos, name="a_propos"),
    path("contact/", views.contact, name="contact"),
    path("promotions/", views.promotions, name="promotions"),
    path("faq/", views.faq, name="faq"),
    path("confidentialite/", views.confidentialite, name="confidentialite"),
    path("conditions/", views.conditions, name="conditions"),
]
