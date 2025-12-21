"""
Care Management Friction Classifier
Vitals & Variables Edition 18: Care Management AI vs. Member Reality

This module classifies apparent member "nonadherence" by system friction vs.
behavioral causes. Based on peer-reviewed evidence that most care management
AI blames individuals for structural barriers.

Key insight: Detection capability without intervention architecture is
documentation theater.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import warnings

class FrictionType(Enum):
    """Categories of system friction that drive apparent nonadherence."""
    PA_DELAY = "Prior Authorization Delay"
    COST_BARRIER = "Cost-Sharing Barrier"
    NETWORK_ACCESS = "Network Access Gap"
    OUTREACH_TIMING = "Outreach Timing Mismatch"
    BENEFIT_DESIGN = "Benefit Design Friction"
    VENDOR_FAILURE = "Vendor Performance Issue"

class FrictionLevel(Enum):
    """Severity classification for system friction."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class FrictionScore:
    """Individual friction score with attribution."""
    friction_type: FrictionType
    level: FrictionLevel
    score: float
    evidence: str
    recommended_action: str

@dataclass
class MemberFrictionProfile:
    """Complete friction profile for a member."""
    member_id: str
    total_friction_score: float
    friction_scores: List[FrictionScore]
    attribution: str  # 'SYSTEM', 'MIXED', 'BEHAVIORAL'
    intervention_priority: str
    notes: List[str]


