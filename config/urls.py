"""
URL Configuration for REJLERS Django Backend

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from apps.core.health_views import health_check, ready_check
import datetime

def api_root(request):
    """API root endpoint with basic information"""
    return JsonResponse({
        'message': 'Welcome to REJLERS Backend API',
        'company': 'REJLERS AB',
        'tagline': 'Engineering Excellence Since 1942',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/v1/auth/',
            'contacts': '/api/v1/contacts/',
            'services': '/api/v1/services/',
            'hr_management': '/api/v1/hr/',
            'documentation': '/api/docs/',
        },
        'timestamp': datetime.datetime.now().isoformat()
    })

# API URL patterns
api_v1_patterns = [
    path('', api_root, name='api-root'),
    path('auth/', include('apps.authentication.urls')),
    path('contacts/', include('apps.contacts.urls')),
    path('hr/', include('apps.hr_management.urls')),
    # path('services/', include('apps.services.urls')),  # Disabled - empty app
    path('core/', include('apps.core.urls')),
]

# Main URL patterns
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health checks for deployment
    path('health/', health_check, name='health-check'),
    path('ready/', ready_check, name='ready-check'),
    
    # API v1
    path('api/v1/', include(api_v1_patterns)),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Static and Media files (only in development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar URLs in development
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom admin configuration
admin.site.site_header = "REJLERS Backend Administration"
admin.site.site_title = "REJLERS Admin"
admin.site.index_title = "Welcome to REJLERS Backend Administration"