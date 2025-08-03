#!/usr/bin/env python3
"""
Gold Card Eligibility Analyzer
Identifies providers eligible for auto-approval programs
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

class GoldCardAnalyzer:
    """Analyze provider performance for gold card eligibility"""
    
    def __init__(self, approval_threshold=0.92, min_volume_threshold=50):
        self.approval_threshold = approval_threshold
        self.min_volume_threshold = min_volume_threshold
        self.eligibility_criteria = {
            'immediate': {'approval_rate': 0.95, 'min_volume': 100, 'min_months': 12},
            'standard': {'approval_rate': 0.92, 'min_volume': 50, 'min_months': 12},
            'conditional': {'approval_rate': 0.90, 'min_volume': 50, 'min_months': 6},
            'probationary': {'approval_rate': 0.88, 'min_volume': 100, 'min_months': 18}
        }
    
    def calculate_provider_metrics(self, pa_data):
        """
        Calculate comprehensive provider performance metrics
        
        Parameters:
        pa_data: DataFrame with PA transaction data
        """
        # Group by provider
        provider_metrics = pa_data.groupby('provider_id').agg({
            'pa_id': 'count',
            'status': lambda x: (x == 'APPROVED').sum() / len(x),
            'member_id': 'nunique',
            'service_code': 'nunique',
            'created_date': ['min', 'max'],
            'appeal_flag': 'sum',
            'appeal_overturned': 'sum',
            'processing_hours': 'mean',
            'documentation_complete': 'mean'
        }).reset_index()
        
        # Flatten column names
        provider_metrics.columns = ['provider_id', 'total_pas', 'approval_rate', 
                                   'unique_members', 'service_variety', 
                                   'first_pa_date', 'last_pa_date',
                                   'total_appeals', 'overturned_appeals',
                                   'avg_processing_hours', 'doc_completeness']
        
        # Calculate additional metrics
        provider_metrics['months_active'] = (
            (provider_metrics['last_pa_date'] - provider_metrics['first_pa_date']).dt.days / 30.44
        )
        
        provider_metrics['appeal_overturn_rate'] = np.where(
            provider_metrics['total_appeals'] > 0,
            provider_metrics['overturned_appeals'] / provider_metrics['total_appeals'],
            0
        )
        
        # Calculate consistency score (low variance in monthly approval rates)
        monthly_consistency = self._calculate_monthly_consistency(pa_data)
        provider_metrics = provider_metrics.merge(monthly_consistency, on='provider_id', how='left')
        
        return provider_metrics
    
    def _calculate_monthly_consistency(self, pa_data):
        """Calculate approval rate consistency over time"""
        monthly_approval = pa_data.groupby([
            'provider_id',
            pd.Grouper(key='created_date', freq='M')
        ]).agg({
            'status': lambda x: (x == 'APPROVED').mean()
        }).reset_index()
        
        consistency = monthly_approval.groupby('provider_id')['status'].agg([
            'std',
            'mean'
        ]).reset_index()
        
        consistency.columns = ['provider_id', 'approval_std', 'approval_mean']
        consistency['consistency_score'] = 1 - (consistency['approval_std'] / consistency['approval_mean']).fillna(0)
        
        return consistency[['provider_id', 'consistency_score']]
    
    def determine_eligibility(self, provider_metrics):
        """
        Determine gold card eligibility for each provider
        """
        provider_metrics = provider_metrics.copy()
        
        # Initialize eligibility columns
        provider_metrics['eligibility_tier'] = 'NOT_ELIGIBLE'
        provider_metrics['gold_card_score'] = 0
        provider_metrics['recommended_services'] = 'NONE'
        
        for index, provider in provider_metrics.iterrows():
            # Check each tier
            for tier, criteria in self.eligibility_criteria.items():
                if (provider['approval_rate'] >= criteria['approval_rate'] and
                    provider['total_pas'] >= criteria['min_volume'] and
                    provider['months_active'] >= criteria['min_months']):
                    
                    provider_metrics.at[index, 'eligibility_tier'] = tier.upper()
                    break
            
            # Calculate gold card score (0-100)
            score = self._calculate_gold_card_score(provider)
            provider_metrics.at[index, 'gold_card_score'] = score
            
            # Recommend service scope
            if score >= 90:
                provider_metrics.at[index, 'recommended_services'] = 'ALL_SERVICES'
            elif score >= 80:
                provider_metrics.at[index, 'recommended_services'] = 'HIGH_VOLUME_SERVICES'
            elif score >= 70:
                provider_metrics.at[index, 'recommended_services'] = 'ROUTINE_SERVICES'
            else:
                provider_metrics.at[index, 'recommended_services'] = 'NONE'
        
        return provider_metrics
    
    def _calculate_gold_card_score(self, provider):
        """Calculate composite gold card score"""
        # Weighted scoring
        weights = {
            'approval_rate': 0.4,
            'volume': 0.2,
            'consistency': 0.2,
            'documentation': 0.1,
            'efficiency': 0.1
        }
        
        # Normalize metrics to 0-100 scale
        scores = {
            'approval_rate': provider['approval_rate'] * 100,
            'volume': min(provider['total_pas'] / 500, 1) * 100,
            'consistency': provider.get('consistency_score', 0.8) * 100,
            'documentation': provider.get('doc_completeness', 0.9) * 100,
            'efficiency': max(0, 100 - provider.get('avg_processing_hours', 10) * 5)
        }
        
        # Calculate weighted score
        total_score = sum(scores[metric] * weight for metric, weight in weights.items())
        
        return round(total_score, 1)
    
    def analyze_service_patterns(self, pa_data, eligible_providers):
        """
        Analyze which services should be gold-carded for each provider
        """
        eligible_ids = eligible_providers['provider_id'].tolist()
        
        # Filter to eligible providers
        eligible_pa_data = pa_data[pa_data['provider_id'].isin(eligible_ids)]
        
        # Analyze by service
        service_analysis = eligible_pa_data.groupby(['provider_id', 'service_code']).agg({
            'pa_id': 'count',
            'status': lambda x: (x == 'APPROVED').mean()
        }).reset_index()
        
        service_analysis.columns = ['provider_id', 'service_code', 'volume', 'approval_rate']
        
        # Identify services for gold carding
        service_analysis['gold_card_eligible'] = (
            (service_analysis['approval_rate'] >= 0.95) & 
            (service_analysis['volume'] >= 10)
        )
        
        return service_analysis
    
    def calculate_impact(self, provider_metrics, cost_per_manual_pa=14.49, cost_per_auto_pa=1.50):
        """
        Calculate financial and operational impact of gold carding
        """
        eligible = provider_metrics[provider_metrics['eligibility_tier'] != 'NOT_ELIGIBLE'].copy()
        
        # Calculate savings
        eligible['annual_pas'] = eligible['total_pas'] * 12 / eligible['months_active']
        eligible['current_cost'] = eligible['annual_pas'] * cost_per_manual_pa
        eligible['future_cost'] = eligible['annual_pas'] * cost_per_auto_pa
        eligible['annual_savings'] = eligible['current_cost'] - eligible['future_cost']
        
        # Summary metrics
        impact_summary = {
            'total_eligible_providers': len(eligible),
            'total_providers_analyzed': len(provider_metrics),
            'eligibility_rate': len(eligible) / len(provider_metrics) * 100,
            'total_pa_volume': eligible['annual_pas'].sum(),
            'total_annual_savings': eligible['annual_savings'].sum(),
            'avg_processing_time_reduction': eligible['avg_processing_hours'].mean() * 0.9,
            'member_impact': eligible['unique_members'].sum()
        }
        
        # Breakdown by tier
        tier_summary = eligible.groupby('eligibility_tier').agg({
            'provider_id': 'count',
            'annual_pas': 'sum',
            'annual_savings': 'sum'
        }).reset_index()
        
        impact_summary['tier_breakdown'] = tier_summary
        
        return impact_summary
    
    def generate_eligibility_report(self, provider_metrics, output_path='gold_card_analysis.png'):
        """
        Generate comprehensive eligibility report with visualizations
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Eligibility distribution
        eligibility_counts = provider_metrics['eligibility_tier'].value_counts()
        colors = ['gold', 'silver', 'bronze', 'lightgray', 'red']
        ax1.pie(eligibility_counts.values, labels=eligibility_counts.index, 
                autopct='%1.1f%%', colors=colors[:len(eligibility_counts)])
        ax1.set_title('Provider Eligibility Distribution')
        
        # 2. Approval rate distribution
        eligible = provider_metrics[provider_metrics['eligibility_tier'] != 'NOT_ELIGIBLE']
        ax2.hist(eligible['approval_rate'] * 100, bins=20, color='skyblue', edgecolor='black')
        ax2.axvline(x=92, color='red', linestyle='--', label='Gold Card Threshold')
        ax2.set_xlabel('Approval Rate (%)')
        ax2.set_ylabel('Number of Providers')
        ax2.set_title('Eligible Provider Approval Rates')
        ax2.legend()
        
        # 3. Score vs Volume scatter
        ax3.scatter(provider_metrics['total_pas'], 
                   provider_metrics['gold_card_score'],
                   c=provider_metrics['approval_rate'],
                   cmap='RdYlGn', alpha=0.6)
        ax3.set_xlabel('Total PA Volume')
        ax3.set_ylabel('Gold Card Score')
        ax3.set_title('Provider Score vs Volume')
        ax3.set_xscale('log')
        
        # 4. Potential savings by tier
        tier_savings = provider_metrics.groupby('eligibility_tier').apply(
            lambda x: (x['total_pas'] * 12 / x['months_active'] * 12.99).sum()
        ).sort_values(ascending=False)
        
        ax4.bar(tier_savings.index, tier_savings.values, color='green', alpha=0.7)
        ax4.set_xlabel('Eligibility Tier')
        ax4.set_ylabel('Annual Savings Potential ($)')
        ax4.set_title('Savings Opportunity by Tier')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def export_recommendations(self, provider_metrics, filename='gold_card_recommendations.csv'):
        """
        Export actionable recommendations
        """
        recommendations = provider_metrics[
            provider_metrics['eligibility_tier'] != 'NOT_ELIGIBLE'
        ][['provider_id', 'approval_rate', 'total_pas', 'eligibility_tier', 
           'gold_card_score', 'recommended_services']].copy()
        
        recommendations['implementation_priority'] = recommendations['gold_card_score'].apply(
            lambda x: 'HIGH' if x >= 85 else 'MEDIUM' if x >= 75 else 'LOW'
        )
        
        recommendations.to_csv(filename, index=False)
        print(f"Recommendations exported to {filename}")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    # NOTE: This generates sample data for demonstration purposes
    # In production, you would load actual PA transaction data from your database
    # Example: pa_data = pd.read_sql("SELECT * FROM prior_authorizations", connection)
    
    # Generate sample data for demo
    np.random.seed(42)
    n_providers = 500
    n_pas = 50000
    
    # Create sample PA data
    pa_data = pd.DataFrame({
        'pa_id': range(n_pas),
        'provider_id': np.random.choice(range(n_providers), n_pas, 
                                       p=np.random.dirichlet(np.ones(n_providers)*2)),
        'member_id': np.random.choice(range(10000), n_pas),
        'service_code': np.random.choice(['MRI', 'CT', 'PT', 'SURGERY', 'LAB'], n_pas),
        'created_date': pd.date_range(end=datetime.now(), periods=n_pas, freq='H'),
        'status': np.random.choice(['APPROVED', 'DENIED'], n_pas, p=[0.85, 0.15]),
        'appeal_flag': np.random.choice([0, 1], n_pas, p=[0.9, 0.1]),
        'appeal_overturned': 0,
        'processing_hours': np.random.exponential(10, n_pas),
        'documentation_complete': np.random.choice([0, 1], n_pas, p=[0.1, 0.9])
    })
    
    # Set overturned appeals
    pa_data.loc[pa_data['appeal_flag'] == 1, 'appeal_overturned'] = np.random.choice(
        [0, 1], sum(pa_data['appeal_flag'] == 1), p=[0.4, 0.6]
    )
    
    # Analyze
    analyzer = GoldCardAnalyzer()
    provider_metrics = analyzer.calculate_provider_metrics(pa_data)
    provider_metrics = analyzer.determine_eligibility(provider_metrics)
    
    # Calculate impact
    impact = analyzer.calculate_impact(provider_metrics)
    print(f"Total eligible providers: {impact['total_eligible_providers']}")
    print(f"Annual savings opportunity: ${impact['total_annual_savings']:,.0f}")
    
    # Generate report
    analyzer.generate_eligibility_report(provider_metrics)
    analyzer.export_recommendations(provider_metrics)