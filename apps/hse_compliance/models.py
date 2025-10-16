"""
HSE (Health, Safety, Environment) Compliance Module
Enhanced with Regulatory Compliance Integration for Enterprise-Grade Compliance Management
Handles safety protocols, compliance tracking, environmental monitoring, and multi-regulatory frameworks
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

User = get_user_model()

# ============================================================================
# REGULATORY COMPLIANCE FRAMEWORK MODELS
# ============================================================================

class RegulatoryFramework(models.Model):
    """Master table for regulatory frameworks"""
    FRAMEWORK_TYPES = [
        ('ISO_27001', 'ISO 27001 - Information Security Management'),
        ('API_Q1_Q2', 'API Q1/Q2 - Oil & Gas Quality Standards'),
        ('IEC_62443', 'IEC 62443 - Industrial Network Security'),
        ('NIST_SP_800_53', 'NIST SP 800-53 - Access & Role Controls'),
        ('GDPR_UAE', 'GDPR/UAE Data Protection Laws'),
    ]
    
    framework_code = models.CharField(max_length=20, choices=FRAMEWORK_TYPES, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    version = models.CharField(max_length=50, default='1.0')
    
    # Compliance scoring weights
    base_score_weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('20.00'))
    
    # Framework metadata
    regulatory_body = models.CharField(max_length=200)
    last_updated = models.DateField()
    next_review_date = models.DateField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['framework_code']
    
    def __str__(self):
        return f"{self.framework_code} - {self.name}"

class ComplianceControl(models.Model):
    """Individual compliance controls within regulatory frameworks"""
    CONTROL_TYPES = [
        ('TECHNICAL', 'Technical Control'),
        ('ADMINISTRATIVE', 'Administrative Control'),
        ('PHYSICAL', 'Physical Control'),
        ('PROCEDURAL', 'Procedural Control'),
    ]
    
    RISK_LEVELS = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ]
    
    framework = models.ForeignKey(RegulatoryFramework, on_delete=models.CASCADE, related_name='controls')
    
    control_id = models.CharField(max_length=50)  # e.g., "A.5.1.1" for ISO 27001
    control_name = models.CharField(max_length=200)
    description = models.TextField()
    
    control_type = models.CharField(max_length=20, choices=CONTROL_TYPES)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='MEDIUM')
    
    # Implementation details
    implementation_guidance = models.TextField(blank=True)
    evidence_requirements = JSONField(default=list)  # List of required evidence types
    
    # Scoring and weighting
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.00'))
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    
    is_mandatory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['framework', 'control_id']
        ordering = ['framework', 'control_id']
    
    def __str__(self):
        return f"{self.framework.framework_code} - {self.control_id}: {self.control_name}"

class ComplianceAssessment(models.Model):
    """Compliance assessment instances with enhanced regulatory tracking"""
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('COMPLIANT', 'Compliant'),
        ('NON_COMPLIANT', 'Non-Compliant'),
        ('NEEDS_IMPROVEMENT', 'Needs Improvement'),
        ('UNDER_REVIEW', 'Under Review'),
    ]
    
    ASSESSMENT_TYPES = [
        ('INTERNAL_AUDIT', 'Internal Audit'),
        ('EXTERNAL_AUDIT', 'External Audit'),
        ('SELF_ASSESSMENT', 'Self Assessment'),
        ('THIRD_PARTY', 'Third Party Assessment'),
        ('AI_AUTOMATED', 'AI Automated Assessment'),
    ]
    
    assessment_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    framework = models.ForeignKey(RegulatoryFramework, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    
    # Assessment scope and details
    scope_description = models.TextField()
    assessment_criteria = JSONField(default=dict)
    
    # Dates and timeline
    planned_start_date = models.DateTimeField()
    planned_end_date = models.DateTimeField()
    actual_start_date = models.DateTimeField(null=True, blank=True)
    actual_end_date = models.DateTimeField(null=True, blank=True)
    
    # Assessment team
    lead_assessor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='led_assessments')
    assessment_team = models.ManyToManyField(User, related_name='team_assessments', blank=True)
    
    # Results and scoring
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    compliance_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    
    # Assessment metadata
    executive_summary = models.TextField(blank=True)
    findings = JSONField(default=list)  # List of findings with severity, description, recommendations
    action_items = JSONField(default=list)  # List of action items with owners, due dates
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.framework.framework_code} Assessment - {self.title}"

class ControlAssessmentResult(models.Model):
    """Individual control assessment results"""
    COMPLIANCE_STATUS = [
        ('COMPLIANT', 'Fully Compliant'),
        ('PARTIALLY_COMPLIANT', 'Partially Compliant'),
        ('NON_COMPLIANT', 'Non-Compliant'),
        ('NOT_APPLICABLE', 'Not Applicable'),
        ('NOT_ASSESSED', 'Not Assessed'),
    ]
    
    assessment = models.ForeignKey(ComplianceAssessment, on_delete=models.CASCADE, related_name='control_results')
    control = models.ForeignKey(ComplianceControl, on_delete=models.CASCADE)
    
    compliance_status = models.CharField(max_length=25, choices=COMPLIANCE_STATUS)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Assessment details
    evidence_provided = JSONField(default=list)  # List of evidence documents/links
    assessor_notes = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Risk and impact assessment
    risk_rating = models.CharField(max_length=10, choices=ComplianceControl.RISK_LEVELS, blank=True)
    business_impact = models.TextField(blank=True)
    
    # Remediation tracking
    requires_action = models.BooleanField(default=False)
    action_plan = models.TextField(blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    
    assessed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    assessed_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['assessment', 'control']
        ordering = ['control__control_id']
    
    def __str__(self):
        return f"{self.assessment.assessment_id} - {self.control.control_id} ({self.compliance_status})"

class AIComplianceInsight(models.Model):
    """AI-generated compliance insights and predictions"""
    INSIGHT_TYPES = [
        ('RISK_PREDICTION', 'Risk Prediction'),
        ('COMPLIANCE_TREND', 'Compliance Trend Analysis'),
        ('REMEDIATION_SUGGESTION', 'Remediation Suggestion'),
        ('POLICY_RECOMMENDATION', 'Policy Recommendation'),
        ('AUDIT_PREPARATION', 'Audit Preparation'),
        ('REGULATORY_CHANGE', 'Regulatory Change Impact'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority'),
        ('CRITICAL', 'Critical Priority'),
    ]
    
    insight_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    framework = models.ForeignKey(RegulatoryFramework, on_delete=models.CASCADE, related_name='ai_insights')
    
    insight_type = models.CharField(max_length=25, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # AI analysis details
    confidence_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    priority_level = models.CharField(max_length=10, choices=PRIORITY_LEVELS)
    
    # Recommendations and actions
    recommendations = JSONField(default=list)
    suggested_actions = JSONField(default=list)
    
    # Impact assessment
    potential_impact = models.TextField()
    estimated_effort = models.CharField(max_length=100, blank=True)  # e.g., "2-4 weeks", "Low effort"
    
    # Metadata
    affected_controls = models.ManyToManyField(ComplianceControl, blank=True)
    related_assessments = models.ManyToManyField(ComplianceAssessment, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority_level', '-confidence_score', '-created_at']
    
    def __str__(self):
        return f"{self.framework.framework_code} - {self.title} (Confidence: {self.confidence_score}%)"

# ============================================================================
# EXISTING MODELS (Enhanced)
# ============================================================================

class SafetyIncident(models.Model):
    """Safety incident tracking"""
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    INCIDENT_TYPES = [
        ('INJURY', 'Personal Injury'),
        ('PROPERTY', 'Property Damage'),
        ('ENVIRONMENTAL', 'Environmental'),
        ('NEAR_MISS', 'Near Miss'),
        ('EQUIPMENT', 'Equipment Failure'),
    ]
    
    incident_id = models.CharField(max_length=50, unique=True)
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    
    incident_date = models.DateTimeField()
    reported_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.incident_id} - {self.title}"

class ComplianceChecklist(models.Model):
    """Enhanced compliance checklist templates with regulatory framework integration"""
    COMPLIANCE_TYPES = [
        ('SAFETY', 'Safety Compliance'),
        ('ENVIRONMENTAL', 'Environmental Compliance'),
        ('REGULATORY', 'Regulatory Compliance'),
        ('INTERNAL', 'Internal Policy'),
        ('ISO_27001', 'ISO 27001 Information Security'),
        ('API_Q1_Q2', 'API Q1/Q2 Oil & Gas Quality'),
        ('IEC_62443', 'IEC 62443 Industrial Security'),
        ('NIST_SP_800_53', 'NIST SP 800-53 Access Controls'),
        ('GDPR_UAE', 'GDPR/UAE Data Protection'),
    ]
    
    name = models.CharField(max_length=200)
    compliance_type = models.CharField(max_length=20, choices=COMPLIANCE_TYPES)
    description = models.TextField()
    
    # Link to regulatory framework (optional for backward compatibility)
    regulatory_framework = models.ForeignKey(
        RegulatoryFramework, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='checklists'
    )
    
    checklist_items = JSONField(default=list)  # List of checklist items
    
    is_mandatory = models.BooleanField(default=True)
    frequency_days = models.IntegerField(default=30)  # How often to check (in days)
    
    # Enhanced metadata
    version = models.CharField(max_length=20, default='1.0')
    tags = JSONField(default=list)  # Tags for categorization
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.compliance_type})"

class ChecklistAssessment(models.Model):
    """Checklist-based compliance assessment instances (legacy support)"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('NON_COMPLIANT', 'Non-Compliant'),
    ]
    
    checklist = models.ForeignKey(ComplianceChecklist, on_delete=models.PROTECT)
    assessed_location = models.CharField(max_length=200)
    
    assessment_data = JSONField(default=dict)  # Results of checklist items
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    assessed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    assessment_date = models.DateTimeField()
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.checklist.name} - {self.assessed_location} - {self.assessment_date.date()}"

class EnvironmentalMonitoring(models.Model):
    """Environmental monitoring data"""
    MONITORING_TYPES = [
        ('AIR_QUALITY', 'Air Quality'),
        ('WATER_QUALITY', 'Water Quality'),
        ('NOISE_LEVEL', 'Noise Level'),
        ('WASTE_TRACKING', 'Waste Tracking'),
        ('ENERGY_CONSUMPTION', 'Energy Consumption'),
    ]
    
    monitoring_type = models.CharField(max_length=20, choices=MONITORING_TYPES)
    location = models.CharField(max_length=200)
    
    measured_value = models.DecimalField(max_digits=10, decimal_places=3)
    unit_of_measure = models.CharField(max_length=50)
    
    threshold_limit = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    is_within_limits = models.BooleanField(default=True)
    
    measurement_date = models.DateTimeField()
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.monitoring_type} at {self.location} - {self.measured_value} {self.unit_of_measure}"