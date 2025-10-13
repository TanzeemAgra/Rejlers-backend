"""
User models for REJLERS Backend authentication system with RBAC
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
import uuid
import json


class Role(models.Model):
    """
    Role model for RBAC system - defines user roles and permissions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('role name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    permissions = models.JSONField(_('permissions'), default=dict)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # Business module permissions structure
    MODULE_PERMISSIONS = {
        'hr_management': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'projects_engineering': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'contracts_legal': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'finance_estimation': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'reporting_dashboards': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'hse_compliance': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'supply_chain': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'sales_engagement': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'rto_apc_consulting': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'user_management': ['view', 'create', 'edit', 'delete', 'manage_all'],
        'system_settings': ['view', 'edit', 'manage_all'],
        'ai_services': ['view', 'use', 'configure', 'manage_all']
    }
    
    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        
    def __str__(self):
        return self.name
    
    def has_permission(self, module, permission):
        """Check if role has specific permission for a module"""
        if not self.is_active:
            return False
        module_perms = self.permissions.get(module, [])
        return permission in module_perms or 'manage_all' in module_perms
    
    def add_permission(self, module, permission):
        """Add permission to role for a specific module"""
        if module not in self.permissions:
            self.permissions[module] = []
        if permission not in self.permissions[module]:
            self.permissions[module].append(permission)
    
    def remove_permission(self, module, permission):
        """Remove permission from role for a specific module"""
        if module in self.permissions and permission in self.permissions[module]:
            self.permissions[module].remove(permission)


class User(AbstractUser):
    """
    Enhanced User model with RBAC integration and business profile
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    
    # Role-based access control
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('user role')
    )
    
    # Business profile fields
    employee_id = models.CharField(_('employee ID'), max_length=20, unique=True, null=True, blank=True)
    company_name = models.CharField(_('company name'), max_length=200, default='Rejlers')
    job_title = models.CharField(_('job title'), max_length=150, default='AI Team Lead')
    department = models.CharField(_('department'), max_length=100, blank=True)
    position = models.CharField(_('position'), max_length=100, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    profile_image = models.ImageField(_('profile image'), upload_to='profiles/', null=True, blank=True)
    
    # Account status and metadata
    is_approved = models.BooleanField(_('approved'), default=False)
    is_verified = models.BooleanField(_('verified'), default=False)
    last_login_ip = models.GenericIPAddressField(_('last login IP'), null=True, blank=True)
    failed_login_attempts = models.PositiveSmallIntegerField(_('failed login attempts'), default=0)
    last_password_change = models.DateTimeField(_('last password change'), null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    # RBAC Methods
    def has_module_permission(self, module, permission):
        """Check if user has specific permission for a module"""
        if self.is_superuser:
            return True
        if not self.role or not self.role.is_active:
            return False
        return self.role.has_permission(module, permission)
    
    def get_accessible_modules(self):
        """Get list of modules user can access"""
        if self.is_superuser:
            return list(Role.MODULE_PERMISSIONS.keys())
        if not self.role:
            return []
        
        accessible = []
        for module in Role.MODULE_PERMISSIONS.keys():
            if self.has_module_permission(module, 'view'):
                accessible.append(module)
        return accessible
    
    def get_role_name(self):
        """Get user's role name"""
        if self.is_superuser:
            return 'Super Admin'
        return self.role.name if self.role else 'No Role'
    
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.has_module_permission('user_management', 'manage_all')
    
    def can_access_ai_services(self):
        """Check if user can access AI services"""
        return self.has_module_permission('ai_services', 'use')


class AuditLog(models.Model):
    """
    Audit log model for tracking user activities and system changes
    """
    ACTION_TYPES = [
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('view', _('View')),
        ('export', _('Export')),
        ('import', _('Import')),
        ('permission_change', _('Permission Change')),
        ('system_config', _('System Configuration'))
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(_('action'), max_length=20, choices=ACTION_TYPES)
    module = models.CharField(_('module'), max_length=50, blank=True)
    object_type = models.CharField(_('object type'), max_length=100, blank=True)
    object_id = models.CharField(_('object ID'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    additional_data = models.JSONField(_('additional data'), default=dict, blank=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['module', 'timestamp']),
        ]
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Anonymous'
        return f"{user_name} - {self.get_action_display()} - {self.timestamp}"
    
    @classmethod
    def log_activity(cls, user, action, module='', object_type='', object_id='', 
                     description='', ip_address=None, user_agent='', additional_data=None):
        """Create an audit log entry"""
        return cls.objects.create(
            user=user,
            action=action,
            module=module,
            object_type=object_type,
            object_id=str(object_id) if object_id else '',
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_data=additional_data or {}
        )