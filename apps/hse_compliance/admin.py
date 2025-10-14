from django.contrib import admin
from .models import SafetyIncident, ComplianceChecklist, ComplianceAssessment, EnvironmentalMonitoring


@admin.register(SafetyIncident)
class SafetyIncidentAdmin(admin.ModelAdmin):
    list_display = ('incident_id', 'title', 'incident_type', 'severity', 'is_resolved', 'incident_date')
    list_filter = ('incident_type', 'severity', 'is_resolved', 'incident_date')
    search_fields = ('incident_id', 'title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ComplianceChecklist)
class ComplianceChecklistAdmin(admin.ModelAdmin):
    list_display = ('name', 'compliance_type', 'is_mandatory', 'frequency_days', 'is_active')
    list_filter = ('compliance_type', 'is_mandatory', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)


@admin.register(ComplianceAssessment)
class ComplianceAssessmentAdmin(admin.ModelAdmin):
    list_display = ('checklist', 'assessed_location', 'status', 'compliance_score', 'assessment_date')
    list_filter = ('status', 'checklist__compliance_type', 'assessment_date')
    search_fields = ('assessed_location', 'checklist__name')
    readonly_fields = ('created_at',)


@admin.register(EnvironmentalMonitoring)
class EnvironmentalMonitoringAdmin(admin.ModelAdmin):
    list_display = ('monitoring_type', 'location', 'measured_value', 'unit_of_measure', 'is_within_limits', 'measurement_date')
    list_filter = ('monitoring_type', 'is_within_limits', 'measurement_date')
    search_fields = ('location', 'notes')
    readonly_fields = ('created_at',)