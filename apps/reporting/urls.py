from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.ReportTemplateViewSet)
router.register(r'reports', views.GeneratedReportViewSet)
router.register(r'kpis', views.KPIViewSet)

urlpatterns = [
    path('', include(router.urls)),
]