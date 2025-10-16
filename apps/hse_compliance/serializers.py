from rest_framework import serializers
from django.db.models import Avg, Count, Sum
from .models import (
    SafetyIncident, ComplianceChecklist, ChecklistAssessment, EnvironmentalMonitoring,
    RegulatoryFramework, ComplianceControl, ComplianceAssessment, 
    ControlAssessmentResult, AIComplianceInsight
)

# ============================================================================
# REGULATORY COMPLIANCE SERIALIZERS
# ============================================================================

class RegulatoryFrameworkSerializer(serializers.ModelSerializer):
    """Regulatory framework serializer with computed stats"""
    total_controls = serializers.SerializerMethodField()
    active_assessments = serializers.SerializerMethodField()
    avg_compliance_score = serializers.SerializerMethodField()
    
    class Meta:
        model = RegulatoryFramework
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_total_controls(self, obj):
        return obj.controls.filter(is_active=True).count()
    
    def get_active_assessments(self, obj):
        return obj.complianceassessment_set.filter(
            status__in=['IN_PROGRESS', 'UNDER_REVIEW']
        ).count()
    
    def get_avg_compliance_score(self, obj):
        avg_score = obj.complianceassessment_set.filter(
            status='COMPLIANT'
        ).aggregate(avg_score=Avg('compliance_percentage'))
        return round(avg_score['avg_score'] or 0, 2)

class ComplianceControlSerializer(serializers.ModelSerializer):
    """Compliance control serializer with framework details"""
    framework_name = serializers.CharField(source='framework.name', read_only=True)
    framework_code = serializers.CharField(source='framework.framework_code', read_only=True)
    
    class Meta:
        model = ComplianceControl
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ControlAssessmentResultSerializer(serializers.ModelSerializer):
    """Control assessment result serializer"""
    control_name = serializers.CharField(source='control.control_name', read_only=True)
    control_id = serializers.CharField(source='control.control_id', read_only=True)
    assessor_name = serializers.CharField(source='assessed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ControlAssessmentResult
        fields = '__all__'
        read_only_fields = ('assessed_date',)

class ComplianceAssessmentDetailSerializer(serializers.ModelSerializer):
    """Detailed compliance assessment serializer with results"""
    framework_name = serializers.CharField(source='framework.name', read_only=True)
    framework_code = serializers.CharField(source='framework.framework_code', read_only=True)
    lead_assessor_name = serializers.CharField(source='lead_assessor.get_full_name', read_only=True)
    
    control_results = ControlAssessmentResultSerializer(many=True, read_only=True)
    
    # Computed fields
    total_controls = serializers.SerializerMethodField()
    compliant_controls = serializers.SerializerMethodField()
    non_compliant_controls = serializers.SerializerMethodField()
    
    class Meta:
        model = ComplianceAssessment
        fields = '__all__'
        read_only_fields = ('assessment_id', 'created_at', 'updated_at')
    
    def get_total_controls(self, obj):
        return obj.control_results.count()
    
    def get_compliant_controls(self, obj):
        return obj.control_results.filter(compliance_status='COMPLIANT').count()
    
    def get_non_compliant_controls(self, obj):
        return obj.control_results.filter(compliance_status='NON_COMPLIANT').count()

class ComplianceAssessmentListSerializer(serializers.ModelSerializer):
    """Simplified compliance assessment serializer for lists"""
    framework_name = serializers.CharField(source='framework.name', read_only=True)
    framework_code = serializers.CharField(source='framework.framework_code', read_only=True)
    lead_assessor_name = serializers.CharField(source='lead_assessor.get_full_name', read_only=True)
    
    class Meta:
        model = ComplianceAssessment
        fields = [
            'assessment_id', 'title', 'framework_name', 'framework_code',
            'assessment_type', 'status', 'compliance_percentage', 'overall_score',
            'lead_assessor_name', 'planned_start_date', 'planned_end_date',
            'created_at', 'updated_at'
        ]

class AIComplianceInsightSerializer(serializers.ModelSerializer):
    """AI compliance insight serializer"""
    framework_name = serializers.CharField(source='framework.name', read_only=True)
    framework_code = serializers.CharField(source='framework.framework_code', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.get_full_name', read_only=True)
    
    # Related data counts
    affected_controls_count = serializers.SerializerMethodField()
    related_assessments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AIComplianceInsight
        fields = '__all__'
        read_only_fields = ('insight_id', 'created_at', 'updated_at')
    
    def get_affected_controls_count(self, obj):
        return obj.affected_controls.count()
    
    def get_related_assessments_count(self, obj):
        return obj.related_assessments.count()

# ============================================================================
# DASHBOARD AND ANALYTICS SERIALIZERS
# ============================================================================

class ComplianceDashboardSerializer(serializers.Serializer):
    """Compliance dashboard overview serializer"""
    framework_code = serializers.CharField()
    framework_name = serializers.CharField()
    compliance_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_controls = serializers.IntegerField()
    compliant_controls = serializers.IntegerField()
    non_compliant_controls = serializers.IntegerField()
    pending_controls = serializers.IntegerField()
    last_assessment_date = serializers.DateTimeField()
    next_assessment_due = serializers.DateField()
    risk_level = serializers.CharField()
    
    # Trend data
    compliance_trend = serializers.ListField(child=serializers.DictField())
    
    # Action items
    urgent_actions = serializers.IntegerField()
    overdue_actions = serializers.IntegerField()

class ComplianceMetricsSerializer(serializers.Serializer):
    """Overall compliance metrics serializer"""
    overall_compliance_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    frameworks_count = serializers.IntegerField()
    total_assessments = serializers.IntegerField()
    active_assessments = serializers.IntegerField()
    completed_assessments = serializers.IntegerField()
    
    # By framework breakdown
    framework_scores = serializers.ListField(child=serializers.DictField())
    
    # AI insights summary
    total_ai_insights = serializers.IntegerField()
    critical_insights = serializers.IntegerField()
    high_priority_insights = serializers.IntegerField()
    
    # Recent activity
    recent_assessments = ComplianceAssessmentListSerializer(many=True, read_only=True)
    recent_insights = AIComplianceInsightSerializer(many=True, read_only=True)

# ============================================================================
# LEGACY/EXISTING MODEL SERIALIZERS (Updated)
# ============================================================================

class SafetyIncidentSerializer(serializers.ModelSerializer):
    """Safety incident serializer"""
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    
    class Meta:
        model = SafetyIncident
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ComplianceChecklistSerializer(serializers.ModelSerializer):
    """Compliance checklist serializer with regulatory framework integration"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    regulatory_framework_name = serializers.CharField(source='regulatory_framework.name', read_only=True)
    
    class Meta:
        model = ComplianceChecklist
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ChecklistAssessmentSerializer(serializers.ModelSerializer):
    """Checklist-based compliance assessment serializer (legacy support)"""
    checklist_name = serializers.CharField(source='checklist.name', read_only=True)
    assessed_by_name = serializers.CharField(source='assessed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ChecklistAssessment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class EnvironmentalMonitoringSerializer(serializers.ModelSerializer):
    """Environmental monitoring serializer"""
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    
    class Meta:
        model = EnvironmentalMonitoring
        fields = '__all__'
        read_only_fields = ('created_at',)