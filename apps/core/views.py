"""
Core views for REJLERS Backend API
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.conf import settings
from .models import CompanyInfo, ServiceCategory, IndustrySector, ProjectType, Office
from .serializers import (
    CompanyInfoSerializer, ServiceCategorySerializer, 
    IndustrySectorSerializer, ProjectTypeSerializer, OfficeSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def company_info(request):
    """
    Get company information
    """
    try:
        company = CompanyInfo.objects.filter(is_active=True).first()
        if company:
            serializer = CompanyInfoSerializer(company)
            return Response(serializer.data)
        else:
            # Return default company info if none exists in database
            return Response({
                'name': settings.COMPANY_CONFIG['NAME'],
                'full_name': settings.COMPANY_CONFIG['FULL_NAME'],
                'tagline': settings.COMPANY_CONFIG['TAGLINE'],
                'email': settings.COMPANY_CONFIG['EMAIL'],
                'phone': settings.COMPANY_CONFIG['PHONE'],
                'website': settings.COMPANY_CONFIG['WEBSITE'],
                'address': settings.COMPANY_CONFIG['ADDRESS'],
            })
    except Exception as e:
        return Response(
            {'error': 'Unable to fetch company information'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ServiceCategoryListView(generics.ListAPIView):
    """
    List all service categories
    """
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return super().get_queryset().order_by('order', 'name')


class IndustrySectorListView(generics.ListAPIView):
    """
    List all industry sectors
    """
    queryset = IndustrySector.objects.filter(is_active=True)
    serializer_class = IndustrySectorSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return super().get_queryset().order_by('order', 'name')


class ProjectTypeListView(generics.ListAPIView):
    """
    List all project types
    """
    queryset = ProjectType.objects.filter(is_active=True)
    serializer_class = ProjectTypeSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return super().get_queryset().order_by('order', 'name')


class OfficeListView(generics.ListAPIView):
    """
    List all office locations
    """
    queryset = Office.objects.filter(is_active=True)
    serializer_class = OfficeSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return super().get_queryset().select_related('country').order_by('-is_headquarters', 'country__name', 'city')