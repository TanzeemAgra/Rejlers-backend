"""
Finance & Estimation Module
Handles financial operations, budgeting, and cost estimation for REJLERS
"""
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Budget(models.Model):
    """Budget management"""
    BUDGET_TYPES = [
        ('PROJECT', 'Project Budget'),
        ('DEPARTMENT', 'Department Budget'),
        ('ANNUAL', 'Annual Budget'),
        ('OPERATIONAL', 'Operational Budget'),
    ]
    
    name = models.CharField(max_length=200)
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPES)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    fiscal_year = models.IntegerField()
    manager = models.ForeignKey(User, on_delete=models.PROTECT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.fiscal_year}"

class Invoice(models.Model):
    """Invoice management"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    client_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    issue_date = models.DateField()
    due_date = models.DateField()
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.invoice_number} - {self.client_name}"

class Expense(models.Model):
    """Expense tracking"""
    EXPENSE_CATEGORIES = [
        ('TRAVEL', 'Travel & Transport'),
        ('MATERIALS', 'Materials & Supplies'),
        ('EQUIPMENT', 'Equipment'),
        ('SERVICES', 'Professional Services'),
        ('OFFICE', 'Office Expenses'),
    ]
    
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    expense_date = models.DateField()
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.description} - {self.amount}"