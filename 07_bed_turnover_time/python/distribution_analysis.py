#!/usr/bin/env python3
"""
Distribution Analysis for Bed Turnover ROI Calculator
Analyze which distributions are causing excessive variance in Monte Carlo simulation
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def analyze_distributions(n_samples=10000):
    """Analyze the individual distributions used in the Monte Carlo simulation"""
    np.random.seed(42)
    
    print("DISTRIBUTION ANALYSIS - BED TURNOVER ROI")
    print("=" * 50)
    
    # Generate samples from each distribution
    samples = {}
    
    # 1. Occupancy rate - Beta(7.5, 2.5)
    occupancy = np.random.beta(7.5, 2.5, n_samples)
    samples['occupancy'] = occupancy
    print(f"\n1. OCCUPANCY RATE - Beta(7.5, 2.5)")
    print(f"   Mean: {np.mean(occupancy):.3f}")
    print(f"   Std:  {np.std(occupancy):.3f}")
    print(f"   95% CI: {np.percentile(occupancy, 2.5):.3f} - {np.percentile(occupancy, 97.5):.3f}")
    print(f"   Range: {np.min(occupancy):.3f} - {np.max(occupancy):.3f}")
    print(f"   Coefficient of Variation: {np.std(occupancy)/np.mean(occupancy):.3f}")
    
    # 2. Current turnover time - Normal(180, 30)
    current_turnover = np.random.normal(180, 30, n_samples)
    current_turnover = np.maximum(120, current_turnover)  # Floor at 2 hours
    samples['current_turnover'] = current_turnover
    print(f"\n2. CURRENT TURNOVER TIME - Normal(180, 30), floored at 120")
    print(f"   Mean: {np.mean(current_turnover):.1f} minutes")
    print(f"   Std:  {np.std(current_turnover):.1f} minutes")
    print(f"   95% CI: {np.percentile(current_turnover, 2.5):.1f} - {np.percentile(current_turnover, 97.5):.1f} minutes")
    print(f"   Range: {np.min(current_turnover):.1f} - {np.max(current_turnover):.1f} minutes")
    print(f"   Coefficient of Variation: {np.std(current_turnover)/np.mean(current_turnover):.3f}")
    
    # 3. Target turnover time - Normal(90, 15)
    target_turnover = np.random.normal(90, 15, n_samples)
    target_turnover = np.clip(target_turnover, 60, 120)  # Bound 60-120
    samples['target_turnover'] = target_turnover
    print(f"\n3. TARGET TURNOVER TIME - Normal(90, 15), bounded 60-120")
    print(f"   Mean: {np.mean(target_turnover):.1f} minutes")
    print(f"   Std:  {np.std(target_turnover):.1f} minutes")
    print(f"   95% CI: {np.percentile(target_turnover, 2.5):.1f} - {np.percentile(target_turnover, 97.5):.1f} minutes")
    print(f"   Range: {np.min(target_turnover):.1f} - {np.max(target_turnover):.1f} minutes")
    print(f"   Coefficient of Variation: {np.std(target_turnover)/np.mean(target_turnover):.3f}")
    
    # 4. Revenue per bed day - Lognormal
    revenue_per_bed = np.random.lognormal(np.log(2000), 0.2, n_samples)
    samples['revenue_per_bed'] = revenue_per_bed
    print(f"\n4. REVENUE PER BED DAY - Lognormal(ln(2000), 0.2)")
    print(f"   Mean: ${np.mean(revenue_per_bed):.0f}")
    print(f"   Std:  ${np.std(revenue_per_bed):.0f}")
    print(f"   95% CI: ${np.percentile(revenue_per_bed, 2.5):.0f} - ${np.percentile(revenue_per_bed, 97.5):.0f}")
    print(f"   Range: ${np.min(revenue_per_bed):.0f} - ${np.max(revenue_per_bed):.0f}")
    print(f"   Coefficient of Variation: {np.std(revenue_per_bed)/np.mean(revenue_per_bed):.3f}")
    
    # 5. Implementation cost - Triangular(200k, 350k, 500k)
    impl_cost = np.random.triangular(200000, 350000, 500000, n_samples)
    samples['impl_cost'] = impl_cost
    print(f"\n5. IMPLEMENTATION COST - Triangular(200k, 350k, 500k)")
    print(f"   Mean: ${np.mean(impl_cost):.0f}")
    print(f"   Std:  ${np.std(impl_cost):.0f}")
    print(f"   95% CI: ${np.percentile(impl_cost, 2.5):.0f} - ${np.percentile(impl_cost, 97.5):.0f}")
    print(f"   Range: ${np.min(impl_cost):.0f} - ${np.max(impl_cost):.0f}")
    print(f"   Coefficient of Variation: {np.std(impl_cost)/np.mean(impl_cost):.3f}")
    
    # 6. Margin - Beta(4, 6) 
    margin = np.random.beta(4, 6, n_samples)
    samples['margin'] = margin
    print(f"\n6. PROFIT MARGIN - Beta(4, 6)")
    print(f"   Mean: {np.mean(margin):.3f}")
    print(f"   Std:  {np.std(margin):.3f}")
    print(f"   95% CI: {np.percentile(margin, 2.5):.3f} - {np.percentile(margin, 97.5):.3f}")
    print(f"   Range: {np.min(margin):.3f} - {np.max(margin):.3f}")
    print(f"   Coefficient of Variation: {np.std(margin)/np.mean(margin):.3f}")
    
    # Calculate compound effect on annual benefit
    print(f"\n" + "="*50)
    print("COMPOUND VARIANCE ANALYSIS")
    print("="*50)
    
    # Simulate the key calculation components
    bed_count = 300
    annual_discharges_per_bed = 91.25
    
    # Time savings component
    time_saved = current_turnover - target_turnover
    time_saved_cv = np.std(time_saved) / np.mean(time_saved)
    print(f"Time Saved CV: {time_saved_cv:.3f}")
    
    # Operational beds
    operational_beds = bed_count * occupancy
    operational_beds_cv = np.std(operational_beds) / np.mean(operational_beds)
    print(f"Operational Beds CV: {operational_beds_cv:.3f}")
    
    # Annual turnovers
    annual_turnovers = operational_beds * annual_discharges_per_bed
    annual_turnovers_cv = np.std(annual_turnovers) / np.mean(annual_turnovers)
    print(f"Annual Turnovers CV: {annual_turnovers_cv:.3f}")
    
    # Bed days gained
    annual_hours_saved = (annual_turnovers * time_saved) / 60
    annual_bed_days_gained = annual_hours_saved / 24
    bed_days_cv = np.std(annual_bed_days_gained) / np.mean(annual_bed_days_gained)
    print(f"Bed Days Gained CV: {bed_days_cv:.3f}")
    
    # Direct revenue (before margin)
    direct_revenue_gross = annual_bed_days_gained * revenue_per_bed
    direct_revenue_gross_cv = np.std(direct_revenue_gross) / np.mean(direct_revenue_gross)
    print(f"Direct Revenue (gross) CV: {direct_revenue_gross_cv:.3f}")
    
    # With margin applied
    direct_revenue = direct_revenue_gross * margin
    direct_revenue_cv = np.std(direct_revenue) / np.mean(direct_revenue)
    print(f"Direct Revenue (net) CV: {direct_revenue_cv:.3f}")
    
    # Identify the biggest drivers
    print(f"\nVARIANCE CONTRIBUTION RANKING:")
    cv_components = {
        'Time Saved': time_saved_cv,
        'Occupancy': np.std(occupancy)/np.mean(occupancy),
        'Revenue per Bed': np.std(revenue_per_bed)/np.mean(revenue_per_bed),
        'Margin': np.std(margin)/np.mean(margin),
        'Implementation Cost': np.std(impl_cost)/np.mean(impl_cost)
    }
    
    for name, cv in sorted(cv_components.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name}: {cv:.3f}")
    
    return samples

def realistic_distributions_analysis(n_samples=10000):
    """Analyze more realistic, tighter distributions"""
    np.random.seed(42)
    
    print(f"\n" + "="*50)
    print("PROPOSED REALISTIC DISTRIBUTIONS")
    print("="*50)
    
    # More realistic distributions
    samples_realistic = {}
    
    # 1. Occupancy - Much tighter, hospitals know their occupancy well
    # Beta(30, 10) gives mean 0.75 with much tighter range
    occupancy_real = np.random.beta(30, 10, n_samples)
    samples_realistic['occupancy'] = occupancy_real
    print(f"\n1. OCCUPANCY RATE - Beta(30, 10) [TIGHTER]")
    print(f"   Mean: {np.mean(occupancy_real):.3f}")
    print(f"   Std:  {np.std(occupancy_real):.3f}")
    print(f"   95% CI: {np.percentile(occupancy_real, 2.5):.3f} - {np.percentile(occupancy_real, 97.5):.3f}")
    print(f"   CV: {np.std(occupancy_real)/np.mean(occupancy_real):.3f}")
    
    # 2. Current turnover - Much smaller variation
    current_turnover_real = np.random.normal(180, 15, n_samples)  # Half the std
    current_turnover_real = np.maximum(150, current_turnover_real)
    samples_realistic['current_turnover'] = current_turnover_real
    print(f"\n2. CURRENT TURNOVER - Normal(180, 15) [TIGHTER]")
    print(f"   Mean: {np.mean(current_turnover_real):.1f} minutes")
    print(f"   95% CI: {np.percentile(current_turnover_real, 2.5):.1f} - {np.percentile(current_turnover_real, 97.5):.1f}")
    print(f"   CV: {np.std(current_turnover_real)/np.mean(current_turnover_real):.3f}")
    
    # 3. Target turnover - Fixed (hospitals control this)
    target_turnover_real = np.full(n_samples, 90)  # Fixed target
    samples_realistic['target_turnover'] = target_turnover_real
    print(f"\n3. TARGET TURNOVER - Fixed at 90 minutes [NO VARIATION]")
    
    # 4. Revenue - Truncated normal instead of lognormal
    revenue_real = np.random.normal(2000, 200, n_samples)  # Much tighter
    revenue_real = np.clip(revenue_real, 1500, 2500)
    samples_realistic['revenue_per_bed'] = revenue_real
    print(f"\n4. REVENUE PER BED - Normal(2000, 200), clipped [MUCH TIGHTER]")
    print(f"   Mean: ${np.mean(revenue_real):.0f}")
    print(f"   95% CI: ${np.percentile(revenue_real, 2.5):.0f} - ${np.percentile(revenue_real, 97.5):.0f}")
    print(f"   CV: {np.std(revenue_real)/np.mean(revenue_real):.3f}")
    
    # 5. Implementation cost - Tighter triangular
    impl_cost_real = np.random.triangular(300000, 350000, 400000, n_samples)
    samples_realistic['impl_cost'] = impl_cost_real
    print(f"\n5. IMPLEMENTATION COST - Triangular(300k, 350k, 400k) [TIGHTER]")
    print(f"   Mean: ${np.mean(impl_cost_real):.0f}")
    print(f"   95% CI: ${np.percentile(impl_cost_real, 2.5):.0f} - ${np.percentile(impl_cost_real, 97.5):.0f}")
    print(f"   CV: {np.std(impl_cost_real)/np.mean(impl_cost_real):.3f}")
    
    # 6. Margin - Tighter beta
    margin_real = np.random.beta(8, 12, n_samples)  # Mean 0.4, much tighter
    samples_realistic['margin'] = margin_real
    print(f"\n6. PROFIT MARGIN - Beta(8, 12) [TIGHTER]")
    print(f"   Mean: {np.mean(margin_real):.3f}")
    print(f"   95% CI: {np.percentile(margin_real, 2.5):.3f} - {np.percentile(margin_real, 97.5):.3f}")
    print(f"   CV: {np.std(margin_real)/np.mean(margin_real):.3f}")
    
    # Calculate realistic annual benefit range
    bed_count = 300
    annual_discharges_per_bed = 91.25
    
    time_saved_real = current_turnover_real - target_turnover_real
    operational_beds_real = bed_count * occupancy_real
    annual_turnovers_real = operational_beds_real * annual_discharges_per_bed
    annual_hours_saved_real = (annual_turnovers_real * time_saved_real) / 60
    annual_bed_days_gained_real = annual_hours_saved_real / 24
    direct_revenue_real = annual_bed_days_gained_real * revenue_real * margin_real
    
    # Add other benefits (keep these as reasonable constants)
    ed_benefit_pct = 0.10  # Fixed 10%
    surgery_benefit_pct = 0.05  # Fixed 5%
    overtime_benefit_pct = 0.15  # Fixed 15%
    
    ed_savings_real = direct_revenue_real * ed_benefit_pct
    surgery_savings_real = direct_revenue_real * surgery_benefit_pct
    overtime_savings_real = annual_turnovers_real * 0.5 * 75 * overtime_benefit_pct
    
    total_benefit_real = direct_revenue_real + ed_savings_real + surgery_savings_real + overtime_savings_real
    
    print(f"\nREALISTIC ANNUAL BENEFIT DISTRIBUTION:")
    print(f"   Mean: ${np.mean(total_benefit_real):,.0f}")
    print(f"   Std:  ${np.std(total_benefit_real):,.0f}")
    print(f"   95% CI: ${np.percentile(total_benefit_real, 2.5):,.0f} - ${np.percentile(total_benefit_real, 97.5):,.0f}")
    print(f"   CV: {np.std(total_benefit_real)/np.mean(total_benefit_real):.3f}")
    print(f"   Range Factor: {np.percentile(total_benefit_real, 97.5)/np.percentile(total_benefit_real, 2.5):.1f}x")
    
    return samples_realistic, total_benefit_real

if __name__ == "__main__":
    # Analyze current distributions
    current_samples = analyze_distributions()
    
    # Analyze realistic distributions
    realistic_samples, realistic_benefits = realistic_distributions_analysis()
    
    print(f"\n" + "="*50)
    print("RECOMMENDATION SUMMARY")
    print("="*50)
    print("The excessive variance is caused by:")
    print("1. Lognormal revenue distribution creates extreme outliers")
    print("2. Wide occupancy variation (Beta(7.5, 2.5) = 60-85% range)")
    print("3. Large turnover time standard deviations")
    print("4. Profit margin variation adds multiplicative uncertainty")
    print("5. All uncertainties compound multiplicatively")
    print("\nRealistic assumptions should produce 2-3x range instead of 10x range.")