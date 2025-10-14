"""
Base Django settings for REJLERS Backend project.

This file contains all the base configuration that's shared across environments.
Environment-specific settings should inherit from this file.
"""

import os
from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    'storages',
]

LOCAL_APPS = [
    'apps.core',
    'apps.authentication',
    'apps.contacts',
    'apps.services',
    'apps.hr_management',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Multi-Database Configuration (Soft Coding - Railway PostgreSQL & MongoDB)
import dj_database_url

# Primary Database: PostgreSQL (Railway)
database_url = config('DATABASE_URL', default=None)

if database_url:
    # Railway/Cloud PostgreSQL configuration
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=600)
    }
    # Add additional options for Railway
    DATABASES['default'].update({
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'require',
        }
    })
else:
    # Fallback: Individual environment variables (Local development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='rejlers_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
    }

# Secondary Database: MongoDB (MangaDB) - TEMPORARILY DISABLED
# Add MongoDB configuration using soft coding
# DATABASES['mangadb'] = {
#     'ENGINE': 'djongo',
#     'NAME': config('MONGODB_NAME', default='MangaDB'),
#     'CLIENT': {
#         'host': config('MONGODB_URL', default=f"mongodb://{config('MONGODB_HOST', default='localhost')}:{config('MONGODB_PORT', default='27017')}/{config('MONGODB_NAME', default='MangaDB')}"),
#         'username': config('MONGODB_USER', default=''),
#         'password': config('MONGODB_PASSWORD', default=''),
#         'authSource': config('MONGODB_NAME', default='MangaDB'),
#         'authMechanism': 'SCRAM-SHA-1',
#     }
# }

# Database Router Configuration - TEMPORARILY DISABLED
# DATABASE_ROUTERS = ['apps.core.routers.DatabaseRouter']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Stockholm'  # REJLERS is Swedish company
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Sites framework
SITE_ID = 1

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
}

# API Documentation with drf-spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'REJLERS Backend API',
    'DESCRIPTION': 'API documentation for REJLERS industrial consulting platform',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1',
}

# CORS Settings (will be overridden in environment-specific settings)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = []

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email Configuration (base settings)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# REJLERS Company Configuration
COMPANY_CONFIG = {
    'NAME': 'REJLERS',
    'FULL_NAME': 'REJLERS AB',
    'TAGLINE': 'Engineering Excellence Since 1942',
    'EMAIL': 'info@rejlers.se',
    'PHONE': '+46 (0)771 78 00 00',
    'ADDRESS': {
        'STREET': 'Box 30233',
        'CITY': 'Stockholm',
        'POSTAL_CODE': '104 25',
        'COUNTRY': 'Sweden'
    },
    'WEBSITE': 'https://www.rejlers.se',
    'LINKEDIN': 'https://www.linkedin.com/company/rejlers',
}

# Business Logic Configuration
BUSINESS_CONFIG = {
    'SERVICES': {
        'INDUSTRIAL_AUTOMATION': 'Industrial Automation & Control Systems',
        'ENERGY_SOLUTIONS': 'Energy & Power Systems',
        'INFRASTRUCTURE': 'Infrastructure & Civil Engineering',
        'ENVIRONMENTAL': 'Environmental Engineering',
        'CONSULTING': 'Technical Consulting Services',
    },
    'SECTORS': {
        'ENERGY': 'Energy & Utilities',
        'MANUFACTURING': 'Manufacturing & Industry',
        'INFRASTRUCTURE': 'Infrastructure & Transport',
        'ENVIRONMENTAL': 'Environmental & Sustainability',
        'TELECOMMUNICATIONS': 'Telecommunications',
    },
    'PROJECT_TYPES': {
        'FEASIBILITY_STUDY': 'Feasibility Studies',
        'DESIGN': 'Engineering Design',
        'IMPLEMENTATION': 'Project Implementation',
        'CONSULTING': 'Technical Consulting',
        'MAINTENANCE': 'Maintenance & Support',
    }
}

# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Security Settings (base configuration)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ===========================================
# AI SERVICES CONFIGURATION - OpenAI
# ===========================================
# OpenAI API Configuration with soft coding for security
OPENAI_API_KEY = config('OPENAI_API_KEY', default=None)
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4')
OPENAI_MAX_TOKENS = config('OPENAI_MAX_TOKENS', default=2000, cast=int)
OPENAI_TEMPERATURE = config('OPENAI_TEMPERATURE', default=0.7, cast=float)
OPENAI_TIMEOUT = config('OPENAI_TIMEOUT', default=30, cast=int)
OPENAI_ORGANIZATION = config('OPENAI_ORGANIZATION', default=None)

# AI Service Settings
AI_SERVICES = {
    'OPENAI': {
        'API_KEY': OPENAI_API_KEY,
        'MODEL': OPENAI_MODEL,
        'MAX_TOKENS': OPENAI_MAX_TOKENS,
        'TEMPERATURE': OPENAI_TEMPERATURE,
        'TIMEOUT': OPENAI_TIMEOUT,
        'ORGANIZATION': OPENAI_ORGANIZATION,
        'ENABLED': OPENAI_API_KEY is not None,
    }
}