"""
Compute-to-Data ROI Calculator
Calculate the financial impact of switching from traditional ETL to compute-to-data
"""

from datetime import datetime
from typing import Dict, List, Optional
import json


class ComputeToDataROICalculator:
    """Calculate ROI for compute-to-data implementations in healthcare"""
    
    def __init__(self):
        # Industry average costs (adjustable)
        self.defaults = {
            "developer_hourly_rate": 150,
            "infrastructure_cost_per_gb": 0.10,
            "security_incident_avg_cost": 50000,
            "downtime_cost_per_hour": 5000,
            "data_engineer_hourly_rate": 125
        }
    
    def calculate_traditional_costs(self, 
                                  integration_weeks: int = 8,
                                  data_volume_gb_daily: float = 50,
                                  team_size: int = 3,
                                  monthly_infrastructure: float = 5000) -> Dict:
        """Calculate costs for traditional ETL approach"""
        
        # Development costs
        dev_hours = integration_weeks * 40 * team_size
        dev_cost = dev_hours * self.defaults["developer_hourly_rate"]
        
        # Annual operational costs
        annual_data_movement = data_volume_gb_daily * 365 * self.defaults["infrastructure_cost_per_gb"]
        annual_infrastructure = monthly_infrastructure * 12
        
        # Risk costs (estimated based on industry averages)
        security_risk_cost = self.defaults["security_incident_avg_cost"] * 0.2  # Estimated annual risk
        downtime_cost = self.defaults["downtime_cost_per_hour"] * 24  # Estimated downtime/year
        
        total_first_year = dev_cost + annual_data_movement + annual_infrastructure + security_risk_cost + downtime_cost
        annual_ongoing = annual_data_movement + annual_infrastructure + security_risk_cost + downtime_cost
        
        return {
            "development_cost": dev_cost,
            "development_time_weeks": integration_weeks,
            "annual_data_movement_cost": annual_data_movement,
            "annual_infrastructure_cost": annual_infrastructure,
            "annual_risk_cost": security_risk_cost + downtime_cost,
            "total_first_year_cost": total_first_year,
            "annual_ongoing_cost": annual_ongoing
        }
    
    def calculate_compute_to_data_costs(self,
                                      pilot_weeks: int = 4,
                                      deployment_days_per_source: int = 2,
                                      monthly_compute_cost: float = 500) -> Dict:
        """Calculate costs for compute-to-data approach"""
        
        # Pilot development
        pilot_hours = pilot_weeks * 40 * 2  # Smaller team
        pilot_cost = pilot_hours * self.defaults["developer_hourly_rate"]
        
        # Deployment costs (much faster)
        deployment_hours = deployment_days_per_source * 8
        deployment_cost = deployment_hours * self.defaults["developer_hourly_rate"]
        
        # Annual operational costs (much lower)
        annual_compute = monthly_compute_cost * 12
        security_risk_cost = self.defaults["security_incident_avg_cost"] * 0.02  # Significantly reduced risk
        downtime_cost = self.defaults["downtime_cost_per_hour"] * 2  # Minimal downtime
        
        total_first_year = pilot_cost + deployment_cost + annual_compute + security_risk_cost + downtime_cost
        annual_ongoing = annual_compute + security_risk_cost + downtime_cost
        
        return {
            "pilot_cost": pilot_cost,
            "deployment_cost": deployment_cost,
            "pilot_time_weeks": pilot_weeks,
            "deployment_time_days": deployment_days_per_source,
            "annual_compute_cost": annual_compute,
            "annual_risk_cost": security_risk_cost + downtime_cost,
            "total_first_year_cost": total_first_year,
            "annual_ongoing_cost": annual_ongoing
        }
    
    def calculate_roi(self, traditional_costs: Dict, compute_costs: Dict, years: int = 3) -> Dict:
        """Calculate ROI metrics comparing traditional to compute-to-data"""
        
        # First year savings
        first_year_savings = traditional_costs["total_first_year_cost"] - compute_costs["total_first_year_cost"]
        
        # Multi-year calculations
        traditional_total = traditional_costs["total_first_year_cost"] + (traditional_costs["annual_ongoing_cost"] * (years - 1))
        compute_total = compute_costs["total_first_year_cost"] + (compute_costs["annual_ongoing_cost"] * (years - 1))
        total_savings = traditional_total - compute_total
        
        # ROI calculation
        investment = compute_costs["pilot_cost"]
        roi_percentage = (total_savings / investment) * 100 if investment > 0 else 0
        
        # Payback period (months)
        monthly_savings = (traditional_costs["annual_ongoing_cost"] - compute_costs["annual_ongoing_cost"]) / 12
        payback_months = investment / monthly_savings if monthly_savings > 0 else float('inf')
        
        # Time to value
        time_to_value_weeks = compute_costs["pilot_time_weeks"] + (compute_costs["deployment_time_days"] / 5)
        time_to_value_reduction = 1 - (time_to_value_weeks / traditional_costs["development_time_weeks"])
        
        return {
            "first_year_savings": first_year_savings,
            f"{years}_year_savings": total_savings,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
            "time_to_value_reduction_percent": time_to_value_reduction * 100,
            "cost_reduction_percent": (1 - compute_total / traditional_total) * 100
        }
    
    def generate_report(self, 
                       integration_weeks: int = 8,
                       data_volume_gb_daily: float = 50,
                       num_data_sources: int = 5) -> str:
        """Generate a complete ROI report"""
        
        # Calculate costs
        traditional = self.calculate_traditional_costs(
            integration_weeks=integration_weeks,
            data_volume_gb_daily=data_volume_gb_daily
        )
        
        compute = self.calculate_compute_to_data_costs()
        
        # Calculate ROI
        roi = self.calculate_roi(traditional, compute)
        
        # Format report
        report = f"""
# Compute-to-Data ROI Analysis
Generated: {datetime.now().strftime("%Y-%m-%d")}

## Scenario
- Current integration timeline: {integration_weeks} weeks per source
- Daily data volume: {data_volume_gb_daily} GB
- Number of data sources: {num_data_sources}

## Traditional ETL Approach
- Development cost: ${traditional['development_cost']:,.0f}
- Time to deploy: {traditional['development_time_weeks']} weeks
- Annual operational cost: ${traditional['annual_ongoing_cost']:,.0f}
- First year total: ${traditional['total_first_year_cost']:,.0f}

## Compute-to-Data Approach  
- Pilot cost: ${compute['pilot_cost']:,.0f}
- Time to first deployment: {compute['pilot_time_weeks']} weeks
- Additional sources: {compute['deployment_time_days']} days each
- Annual operational cost: ${compute['annual_ongoing_cost']:,.0f}
- First year total: ${compute['total_first_year_cost']:,.0f}

## ROI Summary
- **First year savings: ${roi['first_year_savings']:,.0f}**
- **3-year savings: ${roi['3_year_savings']:,.0f}**
- **ROI: {roi['roi_percentage']:.0f}%**
- **Payback period: {roi['payback_months']:.1f} months**
- **Time-to-value improvement: {roi['time_to_value_reduction_percent']:.0f}% faster**
- **Cost reduction: {roi['cost_reduction_percent']:.0f}%**

## Additional Benefits (Not Quantified)
- ✅ Significant reduction in security incidents
- ✅ Real-time vs batch processing
- ✅ Simplified compliance audits
- ✅ Reduced vendor lock-in
- ✅ Improved data governance

## Recommendation
With a {roi['roi_percentage']:.0f}% ROI and {roi['payback_months']:.1f} month payback period,
compute-to-data represents a compelling investment for healthcare data integration.
"""
        
        return report


# Example usage
if __name__ == "__main__":
    calculator = ComputeToDataROICalculator()
    
    # Generate report for typical hospital scenario
    report = calculator.generate_report(
        integration_weeks=8,
        data_volume_gb_daily=50,
        num_data_sources=5
    )
    
    print(report)
    
    # Save detailed calculations
    traditional = calculator.calculate_traditional_costs()
    compute = calculator.calculate_compute_to_data_costs()
    roi = calculator.calculate_roi(traditional, compute)
    
    with open("roi_calculations.json", "w") as f:
        json.dump({
            "traditional_approach": traditional,
            "compute_to_data_approach": compute,
            "roi_metrics": roi,
            "generated_at": datetime.now().isoformat()
        }, f, indent=2)