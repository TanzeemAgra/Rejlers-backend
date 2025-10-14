from django.contrib import admin
from .models import Contract, LegalDocument


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_id', 'title', 'client_name', 'contract_type', 'status', 'start_date', 'end_date')
    list_filter = ('contract_type', 'status', 'start_date')
    search_fields = ('contract_id', 'title', 'client_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'version', 'created_by', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('title',)
    readonly_fields = ('created_at',)