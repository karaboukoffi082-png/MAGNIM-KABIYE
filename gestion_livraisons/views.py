from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Livraison, LivraisonEvenement


@login_required
def suivi_livraison(request, numero_commande):
    livraison = get_object_or_404(
        Livraison,
        commande__numero=numero_commande,
        commande__client=request.user,
    )
    evenements = livraison.evenements.order_by("-date")
    return render(request, "gestion_livraisons/suivi.html", {
        "livraison": livraison,
        "evenements": evenements,
    })
