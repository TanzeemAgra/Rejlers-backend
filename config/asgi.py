"""
ASGI config for REJLERS Django Backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Use Railway-specific settings if RAILWAY_PROJECT_ID is present
if os.getenv('RAILWAY_PROJECT_ID'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway_production')
    print("🚂 Railway detected: Using railway_production settings for ASGI")
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    print("🖥️ Local/Other: Using production settings for ASGI")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # WebSocket handling (if you add WebSocket consumers later)
    # "websocket": AuthMiddlewareStack(
    #     URLRouter([
    #         # Add WebSocket URL patterns here when needed
    #     ])
    # ),
})