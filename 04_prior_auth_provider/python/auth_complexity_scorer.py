#!/usr/bin/env python3
"""
Prior Authorization Complexity Scorer
Purpose: Proactively identify high-risk authorization requests
Based on verified industry data from:
- Centers for Medicare & Medicaid Services (2023): Medicare Advantage denial rates
- American Medical Association (2024): Prior authorization survey data
- Council for Affordable Quality Healthcare (2023): CAQH Index
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, List, Optional

class AuthorizationComplexityScorer:
    """Score authorization requests to predict denial risk"""
    
    def __init__(self):
        # High-denial payers based on CMS Medicare Advantage Data 2023
        # Source: Centers for Medicare & Medicaid Services (2023)
        self.high_denial_payers = {
            'Centene': 13.6,
            'CVS/Aetna': 12.1,
            'UnitedHealth': 10.8,
            'Anthem': 8.7
        }
        
        # Low-denial payers for comparison
        # Source: CMS Medicare Advantage Data 2023
        self.low_denial_payers = {
            'Humana': 3.5,
            'Kaiser': 4.2,
            'BCBS': 5.1
        }
        
    def calculate_complexity_score(self, auth_request: Dict) -> Tuple[int, str, Dict]:
        """
        Calculate risk score for prior authorization denial
        
        Args:
            auth_request: Dictionary containing authorization details
            
        Returns:
            Tuple of (score, risk_level, risk_factors)
        """
        score = 0
        risk_factors = []
        
        # 1. Payer History (Most important factor)
        payer_name = auth_request.get('payer_name', '')
        if payer_name in self.high_denial_payers:
            score += 3
            risk_factors.append(f"High-denial payer ({self.high_denial_payers[payer_name]}% rate)")
        elif payer_name not in self.low_denial_payers and payer_name:
            score += 1
            risk_factors.append("Unknown payer denial rate")
            
        # 2. Procedure Cost
        estimated_cost = auth_request.get('estimated_cost', 0)
        if estimated_cost > 10000:
            score += 3
            risk_factors.append(f"Very high cost procedure (${estimated_cost:,.2f})")
        elif estimated_cost > 5000:
            score += 2
            risk_factors.append(f"High cost procedure (${estimated_cost:,.2f})")
        elif estimated_cost > 2500:
            score += 1
            risk_factors.append(f"Moderate cost procedure (${estimated_cost:,.2f})")
            
        # 3. Service Type
        service_type = auth_request.get('service_type', '').lower()
        if service_type == 'surgical':
            score += 2
            risk_factors.append("Surgical procedure")
        elif service_type in ['genetic_testing', 'experimental']:
            score += 3
            risk_factors.append("High-scrutiny service type")
            
        # 4. Clinical Urgency
        urgency = auth_request.get('urgency', '').lower()
        if urgency == 'urgent':
            score += 1
            risk_factors.append("Urgent request (documentation risk)")
        elif urgency == 'emergent':
            score += 2
            risk_factors.append("Emergent request (high documentation risk)")
            
        # 5. Patient History
        if auth_request.get('patient_recent_denial', False):
            score += 2
            risk_factors.append("Patient has recent denial history")
            
        # 6. Documentation Completeness
        doc_score = auth_request.get('documentation_score', 100)
        if doc_score < 70:
            score += 2
            risk_factors.append(f"Incomplete documentation ({doc_score}% complete)")
        elif doc_score < 85:
            score += 1
            risk_factors.append(f"Documentation gaps ({doc_score}% complete)")
            
        # 7. Provider History
        if auth_request.get('provider_denial_rate', 0) > 15:
            score += 1
            risk_factors.append("Provider has high denial rate")
            
        # Determine risk level
        if score <= 3:
            risk_level = 'LOW'
        elif score <= 6:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'HIGH'
            
        return score, risk_level, {'factors': risk_factors, 'total_score': score}
    
    def batch_score_requests(self, requests_df: pd.DataFrame) -> pd.DataFrame:
        """Score multiple authorization requests"""
        results = []
        
        for idx, row in requests_df.iterrows():
            score, risk_level, risk_details = self.calculate_complexity_score(row.to_dict())
            results.append({
                'request_id': row.get('request_id', idx),
                'complexity_score': score,
                'risk_level': risk_level,
                'risk_factors': '; '.join(risk_details['factors'])
            })
            
        return pd.DataFrame(results)
    
    def get_recommendations(self, score: int, risk_level: str) -> List[str]:
        """Get workflow recommendations based on risk level"""
        recommendations = []
        
        if risk_level == 'LOW':
            recommendations.append("Process via standard automated workflow")
            recommendations.append("No additional review required")
            
        elif risk_level == 'MEDIUM':
            recommendations.append("Route to senior specialist for review")
            recommendations.append("Verify documentation completeness")
            recommendations.append("Consider proactive payer outreach")
            
        else:  # HIGH
            recommendations.append("Immediate P2P Gatekeeper review required")
            recommendations.append("Assemble complete clinical documentation packet")
            recommendations.append("Prepare physician for potential peer-to-peer")
            recommendations.append("Consider pre-submission payer discussion")
            
        return recommendations


# Example usage
if __name__ == "__main__":
    # Initialize scorer
    scorer = AuthorizationComplexityScorer()
    
    # Example 1: Single request scoring
    print("=== Example 1: High-Risk Surgical Request ===")
    auth_request = {
        'payer_name': 'Centene',
        'estimated_cost': 85000,
        'service_type': 'surgical',
        'urgency': 'routine',
        'patient_recent_denial': True,
        'documentation_score': 95,
        'cpt_code': '22633',  # Lumbar fusion
        'provider_denial_rate': 8
    }
    
    score, risk, details = scorer.calculate_complexity_score(auth_request)
    print(f"Complexity Score: {score}")
    print(f"Risk Level: {risk}")
    print(f"Risk Factors: {details['factors']}")
    print(f"Recommendations: {scorer.get_recommendations(score, risk)}")
    
    # Example 2: Batch scoring
    print("\n=== Example 2: Batch Scoring ===")
    sample_requests = pd.DataFrame([
        {
            'request_id': 'PA-001',
            'payer_name': 'Humana',
            'estimated_cost': 1200,
            'service_type': 'diagnostic',
            'urgency': 'routine',
            'patient_recent_denial': False
        },
        {
            'request_id': 'PA-002',
            'payer_name': 'Aetna',
            'estimated_cost': 15000,
            'service_type': 'surgical',
            'urgency': 'urgent',
            'patient_recent_denial': True
        },
        {
            'request_id': 'PA-003',
            'payer_name': 'Kaiser',
            'estimated_cost': 3500,
            'service_type': 'therapy',
            'urgency': 'routine',
            'patient_recent_denial': False
        }
    ])
    
    results = scorer.batch_score_requests(sample_requests)
    print(results.to_string(index=False))