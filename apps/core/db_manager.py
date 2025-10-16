"""
Schema-Aware Database Manager
============================

Advanced database manager that provides:
- Schema-aware ORM operations
- AI-powered query optimization
- Security-enhanced database access
- Cross-schema relationship management
"""

from django.db import models, connection
from django.core.exceptions import PermissionDenied
from django.conf import settings
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class SchemaAwareQuerySet(models.QuerySet):
    """
    QuerySet that enforces schema-based security
    """
    
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self.schema_context = None
        self.user_context = None
        self.ai_optimization = True

    def with_schema_context(self, schema: str, user: Any = None):
        """
        Set schema context for this queryset
        """
        clone = self._clone()
        clone.schema_context = schema
        clone.user_context = user
        return clone

    def secure_filter(self, user, **kwargs):
        """
        Apply security filters based on user permissions and schema
        """
        clone = self._clone()
        clone.user_context = user
        
        # Apply row-level security based on user roles
        security_filters = self._get_security_filters(user)
        if security_filters:
            clone = clone.filter(**security_filters)
        
        # Apply additional filters
        if kwargs:
            clone = clone.filter(**kwargs)
        
        return clone

    def ai_optimized(self, enable: bool = True):
        """
        Enable or disable AI query optimization
        """
        clone = self._clone()
        clone.ai_optimization = enable
        return clone

    def _get_security_filters(self, user) -> Dict[str, Any]:
        """
        Get security filters based on user permissions
        """
        if not user or not user.is_authenticated:
            return {}
        
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        
        # Define model-specific security filters
        security_rules = {
            'hr_management': {
                'employee': self._get_hr_employee_filters(user),
                'payroll': self._get_hr_payroll_filters(user),
                'performance': self._get_hr_performance_filters(user),
            },
            'finance': {
                'transaction': self._get_finance_transaction_filters(user),
                'budget': self._get_finance_budget_filters(user),
                'invoice': self._get_finance_invoice_filters(user),
            },
            'projects': {
                'project': self._get_project_filters(user),
                'task': self._get_task_filters(user),
            }
        }
        
        app_rules = security_rules.get(app_label, {})
        return app_rules.get(model_name, {})

    def _get_hr_employee_filters(self, user) -> Dict[str, Any]:
        """Security filters for employee data"""
        user_roles = self._get_user_roles(user)
        
        if 'SuperAdmin' in user_roles or 'HR_Manager' in user_roles:
            return {}  # Full access
        elif 'HR_Specialist' in user_roles:
            # HR specialists can see employees in their department
            return {'department__hr_specialists': user}
        elif 'Team_Lead' in user_roles or 'Project_Manager' in user_roles:
            # Team leads can see their team members
            return {'projects__team_leads': user}
        else:
            # Regular employees can only see themselves
            return {'user': user}

    def _get_hr_payroll_filters(self, user) -> Dict[str, Any]:
        """Security filters for payroll data"""
        user_roles = self._get_user_roles(user)
        
        if 'SuperAdmin' in user_roles or 'HR_Manager' in user_roles:
            return {}  # Full access
        elif 'Finance_Manager' in user_roles:
            # Finance managers can see payroll summaries
            return {'is_summary': True}
        else:
            # Employees can only see their own payroll
            return {'employee__user': user}

    def _get_finance_transaction_filters(self, user) -> Dict[str, Any]:
        """Security filters for financial transactions"""
        user_roles = self._get_user_roles(user)
        
        if 'SuperAdmin' in user_roles or 'Finance_Manager' in user_roles:
            return {}  # Full access
        elif 'Executive' in user_roles:
            # Executives can see high-value transactions
            return {'amount__gte': 10000}
        elif 'Project_Manager' in user_roles:
            # Project managers can see project-related transactions
            return {'project__managers': user}
        else:
            # No access to financial transactions for regular users
            return {'id__in': []}  # Empty result set

    def _get_project_filters(self, user) -> Dict[str, Any]:
        """Security filters for project data"""
        user_roles = self._get_user_roles(user)
        
        if 'SuperAdmin' in user_roles or 'Executive' in user_roles:
            return {}  # Full access
        elif 'Project_Manager' in user_roles:
            # Project managers can see their projects
            return models.Q(managers=user) | models.Q(team_members=user)
        elif 'Team_Lead' in user_roles:
            # Team leads can see projects they're involved in
            return {'team_members': user}
        else:
            # Employees can see public projects and projects they're assigned to
            return models.Q(is_public=True) | models.Q(team_members=user)

    def _get_user_roles(self, user) -> List[str]:
        """Get user roles for permission checking"""
        try:
            if hasattr(user, 'roles'):
                return [role.name for role in user.roles.filter(is_active=True)]
            elif user.is_superuser:
                return ['SuperAdmin']
            elif user.is_staff:
                return ['Executive']
            else:
                return ['Employee']
        except Exception:
            return ['Employee']

    def _clone(self):
        """Override clone to preserve schema context"""
        clone = super()._clone()
        clone.schema_context = self.schema_context
        clone.user_context = self.user_context
        clone.ai_optimization = self.ai_optimization
        return clone


