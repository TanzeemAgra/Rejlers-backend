"""
Enhanced JWT Authentication with Role Claims and AI-Powered Security
==================================================================

Custom JWT authentication that includes role information in tokens
and provides AI-powered security monitoring.
"""

import json
import logging
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from apps.authentication.models import Role
from apps.core.rbac_enforcement import permission_manager

logger = logging.getLogger(__name__)


class EnhancedTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Enhanced JWT serializer that includes role claims and security metadata
    """
    
    @classmethod
    def get_token(cls, user):
        """
        Generate token with enhanced role and security claims
        """
        token = super().get_token(user)
        
        # Add user information
        token['user_id'] = str(user.id)
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        # Add role information
        user_roles = []  # UserRole model not available, using simplified roles
        roles_data = []
        
        for role in user_roles:
            roles_data.append({
                'role_name': role.role_name,
                'role_category': role.role_category,
                'is_active': role.is_active,
                'assigned_at': role.assigned_at.isoformat() if role.assigned_at else None
            })
        
        token['roles'] = roles_data
        token['role_names'] = [role.role_name for role in user_roles]
        token['role_categories'] = list(set(role.role_category for role in user_roles))
        
        # Add security metadata
        token['last_login'] = user.last_login.isoformat() if user.last_login else None
        token['date_joined'] = user.date_joined.isoformat()
        token['token_issued_at'] = timezone.now().isoformat()
        
        # Add AI-powered risk assessment
        token['risk_profile'] = cls._get_user_risk_profile(user)
        
        # Add permissions summary
        token['permissions'] = cls._get_user_permissions_summary(user)
        
        return token
    
    @classmethod
    def _get_user_risk_profile(cls, user):
        """
        Get AI-powered user risk profile
        """
        try:
            from apps.core.models import AccessLog
            risk_profile = AccessLog.get_user_risk_profile(user, days=7)
            
            # AI-enhanced risk calculation
            ai_analysis = permission_manager.ai_engine.analyze_access_pattern(
                user, 'token_request', 'authenticate'
            )
            
            return {
                'base_risk': risk_profile,
                'ai_risk_score': ai_analysis.get('risk_score', 0.0),
                'calculated_at': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Risk profile calculation failed: {str(e)}")
            return {'base_risk': {}, 'ai_risk_score': 0.0}
    
    @classmethod 
    def _get_user_permissions_summary(cls, user):
        """
        Get summary of user permissions for token
        """
        try:
            # Get role-based permission categories
            role_permissions = []
            for role in user.userrole_set.all():
                role_permissions.append({
                    'role': role.role_name,
                    'category': role.role_category,
                    'level': cls._get_role_permission_level(role.role_name)
                })
            
            return {
                'role_permissions': role_permissions,
                'is_enterprise_user': any(
                    'CEO' in role.role_name or 'CFO' in role.role_name or 'CTO' in role.role_name
                    for role in user.userrole_set.all()
                ),
                'has_sensitive_access': cls._has_sensitive_data_access(user),
                'permission_level': cls._calculate_overall_permission_level(user)
            }
        except Exception as e:
            logger.error(f"Permission summary calculation failed: {str(e)}")
            return {}
    
    @classmethod
    def _get_role_permission_level(cls, role_name):
        """
        Calculate permission level for a specific role
        """
        enterprise_roles = ['CEO', 'COO', 'CFO', 'CTO', 'CMO', 'CHRO']
        if any(title in role_name for title in enterprise_roles):
            return 'executive'
        
        management_roles = ['Manager', 'Director', 'Lead']
        if any(title in role_name for title in management_roles):
            return 'management'
        
        ai_roles = ['AI Ethics Officer', 'AI Data Scientist', 'AI Operations Specialist']
        if role_name in ai_roles:
            return 'ai_specialist'
        
        return 'standard'
    
    @classmethod
    def _has_sensitive_data_access(cls, user):
        """
        Check if user has access to sensitive data
        """
        sensitive_roles = [
            'Chief Executive Officer (CEO)', 'Chief Financial Officer (CFO)',
            'Chief Human Resources Officer (CHRO)', 'Finance Manager', 'HR Manager'
        ]
        
        return user.userrole_set.filter(role_name__in=sensitive_roles).exists()
    
    @classmethod
    def _calculate_overall_permission_level(cls, user):
        """
        Calculate overall permission level
        """
        if user.is_superuser:
            return 'superuser'
        
        user_roles = [role.role_name for role in user.userrole_set.all()]
        
        if any('CEO' in role for role in user_roles):
            return 'executive_max'
        elif any('CFO' in role or 'CTO' in role or 'COO' in role for role in user_roles):
            return 'executive_high'
        elif any('Manager' in role for role in user_roles):
            return 'management'
        elif any('AI' in role for role in user_roles):
            return 'ai_specialist'
        else:
            return 'standard'
    
    def validate(self, attrs):
        """
        Enhanced validation with security logging
        """
        try:
            data = super().validate(attrs)
            
            # Log successful authentication
            user = self.user
            self._log_authentication_attempt(user, True, attrs)
            
            # Check for account security
            self._perform_security_checks(user, attrs)
            
            return data
            
        except Exception as e:
            # Log failed authentication
            username = attrs.get('username', 'unknown')
            try:
                user = User.objects.get(username=username)
                self._log_authentication_attempt(user, False, attrs, str(e))
            except User.DoesNotExist:
                logger.warning(f"Authentication attempt with non-existent user: {username}")
            
            raise
    
    def _log_authentication_attempt(self, user, success, attrs, error=None):
        """
        Log authentication attempt for security monitoring
        """
        try:
            from apps.core.models import AccessLog
            
            # Get request metadata if available
            request = self.context.get('request')
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            AccessLog.objects.create(
                user=user,
                resource='authentication',
                action='login_attempt',
                success=success,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={
                    'username': attrs.get('username'),
                    'error': error,
                    'timestamp': timezone.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to log authentication attempt: {str(e)}")
    
    def _perform_security_checks(self, user, attrs):
        """
        Perform additional security checks during authentication
        """
        # Check for suspicious login patterns
        self._check_login_patterns(user)
        
        # Check account status
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {user.username}")
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
    
    def _check_login_patterns(self, user):
        """
        Check for suspicious login patterns
        """
        from apps.core.models import AccessLog
        
        # Check recent failed attempts
        recent_failed = AccessLog.objects.filter(
            user=user,
            action='login_attempt',
            success=False,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        if recent_failed > 5:
            logger.warning(f"Multiple failed login attempts for user: {user.username}")
    
    def _get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EnhancedTokenObtainPairView(TokenObtainPairView):
    """
    Enhanced token view with additional security features
    """
    serializer_class = EnhancedTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Enhanced token generation with rate limiting and monitoring
        """
        # Rate limiting
        ip_address = self._get_client_ip(request)
        rate_limit_key = f"login_attempts_{ip_address}"
        attempts = cache.get(rate_limit_key, 0)
        
        if attempts > 10:  # Max 10 attempts per hour per IP
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            from rest_framework import status
            from rest_framework.response import Response
            return Response(
                {'error': 'Too many login attempts. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Increment attempt counter
        cache.set(rate_limit_key, attempts + 1, 3600)
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Clear rate limit on successful login
            cache.delete(rate_limit_key)
            
            # Add security headers
            response['X-Auth-Success'] = 'true'
            response['X-Token-Issued'] = timezone.now().isoformat()
        
        return response
    
    def _get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AIEnhancedJWTAuthentication(JWTAuthentication):
    """
    AI-Enhanced JWT Authentication with real-time security monitoring
    """
    
    def authenticate(self, request):
        """
        Enhanced authentication with AI-powered monitoring
        """
        result = super().authenticate(request)
        
        if result is not None:
            user, validated_token = result
            
            # Perform AI-powered security checks
            self._ai_security_check(request, user, validated_token)
            
            # Add security context to request
            request.security_context = {
                'user_risk_profile': self._get_cached_risk_profile(user),
                'token_metadata': self._extract_token_metadata(validated_token),
                'authentication_timestamp': timezone.now()
            }
        
        return result
    
    def _ai_security_check(self, request, user, token):
        """
        AI-powered security check for authenticated requests
        """
        try:
            # Check token metadata for anomalies
            token_payload = token.payload
            
            # Check for token age anomalies
            issued_at = datetime.fromtimestamp(token_payload.get('iat', 0), tz=timezone.utc)
            token_age = timezone.now() - issued_at
            
            if token_age > timedelta(hours=24):
                logger.info(f"Old token used by user {user.username}: {token_age}")
            
            # Check for role consistency
            token_roles = token_payload.get('role_names', [])
            current_roles = [role.role_name for role in user.userrole_set.all()]
            
            if set(token_roles) != set(current_roles):
                logger.warning(f"Role mismatch detected for user {user.username}")
                # Could invalidate token or trigger re-authentication
            
            # AI-powered behavior analysis
            if hasattr(permission_manager, 'ai_engine'):
                ai_analysis = permission_manager.ai_engine.analyze_access_pattern(
                    user, 'api_access', request.method
                )
                
                if ai_analysis.get('risk_score', 0) > 0.8:
                    logger.warning(f"High risk AI score for user {user.username}: {ai_analysis}")
        
        except Exception as e:
            logger.error(f"AI security check failed: {str(e)}")
    
    def _get_cached_risk_profile(self, user):
        """
        Get cached user risk profile
        """
        cache_key = f"risk_profile_{user.id}"
        risk_profile = cache.get(cache_key)
        
        if not risk_profile:
            try:
                from apps.core.models import AccessLog
                risk_profile = AccessLog.get_user_risk_profile(user)
                cache.set(cache_key, risk_profile, 300)  # Cache for 5 minutes
            except:
                risk_profile = {}
        
        return risk_profile
    
    def _extract_token_metadata(self, token):
        """
        Extract relevant metadata from JWT token
        """
        payload = token.payload
        
        return {
            'user_id': payload.get('user_id'),
            'issued_at': payload.get('iat'),
            'expires_at': payload.get('exp'),
            'roles': payload.get('roles', []),
            'permission_level': payload.get('permissions', {}).get('permission_level'),
            'risk_score': payload.get('risk_profile', {}).get('ai_risk_score', 0.0)
        }


def create_enhanced_token_for_user(user):
    """
    Create enhanced JWT token for a user programmatically
    """
    refresh = RefreshToken.for_user(user)
    
    # Add enhanced claims using our serializer logic
    token = EnhancedTokenObtainPairSerializer.get_token(user)
    
    return {
        'refresh': str(token),
        'access': str(token.access_token),
        'user_data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [role.role_name for role in user.userrole_set.all()],
            'permission_level': EnhancedTokenObtainPairSerializer._calculate_overall_permission_level(user)
        }
    }