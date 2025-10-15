#!/bin/bash
# Railway startup script with error handling and logging

echo "🚀 Starting REJLERS Backend on Railway..."

# Set environment
export DJANGO_SETTINGS_MODULE=config.settings.production

# Check environment variables
echo "📋 Environment Check:"
echo "  PORT: $PORT"
echo "  DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "  DATABASE_URL: ${DATABASE_URL:0:30}..." # Show first 30 chars only

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput
if [ $? -ne 0 ]; then
    echo "❌ Migration failed"
    exit 1
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "⚠️ Static files collection failed, continuing anyway"
fi

# Create superuser if needed (optional)
echo "👤 Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@rejlers.com', 'rejlers2024')
    print('✅ Superuser created')
else:
    print('✅ Superuser already exists')
EOF

# Start the server
echo "🌐 Starting Django server on 0.0.0.0:$PORT"
exec python manage.py runserver 0.0.0.0:$PORT