"""
AI-Powered Attendance Tracking Serializers
Advanced serializers for the attendance management system
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    WorkSchedule, AttendanceRecord, AttendancePattern,
    AttendanceAlert, AttendanceReport, Employee,
    PunchRecord, EmployeeSchedule
)

User = get_user_model()


class WorkScheduleSerializer(serializers.ModelSerializer):
    """Work schedule serializer with employee details"""
    
    employee_name = serializers.SerializerMethodField()
    schedule_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkSchedule
        fields = [
            'id', 'employee', 'employee_name', 'schedule_name', 'schedule_type',
            'days_of_week', 'start_time', 'end_time', 'break_duration_minutes',
            'flexible_start_window', 'flexible_end_window', 'minimum_hours_per_day',
            'work_location', 'remote_work_allowed', 'hybrid_days_in_office',
            'effective_from', 'effective_to', 'is_active', 'schedule_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return obj.employee.user.get_full_name()
    
    def get_schedule_summary(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')} ({obj.schedule_type})"


class PunchRecordSerializer(serializers.ModelSerializer):
    """Serializer for individual punch records"""
    
    time = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    device = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()
    
    class Meta:
        model = PunchRecord
        fields = ['id', 'time', 'type', 'location', 'device', 'verified']
    
    def get_time(self, obj):
        return obj.punch_time.strftime('%H:%M') if obj.punch_time else None
    
    def get_type(self, obj):
        return obj.punch_type
    
    def get_device(self, obj):
        return obj.device_info or 'Unknown Device'
    
    def get_verified(self, obj):
        return obj.is_verified


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Comprehensive attendance record serializer with AI insights"""
    
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    work_duration = serializers.SerializerMethodField()
    ai_score = serializers.SerializerMethodField()
    punch_records = PunchRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'department_name',
            'date', 'clock_in_time', 'clock_out_time', 'break_start_time', 'break_end_time',
            'total_break_minutes', 'scheduled_hours', 'actual_hours', 'overtime_hours',
            'status', 'status_display', 'work_location', 'is_remote',
            'clock_in_method', 'clock_out_method', 'clock_in_lat_lng', 'clock_out_lat_lng',
            'device_info', 'ip_address', 'attendance_score', 'pattern_analysis',
            'anomaly_detected', 'anomaly_details', 'manager_approved',
            'notes', 'employee_comments', 'work_duration', 'ai_score',
            'scheduled_in_time', 'scheduled_out_time', 'late_by_minutes', 'early_by_minutes',
            'punch_records', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'actual_hours', 'overtime_hours',
            'attendance_score', 'pattern_analysis', 'anomaly_detected'
        ]
    
    def get_employee_name(self, obj):
        return obj.employee.user.get_full_name()
    
    def get_employee_id(self, obj):
        return obj.employee.employee_id
    
    def get_department_name(self, obj):
        return obj.employee.department.name if obj.employee.department else None
    
    def get_status_display(self, obj):
        return dict(AttendanceRecord.STATUS_CHOICES).get(obj.status, obj.status)
    
    def get_work_duration(self, obj):
        if obj.clock_in_time and obj.clock_out_time:
            duration = obj.clock_out_time - obj.clock_in_time
            return str(duration).split('.')[0]  # Remove microseconds
        return None
    
    def get_ai_score(self, obj):
        return {
            'attendance_score': float(obj.attendance_score),
            'punctuality_rating': self._calculate_punctuality_rating(obj),
            'consistency_rating': self._calculate_consistency_rating(obj),
            'anomaly_risk': 'high' if obj.anomaly_detected else 'low'
        }
    
    def _calculate_punctuality_rating(self, obj):
        # Simplified rating - in production would use ML model
        if obj.status == 'LATE':
            return 'poor'
        elif obj.clock_in_time and hasattr(obj.employee, 'work_schedules'):
            # Check if on time based on schedule
            return 'excellent'  # Placeholder
        return 'good'
    
    def _calculate_consistency_rating(self, obj):
        # Placeholder for ML-based consistency analysis
        return 'good'


