from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.contrib import messages
from gestion_livres.models import Livre
from gestion_categories.models import Categorie
from gestion_commandes.models import Commande
from gestion_utilisateurs.models import Utilisateur
from .models import ContactMessage


def accueil(request):
    # Changement ici : Limitation à 4 livres au lieu de 8 pour l'affichage en colonne
    livres_vedette = Livre.objects.filter(disponible=True, en_vedette=True)[:4]
    livres_recents = Livre.objects.filter(disponible=True).order_by("-created_at")[:4]
    categories = Categorie.objects.filter(active=True, parent__isnull=True)[:6]
    return render(request, "main/accueil.html", {
        "livres_vedette": livres_vedette,
        "livres_recents": livres_recents,
        "categories": categories,
    })


def a_propos(request):
    return render(request, "main/a_propos.html")


def contact(request):
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        email = request.POST.get("email", "").strip()
        sujet = request.POST.get("sujet", "").strip()
        message_text = request.POST.get("message", "").strip()

        if nom and email and sujet and message_text:
            ContactMessage.objects.create(
                nom=nom,
                email=email,
                sujet=sujet,
                message=message_text,
            )
            messages.success(request, "Merci ! Votre message a bien été envoyé. Nous vous répondrons sous 24h.")
            return redirect("contact")
        else:
            messages.error(request, "Veuillez remplir tous les champs du formulaire.")

    return render(request, "main/contact.html")


def promotions(request):
    livres = Livre.objects.filter(disponible=True, prix_promo__isnull=False).order_by("-created_at")
    return render(request, "main/promotions.html", {"livres": livres})


def faq(request):
    return render(request, "main/faq.html")


def confidentialite(request):
    return render(request, "main/confidentialite.html")


def conditions(request):
    return render(request, "main/conditions.html")


# ─── Admin Dashboard ──────────────────────────────────────────────────────────
from django.contrib.admin.views.decorators import staff_member_required
from gestion_livres.forms import LivreForm
import datetime


@staff_member_required
def dashboard_admin(request):
    today = datetime.date.today()
    debut_mois = today.replace(day=1)

    total_ventes = Commande.objects.filter(statut="payee").aggregate(
        total=Sum("lignes__prix_unitaire")
    )["total"] or 0

    commandes_mois = Commande.objects.filter(created_at__date__gte=debut_mois).count()
    commandes_recentes = Commande.objects.order_by("-created_at")[:10]
    total_livres = Livre.objects.count()
    total_utilisateurs = Utilisateur.objects.count()
    stock_faible = Livre.objects.filter(quantite_stock__lte=5, disponible=True).order_by("quantite_stock")[:10]
    messages_non_lus = ContactMessage.objects.filter(lu=False).count()

    statuts = {}
    for choice in Commande.STATUT_CHOICES:
        statuts[choice[1]] = Commande.objects.filter(statut=choice[0]).count()

    return render(request, "admin_custom/dashboard.html", {
        "total_ventes": total_ventes,
        "commandes_mois": commandes_mois,
        "commandes_recentes": commandes_recentes,
        "total_livres": total_livres,
        "total_utilisateurs": total_utilisateurs,
        "stock_faible": stock_faible,
        "statuts": statuts,
        "messages_non_lus": messages_non_lus,
    })


@staff_member_required
def admin_livres(request):
    q = request.GET.get("q", "")
    livres = Livre.objects.all().order_by("-created_at")
    if q:
        livres = livres.filter(titre__icontains=q) | livres.filter(auteur__icontains=q)
    return render(request, "admin_custom/livres.html", {"livres": livres, "q": q})


@staff_member_required
def admin_ajouter_livre(request):
    form = LivreForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        livre = form.save()
        messages.success(request, f"Livre « {livre.titre} » ajouté avec succès !")
        return redirect("admin_livres")
    return render(request, "admin_custom/livre_form.html", {"form": form, "action": "Ajouter"})


@staff_member_required
def admin_modifier_livre(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    form = LivreForm(request.POST or None, request.FILES or None, instance=livre)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Livre « {livre.titre} » modifié avec succès !")
        return redirect("admin_livres")
    return render(request, "admin_custom/livre_form.html", {"form": form, "livre": livre, "action": "Modifier"})


@staff_member_required
def admin_supprimer_livre(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    if request.method == "POST":
        titre = livre.titre
        livre.delete()
        messages.success(request, f"Livre « {titre} » supprimé.")
    return redirect("admin_livres")


@staff_member_required
def admin_commandes(request):
    commandes = Commande.objects.all().order_by("-created_at")
    statut = request.GET.get("statut")
    if statut:
        commandes = commandes.filter(statut=statut)
    return render(request, "admin_custom/commandes.html", {
        "commandes": commandes,
        "statut_choices": Commande.STATUT_CHOICES,
    })


@staff_member_required
def admin_detail_commande(request, numero):
    commande = get_object_or_404(Commande, numero=numero)
    if request.method == "POST":
        nouveau_statut = request.POST.get("statut")
        if nouveau_statut and nouveau_statut in dict(Commande.STATUT_CHOICES):
            commande.statut = nouveau_statut
            commande.save()
            messages.success(request, f"Statut de la commande mis à jour : {commande.statut_label}")
    return render(request, "admin_custom/detail_commande.html", {
        "commande": commande,
        "statut_choices": Commande.STATUT_CHOICES,
    })


@staff_member_required
def admin_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all().order_by("-date_joined")
    return render(request, "admin_custom/utilisateurs.html", {"utilisateurs": utilisateurs})


@staff_member_required
def admin_messages_contact(request):
    msgs = ContactMessage.objects.all()
    ContactMessage.objects.filter(lu=False).update(lu=True)
    return render(request, "admin_custom/messages_contact.html", {"contact_messages": msgs})


@staff_member_required
def admin_categories(request):
    categories = Categorie.objects.select_related("parent").prefetch_related("sous_categories")
    return render(request, "admin_custom/categories.html", {"categories": categories})