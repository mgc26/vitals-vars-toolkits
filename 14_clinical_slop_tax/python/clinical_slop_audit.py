"""
Clinical Slop Audit Calculator
Quantifies the cost and impact of workflow fragmentation in your organization

Usage:
    python clinical_slop_audit.py

Outputs:
    - Clinical slop cost estimation
    - ROI calculator for workflow optimization
    - Recommendations based on audit findings
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json


class ClinicalSlopAuditor:
    """
    Calculates the organizational cost of clinical slop (fragmented workflows)
    """

    def __init__(self):
        # Default hourly rates (adjust for your organization)
        self.hourly_rates = {
            'Physician': 150.00,
            'Nurse': 90.00,
            'APP': 110.00  # Advanced Practice Provider
        }

        # Benchmark task-switching thresholds (from research)
        self.benchmarks = {
            'task_switches_per_hour': {
                'excellent': 80,
                'acceptable': 100,
                'concerning': 150,
                'crisis': 180
            },
            'documentation_pct': {
                'excellent': 30,
                'acceptable': 40,
                'concerning': 50,
                'crisis': 60
            },
            'after_hours_minutes': {
                'excellent': 15,
                'acceptable': 25,
                'concerning': 35,
                'crisis': 50
            }
        }

    def calculate_task_switching_cost(self,
                                     role: str,
                                     fte_count: int,
                                     avg_switches_per_hour: float,
                                     avg_daily_hours: float = 8,
                                     work_days_per_year: int = 240) -> dict:
        """
        Calculates the annual cost of excessive task-switching

        Research shows cognitive switching costs ~15 seconds per switch
        (context reorientation, attention restoration, task resumption lag)

        Args:
            role: Clinical role ('Physician', 'Nurse', 'APP')
            fte_count: Number of FTEs in this role
            avg_switches_per_hour: Measured task switches per hour
            avg_daily_hours: Average EHR hours per day
            work_days_per_year: Working days per year

        Returns:
            Dictionary with cost breakdown
        """
        hourly_rate = self.hourly_rates.get(role, 90.00)

        # Benchmark comparison
        benchmark_switches = self.benchmarks['task_switches_per_hour']['acceptable']
        excess_switches_per_hour = max(0, avg_switches_per_hour - benchmark_switches)

        # Cost calculation
        switching_cost_seconds = 15  # Research-based cognitive switching cost
        wasted_seconds_per_hour = excess_switches_per_hour * switching_cost_seconds
        wasted_hours_per_day = (wasted_seconds_per_hour / 3600) * avg_daily_hours
        wasted_hours_per_year = wasted_hours_per_day * work_days_per_year

        cost_per_fte = wasted_hours_per_year * hourly_rate
        total_annual_cost = cost_per_fte * fte_count

        # Assessment
        if avg_switches_per_hour <= self.benchmarks['task_switches_per_hour']['excellent']:
            status = 'Excellent'
        elif avg_switches_per_hour <= self.benchmarks['task_switches_per_hour']['acceptable']:
            status = 'Acceptable'
        elif avg_switches_per_hour <= self.benchmarks['task_switches_per_hour']['concerning']:
            status = 'Concerning'
        else:
            status = 'CRISIS'

        return {
            'role': role,
            'fte_count': fte_count,
            'avg_switches_per_hour': avg_switches_per_hour,
            'benchmark_switches_per_hour': benchmark_switches,
            'excess_switches_per_hour': excess_switches_per_hour,
            'wasted_hours_per_fte_per_year': round(wasted_hours_per_year, 1),
            'cost_per_fte_per_year': round(cost_per_fte, 2),
            'total_annual_cost': round(total_annual_cost, 2),
            'status': status
        }

    def calculate_redundancy_cost(self,
                                  role: str,
                                  fte_count: int,
                                  redundant_entries_per_day: float,
                                  avg_time_per_entry_minutes: float = 2.0,
                                  work_days_per_year: int = 240) -> dict:
        """
        Calculates cost of redundant data entry (entering same info multiple times)

        Common examples:
        - Medication reconciliation in ED, admission, pharmacy
        - Allergies re-entered at each encounter
        - Problem lists maintained separately by departments

        Args:
            role: Clinical role
            fte_count: Number of FTEs
            redundant_entries_per_day: Avg redundant entries per clinician per day
            avg_time_per_entry_minutes: Avg time to re-enter information
            work_days_per_year: Working days per year

        Returns:
            Dictionary with cost breakdown
        """
        hourly_rate = self.hourly_rates.get(role, 90.00)
        cost_per_minute = hourly_rate / 60

        # Annual calculations
        redundant_entries_per_year = redundant_entries_per_day * work_days_per_year
        wasted_minutes_per_year = redundant_entries_per_year * avg_time_per_entry_minutes
        wasted_hours_per_year = wasted_minutes_per_year / 60

        cost_per_fte = wasted_hours_per_year * hourly_rate
        total_annual_cost = cost_per_fte * fte_count

        return {
            'role': role,
            'fte_count': fte_count,
            'redundant_entries_per_day': redundant_entries_per_day,
            'avg_time_per_entry_minutes': avg_time_per_entry_minutes,
            'wasted_hours_per_fte_per_year': round(wasted_hours_per_year, 1),
            'cost_per_fte_per_year': round(cost_per_fte, 2),
            'total_annual_cost': round(total_annual_cost, 2)
        }

    def calculate_incomplete_handoff_cost(self,
                                         role: str,
                                         fte_count: int,
                                         incomplete_handoffs_per_week: float,
                                         avg_cleanup_time_minutes: float = 15.0,
                                         work_weeks_per_year: int = 48) -> dict:
        """
        Calculates cost of incomplete handoffs requiring downstream cleanup

        Examples:
        - Incomplete discharge instructions requiring callback
        - Missing medication reconciliation requiring rework
        - Vague notes requiring follow-up questions

        Args:
            role: Clinical role doing the cleanup work
            fte_count: Number of FTEs
            incomplete_handoffs_per_week: Avg incomplete handoffs per clinician per week
            avg_cleanup_time_minutes: Time to fix incomplete work
            work_weeks_per_year: Working weeks per year

        Returns:
            Dictionary with cost breakdown
        """
        hourly_rate = self.hourly_rates.get(role, 90.00)

        # Annual calculations
        incomplete_handoffs_per_year = incomplete_handoffs_per_week * work_weeks_per_year
        wasted_minutes_per_year = incomplete_handoffs_per_year * avg_cleanup_time_minutes
        wasted_hours_per_year = wasted_minutes_per_year / 60

        cost_per_fte = wasted_hours_per_year * hourly_rate
        total_annual_cost = cost_per_fte * fte_count

        return {
            'role': role,
            'fte_count': fte_count,
            'incomplete_handoffs_per_week': incomplete_handoffs_per_week,
            'avg_cleanup_time_minutes': avg_cleanup_time_minutes,
            'wasted_hours_per_fte_per_year': round(wasted_hours_per_year, 1),
            'cost_per_fte_per_year': round(cost_per_fte, 2),
            'total_annual_cost': round(total_annual_cost, 2)
        }

    def calculate_optimization_roi(self,
                                  current_annual_cost: float,
                                  time_savings_pct: float,
                                  implementation_cost: float,
                                  implementation_hours: int = 0,
                                  hourly_implementation_rate: float = 150.00) -> dict:
        """
        Calculates ROI for workflow optimization project

        Args:
            current_annual_cost: Total annual cost of clinical slop
            time_savings_pct: Expected % reduction in slop (e.g., 20.0 for 20%)
            implementation_cost: One-time cost (software, consulting, etc.)
            implementation_hours: Internal staff hours needed
            hourly_implementation_rate: Blended rate for implementation work

        Returns:
            Dictionary with ROI metrics
        """
        # Annual savings
        annual_savings = current_annual_cost * (time_savings_pct / 100)

        # Total implementation cost
        total_impl_cost = implementation_cost + (implementation_hours * hourly_implementation_rate)

        # ROI calculations
        payback_period_months = (total_impl_cost / annual_savings) * 12 if annual_savings > 0 else 999
        roi_1year = ((annual_savings - total_impl_cost) / total_impl_cost * 100) if total_impl_cost > 0 else 0
        roi_3year = (((annual_savings * 3) - total_impl_cost) / total_impl_cost * 100) if total_impl_cost > 0 else 0

        return {
            'current_annual_cost': round(current_annual_cost, 2),
            'time_savings_pct': time_savings_pct,
            'annual_savings': round(annual_savings, 2),
            'implementation_cost': round(total_impl_cost, 2),
            'payback_period_months': round(payback_period_months, 1),
            'roi_1year_pct': round(roi_1year, 1),
            'roi_3year_pct': round(roi_3year, 1),
            '3year_net_savings': round((annual_savings * 3) - total_impl_cost, 2)
        }

    def generate_audit_report(self, audit_data: dict) -> str:
        """
        Generates formatted audit report

        Args:
            audit_data: Dictionary containing all audit calculations

        Returns:
            Formatted string report
        """
        report = []
        report.append("=" * 80)
        report.append("CLINICAL SLOP AUDIT REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("=" * 80)
        report.append("")

        if 'task_switching' in audit_data:
            report.append("TASK-SWITCHING COST ANALYSIS")
            report.append("-" * 80)
            for result in audit_data['task_switching']:
                report.append(f"Role: {result['role']}")
                report.append(f"  FTE Count: {result['fte_count']}")
                report.append(f"  Avg Switches/Hour: {result['avg_switches_per_hour']} (Status: {result['status']})")
                report.append(f"  Benchmark: {result['benchmark_switches_per_hour']} switches/hour")
                report.append(f"  Excess Switches: {result['excess_switches_per_hour']}/hour")
                report.append(f"  Wasted Hours/FTE/Year: {result['wasted_hours_per_fte_per_year']}")
                report.append(f"  Cost/FTE/Year: ${result['cost_per_fte_per_year']:,.2f}")
                report.append(f"  TOTAL ANNUAL COST: ${result['total_annual_cost']:,.2f}")
                report.append("")

        if 'redundancy' in audit_data:
            report.append("REDUNDANT DOCUMENTATION COST ANALYSIS")
            report.append("-" * 80)
            for result in audit_data['redundancy']:
                report.append(f"Role: {result['role']}")
                report.append(f"  Redundant Entries/Day: {result['redundant_entries_per_day']}")
                report.append(f"  Wasted Hours/FTE/Year: {result['wasted_hours_per_fte_per_year']}")
                report.append(f"  TOTAL ANNUAL COST: ${result['total_annual_cost']:,.2f}")
                report.append("")

        if 'incomplete_handoffs' in audit_data:
            report.append("INCOMPLETE HANDOFF CLEANUP COST ANALYSIS")
            report.append("-" * 80)
            for result in audit_data['incomplete_handoffs']:
                report.append(f"Role: {result['role']}")
                report.append(f"  Incomplete Handoffs/Week: {result['incomplete_handoffs_per_week']}")
                report.append(f"  Avg Cleanup Time: {result['avg_cleanup_time_minutes']} minutes")
                report.append(f"  Wasted Hours/FTE/Year: {result['wasted_hours_per_fte_per_year']}")
                report.append(f"  TOTAL ANNUAL COST: ${result['total_annual_cost']:,.2f}")
                report.append("")

        # Total summary
        total_cost = 0
        for category in ['task_switching', 'redundancy', 'incomplete_handoffs']:
            if category in audit_data:
                total_cost += sum(r['total_annual_cost'] for r in audit_data[category])

        report.append("=" * 80)
        report.append(f"TOTAL ANNUAL CLINICAL SLOP COST: ${total_cost:,.2f}")
        report.append("=" * 80)
        report.append("")

        if 'roi' in audit_data:
            roi = audit_data['roi']
            report.append("OPTIMIZATION ROI PROJECTION")
            report.append("-" * 80)
            report.append(f"Expected Time Savings: {roi['time_savings_pct']}%")
            report.append(f"Annual Savings: ${roi['annual_savings']:,.2f}")
            report.append(f"Implementation Cost: ${roi['implementation_cost']:,.2f}")
            report.append(f"Payback Period: {roi['payback_period_months']} months")
            report.append(f"1-Year ROI: {roi['roi_1year_pct']}%")
            report.append(f"3-Year ROI: {roi['roi_3year_pct']}%")
            report.append(f"3-Year Net Savings: ${roi['3year_net_savings']:,.2f}")
            report.append("")

        return "\n".join(report)


def run_example_audit():
    """
    Example audit for a 400-bed hospital
    Customize these values for your organization
    """
    auditor = ClinicalSlopAuditor()

    audit_data = {}

    # Task-switching analysis
    audit_data['task_switching'] = [
        auditor.calculate_task_switching_cost(
            role='Physician',
            fte_count=150,
            avg_switches_per_hour=185.8,  # From research (Moy et al. 2023)
            avg_daily_hours=6
        ),
        auditor.calculate_task_switching_cost(
            role='Nurse',
            fte_count=600,
            avg_switches_per_hour=120.0,
            avg_daily_hours=8
        )
    ]

    # Redundant documentation
    audit_data['redundancy'] = [
        auditor.calculate_redundancy_cost(
            role='Nurse',
            fte_count=600,
            redundant_entries_per_day=8.0,  # Med recs, allergies, problem lists
            avg_time_per_entry_minutes=2.5
        )
    ]

    # Incomplete handoffs
    audit_data['incomplete_handoffs'] = [
        auditor.calculate_incomplete_handoff_cost(
            role='Nurse',
            fte_count=600,
            incomplete_handoffs_per_week=3.0,  # Incomplete discharge instructions, etc.
            avg_cleanup_time_minutes=15.0
        )
    ]

    # Calculate total cost
    total_cost = sum(
        sum(r['total_annual_cost'] for r in category)
        for category in audit_data.values()
    )

    # ROI projection (20% reduction, Duke Health achieved 18.5%)
    audit_data['roi'] = auditor.calculate_optimization_roi(
        current_annual_cost=total_cost,
        time_savings_pct=20.0,
        implementation_cost=50000,  # Modest implementation cost
        implementation_hours=200,   # Informatics team time
        hourly_implementation_rate=120.00
    )

    # Generate report
    report = auditor.generate_audit_report(audit_data)
    print(report)

    # Save to file
    with open('clinical_slop_audit_report.txt', 'w') as f:
        f.write(report)

    print("\nReport saved to: clinical_slop_audit_report.txt")


if __name__ == '__main__':
    print("Clinical Slop Audit Calculator")
    print("=" * 80)
    print("\nRunning example audit for 400-bed hospital...")
    print("(Customize parameters in run_example_audit() for your organization)\n")

    run_example_audit()
