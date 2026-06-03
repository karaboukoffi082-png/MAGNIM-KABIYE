# Guide de Déploiement sur Dokploy

Ce document explique comment déployer l'application **KabiyèBooks** sur un serveur VPS à l'aide de **Dokploy**.

Dokploy est une alternative auto-hébergée à Heroku ou Coolify qui utilise Docker pour orchestrer vos applications et bases de données. Deux méthodes de déploiement sont disponibles.

---

## Méthode 1 : Application Native + Base de Données Gérée (Recommandé)

Cette méthode est la plus robuste et la plus simple. Elle permet à Dokploy de gérer automatiquement les sauvegardes de la base de données, la sécurité et le routage SSL via Traefik sans avoir à gérer manuellement un fichier Compose.

### Étape 1 : Créer la Base de Données PostgreSQL
1. Connectez-vous à votre tableau de bord **Dokploy**.
2. Allez dans l'onglet **Databases** et cliquez sur **Create Database**.
3. Choisissez **PostgreSQL**.
4. Donnez-lui un nom (ex: `kabiye-db`).
5. Une fois créée, allez dans les détails de la base de données et copiez l'**Internal Connection String** (qui ressemble à `postgresql://postgres:motdepasse@nom-hote:5432/database`). Cette chaîne sera utilisée comme `DATABASE_URL`.

### Étape 2 : Créer l'Application
1. Allez dans l'onglet **Applications** et cliquez sur **Create Application**.
2. Connectez votre dépôt Git (GitHub/GitLab) ou configurez le déploiement par clé SSH.
3. Sélectionnez la branche principale (`main` ou `master`).
4. Dans **Build Provider**, choisissez **Dockerfile**. Dokploy détectera automatiquement le fichier `Dockerfile` à la racine du projet.

### Étape 3 : Configurer les Variables d'Environnement
Dans l'onglet **Environment** de votre application, ajoutez les variables suivantes :

| Variable | Valeur | Description |
|---|---|---|
| `DATABASE_URL` | *Coller l'Internal Connection String de l'Étape 1* | Connexion à la base de données PostgreSQL |
| `SECRET_KEY` | *Votre clé secrète Django de production* | Clé de chiffrement Django |
| `DEBUG` | `False` | Désactive le mode debug en production |
| `ALLOWED_HOSTS` | `centremagnim.com,www.centremagnim.com` | Vos domaines (séparés par des virgules) |
| `CSRF_TRUSTED_ORIGINS` | `https://centremagnim.com,https://www.centremagnim.com` | Origines autorisées pour les formulaires |
| `CLOUDINARY_CLOUD_NAME` | *Votre Cloud Name Cloudinary* | Stockage des images / couvertures de livres |
| `CLOUDINARY_API_KEY` | *Votre clé API Cloudinary* | Authentification Cloudinary |
| `CLOUDINARY_API_SECRET` | *Votre secret API Cloudinary* | Secret Cloudinary |
| `BREVO_SMTP_LOGIN` | *Votre email Brevo* | Identifiant d'envoi d'e-mails |
| `BREVO_SMTP_KEY` | *Votre clé SMTP Brevo* | Mot de passe SMTP Brevo |

### Étape 4 : Configurer le Domaine et SSL
1. Dans l'onglet **Domains** de l'application sur Dokploy, cliquez sur **Add Domain**.
2. Entrez votre nom de domaine (ex: `centremagnim.com` ou `www.centremagnim.com`).
3. Configurez le port de destination sur `8000` (port exposé par le conteneur).
4. Cochez la case **SSL** pour que Dokploy génère automatiquement un certificat Let's Encrypt gratuit.

### Étape 5 : Déployer
Cliquez sur **Deploy** dans Dokploy.
Le conteneur va se construire. Lors de son démarrage, le script `docker-entrypoint.sh` exécutera automatiquement :
1. Les migrations de la base de données (`python manage.py migrate`).
2. La collecte des fichiers statiques (`python manage.py collectstatic`).
3. Le serveur de production **Gunicorn** sur le port `8000`.

---

## Méthode 2 : Déploiement via Docker Compose

Si vous préférez exécuter la base de données et l'application ensemble à l'aide du fichier `docker-compose.yml` du projet :

### Étape 1 : Créer un Projet Compose
1. Sur Dokploy, allez dans **Compose** et cliquez sur **Create Compose**.
2. Liez votre dépôt Git et configurez le chemin vers le fichier `docker-compose.yml`.

### Étape 2 : Configurer les Variables d'Environnement
Ajoutez les variables d'environnement listées dans la Méthode 1 directement dans l'onglet **Environment** du projet Compose sur Dokploy. Elles seront automatiquement injectées dans le fichier Compose grâce à la syntaxe `${VARIABLE}`.

### Étape 3 : S'assurer du Réseau Externe
Le fichier `docker-compose.yml` nécessite un réseau externe appelé `dokploy-network` pour communiquer avec le proxy Traefik de Dokploy.
- Ce réseau est créé par défaut par Dokploy. S'il n'existe pas ou porte un autre nom, vous pouvez le créer sur votre VPS via SSH :
  ```bash
  docker network create dokploy-network
  ```

---

## Tâches Administratives Post-Déploiement

### Créer un Superutilisateur Django (Admin)
Une fois l'application déployée et fonctionnelle, vous devez créer un compte administrateur :
1. Allez dans les logs ou le terminal de l'application sur Dokploy.
2. Si Dokploy fournit une console interactive pour le conteneur applicatif, lancez :
   ```bash
   python manage.py createsuperuser
   ```
3. Sinon, connectez-vous en SSH à votre VPS, trouvez le conteneur en cours d'exécution :
   ```bash
   docker ps | grep web-app
   ```
4. Exécutez la commande directement dans le conteneur :
   ```bash
   docker exec -it <ID_DU_CONTENEUR> python manage.py createsuperuser
   ```
5. Suivez les instructions à l'écran pour définir le nom d'utilisateur, l'email et le mot de passe.
