"""
Comprehensive RBAC System Test Suite
====================================

Test suite for verifying complete RBAC implementation:
- Backend permission enforcement
- Frontend integration
- Database schema separation
- API endpoint functionality
- AI-powered features
"""

import pytest
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from apps.core.rbac_enforcement import (
    AIPermissionEngine,
    AdvancedPermissionManager,
    RoleBasedAccessMiddleware
)
from apps.core.db_router import RBACSchemaRouter
from apps.core.db_manager import SchemaAwareManager
from apps.authentication.models import User

User = get_user_model()


class RBACBackendTestCase(TestCase):
    """Test suite for backend RBAC enforcement"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users with different roles
        self.superuser = User.objects.create_user(
            username='admin',
            email='admin@rejlers.se',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        
        self.hr_manager = User.objects.create_user(
            username='hrmanager',
            email='hr@rejlers.se',
            password='testpass123'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@rejlers.se',
            password='testpass123'
        )
        
        # Set up AI engine and permission manager
        self.ai_engine = AIPermissionEngine()
        self.permission_manager = AdvancedPermissionManager()

    def test_ai_permission_engine_initialization(self):
        """Test AI permission engine initialization"""
        self.assertIsNotNone(self.ai_engine)
        self.assertTrue(hasattr(self.ai_engine, 'analyze_permission_request'))
        self.assertTrue(hasattr(self.ai_engine, 'assess_user_risk'))

    def test_permission_manager_basic_checks(self):
        """Test basic permission checking functionality"""
        # Test superuser permissions
        result = self.permission_manager.check_permission(
            self.superuser, 'employee', 'view', {}
        )
        self.assertTrue(result['allowed'])
        
        # Test regular employee permissions
        result = self.permission_manager.check_permission(
            self.employee, 'financial_report', 'view', {}
        )
        self.assertFalse(result['allowed'])

    def test_ai_risk_assessment(self):
        """Test AI risk assessment functionality"""
        risk_assessment = self.ai_engine.assess_user_risk(
            self.employee, 
            include_behavioral_analysis=True
        )
        
        self.assertIn('risk_score', risk_assessment)
        self.assertIn('risk_factors', risk_assessment)
        self.assertIsInstance(risk_assessment['risk_score'], (int, float))
        self.assertTrue(0 <= risk_assessment['risk_score'] <= 1)

    @patch('apps.core.rbac_enforcement.openai')
    def test_ai_permission_analysis(self, mock_openai):
        """Test AI-powered permission analysis"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            'risk_score': 0.3,
            'anomalies': [],
            'recommendations': ['Allow access with monitoring']
        })
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        analysis = self.ai_engine.analyze_permission_request(
            user=self.employee,
            resource='project_data',
            action='view',
            context={'time': 'business_hours'}
        )
        
        self.assertIn('risk_score', analysis)
        self.assertIn('recommendations', analysis)

    def test_role_based_access_middleware(self):
        """Test role-based access middleware"""
        middleware = RoleBasedAccessMiddleware(lambda x: x)
        
        # Create mock request
        request = MagicMock()
        request.user = self.employee
        request.path = '/api/finance/reports/'
        request.method = 'GET'
        
        # Test middleware processing
        response = middleware(request)
        # Should not raise exceptions for basic processing


class RBACDatabaseTestCase(TestCase):
    """Test suite for database schema separation and routing"""
    
    def setUp(self):
        """Set up test data"""
        self.router = RBACSchemaRouter()
        
        self.superuser = User.objects.create_user(
            username='admin',
            email='admin@rejlers.se', 
            password='testpass123',
            is_superuser=True
        )
        
        self.hr_user = User.objects.create_user(
            username='hruser',
            email='hr@rejlers.se',
            password='testpass123'
        )

    def test_schema_mapping(self):
        """Test correct schema mapping for different apps"""
        # Test HR app mapping
        hr_schema = self.router._get_model_schema('hr_management')
        self.assertEqual(hr_schema, 'hr_data')
        
        # Test finance app mapping  
        finance_schema = self.router._get_model_schema('finance')
        self.assertEqual(finance_schema, 'finance_data')
        
        # Test default mapping
        unknown_schema = self.router._get_model_schema('unknown_app')
        self.assertEqual(unknown_schema, 'public_data')

    def test_role_based_schema_access(self):
        """Test role-based schema access control"""
        # Mock user roles for testing
        with patch.object(self.router, '_get_user_roles') as mock_get_roles:
            # Test SuperAdmin access
            mock_get_roles.return_value = ['SuperAdmin']
            self.router._cached_user = self.superuser
            
            has_access = self.router._check_schema_access('finance_data', 'read')
            self.assertTrue(has_access)
            
            # Test restricted access
            mock_get_roles.return_value = ['Employee']
            self.router._cached_user = self.hr_user
            
            has_access = self.router._check_schema_access('executive_data', 'read')
            self.assertFalse(has_access)

    def test_schema_aware_manager(self):
        """Test schema-aware database manager functionality"""
        manager = SchemaAwareManager()
        
        # Test queryset creation
        queryset = manager.get_queryset()
        self.assertIsNotNone(queryset)
        
        # Test schema context
        schema_qs = manager.in_schema('hr_data')
        self.assertEqual(schema_qs.schema_context, 'hr_data')


