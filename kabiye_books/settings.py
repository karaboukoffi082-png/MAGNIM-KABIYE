import os
import sys
import secrets
from pathlib import Path
import environ

# --- DOSSIER RACINE DU PROJET ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- INITIALISATION DJANGO-ENVIRON ---
env = environ.Env(
    DEBUG=(bool, False)
)

# Lecture du fichier .env s'il existe
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

# --- SÉCURITÉ ET CONFIGURATION DE BASE ---
DEBUG = env.bool('DEBUG', default=False)

SECRET_KEY = env('SECRET_KEY', default='')
if not SECRET_KEY:
    print("=== WARNING: SECRET_KEY non définie dans l'environnement ===")
    SECRET_KEY = secrets.token_hex(24)
    if not DEBUG:
        print("ATTENTION : Génération d'une SECRET_KEY temporaire en production. Les sessions seront réinitialisées à chaque redémarrage !")

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost', '0.0.0.0'] if DEBUG else ['centremagnim.com', 'www.centremagnim.com', '.centremagnim.com'])

# --- SÉCURITÉ HTTPS & CSRF ---
if DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://0.0.0.0:8000",
    ]
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
else:
    CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
        "https://centremagnim.com",
        "https://www.centremagnim.com",
    ])
    CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
    SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
    
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)

# --- APPLICATIONS INSTALLÉES ---
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",  # Gestion des statiques en dev
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary_storage",

    # Librairies tierces
    "rest_framework",
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",

    # Applications du projet
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
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Directement après SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kabiye_books.urls"

# --- TEMPLATES ---
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

# --- BASE DE DONNÉES ---
DATABASE_URL = env('REAL_DATABASE_URL', default='') or env('DATABASE_URL', default='')

if DATABASE_URL:
    # URL de connexion PostgreSQL (ex: transmise par Dokploy/Heroku)
    DATABASES = {
        'default': env.db_url_config(DATABASE_URL)
    }
elif env('DB_PASSWORD', default=''):
    # Connexion PostgreSQL explicite via variables d'environnement
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
else:
    # Mode développement local / fallback SQLite si aucune info Postgres disponible
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- VALIDATION DES MOTS DE PASSE ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- INTERNATIONALISATION ---
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Lome"
USE_I18N = True
USE_TZ = True

# --- FICHIERS STATIQUES ET MÉDIAS ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Ignorer le mode strict pour éviter les erreurs de sourcemaps
WHITENOISE_MANIFEST_STRICT = False

# --- CONFIGURATION STORAGES (DJANGO 4.2+) ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
}

STORAGE_DEFAULT = (
    "cloudinary_storage.storage.MediaCloudinaryStorage"
    if CLOUDINARY_STORAGE['CLOUD_NAME']
    else "django.core.files.storage.FileSystemStorage"
)

# Utilisation de CompressedStaticFilesStorage pour éviter l'échec sur les fichiers .map manquants
STORAGE_STATIC = (
    "whitenoise.storage.CompressedStaticFilesStorage"
    if not DEBUG
    else "django.contrib.staticfiles.storage.StaticFilesStorage"
)

STORAGES = {
    "default": {
        "BACKEND": STORAGE_DEFAULT,
    },
    "staticfiles": {
        "BACKEND": STORAGE_STATIC,
    },
}

# Compatibilité legacy
DEFAULT_FILE_STORAGE = STORAGE_DEFAULT
STATICFILES_STORAGE = STORAGE_STATIC

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- AUTHENTIFICATION ---
AUTH_USER_MODEL = "gestion_utilisateurs.Utilisateur"
LOGIN_URL = "/utilisateurs/connexion/"
LOGIN_REDIRECT_URL = "/tableau-de-bord/"
LOGOUT_REDIRECT_URL = "/"

# --- CRISPY FORMS ---
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- CORS & REST FRAMEWORK ---
CORS_ALLOW_ALL_ORIGINS = DEBUG
if not DEBUG:
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
        "https://centremagnim.com",
        "https://www.centremagnim.com",
    ])

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

# --- PAIEMENTS ---
BKAPAY_PUBLIC_KEY = env('BKAPAY_PUBLIC_KEY', default='')
BKAPAY_SECRET_WEBHOOK = env('BKAPAY_SECRET_WEBHOOK', default='')

CASHPAY_CLIENT_ID = env('CASHPAY_CLIENT_ID', default='')
CASHPAY_CLIENT_SECRET = env('CASHPAY_CLIENT_SECRET', default='')
CASHPAY_USERNAME = env('CASHPAY_USERNAME', default='')
CASHPAY_PASSWORD = env('CASHPAY_PASSWORD', default='')
CASHPAY_API_BASE_URL = env('CASHPAY_API_BASE_URL', default='https://api.semoa-payments.ovh/sandbox-v3')
CASHPAY_SECRET_WEBHOOK = env('CASHPAY_SECRET_WEBHOOK', default='')

# --- EMAILS (BREVO SMTP) ---
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

    EMAIL_HOST_USER = env('BREVO_SMTP_LOGIN', default='') or env('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env('BREVO_SMTP_KEY', default='') or env('EMAIL_HOST_PASSWORD', default='')

BREVO_FROM_EMAIL = env('BREVO_FROM_EMAIL', default='centremagnim@gmail.com')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=f'KabiyèBooks <{BREVO_FROM_EMAIL}>')
SERVER_EMAIL = env('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

PASSWORD_RESET_TIMEOUT = env.int('PASSWORD_RESET_TIMEOUT', default=86400)

# --- RÉSEAUX SOCIAUX ---
WHATSAPP_NUMBER = env('WHATSAPP_NUMBER', default='22870766060')
FACEBOOK_URL = env('FACEBOOK_URL', default='https://www.facebook.com/centremagnim')
TWITTER_URL = env('TWITTER_URL', default='https://twitter.com/centremagnim')
INSTAGRAM_URL = env('INSTAGRAM_URL', default='https://www.instagram.com/centremagnim/')
LINKEDIN_URL = env('LINKEDIN_URL', default='')
TIKTOK_URL = env('TIKTOK_URL', default='https://www.tiktok.com/@centremagnim')
YOUTUBE_URL = env('YOUTUBE_URL', default='')