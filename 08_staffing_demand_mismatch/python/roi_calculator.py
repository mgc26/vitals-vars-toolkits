#!/usr/bin/env python3
"""
Staffing Variance ROI Calculator
Calculate the potential financial impact and ROI of reducing staffing variance

IMPORTANT: These calculations use industry estimates and assumptions.
Your actual ROI will depend on:
- Current variance levels and baseline costs
- Local labor costs (base, overtime, agency rates)
- Implementation effectiveness
- Organizational change management success
Conduct facility-specific analysis with your actual data before making investment decisions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import matplotlib.pyplot as plt
import seaborn as sns


class StaffingROICalculator:
    def __init__(self, 
                 beds: int = 300,
                 units: int = 12,
                 nurses_per_unit: int = 6):
        """
        Initialize ROI calculator with hospital parameters
        
        Args:
            beds: Total hospital beds
            units: Number of nursing units
            nurses_per_unit: Average nurses per unit per shift
        """
        self.beds = beds
        self.units = units  
        self.nurses_per_unit = nurses_per_unit
        self.total_nurses = units * nurses_per_unit * 3  # 3 shifts
        
        # Default cost parameters (adjustable)
        self.costs = {
            'regular_hourly': 45,
            'overtime_multiplier': 1.5,
            'agency_multiplier': 2.5,
            'training_cost_per_nurse': 5000,
            'turnover_cost_per_nurse': 61110,  # NSI 2025 average RN turnover cost
            'sick_day_cost': 540,  # 12 hours at regular rate
        }
        
        # Current state defaults (15-20% variance typical)
        self.current_state = {
            'variance_pct': 18,
            'overtime_pct': 8,
            'agency_pct': 5,
            'turnover_rate': 18,
            'sick_call_rate': 4,
        }
        
        # Target state after intervention
        self.target_state = {
            'variance_pct': 7,
            'overtime_pct': 3,
            'agency_pct': 1,
            'turnover_rate': 15,
            'sick_call_rate': 3,
        }
        
        # Implementation costs
        self.implementation = {
            'software_platform': 150000,
            'training_hours': 500,
            'consulting_days': 20,
            'consulting_rate': 2500,
            'flex_pool_setup': 50000,
            'annual_software': 60000,
            'flex_pool_incentive_annual': 120000,
        }
    
    def calculate_current_costs(self) -> Dict:
        """Calculate current annual costs due to staffing variance"""
        
        # Base calculations
        total_nursing_hours = self.total_nurses * 2080  # Annual hours per FTE
        
        # Overtime costs
        overtime_hours = total_nursing_hours * (self.current_state['overtime_pct'] / 100)
        overtime_premium = overtime_hours * self.costs['regular_hourly'] * (self.costs['overtime_multiplier'] - 1)
        
        # Agency costs  
        agency_hours = total_nursing_hours * (self.current_state['agency_pct'] / 100)
        agency_premium = agency_hours * self.costs['regular_hourly'] * (self.costs['agency_multiplier'] - 1)
        
        # Turnover costs
        annual_turnover = self.total_nurses * (self.current_state['turnover_rate'] / 100)
        turnover_cost = annual_turnover * self.costs['turnover_cost_per_nurse']
        
        # Sick call costs (excess due to burnout)
        excess_sick_days = self.total_nurses * (self.current_state['sick_call_rate'] - 2) * 8  # Days above baseline
        sick_call_cost = excess_sick_days * self.costs['sick_day_cost']
        
        # Productivity loss due to variance (estimated 5% productivity loss)
        productivity_loss = total_nursing_hours * self.costs['regular_hourly'] * 0.05 * (self.current_state['variance_pct'] / 20)
        
        return {
            'overtime_premium': overtime_premium,
            'agency_premium': agency_premium,
            'turnover_cost': turnover_cost,
            'sick_call_cost': sick_call_cost,
            'productivity_loss': productivity_loss,
            'total_annual_cost': overtime_premium + agency_premium + turnover_cost + sick_call_cost + productivity_loss
        }
    
    def calculate_target_costs(self) -> Dict:
        """Calculate costs after implementing variance reduction"""
        
        total_nursing_hours = self.total_nurses * 2080
        
        # Reduced overtime
        overtime_hours = total_nursing_hours * (self.target_state['overtime_pct'] / 100)
        overtime_premium = overtime_hours * self.costs['regular_hourly'] * (self.costs['overtime_multiplier'] - 1)
        
        # Reduced agency
        agency_hours = total_nursing_hours * (self.target_state['agency_pct'] / 100)
        agency_premium = agency_hours * self.costs['regular_hourly'] * (self.costs['agency_multiplier'] - 1)
        
        # Reduced turnover
        annual_turnover = self.total_nurses * (self.target_state['turnover_rate'] / 100)
        turnover_cost = annual_turnover * self.costs['turnover_cost_per_nurse']
        
        # Reduced sick calls
        excess_sick_days = self.total_nurses * (self.target_state['sick_call_rate'] - 2) * 8
        sick_call_cost = excess_sick_days * self.costs['sick_day_cost']
        
        # Improved productivity
        productivity_loss = total_nursing_hours * self.costs['regular_hourly'] * 0.05 * (self.target_state['variance_pct'] / 20)
        
        return {
            'overtime_premium': overtime_premium,
            'agency_premium': agency_premium,
            'turnover_cost': turnover_cost,
            'sick_call_cost': sick_call_cost,
            'productivity_loss': productivity_loss,
            'total_annual_cost': overtime_premium + agency_premium + turnover_cost + sick_call_cost + productivity_loss
        }
    
    def calculate_roi(self) -> Dict:
        """Calculate ROI metrics for variance reduction initiative"""
        
        current_costs = self.calculate_current_costs()
        target_costs = self.calculate_target_costs()
        
        # Annual savings
        annual_savings = current_costs['total_annual_cost'] - target_costs['total_annual_cost']
        
        # One-time implementation costs
        one_time_costs = (
            self.implementation['software_platform'] +
            self.implementation['training_hours'] * self.costs['regular_hourly'] +
            self.implementation['consulting_days'] * self.implementation['consulting_rate'] +
            self.implementation['flex_pool_setup']
        )
        
        # Ongoing annual costs
        ongoing_costs = (
            self.implementation['annual_software'] +
            self.implementation['flex_pool_incentive_annual']
        )
        
        # Net savings
        year1_net = annual_savings - one_time_costs - ongoing_costs
        year2plus_net = annual_savings - ongoing_costs
        
        # ROI calculations
        year1_roi = (year1_net / one_time_costs) * 100
        ongoing_roi = (year2plus_net / ongoing_costs) * 100
        payback_months = (one_time_costs / (annual_savings / 12)) if annual_savings > 0 else float('inf')
        
        # 5-year NPV (assuming 5% discount rate)
        cashflows = [year1_net] + [year2plus_net] * 4
        npv = sum([cf / (1.05 ** i) for i, cf in enumerate(cashflows, 1)])
        
        return {
            'current_annual_cost': current_costs['total_annual_cost'],
            'target_annual_cost': target_costs['total_annual_cost'],
            'annual_savings': annual_savings,
            'one_time_investment': one_time_costs,
            'ongoing_costs': ongoing_costs,
            'year1_net_savings': year1_net,
            'year2plus_net_savings': year2plus_net,
            'year1_roi_pct': year1_roi,
            'ongoing_roi_pct': ongoing_roi,
            'payback_months': payback_months,
            'five_year_npv': npv,
            'weekly_savings': annual_savings / 52,
            'cost_breakdown': {
                'current': current_costs,
                'target': target_costs
            }
        }
    
    def sensitivity_analysis(self) -> pd.DataFrame:
        """Perform sensitivity analysis on key variables"""
        
        results = []
        base_roi = self.calculate_roi()['annual_savings']
        
        # Variables to test
        variables = [
            ('variance_reduction', [25, 50, 75], 'Variance Reduction %'),
            ('overtime_reduction', [25, 50, 75], 'Overtime Reduction %'),
            ('agency_reduction', [40, 60, 80], 'Agency Reduction %'),
            ('turnover_reduction', [10, 20, 30], 'Turnover Reduction %')
        ]
        
        for var_name, percentages, label in variables:
            for pct in percentages:
                # Save original state
                original_current = self.current_state.copy()
                original_target = self.target_state.copy()
                
                # Apply sensitivity
                if var_name == 'variance_reduction':
                    reduction = self.current_state['variance_pct'] * (pct / 100)
                    self.target_state['variance_pct'] = self.current_state['variance_pct'] - reduction
                elif var_name == 'overtime_reduction':
                    reduction = self.current_state['overtime_pct'] * (pct / 100)
                    self.target_state['overtime_pct'] = self.current_state['overtime_pct'] - reduction
                elif var_name == 'agency_reduction':
                    reduction = self.current_state['agency_pct'] * (pct / 100)
                    self.target_state['agency_pct'] = self.current_state['agency_pct'] - reduction
                elif var_name == 'turnover_reduction':
                    reduction = self.current_state['turnover_rate'] * (pct / 100)
                    self.target_state['turnover_rate'] = self.current_state['turnover_rate'] - reduction
                
                # Calculate new ROI
                new_roi = self.calculate_roi()
                
                results.append({
                    'Variable': label,
                    'Change': f'{pct}%',
                    'Annual Savings': new_roi['annual_savings'],
                    'Impact vs Base': new_roi['annual_savings'] - base_roi
                })
                
                # Restore original state
                self.current_state = original_current
                self.target_state = original_target
        
        return pd.DataFrame(results)
    
    def create_roi_visualization(self) -> plt.Figure:
        """Create comprehensive ROI visualization"""
        
        roi_data = self.calculate_roi()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Cost comparison waterfall
        categories = ['Overtime', 'Agency', 'Turnover', 'Sick Calls', 'Productivity']
        current_values = [
            roi_data['cost_breakdown']['current']['overtime_premium'],
            roi_data['cost_breakdown']['current']['agency_premium'],
            roi_data['cost_breakdown']['current']['turnover_cost'],
            roi_data['cost_breakdown']['current']['sick_call_cost'],
            roi_data['cost_breakdown']['current']['productivity_loss']
        ]
        target_values = [
            roi_data['cost_breakdown']['target']['overtime_premium'],
            roi_data['cost_breakdown']['target']['agency_premium'],
            roi_data['cost_breakdown']['target']['turnover_cost'],
            roi_data['cost_breakdown']['target']['sick_call_cost'],
            roi_data['cost_breakdown']['target']['productivity_loss']
        ]
        
        x = np.arange(len(categories))
        width = 0.35
        
        axes[0, 0].bar(x - width/2, current_values, width, label='Current', color='red', alpha=0.7)
        axes[0, 0].bar(x + width/2, target_values, width, label='Target', color='green', alpha=0.7)
        axes[0, 0].set_xlabel('Cost Category')
        axes[0, 0].set_ylabel('Annual Cost ($)')
        axes[0, 0].set_title('Cost Reduction by Category')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(categories, rotation=45)
        axes[0, 0].legend()
        axes[0, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        # 2. Cumulative savings over 5 years
        years = np.arange(1, 6)
        cumulative_savings = []
        annual_savings = roi_data['annual_savings']
        one_time = roi_data['one_time_investment']
        ongoing = roi_data['ongoing_costs']
        
        for year in years:
            if year == 1:
                cumulative_savings.append(annual_savings - one_time - ongoing)
            else:
                cumulative_savings.append(cumulative_savings[-1] + annual_savings - ongoing)
        
        axes[0, 1].bar(years, cumulative_savings, color=['red' if x < 0 else 'green' for x in cumulative_savings])
        axes[0, 1].set_xlabel('Year')
        axes[0, 1].set_ylabel('Cumulative Savings ($)')
        axes[0, 1].set_title('5-Year Cumulative Savings')
        axes[0, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[0, 1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        # Add payback period line
        if roi_data['payback_months'] < 60:
            payback_year = roi_data['payback_months'] / 12
            axes[0, 1].axvline(x=payback_year, color='blue', linestyle='--', 
                             label=f'Payback: {roi_data["payback_months"]:.0f} months')
            axes[0, 1].legend()
        
        # 3. Sensitivity analysis
        sensitivity_df = self.sensitivity_analysis()
        pivot_df = sensitivity_df.pivot(index='Change', columns='Variable', values='Annual Savings')
        
        for column in pivot_df.columns:
            axes[1, 0].plot(pivot_df.index, pivot_df[column], marker='o', label=column)
        
        axes[1, 0].set_xlabel('Improvement Level')
        axes[1, 0].set_ylabel('Annual Savings ($)')
        axes[1, 0].set_title('Sensitivity Analysis')
        axes[1, 0].legend(loc='best', fontsize=8)
        axes[1, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. ROI metrics summary
        metrics_text = f"""
        Key ROI Metrics
        ═══════════════════════════
        
        Current Annual Cost: ${roi_data['current_annual_cost']/1e6:.2f}M
        Target Annual Cost: ${roi_data['target_annual_cost']/1e6:.2f}M
        Annual Savings: ${roi_data['annual_savings']/1e6:.2f}M
        
        Implementation Cost: ${roi_data['one_time_investment']/1e3:.0f}K
        Ongoing Annual Cost: ${roi_data['ongoing_costs']/1e3:.0f}K
        
        Year 1 ROI: {roi_data['year1_roi_pct']:.0f}%
        Ongoing ROI: {roi_data['ongoing_roi_pct']:.0f}%
        Payback Period: {roi_data['payback_months']:.1f} months
        
        5-Year NPV: ${roi_data['five_year_npv']/1e6:.2f}M
        Weekly Savings: ${roi_data['weekly_savings']/1e3:.0f}K
        """
        
        axes[1, 1].text(0.1, 0.5, metrics_text, transform=axes[1, 1].transAxes,
                       fontsize=10, verticalalignment='center',
                       fontfamily='monospace')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        return fig
    
    def generate_executive_summary(self) -> str:
        """Generate executive summary of ROI analysis"""
        
        roi = self.calculate_roi()
        
        summary = f"""
