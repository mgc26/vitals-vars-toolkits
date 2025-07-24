#!/usr/bin/env python3
"""
Prior Authorization ROI Calculator
Based on verified industry data from AMA, CMS, and HFMA research
Calculates the financial impact of PA process improvements
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class PriorAuthROICalculator:
    """Calculate ROI for prior authorization improvements"""
    
    def __init__(self):
        # Constants from verified sources
        self.APPEAL_SUCCESS_RATE = 0.817  # CMS Medicare Advantage Data 2023
        self.CURRENT_APPEAL_RATE = 0.117  # CMS Medicare Advantage Data 2023
        self.COST_PER_REWORK_LOW = 25     # HFMA estimate low end
        self.COST_PER_REWORK_HIGH = 118   # HFMA estimate high end
        self.COST_PER_REWORK_MID = 70     # HFMA estimate midpoint
        self.PHYSICIAN_HOURS_WEEKLY = 12.5 # AMA 2024 (average of 12-13 hours)
        self.PHYSICIAN_HOURLY_RATE = 400  # Industry estimate
        
    def calculate_administrative_surrender(self, hospital_metrics: Dict) -> Dict:
        """
        Calculate the administrative surrender amount
        This is an illustrative calculation based on industry averages
        
        Args:
            hospital_metrics: Dictionary with keys:
                - gross_revenue: Annual gross revenue
                - denial_rate: Overall denial rate (default 8%)
                - pa_denial_percentage: % of denials that are PA-related (default 25%)
                
        Returns:
            Dictionary with surrender calculations
        """
        # Default values based on industry averages
        gross_revenue = hospital_metrics.get('gross_revenue', 450_000_000)
        denial_rate = hospital_metrics.get('denial_rate', 0.08)
        pa_denial_percentage = hospital_metrics.get('pa_denial_percentage', 0.25)
        
        # Calculate denials
        total_denials = gross_revenue * denial_rate
        pa_denials = total_denials * pa_denial_percentage
        
        # Calculate appeals vs surrender
        amount_appealed = pa_denials * self.CURRENT_APPEAL_RATE
        amount_surrendered = pa_denials * (1 - self.CURRENT_APPEAL_RATE)
        
        # Calculate recovery
        current_recovery = amount_appealed * self.APPEAL_SUCCESS_RATE
        
        return {
            'gross_revenue': gross_revenue,
            'total_denials': total_denials,
            'pa_related_denials': pa_denials,
            'amount_appealed': amount_appealed,
            'amount_surrendered': amount_surrendered,
            'current_recovery': current_recovery,
            'surrender_percentage': (1 - self.CURRENT_APPEAL_RATE) * 100
        }
    
    def calculate_improvement_roi(self, 
                                 hospital_metrics: Dict,
                                 improvement_targets: Dict) -> Dict:
        """
        Calculate ROI from PA process improvements
        
        Args:
            hospital_metrics: Same as calculate_administrative_surrender
            improvement_targets: Dictionary with keys:
                - target_appeal_rate: New appeal rate target (e.g., 0.50)
                - denial_reduction: Expected reduction in denials (e.g., 0.30)
                - p2p_gatekeeper_salary: Annual salary for new role
                - technology_investment: One-time tech costs
                - training_costs: One-time training investment
                
        Returns:
            Dictionary with comprehensive ROI calculations
        """
        # Get baseline surrender calculations
        baseline = self.calculate_administrative_surrender(hospital_metrics)
        
        # Get improvement targets
        target_appeal_rate = improvement_targets.get('target_appeal_rate', 0.50)
        denial_reduction = improvement_targets.get('denial_reduction', 0.30)
        p2p_salary = improvement_targets.get('p2p_gatekeeper_salary', 95_000)
        tech_cost = improvement_targets.get('technology_investment', 50_000)
        training = improvement_targets.get('training_costs', 25_000)
        
        # Revenue recovery from increased appeals
        additional_appeals_value = (baseline['pa_related_denials'] * 
                                  (target_appeal_rate - self.CURRENT_APPEAL_RATE))
        additional_recovery = additional_appeals_value * self.APPEAL_SUCCESS_RATE
        
        # Cost savings from denial prevention
        monthly_denials = baseline['pa_related_denials'] / 12 / baseline['gross_revenue'] * 1_000_000
        denials_prevented_monthly = monthly_denials * denial_reduction
        rework_savings_annual = denials_prevented_monthly * 12 * self.COST_PER_REWORK_MID
        
        # Physician time savings
        num_physicians = hospital_metrics.get('num_physicians', 100)
        hours_saved_per_physician = self.PHYSICIAN_HOURS_WEEKLY * 0.5 * 52  # 50% reduction
        physician_time_value = hours_saved_per_physician * num_physicians * self.PHYSICIAN_HOURLY_RATE
        
        # Total benefits and costs
        total_annual_benefit = additional_recovery + rework_savings_annual
        total_investment = p2p_salary + tech_cost + training
        first_year_costs = p2p_salary + tech_cost + training
        ongoing_costs = p2p_salary
        
        # ROI calculations
        first_year_roi = ((total_annual_benefit - first_year_costs) / first_year_costs) * 100
        ongoing_roi = ((total_annual_benefit - ongoing_costs) / ongoing_costs) * 100
        payback_months = first_year_costs / (total_annual_benefit / 12)
        
        return {
            'baseline_surrender': baseline['amount_surrendered'],
            'additional_recovery': additional_recovery,
            'rework_savings': rework_savings_annual,
            'physician_time_value': physician_time_value,
            'total_annual_benefit': total_annual_benefit,
            'total_investment': total_investment,
            'first_year_roi_pct': first_year_roi,
            'ongoing_roi_pct': ongoing_roi,
            'payback_months': payback_months,
            'net_benefit_year_1': total_annual_benefit - first_year_costs,
            'denials_prevented_monthly': denials_prevented_monthly
        }
    
    def generate_roi_report(self, hospital_metrics: Dict, improvement_targets: Dict) -> str:
        """Generate a formatted ROI report"""
        
        baseline = self.calculate_administrative_surrender(hospital_metrics)
        roi = self.calculate_improvement_roi(hospital_metrics, improvement_targets)
        
        report = f"""
