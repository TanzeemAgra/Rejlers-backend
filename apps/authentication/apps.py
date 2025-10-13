"""
Authentication application configuration for REJLERS Backend
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Authentication & Users'
    
    def ready(self):
        """Initialize authentication application"""
        try:
            import apps.authentication.signals  # noqa
        except ImportError:
            pass
            pass