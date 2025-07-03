#!/usr/bin/env python3
"""
ED Boarding Pattern Visualizer
Creates heatmaps and visualizations to identify boarding patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class BoardingVisualizer:
    def __init__(self):
        self.color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        sns.set_style("whitegrid")
        
    def create_boarding_heatmap(self, df, save_path='boarding_heatmap.png'):
        """
        Create heatmap showing boarding hours by day of week and hour
        """
        # Pivot data for heatmap
        heatmap_data = df.pivot_table(
            values='boarding_hours',
            index='hour_of_day',
            columns='day_of_week',
            aggfunc='mean'
        )
        
        # Day labels
        day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Create heatmap
        sns.heatmap(
            heatmap_data,
            cmap='YlOrRd',
            annot=True,
            fmt='.1f',
            cbar_kws={'label': 'Average Boarding Hours'},
            xticklabels=day_labels
        )
        
        plt.title('ED Boarding Patterns: Average Hours by Day and Time', fontsize=16, pad=20)
        plt.xlabel('Day of Week', fontsize=12)
        plt.ylabel('Hour of Day', fontsize=12)
        
        # Add annotation for worst times
        max_val = heatmap_data.max().max()
        worst_times = []
        for col in heatmap_data.columns:
            for idx in heatmap_data.index:
                if heatmap_data.loc[idx, col] >= max_val * 0.9:
                    worst_times.append(f"{day_labels[col]} {idx}:00")
        
        plt.figtext(0.02, 0.02, f"Peak boarding times: {', '.join(worst_times[:3])}", 
                   fontsize=10, style='italic')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return heatmap_data
    
    def create_behavioral_health_comparison(self, df, save_path='behavioral_health_boarding.png'):
        """
        Compare boarding times for behavioral health vs medical patients
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Box plot comparison
        df_plot = df[['is_behavioral_health', 'boarding_hours']].copy()
        df_plot['Patient Type'] = df_plot['is_behavioral_health'].map({
            1: 'Behavioral Health',
            0: 'Medical/Surgical'
        })
        
        sns.boxplot(data=df_plot, x='Patient Type', y='boarding_hours', ax=ax1)
        ax1.set_title('Boarding Time Distribution by Patient Type', fontsize=14)
        ax1.set_ylabel('Boarding Hours', fontsize=12)
        
        # Add median values
        medians = df_plot.groupby('Patient Type')['boarding_hours'].median()
        for i, (patient_type, median) in enumerate(medians.items()):
            ax1.text(i, median + 0.5, f'Median: {median:.1f}h', 
                    ha='center', va='bottom', fontweight='bold')
        
        # Time series comparison
        daily_avg = df.groupby(['date', 'is_behavioral_health'])['boarding_hours'].mean().reset_index()
        
        for bh_flag, label in [(0, 'Medical/Surgical'), (1, 'Behavioral Health')]:
            data = daily_avg[daily_avg['is_behavioral_health'] == bh_flag]
            ax2.plot(data['date'], data['boarding_hours'], 
                    label=label, linewidth=2, alpha=0.8)
        
        ax2.set_title('Daily Average Boarding Hours Trend', fontsize=14)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Average Boarding Hours', fontsize=12)
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_interactive_dashboard(self, df):
        """
        Create interactive Plotly dashboard for boarding analysis
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Boarding Hours by Hour of Day', 
                          'Weekly Boarding Patterns',
                          'Boarding Duration Distribution',
                          'ECCQ Compliance Tracking'),
            specs=[[{'type': 'scatter'}, {'type': 'bar'}],
                   [{'type': 'histogram'}, {'type': 'indicator'}]]
        )
        
        # 1. Hourly patterns
        hourly = df.groupby('hour_of_day')['boarding_hours'].agg(['mean', 'count']).reset_index()
        fig.add_trace(
            go.Scatter(x=hourly['hour_of_day'], y=hourly['mean'],
                      mode='lines+markers', name='Avg Boarding Hours',
                      line=dict(width=3)),
            row=1, col=1
        )
        
        # 2. Weekly patterns
        weekly = df.groupby('day_of_week')['boarding_hours'].mean().reset_index()
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        fig.add_trace(
            go.Bar(x=day_names, y=weekly['boarding_hours'],
                   name='Avg Hours by Day'),
            row=1, col=2
        )
        
        # 3. Distribution
        fig.add_trace(
            go.Histogram(x=df['boarding_hours'], nbinsx=50,
                        name='Boarding Hours Distribution'),
            row=2, col=1
        )
        
        # 4. ECCQ Compliance
        eccq_compliant = (df['boarding_hours'] <= 4).sum() / len(df) * 100
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=eccq_compliant,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "ECCQ Compliance %"},
                delta={'reference': 90, 'relative': True},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 70], 'color': "lightgray"},
                           {'range': [70, 90], 'color': "gray"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="ED Boarding Analytics Dashboard",
            title_font_size=20
        )
        
        # Save as HTML
        fig.write_html("boarding_dashboard.html")
        return fig
    
    def generate_executive_summary(self, df, save_path='executive_summary.png'):
        """
        Create executive summary visualization
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Key Metrics
        metrics = {
            'Median Boarding': f"{df['boarding_hours'].median():.1f}h",
            '90th Percentile': f"{df['boarding_hours'].quantile(0.9):.1f}h",
            'Behavioral Health': f"{df[df['is_behavioral_health']==1]['boarding_hours'].median():.1f}h",
            'Total Cost Impact': f"${(df['boarding_hours'].sum() * 219):,.0f}"
        }
        
        ax1.axis('off')
        y_pos = 0.8
        for metric, value in metrics.items():
            ax1.text(0.1, y_pos, metric + ':', fontsize=14, fontweight='bold')
            ax1.text(0.6, y_pos, value, fontsize=14)
            y_pos -= 0.2
        ax1.set_title('Key Boarding Metrics', fontsize=16, pad=20)
        
        # 2. Trending
        daily = df.groupby('date')['boarding_hours'].mean()
        ax2.plot(daily.index, daily.values, linewidth=2)
        ax2.axhline(y=4, color='r', linestyle='--', label='ECCQ Threshold')
        ax2.set_title('Daily Average Boarding Trend', fontsize=14)
        ax2.set_ylabel('Hours', fontsize=12)
        ax2.legend()
        
        # 3. Cost breakdown
        cost_data = pd.DataFrame({
            'Category': ['Lost ED Capacity', 'Overtime', 'Quality Penalties', 'Other'],
            'Cost': [137 * df['boarding_hours'].sum(),
                    82 * df['boarding_hours'].sum(),
                    50000,  # Estimated
                    25000]  # Estimated
        })
        
        ax3.pie(cost_data['Cost'], labels=cost_data['Category'], autopct='%1.0f%%',
               colors=self.color_palette[:4])
        ax3.set_title('Annual Cost Breakdown', fontsize=14)
        
        # 4. Intervention impact
        interventions = pd.DataFrame({
            'Intervention': ['Current', 'Alerts', 'Discharge Team', 'Command Center'],
            'Avg_Boarding': [6.9, 4.8, 3.7, 2.4],
            'Annual_Savings': [0, 400000, 800000, 2200000]
        })
        
        ax4_twin = ax4.twinx()
        x = range(len(interventions))
        ax4.bar(x, interventions['Avg_Boarding'], alpha=0.7, label='Avg Boarding (h)')
        ax4_twin.plot(x, interventions['Annual_Savings']/1000000, 'ro-', 
                     linewidth=2, markersize=10, label='Savings ($M)')
        
        ax4.set_xticks(x)
        ax4.set_xticklabels(interventions['Intervention'], rotation=45)
        ax4.set_ylabel('Average Boarding Hours', fontsize=12)
        ax4_twin.set_ylabel('Annual Savings ($M)', fontsize=12)
        ax4.set_title('Intervention Impact Analysis', fontsize=14)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

