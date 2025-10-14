from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from apps.core.permissions import IsHRManagerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import SafetyIncident, ComplianceChecklist, ComplianceAssessment, EnvironmentalMonitoring
from .serializers import (
    SafetyIncidentSerializer, ComplianceChecklistSerializer, 
    ComplianceAssessmentSerializer, EnvironmentalMonitoringSerializer
)


class SafetyIncidentViewSet(viewsets.ModelViewSet):
    """Safety incident CRUD operations"""
    queryset = SafetyIncident.objects.all()
    serializer_class = SafetyIncidentSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['incident_type', 'severity', 'is_resolved', 'reported_by']
    search_fields = ['incident_id', 'title', 'description', 'location']
    ordering_fields = ['incident_date', 'severity', 'created_at']
    ordering = ['-incident_date']


class ComplianceChecklistViewSet(viewsets.ModelViewSet):
    """Compliance checklist CRUD operations"""
    queryset = ComplianceChecklist.objects.all()
    serializer_class = ComplianceChecklistSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['compliance_type', 'is_mandatory', 'is_active', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ComplianceAssessmentViewSet(viewsets.ModelViewSet):
    """Compliance assessment CRUD operations"""
    queryset = ComplianceAssessment.objects.select_related('checklist', 'assessed_by').all()
    serializer_class = ComplianceAssessmentSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['checklist', 'status', 'assessed_by']
    search_fields = ['assessed_location', 'notes']
    ordering_fields = ['assessment_date', 'compliance_score']
    ordering = ['-assessment_date']


class EnvironmentalMonitoringViewSet(viewsets.ModelViewSet):
    """Environmental monitoring CRUD operations"""
    queryset = EnvironmentalMonitoring.objects.all()
    serializer_class = EnvironmentalMonitoringSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['monitoring_type', 'location', 'is_within_limits', 'recorded_by']
    search_fields = ['location', 'notes']
    ordering_fields = ['measurement_date', 'measured_value']
    ordering = ['-measurement_date']