from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'control-systems', views.ControlSystemViewSet)
router.register(r'process-tags', views.ProcessTagViewSet)
router.register(r'process-data', views.ProcessDataViewSet)
router.register(r'alarms', views.AlarmViewSet)
router.register(r'maintenance', views.MaintenanceScheduleViewSet)

urlpatterns = [
    path('api/rto/', include(router.urls)),
]