Prior Authorization ROI Analysis Report
=====================================

CURRENT STATE (Administrative Surrender)
---------------------------------------
Gross Revenue: ${baseline['gross_revenue']:,.0f}
Total Denials: ${baseline['total_denials']:,.0f}
PA-Related Denials: ${baseline['pa_related_denials']:,.0f}
Currently Appealed: ${baseline['amount_appealed']:,.0f} ({self.CURRENT_APPEAL_RATE*100:.1f}%)
Currently Surrendered: ${baseline['amount_surrendered']:,.0f} ({baseline['surrender_percentage']:.1f}%)

IMPROVEMENT OPPORTUNITY
----------------------
Additional Revenue Recovery: ${roi['additional_recovery']:,.0f}
Rework Cost Savings: ${roi['rework_savings']:,.0f}
Physician Time Value: ${roi['physician_time_value']:,.0f}
Total Annual Benefit: ${roi['total_annual_benefit']:,.0f}

INVESTMENT REQUIRED
------------------
P2P Gatekeeper Salary: ${improvement_targets.get('p2p_gatekeeper_salary', 95000):,.0f}
Technology Investment: ${improvement_targets.get('technology_investment', 50000):,.0f}
Training Costs: ${improvement_targets.get('training_costs', 25000):,.0f}
Total Investment: ${roi['total_investment']:,.0f}

ROI SUMMARY
-----------
First Year ROI: {roi['first_year_roi_pct']:.0f}%
Ongoing Annual ROI: {roi['ongoing_roi_pct']:.0f}%
Payback Period: {roi['payback_months']:.1f} months
Net Benefit Year 1: ${roi['net_benefit_year_1']:,.0f}

OPERATIONAL IMPACT
-----------------
Denials Prevented Monthly: {roi['denials_prevented_monthly']:.0f}
Physician Hours Saved Annually: {hospital_metrics.get('num_physicians', 100) * self.PHYSICIAN_HOURS_WEEKLY * 0.5 * 52:,.0f}

DATA SOURCES
-----------
Appeal Success Rate: CMS Medicare Advantage Data 2023 (81.7%)
Current Appeal Rate: CMS Medicare Advantage Data 2023 (11.7%)
Rework Costs: HFMA Estimates ($25-$118, using $70 midpoint)
Physician Time: AMA 2024 Survey (12-13 hours/week)

Note: The administrative surrender calculation is illustrative based on 
industry averages. Your actual results will vary based on payer mix, 
service lines, and current operational efficiency.
"""
        return report


# Example usage
if __name__ == "__main__":
    calculator = PriorAuthROICalculator()
    
    # Define hospital characteristics
    hospital_metrics = {
        'gross_revenue': 450_000_000,  # $450M gross revenue
        'denial_rate': 0.08,           # 8% overall denial rate
        'pa_denial_percentage': 0.25,   # 25% of denials are PA-related
        'num_physicians': 100           # 100 physicians on staff
    }
    
    # Define improvement targets
    improvement_targets = {
        'target_appeal_rate': 0.50,     # Increase appeals to 50%
        'denial_reduction': 0.30,       # Reduce denials by 30%
        'p2p_gatekeeper_salary': 95_000,
        'technology_investment': 50_000,
        'training_costs': 25_000
    }
    
    # Generate report
    report = calculator.generate_roi_report(hospital_metrics, improvement_targets)
    print(report)
    
    # You can also get raw calculations
    roi_data = calculator.calculate_improvement_roi(hospital_metrics, improvement_targets)
    print(f"\nQuick Summary: ${roi_data['net_benefit_year_1']:,.0f} net benefit in Year 1")