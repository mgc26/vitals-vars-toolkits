#!/usr/bin/env python3
"""
The Coasean Calculator for Healthcare AI Buy vs. Build Decisions
Based on Ronald Coase's transaction cost economics (1937)
Now with 100% more economic theory and 50% more snark
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
import json


@dataclass
class CoaseanFactors:
    """
    The 6 Coasean factors that determine whether transaction costs
    favor building (internal hierarchy) or buying (market transaction)
    """
    spec_volatility: float  # 1-5: How often requirements change
    verification_difficulty: float  # 1-5: How hard to verify quality
    interdependence: float  # 1-5: Coupling with other systems
    data_sensitivity: float  # 1-5: PHI/IP sensitivity & regulatory burden
    supplier_power: float  # 1-5: Vendor lock-in risk
    frequency_tempo: float  # 1-5: How often you use it

    def validate(self):
        """Ensure all scores are between 1 and 5 (Coase wouldn't approve of 0s)"""
        for field_name, value in self.__dict__.items():
            if not 1 <= value <= 5:
                raise ValueError(f"{field_name} must be between 1 and 5. Coase is disappointed.")


class CoaseanCalculator:
    """
    The calculator that would make Ronald Coase proud (or at least not spin in his grave)
    Based on transaction cost economics: when market transaction costs exceed
    internal coordination costs, bring it in-house
    """

    # Weights based on healthcare-specific transaction cost importance
    DEFAULT_WEIGHTS = {
        'spec_volatility': 1.0,
        'verification_difficulty': 1.0,
        'interdependence': 1.0,
        'data_sensitivity': 1.5,  # HIPAA makes this extra important
        'supplier_power': 1.0,
        'frequency_tempo': 1.0
    }

    # Thresholds for decision (calibrated on healthcare AI market patterns)
    THRESHOLDS = {
        'strong_buy': 13,
        'lean_buy': 16,
        'hybrid': 19,
        'lean_build': 22,
        'strong_build': 25
    }

    def __init__(self, weights: Dict[str, float] = None):
        """Initialize with custom weights or use defaults"""
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

    def calculate_transaction_cost_score(self, factors: CoaseanFactors) -> Dict[str, any]:
        """
        Calculate the Coasean score: higher = more internal (build), lower = more market (buy)

        This is where Coase's ghost judges your decision
        """
        factors.validate()

        # Calculate weighted score
        weighted_score = 0
        factor_scores = {}

        for factor_name, weight in self.weights.items():
            factor_value = getattr(factors, factor_name)
            factor_contribution = factor_value * weight
            weighted_score += factor_contribution
            factor_scores[factor_name] = {
                'raw': factor_value,
                'weighted': round(factor_contribution, 2)
            }

        # Determine recommendation based on thresholds
        if weighted_score <= self.THRESHOLDS['strong_buy']:
            recommendation = "STRONG BUY"
            confidence = 90
            coase_says = "The market has solved this. Don't be a hero."
        elif weighted_score <= self.THRESHOLDS['lean_buy']:
            recommendation = "LEAN BUY"
            confidence = 70
            coase_says = "Transaction costs favor the market, but keep your options open."
        elif weighted_score <= self.THRESHOLDS['hybrid']:
            recommendation = "HYBRID/PARTNER"
            confidence = 60
            coase_says = "Split the difference. Buy the commodity, build the secret sauce."
        elif weighted_score <= self.THRESHOLDS['lean_build']:
            recommendation = "LEAN BUILD"
            confidence = 70
            coase_says = "Your transaction costs are high. Consider bringing this in-house."
        else:
            recommendation = "STRONG BUILD"
            confidence = 90
            coase_says = "The market can't handle your special snowflake needs. Build it."

        return {
            'total_score': round(weighted_score, 2),
            'recommendation': recommendation,
            'confidence': confidence,
            'coase_says': coase_says,
            'factor_breakdown': factor_scores,
            'transaction_cost_level': self._get_transaction_cost_level(weighted_score)
        }

    def _get_transaction_cost_level(self, score: float) -> str:
        """Translate score to transaction cost level"""
        if score <= 15:
            return "LOW - Market transactions are efficient"
        elif score <= 20:
            return "MEDIUM - Consider hybrid approaches"
        else:
            return "HIGH - Internal coordination is cheaper"

    def compare_scenarios(self, scenarios: List[Tuple[str, CoaseanFactors]]) -> pd.DataFrame:
        """Compare multiple scenarios side by side"""
        results = []

        for name, factors in scenarios:
            scores = self.calculate_transaction_cost_score(factors)
            results.append({
                'Scenario': name,
                'Score': scores['total_score'],
                'Recommendation': scores['recommendation'],
                'Confidence': f"{scores['confidence']}%",
                'Coase Says': scores['coase_says']
            })

        return pd.DataFrame(results)

    def calculate_switching_cost_penalty(self,
                                        current_vendor_years: int,
                                        integration_points: int) -> float:
        """
        Calculate the switching cost penalty (vendor lock-in factor)
        Coase would call this "asset specificity"
        """
        # Each year with vendor increases switching cost by 15%
        time_penalty = current_vendor_years * 0.15

        # Each integration point adds 10% switching cost
        integration_penalty = integration_points * 0.10

        total_penalty = min(time_penalty + integration_penalty, 2.0)  # Cap at 200%

        return total_penalty


def run_healthcare_examples():
    """
    Run through classic healthcare AI scenarios
    What would Coase do?
    """
    calculator = CoaseanCalculator()

    print("=" * 70)
    print("THE COASEAN CALCULATOR FOR HEALTHCARE AI")
    print("Based on 87 years of transaction cost economics")
    print("=" * 70)
    print()

    # Scenario 1: Prior Authorization Automation
    print("SCENARIO 1: Prior Authorization Automation")
    print("-" * 40)
    prior_auth = CoaseanFactors(
        spec_volatility=2,  # Payer rules change quarterly
        verification_difficulty=1,  # Clear metrics: approved/denied
        interdependence=2,  # Mostly standalone
        data_sensitivity=3,  # PHI but standard
        supplier_power=2,  # Many vendors
        frequency_tempo=3  # Daily use
    )

    result = calculator.calculate_transaction_cost_score(prior_auth)
    print(f"Total Score: {result['total_score']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Coase Says: {result['coase_says']}")
    print(f"Transaction Costs: {result['transaction_cost_level']}")
    print()

    # Scenario 2: Custom Clinical Protocol AI
    print("SCENARIO 2: Proprietary Sepsis Protocol")
    print("-" * 40)
    sepsis_ai = CoaseanFactors(
        spec_volatility=4,  # Constantly refined based on research
        verification_difficulty=4,  # Complex clinical validation
        interdependence=5,  # Deep integration with all systems
        data_sensitivity=5,  # Proprietary research data
        supplier_power=5,  # No vendor can replicate
        frequency_tempo=5  # Every patient, every hour
    )

    result = calculator.calculate_transaction_cost_score(sepsis_ai)
    print(f"Total Score: {result['total_score']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Coase Says: {result['coase_says']}")
    print(f"Transaction Costs: {result['transaction_cost_level']}")
    print()

    # Scenario 3: Ambient Clinical Documentation
    print("SCENARIO 3: Ambient Clinical Documentation")
    print("-" * 40)
    ambient_doc = CoaseanFactors(
        spec_volatility=3,  # Some workflow customization
        verification_difficulty=3,  # Quality subjective
        interdependence=4,  # Tight EHR integration
        data_sensitivity=4,  # All patient encounters
        supplier_power=3,  # Few good vendors
        frequency_tempo=4  # Every clinical encounter
    )

    result = calculator.calculate_transaction_cost_score(ambient_doc)
    print(f"Total Score: {result['total_score']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Coase Says: {result['coase_says']}")
    print(f"Transaction Costs: {result['transaction_cost_level']}")
    print()

    # Comparison table
    print("=" * 70)
    print("COMPARATIVE ANALYSIS")
    print("=" * 70)

    scenarios = [
        ("Prior Auth Automation", prior_auth),
        ("Proprietary Sepsis AI", sepsis_ai),
        ("Ambient Documentation", ambient_doc)
    ]

    comparison_df = calculator.compare_scenarios(scenarios)
    print(comparison_df.to_string(index=False))

    print()
    print("=" * 70)
    print("REMEMBER: In 1937, Coase figured out what healthcare IT")
    print("is learning the hard way in 2024:")
    print("Transaction costs determine everything.")
    print("=" * 70)


if __name__ == "__main__":
    run_healthcare_examples()

    print("\n\n🎓 COASE'S PARTING WISDOM:")
    print("\"The limit to the size of the firm is set where its costs of")
    print("organizing a transaction equal the cost of carrying it out in the market.\"")
    print("\nTranslation: Stop building commodity AI. It's been solved.")
    print("Focus on what makes you special (hint: it's less than you think).")