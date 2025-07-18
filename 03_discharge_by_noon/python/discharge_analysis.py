#!/usr/bin/env python3
"""
Discharge by Noon Analysis Tools
Comprehensive analytics for tracking and improving discharge timing
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DischargeAnalyzer:
    """Main class for analyzing discharge patterns and identifying improvement opportunities"""
    
    def __init__(self, discharge_data_path=None):
        """Initialize with discharge data"""
        if discharge_data_path:
            self.data = pd.read_csv(discharge_data_path, parse_dates=['admission_time', 'discharge_time'])
        else:
            self.data = self.generate_sample_data()
            
        self.preprocess_data()
    
    def generate_sample_data(self, n_patients=1000):
        """Generate realistic sample discharge data for demonstration"""
        np.random.seed(42)
        
        # Generate admission times
        start_date = datetime.now() - timedelta(days=90)
        admission_times = pd.date_range(start=start_date, periods=n_patients, freq='6H')
        admission_times += pd.to_timedelta(np.random.randint(0, 360, n_patients), unit='m')
        
        # Generate length of stay (exponential distribution)
        los_hours = np.random.exponential(scale=72, size=n_patients) + 24
        
        # Generate discharge times with bias towards afternoon
        discharge_hours = np.random.normal(loc=14, scale=3, size=n_patients)
        discharge_hours = np.clip(discharge_hours, 6, 20)
        
        # Create DataFrame
        data = pd.DataFrame({
            'encounter_id': range(1000, 1000 + n_patients),
            'patient_id': np.random.randint(10000, 99999, n_patients),
            'admission_time': admission_times,
            'los_hours': los_hours,
            'unit': np.random.choice(['Medical', 'Surgical', 'Cardiology', 'Orthopedics'], n_patients, 
                                   p=[0.4, 0.3, 0.2, 0.1]),
            'attending_physician': np.random.choice([f'Dr. {i}' for i in 'ABCDEFGHIJ'], n_patients),
            'discharge_disposition': np.random.choice(['Home', 'SNF', 'Rehab', 'Home Health'], 
                                                    n_patients, p=[0.6, 0.2, 0.1, 0.1]),
            'complexity_score': np.random.randint(1, 10, n_patients)
        })
        
        # Calculate discharge times
        data['discharge_time'] = data['admission_time'] + pd.to_timedelta(data['los_hours'], unit='h')
        data['discharge_time'] = data['discharge_time'].dt.normalize() + pd.to_timedelta(discharge_hours, unit='h')
        
        # Add some weekend effect
        data.loc[data['discharge_time'].dt.dayofweek.isin([5, 6]), 'discharge_time'] += pd.Timedelta(hours=2)
        
        return data
    
    def preprocess_data(self):
        """Add calculated fields for analysis"""
        self.data['discharge_hour'] = self.data['discharge_time'].dt.hour
        self.data['discharge_date'] = self.data['discharge_time'].dt.date
        self.data['discharge_dow'] = self.data['discharge_time'].dt.day_name()
        self.data['is_weekend'] = self.data['discharge_time'].dt.dayofweek.isin([5, 6])
        self.data['is_dbn'] = self.data['discharge_hour'] < 12
        self.data['los_days'] = self.data['los_hours'] / 24
    
    def calculate_dbn_metrics(self, groupby_col=None):
        """Calculate discharge by noon metrics"""
        if groupby_col:
            metrics = self.data.groupby(groupby_col).agg({
                'encounter_id': 'count',
                'is_dbn': ['sum', 'mean'],
                'discharge_hour': 'mean'
            }).round(2)
            metrics.columns = ['total_discharges', 'dbn_count', 'dbn_rate', 'avg_discharge_hour']
        else:
            metrics = {
                'total_discharges': len(self.data),
                'dbn_count': self.data['is_dbn'].sum(),
                'dbn_rate': self.data['is_dbn'].mean(),
                'avg_discharge_hour': self.data['discharge_hour'].mean()
            }
        return metrics
    
    def plot_hourly_distribution(self, save_path=None):
        """Create hourly discharge distribution chart"""
        plt.figure(figsize=(12, 6))
        
        hourly_counts = self.data['discharge_hour'].value_counts().sort_index()
        
        colors = ['green' if h < 12 else 'orange' for h in hourly_counts.index]
        bars = plt.bar(hourly_counts.index, hourly_counts.values, color=colors, alpha=0.8)
        
        plt.axvline(x=12, color='red', linestyle='--', label='Noon Target')
        plt.xlabel('Hour of Discharge')
        plt.ylabel('Number of Discharges')
        plt.title('Discharge Time Distribution\n(Green = Before Noon, Orange = After Noon)')
        plt.xticks(range(0, 24))
        plt.grid(axis='y', alpha=0.3)
        
        # Add percentage labels
        total = hourly_counts.sum()
        for bar, count in zip(bars, hourly_counts.values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{count/total*100:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # Add DBN rate annotation
        dbn_rate = self.data['is_dbn'].mean() * 100
        plt.text(0.02, 0.95, f'DBN Rate: {dbn_rate:.1f}%', 
                transform=plt.gca().transAxes, fontsize=14, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def analyze_unit_performance(self, save_path=None):
        """Compare DBN performance across units"""
        unit_metrics = self.calculate_dbn_metrics('unit')
        unit_metrics = unit_metrics.sort_values('dbn_rate', ascending=False)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # DBN Rate by Unit
        bars = ax1.bar(unit_metrics.index, unit_metrics['dbn_rate'] * 100, 
                       color=sns.color_palette('viridis', len(unit_metrics)))
        ax1.axhline(y=30, color='red', linestyle='--', label='30% Target')
        ax1.set_xlabel('Unit')
        ax1.set_ylabel('DBN Rate (%)')
        ax1.set_title('Discharge by Noon Rate by Unit')
        ax1.legend()
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Average Discharge Hour by Unit
        ax2.bar(unit_metrics.index, unit_metrics['avg_discharge_hour'], 
               color=sns.color_palette('plasma', len(unit_metrics)))
        ax2.axhline(y=12, color='red', linestyle='--', label='Noon')
        ax2.set_xlabel('Unit')
        ax2.set_ylabel('Average Discharge Hour')
        ax2.set_title('Average Discharge Time by Unit')
        ax2.legend()
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return unit_metrics
    
    def weekend_analysis(self, save_path=None):
        """Analyze weekend vs weekday discharge patterns"""
        weekend_metrics = self.data.groupby('is_weekend').agg({
            'encounter_id': 'count',
            'is_dbn': 'mean',
            'discharge_hour': 'mean',
            'los_days': 'mean'
        }).round(2)
        weekend_metrics.index = ['Weekday', 'Weekend']
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # DBN Rate Comparison
        bars = ax1.bar(weekend_metrics.index, weekend_metrics['is_dbn'] * 100, 
                       color=['skyblue', 'lightcoral'])
        ax1.set_ylabel('DBN Rate (%)')
        ax1.set_title('Discharge by Noon Rate: Weekday vs Weekend')
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Average Discharge Hour
        ax2.bar(weekend_metrics.index, weekend_metrics['discharge_hour'], 
               color=['skyblue', 'lightcoral'])
        ax2.axhline(y=12, color='red', linestyle='--', alpha=0.5)
        ax2.set_ylabel('Average Hour')
        ax2.set_title('Average Discharge Hour')
        
        # Discharge Volume
        ax3.bar(weekend_metrics.index, weekend_metrics['encounter_id'], 
               color=['skyblue', 'lightcoral'])
        ax3.set_ylabel('Number of Discharges')
        ax3.set_title('Discharge Volume')
        
        # Average Length of Stay
        ax4.bar(weekend_metrics.index, weekend_metrics['los_days'], 
               color=['skyblue', 'lightcoral'])
        ax4.set_ylabel('Days')
        ax4.set_title('Average Length of Stay')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return weekend_metrics
    
    def physician_performance(self, min_discharges=20):
        """Analyze discharge patterns by physician"""
        physician_metrics = self.calculate_dbn_metrics('attending_physician')
        physician_metrics = physician_metrics[physician_metrics['total_discharges'] >= min_discharges]
        physician_metrics = physician_metrics.sort_values('dbn_rate', ascending=True)
        
        plt.figure(figsize=(10, 8))
        
        # Create horizontal bar chart
        y_pos = np.arange(len(physician_metrics))
        colors = plt.cm.RdYlGn(physician_metrics['dbn_rate'])
        
        bars = plt.barh(y_pos, physician_metrics['dbn_rate'] * 100, color=colors)
        plt.yticks(y_pos, physician_metrics.index)
        plt.xlabel('DBN Rate (%)')
        plt.title(f'Physician Discharge Performance\n(Minimum {min_discharges} discharges)')
        plt.axvline(x=30, color='red', linestyle='--', label='30% Target')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{width:.1f}%', ha='left', va='center')
        
        plt.legend()
        plt.tight_layout()
        plt.show()
        
        return physician_metrics
    
    def calculate_opportunities(self):
        """Identify specific opportunities for improvement"""
        opportunities = {
            'Simple Cases Delayed': len(self.data[
                (self.data['complexity_score'] <= 3) & 
                (~self.data['is_dbn']) &
                (self.data['discharge_disposition'] == 'Home')
            ]),
            'Weekend Opportunities': len(self.data[
                (self.data['is_weekend']) & 
                (self.data['los_days'] >= 3) &
                (self.data['complexity_score'] <= 5)
            ]),
            'Early Morning Potential': len(self.data[
                (self.data['discharge_hour'].between(12, 14)) &
                (self.data['complexity_score'] <= 5)
            ])
        }
        
        # Calculate potential improvement
        current_dbn_rate = self.data['is_dbn'].mean()
        potential_additions = sum(opportunities.values())
        potential_dbn_rate = (self.data['is_dbn'].sum() + potential_additions * 0.5) / len(self.data)
        
        print("\n=== DISCHARGE BY NOON IMPROVEMENT OPPORTUNITIES ===")
        print(f"\nCurrent Performance:")
        print(f"  - DBN Rate: {current_dbn_rate*100:.1f}%")
        print(f"  - Average Discharge Hour: {self.data['discharge_hour'].mean():.1f}")
        
        print(f"\nIdentified Opportunities:")
        for opp, count in opportunities.items():
            print(f"  - {opp}: {count} patients")
        
        print(f"\nPotential Performance:")
        print(f"  - Achievable DBN Rate: {potential_dbn_rate*100:.1f}%")
        print(f"  - Improvement: +{(potential_dbn_rate-current_dbn_rate)*100:.1f} percentage points")
        
        return opportunities
    
    def generate_daily_report(self, date=None):
        """Generate a daily discharge readiness report"""
        if date is None:
            date = datetime.now().date()
        
        # Filter to specific date
        daily_data = self.data[self.data['discharge_date'] == date]
        
        if len(daily_data) == 0:
            print(f"No discharges found for {date}")
            return
        
        print(f"\n=== DISCHARGE BY NOON DAILY REPORT: {date} ===")
        print(f"\nOverall Metrics:")
        print(f"  - Total Discharges: {len(daily_data)}")
        print(f"  - DBN Count: {daily_data['is_dbn'].sum()}")
        print(f"  - DBN Rate: {daily_data['is_dbn'].mean()*100:.1f}%")
        print(f"  - Average Discharge Hour: {daily_data['discharge_hour'].mean():.1f}")
        
        print(f"\nBy Unit:")
        unit_summary = daily_data.groupby('unit').agg({
            'is_dbn': ['count', 'sum', 'mean']
        }).round(2)
        unit_summary.columns = ['Total', 'DBN_Count', 'DBN_Rate']
        print(unit_summary)
        
        print(f"\nBy Hour:")
        hourly = daily_data['discharge_hour'].value_counts().sort_index()
        for hour, count in hourly.items():
            bar = '█' * int(count * 2)
            print(f"  {hour:02d}:00 - {count:2d} {bar}")


def main():
    """Example usage of the DischargeAnalyzer"""
    print("Initializing Discharge by Noon Analyzer...")
    analyzer = DischargeAnalyzer()
    
    # Generate visualizations
    print("\nGenerating hourly distribution plot...")
    analyzer.plot_hourly_distribution('discharge_hourly_distribution.png')
    
    print("\nAnalyzing unit performance...")
    unit_metrics = analyzer.analyze_unit_performance('unit_performance.png')
    
    print("\nAnalyzing weekend patterns...")
    weekend_metrics = analyzer.weekend_analysis('weekend_analysis.png')
    
    print("\nAnalyzing physician performance...")
    physician_metrics = analyzer.physician_performance()
    
    # Calculate improvement opportunities
    opportunities = analyzer.calculate_opportunities()
    
    # Generate daily report
    analyzer.generate_daily_report()
    
    print("\n✓ Analysis complete! Check generated visualizations.")


if __name__ == "__main__":
    main()