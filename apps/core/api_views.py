"""
RBAC API Endpoints
==================

Comprehensive API endpoints for frontend-backend RBAC integration:
- Permission checking and validation
- AI risk assessment endpoints
- Security monitoring and logging
- Real-time access pattern analysis
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from apps.core.rbac_enforcement import (
    AIPermissionEngine, 
    AdvancedPermissionManager
)
from apps.core.enhanced_jwt import EnhancedTokenObtainPairSerializer
from apps.authentication.models import User

logger = logging.getLogger(__name__)

class RBACPermissionCheckView(APIView):
    """
    API endpoint for checking user permissions with AI enhancement
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Check if user has permission for specific resource/action
        """
        try:
            data = request.data
            resource = data.get('resource')
            action = data.get('action')
            context = data.get('context', {})
            
            if not resource or not action:
                return Response({
                    'error': 'Resource and action are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get AI permission engine
            ai_engine = AIPermissionEngine()
            permission_manager = AdvancedPermissionManager()
            
            # Check permission with AI enhancement
            permission_result = permission_manager.check_permission(
                request.user, resource, action, context
            )
            
            # Get AI analysis
            ai_analysis = ai_engine.analyze_permission_request(
                user=request.user,
                resource=resource,
                action=action,
                context=context,
                request_metadata={
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'timestamp': timezone.now().isoformat(),
                }
            )
            
            # Log the permission check
            self._log_permission_check({
                'user_id': request.user.id,
                'resource': resource,
                'action': action,
                'granted': permission_result['allowed'],
                'ai_risk_score': ai_analysis['risk_score'],
                'context': context,
                'timestamp': timezone.now().isoformat(),
            })
            
            return Response({
                'allowed': permission_result['allowed'],
                'aiAnalysis': {
                    'riskScore': ai_analysis['risk_score'],
                    'anomalies': ai_analysis.get('anomalies', []),
                    'recommendations': ai_analysis.get('recommendations', []),
                    'confidence': ai_analysis.get('confidence', 0.5),
                },
                'reasoning': permission_result.get('reasoning', []),
                'cached': permission_result.get('cached', False),
            })
            
        except Exception as e:
            logger.error(f"Permission check error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Permission check failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def _log_permission_check(self, data):
        """Log permission check for audit and AI learning"""
        try:
            cache_key = f"permission_log_{data['user_id']}_{timezone.now().strftime('%Y%m%d%H')}"
            existing_logs = cache.get(cache_key, [])
            existing_logs.append(data)
            
            # Keep max 100 logs per hour per user
            if len(existing_logs) > 100:
                existing_logs = existing_logs[-100:]
            
            cache.set(cache_key, existing_logs, timeout=3600)  # 1 hour
            
            # Also log to database for long-term analysis
            # This would typically go to a dedicated audit log table
            
        except Exception as e:
            logger.warning(f"Failed to log permission check: {str(e)}")


class RBACRefreshPermissionsView(APIView):
    """
    API endpoint to refresh user permissions and AI predictions
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Refresh permissions and get updated AI predictions
        """
        try:
            user = request.user
            permission_manager = AdvancedPermissionManager()
            ai_engine = AIPermissionEngine()
            
            # Refresh user permissions from database
            updated_permissions = permission_manager.get_user_permissions(user)
            
            # Get fresh AI predictions
            ai_predictions = ai_engine.predict_access_patterns(
                user=user,
                time_horizon_hours=24
            )
            
            # Update cache
            cache_key = f"user_permissions_{user.id}"
            cache.set(cache_key, updated_permissions, timeout=600)  # 10 minutes
            
            ai_cache_key = f"ai_predictions_{user.id}"
            cache.set(ai_cache_key, ai_predictions, timeout=300)  # 5 minutes
            
            return Response({
                'permissions': updated_permissions,
                'aiPredictions': ai_predictions,
                'refreshedAt': timezone.now().isoformat(),
                'cacheTimeout': 600,
            })
            
        except Exception as e:
            logger.error(f"Permission refresh error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to refresh permissions',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RBACRouteAccessView(APIView):
    """
    API endpoint for logging route access attempts
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Log route access for AI analysis and security monitoring
        """
        try:
            data = request.data
            route = data.get('route')
            access_granted = data.get('access_granted', False)
            risk_score = data.get('risk_score', 0.0)
            blocking_factors = data.get('blocking_factors', [])
            
            if not route:
                return Response({
                    'error': 'Route is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create access log entry
            access_log = {
                'user_id': request.user.id,
                'route': route,
                'access_granted': access_granted,
                'risk_score': risk_score,
                'blocking_factors': blocking_factors,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'timestamp': timezone.now().isoformat(),
            }
            
            # Store in cache for real-time monitoring
            cache_key = f"route_access_{request.user.id}"
            recent_access = cache.get(cache_key, [])
            recent_access.append(access_log)
            
            # Keep last 50 access attempts
            if len(recent_access) > 50:
                recent_access = recent_access[-50:]
            
            cache.set(cache_key, recent_access, timeout=1800)  # 30 minutes
            
            # Check for security alerts
            security_alerts = self._check_security_alerts(request.user, access_log, recent_access)
            
            return Response({
                'logged': True,
                'timestamp': access_log['timestamp'],
                'securityAlerts': security_alerts,
            })
            
        except Exception as e:
            logger.error(f"Route access logging error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to log route access',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def _check_security_alerts(self, user, current_access, recent_access):
        """Check for security alert conditions"""
        alerts = []
        
        # Check for multiple failed access attempts
        failed_attempts = [
            access for access in recent_access[-10:]  # Last 10 attempts
            if not access['access_granted']
        ]
        
        if len(failed_attempts) >= 3:
            alerts.append({
                'type': 'multiple_failed_access',
                'severity': 'high',
                'message': f"{len(failed_attempts)} failed access attempts in recent history",
                'count': len(failed_attempts),
            })
        
        # Check for high-risk access patterns
        if current_access['risk_score'] > 0.8:
            alerts.append({
                'type': 'high_risk_access',
                'severity': 'critical',
                'message': f"High risk access attempt: {current_access['risk_score']:.1%}",
                'risk_score': current_access['risk_score'],
            })
        
        # Check for unusual time access
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Outside normal hours
            alerts.append({
                'type': 'off_hours_access',
                'severity': 'medium',
                'message': f"Access attempt during off-hours ({current_hour}:00)",
                'hour': current_hour,
            })
        
        return alerts


class RBACSecurityMonitoringView(APIView):
    """
    API endpoint for security monitoring and alerts
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get security monitoring data for the current user
        """
        try:
            user = request.user
            # SecurityMonitor not yet implemented
            # security_monitor = SecurityMonitor()
            
            # Get user's security status (placeholder)
            security_status = {'status': 'normal', 'risk_level': 'low'}
            
            # Get recent security events
            recent_events = self._get_recent_security_events(user)
            
            # Get AI risk assessment
            ai_engine = AIPermissionEngine()
            risk_assessment = ai_engine.assess_user_risk(user, include_predictions=True)
            
            return Response({
                'securityStatus': security_status,
                'recentEvents': recent_events,
                'riskAssessment': risk_assessment,
                'monitoringTimestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            logger.error(f"Security monitoring error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to get security monitoring data',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_recent_security_events(self, user):
        """Get recent security events for user"""
        try:
            # Get from cache
            cache_key = f"security_events_{user.id}"
            events = cache.get(cache_key, [])
            
            # Filter to last 24 hours
            cutoff_time = timezone.now() - timedelta(hours=24)
            recent_events = [
                event for event in events
                if datetime.fromisoformat(event['timestamp']) > cutoff_time
            ]
            
            return recent_events
            
        except Exception as e:
            logger.warning(f"Error getting security events: {str(e)}")
            return []


class RBACAccessPatternView(APIView):
    """
    API endpoint for access pattern analysis
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Log access pattern for AI learning
        """
        try:
            data = request.data
            
            access_pattern = {
                'user_id': request.user.id,
                'timestamp': data.get('timestamp', timezone.now().isoformat()),
                'resource': data.get('resource'),
                'action': data.get('action'),
                'success': data.get('success', True),
                'risk_score': data.get('risk_score', 0.0),
                'context': data.get('context', {}),
            }
            
            # Store in cache for AI analysis
            cache_key = f"access_patterns_{request.user.id}"
            patterns = cache.get(cache_key, [])
            patterns.append(access_pattern)
            
            # Keep last 100 patterns
            if len(patterns) > 100:
                patterns = patterns[-100:]
            
            cache.set(cache_key, patterns, timeout=3600)  # 1 hour
            
            # Trigger AI analysis if we have enough data
            if len(patterns) >= 10:
                self._trigger_ai_analysis(request.user.id, patterns)
            
            return Response({
                'logged': True,
                'patternCount': len(patterns),
            })
            
        except Exception as e:
            logger.error(f"Access pattern logging error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to log access pattern',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """
        Get user's access patterns for analysis
        """
        try:
            user = request.user
            
            # Get cached patterns
            cache_key = f"access_patterns_{user.id}"
            patterns = cache.get(cache_key, [])
            
            # Calculate pattern statistics
            stats = self._calculate_pattern_stats(patterns)
            
            return Response({
                'patterns': patterns[-20:],  # Last 20 patterns
                'statistics': stats,
                'totalPatterns': len(patterns),
            })
            
        except Exception as e:
            logger.error(f"Access pattern retrieval error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to get access patterns',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _trigger_ai_analysis(self, user_id, patterns):
        """Trigger AI analysis of access patterns"""
        try:
            ai_engine = AIPermissionEngine()
            
            # Analyze patterns asynchronously
            analysis_result = ai_engine.analyze_access_patterns(
                user_id=user_id,
                patterns=patterns
            )
            
            # Cache analysis results
            analysis_cache_key = f"pattern_analysis_{user_id}"
            cache.set(analysis_cache_key, analysis_result, timeout=1800)  # 30 minutes
            
        except Exception as e:
            logger.warning(f"AI analysis trigger error: {str(e)}")
    
    def _calculate_pattern_stats(self, patterns):
        """Calculate statistics from access patterns"""
        if not patterns:
            return {}
        
        total_patterns = len(patterns)
        successful_access = sum(1 for p in patterns if p.get('success', True))
        failed_access = total_patterns - successful_access
        
        # Calculate average risk score
        risk_scores = [p.get('risk_score', 0.0) for p in patterns]
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        
        # Most accessed resources
        resource_counts = {}
        for pattern in patterns:
            resource = pattern.get('resource', 'unknown')
            resource_counts[resource] = resource_counts.get(resource, 0) + 1
        
        most_accessed = sorted(
            resource_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            'totalPatterns': total_patterns,
            'successfulAccess': successful_access,
            'failedAccess': failed_access,
            'successRate': (successful_access / total_patterns) * 100 if total_patterns > 0 else 0,
            'averageRiskScore': avg_risk_score,
            'mostAccessedResources': most_accessed,
        }


class RBACUserRiskAssessmentView(APIView):
    """
    API endpoint for AI-powered user risk assessment
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive risk assessment for current user
        """
        try:
            user = request.user
            ai_engine = AIPermissionEngine()
            
            # Perform comprehensive risk assessment
            risk_assessment = ai_engine.comprehensive_risk_assessment(
                user=user,
                include_behavioral_analysis=True,
                include_predictions=True
            )
            
            return Response({
                'riskAssessment': risk_assessment,
                'assessmentTimestamp': timezone.now().isoformat(),
                'validityPeriod': '1 hour',
            })
            
        except Exception as e:
            logger.error(f"Risk assessment error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to perform risk assessment',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Enhanced Authentication Views
class EnhancedLoginView(APIView):
    """
    Enhanced login with AI risk assessment and RBAC integration
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Authenticate user with enhanced security and AI analysis
        """
        try:
            serializer = EnhancedTokenObtainPairSerializer(data=request.data)
            
            if serializer.is_valid():
                # Get tokens and user data
                tokens = serializer.validated_data
                
                return Response({
                    'access': tokens['access'],
                    'refresh': tokens['refresh'],
                    'user': tokens.get('user_data', {}),
                    'aiRiskAssessment': tokens.get('ai_risk_assessment', {}),
                    'requiresMFA': tokens.get('requires_mfa', False),
                    'mfaMethod': tokens.get('mfa_method'),
                    'loginTimestamp': timezone.now().isoformat(),
                })
            else:
                return Response({
                    'error': 'Invalid credentials',
                    'details': serializer.errors
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            logger.error(f"Enhanced login error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Login failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# URL configuration would be added to urls.py