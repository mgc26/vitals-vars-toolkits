#!/usr/bin/env python3
"""
Monte Carlo Simulation for Virtual Healthcare Avatar ROI
Runs 10,000 simulations to provide robust statistical analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, List
import json
from datetime import datetime

class MonteCarloROISimulator:
    """
    Sophisticated Monte Carlo simulator for avatar deployment ROI analysis
    Uses realistic probability distributions based on empirical evidence
    """
    
    def __init__(self, n_simulations: int = 10000):
        """
        Initialize simulator with parameters from systematic review
        
        Args:
            n_simulations: Number of Monte Carlo iterations
        """
        self.n_simulations = n_simulations
        np.random.seed(42)  # For reproducibility
        self.results = None
        
        # Evidence-based parameter distributions
        self.cost_params = {
            'implementation': {'low': 150000, 'mode': 200000, 'high': 300000},
            'monthly_operating': {'low': 20000, 'mode': 24750, 'high': 35000},
            'per_interaction': {'mean': 0.0124, 'std': 0.003}
        }
        
        self.benefit_params = {
            'readmission_reduction': {'mean': 0.30, 'std': 0.08, 'min': 0.10, 'max': 0.50},
            'nurse_time_saved': {'mean': 2.5, 'std': 0.5, 'min': 1.0, 'max': 4.0},
            'patient_satisfaction': {'mean': 0.15, 'std': 0.05, 'min': 0, 'max': 0.30},
            'medication_adherence': {'mean': 0.22, 'std': 0.06, 'min': 0.10, 'max': 0.40}
        }
        
        self.volume_params = {
            'monthly_interactions': {'shape': 2, 'scale': 1000},  # Gamma distribution
            'adoption_rate': {'alpha': 2, 'beta': 5},  # Beta distribution
        }
        
    def run_simulation(self, use_case: str = 'discharge_education') -> pd.DataFrame:
        """
        Run Monte Carlo simulation for specified use case
        
        Args:
            use_case: One of 'discharge_education', 'mental_health', 'medication_adherence'
            
        Returns:
            DataFrame with simulation results
        """
        results = []
        
        for i in range(self.n_simulations):
            # Sample from distributions
            costs = self._sample_costs()
            benefits = self._sample_benefits(use_case)
            volumes = self._sample_volumes()
            
            # Calculate financial metrics
            metrics = self._calculate_financial_metrics(costs, benefits, volumes)
            
            # Store results
            results.append({
                'simulation': i,
                'use_case': use_case,
                **costs,
                **benefits,
                **volumes,
                **metrics
            })
        
        self.results = pd.DataFrame(results)
        return self.results
    
    def _sample_costs(self) -> Dict:
        """Sample from cost distributions"""
        return {
            'implementation_cost': np.random.triangular(
                self.cost_params['implementation']['low'],
                self.cost_params['implementation']['mode'],
                self.cost_params['implementation']['high']
            ),
            'monthly_operating_cost': np.random.triangular(
                self.cost_params['monthly_operating']['low'],
                self.cost_params['monthly_operating']['mode'],
                self.cost_params['monthly_operating']['high']
            ),
            'cost_per_interaction': np.random.normal(
                self.cost_params['per_interaction']['mean'],
                self.cost_params['per_interaction']['std']
            )
        }
    
    def _sample_benefits(self, use_case: str) -> Dict:
        """Sample from benefit distributions based on use case"""
        benefits = {}
        
        if use_case == 'discharge_education':
            benefits['readmission_reduction'] = np.clip(
                np.random.normal(
                    self.benefit_params['readmission_reduction']['mean'],
                    self.benefit_params['readmission_reduction']['std']
                ),
                self.benefit_params['readmission_reduction']['min'],
                self.benefit_params['readmission_reduction']['max']
            )
            benefits['readmissions_prevented'] = np.random.poisson(30)
            
        elif use_case == 'mental_health':
            benefits['therapy_sessions_saved'] = np.random.poisson(100)
            benefits['cost_per_therapy_session'] = np.random.normal(180, 30)
            
        elif use_case == 'medication_adherence':
            benefits['adherence_improvement'] = np.clip(
                np.random.normal(
                    self.benefit_params['medication_adherence']['mean'],
                    self.benefit_params['medication_adherence']['std']
                ),
                self.benefit_params['medication_adherence']['min'],
                self.benefit_params['medication_adherence']['max']
            )
            benefits['patients_enrolled'] = np.random.poisson(200)
        
        # Common benefits
        benefits['nurse_time_saved_hours'] = np.clip(
            np.random.normal(
                self.benefit_params['nurse_time_saved']['mean'],
                self.benefit_params['nurse_time_saved']['std']
            ),
            self.benefit_params['nurse_time_saved']['min'],
            self.benefit_params['nurse_time_saved']['max']
        )
        
        benefits['patient_satisfaction_increase'] = np.clip(
            np.random.normal(
                self.benefit_params['patient_satisfaction']['mean'],
                self.benefit_params['patient_satisfaction']['std']
            ),
            self.benefit_params['patient_satisfaction']['min'],
            self.benefit_params['patient_satisfaction']['max']
        )
        
        return benefits
    
    def _sample_volumes(self) -> Dict:
        """Sample from volume distributions"""
        return {
            'monthly_interactions': np.random.gamma(
                self.volume_params['monthly_interactions']['shape'],
                self.volume_params['monthly_interactions']['scale']
            ),
            'adoption_rate': np.random.beta(
                self.volume_params['adoption_rate']['alpha'],
                self.volume_params['adoption_rate']['beta']
            )
        }
    
    def _calculate_financial_metrics(self, costs: Dict, benefits: Dict, volumes: Dict) -> Dict:
        """Calculate key financial metrics"""
        # Annual costs
        annual_implementation = costs['implementation_cost'] / 3  # 3-year amortization
        annual_operating = costs['monthly_operating_cost'] * 12
        annual_per_interaction = costs['cost_per_interaction'] * volumes['monthly_interactions'] * 12
        total_annual_cost = annual_implementation + annual_operating + annual_per_interaction
        
        # Annual benefits (varies by use case)
        if 'readmission_reduction' in benefits:
            readmission_savings = benefits.get('readmissions_prevented', 30) * 14000
        else:
            readmission_savings = 0
            
        if 'therapy_sessions_saved' in benefits:
            therapy_savings = benefits['therapy_sessions_saved'] * benefits.get('cost_per_therapy_session', 180) * 12
        else:
            therapy_savings = 0
            
        if 'adherence_improvement' in benefits:
            adherence_savings = benefits['adherence_improvement'] * benefits.get('patients_enrolled', 200) * 4000
        else:
            adherence_savings = 0
        
        # Labor savings
        labor_savings = benefits['nurse_time_saved_hours'] * 250 * 8 * 65  # Hours * days * shifts * hourly rate
        
        # Patient satisfaction impact (estimated as revenue impact)
        satisfaction_revenue = benefits['patient_satisfaction_increase'] * 0.02 * 50000000
        
        # Total benefits
        total_annual_benefit = (
            readmission_savings + 
            therapy_savings + 
            adherence_savings +
            labor_savings + 
            satisfaction_revenue
        )
        
        # Calculate metrics
        roi = (total_annual_benefit - total_annual_cost) / total_annual_cost * 100 if total_annual_cost > 0 else 0
        
        net_monthly_benefit = (total_annual_benefit - total_annual_cost) / 12
        payback_months = costs['implementation_cost'] / net_monthly_benefit if net_monthly_benefit > 0 else 999
        
        # NPV calculation (3-year, 8% discount rate)
        npv = self._calculate_npv(
            costs['implementation_cost'],
            total_annual_benefit,
            annual_operating + annual_per_interaction,
            discount_rate=0.08,
            years=3
        )
        
        return {
            'total_annual_cost': total_annual_cost,
            'total_annual_benefit': total_annual_benefit,
            'net_annual_benefit': total_annual_benefit - total_annual_cost,
            'roi_percent': roi,
            'payback_months': min(payback_months, 999),  # Cap at 999 for outliers
            'npv_3_year': npv,
            'benefit_cost_ratio': total_annual_benefit / total_annual_cost if total_annual_cost > 0 else 0
        }
    
    def _calculate_npv(self, initial_cost: float, annual_benefit: float, 
                      annual_cost: float, discount_rate: float = 0.08, years: int = 3) -> float:
        """Calculate Net Present Value"""
        cash_flows = [-initial_cost]
        
        for year in range(1, years + 1):
            net_cash_flow = annual_benefit - annual_cost
            discounted = net_cash_flow / (1 + discount_rate) ** year
            cash_flows.append(discounted)
        
        return sum(cash_flows)
    
    def get_statistics(self) -> Dict:
        """Calculate comprehensive statistics from simulation results"""
        if self.results is None:
            raise ValueError("Run simulation first")
        
        stats = {
            'roi': {
                'mean': self.results['roi_percent'].mean(),
                'median': self.results['roi_percent'].median(),
                'std': self.results['roi_percent'].std(),
                'ci_95_lower': self.results['roi_percent'].quantile(0.025),
                'ci_95_upper': self.results['roi_percent'].quantile(0.975),
                'probability_positive': (self.results['roi_percent'] > 0).mean(),
                'probability_over_100': (self.results['roi_percent'] > 100).mean(),
                'probability_over_150': (self.results['roi_percent'] > 150).mean(),
                'probability_over_200': (self.results['roi_percent'] > 200).mean(),
            },
            'payback': {
                'mean': self.results[self.results['payback_months'] < 999]['payback_months'].mean(),
                'median': self.results['payback_months'].median(),
                'ci_95_lower': self.results['payback_months'].quantile(0.025),
                'ci_95_upper': self.results['payback_months'].quantile(0.975),
                'probability_under_12': (self.results['payback_months'] < 12).mean(),
                'probability_under_18': (self.results['payback_months'] < 18).mean(),
                'probability_under_24': (self.results['payback_months'] < 24).mean(),
            },
            'npv': {
                'mean': self.results['npv_3_year'].mean(),
                'median': self.results['npv_3_year'].median(),
                'std': self.results['npv_3_year'].std(),
                'ci_95_lower': self.results['npv_3_year'].quantile(0.025),
                'ci_95_upper': self.results['npv_3_year'].quantile(0.975),
                'probability_positive': (self.results['npv_3_year'] > 0).mean(),
                'probability_over_500k': (self.results['npv_3_year'] > 500000).mean(),
                'probability_over_1m': (self.results['npv_3_year'] > 1000000).mean(),
            },
            'benefit_cost_ratio': {
                'mean': self.results['benefit_cost_ratio'].mean(),
                'median': self.results['benefit_cost_ratio'].median(),
                'probability_over_2': (self.results['benefit_cost_ratio'] > 2).mean(),
            }
        }
        
        return stats
    
    def create_visualizations(self, output_dir: str = './'):
        """Create visualization plots for the simulation results"""
        if self.results is None:
            raise ValueError("Run simulation first")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # ROI Distribution
        ax1 = axes[0, 0]
        ax1.hist(self.results['roi_percent'], bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(self.results['roi_percent'].median(), color='red', linestyle='--', label=f'Median: {self.results["roi_percent"].median():.1f}%')
        ax1.axvline(100, color='green', linestyle='--', label='Break-even (100%)')
        ax1.set_xlabel('ROI (%)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('ROI Distribution (n=10,000 simulations)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Payback Period Distribution
        ax2 = axes[0, 1]
        payback_filtered = self.results[self.results['payback_months'] < 60]  # Filter outliers
        ax2.hist(payback_filtered['payback_months'], bins=50, alpha=0.7, color='green', edgecolor='black')
        ax2.axvline(payback_filtered['payback_months'].median(), color='red', linestyle='--', 
                   label=f'Median: {payback_filtered["payback_months"].median():.1f} months')
        ax2.axvline(18, color='orange', linestyle='--', label='18-month target')
        ax2.set_xlabel('Payback Period (months)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Payback Period Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # NPV Distribution
        ax3 = axes[1, 0]
        ax3.hist(self.results['npv_3_year']/1000000, bins=50, alpha=0.7, color='purple', edgecolor='black')
        ax3.axvline(self.results['npv_3_year'].median()/1000000, color='red', linestyle='--', 
                   label=f'Median: ${self.results["npv_3_year"].median()/1000000:.2f}M')
        ax3.axvline(0, color='black', linestyle='-', label='Break-even')
        ax3.set_xlabel('3-Year NPV ($M)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Net Present Value Distribution (3-year)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Tornado diagram for sensitivity
        ax4 = axes[1, 1]
        sensitivities = self._calculate_sensitivities()
        y_pos = np.arange(len(sensitivities))
        ax4.barh(y_pos, [s['impact'] for s in sensitivities], color=['red' if s['impact'] < 0 else 'green' for s in sensitivities])
        ax4.set_yticks(y_pos)
        ax4.set_yticklabels([s['parameter'] for s in sensitivities])
        ax4.set_xlabel('Impact on ROI (%)')
        ax4.set_title('Sensitivity Analysis: Key Drivers')
        ax4.grid(True, alpha=0.3, axis='x')
        
        plt.suptitle('Monte Carlo Simulation Results: Virtual Healthcare Avatars', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save figure
        plt.savefig(f'{output_dir}/monte_carlo_results.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig
    
    def _calculate_sensitivities(self) -> List[Dict]:
        """Calculate parameter sensitivities"""
        if self.results is None:
            return []
        
        # Calculate correlations with ROI
        sensitivities = []
        
        for col in self.results.columns:
            if col not in ['simulation', 'use_case', 'roi_percent', 'npv_3_year', 'payback_months']:
                correlation = self.results[col].corr(self.results['roi_percent'])
                if abs(correlation) > 0.1:  # Only include meaningful correlations
                    sensitivities.append({
                        'parameter': col.replace('_', ' ').title(),
                        'correlation': correlation,
                        'impact': correlation * 100  # Scale for visualization
                    })
        
        # Sort by absolute impact
        sensitivities.sort(key=lambda x: abs(x['impact']), reverse=True)
        
        return sensitivities[:10]  # Top 10 drivers
    
    def export_results(self, filename: str = 'monte_carlo_results.json'):
        """Export results to JSON for documentation"""
        if self.results is None:
            raise ValueError("Run simulation first")
        
        stats = self.get_statistics()
        
        export_data = {
            'metadata': {
                'simulation_date': datetime.now().isoformat(),
                'n_simulations': self.n_simulations,
                'random_seed': 42
            },
            'statistics': stats,
            'summary': {
                'roi_mean': f"{stats['roi']['mean']:.1f}%",
                'roi_median': f"{stats['roi']['median']:.1f}%",
                'roi_95_ci': f"[{stats['roi']['ci_95_lower']:.1f}%, {stats['roi']['ci_95_upper']:.1f}%]",
                'probability_positive_roi': f"{stats['roi']['probability_positive']:.1%}",
                'payback_median': f"{stats['payback']['median']:.1f} months",
                'npv_median': f"${stats['npv']['median']:,.0f}",
                'probability_npv_over_1m': f"{stats['npv']['probability_over_1m']:.1%}"
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return export_data
    
    def export_to_csv(self, prefix: str = 'monte_carlo'):
        """Export raw simulation data to CSV files"""
        if self.results is None:
            raise ValueError("Run simulation first")
        
        # Export full raw data
        raw_filename = f'{prefix}_raw_data.csv'
        self.results.to_csv(raw_filename, index=False)
        print(f"✓ Raw simulation data exported to {raw_filename}")
        
        # Export summary statistics
        summary_data = []
        for metric in ['roi_percent', 'payback_months', 'npv_3_year', 'benefit_cost_ratio']:
            summary_data.append({
                'metric': metric,
                'mean': self.results[metric].mean(),
                'median': self.results[metric].median(),
                'std': self.results[metric].std(),
                'min': self.results[metric].min(),
                'max': self.results[metric].max(),
                'q25': self.results[metric].quantile(0.25),
                'q75': self.results[metric].quantile(0.75),
                'ci_95_lower': self.results[metric].quantile(0.025),
                'ci_95_upper': self.results[metric].quantile(0.975)
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_filename = f'{prefix}_summary_stats.csv'
        summary_df.to_csv(summary_filename, index=False)
        print(f"✓ Summary statistics exported to {summary_filename}")
        
        # Export percentile distribution
        percentiles = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
        percentile_data = []
        
        for p in percentiles:
            percentile_data.append({
                'percentile': f"{int(p*100)}th",
                'roi_percent': self.results['roi_percent'].quantile(p),
                'payback_months': self.results['payback_months'].quantile(p),
                'npv_3_year': self.results['npv_3_year'].quantile(p),
                'benefit_cost_ratio': self.results['benefit_cost_ratio'].quantile(p)
            })
        
        percentile_df = pd.DataFrame(percentile_data)
        percentile_filename = f'{prefix}_percentiles.csv'
        percentile_df.to_csv(percentile_filename, index=False)
        print(f"✓ Percentile distribution exported to {percentile_filename}")
        
        return raw_filename, summary_filename, percentile_filename


def run_complete_analysis():
    """Run complete Monte Carlo analysis for all use cases"""
    print("="*60)
    print("MONTE CARLO SIMULATION: Virtual Healthcare Avatars")
    print("="*60)
    
    simulator = MonteCarloROISimulator(n_simulations=10000)
    
    # Run for primary use case
    print("\nRunning simulation for Discharge Education use case...")
    results = simulator.run_simulation('discharge_education')
    stats = simulator.get_statistics()
    
    print("\nMONTE CARLO SIMULATION RESULTS (n=10,000)")
    print("-"*60)
    
    print(f"\nROI Distribution:")
    print(f"  Mean ROI: {stats['roi']['mean']:.1f}%")
    print(f"  Median ROI: {stats['roi']['median']:.1f}%")
    print(f"  Standard Deviation: {stats['roi']['std']:.1f}%")
    print(f"  95% CI: [{stats['roi']['ci_95_lower']:.1f}%, {stats['roi']['ci_95_upper']:.1f}%]")
    print(f"  Probability ROI > 0%: {stats['roi']['probability_positive']:.1%}")
    print(f"  Probability ROI > 100%: {stats['roi']['probability_over_100']:.1%}")
    print(f"  Probability ROI > 150%: {stats['roi']['probability_over_150']:.1%}")
    print(f"  Probability ROI > 200%: {stats['roi']['probability_over_200']:.1%}")
    
    print(f"\nPayback Period:")
    print(f"  Mean: {stats['payback']['mean']:.1f} months")
    print(f"  Median: {stats['payback']['median']:.1f} months")
    print(f"  95% CI: [{stats['payback']['ci_95_lower']:.1f}, {stats['payback']['ci_95_upper']:.1f}] months")
    print(f"  Probability < 12 months: {stats['payback']['probability_under_12']:.1%}")
    print(f"  Probability < 18 months: {stats['payback']['probability_under_18']:.1%}")
    print(f"  Probability < 24 months: {stats['payback']['probability_under_24']:.1%}")
    
    print(f"\n3-Year Net Present Value:")
    print(f"  Mean: ${stats['npv']['mean']:,.0f}")
    print(f"  Median: ${stats['npv']['median']:,.0f}")
    print(f"  Standard Deviation: ${stats['npv']['std']:,.0f}")
    print(f"  95% CI: [${stats['npv']['ci_95_lower']:,.0f}, ${stats['npv']['ci_95_upper']:,.0f}]")
    print(f"  Probability NPV > $0: {stats['npv']['probability_positive']:.1%}")
    print(f"  Probability NPV > $500K: {stats['npv']['probability_over_500k']:.1%}")
    print(f"  Probability NPV > $1M: {stats['npv']['probability_over_1m']:.1%}")
    
    print(f"\nBenefit-Cost Ratio:")
    print(f"  Mean: {stats['benefit_cost_ratio']['mean']:.2f}")
    print(f"  Median: {stats['benefit_cost_ratio']['median']:.2f}")
    print(f"  Probability BCR > 2.0: {stats['benefit_cost_ratio']['probability_over_2']:.1%}")
    
    # Export results
    export_data = simulator.export_results()
    print(f"\n✓ Results exported to monte_carlo_results.json")
    
    # Export CSV files
    print("\nExporting raw data to CSV files...")
    csv_files = simulator.export_to_csv()
    
    # Create visualizations
    print("\nGenerating visualizations...")
    # Note: Visualization disabled for command-line execution
    # Uncomment the line below to generate plots when running interactively:
    # simulator.create_visualizations()
    
    return simulator, stats


if __name__ == '__main__':
    simulator, stats = run_complete_analysis()
    print("\n" + "="*60)
    print("Simulation complete. Results available for analysis.")
    print("="*60)