class FrictionClassifier:
    """
    Classifies care management "failures" by system vs. behavioral attribution.

    Based on evidence from:
    - Finkelstein et al. (2020) Camden Coalition RCT showing null results
    - Obermeyer et al. (2019) on algorithmic bias in risk scoring
    - Chaiyachati et al. (2018) on transportation intervention failures
    """

    # Thresholds based on peer-reviewed evidence
    PA_DELAY_THRESHOLDS = {
        'low': 3,      # days
        'medium': 7,
        'high': 14,
        'critical': 21
    }

    COST_THRESHOLDS = {
        'low': 25,     # $ OOP
        'medium': 50,
        'high': 100,   # 75% abandonment rate per Eaddy et al.
        'critical': 200
    }

    OUTREACH_SUCCESS_THRESHOLDS = {
        'low': 0.7,    # contact rate
        'medium': 0.5,
        'high': 0.3,
        'critical': 0.1
    }

    def __init__(self, include_sdoh: bool = True):
        """
        Initialize the friction classifier.

        Args:
            include_sdoh: Whether to incorporate SDOH signals in classification
        """
        self.include_sdoh = include_sdoh
        self.friction_weights = {
            FrictionType.PA_DELAY: 1.5,
            FrictionType.COST_BARRIER: 1.4,
            FrictionType.NETWORK_ACCESS: 1.2,
            FrictionType.OUTREACH_TIMING: 1.0,
            FrictionType.BENEFIT_DESIGN: 1.3,
            FrictionType.VENDOR_FAILURE: 1.1
        }

    def classify_pa_friction(
        self,
        avg_days_to_approval: float,
        denial_count: int,
        p2p_required_count: int
    ) -> FrictionScore:
        """
        Classify prior authorization friction.

        Based on Borinstein et al. (2022): complicated PA adds 24.6 days
        to biologic initiation and increases corticosteroid dependence.
        """
        score = 0.0
        evidence_parts = []

        # Days to approval scoring
        if avg_days_to_approval >= self.PA_DELAY_THRESHOLDS['critical']:
            score += 4.0
            evidence_parts.append(f"Avg {avg_days_to_approval:.1f} days to approval (critical)")
        elif avg_days_to_approval >= self.PA_DELAY_THRESHOLDS['high']:
            score += 3.0
            evidence_parts.append(f"Avg {avg_days_to_approval:.1f} days to approval (high)")
        elif avg_days_to_approval >= self.PA_DELAY_THRESHOLDS['medium']:
            score += 2.0
            evidence_parts.append(f"Avg {avg_days_to_approval:.1f} days to approval (medium)")
        elif avg_days_to_approval >= self.PA_DELAY_THRESHOLDS['low']:
            score += 1.0
            evidence_parts.append(f"Avg {avg_days_to_approval:.1f} days to approval")

        # Denial burden
        if denial_count > 2:
            score += 2.0
            evidence_parts.append(f"{denial_count} denials requiring appeal")
        elif denial_count > 0:
            score += 1.0
            evidence_parts.append(f"{denial_count} denial(s)")

        # P2P burden
        if p2p_required_count > 1:
            score += 1.5
            evidence_parts.append(f"{p2p_required_count} peer-to-peer reviews required")
        elif p2p_required_count > 0:
            score += 0.5
            evidence_parts.append("Peer-to-peer review required")

        # Determine level
        if score >= 5:
            level = FrictionLevel.CRITICAL
            action = "Escalate to medical director; consider gold-carding provider"
        elif score >= 3:
            level = FrictionLevel.HIGH
            action = "Review PA criteria for this service; reduce P2P requirements"
        elif score >= 1.5:
            level = FrictionLevel.MEDIUM
            action = "Monitor PA turnaround time for this member's conditions"
        else:
            level = FrictionLevel.LOW
            action = "No PA intervention needed"

        return FrictionScore(
            friction_type=FrictionType.PA_DELAY,
            level=level,
            score=score * self.friction_weights[FrictionType.PA_DELAY],
            evidence=" | ".join(evidence_parts) if evidence_parts else "No significant PA friction",
            recommended_action=action
        )

    def classify_cost_friction(
        self,
        avg_oop_cost: float,
        abandoned_fills: int,
        total_fills: int,
        specialty_drug_flag: bool = False
    ) -> FrictionScore:
        """
        Classify cost-sharing friction.

        Based on Eaddy et al. (2012): $10 OOP increase = 1.9% adherence drop;
        >$100 OOP produces up to 75% specialty Rx abandonment.
        """
        score = 0.0
        evidence_parts = []

        # Cost threshold scoring
        if avg_oop_cost >= self.COST_THRESHOLDS['critical']:
            score += 4.0
            evidence_parts.append(f"Avg OOP ${avg_oop_cost:.0f} (critical - expect >75% abandonment)")
        elif avg_oop_cost >= self.COST_THRESHOLDS['high']:
            score += 3.0
            evidence_parts.append(f"Avg OOP ${avg_oop_cost:.0f} (high - significant abandonment risk)")
        elif avg_oop_cost >= self.COST_THRESHOLDS['medium']:
            score += 2.0
            evidence_parts.append(f"Avg OOP ${avg_oop_cost:.0f} (moderate)")
        elif avg_oop_cost >= self.COST_THRESHOLDS['low']:
            score += 1.0
            evidence_parts.append(f"Avg OOP ${avg_oop_cost:.0f}")

        # Abandonment rate
        if total_fills > 0:
            abandonment_rate = abandoned_fills / total_fills
            if abandonment_rate > 0.3:
                score += 2.5
                evidence_parts.append(f"{abandonment_rate:.0%} abandonment rate")
            elif abandonment_rate > 0.1:
                score += 1.5
                evidence_parts.append(f"{abandonment_rate:.0%} abandonment rate")

        # Specialty drug multiplier
        if specialty_drug_flag and score > 0:
            score *= 1.3
            evidence_parts.append("Specialty drug (higher abandonment risk)")

        # Determine level
        if score >= 5:
            level = FrictionLevel.CRITICAL
            action = "Refer to patient assistance program; review benefit design"
        elif score >= 3:
            level = FrictionLevel.HIGH
            action = "Connect with financial counselor; explore therapeutic alternatives"
        elif score >= 1.5:
            level = FrictionLevel.MEDIUM
            action = "Proactive copay card or assistance program outreach"
        else:
            level = FrictionLevel.LOW
            action = "No cost intervention needed"

        return FrictionScore(
            friction_type=FrictionType.COST_BARRIER,
            level=level,
            score=score * self.friction_weights[FrictionType.COST_BARRIER],
            evidence=" | ".join(evidence_parts) if evidence_parts else "No significant cost friction",
            recommended_action=action
        )

    def classify_outreach_friction(
        self,
        total_attempts: int,
        successful_contacts: int,
        work_hour_attempts: int,
        work_hour_failures: int
    ) -> FrictionScore:
        """
        Classify outreach timing friction.

        Based on evidence that workers without paid sick leave are 3x more
        likely to skip needed care (DeRigne et al., 2016).
        """
        score = 0.0
        evidence_parts = []

        if total_attempts == 0:
            return FrictionScore(
                friction_type=FrictionType.OUTREACH_TIMING,
                level=FrictionLevel.LOW,
                score=0,
                evidence="No outreach attempts recorded",
                recommended_action="Initiate outreach with flexible timing"
            )

        contact_rate = successful_contacts / total_attempts

        # Contact rate scoring
        if contact_rate <= self.OUTREACH_SUCCESS_THRESHOLDS['critical']:
            score += 3.5
            evidence_parts.append(f"{contact_rate:.0%} contact rate (critical)")
        elif contact_rate <= self.OUTREACH_SUCCESS_THRESHOLDS['high']:
            score += 2.5
            evidence_parts.append(f"{contact_rate:.0%} contact rate (low)")
        elif contact_rate <= self.OUTREACH_SUCCESS_THRESHOLDS['medium']:
            score += 1.5
            evidence_parts.append(f"{contact_rate:.0%} contact rate")

        # Work hour mismatch
        if work_hour_attempts > 0:
            work_hour_failure_rate = work_hour_failures / work_hour_attempts
            if work_hour_failure_rate > 0.8:
                score += 2.0
                evidence_parts.append(f"{work_hour_failure_rate:.0%} of work-hour calls failed")
            elif work_hour_failure_rate > 0.5:
                score += 1.0
                evidence_parts.append(f"High work-hour failure rate")

        # Repeated attempts without success
        if total_attempts >= 5 and successful_contacts == 0:
            score += 2.0
            evidence_parts.append(f"{total_attempts} attempts with zero contact")

        # Determine level
        if score >= 4:
            level = FrictionLevel.CRITICAL
            action = "Switch to evening/weekend outreach; consider SMS or mail"
        elif score >= 2.5:
            level = FrictionLevel.HIGH
            action = "Offer callback scheduling; try alternative channels"
        elif score >= 1.5:
            level = FrictionLevel.MEDIUM
            action = "Diversify outreach timing across work and off-hours"
        else:
            level = FrictionLevel.LOW
            action = "Continue current outreach approach"

        return FrictionScore(
            friction_type=FrictionType.OUTREACH_TIMING,
            level=level,
            score=score * self.friction_weights[FrictionType.OUTREACH_TIMING],
            evidence=" | ".join(evidence_parts) if evidence_parts else "Adequate contact rate",
            recommended_action=action
        )

    def classify_network_friction(
        self,
        avg_wait_days: float,
        no_show_count: int,
        appointment_count: int,
        nearest_pcp_miles: Optional[float] = None
    ) -> FrictionScore:
        """
        Classify network access friction.

        Based on Chaiyachati et al. (2018): free rideshare had no effect on
        no-show rates (36.5% vs 36.7%) because "transportation" is a proxy
        for a cluster of barriers.
        """
        score = 0.0
        evidence_parts = []

        # Wait time scoring
        if avg_wait_days >= 21:
            score += 3.0
            evidence_parts.append(f"Avg {avg_wait_days:.0f} day wait for appointments")
        elif avg_wait_days >= 14:
            score += 2.0
            evidence_parts.append(f"Avg {avg_wait_days:.0f} day wait")
        elif avg_wait_days >= 7:
            score += 1.0
            evidence_parts.append(f"Avg {avg_wait_days:.0f} day wait")

        # No-show pattern (may indicate access barriers, not "noncompliance")
        if appointment_count > 0:
            no_show_rate = no_show_count / appointment_count
            if no_show_rate > 0.3:
                score += 2.5
                evidence_parts.append(f"{no_show_rate:.0%} no-show rate - investigate barriers")
            elif no_show_rate > 0.15:
                score += 1.5
                evidence_parts.append(f"{no_show_rate:.0%} no-show rate")

        # Distance factor
        if nearest_pcp_miles is not None and nearest_pcp_miles > 15:
            score += 1.5
            evidence_parts.append(f"Nearest PCP {nearest_pcp_miles:.0f} miles away")

        # Determine level
        if score >= 4:
            level = FrictionLevel.CRITICAL
            action = "Assign patient navigator; consider escorted transport (not app-based)"
        elif score >= 2.5:
            level = FrictionLevel.HIGH
            action = "Review network adequacy for member's area; facilitate telehealth"
        elif score >= 1.5:
            level = FrictionLevel.MEDIUM
            action = "Proactive appointment reminders with barrier assessment"
        else:
            level = FrictionLevel.LOW
            action = "No network intervention needed"

        return FrictionScore(
            friction_type=FrictionType.NETWORK_ACCESS,
            level=level,
            score=score * self.friction_weights[FrictionType.NETWORK_ACCESS],
            evidence=" | ".join(evidence_parts) if evidence_parts else "Adequate network access",
            recommended_action=action
        )

    def classify_member(
        self,
        member_id: str,
        pa_data: Optional[Dict] = None,
        cost_data: Optional[Dict] = None,
        outreach_data: Optional[Dict] = None,
        network_data: Optional[Dict] = None,
        sdoh_factor_count: int = 0
    ) -> MemberFrictionProfile:
        """
        Generate complete friction profile for a member.

        Args:
            member_id: Unique member identifier
            pa_data: Dict with avg_days_to_approval, denial_count, p2p_required_count
            cost_data: Dict with avg_oop_cost, abandoned_fills, total_fills, specialty_drug_flag
            outreach_data: Dict with total_attempts, successful_contacts, work_hour_attempts, work_hour_failures
            network_data: Dict with avg_wait_days, no_show_count, appointment_count, nearest_pcp_miles
            sdoh_factor_count: Number of documented SDOH factors (0-5+)

        Returns:
            MemberFrictionProfile with attribution and recommendations
        """
        friction_scores = []
        notes = []

        # Classify each friction type
        if pa_data:
            friction_scores.append(self.classify_pa_friction(**pa_data))

        if cost_data:
            friction_scores.append(self.classify_cost_friction(**cost_data))

        if outreach_data:
            friction_scores.append(self.classify_outreach_friction(**outreach_data))

        if network_data:
            friction_scores.append(self.classify_network_friction(**network_data))

        # Calculate total friction score
        total_score = sum(fs.score for fs in friction_scores)

        # SDOH multiplier based on Berkowitz et al. (2020)
        # 3+ factors = 3.26x nonadherence odds
        if self.include_sdoh and sdoh_factor_count >= 3:
            sdoh_multiplier = 1.5
            notes.append(f"SDOH burden: {sdoh_factor_count} factors (elevated nonadherence risk per Berkowitz et al.)")
        elif self.include_sdoh and sdoh_factor_count >= 1:
            sdoh_multiplier = 1.2
            notes.append(f"SDOH burden: {sdoh_factor_count} factor(s)")
        else:
            sdoh_multiplier = 1.0

        adjusted_score = total_score * sdoh_multiplier

        # Attribution logic
        # High system friction + high SDOH = system failure
        # Low system friction + any SDOH = behavioral/structural
        # High system friction + low SDOH = system-caused
        high_friction_count = sum(1 for fs in friction_scores if fs.level in [FrictionLevel.HIGH, FrictionLevel.CRITICAL])

        if adjusted_score >= 12 or high_friction_count >= 2:
            attribution = "SYSTEM"
            priority = "IMMEDIATE"
            notes.append("System friction is primary driver - fix process before outreach")
        elif adjusted_score >= 6 or high_friction_count >= 1:
            attribution = "MIXED"
            priority = "HIGH"
            notes.append("Both system and behavioral factors present - address friction first")
        else:
            attribution = "BEHAVIORAL"
            priority = "STANDARD"
            if sdoh_factor_count >= 2:
                notes.append("Low system friction but SDOH present - ensure intervention capacity exists")

        return MemberFrictionProfile(
            member_id=member_id,
            total_friction_score=round(adjusted_score, 2),
            friction_scores=friction_scores,
            attribution=attribution,
            intervention_priority=priority,
            notes=notes
        )


