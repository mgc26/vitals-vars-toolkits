#!/usr/bin/env python3
"""
Discharge by Noon ROI Calculator
Calculate the financial impact and ROI of improving discharge timing
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class DischargeROICalculator:
    """Calculate financial impact of discharge by noon improvements"""
    
    def __init__(self, hospital_size=200, avg_daily_census=160):
        """
        Initialize with hospital parameters
        
        Args:
            hospital_size: Total number of beds
            avg_daily_census: Average daily occupied beds
        """
        self.hospital_size = hospital_size
        self.avg_daily_census = avg_daily_census
        self.occupancy_rate = avg_daily_census / hospital_size
        
        # Financial parameters (can be customized)
        self.financial_params = {
            'revenue_per_admission': 8000,
            'ed_boarding_cost_per_hour': 250,
            'overtime_cost_per_hour': 75,
            'staff_hours_saved_per_early_discharge': 2,
            'unnecessary_day_cost': 600,
            'surgical_case_revenue': 15000,
            'ed_diversion_loss_per_hour': 2000
        }
        
        # Operational parameters
        self.operational_params = {
            'annual_discharges': self.avg_daily_census * 365 / 4.5,  # Assuming 4.5 day ALOS
            'current_dbn_rate': 0.20,
            'target_dbn_rate': 0.40,
            'avg_ed_boarding_hours': 6,
            'surgical_cases_cancelled_per_month': 8,
            'weekend_discharge_rate': 0.10
        }
    
    def calculate_capacity_gains(self, improvement_rate):
        """Calculate bed capacity gains from DBN improvement"""
        # Each 2-hour earlier discharge = 8.3% more bed capacity
        hours_gained = improvement_rate * 0.20 * 2  # 20% improvement * 2 hours
        capacity_gain_percent = hours_gained / 24
        
        # Convert to bed-days
        annual_bed_days_gained = self.hospital_size * 365 * capacity_gain_percent
        
        # New admissions possible
        avg_los = 4.5
        new_admissions_possible = annual_bed_days_gained / avg_los
        
        return {
            'capacity_gain_percent': capacity_gain_percent * 100,
            'annual_bed_days_gained': annual_bed_days_gained,
            'new_admissions_possible': new_admissions_possible,
            'revenue_from_new_admissions': new_admissions_possible * self.financial_params['revenue_per_admission']
        }
    
    def calculate_ed_boarding_reduction(self, dbn_improvement):
        """Calculate savings from reduced ED boarding"""
        # Every 10% DBN improvement reduces ED boarding by ~15%
        boarding_reduction_percent = dbn_improvement * 1.5
        
        # Estimate current ED boarding hours
        annual_ed_visits = self.hospital_size * 365  # Rough estimate
        admission_rate = 0.20  # 20% of ED visits result in admission
        annual_admissions_from_ed = annual_ed_visits * admission_rate
        
        # Current boarding hours
        current_boarding_hours = annual_admissions_from_ed * self.operational_params['avg_ed_boarding_hours']
        boarding_hours_saved = current_boarding_hours * boarding_reduction_percent
        
        # Financial impact
        boarding_cost_savings = boarding_hours_saved * self.financial_params['ed_boarding_cost_per_hour']
        
        # ED diversion reduction (fewer boarding = less diversion)
        diversion_hours_saved = boarding_hours_saved * 0.05  # 5% of boarding time causes diversion
        diversion_revenue_recovered = diversion_hours_saved * self.financial_params['ed_diversion_loss_per_hour']
        
        return {
            'boarding_hours_saved': boarding_hours_saved,
            'boarding_cost_savings': boarding_cost_savings,
            'diversion_hours_saved': diversion_hours_saved,
            'diversion_revenue_recovered': diversion_revenue_recovered,
            'total_ed_impact': boarding_cost_savings + diversion_revenue_recovered
        }
    
    def calculate_staff_efficiency(self, dbn_improvement):
        """Calculate staff efficiency gains"""
        # More morning discharges = less afternoon/evening chaos
        annual_discharges = self.operational_params['annual_discharges']
        
        # Discharges shifting to morning
        discharges_shifted = annual_discharges * dbn_improvement
        
        # Staff hours saved (less overtime, better scheduling)
        staff_hours_saved = discharges_shifted * self.financial_params['staff_hours_saved_per_early_discharge']
        overtime_savings = staff_hours_saved * 0.3 * self.financial_params['overtime_cost_per_hour']
        
        # Reduced weekend staffing needs
        weekend_improvement = dbn_improvement * 0.5  # Weekend improves half as much
        weekend_discharges_improved = annual_discharges * 0.28 * weekend_improvement  # 28% of year is weekend
        weekend_staffing_savings = weekend_discharges_improved * 4 * self.financial_params['overtime_cost_per_hour']
        
        return {
            'staff_hours_saved': staff_hours_saved,
            'overtime_savings': overtime_savings,
            'weekend_staffing_savings': weekend_staffing_savings,
            'total_staff_savings': overtime_savings + weekend_staffing_savings
        }
    
    def calculate_quality_impact(self, dbn_improvement):
        """Calculate quality-related financial impacts"""
        # Reduced unnecessary days
        annual_patient_days = self.avg_daily_census * 365
        unnecessary_days_percent = 0.05  # 5% of days are unnecessary
        unnecessary_days_reduced = annual_patient_days * unnecessary_days_percent * dbn_improvement * 0.4
        unnecessary_day_savings = unnecessary_days_reduced * self.financial_params['unnecessary_day_cost']
        
        # Surgical efficiency (fewer cancellations due to bed shortage)
        monthly_surgical_cancellations = self.operational_params['surgical_cases_cancelled_per_month']
        cancellations_avoided = monthly_surgical_cancellations * dbn_improvement * 0.3 * 12
        surgical_revenue_recovered = cancellations_avoided * self.financial_params['surgical_case_revenue']
        
        # Patient satisfaction (affects reimbursement)
        satisfaction_improvement_value = self.operational_params['annual_discharges'] * 50 * dbn_improvement * 0.2
        
        return {
            'unnecessary_days_reduced': unnecessary_days_reduced,
            'unnecessary_day_savings': unnecessary_day_savings,
            'surgical_cancellations_avoided': cancellations_avoided,
            'surgical_revenue_recovered': surgical_revenue_recovered,
            'satisfaction_improvement_value': satisfaction_improvement_value,
            'total_quality_impact': unnecessary_day_savings + surgical_revenue_recovered + satisfaction_improvement_value
        }
    
    def calculate_implementation_costs(self):
        """Estimate costs of implementing DBN program"""
        costs = {
            'ehr_dashboard_development': 25000,
            'training_hours': 500 * 50,  # 500 hours @ $50/hour
            'process_improvement_consultant': 50000,
            'communication_tools': 10000,
            'pilot_program_costs': 15000,
            'annual_maintenance': 20000
        }
        
        costs['total_first_year'] = sum(costs.values())
        costs['total_ongoing_annual'] = costs['annual_maintenance']
        
        return costs
    
    def calculate_total_roi(self, target_dbn_rate=None):
        """Calculate complete ROI analysis"""
        if target_dbn_rate is None:
            target_dbn_rate = self.operational_params['target_dbn_rate']
        
        current_dbn = self.operational_params['current_dbn_rate']
        improvement = target_dbn_rate - current_dbn
        
        # Calculate all benefits
        capacity = self.calculate_capacity_gains(improvement)
        ed_impact = self.calculate_ed_boarding_reduction(improvement)
        staff = self.calculate_staff_efficiency(improvement)
        quality = self.calculate_quality_impact(improvement)
        
        # Calculate costs
        costs = self.calculate_implementation_costs()
        
        # Summarize financial impact
        total_annual_benefit = (
            capacity['revenue_from_new_admissions'] +
            ed_impact['total_ed_impact'] +
            staff['total_staff_savings'] +
            quality['total_quality_impact']
        )
        
        roi_year1 = (total_annual_benefit - costs['total_first_year']) / costs['total_first_year'] * 100
        roi_ongoing = (total_annual_benefit - costs['total_ongoing_annual']) / costs['total_ongoing_annual'] * 100
        payback_months = costs['total_first_year'] / (total_annual_benefit / 12)
        
        return {
            'current_dbn_rate': current_dbn * 100,
            'target_dbn_rate': target_dbn_rate * 100,
            'improvement_points': improvement * 100,
            'capacity_gains': capacity,
            'ed_impact': ed_impact,
            'staff_efficiency': staff,
            'quality_impact': quality,
            'implementation_costs': costs,
            'total_annual_benefit': total_annual_benefit,
            'roi_year1_percent': roi_year1,
            'roi_ongoing_percent': roi_ongoing,
            'payback_months': payback_months
        }
    
    def generate_roi_report(self, target_dbn_rate=None):
        """Generate comprehensive ROI report"""
        roi = self.calculate_total_roi(target_dbn_rate)
        
        print("\n" + "="*60)
        print("DISCHARGE BY NOON ROI ANALYSIS")
        print("="*60)
        
        print(f"\nHospital Profile:")
        print(f"  - Bed Size: {self.hospital_size}")
        print(f"  - Average Daily Census: {self.avg_daily_census}")
        print(f"  - Current Occupancy: {self.occupancy_rate*100:.1f}%")
        
        print(f"\nDBN Performance:")
        print(f"  - Current DBN Rate: {roi['current_dbn_rate']:.1f}%")
        print(f"  - Target DBN Rate: {roi['target_dbn_rate']:.1f}%")
        print(f"  - Improvement: +{roi['improvement_points']:.1f} percentage points")
        
        print(f"\nAnnual Financial Benefits:")
        print(f"  Capacity & Revenue:")
        print(f"    - New Admissions Possible: {roi['capacity_gains']['new_admissions_possible']:.0f}")
        print(f"    - Revenue from New Capacity: ${roi['capacity_gains']['revenue_from_new_admissions']:,.0f}")
        
        print(f"  ED & Patient Flow:")
        print(f"    - ED Boarding Hours Saved: {roi['ed_impact']['boarding_hours_saved']:,.0f}")
        print(f"    - Total ED Impact: ${roi['ed_impact']['total_ed_impact']:,.0f}")
        
        print(f"  Staff Efficiency:")
        print(f"    - Overtime Savings: ${roi['staff_efficiency']['overtime_savings']:,.0f}")
        print(f"    - Weekend Staffing Savings: ${roi['staff_efficiency']['weekend_staffing_savings']:,.0f}")
        
        print(f"  Quality & Operations:")
        print(f"    - Unnecessary Days Reduced: {roi['quality_impact']['unnecessary_days_reduced']:,.0f}")
        print(f"    - Surgical Revenue Recovered: ${roi['quality_impact']['surgical_revenue_recovered']:,.0f}")
        
        print(f"\nImplementation Investment:")
        print(f"  - First Year Total: ${roi['implementation_costs']['total_first_year']:,.0f}")
        print(f"  - Ongoing Annual: ${roi['implementation_costs']['total_ongoing_annual']:,.0f}")
        
        print(f"\nROI Summary:")
        print(f"  - Total Annual Benefit: ${roi['total_annual_benefit']:,.0f}")
        print(f"  - First Year ROI: {roi['roi_year1_percent']:.0f}%")
        print(f"  - Ongoing Annual ROI: {roi['roi_ongoing_percent']:.0f}%")
        print(f"  - Payback Period: {roi['payback_months']:.1f} months")
        
        print("\n" + "="*60)
        
        return roi
    
    def plot_roi_breakdown(self, roi_data=None):
        """Visualize ROI components"""
        if roi_data is None:
            roi_data = self.calculate_total_roi()
        
        # Prepare data for visualization
        benefits = {
            'New Admission Revenue': roi_data['capacity_gains']['revenue_from_new_admissions'],
            'ED Impact': roi_data['ed_impact']['total_ed_impact'],
            'Staff Savings': roi_data['staff_efficiency']['total_staff_savings'],
            'Quality Impact': roi_data['quality_impact']['total_quality_impact']
        }
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Benefit breakdown
        colors = sns.color_palette('viridis', len(benefits))
        bars = ax1.bar(benefits.keys(), benefits.values(), color=colors)
        ax1.set_ylabel('Annual Benefit ($)')
        ax1.set_title('Annual Financial Benefits by Category')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}', ha='center', va='bottom')
        
        # ROI over time
        years = range(1, 6)
        cumulative_benefit = []
        cumulative_cost = []
        
        for year in years:
            if year == 1:
                cost = roi_data['implementation_costs']['total_first_year']
            else:
                cost = roi_data['implementation_costs']['total_ongoing_annual']
            
            cumulative_cost.append(sum(cumulative_cost) + cost if cumulative_cost else cost)
            cumulative_benefit.append(roi_data['total_annual_benefit'] * year)
        
        ax2.plot(years, cumulative_benefit, 'g-', linewidth=2, label='Cumulative Benefit')
        ax2.plot(years, cumulative_cost, 'r--', linewidth=2, label='Cumulative Cost')
        ax2.fill_between(years, cumulative_benefit, cumulative_cost, 
                        where=[b > c for b, c in zip(cumulative_benefit, cumulative_cost)],
                        alpha=0.3, color='green', label='Net Positive ROI')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Cumulative Amount ($)')
        ax2.set_title('5-Year ROI Projection')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def sensitivity_analysis(self):
        """Analyze ROI sensitivity to different DBN improvement levels"""
        improvements = np.arange(0.05, 0.31, 0.05)
        results = []
        
        for imp in improvements:
            target = self.operational_params['current_dbn_rate'] + imp
            roi = self.calculate_total_roi(target)
            results.append({
                'improvement': imp * 100,
                'target_dbn': target * 100,
                'annual_benefit': roi['total_annual_benefit'],
                'roi_percent': roi['roi_year1_percent'],
                'payback_months': roi['payback_months']
            })
        
        results_df = pd.DataFrame(results)
        
        # Plot sensitivity analysis
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        ax1.plot(results_df['target_dbn'], results_df['annual_benefit'] / 1000000, 
                'bo-', linewidth=2, markersize=8)
        ax1.set_xlabel('Target DBN Rate (%)')
        ax1.set_ylabel('Annual Benefit ($M)')
        ax1.set_title('Annual Benefit vs DBN Target')
        ax1.grid(True, alpha=0.3)
        
        ax2.bar(results_df['target_dbn'], results_df['payback_months'], 
               color=plt.cm.RdYlGn_r(results_df['payback_months'] / 24))
        ax2.set_xlabel('Target DBN Rate (%)')
        ax2.set_ylabel('Payback Period (Months)')
        ax2.set_title('Investment Payback Period')
        ax2.axhline(y=12, color='red', linestyle='--', label='1 Year')
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
        
        return results_df


def main():
    """Example usage of ROI calculator"""
    print("Initializing Discharge by Noon ROI Calculator...")
    
    # Create calculator for a 200-bed hospital
    calculator = DischargeROICalculator(hospital_size=200, avg_daily_census=160)
    
    # Generate comprehensive ROI report
    roi_data = calculator.generate_roi_report(target_dbn_rate=0.40)
    
    # Visualize ROI breakdown
    print("\nGenerating ROI visualizations...")
    calculator.plot_roi_breakdown(roi_data)
    
    # Perform sensitivity analysis
    print("\nPerforming sensitivity analysis...")
    sensitivity_results = calculator.sensitivity_analysis()
    
    print("\n✓ ROI analysis complete!")
    print(f"\nKey Takeaway: Improving DBN from 20% to 40% generates ${roi_data['total_annual_benefit']:,.0f} annually")
    print(f"with a payback period of just {roi_data['payback_months']:.0f} months.")


if __name__ == "__main__":
    main()