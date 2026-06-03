import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from gestion_commandes.models import Commande
from .models import Paiement
from .services import (
    ErreurPaiement,
    MobileMoneyService,
    traiter_webhook_bkapay,  # Importation de la fonction v2 unifiée
)

logger = logging.getLogger(__name__)


@login_required
def payer_commande(request, numero):
    """Page de sélection du mode de paiement."""
    commande = get_object_or_404(Commande, numero=numero, client=request.user)

    if hasattr(commande, "paiement") and commande.paiement.est_valide():
        messages.info(request, "Cette commande a déjà été payée.")
        return redirect("detail_commande", numero=numero)

    paiement_existant = getattr(commande, "paiement", None)
    return render(
        request,
        "gestion_paiements/payer.html",
        {"commande": commande, "paiement": paiement_existant},
    )


@login_required
@require_POST
def initier_paiement(request, numero):
    """Initie le paiement direct v2 et envoie vers la page d'attente du PIN."""
    commande = get_object_or_404(Commande, numero=numero, client=request.user)

    if hasattr(commande, "paiement") and commande.paiement.est_valide():
        return redirect("detail_commande", numero=numero)

    methode = request.POST.get("methode", "").strip()
    telephone = request.POST.get("telephone", "").strip()

    # Récupération sécurisée du montant total de la commande
    try:
        montant_total = commande.total()
    except TypeError:
        montant_total = commande.total

    # Cas du paiement en espèces à la livraison
    if methode == "especes":
        paiement, _ = Paiement.objects.get_or_create(
            commande=commande,
            defaults={
                "montant": montant_total,
                "methode": "especes",
                "statut": "en_attente",
                "message_operateur": "Paiement à effectuer à la livraison."
            }
        )
        if paiement.methode != "especes":
            paiement.methode = "especes"
            paiement.montant = montant_total
            paiement.statut = "en_attente"
            paiement.message_operateur = "Paiement à effectuer à la livraison."
            paiement.save()

        commande.statut = "confirmee"
        commande.save(update_fields=["statut", "updated_at"])
        messages.success(
            request,
            "Commande confirmée ! Vous paierez en espèces à la livraison.",
        )
        return redirect("detail_commande", numero=numero)

    # Validation initiale des opérateurs Mobile Money
    if methode not in ("flooz", "tmoney"):
        messages.error(request, "Méthode de paiement invalide.")
        return redirect("payer_commande", numero=numero)

    if not telephone:
        messages.error(request, "Veuillez entrer votre numéro de téléphone.")
        return redirect("payer_commande", numero=numero)

    # Instanciation du service pour nettoyer et valider le numéro de téléphone en amont
    try:
        service = MobileMoneyService(methode)
        telephone_nettoye = service.valider_telephone(telephone)
    except ErreurPaiement as exc:
        messages.error(request, str(exc))
        return redirect("payer_commande", numero=numero)

    # Enregistrement ou mise à jour de l'objet Paiement
    paiement, created = Paiement.objects.get_or_create(
        commande=commande,
        defaults={
            "montant": montant_total,
            "methode": methode,
            "telephone": telephone_nettoye,
            "statut": "initie"
        }
    )

    if not created:
        paiement.methode = methode
        paiement.montant = montant_total
        paiement.telephone = telephone_nettoye
        paiement.save()

    # Appel de la requête HTTP direct v2 vers BkaPay (Déclenche le pop-up USSD)
    resultat = service.initier_paiement(paiement)

    if not resultat.get("succes", False):
        messages.error(
            request,
            resultat.get("message", "Erreur lors de l'initiation du paiement avec BkaPay."),
        )
        return redirect("payer_commande", numero=numero)

    # Avec l'API Business v2 sans redirection, on envoie directement l'utilisateur
    # vers la page d'attente pour suivre l'état du push USSD en temps réel.
    messages.success(request, "Une demande de paiement a été envoyée sur votre téléphone.")
    return redirect("attente_paiement", numero=numero)


@login_required
def attente_paiement(request, numero):
    """Page d'attente avec minuterie et polling automatique."""
    commande = get_object_or_404(Commande, numero=numero, client=request.user)
    paiement = get_object_or_404(Paiement, commande=commande)

    if paiement.est_valide():
        return redirect("succes_paiement", numero=numero)

    if paiement.est_expire() and paiement.statut not in ("valide",):
        paiement.statut = "expire"
        paiement.save(update_fields=["statut", "updated_at"])

    return render(
        request,
        "gestion_paiements/attente.html",
        {
            "commande": commande,
            "paiement": paiement,
            "secondes_restantes": paiement.secondes_restantes(),
        },
    )


@login_required
def statut_paiement_ajax(request, numero):
    """Endpoint AJAX pour le polling de statut (appelé toutes les 4s)."""
    commande = get_object_or_404(Commande, numero=numero, client=request.user)
    paiement = get_object_or_404(Paiement, commande=commande)

    if paiement.methode in ("flooz", "tmoney") and paiement.statut in ("initie", "en_attente"):
        try:
            service = MobileMoneyService(paiement.methode)
            service.verifier_statut(paiement)
            paiement.refresh_from_db()
        except Exception as exc:
            logger.error("Erreur vérification statut BkaPay %s : %s", numero, exc)

    return JsonResponse(
        {
            "statut": paiement.statut,
            "statut_label": paiement.get_statut_display(),
            "valide": paiement.est_valide(),
            "expire": paiement.est_expire(),
            "peut_reessayer": paiement.peut_reessayer(),
            "secondes_restantes": paiement.secondes_restantes(),
            "message": paiement.message_operateur,
            "reference": paiement.reference or "",
        }
    )


@login_required
def succes_paiement(request, numero):
    """Page de confirmation de paiement réussi."""
    commande = get_object_or_404(Commande, numero=numero, client=request.user)
    paiement = get_object_or_404(Paiement, commande=commande)
    return render(
        request,
        "gestion_paiements/succes.html",
        {"commande": commande, "paiement": paiement},
    )


@login_required
@require_POST
def simuler_confirmation(request, numero):
    """Simule une confirmation opérateur (mode DEBUG uniquement)."""
    from django.conf import settings as conf

    if not conf.DEBUG:
        return JsonResponse({"erreur": "Non disponible en production."}, status=403)

    commande = get_object_or_404(Commande, numero=numero, client=request.user)
    paiement = get_object_or_404(Paiement, commande=commande)

    action = request.POST.get("action", "valider")
    if action == "valider":
        paiement.statut = "valide"
        paiement.message_operateur = "Paiement confirmed (simulation développement)."
        commande.statut = "payee"
        commande.save(update_fields=["statut", "updated_at"])
    else:
        paiement.statut = "echoue"
        paiement.message_operateur = "Paiement refusé (simulation développement)."

    paiement.save()
    return JsonResponse({"statut": paiement.statut, "valide": paiement.est_valide()})


@csrf_exempt
@require_POST
def webhook_flooz(request):
    """Reçoit les notifications de paiement Flooz (redirigé vers la logique v2 unifiée)."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"erreur": "Payload JSON invalide."}, status=400)

    succes = traiter_webhook_bkapay(payload)
    return JsonResponse({"recu": succes}, status=200 if succes else 404)


@csrf_exempt
@require_POST
def webhook_tmoney(request):
    """Reçoit les notifications de paiement T-Money (redirigé vers la logique v2 unifiée)."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"erreur": "Payload JSON invalide."}, status=400)

    succes = traiter_webhook_bkapay(payload)
    return JsonResponse({"recu": succes}, status=200 if succes else 404)