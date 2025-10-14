#!/bin/bash
"""
Smart Railway Startup Script with Environment Detection
Handles build vs runtime phases intelligently
"""

# Environment Detection
export RAILWAY_ENVIRONMENT_NAME="${RAILWAY_ENVIRONMENT_NAME:-production}"
export IS_RAILWAY_BUILD="${NIXPACKS_PLAN_PATH:+true}"
export IS_RAILWAY_RUNTIME="${RAILWAY_PROJECT_ID:+true}"

echo "🚀 REJLERS Backend - Railway Smart Startup"
echo "   Build Phase: ${IS_RAILWAY_BUILD:-false}"
echo "   Runtime Phase: ${IS_RAILWAY_RUNTIME:-false}"
echo "   Environment: ${RAILWAY_ENVIRONMENT_NAME}"

# Set Django settings based on environment
if [ "$IS_RAILWAY_BUILD" = "true" ]; then
    echo "🔧 Build Phase: Using railway settings"
    export DJANGO_SETTINGS_MODULE="config.settings.railway"
elif [ "$IS_RAILWAY_RUNTIME" = "true" ]; then
    echo "🏃 Runtime Phase: Using production settings"
    export DJANGO_SETTINGS_MODULE="config.settings.production"
else
    echo "🏠 Local Development: Using configured settings"
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.development}"
fi

# Only run migrations during runtime, not build
if [ "$IS_RAILWAY_RUNTIME" = "true" ]; then
    echo "📦 Running database migrations..."
    python manage.py migrate --noinput
    
    echo "📂 Collecting static files..."
    python manage.py collectstatic --noinput --clear
    
    echo "🏥 Running health check..."
    python manage.py check --deploy
fi

# Start the appropriate service
if [ "$1" = "web" ] || [ "$IS_RAILWAY_RUNTIME" = "true" ]; then
    echo "🌐 Starting Django web server..."
    exec python manage.py runserver 0.0.0.0:${PORT:-8000}
else
    echo "🔧 Build complete - no web server needed"
fi