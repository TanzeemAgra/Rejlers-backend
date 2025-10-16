"""
RBAC API URL Configuration
=========================

URL routing for RBAC API endpoints with comprehensive security features
"""

from django.urls import path, include
from .api_views import (
    RBACPermissionCheckView,
    RBACRefreshPermissionsView, 
    RBACRouteAccessView,
    RBACSecurityMonitoringView,
    RBACAccessPatternView,
    RBACUserRiskAssessmentView,
    EnhancedLoginView,
)

app_name = 'rbac_api'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', EnhancedLoginView.as_view(), name='enhanced-login'),
    
    # Permission management endpoints
    path('check-permission/', RBACPermissionCheckView.as_view(), name='check-permission'),
    path('refresh-permissions/', RBACRefreshPermissionsView.as_view(), name='refresh-permissions'),
    
    # Access logging and monitoring
    path('log-route-access/', RBACRouteAccessView.as_view(), name='log-route-access'),
    path('log-permission-check/', RBACAccessPatternView.as_view(), name='log-permission-check'),
    path('log-access-pattern/', RBACAccessPatternView.as_view(), name='log-access-pattern'),
    
    # Security monitoring
    path('security-monitoring/', RBACSecurityMonitoringView.as_view(), name='security-monitoring'),
    path('risk-assessment/', RBACUserRiskAssessmentView.as_view(), name='risk-assessment'),
    
    # Access pattern analysis
    path('access-patterns/', RBACAccessPatternView.as_view(), name='access-patterns'),
]