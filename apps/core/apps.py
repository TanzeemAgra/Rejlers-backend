"""
Core application configuration for REJLERS Backend
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core Functionality'
    
    def ready(self):
        """Initialize core application"""
        # Import signals here to ensure they are registered
        try:
            import apps.core.signals  # noqa
        except ImportError:
            pass