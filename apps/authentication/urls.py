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
    path('roles/<uuid:id>/', views.RoleDetailView.as_view(), name='role_detail'),
    path('roles/<uuid:role_id>/users/', views.RoleUsersView.as_view(), name='role_users'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('assign-role/', views.UserRoleAssignmentView.as_view(), name='assign_role'),
    
    # Permission checking and user permissions
    path('permissions/', views.UserPermissionsView.as_view(), name='user_permissions'),
    path('check-permission/', views.UserPermissionCheckView.as_view(), name='check_permission'),
    path('check-module-permission/', views.check_module_permission, name='check_module_permission'),
    
    # RBAC system information
    path('rbac-info/', views.rbac_system_info, name='rbac_system_info'),
    
    # Audit logs (admin only)
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_logs'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]