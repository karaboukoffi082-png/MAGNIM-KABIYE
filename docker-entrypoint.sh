#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== DÉMARRAGE DU CONTENEUR DJANGO ==="

# Attente éventuelle de la base de données (géré par depends_on de compose en dev, ou intégré dans les logs)
echo "Exécution des migrations de la base de données..."
python manage.py migrate --noinput

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "Démarrage du serveur Gunicorn..."
# GUNICORN_WORKERS par défaut à 3 si non défini
WORKERS=${GUNICORN_WORKERS:-3}
exec gunicorn kabiye_books.wsgi:application --bind 0.0.0.0:8000 --workers "$WORKERS"
