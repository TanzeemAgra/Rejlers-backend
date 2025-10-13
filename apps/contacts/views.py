"""
Views for REJLERS Backend contacts system
"""

from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta

from .models import ContactInquiry, Newsletter, InquiryResponse, ContactList, EmailTemplate
from .serializers import (
    ContactInquirySerializer,
    ContactInquiryCreateSerializer,
    NewsletterSerializer,
    InquiryResponseSerializer,
    ContactListSerializer,
    EmailTemplateSerializer,
    ContactInquiryDetailSerializer
)
from .filters import ContactInquiryFilter


class ContactInquiryCreateView(generics.CreateAPIView):
    """
    Create a new contact inquiry (public endpoint)
    """
    serializer_class = ContactInquiryCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Add metadata
        inquiry_data = serializer.validated_data.copy()
        inquiry_data['ip_address'] = self.get_client_ip(request)
        inquiry_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        inquiry_data['referrer'] = request.META.get('HTTP_REFERER', '')
        
        inquiry = ContactInquiry.objects.create(**inquiry_data)
        
        # Handle services interested (many-to-many)
        services_data = request.data.get('services_interested', [])
        if services_data:
            inquiry.services_interested.set(services_data)
        
        # Send confirmation email to inquirer
        self.send_confirmation_email(inquiry)
        
        # Send notification email to admin
        self.send_admin_notification(inquiry)
        
        return Response({
            'message': 'Your inquiry has been submitted successfully',
            'inquiry_id': inquiry.id,
            'reference_number': str(inquiry.id)[:8].upper()
        }, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def send_confirmation_email(self, inquiry):
        """Send confirmation email to the inquirer"""
        try:
            send_mail(
                subject=f'Thank you for contacting REJLERS - {inquiry.subject}',
                message=f'''
Dear {inquiry.get_full_name()},

Thank you for your interest in REJLERS. We have received your inquiry and will respond within 24-48 hours.

Inquiry Details:
- Reference: {str(inquiry.id)[:8].upper()}
- Subject: {inquiry.subject}
- Type: {inquiry.get_inquiry_type_display()}
- Submitted: {inquiry.created_at.strftime('%B %d, %Y at %I:%M %p')}

We appreciate your interest in our services and look forward to discussing how REJLERS can help with your project.

Best regards,
REJLERS Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inquiry.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")
    
    def send_admin_notification(self, inquiry):
        """Send notification email to admin"""
        try:
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@rejlers.com')
            send_mail(
                subject=f'New Contact Inquiry: {inquiry.subject}',
                message=f'''
New contact inquiry received:

Contact Information:
- Name: {inquiry.get_full_name()}
- Email: {inquiry.email}
- Phone: {inquiry.phone or 'Not provided'}
- Company: {inquiry.company_name or 'Not provided'}

Inquiry Details:
- Type: {inquiry.get_inquiry_type_display()}
- Subject: {inquiry.subject}
- Priority: {inquiry.get_priority_display()}
- Timeline: {inquiry.get_project_timeline_display() if inquiry.project_timeline else 'Not specified'}
- Budget: {inquiry.get_estimated_budget_display() if inquiry.estimated_budget else 'Not specified'}

Message:
{inquiry.message}

View in admin: {settings.BACKEND_URL}/admin/contacts/contactinquiry/{inquiry.id}/
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send admin notification: {e}")


class ContactInquiryListView(generics.ListAPIView):
    """
    List contact inquiries (admin only)
    """
    queryset = ContactInquiry.objects.filter(is_active=True)
    serializer_class = ContactInquirySerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContactInquiryFilter
    search_fields = ['first_name', 'last_name', 'email', 'company_name', 'subject', 'message']
    ordering_fields = ['created_at', 'priority', 'status', 'inquiry_type']
    ordering = ['-created_at']


class ContactInquiryDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update contact inquiry (admin only)
    """
    queryset = ContactInquiry.objects.filter(is_active=True)
    serializer_class = ContactInquiryDetailSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class NewsletterSubscribeView(generics.CreateAPIView):
    """
    Newsletter subscription (public endpoint)
    """
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Check if already subscribed
        existing_subscription = Newsletter.objects.filter(email=email).first()
        if existing_subscription:
            if existing_subscription.is_active:
                return Response({
                    'message': 'You are already subscribed to our newsletter'
                }, status=status.HTTP_200_OK)
            else:
                # Reactivate subscription
                existing_subscription.is_active = True
                existing_subscription.save()
                return Response({
                    'message': 'Your newsletter subscription has been reactivated'
                }, status=status.HTTP_200_OK)
        
        # Create new subscription
        subscription = serializer.save()
        
        # Send welcome email
        self.send_welcome_email(subscription)
        
        return Response({
            'message': 'Successfully subscribed to newsletter'
        }, status=status.HTTP_201_CREATED)
    
    def send_welcome_email(self, subscription):
        """Send welcome email to new subscriber"""
        try:
            send_mail(
                subject='Welcome to REJLERS Newsletter',
                message=f'''
Welcome to REJLERS Newsletter!

Thank you for subscribing to our newsletter. You'll receive updates about:
- Industrial and manufacturing insights
- Engineering solutions and innovations
- Industry trends and best practices
- Company news and project highlights

You can update your preferences or unsubscribe at any time.

Best regards,
REJLERS Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send welcome email: {e}")


class NewsletterUnsubscribeView(APIView):
    """
    Newsletter unsubscribe (public endpoint)
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription = Newsletter.objects.get(email=email, is_active=True)
            subscription.is_active = False
            subscription.unsubscribed_at = timezone.now()
            subscription.save()
            
            return Response({
                'message': 'Successfully unsubscribed from newsletter'
            }, status=status.HTTP_200_OK)
        except Newsletter.DoesNotExist:
            return Response({
                'message': 'Email not found in our newsletter list'
            }, status=status.HTTP_404_NOT_FOUND)


class InquiryResponseCreateView(generics.CreateAPIView):
    """
    Create response to inquiry (admin only)
    """
    serializer_class = InquiryResponseSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        response = serializer.save(responder=self.request.user)
        
        # Update inquiry status
        inquiry = response.inquiry
        if inquiry.status == 'new':
            inquiry.status = 'in_progress'
        inquiry.responded_at = timezone.now()
        inquiry.responded_by = self.request.user
        inquiry.save()
        
        # Send email if response method is email
        if response.response_method == 'email':
            self.send_response_email(response)
    
    def send_response_email(self, response):
        """Send email response to inquirer"""
        try:
            inquiry = response.inquiry
            send_mail(
                subject=response.subject or f'Re: {inquiry.subject}',
                message=response.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inquiry.email],
                fail_silently=True,
            )
            
            # Mark email as sent
            response.email_sent = True
            response.save(update_fields=['email_sent'])
            
        except Exception as e:
            print(f"Failed to send response email: {e}")


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def contact_analytics(request):
    """
    Get contact analytics dashboard data
    """
    # Date range (default: last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Query filters
    inquiries_qs = ContactInquiry.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        is_active=True
    )
    
    # Basic stats
    stats = {
        'total_inquiries': inquiries_qs.count(),
        'new_inquiries': inquiries_qs.filter(status='new').count(),
        'in_progress_inquiries': inquiries_qs.filter(status='in_progress').count(),
        'resolved_inquiries': inquiries_qs.filter(status='resolved').count(),
    }
    
    # Inquiry types breakdown
    inquiry_types = inquiries_qs.values('inquiry_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Priority breakdown
    priority_breakdown = inquiries_qs.values('priority').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Daily inquiry counts (last 7 days)
    daily_inquiries = []
    for i in range(7):
        date = end_date - timedelta(days=i)
        count = inquiries_qs.filter(created_at__date=date).count()
        daily_inquiries.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    daily_inquiries.reverse()
    
    # Newsletter stats
    newsletter_stats = {
        'total_subscribers': Newsletter.objects.filter(is_active=True).count(),
        'new_subscribers': Newsletter.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_active=True
        ).count(),
    }
    
    return Response({
        'stats': stats,
        'inquiry_types': inquiry_types,
        'priority_breakdown': priority_breakdown,
        'daily_inquiries': daily_inquiries,
        'newsletter_stats': newsletter_stats,
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def bulk_update_inquiries(request):
    """
    Bulk update inquiries
    """
    inquiry_ids = request.data.get('inquiry_ids', [])
    updates = request.data.get('updates', {})
    
    if not inquiry_ids or not updates:
        return Response({
            'error': 'inquiry_ids and updates are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate updates
    allowed_fields = ['status', 'priority', 'assigned_to']
    update_data = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not update_data:
        return Response({
            'error': 'No valid update fields provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Perform bulk update
    updated_count = ContactInquiry.objects.filter(
        id__in=inquiry_ids,
        is_active=True
    ).update(**update_data)
    
    return Response({
        'message': f'Updated {updated_count} inquiries',
        'updated_count': updated_count
    })


class ContactListView(generics.ListCreateAPIView):
    """
    List and create contact lists (admin only)
    """
    queryset = ContactList.objects.filter(is_active=True)
    serializer_class = ContactListSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EmailTemplateView(generics.ListCreateAPIView):
    """
    List and create email templates (admin only)
    """
    queryset = EmailTemplate.objects.filter(is_active=True)
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)