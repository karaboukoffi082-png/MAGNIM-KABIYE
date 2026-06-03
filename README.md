# KabiyèBooks

Specialized online bookstore for Kabiyè, Togolese, and African physical books — built with Django 5 + Python.

## Run & Operate

- `cd kabiye-books && python manage.py runserver 0.0.0.0:8000 --noreload` — dev server
- `cd kabiye-books && gunicorn kabiye_books.wsgi:application --bind 0.0.0.0:8000 --workers 2` — production server (used by workflow)
- `cd kabiye-books && python manage.py migrate` — apply DB migrations
- `cd kabiye-books && python manage.py makemigrations` — create new migrations
- `cd kabiye-books && python manage.py collectstatic --noinput` — collect static files
- `cd kabiye-books && python manage.py createsuperuser` — create an admin user

## Stack

- Python 3.11 + Django 5.2
- Django REST Framework (DRF)
- SQLite (dev) / PostgreSQL (prod via psycopg2-binary)
- Bootstrap 5.3 + Bootstrap Icons (CDN)
- django-crispy-forms + crispy-bootstrap5
- Whitenoise (static file serving)
- Gunicorn (WSGI server)
- Pillow (image handling)

## Where things live

- `kabiye-books/` — Django project root
- `kabiye-books/kabiye_books/` — project settings/urls/wsgi
- `kabiye-books/kabiye_books/settings.py` — main settings (AUTH_USER_MODEL, INSTALLED_APPS, etc.)
- `kabiye-books/kabiye_books/urls.py` — root URL routing
- `kabiye-books/templates/` — all HTML templates
- `kabiye-books/static/` — CSS (`style.css`) + JS (`main.js`)
- `kabiye-books/staticfiles/` — collected static files (auto-generated)
- `kabiye-books/db.sqlite3` — SQLite dev database
- `kabiye-books/requirements.txt` — Python dependencies
- `kabiye-books/media/` — user-uploaded files (book covers, etc.)

## Apps

| App | Purpose | URL prefix |
|-----|---------|-----------|
| `main` | Home, about, contact, promotions, admin dashboard | `/`, `/admin-dashboard/` |
| `gestion_utilisateurs` | Custom User model, auth, dashboard | `/utilisateurs/` |
| `gestion_livres` | Books, reviews, favorites | `/livres/` |
| `gestion_categories` | Book categories | `/categories/` |
| `gestion_commandes` | Orders | `/commandes/` |
| `gestion_paiements` | Payments | `/paiements/` |
| `gestion_livraisons` | Deliveries | `/livraisons/` |
| `gestion_notifications` | Notifications | (internal) |
| `panier` | Shopping cart | `/panier/` |

## Admin

- Django admin: `/admin/` — login with `admin` / `admin1234`
- Custom admin dashboard: `/admin-dashboard/`

## Architecture decisions

- Custom User model (`gestion_utilisateurs.Utilisateur`) extending `AbstractUser` — allows adding fields (phone, city, profile photo, is_admin_boutique flag)
- Cart stored in Django session (no login required to browse) via `panier` context processor
- Bootstrap 5.3 loaded from CDN (no npm/build step needed)
- Whitenoise serves static files directly (no Nginx needed in development or simple deployments)
- Gunicorn runs in production mode for the Replit workflow

## Product

- Browse books by category (Kabiyè, Togolais, Africain, Scolaire, Romans, etc.)
- Book detail pages with reviews and favoriting
- Shopping cart and checkout flow
- User accounts with order history and profile management
- Payment and delivery tracking
- Promotions/deals page
- Admin dashboard for managing books, orders, users

## User preferences

- Django + Python stack only (no Node.js/React)
- Bootstrap/Tailwind for styling (Bootstrap 5 chosen)
- SQLite for development, PostgreSQL-ready for production
- African-themed design: green/gold/brown palette, Playfair Display + Inter fonts

## Gotchas

- Run `makemigrations <app_name>` explicitly for each app when creating models (auto-detection may miss apps)
- Slug fields must use ASCII-only characters — use Django's `slugify()` (non-unicode) to avoid URL pattern mismatches
- `AUTH_USER_MODEL = "gestion_utilisateurs.Utilisateur"` is set — always use `get_user_model()` not `User` directly
- `collectstatic` must be run after changing static files when using Whitenoise
- The Django workflow uses Gunicorn (not `runserver`) for reliability in the Replit environment
- Cart context processor (`panier.context_processors.panier_count`) is added to TEMPLATES settings so cart count appears in navbar everywhere
