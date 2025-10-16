from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Avg, Count, Sum, Q, F
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from decimal import Decimal
from apps.core.permissions import IsHRManagerOrReadOnly
from apps.core.pagination import StandardResultsSetPagination

from .models import (
    SafetyIncident, ComplianceChecklist, ChecklistAssessment, EnvironmentalMonitoring,
    RegulatoryFramework, ComplianceControl, ComplianceAssessment, 
    ControlAssessmentResult, AIComplianceInsight
)
from .serializers import (
    SafetyIncidentSerializer, ComplianceChecklistSerializer, ChecklistAssessmentSerializer,
    EnvironmentalMonitoringSerializer, RegulatoryFrameworkSerializer, ComplianceControlSerializer,
    ComplianceAssessmentDetailSerializer, ComplianceAssessmentListSerializer,
    ControlAssessmentResultSerializer, AIComplianceInsightSerializer,
    ComplianceDashboardSerializer, ComplianceMetricsSerializer
)

# AI Analytics Service (Simulated - can be replaced with actual ML/AI service)
class AIComplianceAnalyticsService:
    """AI-powered compliance analytics service"""
    
    @staticmethod
    def generate_insights(framework=None):
        """Generate AI insights for compliance frameworks"""
        insights = []
        
        # Sample AI-generated insights (in production, this would call actual ML models)
        if framework is None or framework.framework_code == 'ISO_27001':
            insights.append({
                'framework_code': 'ISO_27001',
                'insight_type': 'RISK_PREDICTION',
                'title': 'ISO 27001 Control Gap Detected',
                'description': 'AI analysis indicates potential non-compliance risk in access control procedures (A.9.1.1)',
                'confidence_score': Decimal('89.5'),
                'priority_level': 'HIGH',
                'recommendations': [
                    'Review user access provisioning processes',
                    'Implement automated access review workflows',
                    'Update access control policy documentation'
                ]
            })
        
        if framework is None or framework.framework_code == 'GDPR_UAE':
            insights.append({
                'framework_code': 'GDPR_UAE',
                'insight_type': 'POLICY_RECOMMENDATION',
                'title': 'Data Retention Policy Enhancement',
                'description': 'Predictive analysis suggests updating data retention schedules to improve GDPR Article 17 compliance',
                'confidence_score': Decimal('92.3'),
                'priority_level': 'MEDIUM',
                'recommendations': [
                    'Implement automated data lifecycle management',
                    'Update consent management workflows',
                    'Review data processing agreements'
                ]
            })
            
        return insights
    
    @staticmethod
    def calculate_predictive_scores(framework_code):
        """Calculate predictive compliance scores"""
        # AI-powered predictive scoring (simulated)
        base_scores = {
            'ISO_27001': Decimal('97.3'),
            'API_Q1_Q2': Decimal('99.1'),
            'IEC_62443': Decimal('95.8'),
            'NIST_SP_800_53': Decimal('99.5'),
            'GDPR_UAE': Decimal('98.9'),
        }
        
        return base_scores.get(framework_code, Decimal('95.0'))
    
    @staticmethod
    def get_compliance_trends(framework_code, months=6):
        """Generate compliance trend data"""
        # Generate sample trend data (replace with actual analytics)
        trends = []
        base_score = AIComplianceAnalyticsService.calculate_predictive_scores(framework_code)
        
        for i in range(months):
            month_date = timezone.now() - timedelta(days=30 * i)
            # Add some variability to simulate trends
            score_variation = Decimal(str((-1 if i % 2 else 1) * (i * 0.5)))
            score = max(Decimal('85.0'), min(Decimal('100.0'), base_score + score_variation))
            
            trends.insert(0, {
                'month': month_date.strftime('%Y-%m'),
                'compliance_score': float(score),
                'assessments_count': 3 + (i % 3),
                'issues_resolved': 2 + (i % 4)
            })
        
        return trends

# ============================================================================
# REGULATORY COMPLIANCE VIEWSETS
# ============================================================================

