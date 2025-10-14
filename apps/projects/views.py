from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.utils import timezone

from apps.core.permissions import IsProjectManagerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import ProjectCategory, Client, Project, Task
from .serializers import (
    ProjectCategorySerializer, ClientSerializer, ProjectSerializer, TaskSerializer
)


class ProjectCategoryViewSet(viewsets.ModelViewSet):
    """Project category CRUD operations"""
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [IsProjectManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ClientViewSet(viewsets.ModelViewSet):
    """Client CRUD operations"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsProjectManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['client_type']
    search_fields = ['company_name', 'contact_person', 'email']
    ordering_fields = ['company_name', 'created_at']
    ordering = ['company_name']


class ProjectViewSet(viewsets.ModelViewSet):
    """Project CRUD operations"""
    queryset = Project.objects.select_related('category', 'client', 'manager').all()
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'client', 'manager']
    search_fields = ['name', 'description', 'client__company_name']
    ordering_fields = ['name', 'start_date', 'end_date', 'budget', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def active_projects(self, request):
        """Get all active projects"""
        active_projects = self.queryset.filter(
            status__in=['PLANNING', 'IN_PROGRESS', 'ON_HOLD']
        )
        serializer = self.get_serializer(active_projects, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """Task management"""
    queryset = Task.objects.select_related('project', 'assigned_to').all()
    serializer_class = TaskSerializer
    permission_classes = [IsProjectManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status', 'assigned_to']
    search_fields = ['title', 'description', 'project__name']
    ordering_fields = ['title', 'due_date', 'created_at']
    ordering = ['due_date']
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to current user"""
        my_tasks = self.queryset.filter(assigned_to=request.user)
        serializer = self.get_serializer(my_tasks, many=True)
        return Response(serializer.data)