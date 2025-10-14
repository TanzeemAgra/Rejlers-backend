"""
Sales & Marketing Module  
Handles lead management, sales pipeline, and marketing campaigns for REJLERS
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField

User = get_user_model()

class Lead(models.Model):
    """Sales lead management"""
    LEAD_SOURCES = [
        ('WEBSITE', 'Website'),
        ('REFERRAL', 'Referral'),
        ('COLD_CALL', 'Cold Call'),
        ('EMAIL_CAMPAIGN', 'Email Campaign'),
        ('TRADE_SHOW', 'Trade Show'),
        ('SOCIAL_MEDIA', 'Social Media'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONTACTED', 'Contacted'),
        ('QUALIFIED', 'Qualified'),
        ('PROPOSAL', 'Proposal Sent'),
        ('NEGOTIATION', 'Negotiation'),
        ('WON', 'Won'),
        ('LOST', 'Lost'),
    ]
    
    lead_id = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    lead_source = models.CharField(max_length=20, choices=LEAD_SOURCES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='NEW')
    
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    probability = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 0-100%
    
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.lead_id} - {self.company_name}"

class Opportunity(models.Model):
    """Sales opportunity tracking"""
    STAGES = [
        ('PROSPECTING', 'Prospecting'),
        ('QUALIFICATION', 'Qualification'),
        ('NEEDS_ANALYSIS', 'Needs Analysis'),
        ('PROPOSAL', 'Proposal/Quote'),
        ('NEGOTIATION', 'Negotiation'),
        ('CLOSED_WON', 'Closed Won'),
        ('CLOSED_LOST', 'Closed Lost'),
    ]
    
    opportunity_id = models.CharField(max_length=20, unique=True)
    lead = models.ForeignKey(Lead, on_delete=models.PROTECT)
    
    opportunity_name = models.CharField(max_length=200)
    description = models.TextField()
    
    stage = models.CharField(max_length=20, choices=STAGES, default='PROSPECTING')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    probability = models.DecimalField(max_digits=5, decimal_places=2)  # 0-100%
    
    expected_close_date = models.DateField()
    actual_close_date = models.DateField(null=True, blank=True)
    
    sales_rep = models.ForeignKey(User, on_delete=models.PROTECT)
    
    competitor_info = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.opportunity_id} - {self.opportunity_name}"

class Campaign(models.Model):
    """Marketing campaign management"""
    CAMPAIGN_TYPES = [
        ('EMAIL', 'Email Campaign'),
        ('SOCIAL_MEDIA', 'Social Media'),
        ('TRADE_SHOW', 'Trade Show'),
        ('WEBINAR', 'Webinar'),
        ('CONTENT', 'Content Marketing'),
        ('PPC', 'Pay-Per-Click'),
    ]
    
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    campaign_name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=15, choices=CAMPAIGN_TYPES)
    description = models.TextField()
    
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PLANNING')
    
    target_audience = models.TextField()
    campaign_metrics = JSONField(default=dict)  # Store various metrics
    
    manager = models.ForeignKey(User, on_delete=models.PROTECT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.campaign_name} ({self.campaign_type})"

class Customer(models.Model):
    """Customer management"""
    CUSTOMER_TYPES = [
        ('INDIVIDUAL', 'Individual'),
        ('SMB', 'Small/Medium Business'),
        ('ENTERPRISE', 'Enterprise'),
        ('GOVERNMENT', 'Government'),
        ('NGO', 'Non-Profit Organization'),
    ]
    
    customer_id = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=200)
    customer_type = models.CharField(max_length=15, choices=CUSTOMER_TYPES)
    
    primary_contact = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    billing_address = models.TextField()
    shipping_address = models.TextField(blank=True)
    
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_terms = models.CharField(max_length=50)
    
    account_manager = models.ForeignKey(User, on_delete=models.PROTECT)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer_id} - {self.company_name}"