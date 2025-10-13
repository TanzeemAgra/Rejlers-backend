"""
Development settings for REJLERS Backend project.

These settings are optimized for local development with debugging enabled.
"""

from .base import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    config('LOCAL_HOST', default='localhost'),
]

# Development-specific apps
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

# Development-specific middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug Toolbar Configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# Database - Development can use SQLite for quick setup
if config('USE_SQLITE', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# CORS Settings for Development
CORS_ALLOW_ALL_ORIGINS = True  # Only for development!
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js frontend
    "http://localhost:3001",  # Testing frontend
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Email Backend for Development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache - Use dummy cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Logging - More verbose for development
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Create logs directory if it doesn't exist
import os
logs_dir = BASE_DIR / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(exist_ok=True)

# Static files - Simpler setup for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Security settings - Relaxed for development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Development-specific REST Framework settings
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += [
    'rest_framework.renderers.BrowsableAPIRenderer',  # Enable browsable API
]

# JWT Settings - Longer token life for development
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(hours=24)  # 24 hours for dev
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(days=30)  # 30 days for dev

# File uploads - Local storage for development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Development-specific business configuration
DEVELOPMENT_CONFIG = {
    'ENABLE_API_DOCS': True,
    'ENABLE_ADMIN_INTERFACE': True,
    'ALLOW_REGISTRATION': True,
    'REQUIRE_EMAIL_VERIFICATION': False,  # Simplified for development
    'ENABLE_DEBUG_FEATURES': True,
}

# Merge with base business config
BUSINESS_CONFIG.update(DEVELOPMENT_CONFIG)

# Print helpful development information
if DEBUG:
    print("=" * 50)
    print("🚀 REJLERS Backend - Development Mode")
    print("=" * 50)
    print(f"📍 Base Directory: {BASE_DIR}")
    print(f"🗄️  Database: {DATABASES['default']['ENGINE']}")
    print(f"🌐 CORS Origins: {CORS_ALLOWED_ORIGINS}")
    print(f"📧 Email Backend: {EMAIL_BACKEND}")
    print("=" * 50)