class SchemaAwareManager(models.Manager):
    """
    Manager that provides schema-aware database operations
    """
    
    def get_queryset(self):
        return SchemaAwareQuerySet(self.model, using=self._db)

    def in_schema(self, schema: str):
        """
        Get queryset limited to specific schema
        """
        return self.get_queryset().with_schema_context(schema)

    def for_user(self, user, **filters):
        """
        Get queryset filtered for user permissions
        """
        return self.get_queryset().secure_filter(user, **filters)

    def create_in_schema(self, schema: str, user: Any = None, **kwargs):
        """
        Create object in specific schema with proper permissions
        """
        # Check user permissions for schema
        if not self._check_create_permission(schema, user):
            raise PermissionDenied(f"No permission to create in schema: {schema}")
        
        # Set schema context in database
        with self._schema_context(schema):
            return self.create(**kwargs)

    def bulk_create_secure(self, objs: List[models.Model], user: Any = None, 
                          batch_size: Optional[int] = None):
        """
        Secure bulk create with permission checking
        """
        # Group objects by their target schema
        schema_groups = {}
        
        for obj in objs:
            schema = self._get_object_schema(obj)
            if not self._check_create_permission(schema, user):
                raise PermissionDenied(f"No permission to create in schema: {schema}")
            
            if schema not in schema_groups:
                schema_groups[schema] = []
            schema_groups[schema].append(obj)
        
        # Create objects in each schema
        results = []
        for schema, schema_objs in schema_groups.items():
            with self._schema_context(schema):
                batch_results = self.bulk_create(schema_objs, batch_size=batch_size)
                results.extend(batch_results)
        
        return results

    def ai_recommended_queries(self, user: Any, limit: int = 10):
        """
        Get AI-recommended queries for the user based on access patterns
        """
        try:
            # Analyze user's recent query patterns
            patterns = self._analyze_user_patterns(user)
            
            # Generate recommendations based on patterns
            recommendations = []
            
            # Most accessed models
            for pattern in patterns['frequent_models'][:3]:
                qs = self.for_user(user).filter(**pattern['common_filters'])
                recommendations.append({
                    'type': 'frequent_access',
                    'description': f"Recent {pattern['model']} data",
                    'queryset': qs[:5],
                })
            
            # Related data suggestions
            for pattern in patterns['related_suggestions'][:2]:
                qs = self.for_user(user).filter(**pattern['filters'])
                recommendations.append({
                    'type': 'related_data',
                    'description': pattern['description'],
                    'queryset': qs[:3],
                })
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.warning(f"AI recommendation error: {str(e)}")
            return []

    def cross_schema_search(self, query: str, user: Any, schemas: Optional[List[str]] = None):
        """
        Search across multiple schemas that user has access to
        """
        if not schemas:
            schemas = self._get_user_accessible_schemas(user)
        
        results = {}
        
        for schema in schemas:
            try:
                with self._schema_context(schema):
                    # Perform text search in schema
                    schema_results = self._search_in_schema(query, schema, user)
                    if schema_results:
                        results[schema] = schema_results
            except PermissionDenied:
                continue  # Skip schemas user can't access
            except Exception as e:
                logger.warning(f"Search error in schema {schema}: {str(e)}")
                continue
        
        return results

    def _check_create_permission(self, schema: str, user: Any) -> bool:
        """Check if user can create objects in schema"""
        if not user or not user.is_authenticated:
            return schema == 'public_data'
        
        if user.is_superuser:
            return True
        
        user_roles = self._get_user_roles(user)
        
        # Schema-specific create permissions
        create_permissions = {
            'public_data': ['Employee', 'Team_Lead', 'Project_Manager', 'HR_Specialist', 
                           'Finance_Analyst', 'AI_Specialist', 'Executive', 'SuperAdmin'],
            'project_data': ['Team_Lead', 'Project_Manager', 'Executive', 'SuperAdmin'],
            'hr_data': ['HR_Specialist', 'HR_Manager', 'Executive', 'SuperAdmin'],
            'finance_data': ['Finance_Analyst', 'Finance_Manager', 'Executive', 'SuperAdmin'],
            'executive_data': ['Executive', 'SuperAdmin'],
            'ai_data': ['AI_Specialist', 'Data_Scientist', 'Executive', 'SuperAdmin'],
            'audit_data': ['SuperAdmin'],  # Very restricted
        }
        
        allowed_roles = create_permissions.get(schema, [])
        return any(role in allowed_roles for role in user_roles)

    def _get_object_schema(self, obj: models.Model) -> str:
        """Get target schema for an object"""
        app_label = obj._meta.app_label
        
        # Import schema mapping from router
        from .db_router import RBACSchemaRouter
        router = RBACSchemaRouter()
        return router.SCHEMA_MAPPING.get(app_label, 'public_data')

    def _schema_context(self, schema: str):
        """Context manager for schema-specific operations"""
        return SchemaContext(schema)

    def _get_user_roles(self, user) -> List[str]:
        """Get user roles"""
        try:
            if hasattr(user, 'roles'):
                return [role.name for role in user.roles.filter(is_active=True)]
            elif user.is_superuser:
                return ['SuperAdmin']
            elif user.is_staff:
                return ['Executive']
            else:
                return ['Employee']
        except Exception:
            return ['Employee']

    def _get_user_accessible_schemas(self, user) -> List[str]:
        """Get schemas user has access to"""
        from .db_router import RBACSchemaRouter
        router = RBACSchemaRouter()
        
        user_roles = self._get_user_roles(user)
        accessible_schemas = set()
        
        for role in user_roles:
            role_schemas = router.ROLE_SCHEMA_ACCESS.get(role, [])
            accessible_schemas.update(role_schemas)
        
        return list(accessible_schemas)

    def _analyze_user_patterns(self, user) -> Dict[str, Any]:
        """Analyze user access patterns for AI recommendations"""
        # This would integrate with the AI analytics system
        # For now, return mock patterns
        return {
            'frequent_models': [
                {
                    'model': 'Project',
                    'common_filters': {'is_active': True},
                    'access_count': 15,
                },
            ],
            'related_suggestions': [
                {
                    'description': 'Projects with recent activity',
                    'filters': {'updated_at__gte': '2024-01-01'},
                },
            ],
        }

    def _search_in_schema(self, query: str, schema: str, user: Any):
        """Search within a specific schema"""
        # Implement full-text search within schema
        # This is a simplified version
        queryset = self.for_user(user)
        
        # Apply text search filters based on model fields
        text_fields = self._get_searchable_fields()
        if text_fields:
            from django.db.models import Q
            search_q = Q()
            for field in text_fields:
                search_q |= Q(**{f"{field}__icontains": query})
            queryset = queryset.filter(search_q)
        
        return queryset[:10]  # Limit results

    def _get_searchable_fields(self) -> List[str]:
        """Get searchable text fields for the model"""
        text_fields = []
        for field in self.model._meta.get_fields():
            if isinstance(field, (models.CharField, models.TextField)):
                text_fields.append(field.name)
        return text_fields


