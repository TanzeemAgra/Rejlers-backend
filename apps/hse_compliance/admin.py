from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SafetyIncident, ComplianceChecklist, ChecklistAssessment, EnvironmentalMonitoring,
    RegulatoryFramework, ComplianceControl, ComplianceAssessment, 
    ControlAssessmentResult, AIComplianceInsight
)

# ============================================================================
# REGULATORY COMPLIANCE ADMIN INTERFACES
# ============================================================================

@admin.register(RegulatoryFramework)
class RegulatoryFrameworkAdmin(admin.ModelAdmin):
    list_display = ['framework_code', 'name', 'regulatory_body', 'version', 'is_active', 'last_updated']
    list_filter = ['framework_code', 'is_active', 'regulatory_body']
    search_fields = ['name', 'description', 'framework_code']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ComplianceControl)
class ComplianceControlAdmin(admin.ModelAdmin):
    list_display = ['control_id', 'control_name', 'framework', 'control_type', 'risk_level', 'is_mandatory', 'is_active']
    list_filter = ['framework', 'control_type', 'risk_level', 'is_mandatory', 'is_active']
    search_fields = ['control_id', 'control_name', 'description']
    readonly_fields = ['created_at', 'updated_at']

class ControlAssessmentResultInline(admin.TabularInline):
    model = ControlAssessmentResult
    extra = 0
    readonly_fields = ['assessed_date']
    fields = ['control', 'compliance_status', 'score', 'assessor_notes', 'requires_action']

@admin.register(ComplianceAssessment)
class ComplianceAssessmentAdmin(admin.ModelAdmin):
    list_display = ['assessment_id', 'title', 'framework', 'status', 'compliance_percentage', 'lead_assessor', 'created_at']
    list_filter = ['framework', 'status', 'assessment_type', 'lead_assessor']
    search_fields = ['title', 'scope_description', 'assessment_id']
    readonly_fields = ['assessment_id', 'created_at', 'updated_at']
    inlines = [ControlAssessmentResultInline]

@admin.register(AIComplianceInsight)
class AIComplianceInsightAdmin(admin.ModelAdmin):
    list_display = ['title', 'framework', 'insight_type', 'priority_level', 'confidence_score', 'is_acknowledged', 'created_at']
    list_filter = ['framework', 'insight_type', 'priority_level', 'is_acknowledged']
    search_fields = ['title', 'description', 'insight_id']
    readonly_fields = ['insight_id', 'created_at', 'updated_at']

# ============================================================================
# LEGACY/EXISTING MODEL ADMIN INTERFACES (Enhanced)
# ============================================================================

@admin.register(SafetyIncident)
class SafetyIncidentAdmin(admin.ModelAdmin):
    list_display = ['incident_id', 'title', 'incident_type', 'severity', 'is_resolved', 'incident_date', 'reported_by']
    list_filter = ['incident_type', 'severity', 'is_resolved', 'incident_date']
    search_fields = ['incident_id', 'title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'incident_date'

@admin.register(ComplianceChecklist)
class ComplianceChecklistAdmin(admin.ModelAdmin):
    list_display = ['name', 'compliance_type', 'regulatory_framework', 'is_mandatory', 'is_active', 'created_by']
    list_filter = ['compliance_type', 'regulatory_framework', 'is_mandatory', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChecklistAssessment)
class ChecklistAssessmentAdmin(admin.ModelAdmin):
    list_display = ['checklist', 'assessed_location', 'status', 'compliance_score', 'assessment_date', 'assessed_by']
    list_filter = ['status', 'checklist__compliance_type', 'assessment_date']
    search_fields = ['assessed_location', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'assessment_date'

@admin.register(EnvironmentalMonitoring)
class EnvironmentalMonitoringAdmin(admin.ModelAdmin):
    list_display = ['monitoring_type', 'location', 'measured_value', 'unit_of_measure', 'is_within_limits', 'measurement_date']
    list_filter = ['monitoring_type', 'is_within_limits', 'measurement_date']
    search_fields = ['location', 'notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'measurement_date'