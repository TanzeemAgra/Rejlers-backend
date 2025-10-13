"""
Serializers for REJLERS RBAC authentication system
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import User, Role, AuditLog


class RoleSerializer(serializers.ModelSerializer):
    """
    Role serializer for RBAC system
    """
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'permissions', 
            'is_active', 'user_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_count']
    
    def get_user_count(self, obj):
        """Get number of users with this role"""
        return obj.users.count()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Enhanced user registration serializer with RBAC
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'employee_id', 'company_name', 'job_title', 'department', 'position', 'phone_number',
            'password', 'password_confirm', 'role', 'role_name'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': _('Password fields do not match.')
            })
        attrs.pop('password_confirm', None)
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('User with this email already exists.'))
        return value
    
    def validate_employee_id(self, value):
        """Validate employee ID uniqueness if provided"""
        if value and User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError(_('User with this employee ID already exists.'))
        return value
    
    def create(self, validated_data):
        """Create new user with hashed password"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Log user creation
        AuditLog.log_activity(
            user=None,
            action='create',
            module='user_management',
            object_type='User',
            object_id=user.id,
            description=f'New user registered: {user.email}'
        )
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Enhanced user serializer with RBAC information
    """
    role_name = serializers.CharField(source='role.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    accessible_modules = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'employee_id', 'company_name', 'job_title', 'department', 'position', 'phone_number', 'profile_image',
            'role', 'role_name', 'accessible_modules',
            'is_active', 'is_approved', 'is_verified', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'created_at', 'updated_at',
            'full_name', 'role_name', 'accessible_modules'
        ]
    
    def get_accessible_modules(self, obj):
        """Get list of modules user can access"""
        return obj.get_accessible_modules()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Enhanced JWT token serializer with RBAC information
    """
    username_field = 'email'
    
    def validate(self, attrs):
        """Enhanced validation with audit logging"""
        data = super().validate(attrs)
        
        # Add user information to token response
        user = self.user
        data.update({
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name(),
            'role': user.get_role_name(),
            'accessible_modules': user.get_accessible_modules(),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })
        
        # Log successful login
        AuditLog.log_activity(
            user=user,
            action='login',
            description=f'User logged in successfully'
        )
        
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Password change serializer
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Old password is incorrect.'))
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _('New password fields do not match.')
            })
        return attrs
    
    def save(self):
        """Update user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.last_password_change = timezone.now()
        user.save()
        
        # Log password change
        AuditLog.log_activity(
            user=user,
            action='update',
            module='user_management',
            object_type='User',
            object_id=user.id,
            description='Password changed successfully'
        )
        
        return user


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Audit log serializer for tracking user activities
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'user_name', 'action', 'module',
            'object_type', 'object_id', 'description', 'ip_address',
            'user_agent', 'additional_data', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp', 'user_email', 'user_name']


class UserPermissionSerializer(serializers.Serializer):
    """
    Serializer for checking user permissions
    """
    module = serializers.CharField()
    permission = serializers.CharField()
    
    def validate_module(self, value):
        """Validate module name"""
        if value not in Role.MODULE_PERMISSIONS:
            raise serializers.ValidationError(_('Invalid module name.'))
        return value
    
    def validate_permission(self, value):
        """Validate permission name"""
        valid_permissions = ['view', 'create', 'edit', 'delete', 'manage_all', 'use', 'configure']
        if value not in valid_permissions:
            raise serializers.ValidationError(_('Invalid permission name.'))
        return value