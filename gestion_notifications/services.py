"""
Service de notifications — SMS (simulé en dev) et notifications in-app.
En production, remplacer send_sms() par un vrai provider (Twilio, Africa's Talking, etc.)
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms(telephone: str, message: str) -> bool:
    """Envoie un SMS. En DEV, log seulement. En PROD, connecter un provider réel."""
    from .models import SmsLog

    if settings.DEBUG:
        logger.info(f"[SMS SIMULÉ] → {telephone}: {message}")
        SmsLog.objects.create(
            telephone=telephone,
            message=message,
            statut="simule",
            reponse="Mode développement — SMS non envoyé réellement",
        )
        return True

    try:
        # TODO: Intégrer Africa's Talking ou autre provider SMS Togo
        # import africastalking
        # africastalking.initialize(username, api_key)
        # sms = africastalking.SMS
        # response = sms.send(message, [telephone])
        logger.warning("Provider SMS non configuré. SMS non envoyé.")
        SmsLog.objects.create(telephone=telephone, message=message, statut="echec", reponse="Provider non configuré")
        return False
    except Exception as e:
        logger.error(f"Erreur envoi SMS vers {telephone}: {e}")
        SmsLog.objects.create(telephone=telephone, message=message, statut="echec", reponse=str(e))
        return False


def notifier_utilisateur(utilisateur, type_notif: str, titre: str, message: str, lien: str = "") -> None:
    """Crée une notification in-app pour un utilisateur."""
    from .models import Notification
    Notification.objects.create(
        utilisateur=utilisateur,
        type=type_notif,
        titre=titre,
        message=message,
        lien=lien,
    )
    logger.info(f"Notification créée pour {utilisateur}: {titre}")


def notifier_nouvelle_commande(commande) -> None:
    """Notification et SMS lors d'une nouvelle commande."""
    utilisateur = commande.client
    lien = f"/commandes/{commande.numero}/"
    notifier_utilisateur(
        utilisateur,
        "commande",
        f"Commande #{commande.numero} confirmée",
        f"Votre commande de {commande.total} FCFA a bien été reçue. Nous la traitons dès que possible.",
        lien=lien,
    )
    if utilisateur.telephone:
        send_sms(
            utilisateur.telephone,
            f"KabiyèBooks: Votre commande #{commande.numero} ({commande.total} FCFA) est confirmée. Merci!",
        )


def notifier_paiement_recu(commande) -> None:
    """Notification paiement reçu."""
    utilisateur = commande.client
    lien = f"/commandes/{commande.numero}/"
    notifier_utilisateur(
        utilisateur,
        "paiement",
        "Paiement reçu ✓",
        f"Votre paiement de {commande.total} FCFA pour la commande #{commande.numero} a été reçu avec succès.",
        lien=lien,
    )
    if utilisateur.telephone:
        send_sms(
            utilisateur.telephone,
            f"KabiyèBooks: Paiement reçu ({commande.total} FCFA) pour commande #{commande.numero}. Merci!",
        )


def notifier_changement_livraison(livraison, nouveau_statut: str) -> None:
    """Notification et SMS lors d'un changement de statut de livraison."""
    commande = livraison.commande
    utilisateur = commande.client
    lien = f"/livraisons/suivi/{commande.numero}/"

    messages_statut = {
        "prepare": "Votre commande est en cours de préparation dans notre entrepôt.",
        "expedie": f"Votre commande #{commande.numero} a été expédiée par {livraison.transporteur}.",
        "en_transit": f"Votre colis est en transit. Numéro de suivi: {livraison.numero_suivi or 'À venir'}.",
        "en_livraison": "Votre colis est en cours de livraison. Soyez disponible.",
        "livree": f"Votre commande #{commande.numero} a été livrée. Bonne lecture! 📚",
        "echec": "Une tentative de livraison a échoué. Nous vous recontactons.",
    }

    message_notif = messages_statut.get(nouveau_statut, f"Statut livraison mis à jour: {nouveau_statut}")
    titres_statut = {
        "prepare": "📦 Commande en préparation",
        "expedie": "🚚 Commande expédiée",
        "en_transit": "🔄 Colis en transit",
        "en_livraison": "🏠 Livraison en cours",
        "livree": "✅ Commande livrée!",
        "echec": "⚠️ Échec de livraison",
    }
    titre_notif = titres_statut.get(nouveau_statut, "Mise à jour livraison")

    notifier_utilisateur(utilisateur, "livraison", titre_notif, message_notif, lien=lien)

    if utilisateur.telephone:
        send_sms(
            utilisateur.telephone,
            f"KabiyèBooks: {message_notif}",
        )
