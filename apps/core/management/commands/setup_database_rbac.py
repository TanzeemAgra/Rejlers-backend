"""
Database Schema Separation and RBAC Implementation
=================================================

Comprehensive PostgreSQL schema separation with role-based access control:
- Schema-level permission management
- AI-powered data access monitoring  
- Sensitive data isolation
- Role-based database privileges
"""

import os
import logging
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set up PostgreSQL schema separation with RBAC'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-schemas',
            action='store_true',
            help='Create separate schemas for different data types',
        )
        parser.add_argument(
            '--create-roles',
            action='store_true',
            help='Create PostgreSQL roles for different user types',
        )
        parser.add_argument(
            '--setup-permissions',
            action='store_true',
            help='Set up role-based permissions on schemas',
        )
        parser.add_argument(
            '--migrate-data',
            action='store_true',
            help='Migrate existing data to appropriate schemas',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all setup operations',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting PostgreSQL RBAC schema separation setup...')
        )

        try:
            if options['all']:
                options['create_schemas'] = True
                options['create_roles'] = True 
                options['setup_permissions'] = True
                options['migrate_data'] = True

            if options['create_schemas']:
                self.create_schemas()
            
            if options['create_roles']:
                self.create_database_roles()
            
            if options['setup_permissions']:
                self.setup_schema_permissions()
            
            if options['migrate_data']:
                self.migrate_existing_data()

            self.stdout.write(
                self.style.SUCCESS('PostgreSQL RBAC setup completed successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during setup: {str(e)}')
            )
            logger.error(f'PostgreSQL RBAC setup error: {str(e)}', exc_info=True)

    def create_schemas(self):
        """Create separate schemas for different data types"""
        self.stdout.write('Creating database schemas...')
        
        schemas = {
            'public_data': 'General application data accessible to all users',
            'hr_data': 'Human resources and employee data (highly sensitive)',
            'finance_data': 'Financial records and accounting data (highly sensitive)',
            'executive_data': 'Executive and strategic information (maximum security)',
            'project_data': 'Project management and operational data',
            'ai_data': 'AI models, analytics, and machine learning data',
            'audit_data': 'Security logs and audit trails (read-only for most)',
            'temp_data': 'Temporary processing and staging data',
        }

        with connection.cursor() as cursor:
            for schema_name, description in schemas.items():
                try:
                    # Create schema
                    cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {schema_name}')
                    
                    # Add comment
                    cursor.execute(
                        f"COMMENT ON SCHEMA {schema_name} IS %s",
                        [description]
                    )
                    
                    self.stdout.write(f'  ✓ Created schema: {schema_name}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Schema {schema_name} may already exist: {str(e)}')
                    )

    def create_database_roles(self):
        """Create PostgreSQL roles corresponding to application roles"""
        self.stdout.write('Creating database roles...')
        
        # Database roles with their privileges
        db_roles = {
            # Administrative roles
            'db_superadmin': {
                'description': 'Database superuser with full access',
                'privileges': ['CREATEDB', 'CREATEROLE', 'REPLICATION'],
                'schemas': ['ALL'],
                'inherit': True,
            },
            
            # Executive roles
            'db_executive': {
                'description': 'Executive access to all business data',
                'privileges': ['CONNECT'],
                'schemas': ['public_data', 'project_data', 'finance_data', 'hr_data', 'executive_data'],
                'inherit': True,
            },
            
            # Departmental roles  
            'db_hr_manager': {
                'description': 'HR department full access',
                'privileges': ['CONNECT'],
                'schemas': ['public_data', 'project_data', 'hr_data'],
                'inherit': True,
            },
            
            'db_finance_manager': {
                'description': 'Finance department full access',
                'privileges': ['CONNECT'],
                'schemas': ['public_data', 'project_data', 'finance_data'],
                'inherit': True,
            },
            
            'db_project_manager': {
                'description': 'Project management access',
                'privileges': ['CONNECT'],
                'schemas': ['public_data', 'project_data'],
                'inherit': True,
            },
            
            # Specialist roles
            'db_ai_specialist': {
                'description': 'AI and data science access',
                'privileges': ['CONNECT'],
                'schemas': ['public_data', 'project_data', 'ai_data', 'audit_data'],
                'inherit': True,
            },
            
            # Standard roles
            'db_employee': {
                'description': 'Standard employee access',
                'privileges': ['CONNECT'],
                'schemas': ['public_data'],
                'inherit': True,
            },
            
            # Service roles
            'db_audit_reader': {
                'description': 'Read-only audit access',
                'privileges': ['CONNECT'],
                'schemas': ['audit_data'],
                'inherit': True,
            },
            
            'db_backup_service': {
                'description': 'Backup service account',
                'privileges': ['CONNECT', 'REPLICATION'],
                'schemas': ['ALL'],
                'inherit': False,
            },
        }

        with connection.cursor() as cursor:
            for role_name, role_config in db_roles.items():
                try:
                    # Create role
                    privileges = ' '.join(role_config['privileges'])
                    inherit_clause = 'INHERIT' if role_config['inherit'] else 'NOINHERIT'
                    
                    cursor.execute(f'''
                        CREATE ROLE {role_name} 
                        WITH {privileges} {inherit_clause} LOGIN
                        PASSWORD '{self.generate_secure_password()}'
                    ''')
                    
                    # Add comment
                    cursor.execute(
                        f"COMMENT ON ROLE {role_name} IS %s",
                        [role_config['description']]
                    )
                    
                    self.stdout.write(f'  ✓ Created role: {role_name}')
                    
                except Exception as e:
                    if 'already exists' in str(e):
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ Role {role_name} already exists')
                        )
                    else:
                        raise e

    def setup_schema_permissions(self):
        """Set up role-based permissions on schemas"""
        self.stdout.write('Setting up schema permissions...')
        
        # Schema permission mappings
        schema_permissions = {
            'public_data': {
                'db_superadmin': ['ALL'],
                'db_executive': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_hr_manager': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_finance_manager': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_project_manager': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_ai_specialist': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_employee': ['SELECT', 'INSERT', 'UPDATE'],
                'db_audit_reader': ['SELECT'],
            },
            
            'hr_data': {
                'db_superadmin': ['ALL'],
                'db_executive': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_hr_manager': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_audit_reader': ['SELECT'],
            },
            
            'finance_data': {
                'db_superadmin': ['ALL'],
                'db_executive': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_finance_manager': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_audit_reader': ['SELECT'],
            },
            
            'executive_data': {
                'db_superadmin': ['ALL'],
                'db_executive': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
            },
            
            'project_data': {
                'db_superadmin': ['ALL'],
                'db_executive': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_hr_manager': ['SELECT'],
                'db_finance_manager': ['SELECT'],
                'db_project_manager': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_ai_specialist': ['SELECT'],
                'db_employee': ['SELECT'],
            },
            
            'ai_data': {
                'db_superadmin': ['ALL'],
                'db_executive': ['SELECT'],
                'db_ai_specialist': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
            },
            
            'audit_data': {
                'db_superadmin': ['ALL'],
                'db_executive': ['SELECT'],
                'db_audit_reader': ['SELECT'],
                'db_ai_specialist': ['SELECT'],
            },
            
            'temp_data': {
                'db_superadmin': ['ALL'],
                'db_executive': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_hr_manager': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_finance_manager': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_project_manager': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_ai_specialist': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                'db_employee': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
            },
        }

        with connection.cursor() as cursor:
            for schema_name, roles_perms in schema_permissions.items():
                self.stdout.write(f'  Setting permissions for schema: {schema_name}')
                
                for role_name, permissions in roles_perms.items():
                    try:
                        # Grant schema usage
                        cursor.execute(f'GRANT USAGE ON SCHEMA {schema_name} TO {role_name}')
                        
                        # Grant specific permissions
                        if 'ALL' in permissions:
                            cursor.execute(f'GRANT ALL PRIVILEGES ON SCHEMA {schema_name} TO {role_name}')
                            cursor.execute(f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {schema_name} TO {role_name}')
                            cursor.execute(f'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {schema_name} TO {role_name}')
                            cursor.execute(f'ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON TABLES TO {role_name}')
                        else:
                            perm_str = ', '.join(permissions)
                            cursor.execute(f'GRANT {perm_str} ON ALL TABLES IN SCHEMA {schema_name} TO {role_name}')
                            
                            # Grant sequence permissions for INSERT operations
                            if 'INSERT' in permissions:
                                cursor.execute(f'GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA {schema_name} TO {role_name}')
                                cursor.execute(f'ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT USAGE, SELECT ON SEQUENCES TO {role_name}')
                            
                            # Set default privileges for future objects
                            cursor.execute(f'ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT {perm_str} ON TABLES TO {role_name}')
                        
                        self.stdout.write(f'    ✓ {role_name}: {", ".join(permissions)}')
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'    ⚠ Error setting permissions for {role_name}: {str(e)}')
                        )

    def migrate_existing_data(self):
        """Migrate existing data to appropriate schemas"""
        self.stdout.write('Migrating existing data to schemas...')
        
        # Table schema mappings (where to move existing tables)
        table_migrations = {
            # HR app tables
            'hr_data': [
                'hr_management_employee',
                'hr_management_department', 
                'hr_management_position',
                'hr_management_payroll',
                'hr_management_performance',
                'hr_management_leave',
            ],
            
            # Finance app tables
            'finance_data': [
                'finance_budget',
                'finance_expense',
                'finance_invoice',
                'finance_payment',
                'finance_account',
                'finance_transaction',
            ],
            
            # Executive tables
            'executive_data': [
                'executive_strategy',
                'executive_board_minutes',
                'executive_confidential',
            ],
            
            # Project tables
            'project_data': [
                'projects_project',
                'projects_task', 
                'projects_milestone',
                'projects_resource',
                'projects_team',
            ],
            
            # AI/Analytics tables
            'ai_data': [
                'ai_model',
                'ai_prediction',
                'ai_training_data',
                'analytics_report',
                'analytics_metric',
            ],
            
            # Audit tables
            'audit_data': [
                'audit_log',
                'access_log',
                'security_event',
                'permission_change',
            ],
        }

        with connection.cursor() as cursor:
            for target_schema, table_list in table_migrations.items():
                self.stdout.write(f'  Migrating tables to {target_schema}:')
                
                for table_name in table_list:
                    try:
                        # Check if table exists in public schema
                        cursor.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = %s
                            )
                        """, [table_name])
                        
                        exists = cursor.fetchone()[0]
                        
                        if exists:
                            # Move table to target schema
                            cursor.execute(f'ALTER TABLE public.{table_name} SET SCHEMA {target_schema}')
                            self.stdout.write(f'    ✓ Moved {table_name}')
                        else:
                            self.stdout.write(f'    ⚠ Table {table_name} not found (may not exist yet)')
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'    ⚠ Error migrating {table_name}: {str(e)}')
                        )

    def generate_secure_password(self, length=32):
        """Generate a secure random password"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def create_row_level_security_policies(self):
        """Create row-level security policies for fine-grained access control"""
        self.stdout.write('Creating row-level security policies...')
        
        # RLS policies for different tables
        rls_policies = {
            'hr_data.hr_management_employee': [
                {
                    'name': 'hr_employee_access',
                    'command': 'ALL',
                    'role': 'db_hr_manager',
                    'expression': 'true'  # HR managers see all employees
                },
                {
                    'name': 'employee_self_access',
                    'command': 'SELECT', 
                    'role': 'db_employee',
                    'expression': 'user_id = current_setting(\'app.current_user_id\')::integer'
                },
            ],
            
            'finance_data.finance_transaction': [
                {
                    'name': 'finance_manager_access',
                    'command': 'ALL',
                    'role': 'db_finance_manager', 
                    'expression': 'true'
                },
                {
                    'name': 'executive_read_access',
                    'command': 'SELECT',
                    'role': 'db_executive',
                    'expression': 'amount >= 10000 OR department_id IN (SELECT id FROM executive_departments)'
                },
            ],
        }

        with connection.cursor() as cursor:
            for table_name, policies in rls_policies.items():
                try:
                    # Enable RLS on table
                    cursor.execute(f'ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY')
                    
                    for policy in policies:
                        # Create policy
                        cursor.execute(f'''
                            CREATE POLICY {policy['name']} ON {table_name}
                            FOR {policy['command']} TO {policy['role']}
                            USING ({policy['expression']})
                        ''')
                        
                        self.stdout.write(f'    ✓ Created RLS policy {policy["name"]} on {table_name}')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'    ⚠ Error creating RLS policy: {str(e)}')
                    )