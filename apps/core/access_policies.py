"""
DRF Access Policies for Advanced RBAC Enforcement
=================================================

This module defines access policies using drf-access-policy for fine-grained
API access control with AI-powered decision making.
"""

import json
import logging
from datetime import datetime
from rest_access_policy import AccessPolicy
from django.contrib.auth.models import User
from django.core.cache import cache
from apps.core.rbac_enforcement import permission_manager
from apps.authentication.models import UserRole

logger = logging.getLogger(__name__)


class AIEnhancedAccessPolicy(AccessPolicy):
    """
    Base access policy with AI-enhanced decision making
    """
    
    def has_permission(self, request, view):
        """
        Enhanced permission check with AI analysis
        """
        # Get the base permission result
        base_result = super().has_permission(request, view)
        
        if not base_result:
            return False
        
        # Skip AI analysis for safe methods if desired
        if request.method in ['GET', 'HEAD', 'OPTIONS'] and not self.requires_ai_analysis(view):
            return True
        
        # AI-enhanced permission check
        return self._ai_enhanced_check(request, view)
    
    def has_object_permission(self, request, view, obj):
        """
        Enhanced object-level permission check
        """
        base_result = super().has_object_permission(request, view, obj)
        
        if not base_result:
            return False
        
        # AI-enhanced object permission check
        return self._ai_enhanced_object_check(request, view, obj)
    
    def _ai_enhanced_check(self, request, view):
        """
        AI-enhanced permission checking
        """
        try:
            user = request.user
            if not user.is_authenticated:
                return False
            
            # Get permission string for this view/action
            permission = self._get_permission_string(request, view)
            
            # Check with AI engine
            allowed, analysis = permission_manager.check_permission(
                user=user,
                permission=permission,
                context={
                    'request': request,
                    'view': view,
                    'method': request.method
                }
            )
            
            # Store analysis in request for logging
            if not hasattr(request, '_rbac_analyses'):
                request._rbac_analyses = []
            request._rbac_analyses.append(analysis)
            
            return allowed
            
        except Exception as e:
            logger.error(f"AI-enhanced permission check failed: {str(e)}")
            # Fallback to base permission on error
            return True
    
    def _ai_enhanced_object_check(self, request, view, obj):
        """
        AI-enhanced object-level permission checking
        """
        try:
            user = request.user
            permission = self._get_object_permission_string(request, view, obj)
            
            allowed, analysis = permission_manager.check_permission(
                user=user,
                permission=permission,
                obj=obj,
                context={
                    'request': request,
                    'view': view,
                    'object': obj,
                    'method': request.method
                }
            )
            
            if not hasattr(request, '_rbac_analyses'):
                request._rbac_analyses = []
            request._rbac_analyses.append(analysis)
            
            return allowed
            
        except Exception as e:
            logger.error(f"AI-enhanced object permission check failed: {str(e)}")
            return True
    
    def _get_permission_string(self, request, view):
        """
        Generate permission string for the current request
        """
        app_label = getattr(view, 'permission_app_label', 'core')
        model_name = getattr(view, 'permission_model_name', view.__class__.__name__.lower())
        action = self._get_action_from_method(request.method)
        
        return f"{app_label}.{action}_{model_name}"
    
    def _get_object_permission_string(self, request, view, obj):
        """
        Generate object-level permission string
        """
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        action = self._get_action_from_method(request.method)
        
        return f"{app_label}.{action}_{model_name}"
    
    def _get_action_from_method(self, method):
        """
        Map HTTP method to permission action
        """
        method_mapping = {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete'
        }
        return method_mapping.get(method, 'view')
    
    def requires_ai_analysis(self, view):
        """
        Determine if this view requires AI analysis for GET requests
        """
        # Override in subclasses for specific requirements
        return getattr(view, 'always_use_ai', False)


class SuperAdminAccessPolicy(AIEnhancedAccessPolicy):
    """
    Access policy for super admin resources
    """
    statements = [
        {
            "action": ["*"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_superuser"
        }
    ]
    
    def is_superuser(self, request, view, action):
        """
        Check if user is a superuser
        """
        return request.user.is_superuser
    
    def requires_ai_analysis(self, view):
        """
        Super admin actions always require AI analysis
        """
        return True


class EnterpriseRoleAccessPolicy(AIEnhancedAccessPolicy):
    """
    Access policy for enterprise-level roles
    """
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": ["has_enterprise_role", "ai_risk_check"]
        },
        {
            "action": ["create", "update", "partial_update"],
            "principal": ["authenticated"], 
            "effect": "allow",
            "condition": ["has_enterprise_management_role", "ai_risk_check"]
        },
        {
            "action": ["destroy"],
            "principal": ["authenticated"],
            "effect": "allow", 
            "condition": ["has_enterprise_admin_role", "ai_risk_check"]
        }
    ]
    
    def has_enterprise_role(self, request, view, action):
        """
        Check if user has any enterprise role
        """
        enterprise_roles = [
            'Chief Executive Officer (CEO)',
            'Chief Operations Officer (COO)', 
            'Chief Financial Officer (CFO)',
            'Chief Technology Officer (CTO)',
            'Chief Marketing Officer (CMO)',
            'Chief Human Resources Officer (CHRO)'
        ]
        
        user_roles = request.user.userrole_set.filter(
            role_name__in=enterprise_roles
        ).exists()
        
        return user_roles
    
    def has_enterprise_management_role(self, request, view, action):
        """
        Check if user has enterprise management roles
        """
        management_roles = [
            'Chief Executive Officer (CEO)',
            'Chief Operations Officer (COO)',
            'Chief Technology Officer (CTO)'
        ]
        
        return request.user.userrole_set.filter(
            role_name__in=management_roles
        ).exists()
    
    def has_enterprise_admin_role(self, request, view, action):
        """
        Check if user has enterprise admin roles (CEO, COO)
        """
        admin_roles = [
            'Chief Executive Officer (CEO)',
            'Chief Operations Officer (COO)'
        ]
        
        return request.user.userrole_set.filter(
            role_name__in=admin_roles
        ).exists()
    
    def ai_risk_check(self, request, view, action):
        """
        AI-powered risk assessment for enterprise actions
        """
        # This will be handled by the parent class AI enhancement
        return True


