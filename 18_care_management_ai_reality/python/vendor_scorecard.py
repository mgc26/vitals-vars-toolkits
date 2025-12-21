"""
Vendor Performance Scorecard
Vitals & Variables Edition 18: Care Management AI vs. Member Reality

This module generates vendor performance scorecards that measure what matters:
member outcomes, not just SLA compliance.

Key insight: A vendor can hit every process metric and still fail if
members don't improve. "Touches" and "outreach attempts" are vanity metrics.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json


class VendorType(Enum):
    """Categories of care management vendors."""
    TRANSPORTATION = "Transportation"
    CARE_MANAGEMENT = "Care Management"
    PBM = "Pharmacy Benefit Manager"
    TELEHEALTH = "Telehealth"
    BEHAVIORAL_HEALTH = "Behavioral Health"
    SDOH_SERVICES = "SDOH Services"


class PerformanceGrade(Enum):
    """Vendor performance grades based on outcome impact."""
    A = "Effective - Measurable outcome improvement"
    B = "Moderate - Some outcome improvement"
    C = "Process Compliant - Meets SLAs but limited outcomes"
    D = "Ineffective - High activity, low impact"
    F = "Failing - Not meeting SLAs or outcomes"


@dataclass
class VendorMetrics:
    """Core metrics for vendor evaluation."""
    vendor_name: str
    vendor_type: VendorType
    members_served: int
    total_interventions: int
    successful_completions: int
    outcomes_improved: int
    cost_per_intervention: float
    cost_per_outcome: float


@dataclass
class VendorScorecard:
    """Complete vendor scorecard with grade and recommendations."""
    vendor_name: str
    vendor_type: VendorType
    grade: PerformanceGrade
    process_score: float  # 0-100
    outcome_score: float  # 0-100
    efficiency_score: float  # 0-100
    overall_score: float  # 0-100
    strengths: List[str]
    concerns: List[str]
    recommendations: List[str]
    key_metrics: Dict[str, float]


class VendorScorer:
    """
    Scores vendors based on outcome impact, not just process compliance.

    Based on evidence that high-touch, high-volume interventions often
    fail to move outcomes (Finkelstein et al., 2020 Camden Coalition RCT).
    """

    # Benchmark thresholds by vendor type
    BENCHMARKS = {
        VendorType.TRANSPORTATION: {
            'completion_rate': {'good': 0.85, 'acceptable': 0.70, 'poor': 0.50},
            'care_delivery_rate': {'good': 0.75, 'acceptable': 0.60, 'poor': 0.40},
            'cost_per_outcome': {'good': 50, 'acceptable': 100, 'poor': 200}
        },
        VendorType.CARE_MANAGEMENT: {
            'contact_rate': {'good': 0.60, 'acceptable': 0.40, 'poor': 0.25},
            'engagement_rate': {'good': 0.50, 'acceptable': 0.35, 'poor': 0.20},
            'gap_closure_rate': {'good': 0.40, 'acceptable': 0.25, 'poor': 0.10},
            'cost_per_gap_closed': {'good': 150, 'acceptable': 300, 'poor': 600}
        },
        VendorType.PBM: {
            'adherence_rate': {'good': 0.80, 'acceptable': 0.70, 'poor': 0.55},
            'abandonment_rate': {'good': 0.05, 'acceptable': 0.10, 'poor': 0.20},
            'generic_fill_rate': {'good': 0.85, 'acceptable': 0.75, 'poor': 0.60}
        }
    }

    def __init__(self, outcome_weight: float = 0.5, process_weight: float = 0.3,
                 efficiency_weight: float = 0.2):
        """
        Initialize scorer with configurable weights.

        Args:
            outcome_weight: Weight for outcome metrics (default 0.5)
            process_weight: Weight for process metrics (default 0.3)
            efficiency_weight: Weight for efficiency metrics (default 0.2)
        """
        self.outcome_weight = outcome_weight
        self.process_weight = process_weight
        self.efficiency_weight = efficiency_weight

    def score_transportation_vendor(
        self,
        vendor_name: str,
        rides_scheduled: int,
        rides_completed: int,
        appointments_kept: int,
        appointments_missed: int,
        driver_no_shows: int,
        total_cost: float,
        ride_type: str = "MIXED"
    ) -> VendorScorecard:
        """
        Score transportation vendor on outcome delivery, not just rides.

        Based on Chaiyachati et al. (2018): free rideshare had no effect on
        no-show rates. Only 25% of offered rides were used.
        """
        benchmarks = self.BENCHMARKS[VendorType.TRANSPORTATION]
        strengths = []
        concerns = []
        recommendations = []

        # Process metrics
        completion_rate = rides_completed / max(rides_scheduled, 1)
        driver_reliability = 1 - (driver_no_shows / max(rides_scheduled, 1))

        # Outcome metrics
        total_appointments = appointments_kept + appointments_missed
        care_delivery_rate = appointments_kept / max(total_appointments, 1) if total_appointments > 0 else 0

        # Efficiency metrics
        cost_per_ride = total_cost / max(rides_completed, 1)
        cost_per_outcome = total_cost / max(appointments_kept, 1) if appointments_kept > 0 else float('inf')

        # Score each dimension
        process_score = self._score_metric(completion_rate, benchmarks['completion_rate']) * 0.6
        process_score += self._score_metric(driver_reliability, {'good': 0.95, 'acceptable': 0.90, 'poor': 0.80}) * 0.4

        outcome_score = self._score_metric(care_delivery_rate, benchmarks['care_delivery_rate'])

        efficiency_score = self._score_metric_inverse(cost_per_outcome, benchmarks['cost_per_outcome'])

        # Identify strengths and concerns
        if completion_rate >= benchmarks['completion_rate']['good']:
            strengths.append(f"High ride completion rate ({completion_rate:.0%})")
        if care_delivery_rate >= benchmarks['care_delivery_rate']['good']:
            strengths.append(f"Strong care delivery rate ({care_delivery_rate:.0%})")

        if completion_rate >= 0.8 and care_delivery_rate < 0.5:
            concerns.append("High ride completion but low care delivery - rides not translating to care")
            recommendations.append("Investigate post-drop-off barriers (clinic navigation, wait anxiety)")

        if ride_type == "APP_BASED" and care_delivery_rate < 0.6:
            concerns.append("App-based rides showing limited effectiveness")
            recommendations.append("Consider escorted transport for high-need members (Chaiyachati 2018)")

        if driver_no_shows / max(rides_scheduled, 1) > 0.1:
            concerns.append(f"Driver no-show rate {driver_no_shows/rides_scheduled:.0%} exceeds threshold")
            recommendations.append("Review driver accountability provisions in contract")

        # Calculate overall score
        overall_score = (
            outcome_score * self.outcome_weight +
            process_score * self.process_weight +
            efficiency_score * self.efficiency_weight
        )

        grade = self._determine_grade(overall_score, outcome_score)

        return VendorScorecard(
            vendor_name=vendor_name,
            vendor_type=VendorType.TRANSPORTATION,
            grade=grade,
            process_score=round(process_score, 1),
            outcome_score=round(outcome_score, 1),
            efficiency_score=round(efficiency_score, 1),
            overall_score=round(overall_score, 1),
            strengths=strengths,
            concerns=concerns,
            recommendations=recommendations,
            key_metrics={
                'rides_scheduled': rides_scheduled,
                'completion_rate': round(completion_rate, 3),
                'care_delivery_rate': round(care_delivery_rate, 3),
                'cost_per_outcome': round(cost_per_outcome, 2),
                'driver_no_show_rate': round(driver_no_shows / max(rides_scheduled, 1), 3)
            }
        )

    def score_care_management_vendor(
        self,
        vendor_name: str,
        members_assigned: int,
        outreach_attempts: int,
        successful_contacts: int,
        engaged_members: int,
        care_gaps_addressed: int,
        care_gaps_closed: int,
        readmission_rate: float,
        ed_visit_delta: float,
        total_cost: float
    ) -> VendorScorecard:
        """
        Score care management vendor on gap closure and outcome improvement.

        Key insight: High outreach volume with low gap closure = documentation theater.
        """
        benchmarks = self.BENCHMARKS[VendorType.CARE_MANAGEMENT]
        strengths = []
        concerns = []
        recommendations = []

        # Process metrics
        contact_rate = successful_contacts / max(outreach_attempts, 1)
        engagement_rate = engaged_members / max(successful_contacts, 1) if successful_contacts > 0 else 0
        attempts_per_member = outreach_attempts / max(members_assigned, 1)

        # Outcome metrics
        gap_closure_rate = care_gaps_closed / max(care_gaps_addressed, 1)

        # Efficiency metrics
        cost_per_gap_closed = total_cost / max(care_gaps_closed, 1) if care_gaps_closed > 0 else float('inf')
        cost_per_member = total_cost / max(members_assigned, 1)

        # Score each dimension
        process_score = self._score_metric(contact_rate, benchmarks['contact_rate']) * 0.5
        process_score += self._score_metric(engagement_rate, benchmarks['engagement_rate']) * 0.5

        outcome_score = self._score_metric(gap_closure_rate, benchmarks['gap_closure_rate']) * 0.7
        # Adjust for readmission and ED utilization
        if readmission_rate < 0.15:
            outcome_score += 15
        if ed_visit_delta < 0:
            outcome_score += 15

        efficiency_score = self._score_metric_inverse(cost_per_gap_closed, benchmarks['cost_per_gap_closed'])

        # Identify strengths and concerns
        if gap_closure_rate >= benchmarks['gap_closure_rate']['good']:
            strengths.append(f"Strong gap closure rate ({gap_closure_rate:.0%})")
        if contact_rate >= benchmarks['contact_rate']['good']:
            strengths.append(f"High contact rate ({contact_rate:.0%})")
        if ed_visit_delta < -0.5:
            strengths.append(f"ED utilization reduced by {abs(ed_visit_delta):.1f} visits/member")

        if attempts_per_member > 10 and gap_closure_rate < 0.3:
            concerns.append(f"High outreach volume ({attempts_per_member:.1f}/member) with low gap closure")
            recommendations.append("Review member stratification - may be reaching members with system friction")

        if contact_rate >= 0.5 and gap_closure_rate < 0.2:
            concerns.append("Making contact but not closing gaps - intervention design issue")
            recommendations.append("Audit intervention capabilities vs. member barriers")

        if readmission_rate > 0.20:
            concerns.append(f"Readmission rate {readmission_rate:.0%} above target")

        # Calculate overall score
        overall_score = (
            outcome_score * self.outcome_weight +
            process_score * self.process_weight +
            efficiency_score * self.efficiency_weight
        )

        grade = self._determine_grade(overall_score, outcome_score)

        return VendorScorecard(
            vendor_name=vendor_name,
            vendor_type=VendorType.CARE_MANAGEMENT,
            grade=grade,
            process_score=round(process_score, 1),
            outcome_score=round(outcome_score, 1),
            efficiency_score=round(efficiency_score, 1),
            overall_score=round(overall_score, 1),
            strengths=strengths,
            concerns=concerns,
            recommendations=recommendations,
            key_metrics={
                'members_assigned': members_assigned,
                'contact_rate': round(contact_rate, 3),
                'engagement_rate': round(engagement_rate, 3),
                'gap_closure_rate': round(gap_closure_rate, 3),
                'attempts_per_member': round(attempts_per_member, 1),
                'readmission_rate': round(readmission_rate, 3),
                'ed_visit_delta': round(ed_visit_delta, 2),
                'cost_per_gap_closed': round(cost_per_gap_closed, 2)
            }
        )

    def _score_metric(self, value: float, thresholds: Dict[str, float]) -> float:
        """Score a metric where higher is better."""
        if value >= thresholds['good']:
            return 85 + 15 * min((value - thresholds['good']) / (1 - thresholds['good']), 1)
        elif value >= thresholds['acceptable']:
            return 60 + 25 * (value - thresholds['acceptable']) / (thresholds['good'] - thresholds['acceptable'])
        elif value >= thresholds['poor']:
            return 30 + 30 * (value - thresholds['poor']) / (thresholds['acceptable'] - thresholds['poor'])
        else:
            return max(0, 30 * value / thresholds['poor'])

    def _score_metric_inverse(self, value: float, thresholds: Dict[str, float]) -> float:
        """Score a metric where lower is better (e.g., cost)."""
        if value <= thresholds['good']:
            return 90
        elif value <= thresholds['acceptable']:
            return 60 + 30 * (thresholds['acceptable'] - value) / (thresholds['acceptable'] - thresholds['good'])
        elif value <= thresholds['poor']:
            return 30 + 30 * (thresholds['poor'] - value) / (thresholds['poor'] - thresholds['acceptable'])
        else:
            return max(0, 30 * thresholds['poor'] / value)

    def _determine_grade(self, overall_score: float, outcome_score: float) -> PerformanceGrade:
        """Determine letter grade with outcome veto."""
        # Outcome veto: can't get above C without good outcomes
        if outcome_score < 40:
            if overall_score >= 50:
                return PerformanceGrade.C  # Process compliant but outcomes lacking
            else:
                return PerformanceGrade.D if overall_score >= 30 else PerformanceGrade.F

        if overall_score >= 80:
            return PerformanceGrade.A
        elif overall_score >= 65:
            return PerformanceGrade.B
        elif overall_score >= 50:
            return PerformanceGrade.C
        elif overall_score >= 30:
            return PerformanceGrade.D
        else:
            return PerformanceGrade.F


def generate_scorecard_report(scorecards: List[VendorScorecard]) -> str:
    """Generate executive summary report of vendor performance."""
    report = []
    report.append("=" * 70)
    report.append("VENDOR PERFORMANCE SCORECARD REPORT")
    report.append("Based on Vitals & Variables Edition 18 Methodology")
    report.append("=" * 70)
    report.append("")

    # Summary by grade
    grades = {}
    for sc in scorecards:
        grade_letter = sc.grade.name
        grades[grade_letter] = grades.get(grade_letter, 0) + 1

    report.append("GRADE DISTRIBUTION:")
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = grades.get(grade, 0)
        if count > 0:
            report.append(f"  {grade}: {count} vendor(s)")
    report.append("")

    # Individual vendor summaries
    report.append("VENDOR DETAILS:")
    report.append("-" * 70)

    for sc in sorted(scorecards, key=lambda x: x.overall_score, reverse=True):
        report.append(f"\n{sc.vendor_name} ({sc.vendor_type.value})")
        report.append(f"  Grade: {sc.grade.name} - {sc.grade.value}")
        report.append(f"  Overall Score: {sc.overall_score}/100")
        report.append(f"    Process: {sc.process_score}/100")
        report.append(f"    Outcome: {sc.outcome_score}/100")
        report.append(f"    Efficiency: {sc.efficiency_score}/100")

        if sc.strengths:
            report.append(f"  Strengths: {'; '.join(sc.strengths)}")
        if sc.concerns:
            report.append(f"  Concerns: {'; '.join(sc.concerns)}")
        if sc.recommendations:
            report.append(f"  Recommendations:")
            for rec in sc.recommendations:
                report.append(f"    - {rec}")

    report.append("")
    report.append("-" * 70)
    report.append("NOTE: Vendors with high process scores but low outcome scores")
    report.append("are flagged as 'Process Compliant' (Grade C). High activity")
    report.append("without outcome improvement is documentation, not care management.")
    report.append("")
    report.append("Reference: Finkelstein et al. (2020) NEJM - Camden Coalition RCT")

    return "\n".join(report)


# Example usage
if __name__ == "__main__":
    scorer = VendorScorer()

    # Example transportation vendor
    transport_scorecard = scorer.score_transportation_vendor(
        vendor_name="MedTrans Services",
        rides_scheduled=1000,
        rides_completed=850,
        appointments_kept=520,
        appointments_missed=200,
        driver_no_shows=50,
        total_cost=45000,
        ride_type="ESCORTED"
    )

    # Example care management vendor
    cm_scorecard = scorer.score_care_management_vendor(
        vendor_name="CareFirst Solutions",
        members_assigned=500,
        outreach_attempts=4500,
        successful_contacts=1800,
        engaged_members=900,
        care_gaps_addressed=1200,
        care_gaps_closed=360,
        readmission_rate=0.14,
        ed_visit_delta=-0.3,
        total_cost=180000
    )

    # Generate report
    print(generate_scorecard_report([transport_scorecard, cm_scorecard]))
