"""
Health check views for deployment monitoring
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import sys
import django
import psycopg2
from datetime import datetime

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Simple health check endpoint for Railway deployment monitoring
    """
    try:
        # Check database connection
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "django_version": django.VERSION,
        "python_version": sys.version,
        "database": db_status,
        "debug_mode": settings.DEBUG,
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "deployment": "railway",
    }
    
    return JsonResponse(health_data)

@csrf_exempt
@require_http_methods(["GET"])
def ready_check(request):
    """
    Readiness check for Railway deployment
    """
    try:
        # Check critical services
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM django_migrations")
        migration_count = cursor.fetchone()[0]
        
        return JsonResponse({
            "status": "ready",
            "database": "connected",
            "migrations": migration_count,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=503)