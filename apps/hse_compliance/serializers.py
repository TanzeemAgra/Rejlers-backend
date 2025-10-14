from rest_framework import serializers
from .models import SafetyIncident, ComplianceChecklist, ComplianceAssessment, EnvironmentalMonitoring


class SafetyIncidentSerializer(serializers.ModelSerializer):
    """Safety incident serializer"""
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    
    class Meta:
        model = SafetyIncident
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ComplianceChecklistSerializer(serializers.ModelSerializer):
    """Compliance checklist serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ComplianceChecklist
        fields = '__all__'
        read_only_fields = ('created_at',)


class ComplianceAssessmentSerializer(serializers.ModelSerializer):
    """Compliance assessment serializer"""
    checklist_name = serializers.CharField(source='checklist.name', read_only=True)
    assessed_by_name = serializers.CharField(source='assessed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ComplianceAssessment
        fields = '__all__'
        read_only_fields = ('created_at',)


class EnvironmentalMonitoringSerializer(serializers.ModelSerializer):
    """Environmental monitoring serializer"""
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    
    class Meta:
        model = EnvironmentalMonitoring
        fields = '__all__'
        read_only_fields = ('created_at',)