class RegulatoryFrameworkViewSet(viewsets.ModelViewSet):
    """Regulatory framework management"""
    queryset = RegulatoryFramework.objects.filter(is_active=True)
    serializer_class = RegulatoryFrameworkSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['framework_code', 'regulatory_body']
    search_fields = ['name', 'description', 'framework_code']
    ordering_fields = ['framework_code', 'name', 'created_at']
    ordering = ['framework_code']
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get compliance dashboard for specific framework"""
        framework = self.get_object()
        
        # Get compliance statistics
        total_controls = framework.controls.filter(is_active=True).count()
        
        # Get latest assessment results
        latest_assessment = framework.complianceassessment_set.filter(
            status='COMPLIANT'
        ).order_by('-actual_end_date').first()
        
        compliance_score = AIComplianceAnalyticsService.calculate_predictive_scores(
            framework.framework_code
        )
        
        # Calculate control compliance breakdown
        if latest_assessment:
            control_stats = latest_assessment.control_results.aggregate(
                compliant=Count('id', filter=Q(compliance_status='COMPLIANT')),
                non_compliant=Count('id', filter=Q(compliance_status='NON_COMPLIANT')),
                partial=Count('id', filter=Q(compliance_status='PARTIALLY_COMPLIANT')),
                pending=Count('id', filter=Q(compliance_status='NOT_ASSESSED'))
            )
        else:
            control_stats = {
                'compliant': int(total_controls * 0.85),
                'non_compliant': int(total_controls * 0.05),
                'partial': int(total_controls * 0.05),
                'pending': int(total_controls * 0.05)
            }
        
        # Get compliance trends
        trends = AIComplianceAnalyticsService.get_compliance_trends(framework.framework_code)
        
        # Calculate next assessment due date
        next_assessment_due = timezone.now().date() + timedelta(days=90)
        
        # Determine risk level based on compliance score
        if compliance_score >= 98:
            risk_level = 'Low'
        elif compliance_score >= 95:
            risk_level = 'Medium'
        elif compliance_score >= 90:
            risk_level = 'High'
        else:
            risk_level = 'Critical'
        
        dashboard_data = {
            'framework_code': framework.framework_code,
            'framework_name': framework.name,
            'compliance_score': compliance_score,
            'total_controls': total_controls,
            'compliant_controls': control_stats['compliant'],
            'non_compliant_controls': control_stats['non_compliant'],
            'pending_controls': control_stats['pending'],
            'last_assessment_date': latest_assessment.actual_end_date if latest_assessment else None,
            'next_assessment_due': next_assessment_due,
            'risk_level': risk_level,
            'compliance_trend': trends,
            'urgent_actions': 2,  # Would be calculated from actual action items
            'overdue_actions': 1
        }
        
        serializer = ComplianceDashboardSerializer(dashboard_data)
        return Response(serializer.data)

class ComplianceControlViewSet(viewsets.ModelViewSet):
    """Compliance control management"""
    queryset = ComplianceControl.objects.select_related('framework').filter(is_active=True)
    serializer_class = ComplianceControlSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['framework', 'control_type', 'risk_level', 'is_mandatory']
    search_fields = ['control_id', 'control_name', 'description']
    ordering_fields = ['control_id', 'control_name', 'risk_level', 'created_at']
    ordering = ['framework__framework_code', 'control_id']

class ComplianceAssessmentViewSet(viewsets.ModelViewSet):
    """Enhanced compliance assessment management"""
    queryset = ComplianceAssessment.objects.select_related(
        'framework', 'lead_assessor'
    ).prefetch_related('assessment_team', 'control_results').all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['framework', 'status', 'assessment_type', 'lead_assessor']
    search_fields = ['title', 'scope_description', 'executive_summary']
    ordering_fields = ['planned_start_date', 'compliance_percentage', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return ComplianceAssessmentListSerializer
        return ComplianceAssessmentDetailSerializer
    
    @action(detail=True, methods=['post'])
    def generate_ai_insights(self, request, pk=None):
        """Generate AI insights for specific assessment"""
        assessment = self.get_object()
        
        # Generate AI insights using the analytics service
        insights_data = AIComplianceAnalyticsService.generate_insights(assessment.framework)
        
        # Create AI insight records
        created_insights = []
        for insight_data in insights_data:
            insight = AIComplianceInsight.objects.create(
                framework=assessment.framework,
                insight_type=insight_data['insight_type'],
                title=insight_data['title'],
                description=insight_data['description'],
                confidence_score=insight_data['confidence_score'],
                priority_level=insight_data['priority_level'],
                recommendations=insight_data['recommendations'],
                potential_impact=f"Impact on {assessment.framework.name} compliance",
                estimated_effort="2-4 weeks"
            )
            insight.related_assessments.add(assessment)
            created_insights.append(insight)
        
        serializer = AIComplianceInsightSerializer(created_insights, many=True)
        return Response({
            'message': f'Generated {len(created_insights)} AI insights',
            'insights': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def compliance_overview(self, request):
        """Get overall compliance metrics across all frameworks"""
        
        # Calculate overall metrics
        total_assessments = self.get_queryset().count()
        active_assessments = self.get_queryset().filter(
            status__in=['IN_PROGRESS', 'UNDER_REVIEW']
        ).count()
        completed_assessments = self.get_queryset().filter(status='COMPLIANT').count()
        
        # Calculate average compliance score
        avg_compliance = self.get_queryset().filter(
            compliance_percentage__isnull=False
        ).aggregate(avg_score=Avg('compliance_percentage'))
        
        overall_score = avg_compliance['avg_score'] or Decimal('0.0')
        
        # Get framework-specific scores
        frameworks = RegulatoryFramework.objects.filter(is_active=True)
        framework_scores = []
        
        for framework in frameworks:
            score = AIComplianceAnalyticsService.calculate_predictive_scores(framework.framework_code)
            framework_scores.append({
                'framework_code': framework.framework_code,
                'framework_name': framework.name,
                'compliance_score': float(score),
                'total_controls': framework.controls.filter(is_active=True).count()
            })
        
        # Get AI insights summary
        ai_insights = AIComplianceInsight.objects.filter(is_active=True)
        total_insights = ai_insights.count()
        critical_insights = ai_insights.filter(priority_level='CRITICAL').count()
        high_priority_insights = ai_insights.filter(priority_level='HIGH').count()
        
        # Get recent activity
        recent_assessments = self.get_queryset().order_by('-updated_at')[:5]
        recent_insights = ai_insights.order_by('-created_at')[:5]
        
        metrics_data = {
            'overall_compliance_score': overall_score,
            'frameworks_count': frameworks.count(),
            'total_assessments': total_assessments,
            'active_assessments': active_assessments,
            'completed_assessments': completed_assessments,
            'framework_scores': framework_scores,
            'total_ai_insights': total_insights,
            'critical_insights': critical_insights,
            'high_priority_insights': high_priority_insights,
            'recent_assessments': recent_assessments,
            'recent_insights': recent_insights
        }
        
        serializer = ComplianceMetricsSerializer(metrics_data)
        return Response(serializer.data)

class AIComplianceInsightViewSet(viewsets.ModelViewSet):
    """AI compliance insight management"""
    queryset = AIComplianceInsight.objects.select_related('framework', 'acknowledged_by').filter(is_active=True)
    serializer_class = AIComplianceInsightSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['framework', 'insight_type', 'priority_level', 'is_acknowledged']
    search_fields = ['title', 'description', 'potential_impact']
    ordering_fields = ['priority_level', 'confidence_score', 'created_at']
    ordering = ['-priority_level', '-confidence_score', '-created_at']
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an AI insight"""
        insight = self.get_object()
        insight.is_acknowledged = True
        insight.acknowledged_by = request.user
        insight.acknowledged_date = timezone.now()
        insight.save()
        
        return Response({
            'message': 'Insight acknowledged successfully',
            'acknowledged_by': request.user.get_full_name(),
            'acknowledged_date': insight.acknowledged_date
        })
    
    @action(detail=False, methods=['post'])
    def generate_bulk_insights(self, request):
        """Generate AI insights for all active frameworks"""
        frameworks = RegulatoryFramework.objects.filter(is_active=True)
        all_insights = []
        
        for framework in frameworks:
            insights_data = AIComplianceAnalyticsService.generate_insights(framework)
            
            for insight_data in insights_data:
                insight = AIComplianceInsight.objects.create(
                    framework=framework,
                    insight_type=insight_data['insight_type'],
                    title=insight_data['title'],
                    description=insight_data['description'],
                    confidence_score=insight_data['confidence_score'],
                    priority_level=insight_data['priority_level'],
                    recommendations=insight_data['recommendations'],
                    potential_impact=f"Impact on {framework.name} compliance",
                    estimated_effort="Varies by recommendation"
                )
                all_insights.append(insight)
        
        serializer = AIComplianceInsightSerializer(all_insights, many=True)
        return Response({
            'message': f'Generated {len(all_insights)} AI insights across {frameworks.count()} frameworks',
            'insights': serializer.data
        })

