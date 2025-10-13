"""
Django signals for contacts app
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ContactInquiry, InquiryResponse


@receiver(post_save, sender=ContactInquiry)
def set_inquiry_priority(sender, instance, created, **kwargs):
    """
    Automatically set priority based on inquiry type and content
    """
    if created:
        # Set high priority for certain inquiry types
        if instance.inquiry_type in ['consultation', 'quote']:
            instance.priority = 'high'
        
        # Check for urgent keywords in message
        urgent_keywords = ['urgent', 'asap', 'immediate', 'emergency']
        if any(keyword in instance.message.lower() for keyword in urgent_keywords):
            instance.priority = 'urgent'
        
        # Save only if priority was changed
        if instance.priority != 'medium':  # default value
            instance.save(update_fields=['priority'])


@receiver(post_save, sender=InquiryResponse)
def update_inquiry_status(sender, instance, created, **kwargs):
    """
    Update inquiry status when a response is created
    """
    if created:
        inquiry = instance.inquiry
        
        # Update status if it's still new
        if inquiry.status == 'new':
            inquiry.status = 'in_progress'
            inquiry.save(update_fields=['status'])
        
        # Set responded timestamp if not already set
        if not inquiry.responded_at:
            inquiry.responded_at = timezone.now()
            inquiry.responded_by = instance.responder
            inquiry.save(update_fields=['responded_at', 'responded_by'])