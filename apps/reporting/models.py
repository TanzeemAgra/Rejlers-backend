"""
Reporting & Analytics Module
Handles business intelligence, KPIs, and reporting for REJLERS
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField

User = get_user_model()

class ReportTemplate(models.Model):
    """Report template definitions"""
    REPORT_TYPES = [
        ('FINANCIAL', 'Financial Report'),
        ('PROJECT', 'Project Status Report'),
        ('HR', 'HR Analytics'),
        ('OPERATIONAL', 'Operational Report'),
        ('COMPLIANCE', 'Compliance Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    
    template_config = JSONField(default=dict)  # JSON structure for report configuration
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.report_type})"

class GeneratedReport(models.Model):
    """Generated report instances"""
    STATUS_CHOICES = [
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    report_data = JSONField(default=dict)  # Actual report data
    file_path = models.CharField(max_length=500, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GENERATING')
    generated_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.created_at.date()}"

class KPI(models.Model):
    """Key Performance Indicators"""
    KPI_CATEGORIES = [
        ('FINANCIAL', 'Financial KPI'),
        ('PROJECT', 'Project KPI'),
        ('HR', 'HR KPI'),
        ('OPERATIONAL', 'Operational KPI'),
        ('SAFETY', 'Safety KPI'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=KPI_CATEGORIES)
    description = models.TextField()
    
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    measurement_unit = models.CharField(max_length=50)
    
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.current_value}/{self.target_value} {self.measurement_unit}"