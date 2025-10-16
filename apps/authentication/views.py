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


# =============================================================================
# COMPREHENSIVE RBAC API ENDPOINTS
# =============================================================================

class RoleListView(generics.ListAPIView):
    """
    Get all available roles in the system
    """
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter roles based on user permissions"""
        user = self.request.user
        if user.is_superuser or user.has_module_permission('user_management', 'manage_all'):
            return Role.objects.filter(is_active=True)
        else:
            # Regular users can only see their own role and basic roles
            return Role.objects.filter(
                Q(id=user.role.id) | Q(name__in=['Engineer', 'Employee', 'Client/External']),
                is_active=True
            )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Group roles by category
        roles_data = {
            'enterprise_roles': [],
            'functional_roles': [],
            'ai_powered_roles': [],
            'total_count': queryset.count()
        }
        
        enterprise_role_names = [
            'Super Admin', 'Chief Digital Officer (CDO)', 'CTO/IT Director', 
            'CFO/Finance Head', 'HR Director', 'Sales Director'
        ]
        
        functional_role_names = [
            'Engineering Lead', 'Engineer', 'QA/QC Engineer', 'Project Manager',
            'AI/ML Lead', 'Operations Manager', 'Procurement Manager', 'Client/External'
        ]
        
        ai_role_names = [
            'AI Assistant (System Role)', 'Digital Twin Bot', 'Compliance Bot', 'Insight Generator'
        ]
        
        for role in queryset:
            role_data = RoleSerializer(role).data
            
            if role.name in enterprise_role_names:
                roles_data['enterprise_roles'].append(role_data)
            elif role.name in functional_role_names:
                roles_data['functional_roles'].append(role_data)
            elif role.name in ai_role_names:
                roles_data['ai_powered_roles'].append(role_data)
        
        return Response(roles_data)


class RoleDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific role
    """
    queryset = Role.objects.filter(is_active=True)
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Add additional role information
        data = serializer.data
        data['user_count'] = User.objects.filter(role=instance, is_active=True).count()
        data['module_permissions_detail'] = {}
        
        # Detailed permissions breakdown
        for module, perms in instance.permissions.items():
            module_readable_name = module.replace('_', ' ').title()
            data['module_permissions_detail'][module_readable_name] = {
                'permissions': perms,
                'can_view': 'view' in perms or 'manage_all' in perms,
                'can_create': 'create' in perms or 'manage_all' in perms,
                'can_edit': 'edit' in perms or 'manage_all' in perms,
                'can_delete': 'delete' in perms or 'manage_all' in perms,
                'full_access': 'manage_all' in perms
            }
        
        return Response(data)


