from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm, ProfilForm
from gestion_commandes.models import Commande


def inscription(request):
    if request.user.is_authenticated:
        return redirect("tableau_de_bord")
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé avec succès ! Bienvenue sur KabiyèBooks.")
            return redirect("tableau_de_bord")
    else:
        form = InscriptionForm()
    return render(request, "registration/inscription.html", {"form": form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect("tableau_de_bord")
    if request.method == "POST":
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next", "tableau_de_bord")
            return redirect(next_url)
        else:
            messages.error(request, "Identifiants incorrects. Veuillez réessayer.")
    else:
        form = ConnexionForm()
    return render(request, "registration/connexion.html", {"form": form})


def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect("accueil")


@login_required
def tableau_de_bord(request):
    commandes = Commande.objects.filter(client=request.user).order_by("-created_at")[:5]
    return render(request, "gestion_utilisateurs/tableau_de_bord.html", {
        "commandes": commandes,
    })


@login_required
def profil(request):
    if request.method == "POST":
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect("profil")
    else:
        form = ProfilForm(instance=request.user)
    return render(request, "gestion_utilisateurs/profil.html", {"form": form})


@login_required
def mes_commandes(request):
    commandes = Commande.objects.filter(client=request.user).order_by("-created_at")
    return render(request, "gestion_utilisateurs/mes_commandes.html", {"commandes": commandes})
