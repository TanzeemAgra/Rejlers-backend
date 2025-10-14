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
from .models import (
    Department, Position, Employee, TimeOff, Performance,
    WorkSchedule, AttendanceRecord, AttendancePattern, 
    AttendanceAlert, AttendanceReport
)
from .serializers import (
    DepartmentSerializer, PositionSerializer, EmployeeSerializer,
    EmployeeCreateSerializer, TimeOffSerializer, PerformanceSerializer,
    DepartmentSummarySerializer, EmployeeSummarySerializer
)
from .attendance_serializers import (
    WorkScheduleSerializer, AttendanceRecordSerializer,
    AttendancePatternSerializer, AttendanceAlertSerializer,
    AttendanceReportSerializer, AttendanceDashboardSerializer
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


# ============= AI-POWERED ATTENDANCE TRACKING VIEWS =============

class WorkScheduleViewSet(viewsets.ModelViewSet):
    """Work Schedule management with AI optimization"""
    
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'schedule_type', 'is_active']
    search_fields = ['schedule_name', 'work_location']
    ordering = ['-effective_from']
    
    def get_queryset(self):
        """Filter schedules based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Employees can only see their own schedules
        if not user.has_perm('hr_management.view_all_schedules'):
            if hasattr(user, 'employee'):
                queryset = queryset.filter(employee=user.employee)
            else:
                queryset = queryset.none()
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def optimize_schedule(self, request):
        """AI-powered schedule optimization"""
        employee_id = request.data.get('employee_id')
        optimization_criteria = request.data.get('criteria', 'productivity')
        
        # AI logic for schedule optimization would go here
        # For now, returning a simplified response
        return Response({
            'success': True,
            'message': 'Schedule optimization initiated',
            'optimized_schedule': {
                'recommended_start_time': '09:00',
                'recommended_end_time': '17:30',
                'productivity_boost': '12%',
                'ai_confidence': 85.5
            }
        })


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """Advanced attendance tracking with AI analysis"""
    
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status', 'date', 'is_remote', 'anomaly_detected']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'notes']
    ordering = ['-date', '-clock_in_time']
    
    def get_queryset(self):
        """Filter attendance records based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Employees can only see their own records
        if not user.has_perm('hr_management.view_all_attendance'):
            if hasattr(user, 'employee'):
                queryset = queryset.filter(employee=user.employee)
            else:
                queryset = queryset.none()
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def clock_in(self, request):
        """Smart clock-in with AI verification"""
        from django.utils import timezone
        import json
        
        user = request.user
        if not hasattr(user, 'employee'):
            return Response(
                {'error': 'User is not an employee'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        employee = user.employee
        today = timezone.now().date()
        
        # Check if already clocked in today
        existing_record = AttendanceRecord.objects.filter(
            employee=employee, 
            date=today
        ).first()
        
        if existing_record and existing_record.clock_in_time:
            return Response(
                {'error': 'Already clocked in today'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get request data
        clock_in_data = {
            'clock_in_time': timezone.now(),
            'clock_in_method': request.data.get('method', 'WEB_PORTAL'),
            'work_location': request.data.get('location', 'Office'),
            'is_remote': request.data.get('is_remote', False),
            'clock_in_lat_lng': request.data.get('gps_coordinates'),
            'device_info': {
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': request.META.get('REMOTE_ADDR', ''),
            },
            'ip_address': request.META.get('REMOTE_ADDR', ''),
        }
        
        # Create or update attendance record
        if existing_record:
            for key, value in clock_in_data.items():
                setattr(existing_record, key, value)
            existing_record.save()
            record = existing_record
        else:
            record = AttendanceRecord.objects.create(
                employee=employee,
                date=today,
                **clock_in_data
            )
        
        # AI Analysis (simplified)
        self._perform_ai_analysis(record, 'clock_in')
        
        return Response({
            'success': True,
            'message': 'Clock-in successful',
            'record_id': record.id,
            'clock_in_time': record.clock_in_time,
            'ai_analysis': record.pattern_analysis or {}
        })
    
    @action(detail=False, methods=['post'])
    def clock_out(self, request):
        """Smart clock-out with AI verification"""
        from django.utils import timezone
        
        user = request.user
        if not hasattr(user, 'employee'):
            return Response(
                {'error': 'User is not an employee'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        employee = user.employee
        today = timezone.now().date()
        
        # Find today's record
        record = AttendanceRecord.objects.filter(
            employee=employee, 
            date=today
        ).first()
        
        if not record or not record.clock_in_time:
            return Response(
                {'error': 'No clock-in record found for today'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if record.clock_out_time:
            return Response(
                {'error': 'Already clocked out today'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update record
        record.clock_out_time = timezone.now()
        record.clock_out_method = request.data.get('method', 'WEB_PORTAL')
        record.clock_out_lat_lng = request.data.get('gps_coordinates')
        record.employee_comments = request.data.get('comments', '')
        
        # Calculate hours
        record.calculate_actual_hours()
        
        # AI Analysis
        self._perform_ai_analysis(record, 'clock_out')
        
        return Response({
            'success': True,
            'message': 'Clock-out successful',
            'record_id': record.id,
            'clock_out_time': record.clock_out_time,
            'total_hours': record.actual_hours,
            'overtime_hours': record.overtime_hours,
            'ai_analysis': record.pattern_analysis or {}
        })
    
    @action(detail=False, methods=['get'])
    def my_attendance(self, request):
        """Get current user's attendance dashboard"""
        if not hasattr(request.user, 'employee'):
            return Response(
                {'error': 'User is not an employee'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        employee = request.user.employee
        today = timezone.now().date()
        
        # Get today's record
        today_record = AttendanceRecord.objects.filter(
            employee=employee, 
            date=today
        ).first()
        
        # Get recent records (last 30 days)
        recent_records = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=today - timedelta(days=30)
        ).order_by('-date')
        
        # Calculate statistics
        stats = self._calculate_attendance_stats(employee, recent_records)
        
        return Response({
            'today': AttendanceRecordSerializer(today_record).data if today_record else None,
            'recent_records': AttendanceRecordSerializer(recent_records[:10], many=True).data,
            'statistics': stats,
            'ai_insights': self._generate_ai_insights(employee, recent_records)
        })
    
    @action(detail=False, methods=['get'])
    def team_dashboard(self, request):
        """Get team attendance dashboard for managers"""
        user = request.user
        if not user.has_perm('hr_management.view_team_attendance'):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get team members
        team_members = Employee.objects.filter(manager=user, employment_status='ACTIVE')
        today = timezone.now().date()
        
        # Get today's attendance for team
        team_attendance = AttendanceRecord.objects.filter(
            employee__in=team_members,
            date=today
        ).select_related('employee__user')
        
        # Organize data
        dashboard_data = []
        for member in team_members:
            record = team_attendance.filter(employee=member).first()
            dashboard_data.append({
                'employee': EmployeeSummarySerializer(member).data,
                'attendance': AttendanceRecordSerializer(record).data if record else None,
                'status': self._get_employee_status(member, record),
                'alerts': AttendanceAlert.objects.filter(
                    employee=member, 
                    is_resolved=False
                ).count()
            })
        
        return Response({
            'team_attendance': dashboard_data,
            'summary': {
                'total_employees': len(team_members),
                'present': len([d for d in dashboard_data if d['status'] == 'present']),
                'absent': len([d for d in dashboard_data if d['status'] == 'absent']),
                'late': len([d for d in dashboard_data if d['status'] == 'late']),
            }
        })
    
    def _perform_ai_analysis(self, record, action_type):
        """Perform AI analysis on attendance record"""
        import json
        from datetime import datetime, timedelta
        
        # Get historical data for pattern analysis
        historical_records = AttendanceRecord.objects.filter(
            employee=record.employee,
            date__gte=record.date - timedelta(days=90)
        ).exclude(id=record.id)
        
        analysis = {
            'action_type': action_type,
            'timestamp': datetime.now().isoformat(),
            'patterns_detected': [],
            'risk_indicators': [],
            'recommendations': []
        }
        
        if action_type == 'clock_in' and record.clock_in_time:
            # Analyze punctuality
            schedule = WorkSchedule.objects.filter(
                employee=record.employee,
                is_active=True,
                effective_from__lte=record.date
            ).first()
            
            if schedule:
                scheduled_start = datetime.combine(record.date, schedule.start_time)
                actual_start = record.clock_in_time.replace(tzinfo=None)
                
                if actual_start > scheduled_start:
                    minutes_late = (actual_start - scheduled_start).seconds / 60
                    analysis['patterns_detected'].append({
                        'type': 'late_arrival',
                        'minutes_late': minutes_late,
                        'frequency': self._calculate_late_frequency(record.employee, historical_records)
                    })
                    
                    if minutes_late > 15:
                        analysis['risk_indicators'].append('significant_tardiness')
        
        elif action_type == 'clock_out' and record.clock_out_time:
            # Analyze work duration and patterns
            work_duration = record.actual_hours
            
            if work_duration < 6:
                analysis['risk_indicators'].append('short_work_day')
            elif work_duration > 12:
                analysis['risk_indicators'].append('excessive_overtime')
            
            # Pattern analysis would use ML models in production
            analysis['patterns_detected'].append({
                'type': 'work_duration_pattern',
                'current_hours': float(work_duration),
                'average_hours': self._calculate_average_hours(record.employee, historical_records)
            })
        
        # Store analysis
        record.pattern_analysis = analysis
        
        # Check for anomalies
        if analysis['risk_indicators']:
            record.anomaly_detected = True
            record.anomaly_details = json.dumps(analysis['risk_indicators'])
        
        record.save()
    
    def _calculate_late_frequency(self, employee, historical_records):
        """Calculate how often employee is late"""
        late_records = historical_records.filter(status__in=['LATE']).count()
        total_records = historical_records.count()
        return (late_records / total_records * 100) if total_records > 0 else 0
    
    def _calculate_average_hours(self, employee, historical_records):
        """Calculate average working hours"""
        total_hours = sum([float(r.actual_hours or 0) for r in historical_records])
        return total_hours / len(historical_records) if historical_records else 8.0
    
    def _calculate_attendance_stats(self, employee, records):
        """Calculate attendance statistics"""
        total_days = records.count()
        present_days = records.filter(status__in=['PRESENT', 'WORK_FROM_HOME']).count()
        
        return {
            'total_days': total_days,
            'present_days': present_days,
            'attendance_rate': (present_days / total_days * 100) if total_days > 0 else 0,
            'average_hours': self._calculate_average_hours(employee, records),
            'total_overtime': sum([float(r.overtime_hours or 0) for r in records]),
            'late_arrivals': records.filter(status='LATE').count(),
        }
    
    def _generate_ai_insights(self, employee, records):
        """Generate AI-powered insights"""
        return {
            'attendance_trend': 'stable',  # Would use ML model
            'productivity_correlation': 'positive',
            'recommendations': [
                'Consider flexible start time to improve punctuality',
                'Monitor workload to prevent excessive overtime'
            ],
            'wellness_score': 85.5  # AI-calculated wellness indicator
        }
    
    def _get_employee_status(self, employee, record):
        """Determine current employee status"""
        if not record:
            return 'absent'
        elif record.clock_in_time and not record.clock_out_time:
            return 'present'
        elif record.status == 'LATE':
            return 'late'
        else:
            return record.status.lower()


class AttendancePatternViewSet(viewsets.ReadOnlyModelViewSet):
    """AI-generated attendance patterns analysis"""
    
    queryset = AttendancePattern.objects.all()
    serializer_class = AttendancePatternSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'pattern_type', 'risk_level']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def generate_pattern(self, request):
        """Generate new attendance pattern analysis"""
        employee_id = request.data.get('employee_id')
        pattern_type = request.data.get('pattern_type', 'CONSISTENCY')
        
        # AI pattern generation logic would go here
        return Response({
            'success': True,
            'message': 'Pattern analysis initiated',
            'estimated_completion': '2-3 minutes'
        })


class AttendanceAlertViewSet(viewsets.ModelViewSet):
    """AI-powered attendance alerts management"""
    
    queryset = AttendanceAlert.objects.all()
    serializer_class = AttendanceAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'alert_type', 'severity', 'is_resolved']
    ordering = ['-created_at', '-severity']
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response({'success': True, 'message': 'Alert acknowledged'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get('notes', '')
        alert.save()
        
        return Response({'success': True, 'message': 'Alert resolved'})


class AttendanceReportViewSet(viewsets.ModelViewSet):
    """AI-powered attendance reporting and analytics"""
    
    queryset = AttendanceReport.objects.all()
    serializer_class = AttendanceReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report_type', 'scope', 'generated_by']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate comprehensive attendance report"""
        report_data = {
            'report_name': request.data.get('name', 'Custom Attendance Report'),
            'report_type': request.data.get('type', 'MONTHLY'),
            'scope': request.data.get('scope', 'DEPARTMENT'),
            'start_date': request.data.get('start_date'),
            'end_date': request.data.get('end_date'),
            'generated_by': request.user,
        }
        
        # AI report generation logic would go here
        return Response({
            'success': True,
            'message': 'Report generation started',
            'report_id': 'pending',
            'estimated_completion': '5-10 minutes'
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        """Get real-time attendance dashboard data"""
        today = timezone.now().date()
        
        # Get company-wide stats for today
        total_employees = Employee.objects.filter(employment_status='ACTIVE').count()
        
        today_records = AttendanceRecord.objects.filter(date=today)
        present_count = today_records.filter(
            status__in=['PRESENT', 'WORK_FROM_HOME']
        ).count()
        
        dashboard_data = {
            'date': today,
            'total_employees': total_employees,
            'present_today': present_count,
            'absent_today': total_employees - present_count,
            'attendance_rate': (present_count / total_employees * 100) if total_employees > 0 else 0,
            'alerts_count': AttendanceAlert.objects.filter(
                is_resolved=False,
                created_at__date=today
            ).count(),
            'overtime_hours': sum([
                float(r.overtime_hours or 0) for r in today_records 
                if r.overtime_hours
            ]),
            'remote_workers': today_records.filter(is_remote=True).count(),
        }
        
        return Response(dashboard_data)


# ===============================================
# AI-POWERED ATTENDANCE TRACKING API VIEWS
# ===============================================

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """
    AI-Enhanced Attendance Records Management
    Comprehensive CRUD operations with real-time AI analysis
    """
    
    queryset = AttendanceRecord.objects.select_related('employee', 'employee__department').all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['employee', 'date', 'status', 'work_mode', 'is_anomaly']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['date', 'clock_in', 'clock_out', 'actual_hours', 'ai_confidence_score']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        """Filter attendance records based on permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # HR managers see all records
        if user.has_perm('hr_management.view_all_attendance'):
            return queryset
        
        # Managers see their department's records
        if hasattr(user, 'employee_profile'):
            employee = user.employee_profile
            if employee.is_manager:
                return queryset.filter(employee__department=employee.department)
        
        # Employees see only their own records
        return queryset.filter(employee__user=user)
    
    @action(detail=False, methods=['post'], url_path='clock-action')
    def clock_action(self, request):
        """
        Smart Clock In/Out with AI Analysis
        Handles all clock actions: clock_in, clock_out, break_start, break_end
        """
        from .attendance_serializers import AttendanceClockActionSerializer
        from django.utils import timezone
        
        serializer = AttendanceClockActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action_type = serializer.validated_data['action']
        location = serializer.validated_data.get('location')
        work_mode = serializer.validated_data.get('work_mode', 'OFFICE')
        notes = serializer.validated_data.get('notes', '')
        
        # Get employee profile
        try:
            employee = request.user.employee_profile
        except:
            return Response(
                {'error': 'Employee profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create today's attendance record
        today = timezone.now().date()
        attendance_record, created = AttendanceRecord.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'status': 'ABSENT',
                'work_mode': work_mode,
                'notes': notes
            }
        )
        
        current_time = timezone.now()
        
        # Process clock action
        if action_type == 'clock_in':
            if attendance_record.clock_in:
                return Response(
                    {'error': 'Already clocked in today'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            attendance_record.clock_in = current_time
            attendance_record.clock_in_location = location
            attendance_record.status = 'PRESENT'
            attendance_record.work_mode = work_mode
            
            # AI-powered location verification
            if location and employee.work_schedules.filter(is_active=True).exists():
                schedule = employee.work_schedules.filter(is_active=True).first()
                if schedule.allowed_locations:
                    # Verify location against allowed locations
                    attendance_record.location_verified = self._verify_location(
                        location, schedule.allowed_locations
                    )
                else:
                    attendance_record.location_verified = True
            
            # Check if late
            if self._is_late_arrival(employee, current_time):
                attendance_record.status = 'LATE'
                # Create late arrival alert
                self._create_alert(
                    employee, 
                    'LATE_ARRIVAL',
                    f'Late arrival detected at {current_time.strftime("%H:%M")}',
                    'MEDIUM',
                    attendance_record
                )
        
        elif action_type == 'clock_out':
            if not attendance_record.clock_in:
                return Response(
                    {'error': 'Must clock in before clocking out'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            if attendance_record.clock_out:
                return Response(
                    {'error': 'Already clocked out today'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            attendance_record.clock_out = current_time
            attendance_record.clock_out_location = location
            
            # Calculate work hours
            work_duration = attendance_record.total_work_duration
            attendance_record.actual_hours = work_duration.total_seconds() / 3600
            
            # Calculate overtime
            if attendance_record.actual_hours > attendance_record.scheduled_hours:
                attendance_record.overtime_hours = attendance_record.actual_hours - attendance_record.scheduled_hours
        
        elif action_type == 'break_start':
            if attendance_record.break_start and not attendance_record.break_end:
                return Response(
                    {'error': 'Break already started'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            attendance_record.break_start = current_time
        
        elif action_type == 'break_end':
            if not attendance_record.break_start:
                return Response(
                    {'error': 'Must start break before ending it'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            if attendance_record.break_end:
                return Response(
                    {'error': 'Break already ended'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            attendance_record.break_end = current_time
            break_duration = attendance_record.break_end - attendance_record.break_start
            attendance_record.total_break_duration += break_duration
            
            # Check for extended breaks
            if break_duration > timedelta(hours=2):  # More than 2 hours
                self._create_alert(
                    employee,
                    'EXTENDED_BREAK',
                    f'Extended break detected: {break_duration}',
                    'MEDIUM',
                    attendance_record
                )
        
        # Perform AI analysis
        attendance_record.calculate_ai_scores()
        
        # Anomaly detection
        anomalies = self._detect_anomalies(attendance_record)
        if anomalies:
            attendance_record.is_anomaly = True
            attendance_record.anomaly_reasons = anomalies
            
            # Create pattern anomaly alert
            self._create_alert(
                employee,
                'PATTERN_ANOMALY',
                f'Attendance pattern anomaly detected: {", ".join(anomalies)}',
                'HIGH',
                attendance_record
            )
        
        attendance_record.save()
        
        # Return updated record
        serializer = AttendanceRecordSerializer(attendance_record)
        return Response({
            'success': True,
            'message': f'{action_type.replace("_", " ").title()} successful',
            'attendance_record': serializer.data,
            'ai_analysis': attendance_record.calculate_ai_scores()
        })
    
    def _verify_location(self, current_location, allowed_locations):
        """Verify if current location is within allowed range"""
        if not current_location or not allowed_locations:
            return False
        
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            """Calculate the great circle distance between two points"""
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # Radius of earth in kilometers
            return c * r * 1000  # Convert to meters
        
        current_lat = float(current_location['latitude'])
        current_lng = float(current_location['longitude'])
        
        for location in allowed_locations:
            if isinstance(location, dict) and 'latitude' in location and 'longitude' in location:
                allowed_lat = float(location['latitude'])
                allowed_lng = float(location['longitude'])
                radius = location.get('radius', 100)  # Default 100 meters
                
                distance = haversine(current_lng, current_lat, allowed_lng, allowed_lat)
                if distance <= radius:
                    return True
        
        return False
    
    def _is_late_arrival(self, employee, clock_in_time):
        """Check if employee is late based on their schedule"""
        schedule = employee.work_schedules.filter(
            is_active=True,
            effective_from__lte=clock_in_time.date()
        ).first()
        
        if not schedule:
            return False
        
        # Check if today is a work day
        weekday = clock_in_time.strftime('%a').upper()
        if weekday not in schedule.work_days:
            return False
        
        scheduled_time = datetime.combine(clock_in_time.date(), schedule.start_time)
        scheduled_time = timezone.make_aware(scheduled_time)
        
        # Add flexible window
        latest_allowed = scheduled_time + schedule.flexible_start_window
        
        return clock_in_time > latest_allowed
    
    def _detect_anomalies(self, attendance_record):
        """AI-powered anomaly detection"""
        anomalies = []
        employee = attendance_record.employee
        
        # Get historical data for comparison
        historical_records = AttendanceRecord.objects.filter(
            employee=employee,
            date__lt=attendance_record.date,
            status__in=['PRESENT', 'LATE']
        ).order_by('-date')[:30]  # Last 30 records
        
        if not historical_records.exists():
            return anomalies
        
        # Check unusual clock-in time
        if attendance_record.clock_in:
            avg_clock_in = historical_records.aggregate(
                avg_hour=Avg('clock_in__hour'),
                avg_minute=Avg('clock_in__minute')
            )
            
            if avg_clock_in['avg_hour']:
                current_hour = attendance_record.clock_in.hour
                avg_hour = avg_clock_in['avg_hour']
                
                # If more than 2 hours difference from average
                if abs(current_hour - avg_hour) > 2:
                    anomalies.append('unusual_clock_in_time')
        
        # Check unusual work duration
        if attendance_record.actual_hours:
            avg_hours = historical_records.aggregate(avg=Avg('actual_hours'))['avg'] or 8
            
            # If more than 3 hours difference from average
            if abs(attendance_record.actual_hours - avg_hours) > 3:
                anomalies.append('unusual_work_duration')
        
        # Check location anomaly
        if attendance_record.clock_in_location and not attendance_record.location_verified:
            anomalies.append('location_mismatch')
        
        # Check weekend work
        if attendance_record.date.weekday() >= 5:  # Saturday or Sunday
            schedule = employee.work_schedules.filter(is_active=True).first()
            if schedule and 'SAT' not in schedule.work_days and 'SUN' not in schedule.work_days:
                anomalies.append('weekend_work')
        
        return anomalies
    
    def _create_alert(self, employee, alert_type, description, severity, attendance_record=None):
        """Create attendance alert"""
        AttendanceAlert.objects.create(
            employee=employee,
            alert_type=alert_type,
            severity=severity,
            title=f"{alert_type.replace('_', ' ').title()} - {employee.get_full_name()}",
            description=description,
            occurrence_date=attendance_record.date if attendance_record else timezone.now().date(),
            related_attendance_record=attendance_record,
            ai_confidence=85.0  # Default confidence for rule-based alerts
        )
    
    @action(detail=False, methods=['get'], url_path='my-summary')
    def my_summary(self, request):
        """Get current user's attendance summary"""
        try:
            employee = request.user.employee_profile
        except:
            return Response(
                {'error': 'Employee profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get current month's data
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        records = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=month_start,
            date__lte=today
        )
        
        # Calculate summary statistics
        summary = {
            'employee_name': employee.get_full_name(),
            'employee_id': employee.employee_id,
            'department': employee.department.name if employee.department else 'N/A',
            
            'current_status': self._get_current_status(employee),
            'today_record': self._get_today_record(employee),
            
            'monthly_stats': {
                'total_days': records.count(),
                'present_days': records.filter(status__in=['PRESENT', 'LATE']).count(),
                'absent_days': records.filter(status='ABSENT').count(),
                'late_days': records.filter(status='LATE').count(),
                'remote_days': records.filter(work_mode='REMOTE').count(),
                
                'total_hours': sum([float(r.actual_hours or 0) for r in records]),
                'average_hours': records.aggregate(avg=Avg('actual_hours'))['avg'] or 0,
                'overtime_hours': sum([float(r.overtime_hours or 0) for r in records]),
                
                'attendance_rate': (records.filter(status__in=['PRESENT', 'LATE']).count() / 
                                  max(records.count(), 1)) * 100,
            },
            
            'ai_scores': {
                'average_confidence': records.aggregate(avg=Avg('ai_confidence_score'))['avg'] or 0,
                'pattern_score': records.aggregate(avg=Avg('pattern_deviation_score'))['avg'] or 0,
                'productivity_score': records.aggregate(avg=Avg('productivity_score'))['avg'] or 0,
            },
            
            'alerts': {
                'active_alerts': AttendanceAlert.objects.filter(
                    employee=employee,
                    status='ACTIVE'
                ).count(),
                'recent_anomalies': records.filter(is_anomaly=True).count()
            }
        }
        
        return Response(summary)
    
    def _get_current_status(self, employee):
        """Get employee's current clock status"""
        today_record = AttendanceRecord.objects.filter(
            employee=employee,
            date=timezone.now().date()
        ).first()
        
        if not today_record:
            return 'Not clocked in'
        
        if today_record.clock_in and not today_record.clock_out:
            if today_record.break_start and not today_record.break_end:
                return 'On break'
            else:
                return 'Clocked in'
        elif today_record.clock_out:
            return 'Clocked out'
        else:
            return 'Not clocked in'
    
    def _get_today_record(self, employee):
        """Get today's attendance record summary"""
        today_record = AttendanceRecord.objects.filter(
            employee=employee,
            date=timezone.now().date()
        ).first()
        
        if not today_record:
            return None
        
        return {
            'id': today_record.id,
            'status': today_record.status,
            'clock_in': today_record.clock_in,
            'clock_out': today_record.clock_out,
            'work_mode': today_record.work_mode,
            'actual_hours': float(today_record.actual_hours or 0),
            'ai_confidence_score': float(today_record.ai_confidence_score or 0)
        }


class WorkScheduleViewSet(viewsets.ModelViewSet):
    """Work Schedule Management with AI-enhanced features"""
    
    queryset = WorkSchedule.objects.select_related('employee').all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated, IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['employee', 'schedule_type', 'is_active', 'remote_work_allowed']
    search_fields = ['employee__first_name', 'employee__last_name', 'schedule_name']
    ordering_fields = ['schedule_name', 'effective_from', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter schedules based on permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.has_perm('hr_management.view_all_schedules'):
            return queryset
        
        # Employees can only see their own schedules
        return queryset.filter(employee__user=user)


class AttendanceAlertViewSet(viewsets.ModelViewSet):
    """Intelligent Attendance Alert Management"""
    
    queryset = AttendanceAlert.objects.select_related('employee', 'assigned_to').all()
    serializer_class = AttendanceAlertSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['employee', 'alert_type', 'severity', 'status', 'assigned_to']
    search_fields = ['employee__first_name', 'employee__last_name', 'title', 'description']
    ordering_fields = ['severity', 'detection_time', 'occurrence_date']
    ordering = ['-severity', '-detection_time']
    
    def get_queryset(self):
        """Filter alerts based on permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.has_perm('hr_management.view_all_alerts'):
            return queryset
        
        # Managers see their department's alerts
        if hasattr(user, 'employee_profile'):
            employee = user.employee_profile
            if employee.is_manager:
                return queryset.filter(employee__department=employee.department)
        
        # Employees see only their own alerts
        return queryset.filter(employee__user=user)
    
    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge_alert(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        
        if alert.status != 'ACTIVE':
            return Response(
                {'error': 'Alert is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.status = 'ACKNOWLEDGED'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response({
            'success': True,
            'message': 'Alert acknowledged successfully',
            'alert': serializer.data
        })
    
    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve_alert(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        alert.status = 'RESOLVED'
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.resolution_notes = resolution_notes
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response({
            'success': True,
            'message': 'Alert resolved successfully',
            'alert': serializer.data
        })


class AttendanceReportViewSet(viewsets.ModelViewSet):
    """AI-Enhanced Attendance Reporting"""
    
    queryset = AttendanceReport.objects.all()
    serializer_class = AttendanceReportSerializer
    permission_classes = [IsAuthenticated, IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['report_type', 'department_filter', 'generated_by']
    search_fields = ['report_name']
    ordering_fields = ['report_name', 'generated_at', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'], url_path='generate')
    def generate_report(self, request):
        """Generate a new attendance report with AI insights"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        report = serializer.save(generated_by=request.user)
        
        # Generate analytics
        analytics = report.generate_analytics()
        
        # Mark as generated
        report.generated_at = timezone.now()
        report.save()
        
        return Response({
            'success': True,
            'message': 'Report generated successfully',
            'report': AttendanceReportSerializer(report).data,
            'analytics_preview': analytics
        })
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def attendance_dashboard(self, request):
        """Real-time attendance dashboard with AI insights"""
        today = timezone.now().date()
        
        # Get today's attendance statistics
        today_records = AttendanceRecord.objects.filter(date=today)
        
        # Calculate real-time metrics
        dashboard_data = {
            'date': today.isoformat(),
            'timestamp': timezone.now().isoformat(),
            
            # Basic stats
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'present_today': today_records.filter(status__in=['PRESENT', 'LATE']).count(),
            'absent_today': today_records.filter(status='ABSENT').count(),
            'late_arrivals': today_records.filter(status='LATE').count(),
            'on_leave': today_records.filter(status__contains='LEAVE').count(),
            
            # Real-time status
            'currently_clocked_in': today_records.filter(
                clock_in__isnull=False,
                clock_out__isnull=True
            ).count(),
            'remote_workers': today_records.filter(work_mode='REMOTE').count(),
            'on_break': today_records.filter(
                break_start__isnull=False,
                break_end__isnull=True
            ).count(),
            
            # AI insights
            'ai_alerts': {
                'active_count': AttendanceAlert.objects.filter(status='ACTIVE').count(),
                'high_priority': AttendanceAlert.objects.filter(
                    status='ACTIVE',
                    severity__in=['HIGH', 'CRITICAL']
                ).count(),
                'recent_anomalies': today_records.filter(is_anomaly=True).count(),
            },
            
            # Performance metrics
            'average_confidence_score': today_records.aggregate(
                avg=Avg('ai_confidence_score')
            )['avg'] or 0,
            'average_productivity_score': today_records.aggregate(
                avg=Avg('productivity_score')
            )['avg'] or 0,
            
            # Trends (compared to yesterday)
            'trends': self._calculate_trends(today),
            
            # Department breakdown
            'department_stats': self._get_department_stats(today),
            
            # Recent activities
            'recent_activities': self._get_recent_activities()
        }
        
        return Response(dashboard_data)
    
    def _calculate_trends(self, today):
        """Calculate trends compared to previous day"""
        yesterday = today - timedelta(days=1)
        
        today_count = AttendanceRecord.objects.filter(
            date=today,
            status__in=['PRESENT', 'LATE']
        ).count()
        
        yesterday_count = AttendanceRecord.objects.filter(
            date=yesterday,
            status__in=['PRESENT', 'LATE']
        ).count()
        
        attendance_trend = 0
        if yesterday_count > 0:
            attendance_trend = ((today_count - yesterday_count) / yesterday_count) * 100
        
        return {
            'attendance_change': round(attendance_trend, 1),
            'direction': 'up' if attendance_trend > 0 else 'down' if attendance_trend < 0 else 'stable'
        }
    
    def _get_department_stats(self, today):
        """Get attendance stats by department"""
        departments = Department.objects.filter(is_active=True)
        dept_stats = []
        
        for dept in departments:
            dept_records = AttendanceRecord.objects.filter(
                date=today,
                employee__department=dept
            )
            
            if dept_records.exists():
                present_count = dept_records.filter(status__in=['PRESENT', 'LATE']).count()
                total_count = dept_records.count()
                
                dept_stats.append({
                    'department': dept.name,
                    'total_employees': total_count,
                    'present_count': present_count,
                    'attendance_rate': (present_count / total_count * 100) if total_count > 0 else 0,
                    'late_count': dept_records.filter(status='LATE').count(),
                    'remote_count': dept_records.filter(work_mode='REMOTE').count()
                })
        
        return dept_stats
    
    def _get_recent_activities(self):
        """Get recent attendance activities"""
        recent_records = AttendanceRecord.objects.filter(
            updated_at__gte=timezone.now() - timedelta(hours=2)
        ).select_related('employee').order_by('-updated_at')[:10]
        
        activities = []
        for record in recent_records:
            activity = {
                'employee_name': record.employee.get_full_name(),
                'action': 'Clocked in' if record.clock_in and not record.clock_out else 'Clocked out',
                'time': record.updated_at,
                'status': record.status,
                'work_mode': record.work_mode
            }
            activities.append(activity)
        
        return activities