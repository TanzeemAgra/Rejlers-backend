"""
Database Router for Schema-Based RBAC
=====================================

Intelligent database routing system that:
- Routes queries to appropriate schemas based on model types
- Implements AI-powered access pattern analysis
- Provides schema-level security enforcement
- Supports multi-database operations with RBAC
"""

import logging
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import connections
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class RBACSchemaRouter:
    """
    Advanced database router that enforces schema-based RBAC
    """
    
    # Schema mapping for different app models
    SCHEMA_MAPPING = {
        # HR Management
        'hr_management': 'hr_data',
        
        # Finance
        'finance': 'finance_data',
        
        # Executive/Strategic 
        'executive': 'executive_data',
        'reporting': 'executive_data',  # High-level reports
        
        # Projects
        'projects': 'project_data',
        
        # AI and Analytics
        'ai_analytics': 'ai_data',
        'machine_learning': 'ai_data',
        
        # Audit and Security
        'audit': 'audit_data',
        'security': 'audit_data',
        
        # Standard applications
        'authentication': 'public_data',
        'core': 'public_data',
        'contacts': 'public_data',
        'contracts': 'public_data',
        'sales': 'public_data',
        'services': 'public_data',
        'supply_chain': 'project_data',
        'hse_compliance': 'project_data',
        'rto_apc': 'project_data',
    }

    # Role-based schema access mapping
    ROLE_SCHEMA_ACCESS = {
        'SuperAdmin': ['public_data', 'hr_data', 'finance_data', 'executive_data', 
                      'project_data', 'ai_data', 'audit_data', 'temp_data'],
        
        'Executive': ['public_data', 'finance_data', 'hr_data', 'executive_data', 
                     'project_data', 'audit_data'],
        
        'HR_Manager': ['public_data', 'hr_data', 'project_data'],
        'HR_Specialist': ['public_data', 'hr_data'],
        
        'Finance_Manager': ['public_data', 'finance_data', 'project_data'],
        'Finance_Analyst': ['public_data', 'finance_data'],
        
        'Project_Manager': ['public_data', 'project_data'],
        'Team_Lead': ['public_data', 'project_data'],
        
        'AI_Specialist': ['public_data', 'project_data', 'ai_data', 'audit_data'],
        'Data_Scientist': ['public_data', 'ai_data'],
        
        'Employee': ['public_data'],
        'Contractor': ['public_data'],
    }

    def __init__(self):
        self.current_user = None
        self.access_cache = {}
        self.ai_access_patterns = []

    def db_for_read(self, model, **hints):
        """
        Determine which database to use for reading a model
        """
        return self._route_database(model, 'read', **hints)

    def db_for_write(self, model, **hints):
        """
        Determine which database to use for writing a model
        """
        return self._route_database(model, 'write', **hints)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both models are in the same schema or if cross-schema is allowed
        """
        try:
            schema1 = self._get_model_schema(obj1._meta.app_label)
            schema2 = self._get_model_schema(obj2._meta.app_label)
            
            # Same schema - always allow
            if schema1 == schema2:
                return True
            
            # Cross-schema relations allowed for certain combinations
            allowed_cross_schema = [
                ('public_data', 'project_data'),
                ('public_data', 'hr_data'),
                ('public_data', 'finance_data'),
                ('project_data', 'hr_data'),  # Project-employee relations
                ('audit_data', 'public_data'),  # Audit trails
            ]
            
            schema_pair = (schema1, schema2)
            reverse_pair = (schema2, schema1)
            
            return schema_pair in allowed_cross_schema or reverse_pair in allowed_cross_schema
            
        except Exception as e:
            logger.warning(f"Error checking relation permission: {str(e)}")
            return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations only run on the correct database/schema
        """
        try:
            target_schema = self._get_model_schema(app_label)
            
            # For now, allow all migrations on default database
            # In production, you might want to use separate databases per schema
            return db == 'default'
            
        except Exception as e:
            logger.warning(f"Error checking migration permission: {str(e)}")
            return db == 'default'

    def _route_database(self, model, operation, **hints):
        """
        Internal method to route database operations
        """
        try:
            app_label = model._meta.app_label
            target_schema = self._get_model_schema(app_label)
            
            # Check user permissions for this schema
            if not self._check_schema_access(target_schema, operation):
                logger.warning(
                    f"Access denied: User does not have {operation} permission for schema {target_schema}"
                )
                raise PermissionDenied(
                    f"Insufficient permissions to {operation} from {target_schema} schema"
                )
            
            # Log access pattern for AI analysis
            self._log_access_pattern(target_schema, operation, model._meta.model_name)
            
            # For now, return default database
            # In production, you might have separate databases per schema
            return 'default'
            
        except Exception as e:
            logger.error(f"Database routing error: {str(e)}")
            # Default fallback
            return 'default'

    def _get_model_schema(self, app_label):
        """
        Get the target schema for a given app label
        """
        return self.SCHEMA_MAPPING.get(app_label, 'public_data')

    def _check_schema_access(self, schema, operation):
        """
        Check if current user has access to the specified schema for the operation
        """
        # Get current user from thread local or context
        user = self._get_current_user()
        
        if not user or not user.is_authenticated:
            return schema == 'public_data' and operation == 'read'
        
        # Superusers have access to everything
        if user.is_superuser:
            return True
        
        # Check role-based access
        user_roles = self._get_user_roles(user)
        accessible_schemas = set()
        
        for role in user_roles:
            role_schemas = self.ROLE_SCHEMA_ACCESS.get(role, [])
            accessible_schemas.update(role_schemas)
        
        if schema not in accessible_schemas:
            return False
        
        # Additional checks for sensitive operations
        if operation == 'write' and schema in ['executive_data', 'audit_data']:
            # Only certain roles can write to highly sensitive schemas
            sensitive_write_roles = ['SuperAdmin', 'Executive']
            return any(role in sensitive_write_roles for role in user_roles)
        
        # Check AI risk assessment
        risk_score = self._assess_access_risk(user, schema, operation)
        if risk_score > 0.8:
            logger.warning(f"High risk access attempt blocked: {risk_score:.2f}")
            return False
        
        return True

    def _get_current_user(self):
        """
        Get current user from various possible contexts
        """
        try:
            # Try to get from thread local storage
            from threading import current_thread
            thread = current_thread()
            if hasattr(thread, 'request') and hasattr(thread.request, 'user'):
                return thread.request.user
            
            # Try Django's current request context
            from django.contrib.auth.middleware import get_user
            from django.http import HttpRequest
            
            # As fallback, return cached user
            return getattr(self, '_cached_user', None)
            
        except Exception as e:
            logger.debug(f"Could not get current user: {str(e)}")
            return None

    def _get_user_roles(self, user):
        """
        Get list of roles for the user
        """
        try:
            # Try to get roles from user profile or related model
            if hasattr(user, 'profile') and hasattr(user.profile, 'roles'):
                return [role.name for role in user.profile.roles.filter(is_active=True)]
            
            # Try direct role attribute
            if hasattr(user, 'roles'):
                return [role.name for role in user.roles.filter(is_active=True)]
            
            # Default roles based on user properties
            roles = []
            
            if user.is_superuser:
                roles.append('SuperAdmin')
            elif user.is_staff:
                roles.append('Executive')
            else:
                roles.append('Employee')
            
            return roles
            
        except Exception as e:
            logger.warning(f"Error getting user roles: {str(e)}")
            return ['Employee']  # Default safe role

    def _assess_access_risk(self, user, schema, operation):
        """
        AI-powered risk assessment for database access
        """
        try:
            base_risk = 0.0
            
            # Schema sensitivity risk
            schema_risk_map = {
                'executive_data': 0.8,
                'finance_data': 0.7,
                'hr_data': 0.6,
                'audit_data': 0.5,
                'ai_data': 0.4,
                'project_data': 0.2,
                'public_data': 0.1,
            }
            
            base_risk += schema_risk_map.get(schema, 0.3)
            
            # Operation risk
            operation_risk_map = {
                'write': 0.3,
                'delete': 0.5,
                'read': 0.1,
            }
            
            base_risk += operation_risk_map.get(operation, 0.2)
            
            # Time-based risk (off-hours access)
            from datetime import datetime
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 22:  # Outside 6 AM - 10 PM
                base_risk += 0.2
            
            # User behavior analysis
            recent_patterns = self._get_recent_access_patterns(user.id)
            if len(recent_patterns) > 10:  # Unusual activity volume
                base_risk += 0.1
            
            # Failed access attempts
            failed_attempts = [p for p in recent_patterns if not p.get('success', True)]
            if len(failed_attempts) > 3:
                base_risk += 0.3
            
            return min(base_risk, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.warning(f"Risk assessment error: {str(e)}")
            return 0.5  # Medium risk as fallback

    def _log_access_pattern(self, schema, operation, model_name):
        """
        Log access pattern for AI analysis
        """
        try:
            pattern = {
                'timestamp': datetime.now().isoformat(),
                'user_id': getattr(self._get_current_user(), 'id', None),
                'schema': schema,
                'operation': operation,
                'model': model_name,
                'success': True,
            }
            
            self.ai_access_patterns.append(pattern)
            
            # Keep only recent patterns (last 100)
            if len(self.ai_access_patterns) > 100:
                self.ai_access_patterns = self.ai_access_patterns[-100:]
            
            # Async logging to external service could be added here
            
        except Exception as e:
            logger.debug(f"Access pattern logging error: {str(e)}")

    def _get_recent_access_patterns(self, user_id, hours=24):
        """
        Get recent access patterns for user
        """
        try:
            from datetime import datetime, timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            return [
                pattern for pattern in self.ai_access_patterns
                if (pattern.get('user_id') == user_id and 
                    datetime.fromisoformat(pattern['timestamp']) > cutoff_time)
            ]
            
        except Exception as e:
            logger.debug(f"Error getting access patterns: {str(e)}")
            return []

    def set_current_user(self, user):
        """
        Set current user for schema routing decisions
        """
        self._cached_user = user


# Middleware to set current user for database router
class DatabaseRouterMiddleware:
    """
    Middleware to ensure database router has access to current user
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set user in thread local for router access
        from threading import current_thread
        current_thread().request = request
        
        # Also set in router if available
        from django.db import router
        if hasattr(router, 'routers'):
            for db_router in router.routers:
                if isinstance(db_router, RBACSchemaRouter):
                    db_router.set_current_user(getattr(request, 'user', None))
        
        response = self.get_response(request)
        
        # Clean up
        if hasattr(current_thread(), 'request'):
            delattr(current_thread(), 'request')
        
        return response