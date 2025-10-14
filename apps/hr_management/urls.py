"""
HR Management URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, PositionViewSet, EmployeeViewSet, 
    TimeOffViewSet, PerformanceViewSet,
    WorkScheduleViewSet, AttendanceRecordViewSet, AttendancePatternViewSet,
    AttendanceAlertViewSet, AttendanceReportViewSet
)
from .team_views import TeamDashboardViewSet

# Create router for HR Management API endpoints
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'positions', PositionViewSet, basename='positions')
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r'time-off', TimeOffViewSet, basename='time-off')
router.register(r'performance', PerformanceViewSet, basename='performance')

# AI-Powered Attendance Tracking Routes
router.register(r'schedules', WorkScheduleViewSet, basename='work-schedules')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'attendance-patterns', AttendancePatternViewSet, basename='attendance-patterns')
router.register(r'attendance-alerts', AttendanceAlertViewSet, basename='attendance-alerts')
router.register(r'attendance-reports', AttendanceReportViewSet, basename='attendance-reports')

# Team Dashboard Routes
router.register(r'team-dashboard', TeamDashboardViewSet, basename='team-dashboard')

app_name = 'hr_management'

urlpatterns = [
    path('api/v1/hr/', include(router.urls)),
]