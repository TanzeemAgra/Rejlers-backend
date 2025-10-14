"""
HR Management Models
Defines employee, department, and HR-related data structures
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

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