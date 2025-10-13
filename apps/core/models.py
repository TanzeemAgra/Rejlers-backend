"""
Core models for REJLERS Backend

Base models and common functionality shared across applications.
"""

from django.db import models
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all models
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def soft_delete(self):
        """Soft delete by setting is_active to False"""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def restore(self):
        """Restore soft deleted record"""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])


class CompanyInfo(BaseModel):
    """
    Company information model for REJLERS
    """
    name = models.CharField(max_length=100, default='REJLERS')
    full_name = models.CharField(max_length=200, default='REJLERS AB')
    tagline = models.CharField(max_length=200, default='Engineering Excellence Since 1942')
    description = models.TextField(blank=True)
    
    # Contact Information
    email = models.EmailField(default='info@rejlers.se')
    phone = models.CharField(max_length=50, default='+46 (0)771 78 00 00')
    website = models.URLField(default='https://www.rejlers.se')
    
    # Address Information
    address_street = models.CharField(max_length=200, default='Box 30233')
    address_city = models.CharField(max_length=100, default='Stockholm')
    address_postal_code = models.CharField(max_length=20, default='104 25')
    address_country = models.CharField(max_length=100, default='Sweden')
    
    # Social Media
    linkedin_url = models.URLField(blank=True, default='https://www.linkedin.com/company/rejlers')
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    
    # Business Information
    established_year = models.PositiveIntegerField(default=1942)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Logo and Branding
    logo = models.ImageField(upload_to='company/logos/', null=True, blank=True)
    favicon = models.ImageField(upload_to='company/favicons/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Company Information'
        verbose_name_plural = 'Company Information'
    
    def __str__(self):
        return self.name


class ServiceCategory(BaseModel):
    """
    Service categories for REJLERS offerings
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text='CSS icon class or emoji')
    color = models.CharField(max_length=7, default='#0ea5e9', help_text='Hex color code')
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    
    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class IndustrySector(BaseModel):
    """
    Industry sectors that REJLERS serves
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text='CSS icon class or emoji')
    color = models.CharField(max_length=7, default='#22c55e', help_text='Hex color code')
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    
    class Meta:
        verbose_name = 'Industry Sector'
        verbose_name_plural = 'Industry Sectors'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ProjectType(BaseModel):
    """
    Types of projects REJLERS handles
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    duration_estimate = models.CharField(max_length=100, help_text='Estimated duration range')
    complexity_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Complexity'),
            ('medium', 'Medium Complexity'),
            ('high', 'High Complexity'),
            ('expert', 'Expert Level'),
        ],
        default='medium'
    )
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    
    class Meta:
        verbose_name = 'Project Type'
        verbose_name_plural = 'Project Types'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Country(BaseModel):
    """
    Countries where REJLERS operates
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True, help_text='ISO country code')
    flag_emoji = models.CharField(max_length=10, blank=True)
    is_primary_market = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['-is_primary_market', 'name']
    
    def __str__(self):
        return f"{self.flag_emoji} {self.name}" if self.flag_emoji else self.name


class Office(BaseModel):
    """
    REJLERS office locations
    """
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='offices')
    city = models.CharField(max_length=100)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    
    # Coordinates for mapping
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Office details
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    is_headquarters = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Office Location'
        verbose_name_plural = 'Office Locations'
        ordering = ['-is_headquarters', 'country__name', 'city']
    
    def __str__(self):
        return f"{self.city}, {self.country.name}"