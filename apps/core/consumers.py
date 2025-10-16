"""
Real-time Security Monitoring WebSocket Consumer
===============================================

WebSocket consumer for real-time RBAC security monitoring:
- Live security alerts and notifications
- Real-time access pattern analysis
- AI-powered anomaly detection streaming
- User activity monitoring dashboard
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.rbac_enforcement import AIPermissionEngine, SecurityMonitor

logger = logging.getLogger(__name__)
User = get_user_model()


class SecurityMonitoringConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time security monitoring
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.security_group = None
        self.monitoring_task = None
        self.ai_engine = AIPermissionEngine()
        self.security_monitor = SecurityMonitor()

    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Get user from scope (set by authentication middleware)
            self.user = self.scope.get('user')
            
            if not self.user or not self.user.is_authenticated:
                await self.close(code=4001)  # Unauthorized
                return
            
            # Check if user has permission for security monitoring
            has_permission = await self.check_monitoring_permission()
            if not has_permission:
                await self.close(code=4003)  # Forbidden
                return
            
            # Create user-specific security monitoring group
            self.security_group = f"security_monitor_{self.user.id}"
            
            # Join the security monitoring group
            await self.channel_layer.group_add(
                self.security_group,
                self.channel_name
            )
            
            # Accept the connection
            await self.accept()
            
            # Start monitoring task
            self.monitoring_task = asyncio.create_task(
                self.start_security_monitoring()
            )
            
            # Send initial security status
            await self.send_initial_security_status()
            
            logger.info(f"Security monitoring connected for user {self.user.id}")
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
            await self.close(code=4000)  # Generic error

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
            
            # Leave the security monitoring group
            if self.security_group:
                await self.channel_layer.group_discard(
                    self.security_group,
                    self.channel_name
                )
            
            logger.info(f"Security monitoring disconnected for user {self.user.id if self.user else 'unknown'}")
            
        except Exception as e:
            logger.error(f"WebSocket disconnection error: {str(e)}")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_alerts':
                await self.handle_subscribe_alerts(data)
            elif message_type == 'request_risk_assessment':
                await self.handle_risk_assessment_request(data)
            elif message_type == 'acknowledge_alert':
                await self.handle_alert_acknowledgment(data)
            elif message_type == 'request_user_activity':
                await self.handle_user_activity_request(data)
            else:
                await self.send_error('Unknown message type')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"WebSocket message handling error: {str(e)}")
            await self.send_error('Message processing failed')

    async def start_security_monitoring(self):
        """Start continuous security monitoring"""
        try:
            while True:
                # Perform security checks
                security_events = await self.check_security_events()
                
                if security_events:
                    await self.send_security_events(security_events)
                
                # Check for AI anomalies
                ai_anomalies = await self.check_ai_anomalies()
                
                if ai_anomalies:
                    await self.send_ai_anomalies(ai_anomalies)
                
                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except asyncio.CancelledError:
            logger.info("Security monitoring task cancelled")
        except Exception as e:
            logger.error(f"Security monitoring error: {str(e)}")

    async def check_monitoring_permission(self) -> bool:
        """Check if user has permission for security monitoring"""
        try:
            # Check if user is admin or has security monitoring role
            if self.user.is_superuser:
                return True
            
            user_roles = await self.get_user_roles()
            monitoring_roles = [
                'SuperAdmin',
                'Security_Admin', 
                'AI_Specialist',
                'Executive'
            ]
            
            return any(role in monitoring_roles for role in user_roles)
            
        except Exception as e:
            logger.error(f"Permission check error: {str(e)}")
            return False

    @database_sync_to_async
    def get_user_roles(self) -> List[str]:
        """Get user roles from database"""
        try:
            if hasattr(self.user, 'roles'):
                return [role.name for role in self.user.roles.filter(is_active=True)]
            else:
                return ['Employee']
        except Exception:
            return ['Employee']

    async def send_initial_security_status(self):
        """Send initial security status to client"""
        try:
            # Get current security status
            security_status = await self.get_security_status()
            
            # Get recent security events
            recent_events = await self.get_recent_security_events()
            
            # Get AI risk assessment
            risk_assessment = await self.get_risk_assessment()
            
            await self.send(text_data=json.dumps({
                'type': 'initial_status',
                'data': {
                    'securityStatus': security_status,
                    'recentEvents': recent_events,
                    'riskAssessment': risk_assessment,
                    'timestamp': timezone.now().isoformat(),
                }
            }))
            
        except Exception as e:
            logger.error(f"Initial status error: {str(e)}")
            await self.send_error('Failed to get initial status')

    async def check_security_events(self) -> List[Dict[str, Any]]:
        """Check for new security events"""
        try:
            # Get security events from cache/database
            cache_key = f"security_events_{self.user.id}"
            events = cache.get(cache_key, [])
            
            # Filter new events (within last 30 seconds)
            cutoff_time = timezone.now() - timedelta(seconds=30)
            new_events = [
                event for event in events
                if datetime.fromisoformat(event.get('timestamp', '')) > cutoff_time
            ]
            
            return new_events
            
        except Exception as e:
            logger.error(f"Security events check error: {str(e)}")
            return []

    async def check_ai_anomalies(self) -> List[Dict[str, Any]]:
        """Check for AI-detected anomalies"""
        try:
            # Use AI engine to detect anomalies
            anomalies = await self.run_ai_anomaly_detection()
            
            return anomalies
            
        except Exception as e:
            logger.error(f"AI anomaly check error: {str(e)}")
            return []

    @database_sync_to_async
    def run_ai_anomaly_detection(self) -> List[Dict[str, Any]]:
        """Run AI anomaly detection"""
        try:
            # Get user's recent access patterns
            cache_key = f"access_patterns_{self.user.id}"
            patterns = cache.get(cache_key, [])
            
            if len(patterns) < 5:  # Need minimum data for analysis
                return []
            
            # Analyze patterns for anomalies
            anomalies = self.ai_engine.detect_access_anomalies(
                user=self.user,
                patterns=patterns
            )
            
            return anomalies
            
        except Exception as e:
            logger.error(f"AI anomaly detection error: {str(e)}")
            return []

    async def handle_subscribe_alerts(self, data):
        """Handle alert subscription request"""
        try:
            alert_types = data.get('alertTypes', ['all'])
            
            # Store subscription preferences
            cache_key = f"alert_subscription_{self.user.id}"
            cache.set(cache_key, {
                'alert_types': alert_types,
                'subscribed_at': timezone.now().isoformat(),
            }, timeout=3600)  # 1 hour
            
            await self.send(text_data=json.dumps({
                'type': 'subscription_confirmed',
                'data': {
                    'alertTypes': alert_types,
                    'message': 'Successfully subscribed to security alerts'
                }
            }))
            
        except Exception as e:
            logger.error(f"Alert subscription error: {str(e)}")
            await self.send_error('Failed to subscribe to alerts')

    async def handle_risk_assessment_request(self, data):
        """Handle risk assessment request"""
        try:
            target_user_id = data.get('userId', self.user.id)
            
            # Check permission to assess other users
            if target_user_id != self.user.id:
                has_permission = await self.check_admin_permission()
                if not has_permission:
                    await self.send_error('Insufficient permission for user risk assessment')
                    return
            
            # Get risk assessment
            risk_assessment = await self.get_user_risk_assessment(target_user_id)
            
            await self.send(text_data=json.dumps({
                'type': 'risk_assessment',
                'data': {
                    'userId': target_user_id,
                    'riskAssessment': risk_assessment,
                    'timestamp': timezone.now().isoformat(),
                }
            }))
            
        except Exception as e:
            logger.error(f"Risk assessment request error: {str(e)}")
            await self.send_error('Failed to get risk assessment')

    async def send_security_events(self, events):
        """Send security events to client"""
        await self.send(text_data=json.dumps({
            'type': 'security_events',
            'data': {
                'events': events,
                'timestamp': timezone.now().isoformat(),
            }
        }))

    async def send_ai_anomalies(self, anomalies):
        """Send AI anomalies to client"""
        await self.send(text_data=json.dumps({
            'type': 'ai_anomalies',
            'data': {
                'anomalies': anomalies,
                'timestamp': timezone.now().isoformat(),
            }
        }))

    async def send_error(self, message: str):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'data': {
                'message': message,
                'timestamp': timezone.now().isoformat(),
            }
        }))

    @database_sync_to_async
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        try:
            return self.security_monitor.get_user_security_status(self.user)
        except Exception as e:
            logger.error(f"Security status error: {str(e)}")
            return {}

    @database_sync_to_async
    def get_recent_security_events(self) -> List[Dict[str, Any]]:
        """Get recent security events"""
        try:
            cache_key = f"security_events_{self.user.id}"
            events = cache.get(cache_key, [])
            
            # Return last 10 events
            return events[-10:]
            
        except Exception as e:
            logger.error(f"Recent events error: {str(e)}")
            return []

    @database_sync_to_async
    def get_risk_assessment(self) -> Dict[str, Any]:
        """Get AI risk assessment"""
        try:
            return self.ai_engine.comprehensive_risk_assessment(self.user)
        except Exception as e:
            logger.error(f"Risk assessment error: {str(e)}")
            return {}

    async def check_admin_permission(self) -> bool:
        """Check if user has admin permissions"""
        try:
            if self.user.is_superuser:
                return True
            
            user_roles = await self.get_user_roles()
            admin_roles = ['SuperAdmin', 'Security_Admin', 'Executive']
            
            return any(role in admin_roles for role in user_roles)
            
        except Exception:
            return False

    @database_sync_to_async
    def get_user_risk_assessment(self, user_id: int) -> Dict[str, Any]:
        """Get risk assessment for specific user"""
        try:
            user = User.objects.get(id=user_id)
            return self.ai_engine.comprehensive_risk_assessment(user)
        except User.DoesNotExist:
            return {'error': 'User not found'}
        except Exception as e:
            logger.error(f"User risk assessment error: {str(e)}")
            return {'error': 'Assessment failed'}


class UserActivityConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time user activity monitoring
    """
    
    async def connect(self):
        """Handle connection for activity monitoring"""
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Create user activity group
        self.activity_group = f"activity_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.activity_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current activity status
        await self.send_activity_status()

    async def disconnect(self, close_code):
        """Handle disconnection"""
        if hasattr(self, 'activity_group'):
            await self.channel_layer.group_discard(
                self.activity_group,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle activity updates"""
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'activity_update':
                await self.handle_activity_update(data)
                
        except Exception as e:
            logger.error(f"Activity consumer error: {str(e)}")

    async def handle_activity_update(self, data):
        """Handle user activity update"""
        try:
            activity_data = {
                'user_id': self.user.id,
                'activity': data.get('activity'),
                'timestamp': timezone.now().isoformat(),
                'metadata': data.get('metadata', {}),
            }
            
            # Store activity in cache
            cache_key = f"user_activity_{self.user.id}"
            recent_activity = cache.get(cache_key, [])
            recent_activity.append(activity_data)
            
            # Keep last 50 activities
            if len(recent_activity) > 50:
                recent_activity = recent_activity[-50:]
            
            cache.set(cache_key, recent_activity, timeout=3600)
            
            # Broadcast to activity monitoring group
            await self.channel_layer.group_send(
                self.activity_group,
                {
                    'type': 'activity_broadcast',
                    'activity': activity_data,
                }
            )
            
        except Exception as e:
            logger.error(f"Activity update error: {str(e)}")

    async def send_activity_status(self):
        """Send current activity status"""
        try:
            cache_key = f"user_activity_{self.user.id}"
            recent_activity = cache.get(cache_key, [])
            
            await self.send(text_data=json.dumps({
                'type': 'activity_status',
                'data': {
                    'recentActivity': recent_activity[-10:],  # Last 10 activities
                    'timestamp': timezone.now().isoformat(),
                }
            }))
            
        except Exception as e:
            logger.error(f"Activity status error: {str(e)}")

    async def activity_broadcast(self, event):
        """Handle activity broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'activity_update',
            'data': event['activity'],
        }))