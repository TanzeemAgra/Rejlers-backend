"""
Supply Chain Management Module
Handles procurement, vendor management, and supply chain operations for REJLERS
"""
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Vendor(models.Model):
    """Vendor/Supplier management"""
    VENDOR_CATEGORIES = [
        ('MATERIALS', 'Materials & Equipment'),
        ('SERVICES', 'Professional Services'),
        ('LOGISTICS', 'Logistics & Transport'),
        ('TECHNOLOGY', 'Technology & Software'),
        ('CONSULTING', 'Consulting Services'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('BLACKLISTED', 'Blacklisted'),
        ('PENDING', 'Pending Approval'),
    ]
    
    vendor_code = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    category = models.CharField(max_length=20, choices=VENDOR_CATEGORIES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    
    payment_terms = models.CharField(max_length=100)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    quality_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # 0-10 scale
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.vendor_code} - {self.company_name}"

class PurchaseOrder(models.Model):
    """Purchase order management"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('DELIVERED', 'Delivered'),
        ('COMPLETED', 'Completed'),
    ]
    
    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT')
    
    order_date = models.DateField()
    expected_delivery = models.DateField()
    actual_delivery = models.DateField(null=True, blank=True)
    
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_orders')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.po_number} - {self.vendor.company_name}"

class PurchaseOrderItem(models.Model):
    """Individual items in purchase orders"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    
    item_description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    unit_of_measure = models.CharField(max_length=20)
    
    delivered_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.item_description} - {self.quantity} {self.unit_of_measure}"

class Inventory(models.Model):
    """Inventory management"""
    ITEM_CATEGORIES = [
        ('RAW_MATERIALS', 'Raw Materials'),
        ('EQUIPMENT', 'Equipment'),
        ('TOOLS', 'Tools'),
        ('SAFETY_EQUIPMENT', 'Safety Equipment'),
        ('OFFICE_SUPPLIES', 'Office Supplies'),
    ]
    
    item_code = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=ITEM_CATEGORIES)
    
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    unit_of_measure = models.CharField(max_length=20)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    location = models.CharField(max_length=100)
    
    last_updated = models.DateTimeField(auto_now=True)
    managed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    def __str__(self):
        return f"{self.item_code} - {self.item_name}"
    
    @property
    def needs_reorder(self):
        return self.current_stock <= self.minimum_stock