def generate_sample_boarding_data(n_days=90):
    """
    Generate sample boarding data for demonstration
    """
    np.random.seed(42)
    
    # Generate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=n_days)
    
    # Number of admissions per day (varies by day of week)
    dates = []
    boarding_hours_list = []
    is_behavioral_list = []
    
    current_date = start_date
    while current_date <= end_date:
        dow = current_date.weekday()
        
        # More admissions on Monday/Tuesday
        if dow in [0, 1]:
            n_admits = np.random.poisson(25)
        else:
            n_admits = np.random.poisson(18)
        
        for _ in range(n_admits):
            # Hour of admission decision
            if dow in [0, 1]:  # Monday/Tuesday peaks
                hour = np.random.choice(range(24), p=[0.02]*6 + [0.08]*6 + [0.04]*12)
            else:
                hour = np.random.choice(range(24), p=[0.04]*24)
            
            # Behavioral health flag
            is_behavioral = np.random.binomial(1, 0.1)
            
            # Boarding hours (higher for behavioral health)
            if is_behavioral:
                boarding = np.random.gamma(3, 6)  # Mean ~18 hours
            else:
                boarding = np.random.gamma(2, 3.5)  # Mean ~7 hours
            
            dates.append(current_date)
            boarding_hours_list.append(boarding)
            is_behavioral_list.append(is_behavioral)
        
        current_date += timedelta(days=1)
    
    # Create dataframe
    df = pd.DataFrame({
        'date': dates,
        'boarding_hours': boarding_hours_list,
        'is_behavioral_health': is_behavioral_list
    })
    
    # Add derived fields
    df['hour_of_day'] = pd.to_datetime(df['date']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
    
    return df

def main():
    """
    Main execution function
    """
    print("ED Boarding Pattern Visualizer")
    print("=" * 50)
    
    # Generate sample data
    print("\nGenerating sample boarding data...")
    df = generate_sample_boarding_data()
    
    print(f"Total admissions analyzed: {len(df)}")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Average boarding time: {df['boarding_hours'].mean():.1f} hours")
    print(f"Behavioral health patients: {df['is_behavioral_health'].sum()} ({df['is_behavioral_health'].mean()*100:.1f}%)")
    
    # Create visualizer
    viz = BoardingVisualizer()
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    
    print("1. Creating boarding heatmap...")
    viz.create_boarding_heatmap(df)
    
    print("2. Creating behavioral health comparison...")
    viz.create_behavioral_health_comparison(df)
    
    print("3. Creating interactive dashboard...")
    viz.create_interactive_dashboard(df)
    
    print("4. Creating executive summary...")
    viz.generate_executive_summary(df)
    
    print("\nVisualizations saved:")
    print("- boarding_heatmap.png")
    print("- behavioral_health_boarding.png")
    print("- boarding_dashboard.html (interactive)")
    print("- executive_summary.png")
    
    # Key insights
    print("\n" + "="*50)
    print("KEY INSIGHTS")
    print("="*50)
    
    # Worst times
    worst_times = df.groupby(['day_of_week', 'hour_of_day'])['boarding_hours'].mean()
    worst_time = worst_times.idxmax()
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    print(f"1. Worst boarding time: {day_names[worst_time[0]]} at {worst_time[1]}:00")
    print(f"   Average boarding: {worst_times.max():.1f} hours")
    
    # Behavioral health impact
    bh_median = df[df['is_behavioral_health']==1]['boarding_hours'].median()
    med_median = df[df['is_behavioral_health']==0]['boarding_hours'].median()
    print(f"\n2. Behavioral health boarding: {bh_median:.1f}h vs {med_median:.1f}h medical")
    print(f"   That's {bh_median/med_median:.1f}x longer")
    
    # ECCQ compliance
    eccq_compliant = (df['boarding_hours'] <= 4).mean() * 100
    print(f"\n3. ECCQ compliance rate: {eccq_compliant:.1f}%")
    print(f"   Patients boarding >4 hours: {(df['boarding_hours'] > 4).sum()}")
    
    # Cost impact
    total_cost = df['boarding_hours'].sum() * 219
    print(f"\n4. Total boarding cost (90 days): ${total_cost:,.0f}")
    print(f"   Annualized: ${total_cost * 365/90:,.0f}")

if __name__ == "__main__":
    main()