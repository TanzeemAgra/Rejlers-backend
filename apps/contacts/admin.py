"""
Django admin configuration for contacts app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from .models import ContactInquiry, Newsletter, InquiryResponse, ContactList, EmailTemplate


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    """
    Contact Inquiry admin
    """
    list_display = [
        'get_full_name', 'email', 'company_name', 'inquiry_type',
        'status', 'priority', 'assigned_to', 'created_at', 'is_high_priority_display'
    ]
    list_filter = [
        'status', 'priority', 'inquiry_type', 'industry_sector',
        'project_timeline', 'estimated_budget', 'created_at'
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'company_name',
        'subject', 'message'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone',
                'company_name', 'job_title', 'company_size'
            )
        }),
        ('Inquiry Details', {
            'fields': (
                'inquiry_type', 'subject', 'message',
                'services_interested', 'industry_sector'
            )
        }),
        ('Project Information', {
            'fields': ('project_timeline', 'estimated_budget')
        }),
        ('Management', {
            'fields': ('status', 'priority', 'assigned_to', 'response_notes')
        }),
        ('Response Tracking', {
            'fields': ('responded_at', 'responded_by'),
            'classes': ('collapse',)
        }),
        ('Source Information', {
            'fields': (
                'source_page', 'utm_source', 'utm_medium', 'utm_campaign',
                'referrer', 'ip_address', 'user_agent'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'created_at', 'updated_at', 'responded_at', 'ip_address',
        'user_agent', 'referrer'
    ]
    filter_horizontal = ['services_interested']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'first_name'
    
    def is_high_priority_display(self, obj):
        if obj.is_high_priority:
            return format_html(
                '<span style="color: red; font-weight: bold;">HIGH</span>'
            )
        return ''
    is_high_priority_display.short_description = 'High Priority'
    
    actions = ['mark_in_progress', 'mark_resolved', 'assign_to_me']
    
    def mark_in_progress(self, request, queryset):
        count = queryset.update(status='in_progress')
        self.message_user(request, f"Marked {count} inquiries as in progress.")
    mark_in_progress.short_description = "Mark selected inquiries as in progress"
    
    def mark_resolved(self, request, queryset):
        count = queryset.update(status='resolved')
        self.message_user(request, f"Marked {count} inquiries as resolved.")
    mark_resolved.short_description = "Mark selected inquiries as resolved"
    
    def assign_to_me(self, request, queryset):
        count = queryset.update(assigned_to=request.user)
        self.message_user(request, f"Assigned {count} inquiries to you.")
    assign_to_me.short_description = "Assign selected inquiries to me"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Newsletter admin
    """
    list_display = [
        'email', 'get_full_name', 'frequency', 'is_active',
        'confirmed', 'created_at'
    ]
    list_filter = [
        'is_active', 'confirmed', 'frequency', 'source', 'created_at'
    ]
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Preferences', {
            'fields': ('interests', 'frequency')
        }),
        ('Status', {
            'fields': ('is_active', 'confirmed', 'confirmed_at', 'unsubscribed_at')
        }),
        ('Source Tracking', {
            'fields': ('source', 'utm_source', 'utm_medium', 'utm_campaign'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'unsubscribed_at']
    filter_horizontal = ['interests']
    
    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or 'Anonymous'
    get_full_name.short_description = 'Name'
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"Activated {count} subscriptions.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {count} subscriptions.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"


class InquiryResponseInline(admin.TabularInline):
    """
    Inline for inquiry responses
    """
    model = InquiryResponse
    extra = 0
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_active=True)


@admin.register(InquiryResponse)
class InquiryResponseAdmin(admin.ModelAdmin):
    """
    Inquiry Response admin
    """
    list_display = [
        'inquiry', 'responder', 'response_method', 'subject',
        'follow_up_required', 'created_at'
    ]
    list_filter = [
        'response_method', 'follow_up_required', 'email_sent',
        'created_at', 'responder'
    ]
    search_fields = ['inquiry__subject', 'subject', 'message']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Response Details', {
            'fields': ('inquiry', 'response_method', 'subject', 'message')
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_date', 'follow_up_notes')
        }),
        ('Email Tracking', {
            'fields': ('email_sent', 'email_opened', 'email_clicked'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    """
    Contact List admin
    """
    list_display = [
        'name', 'get_total_contacts', 'is_active', 'created_by', 'created_at'
    ]
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        ('List Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Contacts', {
            'fields': ('contacts', 'newsletter_subscribers')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    filter_horizontal = ['contacts', 'newsletter_subscribers']
    
    def get_total_contacts(self, obj):
        return obj.total_contacts
    get_total_contacts.short_description = 'Total Contacts'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """
    Email Template admin
    """
    list_display = [
        'name', 'template_type', 'is_active', 'created_by', 'created_at'
    ]
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'body']
    ordering = ['template_type', 'name']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'body'),
            'description': 'Use {{ variable_name }} for dynamic content'
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Add the ContactInquiry inline to the ContactInquiryAdmin
ContactInquiryAdmin.inlines = [InquiryResponseInline]