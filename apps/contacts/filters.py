"""
Django filters for contacts app
"""

import django_filters
from .models import ContactInquiry, Newsletter


class ContactInquiryFilter(django_filters.FilterSet):
    """
    Filter for contact inquiries
    """
    # Date range filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Multiple choice filters
    status = django_filters.MultipleChoiceFilter(
        choices=ContactInquiry.STATUS_CHOICES
    )
    priority = django_filters.MultipleChoiceFilter(
        choices=ContactInquiry.PRIORITY_LEVELS
    )
    inquiry_type = django_filters.MultipleChoiceFilter(
        choices=ContactInquiry.INQUIRY_TYPES
    )
    
    # Text search filters
    company_name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    # Boolean filters
    has_phone = django_filters.BooleanFilter(method='filter_has_phone')
    has_company = django_filters.BooleanFilter(method='filter_has_company')
    is_responded = django_filters.BooleanFilter(method='filter_is_responded')
    
    class Meta:
        model = ContactInquiry
        fields = [
            'status', 'priority', 'inquiry_type', 'industry_sector',
            'assigned_to', 'project_timeline', 'estimated_budget'
        ]
    
    def filter_has_phone(self, queryset, name, value):
        """Filter inquiries with/without phone numbers"""
        if value:
            return queryset.exclude(phone='')
        return queryset.filter(phone='')
    
    def filter_has_company(self, queryset, name, value):
        """Filter inquiries with/without company information"""
        if value:
            return queryset.exclude(company_name='')
        return queryset.filter(company_name='')
    
    def filter_is_responded(self, queryset, name, value):
        """Filter inquiries that have been responded to"""
        if value:
            return queryset.exclude(responded_at__isnull=True)
        return queryset.filter(responded_at__isnull=True)


class NewsletterFilter(django_filters.FilterSet):
    """
    Filter for newsletter subscriptions
    """
    # Date range filters
    subscribed_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    subscribed_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Text filters
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Newsletter
        fields = ['is_active', 'confirmed', 'frequency', 'source']