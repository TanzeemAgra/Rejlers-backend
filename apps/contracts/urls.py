from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'contracts', views.ContractViewSet)
router.register(r'documents', views.LegalDocumentViewSet)

urlpatterns = [
    path('api/contracts/', include(router.urls)),
]