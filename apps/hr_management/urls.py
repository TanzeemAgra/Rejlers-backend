"""
HR Management URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, PositionViewSet, EmployeeViewSet, 
    TimeOffViewSet, PerformanceViewSet
)

# Create router for HR Management API endpoints
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'positions', PositionViewSet, basename='positions')
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r'time-off', TimeOffViewSet, basename='time-off')
router.register(r'performance', PerformanceViewSet, basename='performance')

app_name = 'hr_management'

urlpatterns = [
    path('api/v1/hr/', include(router.urls)),
]