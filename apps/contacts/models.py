"""
Models for REJLERS Backend contacts system
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from apps.core.models import BaseModel, ServiceCategory, IndustrySector

User = get_user_model()


class ContactInquiry(BaseModel):
    """
    Contact form submissions from the REJLERS website
    """
    INQUIRY_TYPES = [
        ('general', 'General Inquiry'),
        ('consultation', 'Consultation Request'),
        ('quote', 'Project Quote'),
        ('partnership', 'Partnership Inquiry'),
        ('career', 'Career Opportunity'),
        ('support', 'Technical Support'),
        ('media', 'Media Inquiry'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('responded', 'Responded'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # Contact Information
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20, 
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be 9-15 digits, optionally starting with +'
        )]
    )
    
    # Company Information
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(
        max_length=50,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-1000', '201-1000 employees'),
            ('1000+', '1000+ employees'),
        ],
        blank=True
    )
    
    # Inquiry Details
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Services and Industries of Interest
    services_interested = models.ManyToManyField(
        ServiceCategory,
        blank=True,
        related_name='interested_inquiries'
    )
    industry_sector = models.ForeignKey(
        IndustrySector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries'
    )
    
    # Project Information
    project_timeline = models.CharField(
        max_length=50,
        choices=[
            ('immediate', 'Immediate (0-1 months)'),
            ('short', 'Short-term (1-3 months)'),
            ('medium', 'Medium-term (3-6 months)'),
            ('long', 'Long-term (6+ months)'),
            ('planning', 'Planning stage'),
        ],
        blank=True
    )
    estimated_budget = models.CharField(
        max_length=50,
        choices=[
            ('under_10k', 'Under $10,000'),
            ('10k_50k', '$10,000 - $50,000'),
            ('50k_100k', '$50,000 - $100,000'),
            ('100k_500k', '$100,000 - $500,000'),
            ('over_500k', 'Over $500,000'),
            ('discuss', 'Prefer to discuss'),
        ],
        blank=True
    )
    
    # Internal Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_inquiries'
    )
    
    # Source and Tracking
    source_page = models.CharField(max_length=200, blank=True, help_text='Which page the inquiry came from')
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    referrer = models.URLField(blank=True)
    
    # Response Information
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responded_inquiries'
    )
    response_notes = models.TextField(blank=True)
    
    # Additional Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['inquiry_type', 'created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.subject}"
    
    def get_full_name(self):
        """Return the full name of the contact"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_high_priority(self):
        """Check if this inquiry is high priority"""
        return self.priority in ['high', 'urgent']


class Newsletter(BaseModel):
    """
    Newsletter subscriptions
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Subscription preferences
    interests = models.ManyToManyField(
        ServiceCategory,
        blank=True,
        related_name='newsletter_subscribers'
    )
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        default='monthly'
    )
    
    # Subscription status
    is_active = models.BooleanField(default=True)
    confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    # Source tracking
    source = models.CharField(max_length=100, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return f"{full_name or 'Anonymous'} ({self.email})"


class InquiryResponse(BaseModel):
    """
    Responses to contact inquiries
    """
    inquiry = models.ForeignKey(
        ContactInquiry,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    responder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inquiry_responses'
    )
    
    response_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone Call'),
            ('meeting', 'Meeting'),
            ('video_call', 'Video Call'),
            ('in_person', 'In Person'),
        ],
        default='email'
    )
    
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    
    # Follow-up information
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    
    # Email tracking (if applicable)
    email_sent = models.BooleanField(default=False)
    email_opened = models.BooleanField(default=False)
    email_clicked = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Inquiry Response'
        verbose_name_plural = 'Inquiry Responses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Response to {self.inquiry.subject} by {self.responder.get_full_name()}"


class ContactList(BaseModel):
    """
    Contact lists for marketing campaigns
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # List criteria
    contacts = models.ManyToManyField(
        ContactInquiry,
        blank=True,
        related_name='contact_lists'
    )
    newsletter_subscribers = models.ManyToManyField(
        Newsletter,
        blank=True,
        related_name='contact_lists'
    )
    
    # List settings
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_contact_lists'
    )
    
    class Meta:
        verbose_name = 'Contact List'
        verbose_name_plural = 'Contact Lists'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def total_contacts(self):
        """Total number of contacts in this list"""
        return self.contacts.count() + self.newsletter_subscribers.count()


class EmailTemplate(BaseModel):
    """
    Email templates for automated responses
    """
    TEMPLATE_TYPES = [
        ('welcome', 'Welcome Email'),
        ('inquiry_confirmation', 'Inquiry Confirmation'),
        ('newsletter_confirmation', 'Newsletter Confirmation'),
        ('follow_up', 'Follow-up Email'),
        ('quote_response', 'Quote Response'),
        ('consultation_booking', 'Consultation Booking'),
    ]
    
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    subject = models.CharField(max_length=200)
    body = models.TextField(help_text='Use {{ variable_name }} for dynamic content')
    
    # Template settings
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_email_templates'
    )
    
    class Meta:
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.get_template_type_display()} - {self.name}"