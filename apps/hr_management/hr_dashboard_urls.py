"""
HR AI Dashboard URL Configuration
================================
"""

from django.urls import path, include
from . import hr_dashboard_views

app_name = 'hr_dashboard'

urlpatterns = [
    # Main dashboard endpoint
    path('dashboard/', hr_dashboard_views.HRDashboardView.as_view(), name='dashboard'),
    
    # Widget-specific data endpoints
    path('dashboard/widget/<str:widget_id>/data', hr_dashboard_views.WidgetDataView.as_view(), name='widget_data'),
    
    # Dashboard layout configuration
    path('dashboard/layout/<str:role>', hr_dashboard_views.DashboardLayoutView.as_view(), name='layout_by_role'),
    path('dashboard/layout', hr_dashboard_views.DashboardLayoutView.as_view(), name='layout'),
]