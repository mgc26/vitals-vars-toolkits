#!/usr/bin/env python3
"""
Staffing Variance Analyzer
Analyzes the gap between scheduled staffing and actual demand
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

class StaffingVarianceAnalyzer:
    def __init__(self):
        self.variance_data = None
        self.patterns = {}
        
    def load_data(self, staffing_file: str = None, census_file: str = None) -> pd.DataFrame:
        """Load staffing and census data or generate sample data"""
        if staffing_file and census_file:
            staffing_df = pd.read_csv(staffing_file)
            census_df = pd.read_csv(census_file)
            return self._merge_data(staffing_df, census_df)
        else:
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate realistic sample staffing data"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', end='2024-06-30', freq='D')
        
        data = []
        for date in dates:
            # Base patterns
            dow = date.dayofweek
            is_monday = dow == 0
            is_weekend = dow >= 5
            
            # Census patterns (higher on Monday, lower on weekends)
            base_census = 24
            if is_monday:
                census_modifier = 1.4  # 40% surge on Mondays
            elif is_weekend:
                census_modifier = 0.85
            else:
                census_modifier = 1.0
            
            # Add seasonality and randomness
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * date.dayofyear / 365)
            census = int(base_census * census_modifier * seasonal_factor + np.random.normal(0, 3))
            census = max(15, min(35, census))  # Bounds
            
            # Scheduled staffing (often flat, not responsive to patterns)
            scheduled_nurses = 6 if not is_weekend else 5
            
            # Actual staffing (reactive to census)
            if census > 28:  # High census
                actual_nurses = scheduled_nurses + np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
                overtime_hours = np.random.uniform(4, 12) if actual_nurses > scheduled_nurses else 0
                agency_hours = np.random.uniform(0, 12) if actual_nurses > scheduled_nurses + 1 else 0
            elif census < 20:  # Low census  
                actual_nurses = scheduled_nurses - np.random.choice([0, 1], p=[0.7, 0.3])
                overtime_hours = 0
                agency_hours = 0
            else:  # Normal census
                actual_nurses = scheduled_nurses
                overtime_hours = np.random.uniform(0, 4) if np.random.random() > 0.7 else 0
                agency_hours = 0
            
            # Required staffing based on ratios (1:4 ratio)
            required_nurses = np.ceil(census / 4)
            
            data.append({
                'date': date,
                'unit': 'Med-Surg-1',
                'shift': 'Day',
                'census': census,
                'scheduled_nurses': scheduled_nurses,
                'actual_nurses': actual_nurses,
                'required_nurses': required_nurses,
                'overtime_hours': overtime_hours,
                'agency_hours': agency_hours,
                'sick_calls': 1 if np.random.random() > 0.9 else 0
            })
        
        return pd.DataFrame(data)
    
    def calculate_variance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate staffing variance metrics"""
        df = df.copy()
        
        # Core variance calculations
        df['variance_to_required'] = ((df['actual_nurses'] - df['required_nurses']) / 
                                      df['required_nurses'] * 100)
        df['variance_to_scheduled'] = ((df['actual_nurses'] - df['scheduled_nurses']) / 
                                       df['scheduled_nurses'] * 100)
        
        # Staffing adequacy
        df['understaffed'] = df['actual_nurses'] < df['required_nurses']
        df['overstaffed'] = df['actual_nurses'] > df['required_nurses'] * 1.1
        
        # Cost indicators
        df['used_overtime'] = df['overtime_hours'] > 0
        df['used_agency'] = df['agency_hours'] > 0
        
        # Day of week
        df['day_of_week'] = df['date'].dt.day_name()
        df['is_monday'] = df['date'].dt.dayofweek == 0
        df['is_weekend'] = df['date'].dt.dayofweek >= 5
        
        self.variance_data = df
        return df
    
    def identify_patterns(self, df: pd.DataFrame) -> Dict:
        """Identify key patterns in staffing variance"""
        patterns = {}
        
        # Monday surge pattern
        monday_census = df[df['is_monday']]['census'].mean()
        other_weekday_census = df[(~df['is_monday']) & (~df['is_weekend'])]['census'].mean()
        patterns['monday_surge'] = (monday_census - other_weekday_census) / other_weekday_census * 100
        
        # Overall variance
        patterns['avg_variance'] = abs(df['variance_to_required']).mean()
        patterns['variance_std'] = df['variance_to_required'].std()
        
        # Crisis points
        patterns['understaffed_pct'] = (df['understaffed'].sum() / len(df)) * 100
        patterns['overstaffed_pct'] = (df['overstaffed'].sum() / len(df)) * 100
        
        # Premium labor usage
        patterns['overtime_frequency'] = (df['used_overtime'].sum() / len(df)) * 100
        patterns['agency_frequency'] = (df['used_agency'].sum() / len(df)) * 100
        
        # Patterns by day of week
        dow_patterns = df.groupby('day_of_week').agg({
            'variance_to_required': 'mean',
            'overtime_hours': 'sum',
            'agency_hours': 'sum'
        })
        patterns['dow_analysis'] = dow_patterns
        
        self.patterns = patterns
        return patterns
    
    def calculate_costs(self, df: pd.DataFrame, 
                       regular_rate: float = 45,
                       overtime_rate: float = 67.5,
                       agency_rate: float = 110) -> Dict:
        """Calculate financial impact of staffing variance"""
        
        # Total hours
        total_regular_hours = df['scheduled_nurses'].sum() * 12  # 12-hour shifts
        total_overtime_hours = df['overtime_hours'].sum()
        total_agency_hours = df['agency_hours'].sum()
        
        # Costs
        regular_cost = total_regular_hours * regular_rate
        overtime_cost = total_overtime_hours * overtime_rate
        agency_cost = total_agency_hours * agency_rate
        
        # Excess costs (overtime and agency premiums)
        overtime_premium = total_overtime_hours * (overtime_rate - regular_rate)
        agency_premium = total_agency_hours * (agency_rate - regular_rate)
        total_excess = overtime_premium + agency_premium
        
        # Annualized (sample is 6 months)
        annual_factor = 365 / len(df)
        
        return {
            'total_regular_cost': regular_cost,
            'total_overtime_cost': overtime_cost,
            'total_agency_cost': agency_cost,
            'excess_cost_6mo': total_excess,
            'excess_cost_annual': total_excess * annual_factor,
            'overtime_pct_of_hours': (total_overtime_hours / total_regular_hours) * 100,
            'agency_pct_of_hours': (total_agency_hours / total_regular_hours) * 100
        }
    
    def plot_variance_analysis(self, df: pd.DataFrame):
        """Create visualization of variance patterns"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Variance distribution
        axes[0, 0].hist(df['variance_to_required'], bins=30, edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(x=0, color='red', linestyle='--', linewidth=2)
        axes[0, 0].set_xlabel('Variance to Required (%)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Distribution of Staffing Variance')
        
        # 2. Day of week patterns
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_data = df.groupby('day_of_week')['variance_to_required'].mean().reindex(dow_order)
        axes[0, 1].bar(range(7), dow_data.values, color=['red' if d == 'Monday' else 'blue' for d in dow_order])
        axes[0, 1].set_xticks(range(7))
        axes[0, 1].set_xticklabels(dow_order, rotation=45)
        axes[0, 1].set_ylabel('Average Variance (%)')
        axes[0, 1].set_title('Variance by Day of Week')
        axes[0, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # 3. Census vs Staffing over time (sample month)
        sample_df = df.head(30)
        axes[1, 0].plot(sample_df['date'], sample_df['census']/4, label='Required Nurses (Census/4)', linewidth=2)
        axes[1, 0].plot(sample_df['date'], sample_df['actual_nurses'], label='Actual Nurses', linewidth=2)
        axes[1, 0].plot(sample_df['date'], sample_df['scheduled_nurses'], label='Scheduled Nurses', linestyle='--')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('Nurses')
        axes[1, 0].set_title('Staffing vs Demand (30-day sample)')
        axes[1, 0].legend()
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Cost breakdown
        costs = self.calculate_costs(df)
        categories = ['Regular', 'Overtime Premium', 'Agency Premium']
        values = [costs['total_regular_cost'], 
                 costs['total_overtime_cost'] - costs['total_regular_cost'] * (costs['overtime_pct_of_hours']/100),
                 costs['total_agency_cost'] - costs['total_regular_cost'] * (costs['agency_pct_of_hours']/100)]
        axes[1, 1].pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('Labor Cost Breakdown (6 months)')
        
        plt.tight_layout()
        return fig
    
    def generate_report(self, df: pd.DataFrame) -> str:
        """Generate executive summary report"""
        patterns = self.identify_patterns(df)
        costs = self.calculate_costs(df)
        
        report = f"""
