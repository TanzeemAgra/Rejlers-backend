"""
HR AI Dashboard Views
====================

REST API endpoints for HR AI Dashboard with comprehensive analytics,
real-time data, and AI-powered insights.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .hr_analytics import hr_analytics_engine
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

class HRDashboardView(APIView):
    """
    Main HR Dashboard data endpoint
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request: Request) -> Response:
        """
        Get comprehensive HR dashboard data
        """
        try:
            user = request.user
            
            # Check authentication only for now
            if not user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Parse query parameters
            filters = self._parse_filters(request.query_params)
            date_range = self._parse_date_range(request.query_params)
            
            # Get dashboard data asynchronously
            dashboard_data = async_to_sync(hr_analytics_engine.get_comprehensive_dashboard_data)(
                user_id=str(user.id),
                filters=filters,
                date_range=date_range
            )
            
            return Response({
                'success': True,
                'data': dashboard_data,
                'user_permissions': {'hr_dashboard': True},  # Simplified permissions
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in HR Dashboard view: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to fetch dashboard data', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _parse_filters(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse filter parameters from request"""
        filters = {}
        
        if query_params.get('department'):
            filters['department'] = query_params.get('department').split(',')
        
        if query_params.get('position'):
            filters['position'] = query_params.get('position').split(',')
        
        if query_params.get('status'):
            filters['status'] = query_params.get('status').split(',')
        
        if query_params.get('employee_type'):
            filters['employee_type'] = query_params.get('employee_type').split(',')
        
        return filters
    
    def _parse_date_range(self, query_params: Dict[str, Any]) -> Optional[tuple]:
        """Parse date range from request parameters"""
        try:
            start_date = query_params.get('start_date')
            end_date = query_params.get('end_date')
            
            if start_date and end_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                return (start_dt, end_dt)
            
            # Default to last 12 months
            end_dt = timezone.now()
            start_dt = end_dt - timedelta(days=365)
            return (start_dt, end_dt)
            
        except ValueError as e:
            logger.warning(f"Invalid date range parameters: {str(e)}")
            return None

class WidgetDataView(APIView):
    """
    Individual widget data endpoint for real-time updates
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request: Request, widget_id: str) -> Response:
        """
        Get specific widget data with custom parameters
        """
        try:
            user = request.user
            
            if not user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Parse request data
            filters = request.data.get('filters', {})
            time_range = request.data.get('timeRange')
            refresh_interval = request.data.get('refreshInterval', 300)
            
            # Generate widget-specific data
            widget_data = self._get_widget_data(widget_id, user, filters, time_range)
            
            return Response({
                'success': True,
                'widget_id': widget_id,
                'data': widget_data,
                'timestamp': timezone.now().isoformat(),
                'next_refresh': (timezone.now() + timedelta(seconds=refresh_interval)).isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching widget data for {widget_id}: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to fetch widget data', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_widget_data(self, widget_id: str, user, filters: Dict[str, Any], time_range: Optional[str]) -> Dict[str, Any]:
        """
        Generate data for specific widget types
        """
        # Cache key for widget data
        cache_key = f"widget_data_{widget_id}_{user.id}_{hash(str(filters))}_{time_range}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Generate widget-specific data based on widget_id
        if widget_id == 'total_employees':
            data = self._get_employee_count_data(filters)
        elif widget_id == 'avg_performance':
            data = self._get_performance_data(filters, time_range)
        elif widget_id == 'employee_satisfaction':
            data = self._get_satisfaction_data(filters)
        elif widget_id == 'turnover_rate':
            data = self._get_turnover_data(filters, time_range)
        elif widget_id == 'employee_growth_trend':
            data = self._get_growth_trend_data(filters, time_range)
        elif widget_id == 'department_distribution':
            data = self._get_department_distribution_data(filters)
        elif widget_id == 'performance_trends':
            data = self._get_performance_trends_data(filters, time_range)
        elif widget_id == 'ai_hr_insights':
            data = self._get_ai_insights_data(filters)
        elif widget_id == 'active_recruitments':
            data = self._get_recruitment_data(filters)
        elif widget_id == 'attendance_rate':
            data = self._get_attendance_data(filters)
        elif widget_id == 'training_completion':
            data = self._get_training_data(filters)
        elif widget_id == 'payroll_processing':
            data = self._get_payroll_data(filters)
        elif widget_id == 'employee_list':
            data = self._get_employee_list_data(filters)
        elif widget_id == 'attendance_heatmap':
            data = self._get_attendance_heatmap_data(filters, time_range)
        elif widget_id == 'recruitment_pipeline':
            data = self._get_recruitment_pipeline_data(filters)
        else:
            data = {'error': f'Unknown widget: {widget_id}'}
        
        # Cache the data for 5 minutes
        cache.set(cache_key, data, timeout=300)
        return data
    
    def _get_employee_count_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get employee count metric data"""
        try:
            from apps.hr_management.models import Employee
            
            employees = Employee.objects.filter(status='active')
            
            if filters.get('department'):
                employees = employees.filter(department__name__in=filters['department'])
            
            current_count = employees.count()
            
            # Calculate trend (mock data for now)
            previous_count = int(current_count * 0.95)  # 5% growth
            trend_value = ((current_count - previous_count) / previous_count * 100) if previous_count > 0 else 0
            
            return {
                'value': current_count,
                'trend': {
                    'value': round(trend_value, 1),
                    'direction': 'up' if trend_value > 0 else 'down' if trend_value < 0 else 'stable',
                    'period': 'vs last month'
                },
                'status': 'good' if current_count > 0 else 'warning',
                'lastUpdated': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting employee count data: {str(e)}")
            return {'value': 0, 'error': str(e)}
    
    def _get_performance_data(self, filters: Dict[str, Any], time_range: Optional[str]) -> Dict[str, Any]:
        """Get performance metric data"""
        try:
            # Mock performance data
            avg_performance = 84.2
            target = 85.0
            
            return {
                'value': avg_performance,
                'target': target,
                'trend': {
                    'value': 3.2,
                    'direction': 'up',
                    'period': 'vs last quarter'
                },
                'status': 'good' if avg_performance >= target * 0.9 else 'warning',
                'lastUpdated': timezone.now().isoformat(),
                'sparklineData': [78, 79, 81, 82, 83, 84, 84.2]  # Last 7 periods
            }
        except Exception as e:
            logger.error(f"Error getting performance data: {str(e)}")
            return {'value': 0, 'error': str(e)}
    
    def _get_satisfaction_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get employee satisfaction data"""
        try:
            satisfaction_score = 78.5
            
            return {
                'value': satisfaction_score,
                'trend': {
                    'value': 2.1,
                    'direction': 'up',
                    'period': 'vs last quarter'
                },
                'status': 'good',
                'lastUpdated': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting satisfaction data: {str(e)}")
            return {'value': 0, 'error': str(e)}
    
    def _get_turnover_data(self, filters: Dict[str, Any], time_range: Optional[str]) -> Dict[str, Any]:
        """Get turnover rate data"""
        try:
            turnover_rate = 12.3
            
            return {
                'value': turnover_rate,
                'trend': {
                    'value': -1.8,
                    'direction': 'down',
                    'period': 'vs last year'
                },
                'status': 'good',
                'lastUpdated': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting turnover data: {str(e)}")
            return {'value': 0, 'error': str(e)}
    
    def _get_growth_trend_data(self, filters: Dict[str, Any], time_range: Optional[str]) -> Dict[str, Any]:
        """Get employee growth trend chart data"""
        try:
            # Generate mock growth trend data
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            headcount = [320, 325, 330, 335, 342, 348, 355, 362, 368, 375, 381, 387]
            
            chart_data = [
                {'month': month, 'count': count, 'predicted_count': count + (5 if i > 8 else 0)}
                for i, (month, count) in enumerate(zip(months, headcount))
            ]
            
            return {
                'chartData': chart_data,
                'statistics': {
                    'total_growth': 67,
                    'avg_monthly_growth': 5.6,
                    'growth_rate': 21.0
                },
                'trend': {
                    'direction': 'up',
                    'confidence': 87.5
                },
                'lastUpdated': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting growth trend data: {str(e)}")
            return {'chartData': [], 'error': str(e)}
    
    def _get_department_distribution_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get department distribution chart data"""
        try:
            # Mock department distribution
            departments = [
                {'department': 'Engineering', 'count': 145},
                {'department': 'Sales', 'count': 89},
                {'department': 'Marketing', 'count': 56},
                {'department': 'HR', 'count': 23},
                {'department': 'Finance', 'count': 34},
                {'department': 'Operations', 'count': 40}
            ]
            
            return {
                'chartData': departments,
                'statistics': {
                    'total_departments': len(departments),
                    'largest_department': 'Engineering',
                    'avg_department_size': sum(d['count'] for d in departments) // len(departments)
                },
                'lastUpdated': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting department distribution data: {str(e)}")
            return {'chartData': [], 'error': str(e)}
    
    def _get_ai_insights_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI insights data"""
        try:
            insights = [
                {
                    'type': 'prediction',
                    'title': 'Turnover Risk Alert',
                    'message': 'AI model predicts 15% increase in turnover risk for Sales department in Q4.',
                    'confidence': 87.5
                },
                {
                    'type': 'positive',
                    'title': 'Performance Improvement',
                    'message': 'Training programs have increased average performance by 8.5% this quarter.',
                    'confidence': 92.1
                },
                {
                    'type': 'warning',
                    'title': 'Attendance Pattern',
                    'message': 'Unusual Friday attendance patterns detected in Engineering department.',
                    'confidence': 76.3
                }
            ]
            
            return {
                'insights': insights,
                'lastUpdated': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting AI insights data: {str(e)}")
            return {'insights': [], 'error': str(e)}
    
    def _get_employee_list_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get employee list table data"""
        try:
            # Mock employee data
            employees = [
                {
                    'id': 1,
                    'name': 'John Doe',
                    'department': 'Engineering',
                    'position': 'Senior Developer',
                    'performance': 92,
                    'attendance': 96,
                    'status': 'active',
                    'avatar': None
                },
                {
                    'id': 2,
                    'name': 'Jane Smith',
                    'department': 'Sales',
                    'position': 'Sales Manager',
                    'performance': 88,
                    'attendance': 94,
                    'status': 'active',
                    'avatar': None
                },
                # Add more mock employees as needed
            ]
            
            return {
                'tableData': employees,
                'totalCount': len(employees),
                'lastUpdated': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting employee list data: {str(e)}")
            return {'tableData': [], 'error': str(e)}
    
    # Add more widget data methods as needed...
    def _get_recruitment_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock recruitment data"""
        return {
            'value': 25,
            'trend': {'value': 3, 'direction': 'up', 'period': 'this week'},
            'status': 'good',
            'lastUpdated': timezone.now().isoformat()
        }
    
    def _get_attendance_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock attendance data"""
        return {
            'value': 94.2,
            'target': 95.0,
            'trend': {'value': 1.2, 'direction': 'up', 'period': 'vs last month'},
            'status': 'good',
            'lastUpdated': timezone.now().isoformat()
        }
    
    def _get_training_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock training data"""
        return {
            'value': 78.5,
            'trend': {'value': 8.5, 'direction': 'up', 'period': 'this month'},
            'status': 'good',
            'lastUpdated': timezone.now().isoformat()
        }
    
    def _get_payroll_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock payroll data"""
        return {
            'value': 98.5,
            'status': 'good',
            'lastUpdated': timezone.now().isoformat()
        }
    
    def _get_attendance_heatmap_data(self, filters: Dict[str, Any], time_range: Optional[str]) -> Dict[str, Any]:
        """Mock attendance heatmap data"""
        return {
            'chartData': [],  # Would contain heatmap data
            'lastUpdated': timezone.now().isoformat()
        }
    
    def _get_recruitment_pipeline_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock recruitment pipeline data"""
        pipeline_data = [
            {'stage': 'Applied', 'count': 145},
            {'stage': 'Screening', 'count': 67},
            {'stage': 'Interview', 'count': 23},
            {'stage': 'Offer', 'count': 8}
        ]
        
        return {
            'chartData': pipeline_data,
            'lastUpdated': timezone.now().isoformat()
        }

class DashboardLayoutView(APIView):
    """
    Dashboard layout configuration endpoint
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request: Request, role: str) -> Response:
        """
        Get dashboard layout for specific role
        """
        try:
            user = request.user
            
            # Get personalized layout from cache/database
            layout_key = f"dashboard_layout_{role}_{user.id}"
            layout = cache.get(layout_key)
            
            if not layout:
                # Return default layout for role
                from frontend.src.config.hrDashboardConfig import HR_DASHBOARD_LAYOUTS
                layout = HR_DASHBOARD_LAYOUTS.get(role.lower())
            
            return Response({
                'success': True,
                'layout': layout,
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting dashboard layout: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to get layout', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request: Request) -> Response:
        """
        Save dashboard layout configuration
        """
        try:
            user = request.user
            
            if not user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            layout_data = request.data
            layout_key = f"dashboard_layout_{layout_data.get('role', 'custom')}_{user.id}"
            
            # Save layout to cache (in production, save to database)
            cache.set(layout_key, layout_data, timeout=86400 * 30)  # 30 days
            
            return Response({
                'success': True,
                'message': 'Layout saved successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error saving dashboard layout: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to save layout', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# WebSocket consumer for real-time updates (would be implemented in consumers.py)
async def send_dashboard_update(user_id: str, widget_id: str, data: Dict[str, Any]):
    """
    Send real-time update to dashboard via WebSocket
    """
    try:
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"hr_dashboard_{user_id}",
            {
                'type': 'dashboard_update',
                'widget_id': widget_id,
                'data': data,
                'timestamp': timezone.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error sending dashboard update: {str(e)}")