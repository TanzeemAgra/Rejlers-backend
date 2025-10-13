"""
Serializers for REJLERS Backend contacts system
"""

from rest_framework import serializers
from .models import ContactInquiry, Newsletter, InquiryResponse, ContactList, EmailTemplate
from apps.core.models import ServiceCategory, IndustrySector


class ContactInquiryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating contact inquiries (public endpoint)
    """
    services_interested = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
        required=False
    )
    
    class Meta:
        model = ContactInquiry
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'company_name', 'job_title', 'company_size',
            'inquiry_type', 'subject', 'message',
            'services_interested', 'industry_sector',
            'project_timeline', 'estimated_budget',
            'source_page', 'utm_source', 'utm_medium', 'utm_campaign'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'subject': {'required': True},
            'message': {'required': True},
        }


class ContactInquirySerializer(serializers.ModelSerializer):
    """
    Serializer for listing contact inquiries (admin)
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    services_interested = serializers.StringRelatedField(many=True, read_only=True)
    industry_sector_name = serializers.CharField(source='industry_sector.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    inquiry_type_display = serializers.CharField(source='get_inquiry_type_display', read_only=True)
    
    class Meta:
        model = ContactInquiry
        fields = [
            'id', 'full_name', 'email', 'phone', 'company_name', 'job_title',
            'inquiry_type', 'inquiry_type_display', 'subject', 'message',
            'services_interested', 'industry_sector_name',
            'project_timeline', 'estimated_budget',
            'status', 'status_display', 'priority', 'priority_display',
            'assigned_to_name', 'created_at', 'responded_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContactInquiryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for contact inquiry (admin)
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    services_interested = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    responses = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactInquiry
        exclude = ['is_active', 'deleted_at']
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'ip_address', 'user_agent',
            'referrer', 'utm_source', 'utm_medium', 'utm_campaign'
        ]
    
    def get_responses(self, obj):
        """Get inquiry responses"""
        responses = obj.responses.filter(is_active=True).order_by('-created_at')
        return InquiryResponseSerializer(responses, many=True, read_only=True).data


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Newsletter subscription serializer
    """
    interests = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ServiceCategory.objects.filter(is_active=True),
        required=False
    )
    
    class Meta:
        model = Newsletter
        fields = [
            'email', 'first_name', 'last_name', 'interests', 'frequency',
            'source', 'utm_source', 'utm_medium', 'utm_campaign'
        ]
        extra_kwargs = {
            'email': {'required': True},
        }


class InquiryResponseSerializer(serializers.ModelSerializer):
    """
    Inquiry response serializer
    """
    responder_name = serializers.CharField(source='responder.get_full_name', read_only=True)
    
    class Meta:
        model = InquiryResponse
        fields = [
            'id', 'inquiry', 'response_method', 'subject', 'message',
            'follow_up_required', 'follow_up_date', 'follow_up_notes',
            'responder_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'responder_name']


class ContactListSerializer(serializers.ModelSerializer):
    """
    Contact list serializer
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    total_contacts = serializers.ReadOnlyField()
    
    class Meta:
        model = ContactList
        fields = [
            'id', 'name', 'description', 'contacts', 'newsletter_subscribers',
            'is_active', 'created_by_name', 'total_contacts', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_name']


class EmailTemplateSerializer(serializers.ModelSerializer):
    """
    Email template serializer
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type', 'template_type_display',
            'subject', 'body', 'is_active', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_name']


class NewsletterListSerializer(serializers.ModelSerializer):
    """
    Newsletter list serializer (admin)
    """
    interests = serializers.StringRelatedField(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Newsletter
        fields = [
            'id', 'email', 'full_name', 'interests', 'frequency',
            'is_active', 'confirmed', 'confirmed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_full_name(self, obj):
        """Get full name or 'Anonymous' if not provided"""
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or 'Anonymous'