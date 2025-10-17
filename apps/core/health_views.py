from django.http import JsonResponse
from django.core.cache import cache
from django.db import connection
import sys
import os

def health_check(request):
    """Health check endpoint for Railway deployment"""
    
    # Add Railway diagnostics
    print(f"🔍 Health check called - Method: {request.method}, Path: {request.path}")
    
    health_data = {
        'status': 'healthy',
        'service': 'rejlers-backend',
        'environment': 'railway-production',
        'checks': {},
        'cache_backend': {
            'class': cache.__class__.__name__,
            'module': cache.__class__.__module__,
            'supports_increment': hasattr(cache, 'incr'),
        },
        'railway_diagnostics': {
            'port': os.getenv('PORT', 'Not set'),
            'project_id': os.getenv('RAILWAY_PROJECT_ID', 'Not set')[:8] + "..." if os.getenv('RAILWAY_PROJECT_ID') else 'Not set',
            'database_url': 'Set' if os.getenv('DATABASE_URL') else 'Not set',
            'redis_url': 'Set' if os.getenv('REDIS_URL') else 'Not set'
        }
    }
    
    try:
        # Database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_data['checks']['database'] = 'healthy'
    except Exception as e:
        health_data['checks']['database'] = f'unhealthy: {str(e)}'
        health_data['status'] = 'unhealthy'
    
    try:
        # Cache check with atomic increment test (for django-ratelimit compatibility)
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            # Test atomic increment operation
            cache.set('health_counter', 0, 30)
            try:
                new_val = cache.incr('health_counter')
                if new_val == 1:
                    health_data['checks']['cache'] = 'healthy (atomic increment: ✅)'
                else:
                    health_data['checks']['cache'] = f'unhealthy: atomic increment failed (got {new_val})'
            except Exception as incr_e:
                health_data['checks']['cache'] = f'unhealthy: atomic increment not supported - {str(incr_e)}'
                health_data['status'] = 'unhealthy'
        else:
            health_data['checks']['cache'] = 'unhealthy: cache test failed'
            health_data['status'] = 'unhealthy'
    except Exception as e:
        health_data['checks']['cache'] = f'unhealthy: {str(e)}'
        health_data['status'] = 'unhealthy'
    
    # Python version
    health_data['python_version'] = sys.version
    
    return JsonResponse(health_data)

def ready_check(request):
    """Ready check endpoint for Railway deployment"""
    
    ready_data = {
        'status': 'ready',
        'service': 'rejlers-backend',
        'message': 'Service is ready to accept requests'
    }
    
    return JsonResponse(ready_data)