STAFFING VARIANCE ANALYSIS REPORT
{'='*50}

EXECUTIVE SUMMARY
-----------------
Analysis Period: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}
Total Days Analyzed: {len(df)}

KEY FINDINGS
------------
1. VARIANCE METRICS
   - Average Absolute Variance: {patterns['avg_variance']:.1f}%
   - Standard Deviation: {patterns['variance_std']:.1f}%
   - Days Understaffed: {patterns['understaffed_pct']:.1f}%
   - Days Overstaffed: {patterns['overstaffed_pct']:.1f}%

2. PATTERN INSIGHTS
   - Monday Census Surge: +{patterns['monday_surge']:.1f}% vs other weekdays
   - Weekend Staffing: Often overstaffed relative to census
   - Crisis Response: {patterns['overtime_frequency']:.1f}% of days require overtime

3. FINANCIAL IMPACT (Annualized)
   - Excess Labor Costs: ${costs['excess_cost_annual']:,.0f}
   - Overtime as % of Hours: {costs['overtime_pct_of_hours']:.1f}%
   - Agency as % of Hours: {costs['agency_pct_of_hours']:.1f}%

4. OPPORTUNITY
   - Reducing variance from {patterns['avg_variance']:.1f}% to 7% would save:
     ${costs['excess_cost_annual'] * 0.6:,.0f} annually
   - Quick wins: Monday surge planning, weekend right-sizing

RECOMMENDATIONS
---------------
1. Implement predictive staffing model (included in toolkit)
2. Create flexible pool for Monday coverage
3. Establish morning rebalancing protocol
4. Track variance daily with provided dashboard

NEXT STEPS
----------
1. Review detailed patterns by day of week
2. Run predictive model on your full dataset
3. Calculate ROI for your specific facility
4. Pilot on highest-variance unit
"""
        return report


def main():
    """Main execution function"""
    print("Staffing Variance Analyzer")
    print("-" * 40)
    
    analyzer = StaffingVarianceAnalyzer()
    
    # Load or generate data
    print("Loading staffing data...")
    df = analyzer.load_data()
    
    # Calculate variance
    print("Calculating variance metrics...")
    df = analyzer.calculate_variance(df)
    
    # Generate report
    report = analyzer.generate_report(df)
    print(report)
    
    # Create visualizations
    print("\nGenerating visualizations...")
    fig = analyzer.plot_variance_analysis(df)
    plt.savefig('staffing_variance_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: staffing_variance_analysis.png")
    
    # Save processed data
    df.to_csv('staffing_variance_data.csv', index=False)
    print("Saved: staffing_variance_data.csv")
    
    return analyzer, df


if __name__ == "__main__":
    analyzer, data = main()