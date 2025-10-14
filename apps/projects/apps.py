"""
Projects & Engineering Django App Configuration
"""
from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.projects'
    verbose_name = 'Projects & Engineering'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.projects.signals
        except ImportError:
            pass
