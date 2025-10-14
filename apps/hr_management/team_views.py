from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import AttendanceRecord, PunchRecord, User
from .serializers import EmployeeSerializer
import json

class TeamDashboardViewSet(viewsets.ViewSet):
    """
    Team Dashboard API endpoints for managers and HR
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def team_stats(self, request):
        """Get comprehensive team statistics"""
        today = timezone.now().date()
        department = request.query_params.get('department')
        team_id = request.query_params.get('team_id')

        # Base queryset for employees
        employees_query = User.objects.filter(is_active=True)
        if department:
            employees_query = employees_query.filter(department=department)
        if team_id:
            employees_query = employees_query.filter(team_id=team_id)

        total_employees = employees_query.count()

        # Today's attendance
        today_attendance = AttendanceRecord.objects.filter(
            date=today,
            employee__in=employees_query
        )

        present_today = today_attendance.filter(status='present').count()
        absent_today = today_attendance.filter(status='absent').count()
        late_today = today_attendance.filter(status='late').count()

        # Calculate average attendance rate
        avg_attendance = AttendanceRecord.objects.filter(
            employee__in=employees_query,
            date__gte=today - timedelta(days=30)
        ).aggregate(
            avg_rate=Avg('attendance_percentage')
        )['avg_rate'] or 0

        # Calculate average productivity
        avg_productivity = AttendanceRecord.objects.filter(
            employee__in=employees_query,
            date__gte=today - timedelta(days=30)
        ).aggregate(
            avg_prod=Avg('productivity_score')
        )['avg_prod'] or 0

        # Total overtime
        total_overtime = AttendanceRecord.objects.filter(
            employee__in=employees_query,
            date=today
        ).aggregate(
            total_ot=Sum('overtime_hours')
        )['total_ot'] or 0

        # Alert count (simplified)
        alert_count = today_attendance.filter(
            Q(status='absent') | Q(status='late')
        ).count()

        return Response({
            'totalEmployees': total_employees,
            'presentToday': present_today,
            'absentToday': absent_today,
            'lateToday': late_today,
            'avgAttendanceRate': round(avg_attendance, 1),
            'avgProductivity': round(avg_productivity, 1),
            'totalOvertime': round(total_overtime, 1),
            'alertCount': alert_count
        })

    @action(detail=False, methods=['get'])
    def team_members(self, request):
        """Get detailed team member information"""
        today = timezone.now().date()
        department = request.query_params.get('department')
        team_id = request.query_params.get('team_id')
        
        # Base queryset for employees
        employees_query = User.objects.filter(is_active=True)
        if department:
            employees_query = employees_query.filter(department=department)
        if team_id:
            employees_query = employees_query.filter(team_id=team_id)

        team_members = []
        
        for employee in employees_query:
            # Get today's attendance record
            attendance_record = AttendanceRecord.objects.filter(
                employee=employee,
                date=today
            ).first()

            # Get latest punch records
            punch_records = PunchRecord.objects.filter(
                attendance_record=attendance_record
            ).order_by('timestamp') if attendance_record else []

            check_in_time = None
            check_out_time = None
            
            if punch_records:
                check_in_time = punch_records.first().timestamp.strftime('%H:%M')
                if punch_records.filter(punch_type='out').exists():
                    check_out_time = punch_records.filter(punch_type='out').last().timestamp.strftime('%H:%M')

            # Calculate attendance rate (last 30 days)
            attendance_rate = AttendanceRecord.objects.filter(
                employee=employee,
                date__gte=today - timedelta(days=30)
            ).aggregate(
                avg_rate=Avg('attendance_percentage')
            )['avg_rate'] or 0

            # Calculate productivity (last 30 days)
            productivity = AttendanceRecord.objects.filter(
                employee=employee,
                date__gte=today - timedelta(days=30)
            ).aggregate(
                avg_prod=Avg('productivity_score')
            )['avg_prod'] or 0

            member_data = {
                'id': str(employee.id),
                'name': employee.get_full_name(),
                'email': employee.email,
                'department': getattr(employee, 'department', 'Unknown'),
                'position': getattr(employee, 'position', 'Employee'),
                'avatar': getattr(employee, 'avatar', '').url if getattr(employee, 'avatar', None) else '',
                'status': attendance_record.status if attendance_record else 'absent',
                'checkInTime': check_in_time,
                'checkOutTime': check_out_time,
                'scheduledStart': '09:00',  # Default - can be made dynamic
                'scheduledEnd': '17:00',   # Default - can be made dynamic
                'totalHours': attendance_record.hours_worked if attendance_record else 0,
                'overtimeHours': attendance_record.overtime_hours if attendance_record else 0,
                'attendanceRate': round(attendance_rate, 0),
                'productivity': round(productivity, 0)
            }
            
            team_members.append(member_data)

        return Response(team_members)

    @action(detail=False, methods=['get'])
    def ai_insights(self, request):
        """Get AI-generated insights and recommendations"""
        department = request.query_params.get('department')
        team_id = request.query_params.get('team_id')
        insight_type = request.query_params.get('type', 'all')

        # Mock AI insights - replace with actual AI analysis
        insights = []

        today = timezone.now().date()
        
        # Base queryset for employees
        employees_query = User.objects.filter(is_active=True)
        if department:
            employees_query = employees_query.filter(department=department)
        if team_id:
            employees_query = employees_query.filter(team_id=team_id)

        # Analyze absence patterns
        absent_employees = AttendanceRecord.objects.filter(
            date__gte=today - timedelta(days=7),
            status='absent',
            employee__in=employees_query
        ).values('employee').annotate(
            absent_count=Count('id')
        ).filter(absent_count__gte=2)

        for absent_emp in absent_employees:
            employee = User.objects.get(id=absent_emp['employee'])
            insights.append({
                'id': f"abs_{employee.id}",
                'type': 'alert',
                'severity': 'high' if absent_emp['absent_count'] >= 3 else 'medium',
                'title': 'Unusual Absence Pattern',
                'description': f"{employee.get_full_name()} has been absent {absent_emp['absent_count']} days this week.",
                'actionable': True,
                'affectedEmployees': [str(employee.id)],
                'timestamp': timezone.now().isoformat()
            })

        # Analyze late arrival trends
        late_arrivals = AttendanceRecord.objects.filter(
            date__gte=today - timedelta(days=30),
            status='late',
            employee__in=employees_query
        ).count()

        total_records = AttendanceRecord.objects.filter(
            date__gte=today - timedelta(days=30),
            employee__in=employees_query
        ).count()

        if total_records > 0 and (late_arrivals / total_records) > 0.1:  # More than 10% late
            insights.append({
                'id': 'late_trend',
                'type': 'trend',
                'severity': 'medium',
                'title': 'Late Arrivals Increasing',
                'description': f'Team shows {round((late_arrivals / total_records) * 100, 1)}% late arrivals over the past month.',
                'actionable': True,
                'affectedEmployees': list(employees_query.values_list('id', flat=True)),
                'timestamp': timezone.now().isoformat()
            })

        # Productivity recommendation
        avg_productivity = AttendanceRecord.objects.filter(
            employee__in=employees_query,
            date__gte=today - timedelta(days=30)
        ).aggregate(
            avg_prod=Avg('productivity_score')
        )['avg_prod'] or 0

        if avg_productivity > 85:
            insights.append({
                'id': 'flex_hours',
                'type': 'recommendation',
                'severity': 'low',
                'title': 'Flexible Hours Suggestion',
                'description': 'Consider implementing flexible start times based on high productivity patterns.',
                'actionable': True,
                'affectedEmployees': list(employees_query.values_list('id', flat=True)),
                'timestamp': timezone.now().isoformat()
            })

        # Filter by type if specified
        if insight_type != 'all':
            insights = [insight for insight in insights if insight['type'] == insight_type]

        return Response(insights)

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get comprehensive analytics data for charts and graphs"""
        time_range = request.query_params.get('range', 'month')
        department = request.query_params.get('department')
        team_id = request.query_params.get('team_id')

        today = timezone.now().date()
        
        if time_range == 'week':
            start_date = today - timedelta(days=7)
        elif time_range == 'quarter':
            start_date = today - timedelta(days=90)
        else:  # month
            start_date = today - timedelta(days=30)

        # Base queryset for employees
        employees_query = User.objects.filter(is_active=True)
        if department:
            employees_query = employees_query.filter(department=department)
        if team_id:
            employees_query = employees_query.filter(team_id=team_id)

        # Attendance trend (weekly)
        attendance_trend = {
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'datasets': [{
                'label': 'Attendance Rate',
                'data': [92, 89, 94, 91],  # Mock data - calculate actual
                'backgroundColor': 'rgba(59, 130, 246, 0.5)',
                'borderColor': 'rgb(59, 130, 246)',
                'borderWidth': 2
            }]
        }

        # Department breakdown
        departments = employees_query.values_list('department', flat=True).distinct()
        dept_data = []
        dept_labels = []
        
        for dept in departments:
            if dept:
                dept_attendance = AttendanceRecord.objects.filter(
                    employee__department=dept,
                    employee__in=employees_query,
                    date__gte=start_date
                ).aggregate(
                    avg_rate=Avg('attendance_percentage')
                )['avg_rate'] or 0
                
                dept_data.append(round(dept_attendance, 0))
                dept_labels.append(dept)

        department_breakdown = {
            'labels': dept_labels,
            'datasets': [{
                'label': 'Attendance Rate',
                'data': dept_data,
                'backgroundColor': [
                    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'
                ][:len(dept_data)]
            }]
        }

        # Monthly comparison
        current_month_avg = AttendanceRecord.objects.filter(
            employee__in=employees_query,
            date__gte=today.replace(day=1)
        ).aggregate(
            avg_rate=Avg('attendance_percentage')
        )['avg_rate'] or 0

        previous_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        previous_month_avg = AttendanceRecord.objects.filter(
            employee__in=employees_query,
            date__gte=previous_month_start,
            date__lt=today.replace(day=1)
        ).aggregate(
            avg_rate=Avg('attendance_percentage')
        )['avg_rate'] or 0

        monthly_comparison = {
            'current': round(current_month_avg, 1),
            'previous': round(previous_month_avg, 1),
            'change': round(current_month_avg - previous_month_avg, 1)
        }

        # Top performers
        top_performers = []
        for employee in employees_query[:10]:  # Top 10
            current_score = AttendanceRecord.objects.filter(
                employee=employee,
                date__gte=start_date
            ).aggregate(
                avg_score=Avg('productivity_score')
            )['avg_score'] or 0

            previous_score = AttendanceRecord.objects.filter(
                employee=employee,
                date__gte=start_date - timedelta(days=30),
                date__lt=start_date
            ).aggregate(
                avg_score=Avg('productivity_score')
            )['avg_score'] or 0

            if current_score > 0:
                top_performers.append({
                    'id': str(employee.id),
                    'name': employee.get_full_name(),
                    'score': round(current_score, 1),
                    'improvement': round(current_score - previous_score, 1)
                })

        # Sort by score
        top_performers.sort(key=lambda x: x['score'], reverse=True)

        return Response({
            'attendanceTrend': attendance_trend,
            'departmentBreakdown': department_breakdown,
            'productivityMetrics': attendance_trend,  # Simplified
            'weeklyPattern': attendance_trend,       # Simplified
            'monthlyComparison': monthly_comparison,
            'topPerformers': top_performers[:4],
            'alerts': []  # Handled by ai_insights endpoint
        })

    @action(detail=False, methods=['get'])
    def employee_status(self, request):
        """Get detailed real-time employee status for manager view"""
        department = request.query_params.get('department')
        team_id = request.query_params.get('team_id')
        
        today = timezone.now().date()
        
        # Base queryset for employees
        employees_query = User.objects.filter(is_active=True)
        if department:
            employees_query = employees_query.filter(department=department)
        if team_id:
            employees_query = employees_query.filter(team_id=team_id)

        employee_statuses = []
        
        for employee in employees_query:
            # Get today's attendance and punch records
            attendance_record = AttendanceRecord.objects.filter(
                employee=employee,
                date=today
            ).first()

            punch_records = PunchRecord.objects.filter(
                attendance_record=attendance_record
            ).order_by('timestamp') if attendance_record else []

            # Determine current status and location
            status = 'absent'
            location = 'office'  # Default
            check_in_time = None
            current_task = None
            
            if attendance_record:
                status = attendance_record.status
                if punch_records:
                    check_in_time = punch_records.first().timestamp.strftime('%H:%M')
                    # Determine if still in office based on punch records
                    last_punch = punch_records.last()
                    if last_punch.punch_type == 'out':
                        status = 'absent' if status == 'present' else status

            # Mock additional data - can be enhanced with actual tracking
            productivity = attendance_record.productivity_score if attendance_record else 0
            breaks_taken = punch_records.filter(punch_type='break_start').count()
            
            employee_status = {
                'id': str(employee.id),
                'name': employee.get_full_name(),
                'email': employee.email,
                'avatar': '',
                'department': getattr(employee, 'department', 'Unknown'),
                'position': getattr(employee, 'position', 'Employee'),
                'status': status,
                'location': location,
                'checkInTime': check_in_time,
                'scheduledStart': '09:00',
                'scheduledEnd': '17:00',
                'currentTask': current_task,
                'lastActivity': '5 minutes ago',  # Mock data
                'productivity': round(productivity, 0),
                'timeInOffice': attendance_record.hours_worked if attendance_record else 0,
                'breaksTaken': breaks_taken,
                'overtime': attendance_record.overtime_hours if attendance_record else 0,
                'notes': attendance_record.notes if attendance_record else None
            }
            
            employee_statuses.append(employee_status)

        return Response(employee_statuses)