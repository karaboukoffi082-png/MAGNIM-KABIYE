from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Commande, LigneCommande
from panier.models import Panier


@login_required
def passer_commande(request):
    panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
    if panier.items.count() == 0:
        messages.warning(request, "Votre panier est vide.")
        return redirect("voir_panier")

    if request.method == "POST":
        adresse = request.POST.get("adresse_livraison", "").strip()
        ville = request.POST.get("ville_livraison", "").strip()
        pays = request.POST.get("pays_livraison", "Togo").strip()

        if not adresse or not ville:
            messages.error(request, "Veuillez renseigner l'adresse de livraison.")
            return render(request, "gestion_commandes/passer_commande.html", {"panier": panier})

        commande = Commande.objects.create(
            client=request.user,
            adresse_livraison=adresse,
            ville_livraison=ville,
            pays_livraison=pays,
            frais_livraison=2000,
        )

        for item in panier.items.all():
            LigneCommande.objects.create(
                commande=commande,
                livre=item.livre,
                titre_livre=item.livre.titre,
                prix_unitaire=item.livre.prix_actuel(),
                quantite=item.quantite,
            )
            if item.livre.quantite_stock >= item.quantite:
                item.livre.quantite_stock -= item.quantite
                item.livre.save()

        panier.items.all().delete()
        messages.info(request, f"Commande {commande.numero} créée — Finalisez votre paiement pour confirmer.")
        return redirect("payer_commande", numero=commande.numero)

    return render(request, "gestion_commandes/passer_commande.html", {"panier": panier})


@login_required
def detail_commande(request, numero):
    commande = get_object_or_404(Commande, numero=numero, client=request.user)
    return render(request, "gestion_commandes/detail_commande.html", {"commande": commande})


@login_required
def annuler_commande(request, numero):
    commande = get_object_or_404(Commande, numero=numero, client=request.user)
    if commande.statut in ["en_attente", "confirmee"]:
        commande.statut = "annulee"
        commande.save()
        messages.success(request, "Commande annulée.")
    else:
        messages.error(request, "Cette commande ne peut plus être annulée.")
    return redirect("mes_commandes")
