from rest_framework import viewsets, serializers
from apps.core.permissions import IsHRManagerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination
from .models import Contract, LegalDocument


class ContractSerializer(serializers.ModelSerializer):
    """Contract serializer"""
    client_name = serializers.CharField(source='client.company_name', read_only=True)
    
    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class LegalDocumentSerializer(serializers.ModelSerializer):
    """Legal document serializer"""
    contract_title = serializers.CharField(source='contract.title', read_only=True)
    
    class Meta:
        model = LegalDocument
        fields = '__all__'
        read_only_fields = ('uploaded_at',)


class ContractViewSet(viewsets.ModelViewSet):
    """Contract CRUD operations"""
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination


class LegalDocumentViewSet(viewsets.ModelViewSet):
    """Legal Document CRUD operations"""
    queryset = LegalDocument.objects.all()
    serializer_class = LegalDocumentSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination