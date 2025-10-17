"""
Management command to clean up test users and keep only real sample users
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Clean up test users and keep only real sample users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Find test users to delete (but keep our seeded users)
        test_users_to_delete = User.objects.exclude(
            username__startswith='user'  # Keep our user01, user02, etc.
        ).exclude(
            is_superuser=True  # Keep superusers
        ).exclude(
            email__endswith='@admin.rejlers.com'  # Keep admin users
        )

        # Filter to remove bulk test and mock users
        test_users_to_delete = test_users_to_delete.filter(
            Q(username__startswith='bulk_test_') |
            Q(username__startswith='test_') |
            Q(email__contains='bulk_test') |
            Q(email__contains='test_orm') |
            Q(first_name__startswith='BulkUser') |
            Q(first_name__startswith='Test')
        )