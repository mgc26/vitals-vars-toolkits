"""
Compute-to-Data Function: 30-Day Readmission Risk Scoring
Deploys directly to data source - no patient data movement required
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def calculate_readmission_risk(patient_id: str, 
                             compute_context: Dict) -> Dict:
    """
    Calculate 30-day readmission risk score without moving patient data.
    
    This function executes AT the data source. Only the risk score is returned,
    not the underlying patient data.
    
    Args:
        patient_id: Patient identifier
        compute_context: Execution context with data access methods
        
    Returns:
        Dictionary with patient_id and risk_score only
    """
    
    # Local data access - these queries execute at the source
    db = compute_context['local_database']
    
    # Risk factors (simplified for demo)
    risk_score = 0.0
    risk_factors = []
    
    # 1. Previous admissions
    admissions = db.query(f"""
        SELECT admission_date, discharge_date, primary_diagnosis
        FROM admissions 
        WHERE patient_id = '{patient_id}'
        AND discharge_date >= CURRENT_DATE - INTERVAL '180 days'
        ORDER BY discharge_date DESC
    """)
    
    if len(admissions) > 2:
        risk_score += 0.3
        risk_factors.append("multiple_recent_admissions")
    
    # 2. Chronic conditions
    conditions = db.query(f"""
        SELECT diagnosis_code 
        FROM patient_conditions
        WHERE patient_id = '{patient_id}'
        AND diagnosis_code IN ('E11', 'I50', 'J44', 'N18')
    """)
    
    chronic_count = len(conditions)
    if chronic_count >= 3:
        risk_score += 0.25
        risk_factors.append("multiple_chronic_conditions")
    
    # 3. Medication complexity
    medications = db.query(f"""
        SELECT COUNT(DISTINCT medication_name) as med_count
        FROM active_medications
        WHERE patient_id = '{patient_id}'
    """)
    
    if medications[0]['med_count'] > 10:
        risk_score += 0.2
        risk_factors.append("polypharmacy")
    
    # 4. Social determinants (if available)
    social_factors = db.query(f"""
        SELECT lives_alone, has_transportation
        FROM patient_social_factors
        WHERE patient_id = '{patient_id}'
    """)
    
    if social_factors and social_factors[0]['lives_alone']:
        risk_score += 0.15
        risk_factors.append("lives_alone")
        
    # Cap risk score at 1.0
    risk_score = min(risk_score, 1.0)
    
    # Return ONLY the score - no PHI leaves the source system
    return {
        "patient_id": patient_id,
        "risk_score": round(risk_score, 3),
        "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
        "factors_count": len(risk_factors),
        "computed_at": datetime.utcnow().isoformat()
    }


def batch_calculate_risk(patient_ids: List[str], 
                        compute_context: Dict) -> Dict:
    """
    Calculate risk scores for multiple patients.
    Returns only aggregate statistics - no individual patient data.
    """
    
    results = []
    for patient_id in patient_ids:
        try:
            risk_result = calculate_readmission_risk(patient_id, compute_context)
            results.append(risk_result)
        except Exception as e:
            # Log error locally, don't expose patient info
            compute_context['logger'].error(f"Error computing risk: {str(e)}")
    
    # Return only aggregate metrics
    high_risk_count = sum(1 for r in results if r['risk_level'] == 'high')
    medium_risk_count = sum(1 for r in results if r['risk_level'] == 'medium')
    low_risk_count = sum(1 for r in results if r['risk_level'] == 'low')
    
    return {
        "total_patients": len(patient_ids),
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
        "high_risk_percentage": round(high_risk_count / len(patient_ids) * 100, 1),
        "computation_timestamp": datetime.utcnow().isoformat()
    }


# Deployment configuration
DEPLOYMENT_CONFIG = {
    "function_name": "readmission_risk_scorer",
    "version": "1.0.0",
    "runtime": "python3.9",
    "memory_limit": "256MB",
    "timeout_seconds": 30,
    "required_permissions": [
        "read:admissions",
        "read:patient_conditions", 
        "read:active_medications",
        "read:patient_social_factors"
    ],
    "output_schema": {
        "type": "object",
        "properties": {
            "patient_id": {"type": "string"},
            "risk_score": {"type": "number", "minimum": 0, "maximum": 1},
            "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
            "factors_count": {"type": "integer"},
            "computed_at": {"type": "string", "format": "date-time"}
        },
        "required": ["patient_id", "risk_score", "risk_level"]
    }
}