class UserRoleAssignmentView(APIView):
    """
    Assign or change user roles (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Assign role to user"""
        if not (request.user.is_superuser or request.user.has_module_permission('user_management', 'manage_all')):
            raise PermissionDenied("You don't have permission to assign roles")
        
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        
        if not user_id or not role_id:
            return Response(
                {'error': 'user_id and role_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(id=role_id, is_active=True)
            
            old_role = user.role.name if user.role else 'No Role'
            user.role = role
            user.save()
            
            # Log the role change
            AuditLog.log_activity(
                user=request.user,
                action='update',
                module='user_management',
                object_type='User Role',
                object_id=str(user.id),
                description=f'Changed user {user.get_full_name()} role from {old_role} to {role.name}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'message': f'Successfully assigned {role.name} role to {user.get_full_name()}',
                'user': UserSerializer(user).data
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserPermissionsView(APIView):
    """
    Get current user's permissions and accessible modules
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user permissions"""
        user = request.user
        
        permissions_data = {
            'user': {
                'id': str(user.id),
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.get_role_name(),
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff
            },
            'role_details': None,
            'module_permissions': {},
            'accessible_modules': user.get_accessible_modules(),
            'can_manage_users': user.can_manage_users(),
            'can_access_ai_services': user.can_access_ai_services()
        }
        
        if user.role:
            permissions_data['role_details'] = {
                'id': str(user.role.id),
                'name': user.role.name,
                'description': user.role.description,
                'permissions': user.role.permissions
            }
            
            # Detailed module permissions
            for module, available_perms in Role.MODULE_PERMISSIONS.items():
                user_perms = user.role.permissions.get(module, [])
                module_readable = module.replace('_', ' ').title()
                
                permissions_data['module_permissions'][module_readable] = {
                    'module_key': module,
                    'available_permissions': available_perms,
                    'user_permissions': user_perms,
                    'access_level': {
                        'can_view': user.has_module_permission(module, 'view'),
                        'can_create': user.has_module_permission(module, 'create'),
                        'can_edit': user.has_module_permission(module, 'edit'),
                        'can_delete': user.has_module_permission(module, 'delete'),
                        'full_access': user.has_module_permission(module, 'manage_all')
                    }
                }
        
        return Response(permissions_data)


class RoleUsersView(generics.ListAPIView):
    """
    Get all users with a specific role
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        role_id = self.kwargs['role_id']
        
        # Check permissions
        if not (self.request.user.is_superuser or 
                self.request.user.has_module_permission('user_management', 'view')):
            raise PermissionDenied("You don't have permission to view users")
        
        try:
            role = Role.objects.get(id=role_id, is_active=True)
            return User.objects.filter(role=role, is_active=True)
        except Role.DoesNotExist:
            return User.objects.none()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        role_id = self.kwargs['role_id']
        try:
            role = Role.objects.get(id=role_id, is_active=True)
            role_info = RoleSerializer(role).data
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'role': role_info,
            'users': serializer.data,
            'user_count': len(serializer.data)
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def rbac_system_info(request):
    """
    Get comprehensive RBAC system information
    """
    if not (request.user.is_superuser or 
            request.user.has_module_permission('user_management', 'view')):
        raise PermissionDenied("You don't have permission to view system information")
    
    # System statistics
    total_users = User.objects.filter(is_active=True).count()
    total_roles = Role.objects.filter(is_active=True).count()
    
    # Role distribution
    role_distribution = []
    for role in Role.objects.filter(is_active=True):
        user_count = User.objects.filter(role=role, is_active=True).count()
        role_distribution.append({
            'role_name': role.name,
            'user_count': user_count,
            'percentage': round((user_count / total_users * 100) if total_users > 0 else 0, 2)
        })
    
    # Recent role changes
    recent_role_changes = AuditLog.objects.filter(
        action='update',
        module='user_management',
        object_type='User Role'
    ).order_by('-timestamp')[:10]
    
    system_info = {
        'system_statistics': {
            'total_users': total_users,
            'total_roles': total_roles,
            'active_sessions': User.objects.filter(
                last_login__gte=timezone.now() - timedelta(hours=24)
            ).count(),
            'super_admins': User.objects.filter(is_superuser=True).count()
        },
        'role_categories': {
            'enterprise_roles': 6,
            'functional_roles': 8,
            'ai_powered_roles': 4
        },
        'role_distribution': role_distribution,
        'recent_role_changes': AuditLogSerializer(recent_role_changes, many=True).data,
        'module_permissions': {
            'available_modules': list(Role.MODULE_PERMISSIONS.keys()),
            'permission_levels': ['view', 'create', 'edit', 'delete', 'manage_all']
        }
    }
    
    return Response(system_info)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_module_permission(request):
    """
    Check if user has specific permission for a module
    """
    module = request.data.get('module')
    permission = request.data.get('permission')
    
    if not module or not permission:
        return Response(
            {'error': 'module and permission are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    has_permission = request.user.has_module_permission(module, permission)
    
    return Response({
        'user': request.user.get_full_name(),
        'module': module,
        'permission': permission,
        'has_permission': has_permission,
        'user_role': request.user.get_role_name()
    })