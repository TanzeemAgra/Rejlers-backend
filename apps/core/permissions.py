"""
Custom permissions for REJLERS applications
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsHRManagerOrReadOnly(BasePermission):
    """
    Permission for HR managers - can modify, others read only
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Check if user has HR management permissions
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or 
             request.user.has_perm('hr_management.change_employee') or
             request.user.groups.filter(name='HR_Managers').exists())
        )


class IsManagerOrOwner(BasePermission):
    """
    Permission for managers or object owners
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in SAFE_METHODS:
            # Managers can view employees in their department
            if hasattr(request.user, 'employee') and hasattr(obj, 'department'):
                user_dept = request.user.employee.department
                return user_dept == obj.department
            return True
        
        # Write permissions for owners or managers
        if hasattr(obj, 'user'):
            # Owner of the record
            if obj.user == request.user:
                return True
            
            # Manager of the employee
            if hasattr(obj, 'manager'):
                return obj.manager == request.user
        
        # HR managers can modify anything
        return (
            request.user.is_staff or
            request.user.has_perm('hr_management.change_employee') or
            request.user.groups.filter(name='HR_Managers').exists()
        )


class IsProjectManagerOrReadOnly(BasePermission):
    """
    Permission for project managers - can modify, others read only
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or 
             request.user.has_perm('projects.change_project') or
             request.user.groups.filter(name='Project_Managers').exists())
        )


class IsFinanceManagerOrReadOnly(BasePermission):
    """
    Permission for finance managers - can modify, others read only
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or 
             request.user.has_perm('finance.change_budget') or
             request.user.groups.filter(name='Finance_Managers').exists())
        )


class IsOwnerOrManagerOrReadOnly(BasePermission):
    """
    Permission for owners, managers, or read only for others
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions for owners
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Manager permissions
        if hasattr(obj, 'manager') and obj.manager == request.user:
            return True
        
        # Staff permissions
        return request.user.is_staff


class IsAdminOrManagerOrReadOnly(BasePermission):
    """
    Permission for admins, managers, or read only
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or 
             request.user.groups.filter(
                 name__in=['Managers', 'Department_Heads', 'Supervisors']
             ).exists())
        )