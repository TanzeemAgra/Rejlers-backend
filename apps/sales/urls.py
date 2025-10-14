from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'leads', views.LeadViewSet)
router.register(r'opportunities', views.OpportunityViewSet)
router.register(r'campaigns', views.CampaignViewSet)
router.register(r'customers', views.CustomerViewSet)

urlpatterns = [
    path('api/sales/', include(router.urls)),
]