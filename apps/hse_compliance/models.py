"""
HSE (Health, Safety, Environment) Compliance Module
Handles safety protocols, compliance tracking, and environmental monitoring for REJLERS
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField

User = get_user_model()

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
    """Compliance checklist templates"""
    COMPLIANCE_TYPES = [
        ('SAFETY', 'Safety Compliance'),
        ('ENVIRONMENTAL', 'Environmental Compliance'),
        ('REGULATORY', 'Regulatory Compliance'),
        ('INTERNAL', 'Internal Policy'),
    ]
    
    name = models.CharField(max_length=200)
    compliance_type = models.CharField(max_length=20, choices=COMPLIANCE_TYPES)
    description = models.TextField()
    
    checklist_items = JSONField(default=list)  # List of checklist items
    
    is_mandatory = models.BooleanField(default=True)
    frequency_days = models.IntegerField(default=30)  # How often to check (in days)
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.compliance_type})"

class ComplianceAssessment(models.Model):
    """Compliance assessment instances"""
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