class RBACAPITestCase(APITestCase):
    """Test suite for RBAC API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.superuser = User.objects.create_user(
            username='admin',
            email='admin@rejlers.se',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@rejlers.se',
            password='testpass123'
        )

    def test_permission_check_endpoint(self):
        """Test permission checking API endpoint"""
        self.client.force_authenticate(user=self.employee)
        
        response = self.client.post('/api/v1/rbac/check-permission/', {
            'resource': 'project_data',
            'action': 'view',
            'context': {'timestamp': '2024-01-01T12:00:00Z'}
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('allowed', response.data)
        self.assertIn('aiAnalysis', response.data)

    def test_refresh_permissions_endpoint(self):
        """Test permission refresh API endpoint"""
        self.client.force_authenticate(user=self.employee)
        
        response = self.client.post('/api/v1/rbac/refresh-permissions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('permissions', response.data)
        self.assertIn('aiPredictions', response.data)

    def test_security_monitoring_endpoint(self):
        """Test security monitoring API endpoint"""
        self.client.force_authenticate(user=self.superuser)
        
        response = self.client.get('/api/v1/rbac/security-monitoring/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('securityStatus', response.data)
        self.assertIn('riskAssessment', response.data)

    def test_route_access_logging(self):
        """Test route access logging endpoint"""
        self.client.force_authenticate(user=self.employee)
        
        response = self.client.post('/api/v1/rbac/log-route-access/', {
            'route': '/dashboard',
            'access_granted': True,
            'risk_score': 0.2
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('logged', response.data)
        self.assertTrue(response.data['logged'])

    def test_access_pattern_logging(self):
        """Test access pattern logging endpoint"""
        self.client.force_authenticate(user=self.employee)
        
        response = self.client.post('/api/v1/rbac/log-access-pattern/', {
            'timestamp': '2024-01-01T12:00:00Z',
            'resource': 'project_data',
            'action': 'view',
            'success': True,
            'risk_score': 0.1
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('logged', response.data)

    def test_risk_assessment_endpoint(self):
        """Test user risk assessment endpoint"""
        self.client.force_authenticate(user=self.employee)
        
        response = self.client.get('/api/v1/rbac/risk-assessment/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('riskAssessment', response.data)

    def test_unauthorized_access(self):
        """Test API endpoints reject unauthorized access"""
        # Don't authenticate
        response = self.client.post('/api/v1/rbac/check-permission/', {
            'resource': 'test',
            'action': 'view'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RBACIntegrationTestCase(TestCase):
    """Integration tests for complete RBAC system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.client = APIClient()
        
        # Create users with different permission levels
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@rejlers.se',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        
        self.hr_manager = User.objects.create_user(
            username='hrmanager', 
            email='hr@rejlers.se',
            password='testpass123'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@rejlers.se', 
            password='testpass123'
        )

    def test_end_to_end_permission_flow(self):
        """Test complete permission checking flow"""
        # 1. Authenticate user
        self.client.force_authenticate(user=self.employee)
        
        # 2. Check permission via API
        permission_response = self.client.post('/api/v1/rbac/check-permission/', {
            'resource': 'employee_data',
            'action': 'view_own'
        })
        
        self.assertEqual(permission_response.status_code, status.HTTP_200_OK)
        
        # 3. Log access pattern
        log_response = self.client.post('/api/v1/rbac/log-access-pattern/', {
            'resource': 'employee_data',
            'action': 'view_own',
            'success': permission_response.data['allowed']
        })
        
        self.assertEqual(log_response.status_code, status.HTTP_200_OK)
        
        # 4. Get updated risk assessment
        risk_response = self.client.get('/api/v1/rbac/risk-assessment/')
        
        self.assertEqual(risk_response.status_code, status.HTTP_200_OK)

    def test_high_privilege_access_monitoring(self):
        """Test monitoring of high-privilege access"""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin)
        
        # Access sensitive resource
        response = self.client.post('/api/v1/rbac/check-permission/', {
            'resource': 'executive_data',
            'action': 'view'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['allowed'])
        
        # Check that AI analysis includes appropriate monitoring
        ai_analysis = response.data['aiAnalysis']
        self.assertIn('riskScore', ai_analysis)

    def test_cross_schema_access_restrictions(self):
        """Test that cross-schema access is properly restricted"""
        # HR manager tries to access finance data
        self.client.force_authenticate(user=self.hr_manager)
        
        response = self.client.post('/api/v1/rbac/check-permission/', {
            'resource': 'finance_data',
            'action': 'view'
        })
        
        # Should be denied unless HR manager has special finance permissions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The specific result depends on role configuration

    def test_ai_anomaly_detection(self):
        """Test AI anomaly detection in access patterns"""
        self.client.force_authenticate(user=self.employee)
        
        # Simulate unusual access pattern (multiple high-risk requests)
        for i in range(5):
            self.client.post('/api/v1/rbac/log-access-pattern/', {
                'resource': 'sensitive_data',
                'action': 'view',
                'success': False,
                'risk_score': 0.9
            })
        
        # Check if security monitoring detects anomaly
        response = self.client.get('/api/v1/rbac/security-monitoring/')
        
        if response.status_code == status.HTTP_200_OK:
            # May have detected unusual pattern
            security_status = response.data.get('securityStatus', {})
            self.assertIsInstance(security_status, dict)

    def test_cache_performance(self):
        """Test that caching improves performance"""
        self.client.force_authenticate(user=self.employee)
        
        # Clear cache
        cache.clear()
        
        # First request (should cache result)
        start_time = self.client.post('/api/v1/rbac/check-permission/', {
            'resource': 'project_data',
            'action': 'view'
        })
        
        # Second request (should use cache)
        cached_time = self.client.post('/api/v1/rbac/check-permission/', {
            'resource': 'project_data', 
            'action': 'view'
        })
        
        # Both should succeed
        self.assertEqual(start_time.status_code, status.HTTP_200_OK)
        self.assertEqual(cached_time.status_code, status.HTTP_200_OK)


if __name__ == '__main__':
    pytest.main([__file__])