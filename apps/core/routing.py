"""
WebSocket Routing Configuration for RBAC
========================================

WebSocket routing for real-time RBAC security monitoring
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/security-monitor/$', consumers.SecurityMonitoringConsumer.as_asgi()),
    re_path(r'ws/user-activity/$', consumers.UserActivityConsumer.as_asgi()),
]