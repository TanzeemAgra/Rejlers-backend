from rest_framework import serializers
from .models import Budget, Invoice, Expense


class BudgetSerializer(serializers.ModelSerializer):
    """Budget serializer"""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ('created_at',)


class InvoiceSerializer(serializers.ModelSerializer):
    """Invoice serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('created_at',)


class ExpenseSerializer(serializers.ModelSerializer):
    """Expense serializer"""
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('created_at',)