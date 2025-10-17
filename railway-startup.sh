#!/bin/bash
# Railway Startup Script for REJLERS Django Backend

echo "🚀 Starting REJLERS Backend on Railway..."

# Set environment
export DJANGO_SETTINGS_MODULE=config.settings.railway_production
export PYTHONPATH=/app

# Database migrations
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Create cache table if using database cache
echo "🗄️ Setting up cache..."
python manage.py setup_cache || echo "Cache setup skipped"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (using environment variables)
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser creation skipped"
fi

echo "✅ Railway startup completed successfully!"

# Start the application
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile -
