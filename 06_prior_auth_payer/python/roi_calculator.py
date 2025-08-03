#!/usr/bin/env python3
"""
Prior Authorization ROI Calculator
Calculates potential savings from PA automation initiatives
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class PriorAuthROICalculator:
    """Calculate ROI for prior authorization automation initiatives"""
    
    def __init__(self):
        # Cost per PA by method (based on CAQH 2023 data)
        self.costs = {
            'manual_fax': 14.49,
            'manual_phone': 14.49,
            'portal': 8.09,
            'electronic': 3.50,
            'api': 2.50,
            'ai_automated': 1.50
        }
        
        # Processing times in hours
        self.processing_times = {
            'manual_fax': 18.7,
            'manual_phone': 16.2,
            'portal': 8.5,
            'electronic': 5.7,
            'api': 2.1,
            'ai_automated': 0.5
        }
        
        # Appeal costs
        self.appeal_cost = 43.84
        
    def calculate_current_state(self, pa_volumes):
        """
        Calculate current PA processing costs
        
        Parameters:
        pa_volumes: dict with keys as methods and values as annual volumes
        """
        current_costs = {}
        total_cost = 0
        total_volume = 0
        
        for method, volume in pa_volumes.items():
            if method in self.costs:
                cost = volume * self.costs[method]
                current_costs[method] = {
                    'volume': volume,
                    'unit_cost': self.costs[method],
                    'total_cost': cost,
                    'processing_hours': volume * self.processing_times.get(method, 0)
                }
                total_cost += cost
                total_volume += volume
        
        current_costs['summary'] = {
            'total_volume': total_volume,
            'total_cost': total_cost,
            'average_cost': total_cost / total_volume if total_volume > 0 else 0
        }
        
        return current_costs
    
    def calculate_automation_scenario(self, current_volumes, automation_targets):
        """
        Calculate savings from automation
        
        Parameters:
        current_volumes: dict of current PA volumes by method
        automation_targets: dict with conversion percentages
        """
        future_volumes = current_volumes.copy()
        
        # Apply automation targets
        for source_method, conversions in automation_targets.items():
            if source_method in future_volumes:
                source_volume = current_volumes[source_method]
                
                for target_method, percentage in conversions.items():
                    conversion_volume = source_volume * percentage
                    future_volumes[source_method] -= conversion_volume
                    
                    if target_method not in future_volumes:
                        future_volumes[target_method] = 0
                    future_volumes[target_method] += conversion_volume
        
        # Calculate future state
        current_state = self.calculate_current_state(current_volumes)
        future_state = self.calculate_current_state(future_volumes)
        
        # Calculate savings
        savings = {
            'annual_cost_savings': current_state['summary']['total_cost'] - future_state['summary']['total_cost'],
            'cost_reduction_percentage': (1 - future_state['summary']['total_cost'] / current_state['summary']['total_cost']) * 100,
            'current_state': current_state,
            'future_state': future_state
        }
        
        return savings
    
    def calculate_gold_card_impact(self, provider_data):
        """
        Calculate savings from gold-carding providers
        
        Parameters:
        provider_data: DataFrame with columns [provider_id, annual_pas, approval_rate]
        """
        try:
            # Gold card criteria: 92% approval rate
            gold_card_threshold = 0.92
            
            # Validate input data
            required_columns = ['provider_id', 'annual_pas', 'approval_rate']
            if not all(col in provider_data.columns for col in required_columns):
                raise ValueError(f"Provider data must contain columns: {required_columns}")
            
            eligible_providers = provider_data[provider_data['approval_rate'] >= gold_card_threshold].copy()
        
        except Exception as e:
            print(f"Error in gold card calculation: {str(e)}")
            # Return empty results rather than crashing
            return {
                'eligible_providers': 0,
                'total_providers': len(provider_data) if 'provider_data' in locals() else 0,
                'eligible_percentage': 0,
                'eligible_pa_volume': 0,
                'total_pa_volume': 0,
                'annual_savings': 0,
                'providers_detail': pd.DataFrame()
            }
        
        # Calculate savings (manual to automated)
        eligible_providers['current_cost'] = eligible_providers['annual_pas'] * self.costs['manual_fax']
        eligible_providers['automated_cost'] = eligible_providers['annual_pas'] * self.costs['ai_automated']
        eligible_providers['savings'] = eligible_providers['current_cost'] - eligible_providers['automated_cost']
        
        summary = {
            'eligible_providers': len(eligible_providers),
            'total_providers': len(provider_data),
            'eligible_percentage': len(eligible_providers) / len(provider_data) * 100,
            'eligible_pa_volume': eligible_providers['annual_pas'].sum(),
            'total_pa_volume': provider_data['annual_pas'].sum(),
            'annual_savings': eligible_providers['savings'].sum(),
            'providers_detail': eligible_providers
        }
        
        return summary
    
    def calculate_denial_improvement_roi(self, denial_data):
        """
        Calculate ROI from reducing false denials
        
        Parameters:
        denial_data: dict with denial statistics
        """
        total_denials = denial_data['total_denials']
        overturn_rate = denial_data['overturn_rate']
        appeal_rate = denial_data['appeal_rate']
        
        # Current state
        current_appeals = total_denials * appeal_rate
        current_overturns = current_appeals * overturn_rate
        current_appeal_cost = current_appeals * self.appeal_cost
        
        # Future state (50% reduction in false positives)
        improvement_factor = 0.5
        future_false_denials = current_overturns * (1 - improvement_factor)
        future_appeals = future_false_denials / overturn_rate if overturn_rate > 0 else 0
        future_appeal_cost = future_appeals * self.appeal_cost
        
        roi = {
            'current_false_denials': current_overturns,
            'future_false_denials': future_false_denials,
            'reduced_appeals': current_appeals - future_appeals,
            'appeal_cost_savings': current_appeal_cost - future_appeal_cost,
            'member_experience_improvement': (1 - improvement_factor) * 100,
            'provider_satisfaction_impact': 'HIGH'
        }
        
        return roi
    
    def generate_roi_report(self, current_volumes, automation_targets, timeline_weeks=8):
        """
        Generate comprehensive ROI report with visualizations
        """
        # Calculate scenarios
        automation_roi = self.calculate_automation_scenario(current_volumes, automation_targets)
        
        # Create timeline projection
        weeks = np.arange(0, timeline_weeks + 1)
        adoption_curve = 1 / (1 + np.exp(-0.5 * (weeks - timeline_weeks/2)))
        
        weekly_savings = automation_roi['annual_cost_savings'] / 52
        cumulative_savings = adoption_curve * weekly_savings * weeks
        
        # Create visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Cost comparison
        methods = list(self.costs.keys())
        costs = list(self.costs.values())
        ax1.bar(methods, costs, color='skyblue')
        ax1.set_title('Cost per PA by Method')
        ax1.set_ylabel('Cost ($)')
        ax1.set_xticklabels(methods, rotation=45)
        
        # 2. Volume distribution (current vs future)
        current_vols = []
        future_vols = []
        labels = []
        
        for method in current_volumes.keys():
            if method in automation_roi['current_state'] and method != 'summary':
                labels.append(method)
                current_vols.append(automation_roi['current_state'][method]['volume'])
                future_vols.append(automation_roi['future_state'][method]['volume'])
        
        x = np.arange(len(labels))
        width = 0.35
        ax2.bar(x - width/2, current_vols, width, label='Current', color='coral')
        ax2.bar(x + width/2, future_vols, width, label='Future', color='lightgreen')
        ax2.set_title('PA Volume Distribution')
        ax2.set_ylabel('Annual Volume')
        ax2.set_xticks(x)
        ax2.set_xticklabels(labels, rotation=45)
        ax2.legend()
        
        # 3. Savings timeline
        ax3.plot(weeks, cumulative_savings, 'g-', linewidth=2)
        ax3.fill_between(weeks, 0, cumulative_savings, alpha=0.3, color='green')
        ax3.set_title('Cumulative Savings Timeline')
        ax3.set_xlabel('Weeks')
        ax3.set_ylabel('Cumulative Savings ($)')
        ax3.grid(True, alpha=0.3)
        
        # 4. ROI metrics
        metrics = {
            'Annual Savings': f"${automation_roi['annual_cost_savings']:,.0f}",
            'Cost Reduction': f"{automation_roi['cost_reduction_percentage']:.1f}%",
            'Break-even': f"{timeline_weeks/4:.1f} months",
            'Year 1 ROI': f"{automation_roi['annual_cost_savings']/100000:.1f}x"
        }
        
        y_pos = np.arange(len(metrics))
        ax4.barh(y_pos, [1]*len(metrics), alpha=0)
        for i, (metric, value) in enumerate(metrics.items()):
            ax4.text(0.5, i, f"{metric}: {value}", ha='center', va='center', fontsize=12)
        ax4.set_ylim(-0.5, len(metrics)-0.5)
        ax4.set_xlim(0, 1)
        ax4.axis('off')
        ax4.set_title('Key ROI Metrics')
        
        plt.tight_layout()
        
        return {
            'automation_roi': automation_roi,
            'figure': fig,
            'metrics': metrics
        }


# Example usage
if __name__ == "__main__":
    calculator = PriorAuthROICalculator()
    
    # Example current state (annual volumes)
    current_volumes = {
        'manual_fax': 30000,
        'manual_phone': 15000,
        'portal': 10000,
        'electronic': 5000
    }
    
    # Automation targets (percentage conversions)
    automation_targets = {
        'manual_fax': {
            'api': 0.3,
            'ai_automated': 0.5
        },
        'manual_phone': {
            'portal': 0.2,
            'api': 0.3,
            'ai_automated': 0.3
        },
        'portal': {
            'api': 0.4,
            'ai_automated': 0.3
        }
    }
    
    # Generate report
    report = calculator.generate_roi_report(current_volumes, automation_targets)
    
    # Print summary
    print("Prior Authorization ROI Analysis")
    print("=" * 50)
    print(f"Current Annual Cost: ${report['automation_roi']['current_state']['summary']['total_cost']:,.0f}")
    print(f"Future Annual Cost: ${report['automation_roi']['future_state']['summary']['total_cost']:,.0f}")
    print(f"Annual Savings: ${report['automation_roi']['annual_cost_savings']:,.0f}")
    print(f"Cost Reduction: {report['automation_roi']['cost_reduction_percentage']:.1f}%")
    
    # Save visualization
    report['figure'].savefig('pa_roi_analysis.png', dpi=300, bbox_inches='tight')
    print("\nROI visualization saved as 'pa_roi_analysis.png'")