from django.contrib import admin
from .models import Budget, Invoice, Expense


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'budget_type', 'total_amount', 'spent_amount', 'fiscal_year', 'manager')
    list_filter = ('budget_type', 'fiscal_year')
    search_fields = ('name', 'manager__first_name', 'manager__last_name')
    readonly_fields = ('created_at',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client_name', 'amount', 'status', 'issue_date', 'due_date')
    list_filter = ('status', 'issue_date')
    search_fields = ('invoice_number', 'client_name')
    readonly_fields = ('created_at',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'category', 'amount', 'expense_date', 'is_approved', 'submitted_by')
    list_filter = ('category', 'is_approved', 'expense_date')
    search_fields = ('description', 'submitted_by__first_name', 'submitted_by__last_name')
    readonly_fields = ('created_at',)