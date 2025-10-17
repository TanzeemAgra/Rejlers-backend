"""
Development settings for REJLERS Backend project.

These settings are optimized for local development with debugging enabled.
"""

from .base import *
from decouple import config
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'testserver',  # For Django testing framework
    config('LOCAL_HOST', default='localhost'),
]

# Development-specific apps
DEV_ONLY_APPS = [
    'django_extensions',
    'debug_toolbar',
]

# Remove rate limiting from development
THIRD_PARTY_APPS_DEV = [app for app in THIRD_PARTY_APPS if app != 'django_ratelimit']
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS_DEV + LOCAL_APPS + DEV_ONLY_APPS

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

# Apply Soft Coding Configuration - Direct Implementation
# USER CREATION CONFIGURATION
USER_CREATION_CONFIG = {
    'auto_approve': os.getenv('AUTO_APPROVE_USERS', 'false').lower() == 'true',
    'auto_verify': os.getenv('AUTO_VERIFY_USERS', 'false').lower() == 'true',
    'default_role_id': os.getenv('DEFAULT_ROLE_ID', None),
    'send_welcome_email': os.getenv('SEND_WELCOME_EMAIL', 'true').lower() == 'true',
    'require_email_verification': os.getenv('REQUIRE_EMAIL_VERIFICATION', 'true').lower() == 'true',
    'password_policy': {
        'min_length': int(os.getenv('PASSWORD_MIN_LENGTH', '8')),
        'require_uppercase': os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true',
        'require_lowercase': os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'true').lower() == 'true',
        'require_numbers': os.getenv('PASSWORD_REQUIRE_NUMBERS', 'true').lower() == 'true',
        'require_special_chars': os.getenv('PASSWORD_REQUIRE_SPECIAL', 'false').lower() == 'true'
    }
}

# BULK IMPORT CONFIGURATION
BULK_IMPORT_CONFIG = {
    'max_users_per_batch': int(os.getenv('BULK_MAX_USERS_PER_BATCH', '100')),
    'auto_generate_passwords': os.getenv('BULK_AUTO_GENERATE_PASSWORDS', 'true').lower() == 'true',
    'password_length': int(os.getenv('BULK_PASSWORD_LENGTH', '12')),
    'auto_approve_all': os.getenv('BULK_AUTO_APPROVE_ALL', 'false').lower() == 'true',
    'auto_verify_all': os.getenv('BULK_AUTO_VERIFY_ALL', 'false').lower() == 'true',
    'skip_invalid_records': os.getenv('BULK_SKIP_INVALID_RECORDS', 'true').lower() == 'true',
    'ai_role_matching': os.getenv('BULK_AI_ROLE_MATCHING', 'true').lower() == 'true'
}

# RBAC CONFIGURATION
RBAC_CONFIG = {
    'enable_role_hierarchy': os.getenv('RBAC_ENABLE_ROLE_HIERARCHY', 'true').lower() == 'true',
    'auto_role_assignment': os.getenv('RBAC_AUTO_ROLE_ASSIGNMENT', 'true').lower() == 'true',
    'permission_caching': os.getenv('RBAC_PERMISSION_CACHING', 'true').lower() == 'true',
    'cache_timeout': int(os.getenv('RBAC_CACHE_TIMEOUT', '3600'))
}

# AI ROLE MATCHING CONFIGURATION
AI_ROLE_MATCHING_CONFIG = {
    'enable_ai_matching': os.getenv('AI_ROLE_MATCHING_ENABLED', 'true').lower() == 'true',
    'confidence_threshold': float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.7')),
    'learning_mode': os.getenv('AI_LEARNING_MODE', 'active').lower(),
    'fallback_role': os.getenv('AI_FALLBACK_ROLE', 'Employee')
}

# AUDIT CONFIGURATION
AUDIT_CONFIG = {
    'enable_audit_logging': os.getenv('AUDIT_LOGGING_ENABLED', 'true').lower() == 'true',
    'log_level': os.getenv('AUDIT_LOG_LEVEL', 'INFO').upper(),
    'retention_days': int(os.getenv('AUDIT_RETENTION_DAYS', '365'))
}

# SECURITY CONFIGURATION
SECURITY_CONFIG = {
    'password_expiry_days': int(os.getenv('PASSWORD_EXPIRY_DAYS', '90')),
    'max_login_attempts': int(os.getenv('MAX_LOGIN_ATTEMPTS', '5')),
    'session_timeout': int(os.getenv('SESSION_TIMEOUT', '28800'))
}

# NOTIFICATION CONFIGURATION
NOTIFICATION_CONFIG = {
    'admin_email': os.getenv('ADMIN_EMAIL', 'admin@rejlers.com'),
    'notify_admin_on_creation': os.getenv('NOTIFY_ADMIN_ON_USER_CREATION', 'true').lower() == 'true'
}

# PERFORMANCE CONFIGURATION
PERFORMANCE_CONFIG = {
    'paginate_users_by': int(os.getenv('PAGINATE_USERS_BY', '50')),
    'bulk_operation_chunk_size': int(os.getenv('BULK_OPERATION_CHUNK_SIZE', '100'))
}

# MONITORING CONFIGURATION
MONITORING_CONFIG = {
    'metrics_collection': os.getenv('METRICS_COLLECTION', 'true').lower() == 'true',
    'log_level': os.getenv('LOG_LEVEL', 'INFO').upper()
}

# Database - Development can use SQLite for quick setup
if config('USE_SQLITE', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# CORS Settings for Development - Soft Coded Configuration
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)

# Soft-coded CORS origins from environment
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js frontend
    "http://localhost:3001",  # Testing frontend  
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Add custom origins from environment variable
custom_origins = config('CUSTOM_CORS_ORIGINS', default='')
if custom_origins:
    CORS_ALLOWED_ORIGINS.extend([origin.strip() for origin in custom_origins.split(',') if origin.strip()])

# Comprehensive CORS headers for frontend integration
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
    'cache-control',
    'pragma',
    'expires',
]

# Additional CORS configuration for better frontend support
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# Email Backend for Development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache - Soft Coded for django-ratelimit Compatibility
# Use LocMem cache for development (supports atomic increment for rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'dev-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
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