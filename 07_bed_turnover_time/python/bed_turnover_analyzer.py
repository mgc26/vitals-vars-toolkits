#!/usr/bin/env python3
"""
Bed Turnover Time Analyzer
Comprehensive analysis and visualization of hospital bed turnover metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for professional visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class BedTurnoverAnalyzer:
    """Analyze and visualize bed turnover performance metrics"""
    
    def __init__(self, turnover_data_path=None):
        """Initialize analyzer with optional data path"""
        self.turnover_data = None
        self.bottleneck_summary = None
        self.financial_impact = None
        
        if turnover_data_path:
            self.load_data(turnover_data_path)
    
    def load_data(self, filepath):
        """Load bed turnover data from CSV"""
        self.turnover_data = pd.read_csv(filepath, parse_dates=[
            'discharge_datetime', 'evs_notified_datetime', 
            'cleaning_completed_datetime', 'next_admission_datetime'
        ])
        self._calculate_time_segments()
    
    def generate_sample_data(self, n_records=1000):
        """Generate realistic sample bed turnover data"""
        np.random.seed(42)
        
        # Generate base timestamps
        base_dates = pd.date_range(start='2024-01-01', periods=n_records, freq='3H')
        
        # Unit distribution (realistic hospital units)
        units = ['ICU', 'Med/Surg A', 'Med/Surg B', 'Telemetry', 'Ortho', 'Cardiac', 'Neuro']
        unit_weights = [0.1, 0.25, 0.25, 0.15, 0.1, 0.1, 0.05]
        
        data = []
        for i, discharge_time in enumerate(base_dates):
            unit = np.random.choice(units, p=unit_weights)
            
            # Realistic time distributions (in minutes)
            if unit == 'ICU':
                # ICU tends to have longer turnovers
                evs_delay = np.random.normal(45, 20)
                cleaning_time = np.random.normal(75, 15)
                assignment_delay = np.random.normal(60, 30)
            else:
                # Standard units
                evs_delay = np.random.normal(30, 15)
                cleaning_time = np.random.normal(45, 10)
                assignment_delay = np.random.normal(45, 20)
            
            # Ensure positive values
            evs_delay = max(5, evs_delay)
            cleaning_time = max(20, cleaning_time)
            assignment_delay = max(10, assignment_delay)
            
            # Calculate timestamps
            evs_notified = discharge_time + timedelta(minutes=evs_delay)
            cleaning_completed = evs_notified + timedelta(minutes=cleaning_time)
            next_admission = cleaning_completed + timedelta(minutes=assignment_delay)
            
            data.append({
                'bed_id': f'BED_{i%100:03d}',
                'unit_name': unit,
                'discharge_datetime': discharge_time,
                'evs_notified_datetime': evs_notified,
                'cleaning_completed_datetime': cleaning_completed,
                'next_admission_datetime': next_admission,
                'patient_type': np.random.choice(['Medical', 'Surgical', 'Emergency'])
            })
        
        self.turnover_data = pd.DataFrame(data)
        self._calculate_time_segments()
        return self.turnover_data
    
    def _calculate_time_segments(self):
        """Calculate time segments for each turnover phase"""
        df = self.turnover_data
        
        # Calculate time segments in minutes
        df['discharge_to_evs_min'] = (
            df['evs_notified_datetime'] - df['discharge_datetime']
        ).dt.total_seconds() / 60
        
        df['evs_cleaning_min'] = (
            df['cleaning_completed_datetime'] - df['evs_notified_datetime']
        ).dt.total_seconds() / 60
        
        df['clean_to_occupied_min'] = (
            df['next_admission_datetime'] - df['cleaning_completed_datetime']
        ).dt.total_seconds() / 60
        
        df['total_turnover_min'] = (
            df['next_admission_datetime'] - df['discharge_datetime']
        ).dt.total_seconds() / 60
        
        # Add hour of day for pattern analysis
        df['discharge_hour'] = df['discharge_datetime'].dt.hour
        df['discharge_dow'] = df['discharge_datetime'].dt.day_name()
    
    def analyze_bottlenecks(self):
        """Identify and quantify bottlenecks in the turnover process"""
        df = self.turnover_data
        
        # Define target benchmarks (in minutes)
        benchmarks = {
            'discharge_to_evs_min': 15,
            'evs_cleaning_min': 45,
            'clean_to_occupied_min': 30,
            'total_turnover_min': 90
        }
        
        # Calculate excess time by phase
        bottlenecks = {}
        for phase, benchmark in benchmarks.items():
            excess = df[phase] - benchmark
            bottlenecks[phase] = {
                'avg_actual': df[phase].mean(),
                'benchmark': benchmark,
                'avg_excess': excess[excess > 0].mean(),
                'pct_over_benchmark': (excess > 0).sum() / len(df) * 100,
                'total_excess_hours': excess[excess > 0].sum() / 60
            }
        
        self.bottleneck_summary = pd.DataFrame(bottlenecks).T
        return self.bottleneck_summary
    
    def calculate_financial_impact(self, beds_count=300, revenue_per_bed_day=2000):
        """Calculate financial impact of turnover delays"""
        df = self.turnover_data
        
        # Calculate excess time per turnover (vs 90 min benchmark)
        excess_minutes = df['total_turnover_min'] - 90
        excess_minutes = excess_minutes[excess_minutes > 0]
        
        # Monthly and annual projections
        monthly_turnovers = len(df)
        annual_turnovers = monthly_turnovers * 12
        
        # Lost bed capacity
        total_excess_hours_monthly = excess_minutes.sum() / 60
        total_excess_hours_annual = total_excess_hours_monthly * 12
        lost_bed_days_annual = total_excess_hours_annual / 24
        
        # Financial calculations
        revenue_loss_annual = lost_bed_days_annual * revenue_per_bed_day
        
        # Equivalent bed capacity
        equivalent_beds_lost = total_excess_hours_annual / (24 * 365)
        
        self.financial_impact = {
            'monthly_turnovers': monthly_turnovers,
            'annual_turnovers': annual_turnovers,
            'avg_turnover_time_min': df['total_turnover_min'].mean(),
            'avg_excess_min': excess_minutes.mean() if len(excess_minutes) > 0 else 0,
            'total_excess_hours_annual': total_excess_hours_annual,
            'lost_bed_days_annual': lost_bed_days_annual,
            'revenue_loss_annual': revenue_loss_annual,
            'equivalent_beds_lost': equivalent_beds_lost,
            'roi_if_improved': revenue_loss_annual * 5  # 5-year NPV
        }
        
        return self.financial_impact
    
    def visualize_turnover_breakdown(self, save_path=None):
        """Create stacked bar chart of turnover time components by unit"""
        df = self.turnover_data
        
        # Aggregate by unit
        unit_summary = df.groupby('unit_name')[
            ['discharge_to_evs_min', 'evs_cleaning_min', 'clean_to_occupied_min']
        ].mean().round(1)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create stacked bar chart
        unit_summary.plot(kind='bar', stacked=True, ax=ax, 
                         color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        
        # Add 90-minute benchmark line
        ax.axhline(y=90, color='red', linestyle='--', linewidth=2, label='90-min Target')
        
        # Formatting
        ax.set_title('Bed Turnover Time Breakdown by Unit', fontsize=16, pad=20)
        ax.set_xlabel('Unit', fontsize=12)
        ax.set_ylabel('Time (minutes)', fontsize=12)
        ax.legend(['Discharge to EVS', 'EVS Cleaning', 'Clean to Occupied', '90-min Target'], 
                 loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for container in ax.containers[:3]:
            ax.bar_label(container, label_type='center', fmt='%.0f')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def visualize_hourly_patterns(self, save_path=None):
        """Visualize discharge patterns by hour of day"""
        df = self.turnover_data
        
        # Create hourly summary
        hourly = df.groupby('discharge_hour').agg({
            'bed_id': 'count',
            'total_turnover_min': 'mean'
        }).rename(columns={'bed_id': 'discharge_count'})
        
        # Create figure with two y-axes
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Bar chart for discharge count
        ax1.bar(hourly.index, hourly['discharge_count'], alpha=0.7, color='#4ECDC4')
        ax1.set_xlabel('Hour of Day', fontsize=12)
        ax1.set_ylabel('Number of Discharges', fontsize=12, color='#4ECDC4')
        ax1.tick_params(axis='y', labelcolor='#4ECDC4')
        
        # Line chart for average turnover time
        ax2 = ax1.twinx()
        ax2.plot(hourly.index, hourly['total_turnover_min'], 
                color='#FF6B6B', marker='o', linewidth=2, markersize=8)
        ax2.set_ylabel('Average Turnover Time (min)', fontsize=12, color='#FF6B6B')
        ax2.tick_params(axis='y', labelcolor='#FF6B6B')
        ax2.axhline(y=90, color='red', linestyle='--', alpha=0.5)
        
        # Title and formatting
        ax1.set_title('Discharge Volume and Turnover Time by Hour', fontsize=16, pad=20)
        ax1.set_xticks(range(24))
        ax1.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def visualize_bottleneck_heatmap(self, save_path=None):
        """Create heatmap showing bottleneck severity by unit and phase"""
        df = self.turnover_data
        
        # Calculate excess time by unit and phase
        phases = ['discharge_to_evs_min', 'evs_cleaning_min', 'clean_to_occupied_min']
        benchmarks = [15, 45, 30]
        
        heatmap_data = []
        for unit in df['unit_name'].unique():
            unit_data = df[df['unit_name'] == unit]
            row = []
            for phase, benchmark in zip(phases, benchmarks):
                excess_pct = ((unit_data[phase] - benchmark) / benchmark * 100).mean()
                row.append(max(0, excess_pct))  # Only show delays, not improvements
            heatmap_data.append(row)
        
        # Create DataFrame for heatmap
        heatmap_df = pd.DataFrame(
            heatmap_data,
            index=df['unit_name'].unique(),
            columns=['Discharge→EVS', 'EVS Cleaning', 'Clean→Occupied']
        )
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_df, annot=True, fmt='.0f', cmap='YlOrRd', 
                   cbar_kws={'label': '% Over Benchmark'})
        
        plt.title('Bottleneck Severity Heatmap\n(% Time Over Benchmark by Unit and Phase)', 
                 fontsize=16, pad=20)
        plt.xlabel('Turnover Phase', fontsize=12)
        plt.ylabel('Unit', fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def generate_executive_summary(self):
        """Generate executive summary of findings"""
        if self.bottleneck_summary is None:
            self.analyze_bottlenecks()
        if self.financial_impact is None:
            self.calculate_financial_impact()
        
        summary = f"""
