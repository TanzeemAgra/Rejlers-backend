#!/bin/bash
# Railway startup script - ensures nixpacks usage

echo "🚀 REJLERS Backend - Railway Deployment"
echo "   Using nixpacks (Python auto-detection)"
echo "   Settings: $DJANGO_SETTINGS_MODULE"

# Collect static files
python manage.py collectstatic --noinput

# Run migrations  
python manage.py migrate --noinput

# Start gunicorn
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info