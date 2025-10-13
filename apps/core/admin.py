"""
Admin configuration for REJLERS Core models
"""

from django.contrib import admin
from .models import CompanyInfo, ServiceCategory, IndustrySector, ProjectType, Country, Office


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'full_name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'full_name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'full_name', 'tagline', 'description')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address_street', 'address_city', 'address_postal_code', 'address_country')
        }),
        ('Social Media', {
            'fields': ('linkedin_url', 'twitter_url', 'facebook_url'),
            'classes': ('collapse',)
        }),
        ('Business Information', {
            'fields': ('established_year', 'employee_count', 'annual_revenue')
        }),
        ('Branding', {
            'fields': ('logo', 'favicon')
        }),
        ('System Information', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color', 'order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']


@admin.register(IndustrySector)
class IndustrySectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color', 'order', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'complexity_level', 'duration_estimate', 'order', 'is_active']
    list_filter = ['complexity_level', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'flag_emoji', 'is_primary_market', 'is_active']
    list_filter = ['is_primary_market', 'is_active']
    search_fields = ['name', 'code']
    list_editable = ['is_primary_market', 'is_active']
    ordering = ['-is_primary_market', 'name']


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'employee_count', 'is_headquarters', 'is_active']
    list_filter = ['country', 'is_headquarters', 'is_active', 'created_at']
    search_fields = ['name', 'city', 'address', 'country__name']
    list_select_related = ['country']
    list_editable = ['is_headquarters', 'is_active']
    ordering = ['-is_headquarters', 'country__name', 'city']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'country', 'city')
        }),
        ('Address', {
            'fields': ('address', 'postal_code')
        }),
        ('Contact', {
            'fields': ('phone', 'email')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'description': 'Coordinates for mapping'
        }),
        ('Details', {
            'fields': ('employee_count', 'is_headquarters')
        }),
        ('System', {
            'fields': ('is_active',)
        })
    )