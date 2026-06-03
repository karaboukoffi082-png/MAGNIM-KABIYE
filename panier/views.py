from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Panier, LignePanier
from gestion_livres.models import Livre


@login_required
def voir_panier(request):
    panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
    return render(request, "panier/panier.html", {"panier": panier})


@login_required
def ajouter_au_panier(request, livre_id):
    livre = get_object_or_404(Livre, pk=livre_id, disponible=True)
    panier, _ = Panier.objects.get_or_create(utilisateur=request.user)

    ligne, created = LignePanier.objects.get_or_create(panier=panier, livre=livre)
    if not created:
        if ligne.quantite < livre.quantite_stock:
            ligne.quantite += 1
            ligne.save()
            messages.success(request, f"Quantité mise à jour pour « {livre.titre} ».")
        else:
            messages.warning(request, "Stock insuffisant.")
    else:
        messages.success(request, f"« {livre.titre} » ajouté au panier.")

    return redirect(request.META.get("HTTP_REFERER", "boutique"))


@login_required
def modifier_quantite(request, ligne_id):
    ligne = get_object_or_404(LignePanier, pk=ligne_id, panier__utilisateur=request.user)
    quantite = int(request.POST.get("quantite", 1))
    if quantite < 1:
        ligne.delete()
        messages.info(request, "Article retiré du panier.")
    elif quantite <= ligne.livre.quantite_stock:
        ligne.quantite = quantite
        ligne.save()
    else:
        messages.warning(request, "Stock insuffisant.")
    return redirect("voir_panier")


@login_required
def supprimer_du_panier(request, ligne_id):
    ligne = get_object_or_404(LignePanier, pk=ligne_id, panier__utilisateur=request.user)
    ligne.delete()
    messages.info(request, "Article retiré du panier.")
    return redirect("voir_panier")


@login_required
def vider_panier(request):
    panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
    panier.items.all().delete()
    messages.info(request, "Panier vidé.")
    return redirect("voir_panier")
