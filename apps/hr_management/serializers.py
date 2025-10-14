"""
HR Management Serializers
API serializers for HR Management models with proper validation and nested relationships
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Department, Position, Employee, TimeOff, Performance

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    """Department serializer with manager details"""
    
    manager_name = serializers.SerializerMethodField()
    parent_department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'department_type', 'description',
            'manager', 'manager_name', 'parent_department', 'parent_department_name',
            'budget_allocated', 'employee_count', 'location', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'employee_count']
    
    def get_manager_name(self, obj):
        return obj.manager.get_full_name() if obj.manager else None
    
    def get_parent_department_name(self, obj):
        return obj.parent_department.name if obj.parent_department else None


class PositionSerializer(serializers.ModelSerializer):
    """Position serializer with department details"""
    
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = [
            'id', 'title', 'department', 'department_name', 'level',
            'description', 'requirements', 'responsibilities',
            'min_salary', 'max_salary', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_department_name(self, obj):
        return obj.department.name


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for nested serialization"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class EmployeeSerializer(serializers.ModelSerializer):
    """Employee serializer with complete information"""
    
    user_info = UserBasicSerializer(source='user', read_only=True)
    department_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    years_of_service = serializers.ReadOnlyField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_info', 'employee_id', 'department', 'department_name',
            'position', 'position_title', 'employment_type', 'employment_status',
            'hire_date', 'termination_date', 'salary', 'manager', 'manager_name',
            'full_name', 'years_of_service',
            # Personal Information
            'date_of_birth', 'personal_email', 'phone_number',
            'emergency_contact_name', 'emergency_contact_phone',
            # Address
            'address_line1', 'address_line2', 'city', 'state_province',
            'postal_code', 'country',
            # Work Information
            'office_location', 'work_phone', 'skills', 'certifications',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'years_of_service']
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    
    def get_position_title(self, obj):
        return obj.position.title if obj.position else None
    
    def get_manager_name(self, obj):
        return obj.manager.get_full_name() if obj.manager else None
    
    def get_full_name(self, obj):
        return obj.full_name


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new employees"""
    
    class Meta:
        model = Employee
        fields = [
            'user', 'employee_id', 'department', 'position',
            'employment_type', 'employment_status', 'hire_date',
            'salary', 'manager', 'office_location'
        ]
    
    def validate_employee_id(self, value):
        """Validate unique employee ID"""
        if Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return value


class TimeOffSerializer(serializers.ModelSerializer):
    """Time off request serializer"""
    
    employee_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeOff
        fields = [
            'id', 'employee', 'employee_name', 'time_off_type',
            'start_date', 'end_date', 'days_requested', 'reason',
            'status', 'approved_by', 'approved_by_name', 'approved_at',
            'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_at']
    
    def get_employee_name(self, obj):
        return obj.employee.full_name
    
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None
    
    def validate(self, data):
        """Validate time off request dates"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date cannot be after end date.")
        
        return data


class PerformanceSerializer(serializers.ModelSerializer):
    """Performance review serializer"""
    
    employee_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Performance
        fields = [
            'id', 'employee', 'employee_name', 'reviewer', 'reviewer_name',
            'review_period', 'review_start_date', 'review_end_date',
            'technical_skills', 'communication', 'teamwork', 'leadership',
            'initiative', 'overall_rating', 'strengths', 'areas_for_improvement',
            'goals_next_period', 'employee_comments', 'completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_name(self, obj):
        return obj.employee.full_name
    
    def get_reviewer_name(self, obj):
        return obj.reviewer.get_full_name()
    
    def validate(self, data):
        """Validate performance review data"""
        review_start = data.get('review_start_date')
        review_end = data.get('review_end_date')
        
        if review_start and review_end and review_start > review_end:
            raise serializers.ValidationError("Review start date cannot be after end date.")
        
        # Calculate overall rating if individual ratings are provided
        ratings = [
            data.get('technical_skills'),
            data.get('communication'),
            data.get('teamwork'),
            data.get('leadership'),
            data.get('initiative')
        ]
        
        if all(rating is not None for rating in ratings):
            data['overall_rating'] = sum(ratings) / len(ratings)
        
        return data


# Summary Serializers for Dashboard
class DepartmentSummarySerializer(serializers.ModelSerializer):
    """Lightweight department serializer for summaries"""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'employee_count', 'budget_allocated']


class EmployeeSummarySerializer(serializers.ModelSerializer):
    """Lightweight employee serializer for listings"""
    
    full_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'department_name',
            'position_title', 'employment_status'
        ]
    
    def get_full_name(self, obj):
        return obj.full_name
    
    def get_department_name(self, obj):
        return obj.department.name if obj.department else None
    
    def get_position_title(self, obj):
        return obj.position.title if obj.position else None