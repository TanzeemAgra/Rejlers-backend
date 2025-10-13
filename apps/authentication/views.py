"""
Enhanced API views for REJLERS RBAC authentication system
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import uuid

from .models import User, Role, AuditLog
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    RoleSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    AuditLogSerializer,
    UserPermissionSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration API endpoint
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': _('User registered successfully. Please wait for admin approval.'),
            'user_id': str(user.id),
            'email': user.email
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Enhanced JWT login with RBAC information
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Update user login metadata
            email = request.data.get('email')
            if email:
                try:
                    user = User.objects.get(email=email)
                    user.last_login_ip = self.get_client_ip(request)
                    user.failed_login_attempts = 0
                    user.save(update_fields=['last_login_ip', 'failed_login_attempts'])
                except User.DoesNotExist:
                    pass
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile management
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def perform_update(self, serializer):
        user = serializer.save()
        
        # Log profile update
        AuditLog.log_activity(
            user=self.request.user,
            action='update',
            module='user_management',
            object_type='User',
            object_id=user.id,
            description='Profile updated successfully',
            ip_address=self.get_client_ip()
        )
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ChangePasswordView(generics.UpdateAPIView):
    """
    Password change endpoint
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': _('Password changed successfully.')
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Logout endpoint with token blacklisting
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Log logout activity
            AuditLog.log_activity(
                user=request.user,
                action='logout',
                description='User logged out successfully'
            )
            
            return Response({
                'message': _('Logout successful.')
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                'error': _('Invalid token.')
            }, status=status.HTTP_400_BAD_REQUEST)


# RBAC Management Views

class RoleListView(generics.ListCreateAPIView):
    """
    Role management - list and create roles
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only users with user management permissions can access roles
        if not self.request.user.has_module_permission('user_management', 'view'):
            return Role.objects.none()
        return Role.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        # Only users with manage_all permission can create roles
        if not self.request.user.has_module_permission('user_management', 'manage_all'):
            raise PermissionDenied(_('You do not have permission to create roles.'))
        
        role = serializer.save()
        
        # Log role creation
        AuditLog.log_activity(
            user=self.request.user,
            action='create',
            module='user_management',
            object_type='Role',
            object_id=role.id,
            description=f'New role created: {role.name}'
        )


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Role management - retrieve, update, delete specific role
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.has_module_permission('user_management', 'view'):
            return Role.objects.none()
        return Role.objects.filter(is_active=True)
    
    def perform_update(self, serializer):
        if not self.request.user.has_module_permission('user_management', 'edit'):
            raise PermissionDenied(_('You do not have permission to edit roles.'))
        
        role = serializer.save()
        
        # Log role update
        AuditLog.log_activity(
            user=self.request.user,
            action='update',
            module='user_management',
            object_type='Role',
            object_id=role.id,
            description=f'Role updated: {role.name}'
        )
    
    def perform_destroy(self, instance):
        if not self.request.user.has_module_permission('user_management', 'delete'):
            raise PermissionDenied(_('You do not have permission to delete roles.'))
        
        # Soft delete by deactivating
        instance.is_active = False
        instance.save()
        
        # Log role deletion
        AuditLog.log_activity(
            user=self.request.user,
            action='delete',
            module='user_management',
            object_type='Role',
            object_id=instance.id,
            description=f'Role deactivated: {instance.name}'
        )


class UserListView(generics.ListAPIView):
    """
    User list for administrators
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.has_module_permission('user_management', 'view'):
            return User.objects.none()
        
        queryset = User.objects.filter(is_active=True).select_related('role')
        
        # Filter by search query if provided
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        return queryset


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    User detail management for administrators
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.has_module_permission('user_management', 'view'):
            return User.objects.none()
        return User.objects.filter(is_active=True)
    
    def perform_update(self, serializer):
        if not self.request.user.has_module_permission('user_management', 'edit'):
            raise PermissionDenied(_('You do not have permission to edit users.'))
        
        user = serializer.save()
        
        # Log user update
        AuditLog.log_activity(
            user=self.request.user,
            action='update',
            module='user_management',
            object_type='User',
            object_id=user.id,
            description=f'User updated: {user.email}'
        )


class UserPermissionCheckView(APIView):
    """
    Check user permissions for specific modules and actions
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = UserPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        module = serializer.validated_data['module']
        permission = serializer.validated_data['permission']
        
        has_permission = request.user.has_module_permission(module, permission)
        
        return Response({
            'user_id': str(request.user.id),
            'module': module,
            'permission': permission,
            'has_permission': has_permission,
            'role': request.user.get_role_name()
        })


class AuditLogListView(generics.ListAPIView):
    """
    Audit log listing for administrators
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.has_module_permission('system_settings', 'view'):
            return AuditLog.objects.none()
        
        queryset = AuditLog.objects.select_related('user').order_by('-timestamp')
        
        # Filter by user if provided
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by action if provided
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by module if provided
        module = self.request.query_params.get('module', None)
        if module:
            queryset = queryset.filter(module=module)
        
        return queryset[:100]  # Limit to recent 100 entries


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_data(request):
    """
    Get user-specific dashboard data based on role and permissions
    """
    user = request.user
    
    # Get accessible modules
    accessible_modules = user.get_accessible_modules()
    
    # Basic user info
    dashboard_data = {
        'user': {
            'id': str(user.id),
            'name': user.get_full_name(),
            'email': user.email,
            'role': user.get_role_name(),
            'employee_id': user.employee_id,
            'department': user.department,
            'position': user.position,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        },
        'accessible_modules': accessible_modules,
        'permissions': {}
    }
    
    # Get permissions for each accessible module
    for module in accessible_modules:
        module_permissions = []
        for permission in ['view', 'create', 'edit', 'delete', 'manage_all']:
            if user.has_module_permission(module, permission):
                module_permissions.append(permission)
        dashboard_data['permissions'][module] = module_permissions
    
    # Get recent activities if user can view audit logs
    if user.has_module_permission('system_settings', 'view'):
        recent_activities = AuditLog.objects.filter(
            user=user
        ).order_by('-timestamp')[:5]
        
        dashboard_data['recent_activities'] = AuditLogSerializer(
            recent_activities, many=True
        ).data
    
    # Log dashboard access
    AuditLog.log_activity(
        user=user,
        action='view',
        module='reporting_dashboards',
        description='Accessed dashboard'
    )
    
    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Simple health check endpoint
    """
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'message': 'REJLERS RBAC API is running'
    })