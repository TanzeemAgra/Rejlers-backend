"""
Contracts & Legal Module
Handles contract management, legal documents, and compliance for REJLERS
"""
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Contract(models.Model):
    """Contract management"""
    CONTRACT_TYPES = [
        ('SERVICE', 'Service Agreement'),
        ('SUPPLY', 'Supply Contract'),
        ('EMPLOYMENT', 'Employment Contract'),
        ('NDA', 'Non-Disclosure Agreement'),
        ('PARTNERSHIP', 'Partnership Agreement'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Approval'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('TERMINATED', 'Terminated'),
    ]
    
    contract_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    client_name = models.CharField(max_length=200)
    contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name='managed_contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contract_id} - {self.title}"

class LegalDocument(models.Model):
    """Legal documents and templates"""
    DOCUMENT_TYPES = [
        ('CONTRACT', 'Contract'),
        ('POLICY', 'Policy Document'),
        ('COMPLIANCE', 'Compliance Document'),
        ('CERTIFICATE', 'Certificate'),
    ]
    
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    content = models.TextField()
    version = models.CharField(max_length=10, default='1.0')
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} (v{self.version})"