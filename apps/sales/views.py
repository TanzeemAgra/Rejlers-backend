from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q
from django.utils import timezone
from apps.core.permissions import IsHRManagerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import Lead, Opportunity, Campaign, Customer
from .serializers import LeadSerializer, OpportunitySerializer, CampaignSerializer, CustomerSerializer


class LeadViewSet(viewsets.ModelViewSet):
    """Lead CRUD operations"""
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lead_source', 'status', 'assigned_to']
    search_fields = ['lead_id', 'company_name', 'contact_person', 'email']
    ordering_fields = ['company_name', 'created_at', 'estimated_value']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def my_leads(self, request):
        """Get leads assigned to current user"""
        my_leads = self.queryset.filter(assigned_to=request.user)
        serializer = self.get_serializer(my_leads, many=True)
        return Response(serializer.data)


class OpportunityViewSet(viewsets.ModelViewSet):
    """Opportunity CRUD operations"""
    queryset = Opportunity.objects.select_related('lead', 'sales_rep').all()
    serializer_class = OpportunitySerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stage', 'sales_rep', 'lead']
    search_fields = ['opportunity_id', 'opportunity_name', 'description']
    ordering_fields = ['opportunity_name', 'amount', 'expected_close_date', 'created_at']
    ordering = ['expected_close_date']
    
    @action(detail=False, methods=['get'])
    def sales_pipeline(self, request):
        """Get sales pipeline summary"""
        pipeline_data = {}
        stages = ['PROSPECTING', 'QUALIFICATION', 'NEEDS_ANALYSIS', 'PROPOSAL', 'NEGOTIATION']
        
        for stage in stages:
            opportunities = self.queryset.filter(stage=stage)
            total_amount = opportunities.aggregate(total=Sum('amount'))['total'] or 0
            pipeline_data[stage] = {
                'count': opportunities.count(),
                'total_amount': float(total_amount)
            }
        
        return Response(pipeline_data)


class CampaignViewSet(viewsets.ModelViewSet):
    """Campaign CRUD operations"""
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['campaign_type', 'status', 'manager']
    search_fields = ['campaign_name', 'description', 'target_audience']
    ordering_fields = ['campaign_name', 'start_date', 'budget']
    ordering = ['-start_date']


class CustomerViewSet(viewsets.ModelViewSet):
    """Customer CRUD operations"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer_type', 'account_manager', 'is_active']
    search_fields = ['customer_id', 'company_name', 'primary_contact', 'email']
    ordering_fields = ['company_name', 'created_at']
    ordering = ['company_name']