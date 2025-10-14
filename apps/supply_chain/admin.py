from django.contrib import admin
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, Inventory


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    readonly_fields = ('total_price',)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_code', 'company_name', 'category', 'status', 'quality_rating')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('vendor_code', 'company_name', 'contact_person')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'vendor', 'total_amount', 'status', 'order_date', 'expected_delivery')
    list_filter = ('status', 'order_date')
    search_fields = ('po_number', 'vendor__company_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PurchaseOrderItemInline]


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'item_name', 'category', 'current_stock', 'minimum_stock', 'needs_reorder')
    list_filter = ('category', 'managed_by')
    search_fields = ('item_code', 'item_name')
    readonly_fields = ('last_updated',)
    
    def needs_reorder(self, obj):
        return obj.needs_reorder
    needs_reorder.boolean = True
    needs_reorder.short_description = 'Needs Reorder'