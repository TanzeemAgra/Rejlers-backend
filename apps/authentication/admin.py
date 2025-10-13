"""
Django admin configuration for authentication app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, UserProfile, EmailVerificationToken, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin
    """
    list_display = [
        'email', 'username', 'get_full_name', 'company_name', 
        'job_title', 'email_verified', 'is_active', 'date_joined'
    ]
    list_filter = [
        'email_verified', 'is_active', 'is_staff', 'is_superuser',
        'company_size', 'industry', 'newsletter_subscribed', 'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'company_name']
    ordering = ['-date_joined']
    
    # Fieldsets for user detail view
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone',
                'profile_picture', 'bio'
            )
        }),
        ('Company info', {
            'fields': ('company_name', 'job_title', 'industry', 'company_size')
        }),
        ('Preferences', {
            'fields': ('newsletter_subscribed', 'marketing_emails')
        }),
        ('Account Status', {
            'fields': (
                'email_verified', 'email_verified_at', 'last_login_ip',
                'is_active', 'is_staff', 'is_superuser'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('groups', 'user_permissions'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2'
            ),
        }),
        ('Company info', {
            'classes': ('wide',),
            'fields': ('company_name', 'job_title', 'industry', 'company_size')
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'email_verified_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    actions = ['verify_email', 'send_welcome_email']
    
    def verify_email(self, request, queryset):
        for user in queryset:
            user.verify_email()
        self.message_user(request, f"Email verified for {queryset.count()} users.")
    verify_email.short_description = "Verify email for selected users"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User Profile admin
    """
    list_display = [
        'user', 'get_user_email', 'city', 'country', 
        'preferred_contact_method', 'profile_visibility', 'created_at'
    ]
    list_filter = [
        'preferred_contact_method', 'profile_visibility', 
        'country', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'city', 'country', 'address_line1'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Professional Links', {
            'fields': ('linkedin_url', 'website')
        }),
        ('Address Information', {
            'fields': (
                'address_line1', 'address_line2', 'city',
                'state_province', 'postal_code', 'country'
            )
        }),
        ('Interests', {
            'fields': ('services_of_interest', 'industries_of_interest')
        }),
        ('Preferences', {
            'fields': ('preferred_contact_method', 'profile_visibility')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['services_of_interest', 'industries_of_interest']
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Email Verification Token admin
    """
    list_display = [
        'user', 'get_user_email', 'token', 'expires_at', 
        'used', 'used_at', 'is_expired_display'
    ]
    list_filter = ['used', 'expires_at', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Token Info', {
            'fields': ('user', 'token', 'expires_at')
        }),
        ('Usage', {
            'fields': ('used', 'used_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'used_at']
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    get_user_email.admin_order_field = 'user__email'
    
    def is_expired_display(self, obj):
        is_expired = obj.is_expired()
        if is_expired:
            return format_html(
                '<span style="color: red;">Expired</span>'
            )
        return format_html(
            '<span style="color: green;">Valid</span>'
        )
    is_expired_display.short_description = 'Status'
    
    actions = ['mark_as_used']
    
    def mark_as_used(self, request, queryset):
        count = 0
        for token in queryset:
            if not token.used:
                token.mark_used()
                count += 1
        self.message_user(request, f"Marked {count} tokens as used.")
    mark_as_used.short_description = "Mark selected tokens as used"


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Password Reset Token admin
    """
    list_display = [
        'user', 'get_user_email', 'token', 'expires_at',
        'used', 'used_at', 'ip_address', 'is_expired_display'
    ]
    list_filter = ['used', 'expires_at', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'ip_address']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Token Info', {
            'fields': ('user', 'token', 'expires_at', 'ip_address')
        }),
        ('Usage', {
            'fields': ('used', 'used_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'used_at']
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    get_user_email.admin_order_field = 'user__email'
    
    def is_expired_display(self, obj):
        is_expired = obj.is_expired()
        if is_expired:
            return format_html(
                '<span style="color: red;">Expired</span>'
            )
        return format_html(
            '<span style="color: green;">Valid</span>'
        )
    is_expired_display.short_description = 'Status'
    
    actions = ['mark_as_used']
    
    def mark_as_used(self, request, queryset):
        count = 0
        for token in queryset:
            if not token.used:
                token.mark_used()
                count += 1
        self.message_user(request, f"Marked {count} tokens as used.")
    mark_as_used.short_description = "Mark selected tokens as used"


# Customize admin site header and title
admin.site.site_header = "REJLERS Administration"
admin.site.site_title = "REJLERS Admin"
admin.site.index_title = "Welcome to REJLERS Administration"