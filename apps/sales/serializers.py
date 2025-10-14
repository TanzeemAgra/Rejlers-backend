from rest_framework import serializers
from .models import Lead, Opportunity, Campaign, Customer


class LeadSerializer(serializers.ModelSerializer):
    """Lead serializer"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class OpportunitySerializer(serializers.ModelSerializer):
    """Opportunity serializer"""
    lead_company = serializers.CharField(source='lead.company_name', read_only=True)
    sales_rep_name = serializers.CharField(source='sales_rep.get_full_name', read_only=True)
    weighted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_weighted_amount(self, obj):
        """Calculate weighted opportunity amount"""
        return float(obj.amount) * (float(obj.probability) / 100)


class CampaignSerializer(serializers.ModelSerializer):
    """Campaign serializer"""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    budget_utilization = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_budget_utilization(self, obj):
        """Calculate budget utilization percentage"""
        if obj.budget > 0:
            return (float(obj.spent_amount) / float(obj.budget)) * 100
        return 0


class CustomerSerializer(serializers.ModelSerializer):
    """Customer serializer"""
    account_manager_name = serializers.CharField(source='account_manager.get_full_name', read_only=True)
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')