STAFFING VARIANCE REDUCTION - ROI ANALYSIS
{'='*60}

FACILITY PROFILE
----------------
Hospital Size: {self.beds} beds
Nursing Units: {self.units}
Total Nursing FTEs: {self.total_nurses}

CURRENT STATE ANALYSIS
----------------------
Staffing Variance: {self.current_state['variance_pct']}%
Overtime Rate: {self.current_state['overtime_pct']}% of hours
Agency Usage: {self.current_state['agency_pct']}% of hours
Annual Turnover: {self.current_state['turnover_rate']}%

Current Annual Cost of Variance: ${roi['current_annual_cost']:,.0f}

PROPOSED INTERVENTION
---------------------
Target Variance: {self.target_state['variance_pct']}%
Target Overtime: {self.target_state['overtime_pct']}% of hours
Target Agency: {self.target_state['agency_pct']}% of hours
Target Turnover: {self.target_state['turnover_rate']}%

Projected Annual Cost: ${roi['target_annual_cost']:,.0f}

FINANCIAL ANALYSIS
------------------
Annual Savings: ${roi['annual_savings']:,.0f}
Weekly Savings: ${roi['weekly_savings']:,.0f}

Investment Required:
  - One-time: ${roi['one_time_investment']:,.0f}
  - Annual: ${roi['ongoing_costs']:,.0f}

