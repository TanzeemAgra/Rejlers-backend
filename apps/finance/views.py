from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsHRManagerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import Budget, Invoice, Expense
from .serializers import BudgetSerializer, InvoiceSerializer, ExpenseSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    """Budget CRUD operations"""
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['budget_type', 'fiscal_year', 'manager']
    search_fields = ['name']
    ordering_fields = ['name', 'total_amount', 'fiscal_year']
    ordering = ['-fiscal_year', 'name']


class InvoiceViewSet(viewsets.ModelViewSet):
    """Invoice CRUD operations"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_by']
    search_fields = ['invoice_number', 'client_name']
    ordering_fields = ['issue_date', 'due_date', 'amount']
    ordering = ['-issue_date']


class ExpenseViewSet(viewsets.ModelViewSet):
    """Expense CRUD operations"""
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_approved', 'submitted_by']
    search_fields = ['description']
    ordering_fields = ['expense_date', 'amount']
    ordering = ['-expense_date']