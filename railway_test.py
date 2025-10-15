"""
Simple Railway Django deployment test
"""
import os
import sys
import django
from django.conf import settings
from django.http import JsonResponse

# Minimal Django setup for Railway testing
def simple_health_check():
    """Simple health check that doesn't require full Django setup"""
    return {
        "status": "ok",
        "message": "REJLERS Backend is running",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "unknown"),
        "port": os.environ.get("PORT", "not-set"),
    }

if __name__ == "__main__":
    # Print environment for debugging
    print("RAILWAY ENVIRONMENT DEBUG:")
    print(f"PORT: {os.environ.get('PORT')}")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')[:50]}...")
    print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
    # Test basic health
    health = simple_health_check()
    print(f"Health check: {health}")
    
    # Now run normal Django
    os.system("python manage.py runserver 0.0.0.0:${PORT:-8000}")