class AttendancePatternSerializer(serializers.ModelSerializer):
    """AI-generated attendance pattern serializer"""
    
    employee_name = serializers.SerializerMethodField()
    pattern_summary = serializers.SerializerMethodField()
    risk_assessment = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendancePattern
        fields = [
            'id', 'employee', 'employee_name', 'pattern_type',
            'analysis_start_date', 'analysis_end_date', 'pattern_data',
            'confidence_score', 'key_insights', 'ai_recommendations',
            'predicted_future_behavior', 'risk_level', 'pattern_summary',
            'risk_assessment', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_employee_name(self, obj):
        return obj.employee.user.get_full_name()
    
    def get_pattern_summary(self, obj):
        return f"{obj.get_pattern_type_display()} - Confidence: {obj.confidence_score}%"
    
    def get_risk_assessment(self, obj):
        return {
            'level': obj.risk_level,
            'score': float(obj.confidence_score),
            'requires_attention': obj.risk_level in ['MEDIUM', 'HIGH']
        }


class AttendanceAlertSerializer(serializers.ModelSerializer):
    """Attendance alert serializer with action items"""
    
    employee_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    alert_summary = serializers.SerializerMethodField()
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceAlert
        fields = [
            'id', 'employee', 'employee_name', 'department_name',
            'alert_type', 'severity', 'title', 'description',
            'ai_analysis', 'suggested_actions', 'context_data',
            'is_acknowledged', 'acknowledged_by', 'acknowledged_at',
            'is_resolved', 'resolved_by', 'resolved_at', 'resolution_notes',
            'alert_summary', 'time_since_created', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_employee_name(self, obj):
        return obj.employee.user.get_full_name()
    
    def get_department_name(self, obj):
        return obj.employee.department.name if obj.employee.department else None
    
    def get_alert_summary(self, obj):
        return f"{obj.get_alert_type_display()} - {obj.get_severity_display()}"
    
    def get_time_since_created(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hours ago"
        else:
            minutes = delta.seconds // 60
            return f"{minutes} minutes ago"


class AttendanceReportSerializer(serializers.ModelSerializer):
    """Comprehensive attendance report serializer"""
    
    generated_by_name = serializers.SerializerMethodField()
    report_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceReport
        fields = [
            'id', 'report_name', 'report_type', 'scope',
            'start_date', 'end_date', 'report_data', 'ai_insights',
            'trends_analysis', 'recommendations', 'chart_data',
            'generated_by', 'generated_by_name', 'is_scheduled',
            'schedule_frequency', 'report_summary', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_generated_by_name(self, obj):
        return obj.generated_by.get_full_name()
    
    def get_report_summary(self, obj):
        return f"{obj.get_report_type_display()} - {obj.get_scope_display()}"


class AttendanceDashboardSerializer(serializers.Serializer):
    """Real-time attendance dashboard data"""
    
    date = serializers.DateField()
    total_employees = serializers.IntegerField()
    present_today = serializers.IntegerField()
    absent_today = serializers.IntegerField()
    attendance_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    alerts_count = serializers.IntegerField()
    overtime_hours = serializers.DecimalField(max_digits=6, decimal_places=2)
    remote_workers = serializers.IntegerField()
    
    # Additional AI-powered metrics
    productivity_trend = serializers.CharField(required=False)
    wellness_indicator = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    predicted_tomorrow = serializers.JSONField(required=False)


# Quick Action Serializers
class AttendanceClockActionSerializer(serializers.Serializer):
    """Clock action request serializer"""
    
    action = serializers.ChoiceField(
        choices=[
            ('clock_in', 'Clock In'),
            ('clock_out', 'Clock Out'),
            ('break_start', 'Start Break'),
            ('break_end', 'End Break')
        ]
    )
    location = serializers.JSONField(required=False, allow_null=True)
    work_mode = serializers.ChoiceField(
        choices=[
            ('OFFICE', 'Office'),
            ('REMOTE', 'Remote'),
            ('HYBRID', 'Hybrid'),
            ('FIELD', 'Field Work'),
            ('CLIENT_SITE', 'Client Site')
        ],
        required=False
    )
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_location(self, value):
        """Validate GPS location format"""
        if value and isinstance(value, dict):
            required_fields = ['latitude', 'longitude']
            if not all(field in value for field in required_fields):
                raise serializers.ValidationError("Location must include latitude and longitude")
            
            try:
                lat = float(value['latitude'])
                lng = float(value['longitude'])
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    raise serializers.ValidationError("Invalid GPS coordinates")
            except (ValueError, TypeError):
                raise serializers.ValidationError("GPS coordinates must be valid numbers")
        
        return value


class EmployeeScheduleSerializer(serializers.ModelSerializer):
    """Serializer for employee schedules"""
    
    class Meta:
        model = EmployeeSchedule
        fields = [
            'id', 'employee', 'scheduled_in_time', 'scheduled_out_time',
            'scheduled_hours', 'work_days', 'grace_period_minutes',
            'effective_from', 'effective_to', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at']