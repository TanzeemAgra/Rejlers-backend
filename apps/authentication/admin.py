"""
Django admin configuration for authentication app with RBAC
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import User, Role, AuditLog


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin interface for Role model
    """
    list_display = ['name', 'description', 'is_active', 'user_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Permissions'), {
            'fields': ('permissions',),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_count(self, obj):
        """Display number of users with this role"""
        count = obj.users.count()
        if count > 0:
            url = reverse('admin:authentication_user_changelist')
            return format_html(
                '<a href="{}?role__id__exact={}">{} users</a>',
                url, obj.id, count
            )
        return "0 users"
    user_count.short_description = _('Users')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Enhanced User admin with RBAC features
    """
    list_display = [
        'email', 'username', 'get_full_name', 'company_name', 'job_title', 'role', 'department', 
        'is_approved', 'is_verified', 'is_active', 'date_joined'
    ]
    list_filter = [
        'role', 'department', 'is_approved', 'is_verified', 
        'is_active', 'is_staff', 'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'employee_id']
    readonly_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_image')
        }),
        (_('Business Profile'), {
            'fields': ('employee_id', 'company_name', 'job_title', 'department', 'position', 'role')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'is_verified', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'last_password_change')
        }),
        (_('Security'), {
            'fields': ('failed_login_attempts', 'last_login_ip'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    
    ordering = ['email']
    
    def get_full_name(self, obj):
        """Display user's full name"""
        return obj.get_full_name() or obj.username
    get_full_name.short_description = _('Full Name')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for Audit Log
    """
    list_display = [
        'user', 'action', 'module', 'object_type', 
        'description_short', 'ip_address', 'timestamp'
    ]
    list_filter = [
        'action', 'module', 'object_type', 'timestamp'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'description', 'object_id'
    ]
    readonly_fields = ['id', 'timestamp']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'action', 'module', 'object_type', 'object_id')
        }),
        (_('Details'), {
            'fields': ('description', 'additional_data')
        }),
        (_('Request Info'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('id', 'timestamp'),
            'classes': ('collapse',)
        })
    )
    
    def description_short(self, obj):
        """Display shortened description"""
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description or '-'
    description_short.short_description = _('Description')
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make audit logs read-only"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs"""
        return False


# Customize admin site headers
admin.site.site_header = "REJLERS RBAC Administration"
admin.site.site_title = "REJLERS Admin"
admin.site.index_title = "Welcome to REJLERS Administration Portal"