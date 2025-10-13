"""
User models for REJLERS Backend authentication system
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel
import uuid


class User(AbstractUser):
    """
    Custom User model for REJLERS system
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Company/Professional Information
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Profile Information
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    
    # Business Details
    industry = models.CharField(max_length=100, blank=True)
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
    
    # Contact Preferences
    newsletter_subscribed = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    
    # Account Status
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the full name of the user"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    def get_short_name(self):
        """Return the short name for the user"""
        return self.first_name or self.username
    
    def verify_email(self):
        """Mark email as verified"""
        self.email_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=['email_verified', 'email_verified_at'])


class UserProfile(BaseModel):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Additional Professional Information
    linkedin_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Professional Interests
    services_of_interest = models.ManyToManyField(
        'core.ServiceCategory', 
        blank=True,
        related_name='interested_users'
    )
    industries_of_interest = models.ManyToManyField(
        'core.IndustrySector',
        blank=True,
        related_name='interested_users'
    )
    
    # Communication Preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('linkedin', 'LinkedIn'),
        ],
        default='email'
    )
    
    # Privacy Settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('contacts', 'Contacts Only'),
        ],
        default='private'
    )
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"


class EmailVerificationToken(BaseModel):
    """
    Email verification tokens for user registration
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
    
    def __str__(self):
        return f"Verification token for {self.user.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def mark_used(self):
        """Mark token as used"""
        self.used = True
        self.used_at = timezone.now()
        self.save(update_fields=['used', 'used_at'])


class PasswordResetToken(BaseModel):
    """
    Password reset tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
    
    def __str__(self):
        return f"Password reset token for {self.user.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def mark_used(self):
        """Mark token as used"""
        self.used = True
        self.used_at = timezone.now()
        self.save(update_fields=['used', 'used_at'])