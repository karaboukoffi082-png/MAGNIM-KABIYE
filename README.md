# KabiyèBooks 📚

Librairie en ligne spécialisée dans les ouvrages physiques en langue Kabiyè, togolais et africains. Propulsé par **Django 5/6 + Python**.

---

## 🛠️ Stack Technique

- **Backend** : Python 3.12+ / Django 6.0
- **Base de données** : PostgreSQL (Production via `psycopg2-binary`) / SQLite (Repli développement)
- **Fichiers Statiques** : Whitenoise (Servis de manière autonome avec compression & cache agressif)
- **Fichiers Médias** : Cloudinary (Stockage cloud persistant) / Système de fichiers local (Repli développement)
- **Interface** : Bootstrap 5.3 + Bootstrap Icons (via CDN pour un rendu rapide)
- **Formulaires** : django-crispy-forms + crispy-bootstrap5
- **Serveur WSGI** : Gunicorn (Production)

---

## 🚀 Lancement en Local (Développement & Tests)

### 1. Prérequis et Installation
Clonez le projet et créez votre environnement virtuel Python :
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows (PowerShell) :
venv\Scripts\Activate.ps1
# Sur Linux/macOS :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Base de données et Fichiers Statiques
Le projet est configuré pour basculer automatiquement sur une base SQLite locale et le stockage de fichiers local si aucune variable de production (PostgreSQL/Cloudinary) n'est définie dans votre fichier `.env`.

```bash
# Appliquer les migrations de base de données
python manage.py migrate

# Créer un compte administrateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

### 3. Exécuter les serveurs & Tests
```bash
# Lancer le serveur de développement local
python manage.py runserver

# Lancer la suite de tests unitaires
python manage.py test
```

---

## 🐋 Lancement en Production avec Docker

L'application intègre un environnement de conteneurisation complet optimisé pour la production.

```bash
# Construire et démarrer l'application avec docker-compose
docker compose up -d --build
```
Le conteneur `web-app` va automatiquement exécuter le script [docker-entrypoint.sh](file:///P:/PROJETS/ProjetsDev/COLLABORATION/KARABOU/MAGNIM-KABIYE/docker-entrypoint.sh) pour appliquer les migrations, collecter les fichiers statiques et lancer le serveur de production Gunicorn sur le port `8000`.

---

## 🌐 Déploiement sur Dokploy

Le projet est configuré pour être déployé en un clic sur **Dokploy** (alternative auto-hébergée à Heroku et Coolify).
Consultez le guide de déploiement détaillé étape par étape dans le fichier [DEPLOYMENT.md](file:///P:/PROJETS/ProjetsDev/COLLABORATION/KARABOU/MAGNIM-KABIYE/DEPLOYMENT.md).

---

## 📁 Structure du Projet

L'application est découpée en applications Django modulaires :

| Application | Description | Préfixe URL |
|---|---|---|
| `main` | Accueil, à propos, contact, promotions & tableau de bord admin personnalisé | `/`, `/admin-dashboard/` |
| `gestion_utilisateurs` | Modèle utilisateur personnalisé (`Utilisateur`), authentification & profils | `/utilisateurs/` |
| `gestion_livres` | Catalogue de livres physiques, avis des lecteurs et favoris | `/livres/` |
| `gestion_categories` | Taxonomie et catégories des livres (Kabiyè, Scolaire, Romans, etc.) | `/categories/` |
| `gestion_commandes` | Gestion du panier d'achat persistant et validation de commandes | `/commandes/` |
| `gestion_paiements` | Intégration des APIs de paiement (BKAPAY, Cashpay/Semoa) | `/paiements/` |
| `gestion_livraisons` | Suivi et gestion de l'état des livraisons physiques | `/livraisons/` |
| `gestion_notifications` | Système d'envoi interne et logs de SMS/Mails de notifications | *(Interne)* |
| `panier` | Gestion du panier utilisateur stocké en session (sans connexion requise) | `/panier/` |

---

## 🛡️ Décisions d'Architecture & Sécurité

- **Modèle Utilisateur Étendu** : Utilisation de `gestion_utilisateurs.Utilisateur` étendant `AbstractUser` pour intégrer des champs spécifiques (téléphone, ville, photo, flags administrateur) dès la création du projet.
- **Ressources Statiques Isolées** : Exclusion complète des bibliothèques locales d'actifs statiques du dépôt Git grâce à une configuration rigoureuse du [.gitignore](file:///P:/PROJETS/ProjetsDev/COLLABORATION/KARABOU/MAGNIM-KABIYE/.gitignore) et du [.dockerignore](file:///P:/PROJETS/ProjetsDev/COLLABORATION/KARABOU/MAGNIM-KABIYE/.dockerignore).
- **Routage SSL & CSRF** : Intégration de `SECURE_PROXY_SSL_HEADER` pour éviter les boucles de redirection HTTPS infinies sur les proxys comme Traefik ou Nginx.