class SchemaContext:
    """
    Context manager for schema-specific database operations
    """
    
    def __init__(self, schema: str):
        self.schema = schema
        self.original_schema_path = None

    def __enter__(self):
        # Set PostgreSQL search_path to prioritize the target schema
        with connection.cursor() as cursor:
            # Get current search_path
            cursor.execute("SHOW search_path")
            self.original_schema_path = cursor.fetchone()[0]
            
            # Set new search_path with target schema first
            new_path = f"{self.schema}, public"
            cursor.execute("SET search_path TO %s", [new_path])
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original search_path
        if self.original_schema_path:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO %s", [self.original_schema_path])


class AIQueryOptimizer:
    """
    AI-powered query optimization for schema-aware operations
    """
    
    @staticmethod
    def optimize_queryset(queryset: SchemaAwareQuerySet) -> SchemaAwareQuerySet:
        """
        Apply AI-based query optimizations
        """
        if not queryset.ai_optimization:
            return queryset
        
        # Analyze query patterns and suggest optimizations
        optimizations = AIQueryOptimizer._analyze_query(queryset)
        
        # Apply suggested optimizations
        optimized_qs = queryset
        
        for optimization in optimizations:
            if optimization['type'] == 'select_related':
                optimized_qs = optimized_qs.select_related(*optimization['fields'])
            elif optimization['type'] == 'prefetch_related':
                optimized_qs = optimized_qs.prefetch_related(*optimization['fields'])
            elif optimization['type'] == 'index_hint':
                # Add database hints for index usage
                optimized_qs = optimized_qs.extra(
                    select={'_optimization_hint': optimization['hint']}
                )
        
        return optimized_qs

    @staticmethod
    def _analyze_query(queryset) -> List[Dict[str, Any]]:
        """
        Analyze query for optimization opportunities
        """
        optimizations = []
        
        # Analyze model relationships
        model = queryset.model
        
        # Suggest select_related for ForeignKey fields
        fk_fields = [
            field.name for field in model._meta.get_fields()
            if isinstance(field, models.ForeignKey)
        ]
        
        if fk_fields:
            optimizations.append({
                'type': 'select_related',
                'fields': fk_fields[:3],  # Limit to avoid over-joining
                'confidence': 0.8,
            })
        
        # Suggest prefetch_related for reverse ForeignKey and ManyToMany
        related_fields = [
            field.name for field in model._meta.get_fields()
            if isinstance(field, (models.ManyToManyField, models.ForeignKey)) 
            and field.related_model
        ]
        
        if related_fields:
            optimizations.append({
                'type': 'prefetch_related',
                'fields': related_fields[:2],
                'confidence': 0.7,
            })
        
        return optimizations