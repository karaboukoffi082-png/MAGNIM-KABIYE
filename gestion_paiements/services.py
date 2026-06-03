"""
Service d'intégration Mobile Money pour KabiyèBooks via BkaPay API v1.
Gestion des sessions de paiement avec redirection et vérification asynchrone.
"""

import logging
import requests
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

PREFIXES_FLOOZ = ("76", "77", "78", "79", "96", "97", "98", "99")
PREFIXES_TMONEY = ("70", "71", "72", "73", "74", "90", "91", "92", "93", "94")
DELAI_EXPIRATION_MINUTES = 15


class ErreurPaiement(Exception):
    pass


class MobileMoneyService:
    """
    Service unifié connecté à l'API v1 de BkaPay (Sessions de paiement).
    """

    def __init__(self, operateur: str):
        operateur = operateur.lower()
        if operateur not in ("flooz", "tmoney"):
            raise ErreurPaiement(f"Opérateur non supporté : {operateur}")
        self.operateur = operateur
        self.config = self._charger_config()

    def _charger_config(self) -> dict:
        # Charge la clé privée payin 'sk_payin_liv_...' depuis le .env
        api_key = getattr(settings, "BKAPAY_PUBLIC_KEY", "").strip(' "\'')
        
        # URL officielle de l'API v1
        base_url = "https://bkapay.com/api/v1"

        if self.operateur == "flooz":
            return {
                "api_key": api_key,
                "base_url": base_url,
                "channel": "FLOOZ",  # Attendu en majuscule par l'API v1
                "prefixes": PREFIXES_FLOOZ,
                "nom_affiche": "Flooz (Moov Africa)",
            }
        return {
            "api_key": api_key,
            "base_url": base_url,
            "channel": "TMONEY",  # Attendu en majuscule par l'API v1
            "prefixes": PREFIXES_TMONEY,
            "nom_affiche": "T-Money (Togocom)",
        }

    def valider_telephone(self, telephone: str) -> str:
        """Nettoie et valide le numéro de téléphone togolais."""
        telephone = telephone.replace(" ", "").replace("-", "").replace(".", "")
        if telephone.startswith("+228"):
            telephone = telephone[4:]
        elif telephone.startswith("228"):
            telephone = telephone[3:]

        if len(telephone) != 8:
            raise ErreurPaiement("Le numéro doit contenir 8 chiffres (ex: 90123456).")
        if not telephone.isdigit():
            raise ErreurPaiement("Le numéro de téléphone ne doit contenir que des chiffres.")

        if not any(telephone.startswith(p) for p in self.config["prefixes"]):
            autres = "T-Money" if self.operateur == "flooz" else "Flooz"
            raise ErreurPaiement(
                f"Ce numéro ne correspond pas à {self.config['nom_affiche']}. Veuillez vérifier ou choisir {autres}."
            )

        return telephone

    def initier_paiement(self, paiement) -> dict:
        """
        Appelle l'API v1 /payment-sessions pour initialiser la session.
        Renvoie l'URL de paiement vers laquelle rediriger l'utilisateur si nécessaire.
        """
        try:
            telephone = self.valider_telephone(paiement.telephone)
        except ErreurPaiement as exc:
            return {"succes": False, "message": str(exc)}

        # Endpoint v1 exact pour créer une session
        url_api = f"{self.config['base_url']}/payment-sessions"
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Structure de données attendue par l'API v1 (image_589e65.png)
        payload = {
            "amount": int(paiement.montant),
            "currency": "XOF",
            "description": f"Achat de livres sur KabiyèBooks - Commande {paiement.commande.numero}",
            "channels": [self.config["channel"]],
            "customer": {
                "phone": f"+228{telephone}"
            },
            "metadata": {
                "commande_numero": paiement.commande.numero,
                "paiement_id": paiement.id
            }
        }

        try:
            logger.info("Création de session de paiement v1 pour la commande %s", paiement.commande.numero)
            response = requests.post(url_api, json=payload, headers=headers, timeout=20)
            
            if response.status_code not in (200, 201):
                logger.error("BkaPay v1 a renvoyé une erreur %s: %s", response.status_code, response.text)
                return {"succes": False, "message": "La plateforme de paiement a refusé la transaction. Vérifiez vos accès."}
                
            data = response.json()
            logger.info("REPONSE BRUTE BKAPAY v1 : %s", data)
            
        except requests.exceptions.RequestException as e:
            logger.error("Erreur de connexion réseau avec l'API BkaPay v1 : %s", e)
            return {"succes": False, "message": "Impossible de joindre le serveur de paiement."}

        # Structure de réponse v1 : récupération de l'ID de session (session_id ou id)
        session_id = data.get("session_id") or data.get("id")
        payment_url = data.get("payment_url")

        if session_id:
            paiement.reference = session_id
            paiement.telephone = telephone
            paiement.statut = "initie"
            paiement.tentatives += 1
            paiement.expires_at = timezone.now() + timedelta(minutes=DELAI_EXPIRATION_MINUTES)
            paiement.message_operateur = "Session de paiement initialisée. En attente de validation."
            paiement.save()

            return {
                "succes": True,
                "transaction_id": session_id,
                "url_paiement": payment_url,
                "message": "Demande initialisée avec succès.",
            }
        
        return {
            "succes": False,
            "message": data.get("message", "BkaPay a refusé l'initialisation du paiement."),
        }

    def verifier_statut(self, paiement) -> dict:
        """
        Vérification manuelle (Polling) basée sur la récupération d'une session v1.
        """
        if not paiement.reference:
            return {"statut": "echoue", "message": "Transaction non initiée."}

        if paiement.est_expire() and paiement.statut not in ("valide", "echoue"):
            paiement.statut = "expire"
            paiement.save(update_fields=["statut", "updated_at"])
            return {"statut": "expire", "message": "Le délai de paiement a expiré."}

        # URL v1 de récupération de statut
        url_api = f"{self.config['base_url']}/payment-sessions/{paiement.reference}"
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Accept": "application/json"
        }

        try:
            response = requests.get(url_api, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                statut_bka = str(data.get("status", "")).upper() # "SUCCESS", "PENDING", "FAILED"
                
                nouveau_statut = paiement.statut
                if statut_bka == "SUCCESS":
                    nouveau_statut = "valide"
                elif statut_bka in ("FAILED", "EXPIRED"):
                    nouveau_statut = "echoue"
                
                if nouveau_statut != paiement.statut:
                    paiement.statut = nouveau_statut
                    paiement.message_operateur = f"Statut mis à jour : {statut_bka}"
                    paiement.save(update_fields=["statut", "message_operateur", "updated_at"])

                    if nouveau_statut == "valide":
                        paiement.commande.statut = "payee"
                        paiement.commande.save(update_fields=["statut", "updated_at"])
                        logger.info("Commande %s validée via Polling v1.", paiement.commande.numero)
        except Exception as e:
            logger.error("Erreur lors du contrôle de statut chez BkaPay v1: %s", e)

        return {"statut": paiement.statut, "message": paiement.message_operateur}


# --- WEBHOOKS DE NOTIFICATION SÉCURISÉS (v1) ---

def traiter_webhook_bkapay(payload: dict) -> bool:
    """
    Traite le webhook asynchrone envoyé par BkaPay v1 (SUCCESS, FAILED).
    """
    from .models import Paiement

    session_id = payload.get("session_id") or payload.get("id")
    statut_bka = str(payload.get("status", "")).upper() # "SUCCESS", "FAILED"

    if not session_id:
        logger.warning("Webhook BkaPay v1 : Payload reçu sans identifiant de session.")
        return False

    try:
        # Recherche du paiement local par l'identifiant de la session v1
        paiement = Paiement.objects.select_related("commande").get(reference=session_id)
    except Paiement.DoesNotExist:
        logger.warning("Webhook BkaPay v1 : Aucune transaction trouvée pour la session : %s", session_id)
        return False

    paiement.callback_data = payload
    
    if statut_bka == "SUCCESS":
        if paiement.statut != "valide":
            paiement.statut = "valide"
            paiement.message_operateur = "Paiement encaissé (Confirmé par Webhook BkaPay v1)."
            paiement.commande.statut = "payee"
            paiement.commande.save(update_fields=["statut", "updated_at"])
    elif statut_bka in ("FAILED", "EXPIRED"):
        paiement.statut = "echoue"
        paiement.message_operateur = f"Échec de la transaction signalé par l'opérateur ({statut_bka})."

    paiement.save()
    logger.info("Webhook v1 traité pour la commande %s. Statut final: %s", paiement.commande.numero, paiement.statut)
    return True