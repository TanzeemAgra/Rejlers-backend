"""
Django management command to setup RBAC system and create Super Admin
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.authentication.models import User, Role, AuditLog


class Command(BaseCommand):
    help = 'Setup RBAC system with default roles and create Super Admin user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-roles',
            action='store_true',
            help='Skip creating default roles',
        )

    def handle(self, *args, **options):
        """Main command handler"""
        try:
            with transaction.atomic():
                if not options['skip_roles']:
                    self.create_default_roles()
                
                self.create_super_admin()
                self.stdout.write(
                    self.style.SUCCESS('Successfully setup RBAC system and Super Admin')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up RBAC system: {str(e)}')
            )

    def create_default_roles(self):
        """Create default system roles"""
        roles_data = [
            {
                'name': 'Super Admin',
                'description': 'Complete system access with all permissions',
                'permissions': {module: ['manage_all'] for module in Role.MODULE_PERMISSIONS.keys()}
            },
            {
                'name': 'Admin',
                'description': 'Administrative access to most modules',
                'permissions': {
                    'hr_management': ['view', 'create', 'edit', 'delete'],
                    'projects_engineering': ['view', 'create', 'edit', 'delete'],
                    'contracts_legal': ['view', 'create', 'edit'],
                    'finance_estimation': ['view', 'create', 'edit'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view', 'create', 'edit', 'delete'],
                    'supply_chain': ['view', 'create', 'edit', 'delete'],
                    'sales_engagement': ['view', 'create', 'edit', 'delete'],
                    'rto_apc_consulting': ['view', 'create', 'edit', 'delete'],
                    'user_management': ['view', 'create', 'edit'],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use']
                }
            },
            {
                'name': 'Manager',
                'description': 'Departmental management with limited admin access',
                'permissions': {
                    'hr_management': ['view', 'create', 'edit'],
                    'projects_engineering': ['view', 'create', 'edit'],
                    'contracts_legal': ['view', 'create'],
                    'finance_estimation': ['view', 'create', 'edit'],
                    'reporting_dashboards': ['view', 'create'],
                    'hse_compliance': ['view', 'create', 'edit'],
                    'supply_chain': ['view', 'create', 'edit'],
                    'sales_engagement': ['view', 'create', 'edit'],
                    'rto_apc_consulting': ['view', 'create', 'edit'],
                    'user_management': ['view'],
                    'ai_services': ['view', 'use']
                }
            },
            {
                'name': 'Senior Employee',
                'description': 'Senior level access with create and edit permissions',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'create', 'edit'],
                    'contracts_legal': ['view'],
                    'finance_estimation': ['view', 'create'],
                    'reporting_dashboards': ['view'],
                    'hse_compliance': ['view', 'create'],
                    'supply_chain': ['view', 'create'],
                    'sales_engagement': ['view', 'create', 'edit'],
                    'rto_apc_consulting': ['view', 'create', 'edit'],
                    'ai_services': ['view', 'use']
                }
            },
            {
                'name': 'Employee',
                'description': 'Standard employee access with basic permissions',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'create'],
                    'contracts_legal': ['view'],
                    'finance_estimation': ['view'],
                    'reporting_dashboards': ['view'],
                    'hse_compliance': ['view', 'create'],
                    'supply_chain': ['view'],
                    'sales_engagement': ['view', 'create'],
                    'rto_apc_consulting': ['view', 'create'],
                    'ai_services': ['view', 'use']
                }
            },
            {
                'name': 'Viewer',
                'description': 'Read-only access to selected modules',
                'permissions': {
                    'projects_engineering': ['view'],
                    'reporting_dashboards': ['view'],
                    'hse_compliance': ['view'],
                    'sales_engagement': ['view'],
                    'ai_services': ['view']
                }
            }
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'permissions': role_data['permissions']
                }
            )
            if created:
                self.stdout.write(f"Created role: {role.name}")
            else:
                # Update permissions for existing roles
                role.permissions = role_data['permissions']
                role.description = role_data['description']
                role.save()
                self.stdout.write(f"Updated role: {role.name}")

    def create_super_admin(self):
        """Create Super Admin user"""
        email = 'tanzeem.agra@gmail.com'
        password = 'Tanzeem@123'
        
        # Get or create Super Admin role
        super_admin_role, _ = Role.objects.get_or_create(
            name='Super Admin',
            defaults={
                'description': 'Complete system access with all permissions',
                'permissions': {module: ['manage_all'] for module in Role.MODULE_PERMISSIONS.keys()}
            }
        )
        
        # Create or update Super Admin user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': 'Tanzeem',
                'last_name': 'Agra',
                'company_name': 'Rejlers',
                'job_title': 'AI Team Lead',
                'phone_number': '+919108391872',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'is_verified': True,
                'is_approved': True,
                'role': super_admin_role,
                'employee_id': 'SA001',
                'department': 'IT Administration',
                'position': 'Super Administrator'
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"Created Super Admin user: {email}")
            
            # Log the creation
            AuditLog.objects.create(
                user=user,
                action='create',
                module='user_management',
                object_type='User',
                object_id=str(user.id),
                description=f'Super Admin user created: {user.email}',
                additional_data={'role': 'Super Admin', 'created_by': 'system'}
            )
        else:
            # Update existing user
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.role = super_admin_role
            user.save()
            self.stdout.write(f"Updated Super Admin user: {email}")

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuper Admin Credentials:\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'Role: {super_admin_role.name}'
            )
        )