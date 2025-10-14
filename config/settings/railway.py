"""
Railway-specific Django settings with smart environment detection
"""
import os
import sys
from .production import *

# Railway Environment Detection
RAILWAY_ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT_NAME', '')
RAILWAY_PROJECT_ID = os.getenv('RAILWAY_PROJECT_ID', '')
IS_RAILWAY_BUILD = os.getenv('NIXPACKS_PLAN_PATH') is not None
IS_RAILWAY_RUNTIME = RAILWAY_PROJECT_ID and not IS_RAILWAY_BUILD

# Smart Database Configuration for Railway
if IS_RAILWAY_BUILD:
    # During build phase, use SQLite to avoid database connection issues
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    print("🔧 Railway Build Phase: Using in-memory SQLite")
    
    # Fix static files for build phase
    import os
    static_dir = BASE_DIR / 'static'
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(STATIC_ROOT, exist_ok=True)
    
elif IS_RAILWAY_RUNTIME:
    # During runtime, use the actual Railway database
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
        }
        print(f"🚀 Railway Runtime: Connected to {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'database'}")
    else:
        print("⚠️ Railway Runtime: No DATABASE_URL found")
        
else:
    # Local development or other environments
    print("🏠 Local Development: Using configured database")

# Railway-specific static files handling
if IS_RAILWAY_RUNTIME or IS_RAILWAY_BUILD:
    # Use WhiteNoise for static files in Railway
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # Create static directories if they don't exist
    os.makedirs(STATIC_ROOT, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)

# Railway CORS Configuration
if IS_RAILWAY_RUNTIME:
    RAILWAY_DOMAIN = os.getenv('RAILWAY_STATIC_URL', '').replace('https://', '').replace('http://', '')
    if RAILWAY_DOMAIN:
        ALLOWED_HOSTS.extend([
            RAILWAY_DOMAIN,
            f"{RAILWAY_DOMAIN}.up.railway.app"
        ])
        CORS_ALLOWED_ORIGINS.extend([
            f"https://{RAILWAY_DOMAIN}",
            f"https://{RAILWAY_DOMAIN}.up.railway.app"
        ])

# Environment-specific logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if IS_RAILWAY_RUNTIME else 'DEBUG',
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR' if IS_RAILWAY_BUILD else 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# Smart migration handling
if 'migrate' in sys.argv and IS_RAILWAY_BUILD:
    print("🚫 Skipping migrations during Railway build phase")
    sys.exit(0)

print(f"""
🌍 Environment Detection:
   Railway Build: {IS_RAILWAY_BUILD}
   Railway Runtime: {IS_RAILWAY_RUNTIME}
   Railway Project: {RAILWAY_PROJECT_ID[:8]}... if {RAILWAY_PROJECT_ID} else 'None'
   Environment: {RAILWAY_ENVIRONMENT or 'Local'}
""")