ROI METRICS
-----------
Year 1 ROI: {roi['year1_roi_pct']:.0f}%
Ongoing Annual ROI: {roi['ongoing_roi_pct']:.0f}%
Payback Period: {roi['payback_months']:.1f} months
5-Year NPV (5% discount): ${roi['five_year_npv']:,.0f}

SAVINGS BREAKDOWN
-----------------
Overtime Reduction: ${roi['cost_breakdown']['current']['overtime_premium'] - roi['cost_breakdown']['target']['overtime_premium']:,.0f}
Agency Reduction: ${roi['cost_breakdown']['current']['agency_premium'] - roi['cost_breakdown']['target']['agency_premium']:,.0f}
Turnover Reduction: ${roi['cost_breakdown']['current']['turnover_cost'] - roi['cost_breakdown']['target']['turnover_cost']:,.0f}
Other Benefits: ${roi['cost_breakdown']['current']['sick_call_cost'] + roi['cost_breakdown']['current']['productivity_loss'] - roi['cost_breakdown']['target']['sick_call_cost'] - roi['cost_breakdown']['target']['productivity_loss']:,.0f}

RECOMMENDATION
--------------
With a payback period of {roi['payback_months']:.0f} months and ongoing ROI of {roi['ongoing_roi_pct']:.0f}%,
this initiative represents a high-value investment in operational efficiency.

