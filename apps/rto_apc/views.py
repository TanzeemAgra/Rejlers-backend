from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from apps.core.permissions import IsHRManagerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import ControlSystem, ProcessTag, ProcessData, Alarm, MaintenanceSchedule
from .serializers import (
    ControlSystemSerializer, ProcessTagSerializer, ProcessDataSerializer,
    AlarmSerializer, MaintenanceScheduleSerializer
)


class ControlSystemViewSet(viewsets.ModelViewSet):
    """Control system CRUD operations"""
    queryset = ControlSystem.objects.all()
    serializer_class = ControlSystemSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['system_type', 'status', 'operator']
    search_fields = ['system_id', 'system_name', 'location']
    ordering_fields = ['system_name', 'installed_date']
    ordering = ['system_name']


class ProcessTagViewSet(viewsets.ModelViewSet):
    """Process tag CRUD operations"""
    queryset = ProcessTag.objects.select_related('control_system').all()
    serializer_class = ProcessTagSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['control_system', 'tag_type', 'data_type', 'is_active']
    search_fields = ['tag_name', 'description']
    ordering_fields = ['tag_name', 'created_at']
    ordering = ['tag_name']


class ProcessDataViewSet(viewsets.ModelViewSet):
    """Process data CRUD operations"""
    queryset = ProcessData.objects.select_related('tag').all()
    serializer_class = ProcessDataSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tag', 'quality']
    ordering_fields = ['timestamp', 'value']
    ordering = ['-timestamp']


class AlarmViewSet(viewsets.ModelViewSet):
    """Alarm CRUD operations"""
    queryset = Alarm.objects.select_related('tag', 'acknowledged_by').all()
    serializer_class = AlarmSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alarm_type', 'priority', 'status', 'tag']
    search_fields = ['message', 'tag__tag_name']
    ordering_fields = ['occurred_at', 'priority']
    ordering = ['-occurred_at']
    
    @action(detail=False, methods=['get'])
    def active_alarms(self, request):
        """Get active alarms"""
        active_alarms = self.queryset.filter(status='ACTIVE')
        serializer = self.get_serializer(active_alarms, many=True)
        return Response(serializer.data)


class MaintenanceScheduleViewSet(viewsets.ModelViewSet):
    """Maintenance schedule CRUD operations"""
    queryset = MaintenanceSchedule.objects.select_related('control_system', 'technician', 'created_by').all()
    serializer_class = MaintenanceScheduleSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['maintenance_type', 'status', 'control_system', 'technician']
    search_fields = ['title', 'description', 'control_system__system_name']
    ordering_fields = ['scheduled_date', 'created_at']
    ordering = ['scheduled_date']