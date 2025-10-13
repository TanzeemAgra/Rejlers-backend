"""
Serializers for REJLERS Core models
"""

from rest_framework import serializers
from .models import CompanyInfo, ServiceCategory, IndustrySector, ProjectType, Country, Office


class CompanyInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for company information
    """
    address = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyInfo
        fields = [
            'id', 'name', 'full_name', 'tagline', 'description',
            'email', 'phone', 'website', 'address', 'linkedin_url',
            'established_year', 'employee_count', 'logo', 'favicon',
            'created_at', 'updated_at'
        ]
    
    def get_address(self, obj):
        return {
            'street': obj.address_street,
            'city': obj.address_city,
            'postal_code': obj.address_postal_code,
            'country': obj.address_country
        }


class ServiceCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for service categories
    """
    class Meta:
        model = ServiceCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color', 'order'
        ]


class IndustrySectorSerializer(serializers.ModelSerializer):
    """
    Serializer for industry sectors
    """
    class Meta:
        model = IndustrySector
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color', 'order'
        ]


class ProjectTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for project types
    """
    class Meta:
        model = ProjectType
        fields = [
            'id', 'name', 'slug', 'description', 'duration_estimate',
            'complexity_level', 'order'
        ]


class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for countries
    """
    class Meta:
        model = Country
        fields = [
            'id', 'name', 'code', 'flag_emoji', 'is_primary_market'
        ]


class OfficeSerializer(serializers.ModelSerializer):
    """
    Serializer for office locations
    """
    country = CountrySerializer(read_only=True)
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Office
        fields = [
            'id', 'name', 'country', 'city', 'address', 'postal_code',
            'phone', 'email', 'latitude', 'longitude', 'employee_count',
            'is_headquarters', 'full_address'
        ]
    
    def get_full_address(self, obj):
        return f"{obj.address}, {obj.postal_code} {obj.city}, {obj.country.name}"