Every week of delay costs approximately ${roi['weekly_savings']:,.0f}.

NEXT STEPS
----------
1. Validate assumptions with your facility's data
2. Identify pilot units for initial implementation
3. Establish baseline metrics for tracking
4. Begin vendor evaluation for predictive analytics platform
"""
        
        return summary


def main():
    """Main execution function"""
    print("Staffing Variance ROI Calculator")
    print("=" * 40)
    
    # Get facility parameters (using defaults for demo)
    beds = 300
    units = 12
    
    print(f"\nAnalyzing {beds}-bed hospital with {units} units...")
    
    # Initialize calculator
    calculator = StaffingROICalculator(beds=beds, units=units)
    
    # Generate executive summary
    summary = calculator.generate_executive_summary()
    print(summary)
    
    # Create visualizations
    print("\nGenerating ROI visualizations...")
    fig = calculator.create_roi_visualization()
    plt.savefig('staffing_roi_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: staffing_roi_analysis.png")
    
    # Perform sensitivity analysis
    print("\nPerforming sensitivity analysis...")
    sensitivity_df = calculator.sensitivity_analysis()
    sensitivity_df.to_csv('sensitivity_analysis.csv', index=False)
    print("Saved: sensitivity_analysis.csv")
    
    # Create detailed breakdown
    roi_details = calculator.calculate_roi()
    breakdown_df = pd.DataFrame([
        {'Category': 'Overtime Premium', 
         'Current': roi_details['cost_breakdown']['current']['overtime_premium'],
         'Target': roi_details['cost_breakdown']['target']['overtime_premium']},
        {'Category': 'Agency Premium',
         'Current': roi_details['cost_breakdown']['current']['agency_premium'],
         'Target': roi_details['cost_breakdown']['target']['agency_premium']},
        {'Category': 'Turnover Cost',
         'Current': roi_details['cost_breakdown']['current']['turnover_cost'],
         'Target': roi_details['cost_breakdown']['target']['turnover_cost']},
        {'Category': 'Excess Sick Calls',
         'Current': roi_details['cost_breakdown']['current']['sick_call_cost'],
         'Target': roi_details['cost_breakdown']['target']['sick_call_cost']},
        {'Category': 'Productivity Loss',
         'Current': roi_details['cost_breakdown']['current']['productivity_loss'],
         'Target': roi_details['cost_breakdown']['target']['productivity_loss']}
    ])
    breakdown_df['Savings'] = breakdown_df['Current'] - breakdown_df['Target']
    breakdown_df.to_csv('cost_breakdown.csv', index=False)
    print("Saved: cost_breakdown.csv")
    
    return calculator


if __name__ == "__main__":
    calculator = main()