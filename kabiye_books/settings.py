import os
import environ
from pathlib import Path

# Définition du dossier racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialisation de django-environ
env = environ.Env(
    DEBUG=(bool, False)  # Par défaut, False si la variable n'est pas trouvée
)

# Lecture du fichier .env
environ.Env.read_env(str(BASE_DIR / '.env'))

# --- SÉCURITÉ ET CONFIGURATION DE BASE ---
SECRET_KEY = env('SECRET_KEY', default='')
if not SECRET_KEY:
    import os
    import secrets
    print("=== DEBUG ENV KEYS ===")
    print("Clés d'environnement disponibles dans le conteneur :")
    print(sorted(list(os.environ.keys())))
    print("=======================")
    # Génération d'une clé temporaire pour éviter le crash au démarrage si absente sur Dokploy
    SECRET_KEY = secrets.token_hex(24)
    print("ATTENTION : SECRET_KEY manquante. Une clé temporaire aléatoire a été générée pour le démarrage.")
DEBUG = env.bool('DEBUG', default=False)

# Configuration des hôtes autorisés (Sécurité renforcée en production via le .env)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'] if DEBUG else [])


# --- CONFIGURATION SÉCURITÉ (S'adapte automatiquement local VS production) ---
if DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://0.0.0.0:8000",
    ]
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
else:
    # Paramètres recommandés pour Hostinger en HTTPS
    CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
        "https://centremagnim.com",
        "https://www.centremagnim.com",
    ])
    
    # CORRECTION CRUCIALE : On désactive la sécurité stricte des cookies SI on travaille sur une IP locale
    # Cela permet de tester le mode "Production locale" dans VS Code sans bloquer le CSRF.
    import sys
    is_local_run = any(addr in sys.argv for addr in ['127.0.0.1:8000', 'localhost:8000', 'runserver'])
    
    if is_local_run:
        CSRF_TRUSTED_ORIGINS += ["http://127.0.0.1:8000", "http://localhost:8000", "http://0.0.0.0:8000"]
        CSRF_COOKIE_SECURE = False
        SESSION_COOKIE_SECURE = False
    else:
        CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
        SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
        
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Indispensable pour éviter les boucles de redirection HTTPS sur Hostinger
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False) # Reste à False en local

# --- APPLICATIONS INSTALLÉES ---
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic", # Gestion parfaite des fichiers statiques en dev
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    
    # Ordre crucial : Cloudinary_storage doit être chargé AVANT staticfiles
    "cloudinary_storage",            
    "django.contrib.staticfiles",
    
    # Librairies tierces
    "rest_framework",
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",
    
    # Applications du projet (KabiyèBooks - MAGNIM)
    "main",
    "gestion_utilisateurs",
    "gestion_livres",
    "gestion_categories",
    "gestion_commandes",
    "gestion_paiements",
    "gestion_livraisons",
    "gestion_notifications",
    "panier",
]

# --- MIDDLEWARES ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Fichiers statiques autonomes
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Au-dessus de CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kabiye_books.urls"

# --- MOTEUR DE TEMPLATES ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "panier.context_processors.panier_count",
                "gestion_categories.context_processors.categories_nav",
            ],
        },
    },
]

WSGI_APPLICATION = "kabiye_books.wsgi.application"

# --- BASE DE DONNÉES (PostgreSQL ou SQLite par défaut) ---
import os

if env('REAL_DATABASE_URL', default=''):
    print("REAL_DATABASE_URL est present, utilisation de la connexion specifique...")
    DATABASES = {
        'default': env.db('REAL_DATABASE_URL')
    }
elif env('DATABASE_URL', default=''):
    print("DATABASE_URL est present, utilisation de la connexion standard...")
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
else:
    print("Fallback sur les variables individuelles...")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env('DB_NAME', default='centremagnim'),
            "USER": env('DB_USER', default='postgres'),
            "PASSWORD": env('DB_PASSWORD', default=''),
            "HOST": env('DB_HOST', default='localhost'),
            "PORT": env('DB_PORT', default='5432'),
        }
    }
print("Configuration DATABASES finale :", {k: (v if k != 'PASSWORD' else '********') for k, v in DATABASES['default'].items()})
print("==============================")

# --- VALIDATION DES MOTS DE PASSE ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- INTERNATIONALISATION (Configuré sur Lomé, Togo) ---
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Lome"
USE_I18N = True
USE_TZ = True