# ============================================================================
# LEGACY/EXISTING VIEWSETS (Updated)
# ============================================================================

class SafetyIncidentViewSet(viewsets.ModelViewSet):
    """Safety incident CRUD operations"""
    queryset = SafetyIncident.objects.all()
    serializer_class = SafetyIncidentSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['incident_type', 'severity', 'is_resolved', 'reported_by']
    search_fields = ['incident_id', 'title', 'description', 'location']
    ordering_fields = ['incident_date', 'severity', 'created_at']
    ordering = ['-incident_date']

class ComplianceChecklistViewSet(viewsets.ModelViewSet):
    """Compliance checklist CRUD operations with regulatory framework integration"""
    queryset = ComplianceChecklist.objects.select_related('regulatory_framework', 'created_by').all()
    serializer_class = ComplianceChecklistSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['compliance_type', 'regulatory_framework', 'is_mandatory', 'is_active', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class ChecklistAssessmentViewSet(viewsets.ModelViewSet):
    """Checklist-based compliance assessment operations (legacy support)"""
    queryset = ChecklistAssessment.objects.select_related('checklist', 'assessed_by').all()
    serializer_class = ChecklistAssessmentSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['checklist', 'status', 'assessed_by']
    search_fields = ['assessed_location', 'notes']
    ordering_fields = ['assessment_date', 'compliance_score']
    ordering = ['-assessment_date']

class EnvironmentalMonitoringViewSet(viewsets.ModelViewSet):
    """Environmental monitoring CRUD operations"""
    queryset = EnvironmentalMonitoring.objects.all()
    serializer_class = EnvironmentalMonitoringSerializer
    permission_classes = [IsHRManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['monitoring_type', 'location', 'is_within_limits', 'recorded_by']
    search_fields = ['location', 'notes']
    ordering_fields = ['measurement_date', 'measured_value']
    ordering = ['-measurement_date']