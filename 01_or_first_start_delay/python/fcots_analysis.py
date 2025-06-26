#!/usr/bin/env python3
"""
First-Case On-Time Start (FCOTS) Analysis
Vitals & Variables Issue #1

Analyzes OR first-case delays and generates visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Set style for cleaner plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def generate_mock_data(start_date='2024-01-01', days=365, num_ors=10):
    """
    Generate realistic OR first-case delay data
    
    Parameters:
    - start_date: Start date for the dataset
    - days: Number of days to generate
    - num_ors: Number of operating rooms
    
    Returns:
    - DataFrame with first-case delay data
    """
    
    # Create date range (weekdays only)
    dates = pd.bdate_range(start=start_date, periods=days)
    
    # Delay reasons with realistic probabilities
    delay_reasons = {
        'Surgeon late': 0.52,
        'Pre-op incomplete': 0.18,
        'Room not ready': 0.13,
        'Anesthesia delay': 0.10,
        'Other': 0.07
    }
    
    data = []
    
    for date in dates:
        # Skip some weekends/holidays randomly (5% chance)
        if np.random.random() < 0.05:
            continue
            
        for room_id in range(1, num_ors + 1):
            # Base delay varies by day of week (Mondays worse)
            dow_factor = 1.3 if date.weekday() == 0 else 1.0
            
            # Room-specific factors (some rooms consistently worse)
            room_factor = 1.2 if room_id in [2, 7] else 1.0
            
            # Seasonal factor (winter months slightly worse)
            season_factor = 1.1 if date.month in [12, 1, 2] else 1.0
            
            # Improvement trend over time (simulating QI intervention)
            days_elapsed = (date - dates[0]).days
            improvement_factor = max(0.5, 1 - (days_elapsed / 365) * 0.3)
            
            # Calculate delay
            base_delay = np.random.gamma(2, 5)  # Right-skewed distribution
            delay = base_delay * dow_factor * room_factor * season_factor * improvement_factor
            
            # 30% chance of being on-time or early
            if np.random.random() < 0.30:
                delay = np.random.normal(-2, 3)  # Early by a few minutes
            
            delay = round(delay)
            
            # Select delay reason based on probabilities
            if delay > 0:
                reason = np.random.choice(
                    list(delay_reasons.keys()),
                    p=list(delay_reasons.values())
                )
            else:
                reason = 'On time'
            
            scheduled_time = pd.Timestamp(date.strftime('%Y-%m-%d') + ' 07:30:00')
            actual_time = scheduled_time + timedelta(minutes=int(delay))
            
            data.append({
                'date': date,
                'room_id': room_id,
                'scheduled_time': scheduled_time,
                'actual_in_time': actual_time,
                'delay_minutes': int(delay),
                'delay_reason': reason,
                'on_time_flag': delay <= 0
            })
    
    return pd.DataFrame(data)


def analyze_fcots(df):
    """
    Perform comprehensive FCOTS analysis
    
    Parameters:
    - df: DataFrame with delay data
    
    Returns:
    - Dictionary with analysis results
    """
    
    results = {}
    
    # Overall metrics
    results['overall_fcots'] = (df['on_time_flag'].sum() / len(df)) * 100
    results['median_delay'] = df[df['delay_minutes'] > 0]['delay_minutes'].median()
    results['total_delay_hours'] = df[df['delay_minutes'] > 0]['delay_minutes'].sum() / 60
    
    # By delay reason
    delay_breakdown = df[df['delay_minutes'] > 0].groupby('delay_reason').agg({
        'delay_minutes': ['count', 'sum', 'mean']
    }).round(1)
    results['delay_breakdown'] = delay_breakdown
    
    # Daily trends
    daily_fcots = df.groupby('date')['on_time_flag'].mean() * 100
    results['daily_fcots'] = daily_fcots
    
    # By day of week
    df['dow'] = df['date'].dt.day_name()
    dow_fcots = df.groupby('dow')['on_time_flag'].mean() * 100
    results['dow_fcots'] = dow_fcots
    
    # By room
    room_fcots = df.groupby('room_id')['on_time_flag'].mean() * 100
    results['room_fcots'] = room_fcots
    
    return results


def create_visualizations(df, results, output_dir='../assets'):
    """
    Create publication-ready visualizations
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Run chart with trend line
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Daily data
    daily = results['daily_fcots']
    ax.plot(daily.index, daily.values, 'o-', markersize=4, alpha=0.6, label='Daily FCOTS %')
    
    # 30-day moving average
    ma30 = daily.rolling(30, center=True).mean()
    ax.plot(ma30.index, ma30.values, linewidth=3, label='30-day average')
    
    # Target line
    ax.axhline(85, linestyle='--', color='green', linewidth=2, label='Target: 85%')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('First-Case On-Time %', fontsize=12)
    ax.set_title('First-Case On-Time Start Performance', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/fcots_run_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Delay reasons Pareto chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Get delay counts by reason
    delay_counts = df[df['delay_minutes'] > 0]['delay_reason'].value_counts()
    
    # Bar chart
    bars = ax1.bar(range(len(delay_counts)), delay_counts.values)
    ax1.set_xticks(range(len(delay_counts)))
    ax1.set_xticklabels(delay_counts.index, rotation=45, ha='right')
    ax1.set_ylabel('Number of Delays', fontsize=12)
    ax1.set_title('Delay Reasons - Frequency', fontsize=14, fontweight='bold')
    
    # Color bars
    colors = sns.color_palette('husl', len(delay_counts))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Cumulative percentage line
    cumsum = delay_counts.cumsum() / delay_counts.sum() * 100
    ax1_twin = ax1.twinx()
    ax1_twin.plot(range(len(delay_counts)), cumsum.values, 'ro-', linewidth=2, markersize=8)
    ax1_twin.set_ylabel('Cumulative %', fontsize=12)
    ax1_twin.set_ylim(0, 105)
    
    # Total delay minutes by reason
    delay_mins = df[df['delay_minutes'] > 0].groupby('delay_reason')['delay_minutes'].sum().sort_values(ascending=False)
    bars2 = ax2.bar(range(len(delay_mins)), delay_mins.values)
    ax2.set_xticks(range(len(delay_mins)))
    ax2.set_xticklabels(delay_mins.index, rotation=45, ha='right')
    ax2.set_ylabel('Total Delay Minutes', fontsize=12)
    ax2.set_title('Delay Reasons - Total Impact', fontsize=14, fontweight='bold')
    
    # Color bars
    for bar, color in zip(bars2, colors):
        bar.set_color(color)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/delay_pareto.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Day of week analysis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    dow_data = results['dow_fcots'].reindex(dow_order)
    
    bars = ax.bar(dow_data.index, dow_data.values)
    ax.axhline(85, linestyle='--', color='green', linewidth=2, label='Target: 85%')
    ax.set_ylabel('First-Case On-Time %', fontsize=12)
    ax.set_title('FCOTS by Day of Week', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # Color Monday differently
    bars[0].set_color('red')
    bars[0].set_alpha(0.7)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/fcots_by_dow.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Room performance heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create weekly room performance matrix
    df['week'] = df['date'].dt.isocalendar().week
    room_weekly = df.groupby(['week', 'room_id'])['on_time_flag'].mean() * 100
    room_matrix = room_weekly.unstack(fill_value=0)
    
    # Create heatmap
    sns.heatmap(room_matrix.T, cmap='RdYlGn', center=85, 
                annot=False, fmt='.0f', cbar_kws={'label': 'FCOTS %'})
    ax.set_xlabel('Week of Year', fontsize=12)
    ax.set_ylabel('Operating Room', fontsize=12)
    ax.set_title('OR Performance Heatmap', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/room_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualizations saved to assets/")


def calculate_financial_impact(results, or_cost_per_min=100, num_ors=10):
    """
    Calculate financial impact of delays
    """
    
    print("\n=== FINANCIAL IMPACT ANALYSIS ===")
    print(f"Assumptions: ${or_cost_per_min}/min, {num_ors} ORs")
    print("-" * 40)
    
    # Current state
    current_fcots = results['overall_fcots']
    total_delay_hours = results['total_delay_hours']
    annual_delay_cost = total_delay_hours * 60 * or_cost_per_min
    
    print(f"Current FCOTS: {current_fcots:.1f}%")
    print(f"Total delay hours (annual): {total_delay_hours:,.0f}")
    print(f"Annual delay cost: ${annual_delay_cost:,.0f}")
    
    # Improvement scenarios
    print("\nImprovement Scenarios:")
    for target in [75, 80, 85, 90]:
        if target > current_fcots:
            improvement = target - current_fcots
            hours_saved = total_delay_hours * (improvement / (100 - current_fcots))
            savings = hours_saved * 60 * or_cost_per_min
            print(f"  Reach {target}% FCOTS: Save {hours_saved:,.0f} hours, ${savings:,.0f}")


def main():
    """
    Main analysis pipeline
    """
    
    print("=== FIRST-CASE ON-TIME START ANALYSIS ===")
    print("Generating mock data...")
    
    # Generate or load data
    if os.path.exists('data/fcots_data.csv'):
        df = pd.read_csv('data/fcots_data.csv', parse_dates=['date', 'scheduled_time', 'actual_in_time'])
        print(f"Loaded existing data: {len(df)} records")
    else:
        df = generate_mock_data()
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/fcots_data.csv', index=False)
        print(f"Generated mock data: {len(df)} records")
    
    # Perform analysis
    print("\nAnalyzing data...")
    results = analyze_fcots(df)
    
    # Print key metrics
    print("\n=== KEY METRICS ===")
    print(f"Overall FCOTS: {results['overall_fcots']:.1f}%")
    print(f"Median delay (when late): {results['median_delay']:.0f} minutes")
    print(f"Total delay time: {results['total_delay_hours']:,.0f} hours")
    
    print("\n=== DELAY BREAKDOWN ===")
    print(results['delay_breakdown'])
    
    # Create visualizations
    print("\nCreating visualizations...")
    create_visualizations(df, results)
    
    # Calculate financial impact
    calculate_financial_impact(results)
    
    # Export summary data
    print("\nExporting summary data...")
    summary_df = pd.DataFrame({
        'metric': ['Overall FCOTS %', 'Median Delay (min)', 'Total Delay Hours', 'Annual Cost @ $100/min'],
        'value': [
            f"{results['overall_fcots']:.1f}%",
            f"{results['median_delay']:.0f}",
            f"{results['total_delay_hours']:,.0f}",
            f"${results['total_delay_hours'] * 60 * 100:,.0f}"
        ]
    })
    summary_df.to_csv('data/fcots_summary.csv', index=False)
    
    print("\nAnalysis complete! Check the assets/ folder for visualizations.")


if __name__ == "__main__":
    main()