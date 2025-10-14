from django.contrib import admin
from .models import Lead, Opportunity, Campaign, Customer


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('lead_id', 'company_name', 'contact_person', 'lead_source', 'status', 'assigned_to')
    list_filter = ('lead_source', 'status', 'assigned_to', 'created_at')
    search_fields = ('lead_id', 'company_name', 'contact_person', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('opportunity_id', 'opportunity_name', 'lead', 'stage', 'amount', 'probability', 'expected_close_date')
    list_filter = ('stage', 'sales_rep', 'expected_close_date')
    search_fields = ('opportunity_id', 'opportunity_name', 'lead__company_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('campaign_name', 'campaign_type', 'status', 'budget', 'spent_amount', 'start_date', 'end_date')
    list_filter = ('campaign_type', 'status', 'start_date')
    search_fields = ('campaign_name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'company_name', 'customer_type', 'account_manager', 'is_active')
    list_filter = ('customer_type', 'account_manager', 'is_active')
    search_fields = ('customer_id', 'company_name', 'primary_contact')
    readonly_fields = ('created_at', 'updated_at')