def analyze_population_friction(
    members_df: pd.DataFrame,
    classifier: FrictionClassifier
) -> pd.DataFrame:
    """
    Analyze friction across a population of members.

    Args:
        members_df: DataFrame with columns for member_id and friction data
        classifier: Configured FrictionClassifier instance

    Returns:
        DataFrame with friction profiles for all members
    """
    results = []

    for _, row in members_df.iterrows():
        # Extract data from row (adjust column names to match your data)
        pa_data = None
        if 'avg_days_to_approval' in row and pd.notna(row['avg_days_to_approval']):
            pa_data = {
                'avg_days_to_approval': row['avg_days_to_approval'],
                'denial_count': row.get('denial_count', 0),
                'p2p_required_count': row.get('p2p_required_count', 0)
            }

        cost_data = None
        if 'avg_oop_cost' in row and pd.notna(row['avg_oop_cost']):
            cost_data = {
                'avg_oop_cost': row['avg_oop_cost'],
                'abandoned_fills': row.get('abandoned_fills', 0),
                'total_fills': row.get('total_fills', 1),
                'specialty_drug_flag': row.get('specialty_drug_flag', False)
            }

        outreach_data = None
        if 'total_attempts' in row and pd.notna(row['total_attempts']):
            outreach_data = {
                'total_attempts': row['total_attempts'],
                'successful_contacts': row.get('successful_contacts', 0),
                'work_hour_attempts': row.get('work_hour_attempts', 0),
                'work_hour_failures': row.get('work_hour_failures', 0)
            }

        network_data = None
        if 'avg_wait_days' in row and pd.notna(row['avg_wait_days']):
            network_data = {
                'avg_wait_days': row['avg_wait_days'],
                'no_show_count': row.get('no_show_count', 0),
                'appointment_count': row.get('appointment_count', 1),
                'nearest_pcp_miles': row.get('nearest_pcp_miles', None)
            }

        sdoh_count = row.get('sdoh_factor_count', 0)

        profile = classifier.classify_member(
            member_id=str(row['member_id']),
            pa_data=pa_data,
            cost_data=cost_data,
            outreach_data=outreach_data,
            network_data=network_data,
            sdoh_factor_count=sdoh_count
        )

        results.append({
            'member_id': profile.member_id,
            'total_friction_score': profile.total_friction_score,
            'attribution': profile.attribution,
            'intervention_priority': profile.intervention_priority,
            'friction_types': ', '.join([fs.friction_type.value for fs in profile.friction_scores if fs.level.value >= 2]),
            'top_recommendation': profile.friction_scores[0].recommended_action if profile.friction_scores else 'Standard outreach',
            'notes': ' | '.join(profile.notes)
        })

    return pd.DataFrame(results)


