"""
HR Management Views
RESTful API views for HR Management operations with proper permissions and filtering
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta

from apps.core.permissions import IsHRManagerOrReadOnly, IsManagerOrOwner
from apps.core.pagination import StandardResultsSetPagination
from .models import Department, Position, Employee, TimeOff, Performance
from .serializers import (
    DepartmentSerializer, PositionSerializer, EmployeeSerializer,
    EmployeeCreateSerializer, TimeOffSerializer, PerformanceSerializer,
    DepartmentSummarySerializer, EmployeeSummarySerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """Department management viewset"""
    
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department_type', 'is_active', 'manager']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at', 'employee_count']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter departments based on user permissions"""
        queryset = super().get_queryset()
        if not self.request.user.has_perm('hr_management.view_all_departments'):
            # Non-HR users can only see their own department
            if hasattr(self.request.user, 'employee'):
                department = self.request.user.employee.department
                queryset = queryset.filter(
                    Q(id=department.id) | Q(parent_department=department)
                ) if department else queryset.none()
        return queryset
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get department hierarchy"""
        root_departments = self.get_queryset().filter(parent_department__isnull=True)
        serializer = DepartmentSummarySerializer(root_departments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get employees in department"""
        department = self.get_object()
        employees = Employee.objects.filter(department=department, employment_status='ACTIVE')
        serializer = EmployeeSummarySerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get department statistics"""
        queryset = self.get_queryset()
        stats = {
            'total_departments': queryset.count(),
            'active_departments': queryset.filter(is_active=True).count(),
            'total_employees': Employee.objects.filter(
                department__in=queryset, employment_status='ACTIVE'
            ).count(),
            'by_type': dict(
                queryset.values('department_type').annotate(
                    count=Count('id')
                ).values_list('department_type', 'count')
            )
        }
        return Response(stats)


class PositionViewSet(viewsets.ModelViewSet):
    """Position management viewset"""
    
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated, IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'level', 'is_active']
    search_fields = ['title', 'description', 'requirements']
    ordering_fields = ['title', 'level', 'min_salary', 'max_salary']
    ordering = ['department', 'level', 'title']
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get positions grouped by department"""
        department_id = request.query_params.get('department_id')
        if department_id:
            positions = self.get_queryset().filter(department_id=department_id)
        else:
            positions = self.get_queryset()
        
        serializer = self.get_serializer(positions, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    """Employee management viewset"""
    
    queryset = Employee.objects.select_related('user', 'department', 'position', 'manager').all()
    permission_classes = [IsAuthenticated, IsManagerOrOwner]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'employment_type', 'employment_status', 'manager']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'skills']
    ordering_fields = ['user__last_name', 'hire_date', 'salary', 'employee_id']
    ordering = ['user__last_name', 'user__first_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    
    def get_queryset(self):
        """Filter employees based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.has_perm('hr_management.view_all_employees'):
            return queryset
        elif user.has_perm('hr_management.view_department_employees'):
            # Managers can see employees in their department
            if hasattr(user, 'employee'):
                department = user.employee.department
                return queryset.filter(department=department) if department else queryset.none()
        else:
            # Regular employees can only see their own record
            return queryset.filter(user=user)
        
        return queryset.none()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's employee record"""
        try:
            employee = Employee.objects.get(user=request.user)
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee record not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def birthdays(self, request):
        """Get employees with birthdays this month"""
        today = timezone.now().date()
        employees = self.get_queryset().filter(
            date_of_birth__month=today.month,
            employment_status='ACTIVE'
        )
        serializer = EmployeeSummarySerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new_hires(self, request):
        """Get recent new hires (last 30 days)"""
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        employees = self.get_queryset().filter(
            hire_date__gte=thirty_days_ago,
            employment_status='ACTIVE'
        )
        serializer = EmployeeSummarySerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get employee statistics"""
        queryset = self.get_queryset()
        stats = {
            'total_employees': queryset.count(),
            'active_employees': queryset.filter(employment_status='ACTIVE').count(),
            'by_department': dict(
                queryset.filter(employment_status='ACTIVE')
                .values('department__name')
                .annotate(count=Count('id'))
                .values_list('department__name', 'count')
            ),
            'by_employment_type': dict(
                queryset.filter(employment_status='ACTIVE')
                .values('employment_type')
                .annotate(count=Count('id'))
                .values_list('employment_type', 'count')
            ),
            'average_tenure_years': queryset.filter(
                employment_status='ACTIVE'
            ).aggregate(
                avg_years=Avg('years_of_service')
            )['avg_years'] or 0
        }
        return Response(stats)


class TimeOffViewSet(viewsets.ModelViewSet):
    """Time off request management viewset"""
    
    queryset = TimeOff.objects.select_related('employee__user', 'approved_by').all()
    serializer_class = TimeOffSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'time_off_type', 'status', 'start_date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'reason']
    ordering_fields = ['start_date', 'created_at', 'days_requested']
    ordering = ['-start_date']
    
    def get_queryset(self):
        """Filter time off requests based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.has_perm('hr_management.view_all_timeoff'):
            return queryset
        elif user.has_perm('hr_management.approve_timeoff'):
            # Managers can see requests from their direct reports
            managed_employees = Employee.objects.filter(manager=user)
            return queryset.filter(
                Q(employee__user=user) | Q(employee__in=managed_employees)
            )
        else:
            # Employees can only see their own requests
            return queryset.filter(employee__user=user)
    
    def perform_create(self, serializer):
        """Set employee when creating time off request"""
        try:
            employee = Employee.objects.get(user=self.request.user)
            serializer.save(employee=employee)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee record not found")
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve time off request"""
        time_off = self.get_object()
        
        if not request.user.has_perm('hr_management.approve_timeoff'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        time_off.status = 'APPROVED'
        time_off.approved_by = request.user
        time_off.approved_at = timezone.now()
        time_off.comments = request.data.get('comments', '')
        time_off.save()
        
        serializer = self.get_serializer(time_off)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        """Deny time off request"""
        time_off = self.get_object()
        
        if not request.user.has_perm('hr_management.approve_timeoff'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        time_off.status = 'DENIED'
        time_off.approved_by = request.user
        time_off.approved_at = timezone.now()
        time_off.comments = request.data.get('comments', 'Request denied')
        time_off.save()
        
        serializer = self.get_serializer(time_off)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending time off requests for approval"""
        pending_requests = self.get_queryset().filter(status='PENDING')
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Get time off calendar view"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset().filter(status='APPROVED')
        
        if start_date:
            queryset = queryset.filter(end_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PerformanceViewSet(viewsets.ModelViewSet):
    """Performance review management viewset"""
    
    queryset = Performance.objects.select_related('employee__user', 'reviewer').all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsAuthenticated, IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'reviewer', 'review_period', 'review_end_date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['review_end_date', 'overall_rating', 'created_at']
    ordering = ['-review_end_date']
    
    def get_queryset(self):
        """Filter performance reviews based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.has_perm('hr_management.view_all_performance'):
            return queryset
        elif user.has_perm('hr_management.conduct_performance_review'):
            # Managers can see reviews they conducted or for their direct reports
            managed_employees = Employee.objects.filter(manager=user)
            return queryset.filter(
                Q(reviewer=user) | 
                Q(employee__in=managed_employees) |
                Q(employee__user=user)
            )
        else:
            # Employees can only see their own reviews
            return queryset.filter(employee__user=user)
    
    @action(detail=False, methods=['get'])
    def due(self, request):
        """Get employees due for performance review"""
        # This is a simplified version - in practice, you'd have more complex logic
        # for determining who needs reviews based on hire dates, last review dates, etc.
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=180)
        
        # Find employees who haven't had a review in 6 months
        employees_with_recent_reviews = Performance.objects.filter(
            review_end_date__gte=six_months_ago
        ).values_list('employee_id', flat=True)
        
        employees_due = Employee.objects.filter(
            employment_status='ACTIVE'
        ).exclude(id__in=employees_with_recent_reviews)
        
        serializer = EmployeeSummarySerializer(employees_due, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get performance analytics"""
        queryset = self.get_queryset()
        
        # Calculate various metrics
        analytics = {
            'total_reviews': queryset.count(),
            'average_rating': queryset.aggregate(avg_rating=Avg('overall_rating'))['avg_rating'] or 0,
            'rating_distribution': {
                'exceptional': queryset.filter(overall_rating__gte=4.5).count(),
                'outstanding': queryset.filter(overall_rating__gte=3.5, overall_rating__lt=4.5).count(),
                'meets_expectations': queryset.filter(overall_rating__gte=2.5, overall_rating__lt=3.5).count(),
                'needs_improvement': queryset.filter(overall_rating__lt=2.5).count(),
            },
            'reviews_by_period': dict(
                queryset.values('review_period')
                .annotate(count=Count('id'))
                .values_list('review_period', 'count')
            )
        }
        
        return Response(analytics)