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

def root_view(request):
    """Root endpoint for the application"""
    return JsonResponse({
        'message': 'REJLERS Backend API Server',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health/',
            'api': '/api/v1/',
            'admin': '/admin/',
            'docs': '/api/docs/',
        }
    })

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
            'hr_management': '/api/v1/hr/',
            'projects': '/api/projects/',
            'finance': '/api/finance/',
            'contracts': '/api/contracts/',
            'supply_chain': '/api/supply-chain/',
            'sales': '/api/sales/',
            'reporting': '/api/reporting/',
            'hse_compliance': '/api/hse/',
            'rto_apc': '/api/rto/',
            'documentation': '/api/docs/',
        },
        'timestamp': datetime.datetime.now().isoformat()
    })

# API URL patterns
api_v1_patterns = [
    path('', api_root, name='api-root'),
    path('health/', health_check, name='api-health-check'),
    path('auth/', include('apps.authentication.urls')),
    path('contacts/', include('apps.contacts.urls')),
    path('hr/', include('apps.hr_management.urls')),
    path('core/', include('apps.core.urls')),
]

# Business Module URL patterns
business_api_patterns = [
    path('projects/', include('apps.projects.urls')),
    path('finance/', include('apps.finance.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('supply-chain/', include('apps.supply_chain.urls')),
    path('sales/', include('apps.sales.urls')),
    path('reporting/', include('apps.reporting.urls')),
    path('hse/', include('apps.hse_compliance.urls')),
    path('rto/', include('apps.rto_apc.urls')),
]

# Main URL patterns
urlpatterns = [
    # Root endpoint
    path('', root_view, name='root'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health checks for deployment
    path('health/', health_check, name='health-check'),
    path('ready/', ready_check, name='ready-check'),
    
    # API v1 - Core APIs
    path('api/v1/', include(api_v1_patterns)),
    
    # Business Module APIs
    path('api/', include(business_api_patterns)),
    
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