def generate_friction_report(profiles_df: pd.DataFrame) -> str:
    """Generate summary report of friction analysis."""
    report = []
    report.append("=" * 60)
    report.append("CARE MANAGEMENT FRICTION ANALYSIS REPORT")
    report.append("Based on Vitals & Variables Edition 18 Methodology")
    report.append("=" * 60)
    report.append("")

    total = len(profiles_df)
    system = len(profiles_df[profiles_df['attribution'] == 'SYSTEM'])
    mixed = len(profiles_df[profiles_df['attribution'] == 'MIXED'])
    behavioral = len(profiles_df[profiles_df['attribution'] == 'BEHAVIORAL'])

    report.append("ATTRIBUTION SUMMARY:")
    report.append(f"  System-caused friction:    {system:,} ({100*system/total:.1f}%)")
    report.append(f"  Mixed attribution:         {mixed:,} ({100*mixed/total:.1f}%)")
    report.append(f"  Behavioral (low friction): {behavioral:,} ({100*behavioral/total:.1f}%)")
    report.append("")

    report.append("KEY INSIGHT:")
    system_pct = 100 * (system + mixed) / total
    report.append(f"  {system_pct:.0f}% of 'nonadherent' members face system friction")
    report.append("  that should be addressed before behavioral intervention.")
    report.append("")

    report.append("PRIORITY BREAKDOWN:")
    immediate = len(profiles_df[profiles_df['intervention_priority'] == 'IMMEDIATE'])
    high = len(profiles_df[profiles_df['intervention_priority'] == 'HIGH'])
    standard = len(profiles_df[profiles_df['intervention_priority'] == 'STANDARD'])
    report.append(f"  IMMEDIATE: {immediate:,} members")
    report.append(f"  HIGH:      {high:,} members")
    report.append(f"  STANDARD:  {standard:,} members")
    report.append("")

    report.append("RECOMMENDATION:")
    report.append("  Do not send 'nudge' interventions to SYSTEM-attributed members.")
    report.append("  Fix the system friction first, then assess member engagement.")
    report.append("")
    report.append("Reference: Finkelstein et al. (2020) NEJM - Camden Coalition RCT")
    report.append("'Navigating a broken system is not the same as fixing it.'")

    return "\n".join(report)