BED TURNOVER ANALYSIS - EXECUTIVE SUMMARY
========================================

CURRENT PERFORMANCE
------------------
• Average Turnover Time: {self.financial_impact['avg_turnover_time_min']:.0f} minutes
• Target Benchmark: 90 minutes  
• Average Excess: {self.financial_impact['avg_excess_min']:.0f} minutes per turnover

BOTTLENECK ANALYSIS
------------------
• Discharge to EVS: {self.bottleneck_summary.loc['discharge_to_evs_min', 'avg_actual']:.0f} min (target: 15 min)
• EVS Cleaning: {self.bottleneck_summary.loc['evs_cleaning_min', 'avg_actual']:.0f} min (target: 45 min)
• Clean to Occupied: {self.bottleneck_summary.loc['clean_to_occupied_min', 'avg_actual']:.0f} min (target: 30 min)

FINANCIAL IMPACT
---------------
• Annual Turnovers: {self.financial_impact['annual_turnovers']:,}
• Lost Bed Days/Year: {self.financial_impact['lost_bed_days_annual']:.0f}
• Annual Revenue Loss: ${self.financial_impact['revenue_loss_annual']:,.0f}
• Equivalent Beds Lost: {self.financial_impact['equivalent_beds_lost']:.1f}

IMPROVEMENT OPPORTUNITY
----------------------
• If turnover reduced to 90 minutes:
  - Capacity gain: {self.financial_impact['equivalent_beds_lost']:.1f} beds
  - Annual revenue recovery: ${self.financial_impact['revenue_loss_annual']:,.0f}
  - 5-year ROI potential: ${self.financial_impact['roi_if_improved']:,.0f}
"""
        return summary


# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = BedTurnoverAnalyzer()
    
    # Generate sample data (or load your own)
    analyzer.generate_sample_data(n_records=1000)
    
    # Perform analysis
    bottlenecks = analyzer.analyze_bottlenecks()
    financial_impact = analyzer.calculate_financial_impact()
    
    # Generate visualizations
    analyzer.visualize_turnover_breakdown('turnover_breakdown.png')
    analyzer.visualize_hourly_patterns('hourly_patterns.png')
    analyzer.visualize_bottleneck_heatmap('bottleneck_heatmap.png')
    
    # Print executive summary
    print(analyzer.generate_executive_summary())