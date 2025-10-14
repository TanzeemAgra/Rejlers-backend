"""
HR Management Models
Defines employee, department, and HR-related data structures
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import datetime, timedelta

User = get_user_model()


class Department(models.Model):
    """Department/Division within REJLERS"""
    
    DEPARTMENT_TYPES = [
        ('ENGINEERING', 'Engineering'),
        ('CONSULTING', 'Consulting'), 
        ('MANAGEMENT', 'Management'),
        ('OPERATIONS', 'Operations'),
        ('FINANCE', 'Finance'),
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
        ('SALES', 'Sales & Marketing'),
        ('QUALITY', 'Quality Assurance'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    department_type = models.CharField(max_length=20, choices=DEPARTMENT_TYPES)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='managed_departments')
    parent_department = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    budget_allocated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    employee_count = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Position(models.Model):
    """Job positions/roles within REJLERS"""
    
    POSITION_LEVELS = [
        ('INTERN', 'Intern'),
        ('JUNIOR', 'Junior'),
        ('SENIOR', 'Senior'),
        ('LEAD', 'Lead'),
        ('MANAGER', 'Manager'),
        ('DIRECTOR', 'Director'),
        ('VP', 'Vice President'),
        ('EXECUTIVE', 'Executive'),
    ]
    
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    level = models.CharField(max_length=20, choices=POSITION_LEVELS)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField()
    
    min_salary = models.DecimalField(max_digits=12, decimal_places=2)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['department', 'level', 'title']
        unique_together = ['title', 'department', 'level']
    
    def __str__(self):
        return f"{self.title} - {self.department.name} ({self.level})"


class Employee(models.Model):
    """Employee information extending User model"""
    
    EMPLOYMENT_TYPES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERN', 'Intern'),
        ('CONSULTANT', 'Consultant'),
    ]
    
    EMPLOYMENT_STATUS = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ON_LEAVE', 'On Leave'),
        ('TERMINATED', 'Terminated'),
        ('RETIRED', 'Retired'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='FULL_TIME')
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='ACTIVE')
    
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='managed_employees')
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    personal_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Sweden')
    
    # Work Information
    office_location = models.CharField(max_length=100, blank=True)
    work_phone = models.CharField(max_length=20, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    certifications = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def years_of_service(self):
        from datetime import date
        if self.termination_date:
            end_date = self.termination_date
        else:
            end_date = date.today()
        
        return (end_date - self.hire_date).days // 365


class TimeOff(models.Model):
    """Employee time off requests and tracking"""
    
    TIME_OFF_TYPES = [
        ('VACATION', 'Vacation'),
        ('SICK', 'Sick Leave'),
        ('PERSONAL', 'Personal Leave'),
        ('MATERNITY', 'Maternity Leave'),
        ('PATERNITY', 'Paternity Leave'),
        ('BEREAVEMENT', 'Bereavement Leave'),
        ('TRAINING', 'Training/Conference'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='time_off_requests')
    time_off_type = models.CharField(max_length=20, choices=TIME_OFF_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.DecimalField(max_digits=5, decimal_places=1)
    
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_time_off')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.time_off_type} ({self.start_date} to {self.end_date})"


class Performance(models.Model):
    """Employee performance reviews and evaluations"""
    
    REVIEW_PERIODS = [
        ('QUARTERLY', 'Quarterly'),
        ('SEMI_ANNUAL', 'Semi-Annual'),
        ('ANNUAL', 'Annual'),
        ('PROBATION', 'Probation Review'),
        ('PROJECT', 'Project Review'),
    ]
    
    RATINGS = [
        (1, 'Needs Improvement'),
        (2, 'Meets Expectations'),
        (3, 'Exceeds Expectations'),
        (4, 'Outstanding'),
        (5, 'Exceptional'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_reviews')
    
    review_period = models.CharField(max_length=20, choices=REVIEW_PERIODS)
    review_start_date = models.DateField()
    review_end_date = models.DateField()
    
    # Ratings
    technical_skills = models.IntegerField(choices=RATINGS)
    communication = models.IntegerField(choices=RATINGS)
    teamwork = models.IntegerField(choices=RATINGS)
    leadership = models.IntegerField(choices=RATINGS)
    initiative = models.IntegerField(choices=RATINGS)
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2)
    
    # Feedback
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    goals_next_period = models.TextField()
    employee_comments = models.TextField(blank=True)
    
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-review_end_date']
        unique_together = ['employee', 'review_period', 'review_end_date']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.review_period} ({self.review_end_date})"


# ============= AI-POWERED ATTENDANCE TRACKING SYSTEM =============

class WorkSchedule(models.Model):
    """Employee work schedules and shifts"""
    
    SCHEDULE_TYPES = [
        ('STANDARD', 'Standard 9-5'),
        ('FLEXIBLE', 'Flexible Hours'),
        ('SHIFT', 'Shift Work'),
        ('REMOTE', 'Remote Work'),
        ('HYBRID', 'Hybrid Work'),
        ('COMPRESSED', 'Compressed Work Week'),
    ]
    
    DAYS_OF_WEEK = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_schedules')
    schedule_name = models.CharField(max_length=100, default='Default Schedule')
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='STANDARD')
    
    # Schedule Details
    days_of_week = models.JSONField(default=list, help_text="List of working days")
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration_minutes = models.PositiveIntegerField(default=60)
    
    # Flexibility Settings
    flexible_start_window = models.PositiveIntegerField(default=0, help_text="Minutes of flexibility for start time")
    flexible_end_window = models.PositiveIntegerField(default=0, help_text="Minutes of flexibility for end time")
    minimum_hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    
    # Location Settings
    work_location = models.CharField(max_length=200, default='Office')
    remote_work_allowed = models.BooleanField(default=False)
    hybrid_days_in_office = models.PositiveIntegerField(default=5, help_text="Days per week required in office")
    
    # Validity Period
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_from']
        
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.schedule_name}"


class AttendanceRecord(models.Model):
    """Individual employee attendance records with AI analysis"""
    
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EARLY_DEPARTURE', 'Early Departure'),
        ('HALF_DAY', 'Half Day'),
        ('WORK_FROM_HOME', 'Work From Home'),
        ('ON_LEAVE', 'On Leave'),
        ('HOLIDAY', 'Holiday'),
        ('SICK_LEAVE', 'Sick Leave'),
    ]
    
    CLOCK_METHODS = [
        ('MANUAL', 'Manual Entry'),
        ('BIOMETRIC', 'Biometric Scanner'),
        ('MOBILE_APP', 'Mobile Application'),
        ('WEB_PORTAL', 'Web Portal'),
        ('RFID_CARD', 'RFID Card'),
        ('FACE_RECOGNITION', 'Face Recognition'),
        ('GPS_TRACKING', 'GPS Tracking'),
        ('AI_DETECTION', 'AI Auto-Detection'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    
    # Clock In/Out Times
    clock_in_time = models.DateTimeField(null=True, blank=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    
    # Break Times
    break_start_time = models.DateTimeField(null=True, blank=True)
    break_end_time = models.DateTimeField(null=True, blank=True)
    total_break_minutes = models.PositiveIntegerField(default=0)
    
    # Calculated Fields
    scheduled_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    actual_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    
    # Status and Location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    work_location = models.CharField(max_length=200, blank=True)
    is_remote = models.BooleanField(default=False)
    
    # Clock Method and Verification
    clock_in_method = models.CharField(max_length=20, choices=CLOCK_METHODS, default='WEB_PORTAL')
    clock_out_method = models.CharField(max_length=20, choices=CLOCK_METHODS, default='WEB_PORTAL')
    
    # GPS and Device Information
    clock_in_lat_lng = models.JSONField(null=True, blank=True, help_text="GPS coordinates for clock in")
    clock_out_lat_lng = models.JSONField(null=True, blank=True, help_text="GPS coordinates for clock out")
    device_info = models.JSONField(null=True, blank=True, help_text="Device and browser information")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # AI Analysis Fields
    attendance_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.0, 
                                         help_text="AI-calculated attendance quality score")
    pattern_analysis = models.JSONField(null=True, blank=True, 
                                      help_text="AI pattern analysis results")
    anomaly_detected = models.BooleanField(default=False)
    anomaly_details = models.TextField(blank=True)
    
    # Approvals and Notes
    manager_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_attendance')
    notes = models.TextField(blank=True)
    employee_comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-clock_in_time']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['anomaly_detected']),
        ]
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.date} ({self.status})"
    
    def calculate_actual_hours(self):
        """Calculate actual working hours"""
        if self.clock_in_time and self.clock_out_time:
            total_seconds = (self.clock_out_time - self.clock_in_time).total_seconds()
            total_minutes = total_seconds / 60
            working_minutes = total_minutes - self.total_break_minutes
            self.actual_hours = round(working_minutes / 60, 2)
            
            # Calculate overtime
            if self.actual_hours > self.scheduled_hours:
                self.overtime_hours = self.actual_hours - self.scheduled_hours
            else:
                self.overtime_hours = 0.0
                
        self.save()
        

class AttendancePattern(models.Model):
    """AI-generated attendance patterns and insights"""
    
    PATTERN_TYPES = [
        ('PUNCTUALITY', 'Punctuality Pattern'),
        ('CONSISTENCY', 'Consistency Pattern'),
        ('PRODUCTIVITY', 'Productivity Correlation'),
        ('SEASONAL', 'Seasonal Trend'),
        ('WEEKLY', 'Weekly Pattern'),
        ('MONTHLY', 'Monthly Trend'),
        ('ANOMALY', 'Anomaly Pattern'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_patterns')
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES)
    
    # Analysis Period
    analysis_start_date = models.DateField()
    analysis_end_date = models.DateField()
    
    # Pattern Data
    pattern_data = models.JSONField(help_text="Detailed pattern analysis data")
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Insights and Recommendations
    key_insights = models.TextField()
    ai_recommendations = models.TextField(blank=True)
    predicted_future_behavior = models.TextField(blank=True)
    
    # Risk Assessment
    risk_level = models.CharField(max_length=10, choices=[
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
    ], default='LOW')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.pattern_type}"


class AttendanceAlert(models.Model):
    """AI-powered attendance alerts and notifications"""
    
    ALERT_TYPES = [
        ('LATE_ARRIVAL', 'Late Arrival'),
        ('EARLY_DEPARTURE', 'Early Departure'),
        ('EXTENDED_ABSENCE', 'Extended Absence'),
        ('PATTERN_CHANGE', 'Pattern Change Detected'),
        ('OVERTIME_ALERT', 'Overtime Alert'),
        ('CONSECUTIVE_LATES', 'Consecutive Late Arrivals'),
        ('LOCATION_ANOMALY', 'Location Anomaly'),
        ('TIME_FRAUD_RISK', 'Time Fraud Risk'),
        ('WELLNESS_CONCERN', 'Employee Wellness Concern'),
    ]
    
    SEVERITY_LEVELS = [
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
        ('URGENT', 'Urgent Action Required'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='INFO')
    
    # Alert Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    ai_analysis = models.TextField(blank=True)
    suggested_actions = models.TextField(blank=True)
    
    # Context Data
    related_attendance_records = models.ManyToManyField(AttendanceRecord, blank=True)
    context_data = models.JSONField(null=True, blank=True)
    
    # Status and Resolution
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at', '-severity']
        indexes = [
            models.Index(fields=['employee', 'alert_type']),
            models.Index(fields=['severity', 'is_resolved']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.alert_type} ({self.severity})"


class AttendanceReport(models.Model):
    """AI-generated attendance reports and analytics"""
    
    REPORT_TYPES = [
        ('DAILY', 'Daily Summary'),
        ('WEEKLY', 'Weekly Report'),
        ('MONTHLY', 'Monthly Analysis'),
        ('QUARTERLY', 'Quarterly Review'),
        ('ANNUAL', 'Annual Report'),
        ('CUSTOM', 'Custom Period'),
        ('REALTIME', 'Real-time Dashboard'),
    ]
    
    REPORT_SCOPE = [
        ('INDIVIDUAL', 'Individual Employee'),
        ('DEPARTMENT', 'Department'),
        ('TEAM', 'Team/Group'),
        ('COMPANY', 'Company-wide'),
        ('LOCATION', 'Location-based'),
    ]
    
    report_name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    scope = models.CharField(max_length=20, choices=REPORT_SCOPE)
    
    # Report Parameters
    start_date = models.DateField()
    end_date = models.DateField()
    employees = models.ManyToManyField(Employee, blank=True)
    departments = models.ManyToManyField(Department, blank=True)
    
    # Generated Data
    report_data = models.JSONField(help_text="Complete report data and statistics")
    ai_insights = models.TextField(blank=True)
    trends_analysis = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Visualization Data
    chart_data = models.JSONField(null=True, blank=True, help_text="Data for charts and graphs")
    
    # Report Metadata
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.report_name} - {self.report_type} ({self.start_date} to {self.end_date})"


# ===============================================
# AI-POWERED ATTENDANCE TRACKING SYSTEM
# ===============================================

class WorkSchedule(models.Model):
    """
    AI-Enhanced Work Schedule Management
    Supports flexible scheduling with intelligent pattern recognition
    """
    SCHEDULE_TYPES = [
        ('STANDARD', 'Standard 9-5'),
        ('FLEXIBLE', 'Flexible Hours'),
        ('SHIFT', 'Shift Work'),
        ('REMOTE', 'Remote Work'),
        ('HYBRID', 'Hybrid Work'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract Based'),
    ]
    
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    
    employee = models.ForeignKey('hr_management.Employee', on_delete=models.CASCADE, related_name='work_schedules')
    schedule_name = models.CharField(max_length=100)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='STANDARD')
    
    # Time configuration
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.DurationField(default=timedelta(hours=1))  # Default 1-hour break
    
    # Days configuration
    work_days = models.JSONField(default=list)  # List of work days ['MON', 'TUE', 'WED', 'THU', 'FRI']
    
    # Flexibility settings
    flexible_start_window = models.DurationField(default=timedelta(hours=1))  # ±1 hour flexibility
    flexible_end_window = models.DurationField(default=timedelta(hours=1))
    minimum_work_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    
    # Location settings
    allowed_locations = models.JSONField(default=list)  # GPS coordinates or office locations
    remote_work_allowed = models.BooleanField(default=False)
    
    # AI Enhancement fields
    ai_pattern_analysis = models.BooleanField(default=True)
    productivity_tracking = models.BooleanField(default=True)
    anomaly_detection = models.BooleanField(default=True)
    
    # Validity period
    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'effective_from']),
            models.Index(fields=['schedule_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.schedule_name}"
    
    @property
    def total_work_hours(self):
        """Calculate total work hours per day"""
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        
        if end < start:  # Handle overnight shifts
            end += timedelta(days=1)
        
        total_time = end - start
        return (total_time - self.break_duration).total_seconds() / 3600
    
    @property
    def weekly_work_hours(self):
        """Calculate total work hours per week"""
        return self.total_work_hours * len(self.work_days)


class AttendanceRecord(models.Model):
    """
    AI-Powered Attendance Tracking with Advanced Analytics
    """
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('LATE', 'Late'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
        ('WORK_FROM_HOME', 'Work From Home'),
        ('ON_LEAVE', 'On Leave'),
        ('SICK_LEAVE', 'Sick Leave'),
        ('VACATION', 'Vacation'),
        ('HOLIDAY', 'Holiday'),
        ('TRAINING', 'Training'),
        ('BUSINESS_TRIP', 'Business Trip'),
    ]
    
    WORK_MODES = [
        ('OFFICE', 'Office'),
        ('REMOTE', 'Remote'),
        ('HYBRID', 'Hybrid'),
        ('FIELD', 'Field Work'),
        ('CLIENT_SITE', 'Client Site'),
    ]
    
    employee = models.ForeignKey('hr_management.Employee', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    
    # Clock in/out times
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    
    # Break tracking
    break_start = models.DateTimeField(null=True, blank=True)
    break_end = models.DateTimeField(null=True, blank=True)
    total_break_duration = models.DurationField(default=timedelta(0))
    
    # Status and work mode
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABSENT')
    work_mode = models.CharField(max_length=15, choices=WORK_MODES, default='OFFICE')
    
    # Location tracking
    clock_in_location = models.JSONField(null=True, blank=True)  # GPS coordinates
    clock_out_location = models.JSONField(null=True, blank=True)
    location_verified = models.BooleanField(default=False)
    
    # Time calculations
    scheduled_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    actual_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    
    # Scheduled times (for frontend compatibility)
    scheduled_in_time = models.TimeField(null=True, blank=True)
    scheduled_out_time = models.TimeField(null=True, blank=True)
    
    # Late/Early calculations
    late_by_minutes = models.PositiveIntegerField(default=0, help_text="Minutes late from scheduled in time")
    early_by_minutes = models.PositiveIntegerField(default=0, help_text="Minutes early from scheduled out time")
    
    # AI Analysis Fields
    ai_confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # 0-100
    pattern_deviation_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    productivity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Anomaly detection
    is_anomaly = models.BooleanField(default=False)
    anomaly_reasons = models.JSONField(default=list)  # List of anomaly detection reasons
    
    # Notes and justification
    notes = models.TextField(blank=True)
    manager_notes = models.TextField(blank=True)
    employee_justification = models.TextField(blank=True)
    
    # Approval workflow
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_attendance')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['status', 'date']),
            models.Index(fields=['is_anomaly', 'date']),
        ]
    
    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.date} ({self.status})"
    
    @property
    def is_late(self):
        """Check if employee was late based on schedule"""
        if not self.clock_in:
            return False
        
        schedule = self.employee.work_schedules.filter(
            is_active=True,
            effective_from__lte=self.date
        ).first()
        
        if not schedule:
            return False
        
        scheduled_time = datetime.combine(self.date, schedule.start_time)
        return self.clock_in > scheduled_time + schedule.flexible_start_window
    
    @property
    def total_work_duration(self):
        """Calculate total work duration excluding breaks"""
        if not (self.clock_in and self.clock_out):
            return timedelta(0)
        
        total_time = self.clock_out - self.clock_in
        return total_time - self.total_break_duration
    
    def calculate_ai_scores(self):
        """AI-powered analysis of attendance record"""
        # This would integrate with ML models for real analysis
        # For now, implementing rule-based scoring
        
        confidence_factors = []
        pattern_factors = []
        productivity_factors = []
        
        # Confidence scoring based on data completeness
        if self.clock_in and self.clock_out:
            confidence_factors.append(40)
        if self.location_verified:
            confidence_factors.append(30)
        if self.notes:
            confidence_factors.append(20)
        if not self.is_anomaly:
            confidence_factors.append(10)
        
        # Pattern deviation scoring
        # Compare with employee's historical patterns
        if self.is_late:
            pattern_factors.append(-20)
        if self.overtime_hours > 2:
            pattern_factors.append(-10)
        if self.work_mode == 'REMOTE' and self.employee.work_schedules.filter(remote_work_allowed=True).exists():
            pattern_factors.append(10)
        
        # Productivity scoring based on hours worked
        if self.actual_hours >= self.scheduled_hours:
            productivity_factors.append(30)
        if self.actual_hours > self.scheduled_hours * 1.1:  # 110% of scheduled
            productivity_factors.append(20)
        
        self.ai_confidence_score = min(100, sum(confidence_factors))
        self.pattern_deviation_score = max(0, min(100, 50 + sum(pattern_factors)))
        self.productivity_score = min(100, sum(productivity_factors))
        
        return {
            'confidence': self.ai_confidence_score,
            'pattern_deviation': self.pattern_deviation_score,
            'productivity': self.productivity_score
        }
    
    def calculate_schedule_adherence(self):
        """Calculate late/early minutes based on employee schedule"""
        # Get employee's active schedule for this date
        schedule = self.employee.schedules.filter(
            is_active=True,
            effective_from__lte=self.date,
            effective_to__gte=self.date
        ).first()
        
        if not schedule or not schedule.is_work_day(self.date):
            return
        
        # Set scheduled times
        self.scheduled_in_time = schedule.scheduled_in_time
        self.scheduled_out_time = schedule.scheduled_out_time
        
        # Calculate late arrival
        if self.clock_in and self.scheduled_in_time:
            scheduled_in_datetime = datetime.combine(self.date, self.scheduled_in_time)
            if self.clock_in > scheduled_in_datetime:
                late_delta = self.clock_in - scheduled_in_datetime
                self.late_by_minutes = int(late_delta.total_seconds() / 60)
            else:
                self.late_by_minutes = 0
        
        # Calculate early departure
        if self.clock_out and self.scheduled_out_time:
            scheduled_out_datetime = datetime.combine(self.date, self.scheduled_out_time)
            if self.clock_out < scheduled_out_datetime:
                early_delta = scheduled_out_datetime - self.clock_out
                self.early_by_minutes = int(early_delta.total_seconds() / 60)
            else:
                self.early_by_minutes = 0
    
    def save(self, *args, **kwargs):
        """Override save to automatically calculate schedule adherence"""
        self.calculate_schedule_adherence()
        super().save(*args, **kwargs)


class AttendancePattern(models.Model):
    """
    AI-Driven Pattern Analysis for Employee Attendance
    """
    PATTERN_TYPES = [
        ('WEEKLY', 'Weekly Pattern'),
        ('MONTHLY', 'Monthly Pattern'),
        ('SEASONAL', 'Seasonal Pattern'),
        ('CUSTOM', 'Custom Pattern'),
    ]
    
    PATTERN_STATUS = [
        ('NORMAL', 'Normal Pattern'),
        ('CONCERNING', 'Concerning Pattern'),
        ('CRITICAL', 'Critical Pattern'),
        ('IMPROVING', 'Improving Pattern'),
    ]
    
    employee = models.ForeignKey('hr_management.Employee', on_delete=models.CASCADE, related_name='attendance_patterns')
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES)
    pattern_name = models.CharField(max_length=100)
    
    # Analysis period
    analysis_start_date = models.DateField()
    analysis_end_date = models.DateField()
    
    # Pattern metrics
    average_clock_in_time = models.TimeField(null=True, blank=True)
    average_clock_out_time = models.TimeField(null=True, blank=True)
    average_daily_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Percentage
    punctuality_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Pattern analysis
    pattern_consistency_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    pattern_status = models.CharField(max_length=15, choices=PATTERN_STATUS, default='NORMAL')
    
    # AI insights
    ai_insights = models.JSONField(default=dict)  # Store AI-generated insights
    recommendations = models.JSONField(default=list)  # AI recommendations
    
    # Trend analysis
    trend_direction = models.CharField(max_length=20, default='STABLE')  # IMPROVING, DECLINING, STABLE
    trend_strength = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # 0-1 scale
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'pattern_type']),
            models.Index(fields=['pattern_status', 'analysis_end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.pattern_name}"


class AttendanceAlert(models.Model):
    """
    Intelligent Alert System for Attendance Management
    """
    ALERT_TYPES = [
        ('LATE_ARRIVAL', 'Late Arrival'),
        ('EARLY_DEPARTURE', 'Early Departure'),
        ('MISSED_PUNCH', 'Missed Clock In/Out'),
        ('EXTENDED_BREAK', 'Extended Break'),
        ('PATTERN_ANOMALY', 'Pattern Anomaly'),
        ('LOCATION_MISMATCH', 'Location Mismatch'),
        ('OVERTIME_EXCESS', 'Excessive Overtime'),
        ('ABSENCE_PATTERN', 'Concerning Absence Pattern'),
        ('SCHEDULE_VIOLATION', 'Schedule Violation'),
        ('PRODUCTIVITY_DROP', 'Productivity Drop'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    ALERT_STATUS = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]
    
    employee = models.ForeignKey('hr_management.Employee', on_delete=models.CASCADE, related_name='attendance_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='MEDIUM')
    status = models.CharField(max_length=15, choices=ALERT_STATUS, default='ACTIVE')
    
    # Alert details
    title = models.CharField(max_length=200)
    description = models.TextField()
    occurrence_date = models.DateField(auto_now_add=True)
    detection_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    # Related records
    related_attendance_record = models.ForeignKey(AttendanceRecord, on_delete=models.SET_NULL, 
                                                null=True, blank=True, related_name='alerts')
    
    # AI analysis
    ai_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    suggested_actions = models.JSONField(default=list)
    
    # Management workflow
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assigned_alerts')
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Escalation
    escalation_level = models.PositiveIntegerField(default=0)
    escalated_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-severity', '-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['alert_type', 'occurrence_date']),
        ]
    
    def __str__(self):
        return f"{self.get_severity_display()} - {self.title}"


class AttendanceReport(models.Model):
    """
    AI-Enhanced Attendance Reporting and Analytics
    """
    REPORT_TYPES = [
        ('DAILY', 'Daily Report'),
        ('WEEKLY', 'Weekly Report'),
        ('MONTHLY', 'Monthly Report'),
        ('QUARTERLY', 'Quarterly Report'),
        ('YEARLY', 'Yearly Report'),
        ('CUSTOM', 'Custom Report'),
        ('REAL_TIME', 'Real-time Dashboard'),
    ]
    
    REPORT_FORMATS = [
        ('PDF', 'PDF Document'),
        ('EXCEL', 'Excel Spreadsheet'),
        ('JSON', 'JSON Data'),
        ('CSV', 'CSV File'),
        ('DASHBOARD', 'Interactive Dashboard'),
    ]
    
    report_name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=15, choices=REPORT_TYPES)
    report_format = models.CharField(max_length=15, choices=REPORT_FORMATS, default='PDF')
    
    # Report scope
    department_filter = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    # employee_filter = models.ManyToManyField('hr_management.Employee', blank=True)  # Commented for migration
    employee_filter_json = models.JSONField(default=list, blank=True)  # Store employee IDs as JSON
    
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Report configuration
    include_ai_insights = models.BooleanField(default=True)
    include_patterns = models.BooleanField(default=True)
    include_alerts = models.BooleanField(default=True)
    include_recommendations = models.BooleanField(default=True)
    
    # Analytics data (stored as JSON for flexibility)
    analytics_data = models.JSONField(default=dict)
    
    # Key metrics
    total_employees_covered = models.PositiveIntegerField(default=0)
    average_attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_work_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_overtime_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # AI-generated insights
    key_findings = models.JSONField(default=list)
    trend_analysis = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    
    # Report generation
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)
    next_generation = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'start_date']),
            models.Index(fields=['generated_at', 'is_scheduled']),
        ]
    
    def __str__(self):
        return f"{self.report_name} - {self.get_report_type_display()}"
    
    def generate_analytics(self):
        """Generate comprehensive analytics for the report period"""
        from django.db.models import Avg, Sum, Count
        from datetime import datetime, timedelta
        
        # Get attendance records in date range
        records = AttendanceRecord.objects.filter(
            date__range=[self.start_date, self.end_date]
        )
        
        # Apply filters
        if self.department_filter:
            records = records.filter(employee__department=self.department_filter)
        
        if self.employee_filter.exists():
            records = records.filter(employee__in=self.employee_filter.all())
        
        # Calculate key metrics
        analytics = {
            'total_records': records.count(),
            'present_days': records.filter(status='PRESENT').count(),
            'late_arrivals': records.filter(status='LATE').count(),
            'absences': records.filter(status='ABSENT').count(),
            'remote_work_days': records.filter(work_mode='REMOTE').count(),
            
            'average_daily_hours': records.aggregate(avg=Avg('actual_hours'))['avg'] or 0,
            'total_overtime': records.aggregate(sum=Sum('overtime_hours'))['sum'] or 0,
            'average_ai_confidence': records.aggregate(avg=Avg('ai_confidence_score'))['avg'] or 0,
            
            'anomaly_count': records.filter(is_anomaly=True).count(),
            'location_verified_rate': records.filter(location_verified=True).count() / max(records.count(), 1) * 100,
        }
        
        # Department-wise breakdown if not filtered by department
        if not self.department_filter:
            dept_analytics = {}
            for dept in Department.objects.filter(is_active=True):
                dept_records = records.filter(employee__department=dept)
                if dept_records.exists():
                    dept_analytics[dept.name] = {
                        'total_records': dept_records.count(),
                        'attendance_rate': dept_records.filter(status='PRESENT').count() / dept_records.count() * 100,
                        'average_hours': dept_records.aggregate(avg=Avg('actual_hours'))['avg'] or 0,
                    }
            analytics['department_breakdown'] = dept_analytics
        
        self.analytics_data = analytics
        self.total_employees_covered = records.values('employee').distinct().count()
        self.average_attendance_rate = analytics.get('present_days', 0) / max(analytics.get('total_records', 1), 1) * 100
        self.total_work_hours = records.aggregate(sum=Sum('actual_hours'))['sum'] or 0
        self.total_overtime_hours = analytics.get('total_overtime', 0)
        
        return analytics


class PunchRecord(models.Model):
    """
    Individual punch records for detailed attendance tracking
    Matches frontend PunchRecord interface
    """
    PUNCH_TYPES = [
        ('IN', 'Clock In'),
        ('OUT', 'Clock Out'),
        ('BREAK_START', 'Break Start'),
        ('BREAK_END', 'Break End'),
    ]
    
    attendance_record = models.ForeignKey(
        'AttendanceRecord', 
        on_delete=models.CASCADE, 
        related_name='punch_records'
    )
    
    # Punch details
    punch_time = models.DateTimeField()
    punch_type = models.CharField(max_length=12, choices=PUNCH_TYPES)
    
    # Location and device tracking
    location = models.CharField(max_length=200, blank=True, help_text="Human-readable location")
    device_info = models.CharField(max_length=200, blank=True, help_text="Device used for punch")
    gps_coordinates = models.JSONField(null=True, blank=True, help_text="GPS lat/lng coordinates")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Verification and validation
    is_verified = models.BooleanField(default=True)
    verification_method = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='punch_records')
    
    class Meta:
        ordering = ['punch_time']
        indexes = [
            models.Index(fields=['attendance_record', 'punch_time']),
            models.Index(fields=['punch_type', 'punch_time']),
        ]
    
    def __str__(self):
        return f"{self.attendance_record.employee} - {self.punch_type} at {self.punch_time.strftime('%H:%M')}"


class EmployeeSchedule(models.Model):
    """
    Employee work schedule for calculating scheduled times and late/early analysis
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='schedules')
    
    # Schedule timing
    scheduled_in_time = models.TimeField(default='09:00')
    scheduled_out_time = models.TimeField(default='17:00')
    scheduled_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    
    # Work days (JSON array of day numbers: 0=Monday, 6=Sunday)
    work_days = models.JSONField(default=list, help_text="Array of work day numbers (0=Monday)")
    
    # Flexibility settings
    grace_period_minutes = models.PositiveIntegerField(default=15, help_text="Grace period for late arrival")
    
    # Validity period
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_from']
        indexes = [
            models.Index(fields=['employee', 'is_active', 'effective_from']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.scheduled_in_time} to {self.scheduled_out_time}"
    
    def is_work_day(self, date):
        """Check if given date is a work day for this schedule"""
        return date.weekday() in self.work_days