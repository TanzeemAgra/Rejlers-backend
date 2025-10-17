# 🔧 Railway Production Settings (Fixed)
# Optimized Django settings for Railway deployment using soft coding

import os
import sys
from .base import *
from decouple import config

# Railway startup diagnostics
print("🚀 REJLERS Backend - Railway Production Settings Loaded")
print(f"   Django Settings: {__name__}")
print(f"   PORT: {os.getenv('PORT', 'Not set')}")
print(f"   RAILWAY_PROJECT_ID: {os.getenv('RAILWAY_PROJECT_ID', 'Not set')[:8]}..." if os.getenv('RAILWAY_PROJECT_ID') else "   RAILWAY_PROJECT_ID: Not set")
print(f"   DATABASE_URL: {'Set' if os.getenv('DATABASE_URL') else 'Not set'}")
print(f"   Python Path: {sys.executable}")

# Debug and Development
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = [
    'rejlers-backend-production.up.railway.app',
    '.railway.app',
    'localhost',
    '127.0.0.1',
    config('RAILWAY_STATIC_URL', default='').replace('https://', '').replace('http://', ''),
]

# Database Configuration - Railway PostgreSQL
database_url = config('DATABASE_URL', default=None)
if database_url:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=600)
    }
    # Railway-specific database optimizations
    DATABASES['default'].update({
        'OPTIONS': {
            'connect_timeout': 30,
            'command_timeout': 30,
        },
        'CONN_MAX_AGE': 600,
    })

# CORS Settings for Production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    'https://rejlers-frontend.vercel.app',
    'https://rejlers.vercel.app', 
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    config('FRONTEND_URL', default='https://rejlers-frontend.vercel.app'),
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
    r"^https://.*\.railway\.app$",
]

# Cache Configuration - Fixed for Rate Limiting Compatibility
REDIS_URL = config('REDIS_URL', default=None)

if REDIS_URL:
    # Use Redis if available (Railway Redis addon)
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 20,
                    'retry_on_timeout': True,
                    'socket_connect_timeout': 5,
                    'socket_timeout': 5,
                },
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            }
        }
    }
else:
    # Fallback to local memory cache (supports atomic increment for rate limiting)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'rejlers-cache',
            'OPTIONS': {
                'MAX_ENTRIES': 10000,
                'CULL_FREQUENCY': 3,
            }
        }
    }

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hour

# Security Settings (Railway-optimized)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Cookie Security
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Static Files - WhiteNoise for Railway
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Email Configuration - Production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY', default='')

# Default email addresses
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@rejlers.com')
SERVER_EMAIL = config('SERVER_EMAIL', default='admin@rejlers.com')

# Production Logging (Railway-optimized)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Railway-specific optimizations
if config('RAILWAY_ENVIRONMENT', default=None):
    # Additional Railway optimizations
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_TZ = True
    
    # Optimize for Railway's build process
    STATICFILES_DIRS = []
    
    # Railway environment variables
    RAILWAY_ENVIRONMENT_NAME = config('RAILWAY_ENVIRONMENT_NAME', default='production')
    RAILWAY_PROJECT_ID = config('RAILWAY_PROJECT_ID', default='')
    RAILWAY_SERVICE_ID = config('RAILWAY_SERVICE_ID', default='')

# Rate Limiting Configuration (Fixed for Railway)
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)
RATELIMIT_USE_CACHE = 'default'  # Use the cache we just configured

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'REJLERS Backend API',
    'DESCRIPTION': 'Industrial consulting platform API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1',
    'SERVERS': [
        {
            'url': 'https://rejlers-backend-production.up.railway.app',
            'description': 'Production server (Railway)'
        },
        {
            'url': 'http://localhost:8000',
            'description': 'Development server'
        }
    ],
}

# Performance optimizations for Railway
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Railway deployment health checks
HEALTHCHECK_ENABLED = True
HEALTHCHECK_CACHE_TIMEOUT = 300

print("Railway production settings loaded successfully!")
print(f"Cache backend: {CACHES['default']['BACKEND']}")
print(f"Database: {'Railway PostgreSQL' if database_url else 'Local'}")
print(f"Debug mode: {DEBUG}")