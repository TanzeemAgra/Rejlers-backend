"""
Management command to seed sample users for testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.authentication.models import User, Role
import uuid


class Command(BaseCommand):
    help = 'Create sample users for testing user management functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample users to create (default: 10)',
        )
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Delete existing sample users before creating new ones',
        )

    def handle(self, *args, **options):
        count = options['count']
        delete_existing = options['delete_existing']

        if delete_existing:
            # Delete existing sample users
            deleted_count = User.objects.filter(
                email__contains='@rejlers.com',
                first_name__startswith='User'
            ).delete()[0]
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing sample users')
            )

        # Get available roles
        roles = list(Role.objects.filter(is_active=True))
        
        created_users = []
        
        for i in range(1, count + 1):
            # Create user data
            user_data = {
                'id': uuid.uuid4(),
                'username': f'user{i:02d}',
                'email': f'user{i:02d}@rejlers.com',
                'first_name': 'User',
                'last_name': str(i),
                'employee_id': f'EMP{1000 + i}',
                'company_name': 'REJLERS AB',
                'department': self._get_department(i),
                'job_title': self._get_job_title(i),
                'phone_number': f'+46 70 {1000000 + i}',
                'is_active': True,
                'is_verified': True,
                'is_approved': True,
                'password': make_password('TempPass123!'),  # Temporary password
            }
            
            # Assign role if available
            if roles:
                user_data['role'] = roles[i % len(roles)]
            
            # Create user
            try:
                user = User.objects.create(**user_data)
                created_users.append(user)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created user: {user.username} ({user.email}) - Role: {user.role.name if user.role else "No Role"}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create user {i}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {len(created_users)} sample users!'
            )
        )
        
        if created_users:
            self.stdout.write('\nSample login credentials:')
            self.stdout.write('Username: user01 | Email: user01@rejlers.com | Password: TempPass123!')
            self.stdout.write('Username: user02 | Email: user02@rejlers.com | Password: TempPass123!')
            self.stdout.write('...')

    def _get_department(self, index):
        departments = [
            'Engineering', 'IT', 'HR', 'Finance', 'Operations', 
            'Marketing', 'Sales', 'Research', 'Quality', 'Support'
        ]
        return departments[index % len(departments)]

    def _get_job_title(self, index):
        titles = [
            'Software Engineer', 'Senior Developer', 'Project Manager', 
            'System Analyst', 'DevOps Engineer', 'QA Engineer',
            'Business Analyst', 'Technical Lead', 'Consultant', 'Specialist'
        ]
        return titles[index % len(titles)]