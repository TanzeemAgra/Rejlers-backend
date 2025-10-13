"""
URL patterns for REJLERS RBAC authentication system
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('dashboard/', views.user_dashboard_data, name='user_dashboard'),
    
    # RBAC management endpoints (admin only)
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/<uuid:pk>/', views.RoleDetailView.as_view(), name='role_detail'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Permission checking
    path('check-permission/', views.UserPermissionCheckView.as_view(), name='check_permission'),
    
    # Audit logs (admin only)
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_logs'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]