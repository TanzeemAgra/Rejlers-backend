"""
AI Hub URL Configuration
========================

URL routing for the Super Admin AI Hub featuring:
- AI-powered security center
- Predictive analytics dashboard
- Real-time monitoring endpoints
- Security alert management
"""

from django.urls import path
from .ai_hub_views import (
    AIHubDashboardView,
    SecurityCenterView,
    PredictiveAnalyticsView,
    RealTimeMonitoringView,
    ai_hub_health_check,
    resolve_security_alert
)

app_name = 'ai_hub'

urlpatterns = [
    # Main AI Hub Dashboard
    path('dashboard/', AIHubDashboardView.as_view(), name='dashboard'),
    
    # AI Security Center
    path('security-center/', SecurityCenterView.as_view(), name='security-center'),
    
    # Predictive Analytics
    path('analytics/', PredictiveAnalyticsView.as_view(), name='predictive-analytics'),
    
    # Real-time Monitoring
    path('monitoring/', RealTimeMonitoringView.as_view(), name='real-time-monitoring'),
    
    # Health Check
    path('health/', ai_hub_health_check, name='health-check'),
    
    # Alert Management
    path('alerts/resolve/', resolve_security_alert, name='resolve-alert'),
]