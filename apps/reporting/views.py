from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from apps.core.permissions import IsHRManagerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import ReportTemplate, GeneratedReport, KPI
from .serializers import ReportTemplateSerializer, GeneratedReportSerializer, KPISerializer


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """Report template CRUD operations"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_active', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class GeneratedReportViewSet(viewsets.ModelViewSet):
    """Generated report CRUD operations"""
    queryset = GeneratedReport.objects.select_related('template', 'generated_by').all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template', 'status', 'generated_by']
    search_fields = ['title']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    ordering = ['-created_at']


class KPIViewSet(viewsets.ModelViewSet):
    """KPI CRUD operations"""
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'owner', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'target_value', 'current_value', 'updated_at']
    ordering = ['category', 'name']
    
    @action(detail=False, methods=['get'])
    def dashboard_kpis(self, request):
        """Get active KPIs for dashboard display"""
        active_kpis = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_kpis, many=True)
        return Response(serializer.data)