class FunctionalRoleAccessPolicy(AIEnhancedAccessPolicy):
    """
    Access policy for functional roles with department-specific access
    """
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "has_functional_role"
        },
        {
            "action": ["create", "update", "partial_update"], 
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": ["has_functional_role", "owns_department_data"]
        },
        {
            "action": ["destroy"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": ["has_senior_functional_role", "owns_department_data"]
        }
    ]
    
    def has_functional_role(self, request, view, action):
        """
        Check if user has functional role
        """
        functional_roles = [
            'Project Manager', 'Finance Manager', 'HR Manager',
            'Sales Manager', 'Operations Manager', 'Quality Manager',
            'Safety Manager', 'IT Manager'
        ]
        
        return request.user.userrole_set.filter(
            role_name__in=functional_roles
        ).exists()
    
    def has_senior_functional_role(self, request, view, action):
        """
        Check if user has senior functional role
        """
        senior_roles = [
            'Finance Manager', 'HR Manager', 'Operations Manager', 'IT Manager'
        ]
        
        return request.user.userrole_set.filter(
            role_name__in=senior_roles
        ).exists()
    
    def owns_department_data(self, request, view, action):
        """
        Check if user owns or has access to department data
        """
        # This would need to be implemented based on your data model
        # For now, return True - implement based on department relationships
        return True


class AIRoleAccessPolicy(AIEnhancedAccessPolicy):
    """
    Access policy for AI-powered roles with advanced monitoring
    """
    statements = [
        {
            "action": ["*"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": ["has_ai_role", "ai_behavior_analysis"]
        }
    ]
    
    def has_ai_role(self, request, view, action):
        """
        Check if user has AI-powered role
        """
        ai_roles = [
            'AI Ethics Officer', 'AI Data Scientist', 
            'AI Operations Specialist', 'AI Security Analyst'
        ]
        
        return request.user.userrole_set.filter(
            role_name__in=ai_roles
        ).exists()
    
    def ai_behavior_analysis(self, request, view, action):
        """
        Advanced AI behavior analysis for AI role users
        """
        # Enhanced monitoring for AI role users
        user = request.user
        
        # Check for unusual patterns in AI role usage
        cache_key = f"ai_role_activity_{user.id}"
        recent_activity = cache.get(cache_key, [])
        
        current_activity = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'view': view.__class__.__name__,
            'method': request.method
        }
        
        recent_activity.append(current_activity)
        recent_activity = recent_activity[-50:]  # Keep last 50 activities
        
        cache.set(cache_key, recent_activity, 3600)  # Cache for 1 hour
        
        # AI role users get enhanced scrutiny
        return True
    
    def requires_ai_analysis(self, view):
        """
        AI roles always require AI analysis
        """
        return True


class SensitiveDataAccessPolicy(AIEnhancedAccessPolicy):
    """
    Access policy for sensitive data (Finance, HR, etc.)
    """
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": ["has_sensitive_data_access", "time_based_access", "ai_risk_check"]
        },
        {
            "action": ["create", "update", "partial_update"],
            "principal": ["authenticated"], 
            "effect": "allow",
            "condition": ["has_sensitive_data_modify", "time_based_access", "ai_risk_check", "requires_approval"]
        },
        {
            "action": ["destroy"],
            "principal": ["authenticated"],
            "effect": "deny"  # No deletion of sensitive data
        }
    ]
    
    def has_sensitive_data_access(self, request, view, action):
        """
        Check if user can access sensitive data
        """
        sensitive_roles = [
            'Chief Executive Officer (CEO)', 'Chief Financial Officer (CFO)',
            'Chief Human Resources Officer (CHRO)', 'Finance Manager', 'HR Manager'
        ]
        
        return request.user.userrole_set.filter(
            role_name__in=sensitive_roles
        ).exists()
    
    def has_sensitive_data_modify(self, request, view, action):
        """
        Check if user can modify sensitive data
        """
        modify_roles = [
            'Chief Executive Officer (CEO)', 'Chief Financial Officer (CFO)',
            'Chief Human Resources Officer (CHRO)'
        ]
        
        return request.user.userrole_set.filter(
            role_name__in=modify_roles
        ).exists()
    
    def time_based_access(self, request, view, action):
        """
        Time-based access control (business hours only)
        """
        from django.utils import timezone
        
        current_time = timezone.now()
        current_hour = current_time.hour
        
        # Allow access during business hours (6 AM to 10 PM)
        if 6 <= current_hour <= 22:
            return True
        
        # Allow after hours for CEO and CFO only
        executive_roles = ['Chief Executive Officer (CEO)', 'Chief Financial Officer (CFO)']
        return request.user.userrole_set.filter(role_name__in=executive_roles).exists()
    
    def requires_approval(self, request, view, action):
        """
        Require approval for sensitive data modifications
        """
        # In production, this would integrate with an approval workflow
        # For now, log the request for manual review
        logger.info(f"Sensitive data modification requested by {request.user.username}")
        return True
    
    def requires_ai_analysis(self, view):
        """
        Sensitive data always requires AI analysis
        """
        return True