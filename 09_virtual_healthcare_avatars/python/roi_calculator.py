#!/usr/bin/env python3
"""
Virtual Healthcare Avatar ROI Calculator
Calculates return on investment for different avatar deployment scenarios
Based on evidence from 49 real-world implementations
"""

import argparse
import numpy as np
import pandas as pd
from typing import Dict, Tuple
import json

class AvatarROICalculator:
    """Calculate ROI for virtual healthcare avatar implementations"""
    
    # Evidence-based parameters from systematic review
    USE_CASE_PARAMS = {
        'mental_health': {
            'success_rate': 0.73,  # 73% completion rate
            'cost_per_session': 180,  # Traditional therapy cost
            'avatar_cost_per_session': 15,  # Avatar session cost
            'sessions_per_patient': 8,  # Typical CBT course
            'effect_size': 0.44,  # Cohen's d from meta-analysis
            'implementation_months': 6,
            'monthly_volume_per_100_beds': 40
        },
        'discharge_education': {
            'baseline_readmission_rate': 0.18,  # 18% baseline
            'readmission_reduction': 0.30,  # 30% reduction
            'cost_per_readmission': 14000,  # Average readmission cost
            'avatar_cost_per_patient': 25,
            'implementation_months': 8,
            'monthly_volume_per_100_beds': 150
        },
        'medication_adherence': {
            'baseline_adherence': 0.60,  # 60% baseline PDC
            'adherence_improvement': 0.22,  # 22% improvement
            'annual_cost_nonadherence': 4000,  # Per patient per year
            'avatar_monthly_cost': 12,  # Per patient per month
            'implementation_months': 6,
            'monthly_volume_per_100_beds': 200
        }
    }
    
    # Implementation cost structure
    IMPLEMENTATION_COSTS = {
        'licensing': {
            'base_annual': 50000,
            'per_interaction': 5
        },
        'integration': {
            'ehr_integration': 75000,
            'data_warehouse': 25000,
            'testing_validation': 30000
        },
        'operations': {
            'training_hours': 40,
            'hourly_rate': 75,
            'ongoing_support_monthly': 5000
        }
    }
    
    def __init__(self, hospital_beds: int = 300):
        """Initialize calculator with hospital size"""
        self.hospital_beds = hospital_beds
        self.bed_multiplier = hospital_beds / 100
        
    def calculate_use_case_roi(self, 
                               use_case: str,
                               months: int = 36,
                               custom_volume: float = None,
                               uncertainty_analysis: bool = True,
                               patient_mix_adjustment: bool = True) -> Dict:
        """Calculate ROI for a specific use case with uncertainty quantification"""
        
        if use_case not in self.USE_CASE_PARAMS:
            raise ValueError(f"Unknown use case: {use_case}")
            
        params = self.USE_CASE_PARAMS[use_case]
        
        # Calculate monthly patient volume
        if custom_volume:
            monthly_volume = custom_volume
        else:
            monthly_volume = params['monthly_volume_per_100_beds'] * self.bed_multiplier
            
        # Implementation timeline
        impl_months = params['implementation_months']
        operational_months = max(0, months - impl_months)
        
        # Calculate base costs and savings
        upfront_costs = self._calculate_implementation_costs(use_case)
        operating_costs = self._calculate_operating_costs(
            use_case, monthly_volume, operational_months
        )
        total_costs = upfront_costs + operating_costs
        
        # Calculate base savings
        if use_case == 'mental_health':
            base_savings = self._calculate_mental_health_savings(
                params, monthly_volume, operational_months
            )
        elif use_case == 'discharge_education':
            base_savings = self._calculate_discharge_savings(
                params, monthly_volume, operational_months
            )
        else:  # medication_adherence
            base_savings = self._calculate_adherence_savings(
                params, monthly_volume, operational_months
            )
        
        # Apply patient mix adjustment if requested
        if patient_mix_adjustment:
            mix_factor = self._calculate_patient_mix_factor(use_case)
            adjusted_savings = base_savings * mix_factor
        else:
            adjusted_savings = base_savings
            mix_factor = 1.0
            
        # Uncertainty analysis using Monte Carlo simulation
        if uncertainty_analysis:
            uncertainty_results = self._monte_carlo_uncertainty(
                use_case, monthly_volume, operational_months, 
                upfront_costs, operating_costs, adjusted_savings
            )
        else:
            uncertainty_results = {
                'confidence_intervals': {},
                'risk_metrics': {},
                'scenario_analysis': {}
            }
            
        # Calculate point estimates
        net_benefit = adjusted_savings - total_costs
        roi_percentage = (net_benefit / total_costs * 100) if total_costs > 0 else 0
        
        # Find break-even month with uncertainty
        break_even_month = self._find_break_even(
            upfront_costs, params, monthly_volume
        )
        
        # Risk-adjusted NPV calculation
        risk_adjusted_npv = self._calculate_risk_adjusted_npv(
            total_costs, adjusted_savings, months, use_case
        )
        
        return {
            'use_case': use_case,
            'total_months': months,
            'operational_months': operational_months,
            'monthly_patient_volume': monthly_volume,
            'total_patients': monthly_volume * operational_months,
            'implementation_costs': upfront_costs,
            'operating_costs': operating_costs,
            'total_costs': total_costs,
            'base_savings': base_savings,
            'patient_mix_factor': mix_factor,
            'adjusted_savings': adjusted_savings,
            'net_benefit': net_benefit,
            'roi_percentage': roi_percentage,
            'risk_adjusted_npv': risk_adjusted_npv,
            'break_even_month': break_even_month,
            'cost_per_patient': total_costs / (monthly_volume * operational_months) if operational_months > 0 else 0,
            'savings_per_patient': adjusted_savings / (monthly_volume * operational_months) if operational_months > 0 else 0,
            'uncertainty_analysis': uncertainty_results,
            'statistical_power': self._calculate_statistical_power(monthly_volume * operational_months, use_case),
            'confidence_intervals': self._calculate_confidence_intervals(
                net_benefit, total_costs, monthly_volume * operational_months
            )
        }
    
    def _calculate_implementation_costs(self, use_case: str) -> float:
        """Calculate one-time implementation costs"""
        costs = self.IMPLEMENTATION_COSTS
        
        # Base implementation
        impl_cost = (
            costs['integration']['ehr_integration'] +
            costs['integration']['data_warehouse'] +
            costs['integration']['testing_validation']
        )
        
        # Training costs (scale with hospital size)
        training_cost = (
            costs['operations']['training_hours'] *
            costs['operations']['hourly_rate'] *
            (self.hospital_beds / 100)  # Scale training with size
        )
        
        return impl_cost + training_cost
        
    def _calculate_operating_costs(self, 
                                   use_case: str,
                                   monthly_volume: float,
                                   months: int) -> float:
        """Calculate ongoing operating costs"""
        costs = self.IMPLEMENTATION_COSTS
        params = self.USE_CASE_PARAMS[use_case]
        
        # Licensing costs
        annual_licensing = costs['licensing']['base_annual']
        monthly_licensing = annual_licensing / 12
        
        # Per-interaction costs
        if 'avatar_cost_per_session' in params:
            interaction_cost = params['avatar_cost_per_session']
        elif 'avatar_cost_per_patient' in params:
            interaction_cost = params['avatar_cost_per_patient']
        else:
            interaction_cost = params['avatar_monthly_cost']
            
        monthly_interaction_costs = monthly_volume * interaction_cost
        
        # Support costs
        monthly_support = costs['operations']['ongoing_support_monthly']
        
        # Total monthly operating cost
        monthly_total = monthly_licensing + monthly_interaction_costs + monthly_support
        
        return monthly_total * months
        
    def _calculate_mental_health_savings(self,
                                        params: Dict,
                                        monthly_volume: float,
                                        months: int) -> float:
        """Calculate savings for mental health use case"""
        sessions_per_patient = params['sessions_per_patient']
        traditional_cost = params['cost_per_session']
        avatar_cost = params['avatar_cost_per_session']
        success_rate = params['success_rate']
        
        # Savings per successful completion
        savings_per_patient = (
            (traditional_cost - avatar_cost) * sessions_per_patient * success_rate
        )
        
        return savings_per_patient * monthly_volume * months
        
    def _calculate_discharge_savings(self,
                                    params: Dict,
                                    monthly_volume: float,
                                    months: int) -> float:
        """Calculate savings for discharge education use case"""
        baseline_rate = params['baseline_readmission_rate']
        reduction = params['readmission_reduction']
        cost_per_readmission = params['cost_per_readmission']
        
        # Readmissions prevented
        prevented_readmissions = (
            monthly_volume * baseline_rate * reduction
        )
        
        return prevented_readmissions * cost_per_readmission * months
        
    def _calculate_adherence_savings(self,
                                    params: Dict,
                                    monthly_volume: float,
                                    months: int) -> float:
        """Calculate savings for medication adherence use case"""
        improvement = params['adherence_improvement']
        annual_cost = params['annual_cost_nonadherence']
        
        # Annual savings per patient
        annual_savings_per_patient = annual_cost * improvement
        monthly_savings_per_patient = annual_savings_per_patient / 12
        
        return monthly_savings_per_patient * monthly_volume * months
        
    def _find_break_even(self,
                        upfront_costs: float,
                        params: Dict,
                        monthly_volume: float) -> int:
        """Find break-even month"""
        cumulative_cost = upfront_costs
        cumulative_savings = 0
        
        for month in range(1, 61):  # Check up to 5 years
            # Add monthly operating costs
            if month > params['implementation_months']:
                operational_months = 1
                monthly_cost = self._calculate_operating_costs(
                    list(self.USE_CASE_PARAMS.keys())[0],  # Simplified
                    monthly_volume,
                    1
                )
                cumulative_cost += monthly_cost
                
                # Add monthly savings
                if 'cost_per_session' in params:
                    monthly_savings = self._calculate_mental_health_savings(
                        params, monthly_volume, 1
                    )
                elif 'baseline_readmission_rate' in params:
                    monthly_savings = self._calculate_discharge_savings(
                        params, monthly_volume, 1
                    )
                else:
                    monthly_savings = self._calculate_adherence_savings(
                        params, monthly_volume, 1
                    )
                    
                cumulative_savings += monthly_savings
                
                if cumulative_savings >= cumulative_cost:
                    return month
                    
        return -1  # No break-even within 5 years
        
    def calculate_portfolio_roi(self,
                               use_cases: list,
                               months: int = 36) -> Dict:
        """Calculate ROI for portfolio of use cases"""
        total_costs = 0
        total_savings = 0
        results = []
        
        for use_case in use_cases:
            roi = self.calculate_use_case_roi(use_case, months)
            results.append(roi)
            total_costs += roi['total_costs']
            total_savings += roi['total_savings']
            
        portfolio_roi = {
            'use_cases': use_cases,
            'individual_results': results,
            'total_costs': total_costs,
            'total_savings': total_savings,
            'net_benefit': total_savings - total_costs,
            'portfolio_roi_percentage': (total_savings - total_costs) / total_costs * 100 if total_costs > 0 else 0,
            'average_break_even': np.mean([r['break_even_month'] for r in results if r['break_even_month'] > 0])
        }
        
        return portfolio_roi
        
    def sensitivity_analysis(self,
                            use_case: str,
                            parameter: str,
                            variations: list = None) -> pd.DataFrame:
        """Perform sensitivity analysis on key parameters"""
        if variations is None:
            variations = [0.5, 0.75, 1.0, 1.25, 1.5]
            
        results = []
        base_roi = self.calculate_use_case_roi(use_case)
        base_value = self.USE_CASE_PARAMS[use_case].get(parameter, 1.0)
        
        for variation in variations:
            # Temporarily modify parameter
            original = self.USE_CASE_PARAMS[use_case][parameter]
            self.USE_CASE_PARAMS[use_case][parameter] = base_value * variation
            
            # Calculate ROI
            roi = self.calculate_use_case_roi(use_case)
            
            results.append({
                'variation': variation,
                'parameter_value': base_value * variation,
                'roi_percentage': roi['roi_percentage'],
                'net_benefit': roi['net_benefit'],
                'break_even_month': roi['break_even_month']
            })
            
            # Restore original value
            self.USE_CASE_PARAMS[use_case][parameter] = original
            
        return pd.DataFrame(results)
    
    def _calculate_patient_mix_factor(self, use_case: str) -> float:
        """Adjust savings based on patient population characteristics"""
        # Evidence-based adjustment factors
        mix_factors = {
            'mental_health': {
                'high_acuity': 0.85,    # More complex patients, lower success
                'low_health_literacy': 0.75,
                'elderly_population': 0.70,
                'baseline': 1.0
            },
            'discharge_education': {
                'high_readmission_risk': 1.25,  # Higher baseline risk, more opportunity
                'complex_conditions': 0.90,
                'social_determinants': 0.80,
                'baseline': 1.0
            },
            'medication_adherence': {
                'polypharmacy': 0.85,  # More complex regimens harder to improve
                'depression_comorbid': 0.75,
                'high_cost_medications': 1.15,
                'baseline': 1.0
            }
        }
        
        # Simplified - would use actual patient data in practice
        return mix_factors.get(use_case, {}).get('baseline', 1.0)
    
    def _monte_carlo_uncertainty(self, use_case: str, monthly_volume: float,
                                operational_months: int, upfront_costs: float,
                                operating_costs: float, base_savings: float,
                                n_simulations: int = 1000) -> Dict:
        """Perform Monte Carlo uncertainty analysis"""
        
        # Define uncertainty distributions for key parameters
        # Implementation cost variation: +/- 25%
        impl_cost_samples = np.random.normal(upfront_costs, upfront_costs * 0.25, n_simulations)
        
        # Effectiveness variation based on use case
        if use_case == 'mental_health':
            # Effect size uncertainty: Cohen's d = 0.44 ± 0.15
            effect_samples = np.random.normal(0.44, 0.15, n_simulations)
            effect_samples = np.clip(effect_samples, 0, 1)  # Reasonable bounds
        elif use_case == 'discharge_education':
            # Readmission reduction: 30% ± 10%
            reduction_samples = np.random.normal(0.30, 0.10, n_simulations)
            reduction_samples = np.clip(reduction_samples, 0, 0.6)
            effect_samples = reduction_samples
        else:  # medication_adherence
            # PDC improvement: 22% ± 8%
            improvement_samples = np.random.normal(0.22, 0.08, n_simulations)
            improvement_samples = np.clip(improvement_samples, 0, 0.5)
            effect_samples = improvement_samples
        
        # Volume uncertainty: ±20%
        volume_samples = np.random.normal(monthly_volume, monthly_volume * 0.2, n_simulations)
        volume_samples = np.maximum(volume_samples, 0)  # Cannot be negative
        
        # Calculate ROI for each simulation
        roi_samples = []
        net_benefit_samples = []
        
        for i in range(n_simulations):
            # Adjust savings based on effectiveness sample
            if use_case == 'mental_health':
                # Scale savings by effect size ratio
                effect_ratio = effect_samples[i] / 0.44  # Baseline effect
                sim_savings = base_savings * effect_ratio
            elif use_case == 'discharge_education':
                # Scale by readmission reduction
                reduction_ratio = effect_samples[i] / 0.30
                sim_savings = base_savings * reduction_ratio
            else:  # medication_adherence
                improvement_ratio = effect_samples[i] / 0.22
                sim_savings = base_savings * improvement_ratio
            
            # Adjust for volume variation
            volume_ratio = volume_samples[i] / monthly_volume
            sim_savings *= volume_ratio
            sim_operating_costs = operating_costs * volume_ratio
            
            sim_total_costs = impl_cost_samples[i] + sim_operating_costs
            sim_net_benefit = sim_savings - sim_total_costs
            sim_roi = (sim_net_benefit / sim_total_costs * 100) if sim_total_costs > 0 else -100
            
            roi_samples.append(sim_roi)
            net_benefit_samples.append(sim_net_benefit)
        
        roi_samples = np.array(roi_samples)
        net_benefit_samples = np.array(net_benefit_samples)
        
        # Calculate summary statistics
        return {
            'confidence_intervals': {
                'roi_5th_percentile': np.percentile(roi_samples, 5),
                'roi_95th_percentile': np.percentile(roi_samples, 95),
                'roi_median': np.median(roi_samples),
                'net_benefit_5th': np.percentile(net_benefit_samples, 5),
                'net_benefit_95th': np.percentile(net_benefit_samples, 95),
                'net_benefit_median': np.median(net_benefit_samples)
            },
            'risk_metrics': {
                'probability_positive_roi': np.mean(roi_samples > 0),
                'probability_breakeven': np.mean(net_benefit_samples > 0),
                'value_at_risk_5pct': np.percentile(net_benefit_samples, 5),
                'expected_value': np.mean(net_benefit_samples)
            },
            'scenario_analysis': {
                'pessimistic_roi': np.percentile(roi_samples, 10),
                'optimistic_roi': np.percentile(roi_samples, 90),
                'most_likely_roi': np.median(roi_samples)
            }
        }
    
    def _calculate_risk_adjusted_npv(self, total_costs: float, total_savings: float,
                                    months: int, use_case: str) -> float:
        """Calculate risk-adjusted NPV using healthcare-appropriate discount rate"""
        
        # Healthcare technology discount rates by risk profile
        discount_rates = {
            'mental_health': 0.12,      # 12% - moderate clinical risk
            'discharge_education': 0.10, # 10% - strong evidence base
            'medication_adherence': 0.08  # 8% - well-established intervention
        }
        
        annual_discount_rate = discount_rates.get(use_case, 0.10)
        monthly_discount_rate = annual_discount_rate / 12
        
        # Discount cash flows monthly
        monthly_net_cashflow = (total_savings - total_costs) / months if months > 0 else 0
        
        discounted_value = 0
        for month in range(1, months + 1):
            discount_factor = (1 + monthly_discount_rate) ** month
            discounted_value += monthly_net_cashflow / discount_factor
        
        return discounted_value
    
    def _calculate_statistical_power(self, total_patients: int, use_case: str) -> Dict:
        """Calculate statistical power for detecting claimed effect sizes"""
        
        # Effect sizes from literature
        effect_sizes = {
            'mental_health': 0.44,      # Cohen's d
            'discharge_education': 0.30,  # Proportion difference
            'medication_adherence': 0.22   # Proportion difference
        }
        
        effect_size = effect_sizes.get(use_case, 0.5)
        
        # Simplified power calculation (would use proper power analysis in practice)
        # Rule of thumb: need ~64 patients per group for d=0.5 with 80% power
        required_n = 128  # Total for two groups
        
        if use_case == 'mental_health':
            required_n = int(128 / (effect_size / 0.5))  # Adjust for actual effect size
        else:
            # For proportions, use different calculation
            required_n = int(200 / effect_size)  # Rough approximation
        
        actual_power = min(1.0, total_patients / required_n)
        
        return {
            'total_patients': total_patients,
            'required_patients': required_n,
            'statistical_power': actual_power,
            'adequately_powered': actual_power >= 0.8,
            'effect_size': effect_size
        }
    
    def _calculate_confidence_intervals(self, net_benefit: float, total_costs: float,
                                      total_patients: int) -> Dict:
        """Calculate confidence intervals for ROI estimates"""
        
        # Standard error estimation (simplified approach)
        if total_patients > 0:
            # Rule of thumb: SE decreases with sqrt(n)
            base_se_ratio = 0.25  # 25% standard error for small samples
            se_ratio = base_se_ratio / np.sqrt(total_patients / 100)
            
            se_net_benefit = abs(net_benefit) * se_ratio
            se_roi = abs(net_benefit / total_costs * 100) * se_ratio if total_costs > 0 else 0
        else:
            se_net_benefit = abs(net_benefit) * 0.5  # High uncertainty
            se_roi = 50  # High uncertainty in ROI
        
        # 95% confidence intervals
        roi_point = (net_benefit / total_costs * 100) if total_costs > 0 else 0
        
        return {
            'net_benefit_ci_lower': net_benefit - 1.96 * se_net_benefit,
            'net_benefit_ci_upper': net_benefit + 1.96 * se_net_benefit,
            'roi_ci_lower': roi_point - 1.96 * se_roi,
            'roi_ci_upper': roi_point + 1.96 * se_roi,
            'standard_error_net_benefit': se_net_benefit,
            'standard_error_roi': se_roi
        }


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description='Calculate ROI for virtual healthcare avatar implementations'
    )
    parser.add_argument(
        '--use-case',
        choices=['mental_health', 'discharge_education', 'medication_adherence', 'all'],
        default='discharge_education',
        help='Use case to analyze'
    )
    parser.add_argument(
        '--hospital-beds',
        type=int,
        default=300,
        help='Number of hospital beds'
    )
    parser.add_argument(
        '--months',
        type=int,
        default=36,
        help='Analysis period in months'
    )
    parser.add_argument(
        '--patient-volume',
        type=float,
        help='Monthly patient volume (overrides default)'
    )
    parser.add_argument(
        '--sensitivity',
        help='Run sensitivity analysis on parameter'
    )
    parser.add_argument(
        '--output',
        choices=['summary', 'detailed', 'json'],
        default='summary',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    # Initialize calculator
    calc = AvatarROICalculator(hospital_beds=args.hospital_beds)
    
    # Run calculations
    if args.use_case == 'all':
        result = calc.calculate_portfolio_roi(
            ['mental_health', 'discharge_education', 'medication_adherence'],
            months=args.months
        )
    else:
        result = calc.calculate_use_case_roi(
            args.use_case,
            months=args.months,
            custom_volume=args.patient_volume
        )
    
    # Output results
    if args.output == 'json':
        print(json.dumps(result, indent=2))
    elif args.output == 'detailed':
        print("\n" + "="*60)
        print(f"AVATAR ROI ANALYSIS: {args.use_case.upper()}")
        print("="*60)
        for key, value in result.items():
            if isinstance(value, float):
                if 'cost' in key or 'saving' in key or 'benefit' in key:
                    print(f"{key:.<40} ${value:,.0f}")
                elif 'percentage' in key:
                    print(f"{key:.<40} {value:.1f}%")
                else:
                    print(f"{key:.<40} {value:.1f}")
            elif key != 'individual_results':
                print(f"{key:.<40} {value}")
    else:  # summary
        print("\n" + "="*60)
        print(f"AVATAR ROI SUMMARY: {args.use_case.upper()}")
        print("="*60)
        print(f"Hospital Size:             {args.hospital_beds} beds")
        print(f"Analysis Period:           {args.months} months")
        if args.use_case != 'all':
            print(f"Monthly Patient Volume:    {result['monthly_patient_volume']:.0f}")
            print(f"Total Investment:          ${result['total_costs']:,.0f}")
            print(f"Total Savings:             ${result['total_savings']:,.0f}")
            print(f"Net Benefit:               ${result['net_benefit']:,.0f}")
            print(f"ROI:                       {result['roi_percentage']:.1f}%")
            print(f"Break-even Month:          {result['break_even_month']}")
        else:
            print(f"Portfolio Investment:      ${result['total_costs']:,.0f}")
            print(f"Portfolio Savings:         ${result['total_savings']:,.0f}")
            print(f"Portfolio Net Benefit:     ${result['net_benefit']:,.0f}")
            print(f"Portfolio ROI:             {result['portfolio_roi_percentage']:.1f}%")
            print(f"Average Break-even:        {result['average_break_even']:.0f} months")
    
    # Run sensitivity analysis if requested
    if args.sensitivity and args.use_case != 'all':
        print("\n" + "="*60)
        print(f"SENSITIVITY ANALYSIS: {args.sensitivity}")
        print("="*60)
        sensitivity_df = calc.sensitivity_analysis(args.use_case, args.sensitivity)
        print(sensitivity_df.to_string(index=False))


if __name__ == '__main__':
    main()