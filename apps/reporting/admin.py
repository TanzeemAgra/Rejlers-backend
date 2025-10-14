from django.contrib import admin
from .models import ReportTemplate, GeneratedReport, KPI


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('report_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'template', 'status', 'start_date', 'end_date', 'generated_by')
    list_filter = ('status', 'template__report_type', 'created_at')
    search_fields = ('title', 'template__name')
    readonly_fields = ('created_at',)


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'current_value', 'target_value', 'measurement_unit', 'is_active')
    list_filter = ('category', 'is_active', 'owner')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')