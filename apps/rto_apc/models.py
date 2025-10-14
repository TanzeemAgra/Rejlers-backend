"""
RTO & APC (Real-Time Operations & Advanced Process Control) Module
Handles real-time monitoring, process control, and automation systems for REJLERS
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField

User = get_user_model()

class ControlSystem(models.Model):
    """Control system configuration"""
    SYSTEM_TYPES = [
        ('SCADA', 'SCADA System'),
        ('DCS', 'Distributed Control System'),
        ('PLC', 'Programmable Logic Controller'),
        ('HMI', 'Human Machine Interface'),
        ('HISTORIAN', 'Process Historian'),
    ]
    
    STATUS_CHOICES = [
        ('OPERATIONAL', 'Operational'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('OFFLINE', 'Offline'),
        ('FAULT', 'Fault Condition'),
    ]
    
    system_id = models.CharField(max_length=50, unique=True)
    system_name = models.CharField(max_length=200)
    system_type = models.CharField(max_length=15, choices=SYSTEM_TYPES)
    
    location = models.CharField(max_length=200)
    description = models.TextField()
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='OPERATIONAL')
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    
    configuration = JSONField(default=dict)  # System-specific configuration
    
    installed_date = models.DateField()
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    
    operator = models.ForeignKey(User, on_delete=models.PROTECT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.system_id} - {self.system_name}"

class ProcessTag(models.Model):
    """Process data tags/points"""
    TAG_TYPES = [
        ('ANALOG_INPUT', 'Analog Input'),
        ('ANALOG_OUTPUT', 'Analog Output'),
        ('DIGITAL_INPUT', 'Digital Input'),
        ('DIGITAL_OUTPUT', 'Digital Output'),
        ('CALCULATED', 'Calculated Value'),
    ]
    
    DATA_TYPES = [
        ('FLOAT', 'Float'),
        ('INTEGER', 'Integer'),
        ('BOOLEAN', 'Boolean'),
        ('STRING', 'String'),
    ]
    
    tag_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200)
    
    control_system = models.ForeignKey(ControlSystem, on_delete=models.CASCADE)
    
    tag_type = models.CharField(max_length=15, choices=TAG_TYPES)
    data_type = models.CharField(max_length=10, choices=DATA_TYPES)
    
    unit_of_measure = models.CharField(max_length=20, blank=True)
    
    min_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    max_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    
    alarm_high = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    alarm_low = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    scan_rate = models.IntegerField(default=1000)  # milliseconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tag_name} - {self.description}"

class ProcessData(models.Model):
    """Real-time process data values"""
    QUALITY_CHOICES = [
        ('GOOD', 'Good'),
        ('BAD', 'Bad'),
        ('UNCERTAIN', 'Uncertain'),
    ]
    
    tag = models.ForeignKey(ProcessTag, on_delete=models.CASCADE)
    
    timestamp = models.DateTimeField()
    value = models.DecimalField(max_digits=15, decimal_places=6)
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, default='GOOD')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['tag', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.tag.tag_name} - {self.value} at {self.timestamp}"

class Alarm(models.Model):
    """Process alarms and events"""
    ALARM_TYPES = [
        ('HIGH', 'High Alarm'),
        ('LOW', 'Low Alarm'),
        ('DEVIATION', 'Deviation Alarm'),
        ('COMMUNICATION', 'Communication Alarm'),
        ('SYSTEM', 'System Alarm'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'), 
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('CLEARED', 'Cleared'),
        ('SUPPRESSED', 'Suppressed'),
    ]
    
    tag = models.ForeignKey(ProcessTag, on_delete=models.CASCADE)
    
    alarm_type = models.CharField(max_length=15, choices=ALARM_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS)
    
    message = models.CharField(max_length=200)
    
    alarm_value = models.DecimalField(max_digits=15, decimal_places=6)
    setpoint = models.DecimalField(max_digits=15, decimal_places=6)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    
    occurred_at = models.DateTimeField()
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    cleared_at = models.DateTimeField(null=True, blank=True)
    
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['occurred_at']),
        ]
    
    def __str__(self):
        return f"{self.tag.tag_name} - {self.alarm_type} - {self.priority}"

class MaintenanceSchedule(models.Model):
    """Maintenance scheduling for control systems"""
    MAINTENANCE_TYPES = [
        ('PREVENTIVE', 'Preventive Maintenance'),
        ('CORRECTIVE', 'Corrective Maintenance'),
        ('PREDICTIVE', 'Predictive Maintenance'),
        ('EMERGENCY', 'Emergency Maintenance'),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    control_system = models.ForeignKey(ControlSystem, on_delete=models.CASCADE)
    
    maintenance_type = models.CharField(max_length=15, choices=MAINTENANCE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    scheduled_date = models.DateTimeField()
    estimated_duration = models.DurationField()
    
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SCHEDULED')
    
    technician = models.ForeignKey(User, on_delete=models.PROTECT)
    
    work_notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_maintenance')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.control_system.system_name} - {self.title} - {self.scheduled_date.date()}"