"""
Enhanced Django management command to setup comprehensive RBAC system
with Enterprise, Functional, and AI-Powered roles for REJLERS
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.authentication.models import User, Role, AuditLog


class Command(BaseCommand):
    help = 'Setup comprehensive RBAC system with Enterprise, Functional, and AI-Powered roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing roles and recreate them',
        )
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Create Super Admin user',
        )

    def handle(self, *args, **options):
        """Main command handler"""
        try:
            with transaction.atomic():
                if options['reset']:
                    self.stdout.write('🗑️  Deleting existing roles...')
                    Role.objects.all().delete()
                
                self.create_enterprise_roles()
                self.create_functional_roles()
                self.create_ai_powered_roles()
                
                if options['create_admin']:
                    self.create_super_admin()
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Successfully setup comprehensive RBAC system!')
                )
                self.print_role_summary()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up RBAC system: {str(e)}')
            )

    def create_enterprise_roles(self):
        """Create Enterprise-level roles with strategic permissions"""
        self.stdout.write('🏢 Creating Enterprise Roles...')
        
        enterprise_roles = [
            {
                'name': 'Super Admin',
                'description': 'Ultimate system authority with complete access to all systems, modules, and administrative functions',
                'permissions': {module: ['manage_all'] for module in Role.MODULE_PERMISSIONS.keys()}
            },
            {
                'name': 'Chief Digital Officer (CDO)',
                'description': 'Strategic digital transformation leadership with oversight of all digital initiatives and AI systems',
                'permissions': {
                    'hr_management': ['view', 'create', 'edit', 'manage_all'],
                    'projects_engineering': ['view', 'create', 'edit', 'manage_all'],
                    'contracts_legal': ['view', 'create', 'edit', 'delete'],
                    'finance_estimation': ['view', 'create', 'edit', 'delete'],
                    'reporting_dashboards': ['view', 'create', 'edit', 'manage_all'],
                    'hse_compliance': ['view', 'create', 'edit', 'delete'],
                    'supply_chain': ['view', 'create', 'edit', 'delete'],
                    'sales_engagement': ['view', 'create', 'edit', 'delete'],
                    'rto_apc_consulting': ['view', 'create', 'edit', 'delete'],
                    'user_management': ['view', 'create', 'edit', 'delete'],
                    'system_settings': ['view', 'edit', 'manage_all'],
                    'ai_services': ['view', 'use', 'configure', 'manage_all']
                }
            },
            {
                'name': 'CTO/IT Director',
                'description': 'Technology leadership with full system architecture and engineering oversight',
                'permissions': {
                    'hr_management': ['view', 'edit'],
                    'projects_engineering': ['view', 'create', 'edit', 'manage_all'],
                    'contracts_legal': ['view', 'create', 'edit'],
                    'finance_estimation': ['view', 'create', 'edit'],
                    'reporting_dashboards': ['view', 'create', 'edit', 'manage_all'],
                    'hse_compliance': ['view', 'create', 'edit'],
                    'supply_chain': ['view', 'create', 'edit'],
                    'sales_engagement': ['view', 'create', 'edit'],
                    'rto_apc_consulting': ['view', 'create', 'edit', 'delete'],
                    'user_management': ['view', 'create', 'edit'],
                    'system_settings': ['view', 'edit', 'manage_all'],
                    'ai_services': ['view', 'use', 'configure', 'manage_all']
                }
            },
            {
                'name': 'CFO/Finance Head',
                'description': 'Financial oversight with comprehensive access to financial systems and budgeting',
                'permissions': {
                    'hr_management': ['view', 'edit'],
                    'projects_engineering': ['view', 'edit'],
                    'contracts_legal': ['view', 'create', 'edit', 'delete'],
                    'finance_estimation': ['view', 'create', 'edit', 'manage_all'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view'],
                    'supply_chain': ['view', 'create', 'edit'],
                    'sales_engagement': ['view', 'create', 'edit'],
                    'rto_apc_consulting': ['view', 'edit'],
                    'user_management': ['view'],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use']
                }
            },
            {
                'name': 'HR Director',
                'description': 'Human resources leadership with complete workforce management authority',
                'permissions': {
                    'hr_management': ['view', 'create', 'edit', 'manage_all'],
                    'projects_engineering': ['view', 'edit'],
                    'contracts_legal': ['view', 'create', 'edit'],
                    'finance_estimation': ['view', 'edit'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view', 'create', 'edit'],
                    'supply_chain': ['view'],
                    'sales_engagement': ['view'],
                    'rto_apc_consulting': ['view', 'create', 'edit', 'delete'],
                    'user_management': ['view', 'create', 'edit', 'delete'],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use']
                }
            },
            {
                'name': 'Sales Director',
                'description': 'Sales and business development leadership with client relationship oversight',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'create', 'edit'],
                    'contracts_legal': ['view', 'create', 'edit', 'delete'],
                    'finance_estimation': ['view', 'create', 'edit'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view'],
                    'supply_chain': ['view', 'edit'],
                    'sales_engagement': ['view', 'create', 'edit', 'manage_all'],
                    'rto_apc_consulting': ['view', 'create', 'edit'],
                    'user_management': ['view'],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use', 'configure']
                }
            }
        ]
        
        for role_data in enterprise_roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'permissions': role_data['permissions']
                }
            )
            if created:
                self.stdout.write(f'  ✅ Created: {role.name}')
            else:
                role.description = role_data['description']
                role.permissions = role_data['permissions']
                role.save()
                self.stdout.write(f'  🔄 Updated: {role.name}')

    def create_functional_roles(self):
        """Create Functional department roles with specialized permissions"""
        self.stdout.write('🛠️  Creating Functional Roles...')
        
        functional_roles = [
            # Engineering Division
            {
                'name': 'Engineering Lead',
                'description': 'Senior engineering leadership with team management and project oversight',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'create', 'edit', 'delete'],
                    'contracts_legal': ['view', 'create'],
                    'finance_estimation': ['view', 'create', 'edit'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view', 'create', 'edit'],
                    'supply_chain': ['view', 'create'],
                    'sales_engagement': ['view', 'create'],
                    'rto_apc_consulting': ['view', 'create', 'edit'],
                    'user_management': ['view'],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use', 'configure']
                }
            },
            {
                'name': 'Engineer',
                'description': 'Professional engineer with project execution and technical implementation rights',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'create', 'edit'],
                    'contracts_legal': ['view'],
                    'finance_estimation': ['view', 'create'],
                    'reporting_dashboards': ['view', 'create'],
                    'hse_compliance': ['view', 'create', 'edit'],
                    'supply_chain': ['view'],
                    'sales_engagement': ['view'],
                    'rto_apc_consulting': ['view', 'create'],
                    'user_management': [],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use']
                }
            },
            {
                'name': 'QA/QC Engineer',
                'description': 'Quality assurance specialist with inspection and compliance authority',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'edit'],
                    'contracts_legal': ['view'],
                    'finance_estimation': ['view'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view', 'create', 'edit', 'delete'],
                    'supply_chain': ['view', 'edit'],
                    'sales_engagement': ['view'],
                    'rto_apc_consulting': ['view', 'create', 'edit'],
                    'user_management': [],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use']
                }
            },
            
            # Project Management
            {
                'name': 'Project Manager',
                'description': 'Project coordination with cross-functional team leadership',
                'permissions': {
                    'hr_management': ['view', 'edit'],
                    'projects_engineering': ['view', 'create', 'edit', 'delete'],
                    'contracts_legal': ['view', 'create', 'edit'],
                    'finance_estimation': ['view', 'create', 'edit'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view', 'create'],
                    'supply_chain': ['view', 'create', 'edit'],
                    'sales_engagement': ['view', 'create'],
                    'rto_apc_consulting': ['view', 'create', 'edit'],
                    'user_management': ['view'],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use']
                }
            },
            
            # AI/ML Division
            {
                'name': 'AI/ML Lead',
                'description': 'Artificial Intelligence and Machine Learning division leadership',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'create', 'edit'],
                    'contracts_legal': ['view', 'create'],
                    'finance_estimation': ['view', 'create'],
                    'reporting_dashboards': ['view', 'create', 'edit', 'delete'],
                    'hse_compliance': ['view', 'create'],
                    'supply_chain': ['view', 'create'],
                    'sales_engagement': ['view', 'create'],
                    'rto_apc_consulting': ['view', 'create', 'edit'],
                    'user_management': ['view'],
                    'system_settings': ['view', 'edit'],
                    'ai_services': ['view', 'use', 'configure', 'manage_all']
                }
            },
            
            # Operations
            {
                'name': 'Operations Manager',
                'description': 'Operational excellence with process optimization and efficiency oversight',
                'permissions': {
                    'hr_management': ['view', 'edit'],
                    'projects_engineering': ['view', 'create', 'edit'],
                    'contracts_legal': ['view', 'edit'],
                    'finance_estimation': ['view', 'create', 'edit'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view', 'create', 'edit'],
                    'supply_chain': ['view', 'create', 'edit', 'delete'],
                    'sales_engagement': ['view', 'create'],
                    'rto_apc_consulting': ['view', 'create'],
                    'user_management': ['view'],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use']
                }
            },
            
            # Procurement & Supply Chain
            {
                'name': 'Procurement Manager',
                'description': 'Supply chain and procurement leadership with vendor management',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'edit'],
                    'contracts_legal': ['view', 'create', 'edit'],
                    'finance_estimation': ['view', 'create', 'edit'],
                    'reporting_dashboards': ['view', 'create'],
                    'hse_compliance': ['view'],
                    'supply_chain': ['view', 'create', 'edit', 'manage_all'],
                    'sales_engagement': ['view'],
                    'rto_apc_consulting': ['view'],
                    'user_management': [],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use']
                }
            },
            
            # External/Client Roles
            {
                'name': 'Client/External',
                'description': 'External stakeholder with limited project visibility and reporting access',
                'permissions': {
                    'hr_management': [],
                    'projects_engineering': ['view'],
                    'contracts_legal': ['view'],
                    'finance_estimation': ['view'],
                    'reporting_dashboards': ['view'],
                    'hse_compliance': ['view'],
                    'supply_chain': [],
                    'sales_engagement': ['view'],
                    'rto_apc_consulting': ['view'],
                    'user_management': [],
                    'system_settings': [],
                    'ai_services': ['view']
                }
            }
        ]
        
        for role_data in functional_roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'permissions': role_data['permissions']
                }
            )
            if created:
                self.stdout.write(f'  ✅ Created: {role.name}')
            else:
                role.description = role_data['description']
                role.permissions = role_data['permissions']
                role.save()
                self.stdout.write(f'  🔄 Updated: {role.name}')

    def create_ai_powered_roles(self):
        """Create AI-Powered system roles for automation and intelligence"""
        self.stdout.write('🤖 Creating AI-Powered Roles...')
        
        ai_roles = [
            {
                'name': 'AI Assistant (System Role)',
                'description': 'Intelligent system assistant with automated task execution and user support capabilities',
                'permissions': {
                    'hr_management': ['view', 'create'],
                    'projects_engineering': ['view', 'create', 'edit'],
                    'contracts_legal': ['view', 'create'],
                    'finance_estimation': ['view', 'create'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view', 'create'],
                    'supply_chain': ['view', 'create'],
                    'sales_engagement': ['view', 'create'],
                    'rto_apc_consulting': ['view', 'create'],
                    'user_management': ['view'],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use', 'configure']
                }
            },
            {
                'name': 'Digital Twin Bot',
                'description': 'Advanced simulation and modeling system with predictive analytics capabilities',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'create', 'edit'],
                    'contracts_legal': ['view'],
                    'finance_estimation': ['view', 'create', 'edit'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view', 'create', 'edit'],
                    'supply_chain': ['view', 'create', 'edit'],
                    'sales_engagement': ['view', 'create'],
                    'rto_apc_consulting': ['view', 'create'],
                    'user_management': [],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use', 'configure']
                }
            },
            {
                'name': 'Compliance Bot',
                'description': 'Automated compliance monitoring and regulatory adherence system',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view', 'edit'],
                    'contracts_legal': ['view', 'edit'],
                    'finance_estimation': ['view'],
                    'reporting_dashboards': ['view', 'create', 'edit'],
                    'hse_compliance': ['view', 'create', 'edit', 'delete'],
                    'supply_chain': ['view', 'edit'],
                    'sales_engagement': ['view'],
                    'rto_apc_consulting': ['view', 'create', 'edit'],
                    'user_management': [],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use', 'configure']
                }
            },
            {
                'name': 'Insight Generator',
                'description': 'Advanced analytics and business intelligence system with predictive modeling',
                'permissions': {
                    'hr_management': ['view'],
                    'projects_engineering': ['view'],
                    'contracts_legal': ['view'],
                    'finance_estimation': ['view'],
                    'reporting_dashboards': ['view', 'create', 'edit', 'manage_all'],
                    'hse_compliance': ['view'],
                    'supply_chain': ['view'],
                    'sales_engagement': ['view'],
                    'rto_apc_consulting': ['view'],
                    'user_management': [],
                    'system_settings': ['view'],
                    'ai_services': ['view', 'use', 'configure']
                }
            }
        ]
        
        for role_data in ai_roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'permissions': role_data['permissions']
                }
            )
            if created:
                self.stdout.write(f'  ✅ Created: {role.name}')
            else:
                role.description = role_data['description']
                role.permissions = role_data['permissions']
                role.save()
                self.stdout.write(f'  🔄 Updated: {role.name}')

    def create_super_admin(self):
        """Create Super Admin user"""
        self.stdout.write('👑 Creating Super Admin user...')
        
        super_admin_role = Role.objects.get(name='Super Admin')
        
        # Check if Super Admin already exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('  ⚠️  Super Admin user already exists')
            return
        
        # Create Super Admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@rejlers.com',
            password='RejlersAdmin2024!',
            first_name='System',
            last_name='Administrator',
            is_staff=True,
            is_superuser=True,
            is_approved=True,
            is_verified=True,
            role=super_admin_role,
            company_name='Rejlers',
            job_title='System Administrator',
            department='IT',
            position='Super Admin'
        )
        
        self.stdout.write(f'  ✅ Created Super Admin: {admin_user.email}')
        self.stdout.write(f'  🔑 Password: RejlersAdmin2024!')

    def print_role_summary(self):
        """Print summary of created roles"""
        self.stdout.write('\n📊 RBAC System Summary:')
        self.stdout.write('=' * 50)
        
        # Enterprise Roles
        self.stdout.write('\n🏢 Enterprise Roles:')
        enterprise_roles = ['Super Admin', 'Chief Digital Officer (CDO)', 'CTO/IT Director', 
                          'CFO/Finance Head', 'HR Director', 'Sales Director']
        for role_name in enterprise_roles:
            try:
                role = Role.objects.get(name=role_name)
                self.stdout.write(f'  ✅ {role.name}')
            except Role.DoesNotExist:
                self.stdout.write(f'  ❌ {role_name} (Not found)')
        
        # Functional Roles
        self.stdout.write('\n🛠️  Functional Roles:')
        functional_roles = ['Engineering Lead', 'Engineer', 'QA/QC Engineer', 'Project Manager',
                          'AI/ML Lead', 'Operations Manager', 'Procurement Manager', 'Client/External']
        for role_name in functional_roles:
            try:
                role = Role.objects.get(name=role_name)
                self.stdout.write(f'  ✅ {role.name}')
            except Role.DoesNotExist:
                self.stdout.write(f'  ❌ {role_name} (Not found)')
        
        # AI-Powered Roles
        self.stdout.write('\n🤖 AI-Powered Roles:')
        ai_roles = ['AI Assistant (System Role)', 'Digital Twin Bot', 'Compliance Bot', 'Insight Generator']
        for role_name in ai_roles:
            try:
                role = Role.objects.get(name=role_name)
                self.stdout.write(f'  ✅ {role.name}')
            except Role.DoesNotExist:
                self.stdout.write(f'  ❌ {role_name} (Not found)')
        
        total_roles = Role.objects.count()
        self.stdout.write(f'\n📈 Total Roles Created: {total_roles}')
        self.stdout.write('=' * 50)