"""
Management command to initialize comprehensive regulatory compliance data
Creates initial data for all 5 regulatory frameworks with controls and sample assessments
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from apps.hse_compliance.models import (
    RegulatoryFramework, ComplianceControl, ComplianceAssessment, 
    ControlAssessmentResult, AIComplianceInsight
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize regulatory compliance data for Super Admin AI Hub'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing compliance data before initialization',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing compliance data...')
            RegulatoryFramework.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing compliance data cleared'))

        self.stdout.write('Initializing regulatory compliance frameworks...')
        
        # Get or create a default admin user for assignments
        admin_user, created = User.objects.get_or_create(
            username='compliance_admin',
            defaults={
                'email': 'compliance@rejlers.com',
                'first_name': 'Compliance',
                'last_name': 'Administrator',
                'is_staff': True
            }
        )

        # Create regulatory frameworks
        frameworks = self.create_regulatory_frameworks()
        
        # Create compliance controls for each framework
        self.create_compliance_controls(frameworks)
        
        # Create sample assessments
        self.create_sample_assessments(frameworks, admin_user)
        
        # Generate AI insights
        self.create_ai_insights(frameworks)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized compliance data for {len(frameworks)} regulatory frameworks'
            )
        )

    def create_regulatory_frameworks(self):
        """Create the 5 main regulatory frameworks"""
        frameworks_data = [
            {
                'framework_code': 'ISO_27001',
                'name': 'ISO 27001 Information Security Management',
                'description': 'International standard for information security management systems',
                'regulatory_body': 'International Organization for Standardization (ISO)',
                'version': '2022',
                'base_score_weight': Decimal('20.00'),
                'last_updated': date(2024, 1, 15),
                'next_review_date': date(2025, 1, 15)
            },
            {
                'framework_code': 'API_Q1_Q2',
                'name': 'API Q1/Q2 Oil & Gas Quality Standards',
                'description': 'American Petroleum Institute quality standards for oil and gas operations',
                'regulatory_body': 'American Petroleum Institute (API)',
                'version': '2024',
                'base_score_weight': Decimal('20.00'),
                'last_updated': date(2024, 3, 1),
                'next_review_date': date(2025, 3, 1)
            },
            {
                'framework_code': 'IEC_62443',
                'name': 'IEC 62443 Industrial Network Security',
                'description': 'International standard for industrial automation and control systems security',
                'regulatory_body': 'International Electrotechnical Commission (IEC)',
                'version': '2021',
                'base_score_weight': Decimal('20.00'),
                'last_updated': date(2024, 2, 10),
                'next_review_date': date(2025, 2, 10)
            },
            {
                'framework_code': 'NIST_SP_800_53',
                'name': 'NIST SP 800-53 Security and Privacy Controls',
                'description': 'Security and privacy controls for information systems and organizations',
                'regulatory_body': 'National Institute of Standards and Technology (NIST)',
                'version': 'Rev 5',
                'base_score_weight': Decimal('20.00'),
                'last_updated': date(2024, 4, 5),
                'next_review_date': date(2025, 4, 5)
            },
            {
                'framework_code': 'GDPR_UAE',
                'name': 'GDPR/UAE Data Protection Laws',
                'description': 'Combined GDPR and UAE data protection regulatory requirements',
                'regulatory_body': 'European Union / UAE Government',
                'version': '2024',
                'base_score_weight': Decimal('20.00'),
                'last_updated': date(2024, 5, 25),
                'next_review_date': date(2025, 5, 25)
            }
        ]

        frameworks = {}
        for framework_data in frameworks_data:
            framework, created = RegulatoryFramework.objects.get_or_create(
                framework_code=framework_data['framework_code'],
                defaults=framework_data
            )
            frameworks[framework_data['framework_code']] = framework
            
            if created:
                self.stdout.write(f'Created framework: {framework.name}')
            else:
                self.stdout.write(f'Framework already exists: {framework.name}')

        return frameworks

    def create_compliance_controls(self, frameworks):
        """Create compliance controls for each framework"""
        
        # ISO 27001 Controls
        iso_controls = [
            {'control_id': 'A.5.1.1', 'name': 'Information Security Policy', 'type': 'ADMINISTRATIVE', 'risk': 'HIGH'},
            {'control_id': 'A.6.1.1', 'name': 'Information Security Roles', 'type': 'ADMINISTRATIVE', 'risk': 'MEDIUM'},
            {'control_id': 'A.8.1.1', 'name': 'Inventory of Assets', 'type': 'TECHNICAL', 'risk': 'MEDIUM'},
            {'control_id': 'A.9.1.1', 'name': 'Access Control Policy', 'type': 'TECHNICAL', 'risk': 'HIGH'},
            {'control_id': 'A.12.1.1', 'name': 'Operating Procedures', 'type': 'PROCEDURAL', 'risk': 'MEDIUM'},
        ]
        
        # API Q1/Q2 Controls
        api_controls = [
            {'control_id': 'Q1-1.1', 'name': 'Quality Management System', 'type': 'ADMINISTRATIVE', 'risk': 'HIGH'},
            {'control_id': 'Q1-2.1', 'name': 'Document Control', 'type': 'PROCEDURAL', 'risk': 'MEDIUM'},
            {'control_id': 'Q2-1.1', 'name': 'Product Quality Control', 'type': 'TECHNICAL', 'risk': 'HIGH'},
            {'control_id': 'Q2-2.1', 'name': 'Inspection Procedures', 'type': 'PROCEDURAL', 'risk': 'MEDIUM'},
        ]
        
        # IEC 62443 Controls
        iec_controls = [
            {'control_id': 'SR-1.1', 'name': 'Identification and Authentication', 'type': 'TECHNICAL', 'risk': 'HIGH'},
            {'control_id': 'SR-2.1', 'name': 'Use Control', 'type': 'TECHNICAL', 'risk': 'HIGH'},
            {'control_id': 'SR-3.1', 'name': 'System Integrity', 'type': 'TECHNICAL', 'risk': 'CRITICAL'},
            {'control_id': 'SR-4.1', 'name': 'Data Confidentiality', 'type': 'TECHNICAL', 'risk': 'HIGH'},
        ]
        
        # NIST SP 800-53 Controls
        nist_controls = [
            {'control_id': 'AC-1', 'name': 'Access Control Policy', 'type': 'ADMINISTRATIVE', 'risk': 'HIGH'},
            {'control_id': 'AC-2', 'name': 'Account Management', 'type': 'TECHNICAL', 'risk': 'HIGH'},
            {'control_id': 'AC-3', 'name': 'Access Enforcement', 'type': 'TECHNICAL', 'risk': 'CRITICAL'},
            {'control_id': 'IA-1', 'name': 'Identification and Authentication Policy', 'type': 'ADMINISTRATIVE', 'risk': 'HIGH'},
        ]
        
        # GDPR/UAE Controls
        gdpr_controls = [
            {'control_id': 'Art-5', 'name': 'Principles of Processing', 'type': 'ADMINISTRATIVE', 'risk': 'HIGH'},
            {'control_id': 'Art-6', 'name': 'Lawfulness of Processing', 'type': 'ADMINISTRATIVE', 'risk': 'CRITICAL'},
            {'control_id': 'Art-17', 'name': 'Right to Erasure', 'type': 'TECHNICAL', 'risk': 'HIGH'},
            {'control_id': 'Art-25', 'name': 'Data Protection by Design', 'type': 'TECHNICAL', 'risk': 'HIGH'},
        ]
        
        all_controls = [
            ('ISO_27001', iso_controls),
            ('API_Q1_Q2', api_controls),
            ('IEC_62443', iec_controls),
            ('NIST_SP_800_53', nist_controls),
            ('GDPR_UAE', gdpr_controls)
        ]
        
        for framework_code, controls in all_controls:
            framework = frameworks[framework_code]
            
            for control_data in controls:
                control, created = ComplianceControl.objects.get_or_create(
                    framework=framework,
                    control_id=control_data['control_id'],
                    defaults={
                        'control_name': control_data['name'],
                        'description': f'Compliance control for {control_data["name"]} under {framework.name}',
                        'control_type': control_data['type'],
                        'risk_level': control_data['risk'],
                        'implementation_guidance': f'Implementation guidance for {control_data["name"]}',
                        'evidence_requirements': ['Documentation', 'Process Evidence', 'Technical Validation']
                    }
                )
                
                if created:
                    self.stdout.write(f'  Created control: {framework_code} - {control_data["control_id"]}')

    def create_sample_assessments(self, frameworks, admin_user):
        """Create sample compliance assessments"""
        
        for framework_code, framework in frameworks.items():
            assessment, created = ComplianceAssessment.objects.get_or_create(
                framework=framework,
                title=f'{framework.name} Annual Assessment 2024',
                defaults={
                    'assessment_type': 'INTERNAL_AUDIT',
                    'scope_description': f'Comprehensive annual assessment of {framework.name} compliance',
                    'planned_start_date': timezone.now() - timedelta(days=30),
                    'planned_end_date': timezone.now() + timedelta(days=7),
                    'actual_start_date': timezone.now() - timedelta(days=25),
                    'lead_assessor': admin_user,
                    'status': 'COMPLIANT',
                    'compliance_percentage': self.get_framework_score(framework_code),
                    'overall_score': self.get_framework_score(framework_code),
                    'executive_summary': f'Annual compliance assessment for {framework.name} completed successfully with high compliance ratings.',
                    'findings': [
                        {
                            'severity': 'Low',
                            'description': 'Minor documentation updates needed',
                            'recommendation': 'Update policy documentation within 30 days'
                        }
                    ],
                    'action_items': [
                        {
                            'item': 'Update compliance documentation',
                            'owner': admin_user.get_full_name(),
                            'due_date': (timezone.now() + timedelta(days=30)).isoformat(),
                            'priority': 'Medium'
                        }
                    ]
                }
            )
            
            if created:
                self.stdout.write(f'Created assessment: {assessment.title}')
                
                # Create control assessment results
                controls = framework.controls.all()[:5]  # First 5 controls
                for control in controls:
                    result, created = ControlAssessmentResult.objects.get_or_create(
                        assessment=assessment,
                        control=control,
                        defaults={
                            'compliance_status': 'COMPLIANT',
                            'score': Decimal('95.0'),
                            'evidence_provided': ['Policy Documentation', 'Process Records'],
                            'assessor_notes': f'Control {control.control_id} is fully compliant',
                            'assessed_by': admin_user
                        }
                    )

    def create_ai_insights(self, frameworks):
        """Create AI-generated compliance insights"""
        
        insights_data = [
            {
                'framework_code': 'ISO_27001',
                'insight_type': 'RISK_PREDICTION',
                'title': 'Access Control Enhancement Needed',
                'description': 'AI analysis indicates potential vulnerability in user access provisioning processes',
                'confidence': Decimal('89.5'),
                'priority': 'HIGH'
            },
            {
                'framework_code': 'GDPR_UAE',
                'insight_type': 'POLICY_RECOMMENDATION',
                'title': 'Data Retention Policy Update Required',
                'description': 'Automated analysis suggests data retention schedules need updating for Article 17 compliance',
                'confidence': Decimal('92.3'),
                'priority': 'MEDIUM'
            },
            {
                'framework_code': 'IEC_62443',
                'insight_type': 'COMPLIANCE_TREND',
                'title': 'Industrial Security Improvement Trend',
                'description': 'Network segmentation compliance has improved by 15% over the last quarter',
                'confidence': Decimal('94.1'),
                'priority': 'LOW'
            },
            {
                'framework_code': 'NIST_SP_800_53',
                'insight_type': 'AUDIT_PREPARATION',
                'title': 'Quarterly Audit Readiness Status',
                'description': 'All NIST controls are audit-ready with 99.5% compliance rate',
                'confidence': Decimal('97.8'),
                'priority': 'LOW'
            },
            {
                'framework_code': 'API_Q1_Q2',
                'insight_type': 'REMEDIATION_SUGGESTION',
                'title': 'Quality Process Optimization Opportunity',
                'description': 'AI suggests workflow automation for Q2 inspection procedures to improve efficiency',
                'confidence': Decimal('88.2'),
                'priority': 'MEDIUM'
            }
        ]
        
        for insight_data in insights_data:
            framework = frameworks[insight_data['framework_code']]
            
            insight, created = AIComplianceInsight.objects.get_or_create(
                framework=framework,
                title=insight_data['title'],
                defaults={
                    'insight_type': insight_data['insight_type'],
                    'description': insight_data['description'],
                    'confidence_score': insight_data['confidence'],
                    'priority_level': insight_data['priority'],
                    'recommendations': [
                        'Review current implementation',
                        'Implement suggested improvements',
                        'Monitor compliance metrics'
                    ],
                    'suggested_actions': [
                        'Schedule review meeting',
                        'Update documentation',
                        'Validate changes'
                    ],
                    'potential_impact': f'Improved compliance for {framework.name}',
                    'estimated_effort': '2-4 weeks'
                }
            )
            
            if created:
                self.stdout.write(f'Created AI insight: {insight.title}')

    def get_framework_score(self, framework_code):
        """Get predefined compliance scores for frameworks"""
        scores = {
            'ISO_27001': Decimal('97.3'),
            'API_Q1_Q2': Decimal('99.1'),
            'IEC_62443': Decimal('95.8'),
            'NIST_SP_800_53': Decimal('99.5'),
            'GDPR_UAE': Decimal('98.9'),
        }
        return scores.get(framework_code, Decimal('95.0'))