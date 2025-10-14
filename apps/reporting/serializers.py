from rest_framework import serializers
from .models import ReportTemplate, GeneratedReport, KPI


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Report template serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class GeneratedReportSerializer(serializers.ModelSerializer):
    """Generated report serializer"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = '__all__'
        read_only_fields = ('created_at',)


class KPISerializer(serializers.ModelSerializer):
    """KPI serializer"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    achievement_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = KPI
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_achievement_percentage(self, obj):
        """Calculate achievement percentage"""
        if obj.target_value > 0:
            return (float(obj.current_value) / float(obj.target_value)) * 100
        return 0