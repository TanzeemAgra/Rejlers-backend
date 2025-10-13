"""
Contacts application configuration for REJLERS Backend
"""

from django.apps import AppConfig


class ContactsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contacts'
    verbose_name = 'Contacts & Inquiries'
    
    def ready(self):
        """Initialize contacts application"""
        try:
            import apps.contacts.signals  # noqa
        except ImportError:
            pass