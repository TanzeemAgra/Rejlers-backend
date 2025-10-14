from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsHRManagerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, Inventory
from .serializers import VendorSerializer, PurchaseOrderSerializer, InventorySerializer


class VendorViewSet(viewsets.ModelViewSet):
    """Vendor CRUD operations"""
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['company_name', 'contact_person', 'email']
    ordering_fields = ['company_name', 'quality_rating', 'created_at']
    ordering = ['company_name']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """Purchase Order CRUD operations"""
    queryset = PurchaseOrder.objects.select_related('vendor', 'requested_by').prefetch_related('items').all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'vendor', 'requested_by']
    search_fields = ['po_number', 'vendor__company_name']
    ordering_fields = ['order_date', 'expected_delivery', 'total_amount']
    ordering = ['-order_date']


class InventoryViewSet(viewsets.ModelViewSet):
    """Inventory CRUD operations"""
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'managed_by']
    search_fields = ['item_code', 'item_name']
    ordering_fields = ['item_name', 'current_stock', 'last_updated']
    ordering = ['item_name']
    
    @action(detail=False, methods=['get'])
    def low_stock_items(self, request):
        """Get items that need reordering"""
        from django.db import models as django_models
        low_stock_items = self.queryset.filter(current_stock__lte=django_models.F('minimum_stock'))
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)