"""
URLs for REJLERS Core application
"""

from django.urls import path
from .views import (
    company_info, ServiceCategoryListView, IndustrySectorListView,
    ProjectTypeListView, OfficeListView
)

app_name = 'core'

urlpatterns = [
    path('company/', company_info, name='company-info'),
    path('service-categories/', ServiceCategoryListView.as_view(), name='service-categories'),
    path('industry-sectors/', IndustrySectorListView.as_view(), name='industry-sectors'),
    path('project-types/', ProjectTypeListView.as_view(), name='project-types'),
    path('offices/', OfficeListView.as_view(), name='offices'),
]