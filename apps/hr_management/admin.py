"""
HR Management Admin Configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Position, Employee, TimeOff, Performance


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department_type', 'manager', 'employee_count', 'is_active']
    list_filter = ['department_type', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    readonly_fields = ['employee_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'department_type', 'description', 'is_active')
        }),
        ('Organization', {
            'fields': ('parent_department', 'manager')
        }),
        ('Details', {
            'fields': ('budget_allocated', 'employee_count', 'location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'level', 'min_salary', 'max_salary', 'is_active']
    list_filter = ['department', 'level', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['department', 'level', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'department', 'level', 'is_active')
        }),
        ('Description', {
            'fields': ('description', 'requirements', 'responsibilities')
        }),
        ('Compensation', {
            'fields': ('min_salary', 'max_salary')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'get_full_name', 'department', 'position', 
        'employment_status', 'hire_date'
    ]
    list_filter = [
        'employment_type', 'employment_status', 'department', 
        'hire_date', 'created_at'
    ]
    search_fields = [
        'employee_id', 'user__first_name', 'user__last_name', 
        'user__email', 'skills'
    ]
    ordering = ['user__last_name', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at', 'years_of_service']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Employment Information', {
            'fields': (
                'employee_id', 'department', 'position', 'manager',
                'employment_type', 'employment_status', 'hire_date', 
                'termination_date', 'salary'
            )
        }),
        ('Personal Information', {
            'fields': (
                'date_of_birth', 'personal_email', 'phone_number',
                'emergency_contact_name', 'emergency_contact_phone'
            ),
            'classes': ('collapse',)
        }),
        ('Address', {
            'fields': (
                'address_line1', 'address_line2', 'city', 'state_province',
                'postal_code', 'country'
            ),
            'classes': ('collapse',)
        }),
        ('Work Information', {
            'fields': ('office_location', 'work_phone', 'skills', 'certifications')
        }),
        ('System', {
            'fields': ('years_of_service', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_full_name(self, obj):
        return obj.full_name
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__last_name'


@admin.register(TimeOff)
class TimeOffAdmin(admin.ModelAdmin):
    list_display = [
        'get_employee_name', 'time_off_type', 'start_date', 
        'end_date', 'days_requested', 'status', 'created_at'
    ]
    list_filter = ['time_off_type', 'status', 'start_date', 'created_at']
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'reason', 'comments'
    ]
    ordering = ['-start_date']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': (
                'employee', 'time_off_type', 'start_date', 'end_date',
                'days_requested', 'reason'
            )
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'comments')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_employee_name(self, obj):
        return obj.employee.full_name
    get_employee_name.short_description = 'Employee'
    get_employee_name.admin_order_field = 'employee__user__last_name'


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = [
        'get_employee_name', 'reviewer', 'review_period', 
        'review_end_date', 'overall_rating', 'completed_at'
    ]
    list_filter = ['review_period', 'review_end_date', 'overall_rating']
    search_fields = [
        'employee__user__first_name', 'employee__user__last_name',
        'reviewer__first_name', 'reviewer__last_name'
    ]
    ordering = ['-review_end_date']
    readonly_fields = ['created_at', 'updated_at', 'overall_rating']
    
    fieldsets = (
        ('Review Information', {
            'fields': (
                'employee', 'reviewer', 'review_period',
                'review_start_date', 'review_end_date'
            )
        }),
        ('Ratings', {
            'fields': (
                'technical_skills', 'communication', 'teamwork',
                'leadership', 'initiative', 'overall_rating'
            )
        }),
        ('Feedback', {
            'fields': (
                'strengths', 'areas_for_improvement', 'goals_next_period',
                'employee_comments'
            )
        }),
        ('Status', {
            'fields': ('completed_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_employee_name(self, obj):
        return obj.employee.full_name
    get_employee_name.short_description = 'Employee'
    get_employee_name.admin_order_field = 'employee__user__last_name'