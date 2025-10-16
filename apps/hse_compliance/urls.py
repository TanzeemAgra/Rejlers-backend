from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# ============================================================================
# REGULATORY COMPLIANCE API ENDPOINTS
# ============================================================================
router.register(r'frameworks', views.RegulatoryFrameworkViewSet, basename='regulatoryframework')
router.register(r'controls', views.ComplianceControlViewSet, basename='compliancecontrol')
router.register(r'compliance-assessments', views.ComplianceAssessmentViewSet, basename='complianceassessment')
router.register(r'ai-insights', views.AIComplianceInsightViewSet, basename='aicomplianceinsight')

# ============================================================================
# LEGACY/EXISTING HSE COMPLIANCE ENDPOINTS
# ============================================================================
router.register(r'incidents', views.SafetyIncidentViewSet, basename='safetyincident')
router.register(r'checklists', views.ComplianceChecklistViewSet, basename='compliancechecklist')
router.register(r'checklist-assessments', views.ChecklistAssessmentViewSet, basename='checklistassessment')
router.register(r'monitoring', views.EnvironmentalMonitoringViewSet, basename='environmentalmonitoring')

urlpatterns = [
    path('', include(router.urls)),
    
    # Custom API endpoints for Super Admin AI Hub
    path('super-admin/', include([
        path('compliance-overview/', 
             views.ComplianceAssessmentViewSet.as_view({'get': 'compliance_overview'}), 
             name='super-admin-compliance-overview'),
        path('generate-bulk-insights/', 
             views.AIComplianceInsightViewSet.as_view({'post': 'generate_bulk_insights'}), 
             name='super-admin-generate-bulk-insights'),
    ])),
]