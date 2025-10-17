# Railway Procfile for REJLERS Django Backend
release: python manage.py migrate --settings=config.settings.railway_production && python manage.py collectstatic --noinput --settings=config.settings.railway_production
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100
