import environ
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Initialisation de l'environnement pour récupérer la clé secrette
env = environ.Env()

def executer_creation_campagne(nom_campagne, sujet, contenu_html, liste_ids=[2], date_programmation=None):
    """
    Fonction réutilisable pour créer et programmer une campagne email sur Brevo.
    """
    # 1. Récupération et configuration de la clé API
    api_key = env('BREVO_API_KEY', default=None)
    if not api_key:
        print("Erreur : BREVO_API_KEY n'est pas configurée dans le fichier .env")
        return None

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key

    # 2. Initialisation du client Brevo
    api_instance = sib_api_v3_sdk.EmailCampaignsApi(sib_api_v3_sdk.ApiClient(configuration))

    # 3. Définition des destinataires
    campaign_recipients = sib_api_v3_sdk.CreateEmailCampaignRecipients(
        list_ids=liste_ids
    )

    # 4. Préparation des données de la campagne
    champs_campagne = {
        "name": nom_campagne,
        "subject": sujet,
        "sender": {"name": "Centre Magnim", "email": "centremagnim@gmail.com"},
        "type": "classic",
        "html_content": contenu_html,
        "recipients": campaign_recipients
    }

    # Si une date de programmation est fournie, on l'ajoute (Format attendu : "2026-06-01T10:00:00.000Z")
    if date_programmation:
        champs_campagne["scheduled_at"] = date_programmation

    email_campaigns = sib_api_v3_sdk.CreateEmailCampaign(**champs_campagne)

    # 5. Envoi de la requête à Brevo
    try:
        api_response = api_instance.create_email_campaign(email_campaigns)
        return api_response
    except ApiException as e:
        print(f"Erreur lors de la création de la campagne Brevo : {e}")
        return None