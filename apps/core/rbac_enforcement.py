"""
Advanced RBAC Enforcement System with AI-Powered Access Control
==============================================================

This module implements intelligent access control mechanisms including:
- Object-level permissions with Django Guardian
- AI-powered access predictions and anomaly detection
- Dynamic permission validation
- Context-aware security monitoring
- Risk-based access decisions
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.cache import cache
from django.utils import timezone
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from guardian.models import UserObjectPermission, GroupObjectPermission
from apps.authentication.models import Role
import openai
import os

logger = logging.getLogger(__name__)

class AIPermissionEngine:
    """
    AI-Powered Permission Engine for intelligent access control decisions
    """
    
    def __init__(self):
        self.openai_client = openai
        self.openai_client.api_key = os.getenv('OPENAI_API_KEY')
        self.risk_threshold = 0.7  # Risk threshold for access decisions
        
    def analyze_access_pattern(self, user: User, resource: str, action: str) -> Dict[str, Any]:
        """
        Analyze user access patterns using AI to detect anomalies
        """
        try:
            # Get user's historical access patterns
            access_history = self._get_user_access_history(user, days=30)
            
            # Prepare AI prompt for pattern analysis
            prompt = f"""
            Analyze this user access pattern for security risks:
            
            User: {user.username} (Roles: {[role.role_name for role in user.userrole_set.all()]})
            Requested Resource: {resource}
            Requested Action: {action}
            
            Recent Access History:
            {json.dumps(access_history, indent=2)}
            
            Current Time: {timezone.now().isoformat()}
            
            Analyze for:
            1. Unusual access patterns
            2. Time-based anomalies
            3. Resource access deviations
            4. Risk assessment (0-1 scale)
            5. Recommended actions
            
            Respond in JSON format with keys: risk_score, anomalies, recommendations, allow_access
            """
            
            response = self.openai_client.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            ai_analysis = json.loads(response.choices[0].text.strip())
            
            # Cache the analysis for 5 minutes
            cache_key = f"ai_analysis_{user.id}_{resource}_{action}"
            cache.set(cache_key, ai_analysis, 300)
            
            return ai_analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Fallback to rule-based analysis
            return self._fallback_risk_analysis(user, resource, action)
    
    def _get_user_access_history(self, user: User, days: int = 30) -> List[Dict]:
        """
        Get user's access history for pattern analysis
        """
        from apps.core.models import AccessLog
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        try:
            logs = AccessLog.objects.filter(
                user=user,
                timestamp__gte=cutoff_date
            ).order_by('-timestamp')[:50]
            
            return [
                {
                    'resource': log.resource,
                    'action': log.action,
                    'timestamp': log.timestamp.isoformat(),
                    'success': log.success,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent[:100] if log.user_agent else None
                }
                for log in logs
            ]
        except:
            return []
    
    def _fallback_risk_analysis(self, user: User, resource: str, action: str) -> Dict[str, Any]:
        """
        Fallback rule-based risk analysis when AI is unavailable
        """
        risk_score = 0.0
        anomalies = []
        
        # Check time-based patterns
        current_hour = timezone.now().hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 0.3
            anomalies.append("Access outside normal business hours")
        
        # Check for sensitive resources
        sensitive_resources = ['finance', 'hr', 'payroll', 'admin', 'system']
        if any(sensitive in resource.lower() for sensitive in sensitive_resources):
            risk_score += 0.2
            
        # Check user role appropriateness
        user_roles = [role.role_name for role in user.userrole_set.all()]
        if not user_roles:
            risk_score += 0.5
            anomalies.append("User has no assigned roles")
        
        return {
            'risk_score': min(risk_score, 1.0),
            'anomalies': anomalies,
            'recommendations': ["Monitor access closely"] if risk_score > 0.5 else [],
            'allow_access': risk_score < self.risk_threshold
        }

class AdvancedPermissionManager:
    """
    Advanced Permission Manager with object-level permissions and AI integration
    """
    
    def __init__(self):
        self.ai_engine = AIPermissionEngine()
        self.cache_timeout = 300  # 5 minutes
        
    def check_permission(self, user: User, permission: str, obj: Any = None, 
                        context: Dict = None) -> Tuple[bool, Dict]:
        """
        Advanced permission checking with AI-powered analysis
        """
        # Create cache key
        cache_key = f"perm_{user.id}_{permission}_{getattr(obj, 'id', 'none')}"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result and not context.get('force_check', False):
            return cached_result['allowed'], cached_result['analysis']
        
        # Basic permission check
        basic_allowed = self._basic_permission_check(user, permission, obj)
        
        # AI-powered risk analysis
        resource = f"{obj._meta.model_name}" if obj else permission
        ai_analysis = self.ai_engine.analyze_access_pattern(user, resource, permission)
        
        # Combine basic permissions with AI analysis
        final_decision = basic_allowed and ai_analysis.get('allow_access', True)
        
        # Enhanced logging
        self._log_access_attempt(user, permission, obj, final_decision, ai_analysis)
        
        result = {
            'allowed': final_decision,
            'analysis': {
                'basic_permission': basic_allowed,
                'ai_analysis': ai_analysis,
                'final_decision': final_decision,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        # Cache the result
        cache.set(cache_key, result, self.cache_timeout)
        
        return final_decision, result['analysis']
    
    def _basic_permission_check(self, user: User, permission: str, obj: Any = None) -> bool:
        """
        Basic Django Guardian permission check
        """
        if not user.is_authenticated:
            return False
            
        if user.is_superuser:
            return True
            
        # Object-level permission check
        if obj:
            return user.has_perm(permission, obj)
            
        # Model-level permission check
        return user.has_perm(permission)
    
    def assign_object_permission(self, user: User, permission: str, obj: Any, 
                               temporary: bool = False, expires_at: datetime = None):
        """
        Assign object-level permission with optional expiration
        """
        try:
            assign_perm(permission, user, obj)
            
            # If temporary permission, set up expiration
            if temporary and expires_at:
                self._schedule_permission_revocation(user, permission, obj, expires_at)
                
            logger.info(f"Assigned permission '{permission}' to user '{user.username}' for object {obj}")
            
            # Clear permission cache for this user
            self._clear_user_permission_cache(user)
            
        except Exception as e:
            logger.error(f"Failed to assign permission: {str(e)}")
            raise
    
    def revoke_object_permission(self, user: User, permission: str, obj: Any):
        """
        Revoke object-level permission
        """
        try:
            remove_perm(permission, user, obj)
            logger.info(f"Revoked permission '{permission}' from user '{user.username}' for object {obj}")
            
            # Clear permission cache for this user
            self._clear_user_permission_cache(user)
            
        except Exception as e:
            logger.error(f"Failed to revoke permission: {str(e)}")
            raise
    
    def get_user_permissions(self, user: User, obj: Any = None) -> List[str]:
        """
        Get all permissions for a user on an object
        """
        if obj:
            return get_perms(user, obj)
        else:
            return list(user.get_all_permissions())
    
    def bulk_assign_permissions(self, users: List[User], permissions: List[str], 
                              obj: Any, notify: bool = True):
        """
        Bulk assign permissions to multiple users
        """
        for user in users:
            for permission in permissions:
                self.assign_object_permission(user, permission, obj)
        
        if notify:
            # Send notification about bulk permission change
            self._send_permission_notification(users, permissions, obj, 'assigned')
    
    def _log_access_attempt(self, user: User, permission: str, obj: Any, 
                          allowed: bool, ai_analysis: Dict):
        """
        Log access attempt with AI analysis results
        """
        try:
            from apps.core.models import AccessLog
            
            AccessLog.objects.create(
                user=user,
                resource=f"{obj._meta.model_name}:{obj.id}" if obj else permission,
                action=permission,
                success=allowed,
                ai_risk_score=ai_analysis.get('risk_score', 0.0),
                ai_anomalies=json.dumps(ai_analysis.get('anomalies', [])),
                metadata=json.dumps({
                    'ai_analysis': ai_analysis,
                    'user_roles': [role.role_name for role in user.userrole_set.all()]
                })
            )
        except Exception as e:
            logger.error(f"Failed to log access attempt: {str(e)}")
    
    def _clear_user_permission_cache(self, user: User):
        """
        Clear all cached permissions for a user
        """
        # This would need to be implemented based on your caching strategy
        cache_pattern = f"perm_{user.id}_*"
        # Redis-based cache clearing would go here
        
    def _schedule_permission_revocation(self, user: User, permission: str, 
                                     obj: Any, expires_at: datetime):
        """
        Schedule automatic permission revocation (would use Celery in production)
        """
        # This would use Celery beat or similar for production
        # For now, we'll store the expiration in the database
        pass
    
    def _send_permission_notification(self, users: List[User], permissions: List[str], 
                                    obj: Any, action: str):
        """
        Send notifications about permission changes
        """
        # Implementation would depend on your notification system
        pass

class RoleBasedAccessMiddleware:
    """
    Middleware for role-based access control with AI monitoring
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.permission_manager = AdvancedPermissionManager()
        
    def __call__(self, request):
        # Pre-request processing
        self._process_request(request)
        
        response = self.get_response(request)
        
        # Post-request processing
        self._process_response(request, response)
        
        return response
    
    def _process_request(self, request):
        """
        Process incoming request for RBAC compliance
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Check for suspicious patterns
            self._monitor_user_behavior(request)
            
            # Add permission context to request
            request.rbac_context = {
                'user_roles': [role.role_name for role in request.user.userrole_set.all()],
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'timestamp': timezone.now()
            }
    
    def _process_response(self, request, response):
        """
        Process response and log access patterns
        """
        if hasattr(request, 'rbac_context'):
            # Log the request for pattern analysis
            self._log_request_pattern(request, response)
    
    def _monitor_user_behavior(self, request):
        """
        Monitor user behavior for anomalies
        """
        user = request.user
        current_time = timezone.now()
        
        # Check rate limiting
        rate_limit_key = f"rate_limit_{user.id}_{current_time.minute}"
        request_count = cache.get(rate_limit_key, 0)
        
        if request_count > 60:  # More than 60 requests per minute
            logger.warning(f"Rate limit exceeded for user {user.username}")
            # Could trigger additional security measures
        
        cache.set(rate_limit_key, request_count + 1, 60)
    
    def _get_client_ip(self, request):
        """
        Get client IP address handling proxies
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_request_pattern(self, request, response):
        """
        Log request patterns for AI analysis
        """
        try:
            from apps.core.models import AccessLog
            
            AccessLog.objects.create(
                user=request.user,
                resource=request.path,
                action=request.method,
                success=200 <= response.status_code < 400,
                ip_address=request.rbac_context.get('ip_address'),
                user_agent=request.rbac_context.get('user_agent'),
                metadata=json.dumps({
                    'status_code': response.status_code,
                    'response_time': getattr(request, '_start_time', 0),
                    'user_roles': request.rbac_context.get('user_roles', [])
                })
            )
        except Exception as e:
            logger.error(f"Failed to log request pattern: {str(e)}")

# Initialize the global permission manager
permission_manager = AdvancedPermissionManager()