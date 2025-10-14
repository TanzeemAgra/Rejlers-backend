from rest_framework import serializers
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, Inventory


class VendorSerializer(serializers.ModelSerializer):
    """Vendor serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Purchase order item serializer"""
    
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'
        read_only_fields = ('total_price',)


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Purchase order serializer"""
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class InventorySerializer(serializers.ModelSerializer):
    """Inventory serializer"""
    managed_by_name = serializers.CharField(source='managed_by.get_full_name', read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ('last_updated',)