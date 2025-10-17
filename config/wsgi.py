"""
WSGI config for REJLERS Django Backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use Railway-specific settings if RAILWAY_PROJECT_ID is present
if os.getenv('RAILWAY_PROJECT_ID'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway_production')
    print("🚂 Railway detected: Using railway_production settings")
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    print("🖥️ Local/Other: Using production settings")

application = get_wsgi_application()