# Example usage and sample data generation
if __name__ == "__main__":
    # Generate sample data for demonstration
    np.random.seed(42)
    n_members = 100

    sample_data = pd.DataFrame({
        'member_id': [f'M{i:05d}' for i in range(n_members)],
        'avg_days_to_approval': np.random.exponential(8, n_members),
        'denial_count': np.random.poisson(0.5, n_members),
        'p2p_required_count': np.random.poisson(0.3, n_members),
        'avg_oop_cost': np.random.exponential(45, n_members),
        'abandoned_fills': np.random.poisson(0.8, n_members),
        'total_fills': np.random.poisson(5, n_members) + 1,
        'specialty_drug_flag': np.random.choice([True, False], n_members, p=[0.2, 0.8]),
        'total_attempts': np.random.poisson(4, n_members),
        'successful_contacts': np.random.poisson(1.5, n_members),
        'work_hour_attempts': np.random.poisson(3, n_members),
        'work_hour_failures': np.random.poisson(2, n_members),
        'avg_wait_days': np.random.exponential(10, n_members),
        'no_show_count': np.random.poisson(1, n_members),
        'appointment_count': np.random.poisson(4, n_members) + 1,
        'sdoh_factor_count': np.random.poisson(1, n_members)
    })

    # Run analysis
    classifier = FrictionClassifier(include_sdoh=True)
    results = analyze_population_friction(sample_data, classifier)

    # Generate report
    print(generate_friction_report(results))
    print("\n" + "=" * 60)
    print("SAMPLE OUTPUT (first 10 members):")
    print("=" * 60)
    print(results.head(10).to_string(index=False))
