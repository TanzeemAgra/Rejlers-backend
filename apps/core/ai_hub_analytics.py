"""
AI Hub Analytics Engine
======================

Comprehensive AI-powered analytics and monitoring system for super admin:
- Security event aggregation and analysis
- Predictive modeling for access patterns
- Advanced threat detection algorithms
- Performance analytics and optimization
- Real-time monitoring and alerting
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import asyncio
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from guardian.models import UserObjectPermission, GroupObjectPermission

import logging
logger = logging.getLogger(__name__)

@dataclass
class SecurityMetrics:
    """Security metrics data structure"""
    total_requests: int
    failed_attempts: int
    success_rate: float
    high_risk_events: int
    anomaly_count: int
    avg_response_time: float
    active_users: int
    critical_alerts: int

@dataclass
class PredictionResult:
    """AI prediction result structure"""
    metric_name: str
    predicted_value: float
    confidence_score: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    recommendations: List[str]
    forecast_period: str

@dataclass
class SecurityAlert:
    """Security alert data structure"""
    alert_id: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    category: str  # 'authentication', 'authorization', 'anomaly', 'performance'
    message: str
    details: Dict[str, Any]
    user_id: Optional[str]
    timestamp: datetime
    resolved: bool = False

class AIHubAnalyticsEngine:
    """
    Advanced AI analytics engine for super admin monitoring
    """
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'AI_HUB_CACHE_TIMEOUT', 300)  # 5 minutes
        self.prediction_models = {}
        self.security_thresholds = {
            'failed_login_rate': 0.15,
            'anomaly_rate': 0.05,
            'response_time_threshold': 2000,  # ms
            'concurrent_users_limit': 1000,
            'high_risk_score': 0.8
        }
        self.alert_history = deque(maxlen=10000)
        self.metrics_history = deque(maxlen=1000)
        
    async def get_comprehensive_security_metrics(self) -> SecurityMetrics:
        """
        Aggregate comprehensive security metrics from all RBAC components
        """
        cache_key = 'ai_hub:security_metrics'
        cached_metrics = cache.get(cache_key)
        
        if cached_metrics:
            return SecurityMetrics(**cached_metrics)
        
        try:
            # Aggregate from multiple sources
            rbac_metrics = await self._get_rbac_metrics()
            auth_metrics = await self._get_authentication_metrics()
            performance_metrics = await self._get_performance_metrics()
            user_metrics = await self._get_user_activity_metrics()
            
            # Combine all metrics
            combined_metrics = SecurityMetrics(
                total_requests=rbac_metrics.get('total_requests', 0) + auth_metrics.get('total_requests', 0),
                failed_attempts=auth_metrics.get('failed_attempts', 0),
                success_rate=self._calculate_success_rate(rbac_metrics, auth_metrics),
                high_risk_events=rbac_metrics.get('high_risk_events', 0),
                anomaly_count=await self._count_anomalies(),
                avg_response_time=performance_metrics.get('avg_response_time', 0),
                active_users=user_metrics.get('active_users', 0),
                critical_alerts=await self._count_critical_alerts()
            )
            
            # Cache the results
            cache.set(cache_key, asdict(combined_metrics), self.cache_timeout)
            
            # Store in history for trend analysis
            self.metrics_history.append({
                'timestamp': timezone.now(),
                'metrics': combined_metrics
            })
            
            return combined_metrics
            
        except Exception as e:
            logger.error(f"Error getting security metrics: {e}")
            return SecurityMetrics(0, 0, 0.0, 0, 0, 0.0, 0, 0)
    
    async def _get_rbac_metrics(self) -> Dict[str, int]:
        """Get RBAC-specific metrics from the enforcement system"""
        from apps.core.rbac_enforcement import AdvancedPermissionManager
        
        try:
            permission_manager = AdvancedPermissionManager()
            
            # Get cached RBAC statistics
            rbac_stats = cache.get('rbac_enforcement:daily_stats', {})
            
            return {
                'total_requests': rbac_stats.get('total_permission_checks', 0),
                'denied_requests': rbac_stats.get('denied_permissions', 0),
                'high_risk_events': rbac_stats.get('high_risk_accesses', 0),
                'ai_interventions': rbac_stats.get('ai_interventions', 0)
            }
        except Exception as e:
            logger.error(f"Error getting RBAC metrics: {e}")
            return {}
    
    async def _get_authentication_metrics(self) -> Dict[str, int]:
        """Get authentication metrics"""
        try:
            # Get authentication statistics from cache or database
            auth_stats = cache.get('auth:daily_stats', {})
            
            return {
                'total_requests': auth_stats.get('login_attempts', 0),
                'failed_attempts': auth_stats.get('failed_logins', 0),
                'successful_logins': auth_stats.get('successful_logins', 0),
                'token_refreshes': auth_stats.get('token_refreshes', 0)
            }
        except Exception as e:
            logger.error(f"Error getting auth metrics: {e}")
            return {}
    
    async def _get_performance_metrics(self) -> Dict[str, float]:
        """Get system performance metrics"""
        try:
            perf_stats = cache.get('system:performance_stats', {})
            
            return {
                'avg_response_time': perf_stats.get('avg_response_time', 0.0),
                'db_query_time': perf_stats.get('db_query_time', 0.0),
                'cache_hit_ratio': perf_stats.get('cache_hit_ratio', 0.0),
                'memory_usage': perf_stats.get('memory_usage', 0.0)
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def _get_user_activity_metrics(self) -> Dict[str, int]:
        """Get user activity metrics"""
        try:
            # Count active users in the last hour
            one_hour_ago = timezone.now() - timedelta(hours=1)
            
            # This would typically query active sessions or recent activity
            user_stats = cache.get('users:activity_stats', {})
            
            return {
                'active_users': user_stats.get('active_users_1h', 0),
                'new_users_today': user_stats.get('new_users_today', 0),
                'concurrent_sessions': user_stats.get('concurrent_sessions', 0)
            }
        except Exception as e:
            logger.error(f"Error getting user metrics: {e}")
            return {}
    
    def _calculate_success_rate(self, rbac_metrics: Dict, auth_metrics: Dict) -> float:
        """Calculate overall system success rate"""
        total_requests = rbac_metrics.get('total_requests', 0) + auth_metrics.get('total_requests', 0)
        total_failures = rbac_metrics.get('denied_requests', 0) + auth_metrics.get('failed_attempts', 0)
        
        if total_requests == 0:
            return 1.0
        
        return max(0.0, (total_requests - total_failures) / total_requests)
    
    async def _count_anomalies(self) -> int:
        """Count detected anomalies in the system"""
        try:
            # Get anomaly count from AI detection system
            anomaly_stats = cache.get('ai:anomaly_detection', {})
            return anomaly_stats.get('anomaly_count_24h', 0)
        except Exception as e:
            logger.error(f"Error counting anomalies: {e}")
            return 0
    
    async def _count_critical_alerts(self) -> int:
        """Count critical security alerts"""
        try:
            # Count unresolved critical alerts
            critical_count = 0
            for alert_data in self.alert_history:
                if isinstance(alert_data, dict):
                    alert = SecurityAlert(**alert_data)
                    if alert.severity == 'critical' and not alert.resolved:
                        critical_count += 1
            return critical_count
        except Exception as e:
            logger.error(f"Error counting critical alerts: {e}")
            return 0
    
    async def generate_predictive_analytics(self, time_horizon: str = '24h') -> List[PredictionResult]:
        """
        Generate AI-powered predictive analytics for security metrics
        """
        cache_key = f'ai_hub:predictions:{time_horizon}'
        cached_predictions = cache.get(cache_key)
        
        if cached_predictions:
            return [PredictionResult(**pred) for pred in cached_predictions]
        
        try:
            predictions = []
            
            # Predict security trends
            security_prediction = await self._predict_security_trends(time_horizon)
            predictions.append(security_prediction)
            
            # Predict user activity
            activity_prediction = await self._predict_user_activity(time_horizon)
            predictions.append(activity_prediction)
            
            # Predict performance metrics
            performance_prediction = await self._predict_performance_trends(time_horizon)
            predictions.append(performance_prediction)
            
            # Predict risk levels
            risk_prediction = await self._predict_risk_levels(time_horizon)
            predictions.append(risk_prediction)
            
            # Cache predictions
            cache.set(cache_key, [asdict(pred) for pred in predictions], self.cache_timeout)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return []
    
    async def _predict_security_trends(self, time_horizon: str) -> PredictionResult:
        """Predict security event trends using AI"""
        try:
            # Get historical data
            historical_data = self._get_historical_security_data()
            
            if len(historical_data) < 10:
                # Not enough data for prediction
                return PredictionResult(
                    metric_name="Security Events",
                    predicted_value=0.0,
                    confidence_score=0.0,
                    trend_direction="stable",
                    risk_level="low",
                    recommendations=["Insufficient historical data for prediction"],
                    forecast_period=time_horizon
                )
            
            # Simple trend analysis (in production, use ML models)
            recent_events = [data['security_events'] for data in historical_data[-10:]]
            trend = np.polyfit(range(len(recent_events)), recent_events, 1)[0]
            
            # Calculate prediction
            predicted_events = recent_events[-1] + (trend * self._get_time_multiplier(time_horizon))
            confidence = min(0.95, len(historical_data) / 100)  # Higher confidence with more data
            
            # Determine trend direction and risk
            if trend > 0.1:
                trend_direction = "increasing"
                risk_level = "high" if predicted_events > 100 else "medium"
            elif trend < -0.1:
                trend_direction = "decreasing"
                risk_level = "low"
            else:
                trend_direction = "stable"
                risk_level = "medium"
            
            recommendations = self._generate_security_recommendations(predicted_events, trend_direction)
            
            return PredictionResult(
                metric_name="Security Events",
                predicted_value=max(0, predicted_events),
                confidence_score=confidence,
                trend_direction=trend_direction,
                risk_level=risk_level,
                recommendations=recommendations,
                forecast_period=time_horizon
            )
            
        except Exception as e:
            logger.error(f"Error predicting security trends: {e}")
            return PredictionResult("Security Events", 0.0, 0.0, "stable", "low", [], time_horizon)
    
    async def _predict_user_activity(self, time_horizon: str) -> PredictionResult:
        """Predict user activity patterns"""
        try:
            # Get user activity history
            activity_data = self._get_historical_activity_data()
            
            if len(activity_data) < 5:
                return PredictionResult(
                    metric_name="User Activity",
                    predicted_value=0.0,
                    confidence_score=0.0,
                    trend_direction="stable",
                    risk_level="low",
                    recommendations=["Need more activity data"],
                    forecast_period=time_horizon
                )
            
            # Analyze patterns
            recent_activity = [data['active_users'] for data in activity_data[-7:]]  # Last 7 periods
            avg_activity = np.mean(recent_activity)
            trend = np.polyfit(range(len(recent_activity)), recent_activity, 1)[0]
            
            predicted_activity = avg_activity + (trend * self._get_time_multiplier(time_horizon))
            confidence = min(0.9, len(activity_data) / 50)
            
            # Determine trend and risk
            if trend > 2:
                trend_direction = "increasing"
                risk_level = "low"  # More users is generally good
            elif trend < -2:
                trend_direction = "decreasing"
                risk_level = "medium"  # Decreasing activity might be concerning
            else:
                trend_direction = "stable"
                risk_level = "low"
            
            recommendations = self._generate_activity_recommendations(predicted_activity, trend_direction)
            
            return PredictionResult(
                metric_name="User Activity",
                predicted_value=max(0, predicted_activity),
                confidence_score=confidence,
                trend_direction=trend_direction,
                risk_level=risk_level,
                recommendations=recommendations,
                forecast_period=time_horizon
            )
            
        except Exception as e:
            logger.error(f"Error predicting user activity: {e}")
            return PredictionResult("User Activity", 0.0, 0.0, "stable", "low", [], time_horizon)
    
    async def _predict_performance_trends(self, time_horizon: str) -> PredictionResult:
        """Predict system performance trends"""
        try:
            performance_data = self._get_historical_performance_data()
            
            if len(performance_data) < 5:
                return PredictionResult(
                    metric_name="System Performance",
                    predicted_value=100.0,  # Assume good performance
                    confidence_score=0.0,
                    trend_direction="stable",
                    risk_level="low",
                    recommendations=["Need more performance data"],
                    forecast_period=time_horizon
                )
            
            # Calculate performance score (inverse of response time)
            recent_times = [data['avg_response_time'] for data in performance_data[-10:]]
            avg_time = np.mean(recent_times)
            trend = np.polyfit(range(len(recent_times)), recent_times, 1)[0]
            
            # Predict future performance (lower response time = better performance)
            predicted_time = avg_time + (trend * self._get_time_multiplier(time_horizon))
            performance_score = max(0, 100 - (predicted_time / 10))  # Convert to 0-100 score
            
            confidence = min(0.85, len(performance_data) / 30)
            
            # Determine trend (inverted because lower response time is better)
            if trend > 50:  # Response time increasing significantly
                trend_direction = "decreasing"  # Performance decreasing
                risk_level = "high"
            elif trend < -50:  # Response time decreasing significantly
                trend_direction = "increasing"  # Performance increasing
                risk_level = "low"
            else:
                trend_direction = "stable"
                risk_level = "medium" if predicted_time > 1000 else "low"
            
            recommendations = self._generate_performance_recommendations(predicted_time, trend_direction)
            
            return PredictionResult(
                metric_name="System Performance",
                predicted_value=performance_score,
                confidence_score=confidence,
                trend_direction=trend_direction,
                risk_level=risk_level,
                recommendations=recommendations,
                forecast_period=time_horizon
            )
            
        except Exception as e:
            logger.error(f"Error predicting performance: {e}")
            return PredictionResult("System Performance", 100.0, 0.0, "stable", "low", [], time_horizon)
    
    async def _predict_risk_levels(self, time_horizon: str) -> PredictionResult:
        """Predict overall system risk levels"""
        try:
            risk_data = self._get_historical_risk_data()
            
            if len(risk_data) < 5:
                return PredictionResult(
                    metric_name="Risk Level",
                    predicted_value=20.0,  # Assume low risk
                    confidence_score=0.0,
                    trend_direction="stable",
                    risk_level="low",
                    recommendations=["Need more risk assessment data"],
                    forecast_period=time_horizon
                )
            
            # Calculate risk trend
            recent_risks = [data['risk_score'] * 100 for data in risk_data[-7:]]
            avg_risk = np.mean(recent_risks)
            trend = np.polyfit(range(len(recent_risks)), recent_risks, 1)[0]
            
            predicted_risk = max(0, min(100, avg_risk + (trend * self._get_time_multiplier(time_horizon))))
            confidence = min(0.9, len(risk_data) / 40)
            
            # Determine trend and risk level
            if trend > 5:
                trend_direction = "increasing"
                risk_level = "high" if predicted_risk > 70 else "medium"
            elif trend < -5:
                trend_direction = "decreasing"
                risk_level = "low" if predicted_risk < 30 else "medium"
            else:
                trend_direction = "stable"
                if predicted_risk > 70:
                    risk_level = "high"
                elif predicted_risk > 40:
                    risk_level = "medium"
                else:
                    risk_level = "low"
            
            recommendations = self._generate_risk_recommendations(predicted_risk, trend_direction)
            
            return PredictionResult(
                metric_name="Risk Level",
                predicted_value=predicted_risk,
                confidence_score=confidence,
                trend_direction=trend_direction,
                risk_level=risk_level,
                recommendations=recommendations,
                forecast_period=time_horizon
            )
            
        except Exception as e:
            logger.error(f"Error predicting risk levels: {e}")
            return PredictionResult("Risk Level", 20.0, 0.0, "stable", "low", [], time_horizon)
    
    def _get_time_multiplier(self, time_horizon: str) -> float:
        """Convert time horizon to multiplier"""
        multipliers = {
            '1h': 0.1,
            '6h': 0.5,
            '12h': 1.0,
            '24h': 2.0,
            '7d': 14.0,
            '30d': 60.0
        }
        return multipliers.get(time_horizon, 1.0)
    
    def _get_historical_security_data(self) -> List[Dict]:
        """Get historical security data"""
        # In production, this would query actual historical data
        historical_data = cache.get('ai_hub:historical_security', [])
        if not historical_data:
            # Generate sample data for demonstration
            historical_data = [
                {'timestamp': timezone.now() - timedelta(hours=i), 'security_events': max(0, 50 + np.random.randint(-20, 21))}
                for i in range(24, 0, -1)
            ]
        return historical_data
    
    def _get_historical_activity_data(self) -> List[Dict]:
        """Get historical user activity data"""
        historical_data = cache.get('ai_hub:historical_activity', [])
        if not historical_data:
            # Generate sample data
            historical_data = [
                {'timestamp': timezone.now() - timedelta(hours=i), 'active_users': max(0, 100 + np.random.randint(-30, 31))}
                for i in range(24, 0, -1)
            ]
        return historical_data
    
    def _get_historical_performance_data(self) -> List[Dict]:
        """Get historical performance data"""
        historical_data = cache.get('ai_hub:historical_performance', [])
        if not historical_data:
            # Generate sample data
            historical_data = [
                {'timestamp': timezone.now() - timedelta(hours=i), 'avg_response_time': max(100, 500 + np.random.randint(-200, 201))}
                for i in range(24, 0, -1)
            ]
        return historical_data
    
    def _get_historical_risk_data(self) -> List[Dict]:
        """Get historical risk assessment data"""
        historical_data = cache.get('ai_hub:historical_risk', [])
        if not historical_data:
            # Generate sample data
            historical_data = [
                {'timestamp': timezone.now() - timedelta(hours=i), 'risk_score': max(0, min(1, 0.3 + np.random.normal(0, 0.1)))}
                for i in range(24, 0, -1)
            ]
        return historical_data
    
    def _generate_security_recommendations(self, predicted_events: float, trend: str) -> List[str]:
        """Generate security-related recommendations"""
        recommendations = []
        
        if predicted_events > 100:
            recommendations.append("Consider increasing security monitoring frequency")
            recommendations.append("Review and update access policies")
        
        if trend == "increasing":
            recommendations.append("Investigate causes of increasing security events")
            recommendations.append("Enable enhanced logging and monitoring")
            recommendations.append("Consider implementing additional security controls")
        elif trend == "decreasing":
            recommendations.append("Security improvements are showing positive results")
            recommendations.append("Maintain current security posture")
        
        return recommendations or ["Continue monitoring security metrics"]
    
    def _generate_activity_recommendations(self, predicted_activity: float, trend: str) -> List[str]:
        """Generate user activity recommendations"""
        recommendations = []
        
        if predicted_activity < 50:
            recommendations.append("Low user activity detected - investigate potential issues")
            recommendations.append("Consider user engagement initiatives")
        
        if trend == "decreasing":
            recommendations.append("Declining user activity - check system accessibility")
            recommendations.append("Review recent system changes that might affect usability")
        elif trend == "increasing":
            recommendations.append("Growing user activity - ensure system scalability")
            recommendations.append("Monitor performance under increased load")
        
        return recommendations or ["Monitor user engagement patterns"]
    
    def _generate_performance_recommendations(self, predicted_time: float, trend: str) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if predicted_time > 2000:
            recommendations.append("High response times predicted - optimize database queries")
            recommendations.append("Consider scaling infrastructure")
            recommendations.append("Review caching strategies")
        
        if trend == "decreasing":  # Performance getting worse
            recommendations.append("Performance degradation detected")
            recommendations.append("Investigate resource bottlenecks")
            recommendations.append("Consider load balancing improvements")
        elif trend == "increasing":  # Performance improving
            recommendations.append("Performance improvements detected")
            recommendations.append("Continue current optimization strategies")
        
        return recommendations or ["Maintain performance monitoring"]
    
    def _generate_risk_recommendations(self, predicted_risk: float, trend: str) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        if predicted_risk > 70:
            recommendations.append("High risk levels predicted - implement immediate security measures")
            recommendations.append("Conduct security audit")
            recommendations.append("Review access controls and permissions")
        elif predicted_risk > 40:
            recommendations.append("Moderate risk levels - maintain vigilance")
            recommendations.append("Regular security assessments recommended")
        
        if trend == "increasing":
            recommendations.append("Rising risk levels - investigate root causes")
            recommendations.append("Consider additional security training")
            recommendations.append("Implement enhanced monitoring")
        elif trend == "decreasing":
            recommendations.append("Risk levels improving - continue current practices")
        
        return recommendations or ["Maintain current risk management practices"]
    
    async def generate_security_alerts(self) -> List[SecurityAlert]:
        """
        Generate real-time security alerts based on current metrics and AI analysis
        """
        try:
            alerts = []
            current_metrics = await self.get_comprehensive_security_metrics()
            
            # Check for various alert conditions
            
            # High failure rate alert
            if current_metrics.success_rate < (1 - self.security_thresholds['failed_login_rate']):
                alert = SecurityAlert(
                    alert_id=f"high_failure_rate_{int(timezone.now().timestamp())}",
                    severity="high",
                    category="authentication",
                    message=f"High failure rate detected: {(1-current_metrics.success_rate)*100:.1f}%",
                    details={
                        "success_rate": current_metrics.success_rate,
                        "threshold": self.security_thresholds['failed_login_rate'],
                        "failed_attempts": current_metrics.failed_attempts
                    },
                    user_id=None,
                    timestamp=timezone.now()
                )
                alerts.append(alert)
                self.alert_history.append(asdict(alert))
            
            # High response time alert
            if current_metrics.avg_response_time > self.security_thresholds['response_time_threshold']:
                alert = SecurityAlert(
                    alert_id=f"high_response_time_{int(timezone.now().timestamp())}",
                    severity="medium",
                    category="performance",
                    message=f"High response time detected: {current_metrics.avg_response_time:.0f}ms",
                    details={
                        "response_time": current_metrics.avg_response_time,
                        "threshold": self.security_thresholds['response_time_threshold']
                    },
                    user_id=None,
                    timestamp=timezone.now()
                )
                alerts.append(alert)
                self.alert_history.append(asdict(alert))
            
            # High anomaly count alert
            if current_metrics.anomaly_count > 10:
                alert = SecurityAlert(
                    alert_id=f"high_anomaly_count_{int(timezone.now().timestamp())}",
                    severity="critical",
                    category="anomaly",
                    message=f"High anomaly count detected: {current_metrics.anomaly_count}",
                    details={
                        "anomaly_count": current_metrics.anomaly_count,
                        "time_window": "last_hour"
                    },
                    user_id=None,
                    timestamp=timezone.now()
                )
                alerts.append(alert)
                self.alert_history.append(asdict(alert))
            
            # Critical alerts threshold
            if current_metrics.critical_alerts > 5:
                alert = SecurityAlert(
                    alert_id=f"critical_alerts_threshold_{int(timezone.now().timestamp())}",
                    severity="critical",
                    category="security",
                    message=f"Multiple critical alerts active: {current_metrics.critical_alerts}",
                    details={
                        "critical_count": current_metrics.critical_alerts
                    },
                    user_id=None,
                    timestamp=timezone.now()
                )
                alerts.append(alert)
                self.alert_history.append(asdict(alert))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating security alerts: {e}")
            return []
    
    async def get_ai_insights_summary(self) -> Dict[str, Any]:
        """
        Generate comprehensive AI insights summary for the super admin dashboard
        """
        try:
            metrics = await self.get_comprehensive_security_metrics()
            predictions = await self.generate_predictive_analytics()
            alerts = await self.generate_security_alerts()
            
            # Calculate trends
            trends = self._calculate_trends()
            
            # Generate summary insights
            insights = {
                'overall_health_score': self._calculate_health_score(metrics, predictions),
                'security_status': self._assess_security_status(metrics, alerts),
                'performance_status': self._assess_performance_status(metrics),
                'user_engagement': self._assess_user_engagement(metrics),
                'risk_assessment': self._assess_overall_risk(predictions),
                'trending_metrics': trends,
                'ai_recommendations': self._generate_ai_recommendations(metrics, predictions, alerts),
                'next_review_time': timezone.now() + timedelta(minutes=15),
                'data_freshness': timezone.now(),
                'confidence_score': self._calculate_confidence_score(predictions)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {}
    
    def _calculate_health_score(self, metrics: SecurityMetrics, predictions: List[PredictionResult]) -> float:
        """Calculate overall system health score (0-100)"""
        try:
            # Weight different factors
            success_rate_score = metrics.success_rate * 100
            performance_score = max(0, 100 - (metrics.avg_response_time / 20))
            security_score = max(0, 100 - (metrics.critical_alerts * 10))
            
            # Include prediction confidence
            prediction_confidence = np.mean([pred.confidence_score for pred in predictions]) if predictions else 0.5
            
            # Weighted average
            health_score = (
                success_rate_score * 0.3 +
                performance_score * 0.3 +
                security_score * 0.3 +
                prediction_confidence * 100 * 0.1
            )
            
            return max(0, min(100, health_score))
            
        except Exception:
            return 75.0  # Default moderate health score
    
    def _assess_security_status(self, metrics: SecurityMetrics, alerts: List[SecurityAlert]) -> str:
        """Assess overall security status"""
        critical_alerts = sum(1 for alert in alerts if alert.severity == 'critical')
        high_alerts = sum(1 for alert in alerts if alert.severity == 'high')
        
        if critical_alerts > 0:
            return "Critical"
        elif high_alerts > 2 or metrics.success_rate < 0.9:
            return "Warning"
        elif metrics.success_rate > 0.95 and metrics.anomaly_count < 5:
            return "Excellent"
        else:
            return "Good"
    
    def _assess_performance_status(self, metrics: SecurityMetrics) -> str:
        """Assess system performance status"""
        if metrics.avg_response_time > 2000:
            return "Poor"
        elif metrics.avg_response_time > 1000:
            return "Fair"
        elif metrics.avg_response_time > 500:
            return "Good"
        else:
            return "Excellent"
    
    def _assess_user_engagement(self, metrics: SecurityMetrics) -> str:
        """Assess user engagement level"""
        if metrics.active_users > 200:
            return "High"
        elif metrics.active_users > 100:
            return "Moderate"
        elif metrics.active_users > 50:
            return "Low"
        else:
            return "Very Low"
    
    def _assess_overall_risk(self, predictions: List[PredictionResult]) -> str:
        """Assess overall system risk"""
        risk_predictions = [pred for pred in predictions if 'risk' in pred.metric_name.lower()]
        
        if not risk_predictions:
            return "Unknown"
        
        risk_levels = [pred.risk_level for pred in risk_predictions]
        
        if 'critical' in risk_levels:
            return "Critical"
        elif 'high' in risk_levels:
            return "High"
        elif 'medium' in risk_levels:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_trends(self) -> Dict[str, str]:
        """Calculate trending metrics"""
        if len(self.metrics_history) < 2:
            return {}
        
        current = self.metrics_history[-1]['metrics']
        previous = self.metrics_history[-2]['metrics']
        
        trends = {}
        
        # Calculate trends for key metrics
        if previous.total_requests > 0:
            request_trend = ((current.total_requests - previous.total_requests) / previous.total_requests) * 100
            trends['requests'] = 'increasing' if request_trend > 5 else ('decreasing' if request_trend < -5 else 'stable')
        
        success_trend = current.success_rate - previous.success_rate
        trends['success_rate'] = 'increasing' if success_trend > 0.05 else ('decreasing' if success_trend < -0.05 else 'stable')
        
        response_trend = current.avg_response_time - previous.avg_response_time
        trends['response_time'] = 'increasing' if response_trend > 100 else ('decreasing' if response_trend < -100 else 'stable')
        
        return trends
    
    def _generate_ai_recommendations(self, metrics: SecurityMetrics, predictions: List[PredictionResult], alerts: List[SecurityAlert]) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        # Performance recommendations
        if metrics.avg_response_time > 1500:
            recommendations.append("🚀 Optimize database queries and implement caching")
        
        # Security recommendations
        if metrics.success_rate < 0.9:
            recommendations.append("🔒 Review authentication mechanisms and security policies")
        
        # User engagement recommendations
        if metrics.active_users < 100:
            recommendations.append("👥 Investigate user engagement and system accessibility")
        
        # Predictive recommendations
        for prediction in predictions:
            if prediction.risk_level in ['high', 'critical']:
                recommendations.extend(prediction.recommendations[:2])  # Take top 2
        
        # Alert-based recommendations
        if len(alerts) > 3:
            recommendations.append("⚠️ Investigate root causes of multiple simultaneous alerts")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_confidence_score(self, predictions: List[PredictionResult]) -> float:
        """Calculate overall confidence in AI predictions"""
        if not predictions:
            return 0.0
        
        return np.mean([pred.confidence_score for pred in predictions])


# Global instance for the AI Hub Analytics Engine
ai_hub_engine = AIHubAnalyticsEngine()