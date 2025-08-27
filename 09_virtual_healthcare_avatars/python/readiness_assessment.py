#!/usr/bin/env python3
"""
Virtual Healthcare Avatar Readiness Assessment Tool
Evaluates organizational readiness for avatar implementation across multiple dimensions
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class AvatarReadinessAssessment:
    """Assess organizational readiness for virtual avatar deployment"""
    
    # Assessment dimensions and criteria
    ASSESSMENT_CRITERIA = {
        'technical_infrastructure': {
            'weight': 0.25,
            'criteria': [
                ('ehr_api_availability', 'EHR has accessible APIs', 3),
                ('integration_team', 'Dedicated integration team exists', 2),
                ('data_warehouse', 'Clinical data warehouse operational', 2),
                ('network_reliability', 'Network uptime >99.5%', 2),
                ('security_compliance', 'HIPAA-compliant infrastructure', 3),
                ('device_availability', 'Patient devices/kiosks available', 1)
            ]
        },
        'clinical_alignment': {
            'weight': 0.20,
            'criteria': [
                ('physician_buy_in', 'Physician champion identified', 3),
                ('nursing_support', 'Nursing leadership supportive', 3),
                ('clinical_protocols', 'Standardized protocols exist', 2),
                ('outcome_metrics', 'Clinical metrics tracked', 2),
                ('safety_committee', 'Clinical safety oversight established', 2)
            ]
        },
        'organizational_culture': {
            'weight': 0.20,
            'criteria': [
                ('innovation_history', 'Successful digital initiatives deployed', 2),
                ('change_management', 'Change management process exists', 2),
                ('pilot_culture', 'Culture supports pilots/experimentation', 3),
                ('patient_feedback', 'Patient feedback mechanisms active', 1),
                ('staff_training', 'Regular technology training provided', 2)
            ]
        },
        'financial_readiness': {
            'weight': 0.15,
            'criteria': [
                ('innovation_budget', 'Dedicated innovation budget exists', 3),
                ('roi_tracking', 'ROI measurement capabilities', 2),
                ('value_based_contracts', 'Value-based care contracts >30%', 2),
                ('cost_transparency', 'Cost per case tracking available', 1)
            ]
        },
        'use_case_fit': {
            'weight': 0.20,
            'criteria': [
                ('high_readmissions', 'Readmission rate >15%', 2),
                ('mental_health_gaps', 'Mental health access gaps identified', 2),
                ('medication_nonadherence', 'Medication adherence <70%', 2),
                ('volume_sufficient', 'Sufficient patient volume for ROI', 3),
                ('workflow_defined', 'Clear workflow integration points', 3)
            ]
        }
    }
    
    # Readiness thresholds
    READINESS_LEVELS = {
        'not_ready': (0, 40),
        'preparation_needed': (40, 60),
        'pilot_ready': (60, 75),
        'scale_ready': (75, 100)
    }
    
    def __init__(self):
        """Initialize assessment tool"""
        self.scores = {}
        self.recommendations = []
        
    def assess(self, responses: Dict[str, bool]) -> Dict:
        """
        Perform readiness assessment based on responses
        
        Args:
            responses: Dictionary mapping criteria IDs to boolean responses
            
        Returns:
            Assessment results with scores and recommendations
        """
        dimension_scores = {}
        
        for dimension, config in self.ASSESSMENT_CRITERIA.items():
            score = self._calculate_dimension_score(dimension, config, responses)
            dimension_scores[dimension] = score
            
        # Calculate weighted total score
        total_score = self._calculate_total_score(dimension_scores)
        
        # Determine readiness level
        readiness_level = self._determine_readiness_level(total_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            dimension_scores, responses
        )
        
        # Identify best use case
        best_use_case = self._recommend_use_case(responses)
        
        return {
            'total_score': total_score,
            'readiness_level': readiness_level,
            'dimension_scores': dimension_scores,
            'recommendations': recommendations,
            'best_use_case': best_use_case,
            'implementation_timeline': self._estimate_timeline(readiness_level),
            'critical_gaps': self._identify_critical_gaps(dimension_scores, responses)
        }
        
    def _calculate_dimension_score(self,
                                  dimension: str,
                                  config: Dict,
                                  responses: Dict) -> float:
        """Calculate score for a single dimension"""
        total_weight = 0
        earned_weight = 0
        
        for criteria_id, description, weight in config['criteria']:
            total_weight += weight
            if responses.get(criteria_id, False):
                earned_weight += weight
                
        return (earned_weight / total_weight * 100) if total_weight > 0 else 0
        
    def _calculate_total_score(self, dimension_scores: Dict) -> float:
        """Calculate weighted total score"""
        total = 0
        
        for dimension, score in dimension_scores.items():
            weight = self.ASSESSMENT_CRITERIA[dimension]['weight']
            total += score * weight
            
        return total
        
    def _determine_readiness_level(self, score: float) -> str:
        """Determine readiness level based on score"""
        for level, (min_score, max_score) in self.READINESS_LEVELS.items():
            if min_score <= score < max_score:
                return level
        return 'scale_ready'
        
    def _generate_recommendations(self,
                                 dimension_scores: Dict,
                                 responses: Dict) -> List[Dict]:
        """Generate specific recommendations based on gaps"""
        recommendations = []
        
        # Check each dimension for gaps
        for dimension, score in dimension_scores.items():
            if score < 60:  # Dimension needs improvement
                config = self.ASSESSMENT_CRITERIA[dimension]
                
                # Find missing critical items (weight >= 3)
                for criteria_id, description, weight in config['criteria']:
                    if weight >= 3 and not responses.get(criteria_id, False):
                        recommendations.append({
                            'priority': 'Critical',
                            'dimension': dimension,
                            'action': description,
                            'impact': f'Required for {dimension.replace("_", " ").title()}',
                            'timeline': '0-30 days'
                        })
                        
        # Add dimension-specific recommendations
        if dimension_scores.get('technical_infrastructure', 0) < 70:
            recommendations.append({
                'priority': 'High',
                'dimension': 'technical_infrastructure',
                'action': 'Conduct EHR integration assessment',
                'impact': 'Foundation for all avatar deployments',
                'timeline': '30-60 days'
            })
            
        if dimension_scores.get('clinical_alignment', 0) < 60:
            recommendations.append({
                'priority': 'High',
                'dimension': 'clinical_alignment',
                'action': 'Identify and engage clinical champions',
                'impact': 'Critical for adoption and success',
                'timeline': '0-30 days'
            })
            
        return sorted(recommendations, 
                     key=lambda x: 0 if x['priority'] == 'Critical' else 1)
        
    def _recommend_use_case(self, responses: Dict) -> Dict:
        """Recommend best use case based on organizational characteristics"""
        use_case_scores = {
            'mental_health': 0,
            'discharge_education': 0,
            'medication_adherence': 0
        }
        
        # Score mental health
        if responses.get('mental_health_gaps', False):
            use_case_scores['mental_health'] += 3
        if responses.get('clinical_protocols', False):
            use_case_scores['mental_health'] += 2
            
        # Score discharge education  
        if responses.get('high_readmissions', False):
            use_case_scores['discharge_education'] += 3
        if responses.get('value_based_contracts', False):
            use_case_scores['discharge_education'] += 2
        if responses.get('outcome_metrics', False):
            use_case_scores['discharge_education'] += 1
            
        # Score medication adherence
        if responses.get('medication_nonadherence', False):
            use_case_scores['medication_adherence'] += 3
        if responses.get('data_warehouse', False):
            use_case_scores['medication_adherence'] += 2
            
        # Find best match
        best_use_case = max(use_case_scores, key=use_case_scores.get)
        
        return {
            'recommended': best_use_case,
            'score': use_case_scores[best_use_case],
            'rationale': self._get_use_case_rationale(best_use_case, responses)
        }
        
    def _get_use_case_rationale(self, use_case: str, responses: Dict) -> str:
        """Generate rationale for use case recommendation"""
        rationales = {
            'mental_health': 'Strong evidence base (d=0.44), structured protocols, and identified access gaps make this ideal starting point.',
            'discharge_education': 'High readmission rates and value-based contracts create clear ROI opportunity with 30% reduction potential.',
            'medication_adherence': 'Poor adherence rates and data infrastructure support targeted interventions with 225% Year 1 ROI potential.'
        }
        return rationales.get(use_case, 'Evaluate specific organizational needs')
        
    def _estimate_timeline(self, readiness_level: str) -> Dict:
        """Estimate implementation timeline based on readiness"""
        timelines = {
            'not_ready': {
                'preparation': '6-9 months',
                'pilot': '12-15 months',
                'scale': '24-36 months'
            },
            'preparation_needed': {
                'preparation': '3-6 months',
                'pilot': '9-12 months',
                'scale': '18-24 months'
            },
            'pilot_ready': {
                'preparation': '1-3 months',
                'pilot': '4-6 months',
                'scale': '12-18 months'
            },
            'scale_ready': {
                'preparation': 'Complete',
                'pilot': '3-4 months',
                'scale': '6-12 months'
            }
        }
        return timelines.get(readiness_level, timelines['preparation_needed'])
        
    def _identify_critical_gaps(self,
                               dimension_scores: Dict,
                               responses: Dict) -> List[str]:
        """Identify critical gaps blocking implementation"""
        critical_gaps = []
        
        # Check for critical missing items
        critical_items = [
            ('ehr_api_availability', 'EHR API access'),
            ('security_compliance', 'HIPAA compliance'),
            ('physician_buy_in', 'Physician champion'),
            ('volume_sufficient', 'Sufficient patient volume'),
            ('workflow_defined', 'Defined workflow integration')
        ]
        
        for item_id, description in critical_items:
            if not responses.get(item_id, False):
                critical_gaps.append(description)
                
        return critical_gaps
        
    def generate_report(self, assessment_results: Dict) -> str:
        """Generate formatted assessment report"""
        report = []
        report.append("="*60)
        report.append("VIRTUAL HEALTHCARE AVATAR READINESS ASSESSMENT")
        report.append("="*60)
        report.append("")
        
        # Overall readiness
        score = assessment_results['total_score']
        level = assessment_results['readiness_level']
        report.append(f"Overall Readiness Score: {score:.1f}/100")
        report.append(f"Readiness Level: {level.replace('_', ' ').title()}")
        report.append("")
        
        # Dimension scores
        report.append("Dimension Scores:")
        report.append("-"*40)
        for dimension, score in assessment_results['dimension_scores'].items():
            dim_name = dimension.replace('_', ' ').title()
            report.append(f"  {dim_name:.<30} {score:.1f}%")
        report.append("")
        
        # Recommended use case
        use_case = assessment_results['best_use_case']
        report.append("Recommended Starting Point:")
        report.append("-"*40)
        report.append(f"  Use Case: {use_case['recommended'].replace('_', ' ').title()}")
        report.append(f"  Rationale: {use_case['rationale']}")
        report.append("")
        
        # Timeline
        timeline = assessment_results['implementation_timeline']
        report.append("Implementation Timeline:")
        report.append("-"*40)
        report.append(f"  Preparation Phase: {timeline['preparation']}")
        report.append(f"  Pilot Phase: {timeline['pilot']}")
        report.append(f"  Scale Phase: {timeline['scale']}")
        report.append("")
        
        # Critical gaps
        if assessment_results['critical_gaps']:
            report.append("Critical Gaps to Address:")
            report.append("-"*40)
            for gap in assessment_results['critical_gaps']:
                report.append(f"  ⚠️  {gap}")
            report.append("")
            
        # Top recommendations
        if assessment_results['recommendations']:
            report.append("Priority Recommendations:")
            report.append("-"*40)
            for i, rec in enumerate(assessment_results['recommendations'][:5], 1):
                report.append(f"  {i}. [{rec['priority']}] {rec['action']}")
                report.append(f"     Timeline: {rec['timeline']}")
            report.append("")
            
        return "\n".join(report)
        
    def create_visualization(self, assessment_results: Dict, output_file: str = None):
        """Create radar chart visualization of readiness"""
        dimensions = list(assessment_results['dimension_scores'].keys())
        scores = list(assessment_results['dimension_scores'].values())
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
        scores_plot = scores + [scores[0]]  # Complete the circle
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
        
        # Plot data
        ax.plot(angles, scores_plot, 'o-', linewidth=2, color='#2E86AB')
        ax.fill(angles, scores_plot, alpha=0.25, color='#2E86AB')
        
        # Set labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([d.replace('_', ' ').title() for d in dimensions])
        ax.set_ylim(0, 100)
        
        # Add readiness zones
        readiness_zones = [40, 60, 75, 100]
        zone_labels = ['Not Ready', 'Preparation', 'Pilot Ready', 'Scale Ready']
        colors = ['#FF6B6B', '#FFD93D', '#6BCF7F', '#4ECDC4']
        
        for i, (zone, label, color) in enumerate(zip(readiness_zones, zone_labels, colors)):
            if i == 0:
                ax.fill_between(angles, 0, zone, alpha=0.1, color=color, label=label)
            else:
                ax.fill_between(angles, readiness_zones[i-1], zone, alpha=0.1, color=color, label=label)
                
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # Title and legend
        plt.title(f'Avatar Readiness Assessment\nOverall Score: {assessment_results["total_score"]:.1f}/100',
                 size=16, weight='bold', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        else:
            plt.show()
            
        return fig


def interactive_assessment():
    """Run interactive command-line assessment"""
    print("\n" + "="*60)
    print("VIRTUAL HEALTHCARE AVATAR READINESS ASSESSMENT")
    print("="*60)
    print("\nAnswer Yes (y) or No (n) to each question:\n")
    
    assessment = AvatarReadinessAssessment()
    responses = {}
    
    # Collect responses for each criterion
    for dimension, config in assessment.ASSESSMENT_CRITERIA.items():
        print(f"\n{dimension.replace('_', ' ').upper()}")
        print("-"*40)
        
        for criteria_id, description, weight in config['criteria']:
            while True:
                response = input(f"{description}? (y/n): ").lower()
                if response in ['y', 'n']:
                    responses[criteria_id] = (response == 'y')
                    break
                print("Please enter 'y' for yes or 'n' for no")
                
    # Run assessment
    results = assessment.assess(responses)
    
    # Display report
    print("\n" + assessment.generate_report(results))
    
    # Offer to save results
    save = input("\nSave detailed results to file? (y/n): ").lower()
    if save == 'y':
        with open('avatar_readiness_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("Results saved to avatar_readiness_results.json")
        
    # Offer to create visualization
    visualize = input("Create visualization? (y/n): ").lower()
    if visualize == 'y':
        assessment.create_visualization(results, 'avatar_readiness_chart.png')
        print("Visualization saved to avatar_readiness_chart.png")
        

if __name__ == '__main__':
    interactive_assessment()