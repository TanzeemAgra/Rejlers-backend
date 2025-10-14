"""
HR Management Django App Configuration
"""
from django.apps import AppConfig


class HrManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hr_management'
    verbose_name = 'HR Management'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.hr_management.signals
        except ImportError:
            pass