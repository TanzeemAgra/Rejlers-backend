from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'incidents', views.SafetyIncidentViewSet)
router.register(r'checklists', views.ComplianceChecklistViewSet)
router.register(r'assessments', views.ComplianceAssessmentViewSet)
router.register(r'monitoring', views.EnvironmentalMonitoringViewSet)

urlpatterns = [
    path('api/hse/', include(router.urls)),
]