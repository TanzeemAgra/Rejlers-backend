"""
Test API URLs for Frontend-Backend Communication Testing
======================================================
URL routing for test endpoints to verify connectivity and data exchange
between Next.js frontend and Django backend using soft coding.
"""

from django.urls import path
from . import test_views

app_name = 'test'

urlpatterns = [
    # Basic connectivity test
    path('connection/', test_views.test_connection, name='test-connection'),
    
    # Database status test (PostgreSQL + MongoDB)
    path('database-status/', test_views.test_database_status, name='test-database-status'),
    
    # CORS configuration test
    path('cors/', test_views.test_cors, name='test-cors'),
    
    # Data exchange test (GET/POST)
    path('data-exchange/', test_views.test_data_exchange, name='test-data-exchange'),
]