from rest_framework import serializers
from .models import ControlSystem, ProcessTag, ProcessData, Alarm, MaintenanceSchedule


class ControlSystemSerializer(serializers.ModelSerializer):
    """Control system serializer"""
    operator_name = serializers.CharField(source='operator.get_full_name', read_only=True)
    
    class Meta:
        model = ControlSystem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProcessTagSerializer(serializers.ModelSerializer):
    """Process tag serializer"""
    control_system_name = serializers.CharField(source='control_system.system_name', read_only=True)
    
    class Meta:
        model = ProcessTag
        fields = '__all__'
        read_only_fields = ('created_at',)


class ProcessDataSerializer(serializers.ModelSerializer):
    """Process data serializer"""
    tag_name = serializers.CharField(source='tag.tag_name', read_only=True)
    
    class Meta:
        model = ProcessData
        fields = '__all__'
        read_only_fields = ('created_at',)


class AlarmSerializer(serializers.ModelSerializer):
    """Alarm serializer"""
    tag_name = serializers.CharField(source='tag.tag_name', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.get_full_name', read_only=True)
    
    class Meta:
        model = Alarm
        fields = '__all__'
        read_only_fields = ('created_at',)


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    """Maintenance schedule serializer"""
    control_system_name = serializers.CharField(source='control_system.system_name', read_only=True)
    technician_name = serializers.CharField(source='technician.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = MaintenanceSchedule
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')