# --- FICHIERS STATIQUES ET MÉDIAS ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# L'optimisation du stockage WhiteNoise est gérée dans l'objet STORAGES ci-dessous

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CONFIGURATION DES COMPTES & AUTHENTIFICATION ---
AUTH_USER_MODEL = "gestion_utilisateurs.Utilisateur"

LOGIN_URL = "/utilisateurs/connexion/"
LOGIN_REDIRECT_URL = "/tableau-de-bord/"
LOGOUT_REDIRECT_URL = "/"

# --- CONFIGURATION CRISPY FORMS BOOTSTRAP 5 ---
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- CONFIGURATION CORS & REST FRAMEWORK ---
CORS_ALLOW_ALL_ORIGINS = True  # À passer à False en prod en listant tes origines réelles

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
}

# --- CONFIGURATION STORAGE (CLOUDINARY & WHITENOISE) ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
}
CLOUDINARY_STORAGE['STATICFILES_STORAGE'] = None

# Utilisation de Cloudinary si configuré, sinon repli sur le système de fichiers local
if CLOUDINARY_STORAGE['CLOUD_NAME']:
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

# Compatibilité avec django-cloudinary-storage (requis pour collectstatic de cette lib)
STATICFILES_STORAGE = STORAGES["staticfiles"]["BACKEND"]
DEFAULT_FILE_STORAGE = STORAGES["default"]["BACKEND"]


# =====================================================================
# --- APIS DE PAIEMENTS AFRICAINES ---
# =====================================================================

# --- BKAPAY (legacy) ---
BKAPAY_PUBLIC_KEY = env('BKAPAY_PUBLIC_KEY', default='')
BKAPAY_SECRET_WEBHOOK = env('BKAPAY_SECRET_WEBHOOK', default='')

# --- CASHPAY (SEMOA API v3 pour T-Money & Flooz au Togo) ---
CASHPAY_CLIENT_ID = env('CASHPAY_CLIENT_ID', default='')
CASHPAY_CLIENT_SECRET = env('CASHPAY_CLIENT_SECRET', default='')
CASHPAY_USERNAME = env('CASHPAY_USERNAME', default='')
CASHPAY_PASSWORD = env('CASHPAY_PASSWORD', default='')
CASHPAY_API_BASE_URL = env('CASHPAY_API_BASE_URL', default='https://api.semoa-payments.ovh/sandbox-v3')
CASHPAY_SECRET_WEBHOOK = env('CASHPAY_SECRET_WEBHOOK', default='')


# =====================================================================
# --- CONFIGURATION EMAILS TRANSITIONNELLE (BREVO SMTP) ---
# =====================================================================
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('BREVO_SMTP_HOST', default='smtp-relay.brevo.com')
    EMAIL_PORT = env.int('BREVO_SMTP_PORT', default=587)
    EMAIL_USE_TLS = env.bool('BREVO_SMTP_TLS', default=True)
    EMAIL_USE_SSL = env.bool('BREVO_SMTP_SSL', default=False)
    EMAIL_TIMEOUT = env.int('EMAIL_TIMEOUT', default=20)
    EMAIL_FAIL_SILENTLY = False

    # Identification SMTP
    EMAIL_HOST_USER = env('BREVO_SMTP_LOGIN', default='') or env('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env('BREVO_SMTP_KEY', default='') or env('EMAIL_HOST_PASSWORD', default='')

# Gestionnaires de l'expéditeur d'e-mails
BREVO_FROM_EMAIL = env('BREVO_FROM_EMAIL', default='centremagnim@gmail.com')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=f'KabiyèBooks <{BREVO_FROM_EMAIL}>')
SERVER_EMAIL = env('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# Sécurité token reset mot de passe (24h)
PASSWORD_RESET_TIMEOUT = env.int('PASSWORD_RESET_TIMEOUT', default=86400)


# =====================================================================
# --- LIENS OFFICIELS RÉSEAUX SOCIAUX (MAGNIM) ---
# =====================================================================
WHATSAPP_NUMBER = env('WHATSAPP_NUMBER', default='22870766060')
FACEBOOK_URL = env('FACEBOOK_URL', default='https://www.facebook.com/centremagnim')
TWITTER_URL = env('TWITTER_URL', default='https://twitter.com/centremagnim')
INSTAGRAM_URL = env('INSTAGRAM_URL', default='https://www.instagram.com/centremagnim/')
LINKEDIN_URL = env('LINKEDIN_URL', default='')
TIKTOK_URL = env('TIKTOK_URL', default='https://www.tiktok.com/@centremagnim')
YOUTUBE_URL = env('YOUTUBE_URL', default='')