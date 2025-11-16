#!/usr/bin/env python3
"""
Nurse Time Valuation Calculator

Calculates the true productivity-adjusted cost per minute of RN time
based on BLS wage data and standard benefits multipliers.

Based on evidence from:
- Bureau of Labor Statistics (2024) RN wage data
- Standard healthcare labor cost multipliers (1.8-2.0x base wage)

Usage:
    python nurse_time_calculator.py
"""

import pandas as pd
import numpy as np


class NurseTimeCalculator:
    """Calculate the fully-loaded cost per minute of RN time"""

    # National median RN hourly wage (BLS 2024)
    NATIONAL_MEDIAN_WAGE = 47.32

    # Standard benefits multiplier range
    BENEFITS_MULTIPLIER_LOW = 1.8
    BENEFITS_MULTIPLIER_HIGH = 2.0

    # Regional wage adjustments (example data - replace with actual market data)
    REGIONAL_ADJUSTMENTS = {
        'San Jose, CA': 1.94,
        'San Francisco, CA': 1.89,
        'Sacramento, CA': 1.47,
        'New York, NY': 1.76,
        'Boston, MA': 1.68,
        'Rural South': 0.85,
        'Rural Midwest': 0.90,
        'National Average': 1.0
    }

    def __init__(self, hourly_wage=None, region='National Average'):
        """
        Initialize calculator

        Args:
            hourly_wage: Base hourly wage (if None, uses national median)
            region: Geographic region for wage adjustment
        """
        if hourly_wage is None:
            # Apply regional adjustment to national median
            adjustment = self.REGIONAL_ADJUSTMENTS.get(region, 1.0)
            self.base_wage = self.NATIONAL_MEDIAN_WAGE * adjustment
        else:
            self.base_wage = hourly_wage

        self.region = region

    def calculate_fully_loaded_cost(self, benefits_multiplier=None):
        """
        Calculate fully-loaded hourly cost including benefits

        Args:
            benefits_multiplier: Multiplier for benefits (default: midpoint of range)

        Returns:
            dict with cost breakdown
        """
        if benefits_multiplier is None:
            benefits_multiplier = (self.BENEFITS_MULTIPLIER_LOW +
                                 self.BENEFITS_MULTIPLIER_HIGH) / 2

        fully_loaded_hourly = self.base_wage * benefits_multiplier
        cost_per_minute = fully_loaded_hourly / 60

        return {
            'base_hourly_wage': round(self.base_wage, 2),
            'benefits_multiplier': benefits_multiplier,
            'fully_loaded_hourly': round(fully_loaded_hourly, 2),
            'cost_per_minute': round(cost_per_minute, 2),
            'cost_per_second': round(cost_per_minute / 60, 4),
            'region': self.region
        }

    def calculate_waste_cost(self, minutes_wasted_per_shift, nurses_count,
                            shifts_per_year=730):
        """
        Calculate annual cost of wasted time

        Args:
            minutes_wasted_per_shift: Minutes of non-value-added time per shift
            nurses_count: Number of RN FTEs
            shifts_per_year: Shifts per nurse per year (default: 730 = 2 shifts/day)

        Returns:
            dict with waste cost analysis
        """
        costs = self.calculate_fully_loaded_cost()
        cost_per_minute = costs['cost_per_minute']

        waste_per_shift = minutes_wasted_per_shift * cost_per_minute
        waste_per_nurse_annual = waste_per_shift * shifts_per_year
        total_annual_waste = waste_per_nurse_annual * nurses_count

        return {
            'minutes_wasted_per_shift': minutes_wasted_per_shift,
            'cost_per_wasted_minute': cost_per_minute,
            'waste_cost_per_shift': round(waste_per_shift, 2),
            'waste_cost_per_nurse_annual': round(waste_per_nurse_annual, 2),
            'total_nurses': nurses_count,
            'total_annual_waste': round(total_annual_waste, 2),
            'hours_wasted_annual': round(minutes_wasted_per_shift *
                                        shifts_per_year * nurses_count / 60, 2)
        }

    def calculate_intervention_roi(self, minutes_saved_per_shift,
                                   implementation_cost, nurses_count,
                                   shifts_per_year=730):
        """
        Calculate ROI for a time-saving intervention

        Args:
            minutes_saved_per_shift: Minutes returned to productive time
            implementation_cost: One-time or annual cost of intervention
            nurses_count: Number of RNs affected
            shifts_per_year: Shifts per nurse per year

        Returns:
            dict with ROI analysis
        """
        costs = self.calculate_fully_loaded_cost()
        cost_per_minute = costs['cost_per_minute']

        value_per_shift = minutes_saved_per_shift * cost_per_minute
        annual_value_per_nurse = value_per_shift * shifts_per_year
        total_annual_value = annual_value_per_nurse * nurses_count

        net_annual_benefit = total_annual_value - implementation_cost
        roi_percentage = (net_annual_benefit / implementation_cost * 100) if implementation_cost > 0 else float('inf')
        payback_months = (implementation_cost / (total_annual_value / 12)) if total_annual_value > 0 else float('inf')

        return {
            'minutes_saved_per_shift': minutes_saved_per_shift,
            'annual_hours_saved': round(minutes_saved_per_shift *
                                       shifts_per_year * nurses_count / 60, 2),
            'total_annual_value': round(total_annual_value, 2),
            'implementation_cost': implementation_cost,
            'net_annual_benefit': round(net_annual_benefit, 2),
            'roi_percentage': round(roi_percentage, 1),
            'payback_period_months': round(payback_months, 1)
        }


