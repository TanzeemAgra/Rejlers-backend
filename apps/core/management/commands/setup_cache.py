"""
Management command to set up cache table for database caching fallback
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.cache import cache
from django.conf import settings


class Command(BaseCommand):
    help = 'Set up cache table if using database caching'

    def handle(self, *args, **options):
        # Check if we're using database caching
        default_cache = settings.CACHES['default']
        
        if default_cache['BACKEND'] == 'django.core.cache.backends.db.DatabaseCache':
            self.stdout.write('Setting up database cache table...')
            try:
                call_command('createcachetable')
                self.stdout.write(
                    self.style.SUCCESS('Successfully created cache table')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Cache table setup skipped: {e}')
                )
        else:
            self.stdout.write('Using Redis cache - no table setup needed')
        
        # Test cache
        try:
            cache.set('test_key', 'test_value', 1)
            test_val = cache.get('test_key')
            if test_val == 'test_value':
                self.stdout.write(
                    self.style.SUCCESS('Cache system is working correctly')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Cache test failed')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Cache test error: {e}')
            )