def print_cost_breakdown(calculator):
    """Print formatted cost breakdown"""
    costs = calculator.calculate_fully_loaded_cost()

    print("\n" + "="*60)
    print("NURSE TIME VALUATION - COST BREAKDOWN")
    print("="*60)
    print(f"\nRegion: {costs['region']}")
    print(f"Base Hourly Wage: ${costs['base_hourly_wage']:.2f}")
    print(f"Benefits Multiplier: {costs['benefits_multiplier']:.1f}x")
    print(f"\nFully-Loaded Hourly Cost: ${costs['fully_loaded_hourly']:.2f}")
    print(f"Cost per Minute: ${costs['cost_per_minute']:.2f}")
    print(f"Cost per Second: ${costs['cost_per_second']:.4f}")
    print("="*60 + "\n")


def example_waste_analysis():
    """Example: Calculate cost of documentation waste"""
    print("\n" + "="*60)
    print("EXAMPLE: DOCUMENTATION WASTE ANALYSIS")
    print("="*60)
    print("\nScenario: Nurses spend 147.5 minutes/shift on documentation")
    print("If 50 minutes could be eliminated through EHR optimization...")
    print()

    calc = NurseTimeCalculator()
    waste = calc.calculate_waste_cost(
        minutes_wasted_per_shift=50,
        nurses_count=500,  # 500 RN FTEs
        shifts_per_year=730
    )

    print(f"Minutes of recoverable time per shift: {waste['minutes_wasted_per_shift']}")
    print(f"Cost per wasted minute: ${waste['cost_per_wasted_minute']:.2f}")
    print(f"\nWaste cost per shift: ${waste['waste_cost_per_shift']:.2f}")
    print(f"Waste cost per nurse (annual): ${waste['waste_cost_per_nurse_annual']:,.2f}")
    print(f"\nTotal nursing staff: {waste['total_nurses']} FTEs")
    print(f"Total annual waste: ${waste['total_annual_waste']:,.2f}")
    print(f"Annual hours wasted: {waste['hours_wasted_annual']:,.2f}")
    print("="*60 + "\n")


def example_roi_analysis():
    """Example: ROI of EHR optimization"""
    print("\n" + "="*60)
    print("EXAMPLE: EHR OPTIMIZATION ROI")
    print("="*60)
    print("\nScenario: Duke Health-style flowsheet optimization")
    print("Implementation: 24 hours of informatics team time @ $150/hr")
    print("Result: Save 5 minutes per shift per nurse")
    print()

    calc = NurseTimeCalculator()
    roi = calc.calculate_intervention_roi(
        minutes_saved_per_shift=5,
        implementation_cost=24 * 150,  # $3,600
        nurses_count=500,
        shifts_per_year=730
    )

    print(f"Minutes saved per shift: {roi['minutes_saved_per_shift']}")
    print(f"Annual hours saved: {roi['annual_hours_saved']:,.2f}")
    print(f"\nTotal annual value: ${roi['total_annual_value']:,.2f}")
    print(f"Implementation cost: ${roi['implementation_cost']:,.2f}")
    print(f"Net annual benefit: ${roi['net_annual_benefit']:,.2f}")
    print(f"\nROI: {roi['roi_percentage']:.1f}%")
    print(f"Payback period: {roi['payback_period_months']:.1f} months")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Initialize calculator with national median wage
    calculator = NurseTimeCalculator()

    # Print basic cost breakdown
    print_cost_breakdown(calculator)

    # Run example analyses
    example_waste_analysis()
    example_roi_analysis()

    print("\nNOTE: Replace example values with your organization's actual data.")
    print("Consider regional wage adjustments and local benefits costs.\n")
