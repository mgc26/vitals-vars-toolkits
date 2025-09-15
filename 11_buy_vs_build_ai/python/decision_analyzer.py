#!/usr/bin/env python3
"""
Buy vs. Build Decision Analyzer for Healthcare AI/Analytics
Analyzes key factors to recommend whether to buy or build solutions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import json
from dataclasses import dataclass, asdict


@dataclass
class DecisionFactors:
    """Factors influencing buy vs build decision"""
    strategic_alignment: float  # 0-10: How core to competitive advantage
    technical_complexity: float  # 0-10: Complexity of the solution
    resource_availability: float  # 0-10: Available technical resources
    time_to_value: float  # 0-10: Urgency (10 = very urgent)
    regulatory_requirements: float  # 0-10: Regulatory complexity
    integration_complexity: float  # 0-10: Number and complexity of integrations
    data_uniqueness: float  # 0-10: How unique is your data/use case

    def validate(self):
        """Ensure all scores are between 0 and 10"""
        for field, value in asdict(self).items():
            if not 0 <= value <= 10:
                raise ValueError(f"{field} must be between 0 and 10")


class BuyVsBuildAnalyzer:
    """Analyzes whether to buy or build healthcare AI/analytics solutions"""

    def __init__(self, weights: Dict[str, float] = None):
        """Initialize with custom weights or use defaults"""
        self.weights = weights or {
            'strategic_alignment': 0.20,
            'technical_complexity': 0.15,
            'resource_availability': 0.15,
            'time_to_value': 0.20,
            'regulatory_requirements': 0.10,
            'integration_complexity': 0.10,
            'data_uniqueness': 0.10
        }
        self._validate_weights()

    def _validate_weights(self):
        """Ensure weights sum to 1.0"""
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def calculate_scores(self, factors: DecisionFactors) -> Dict[str, float]:
        """
        Calculate buy and build scores based on factors

        Returns dict with 'buy_score', 'build_score', and 'recommendation'
        """
        factors.validate()

        # Calculate build favorability for each factor
        build_favorability = {
            'strategic_alignment': factors.strategic_alignment,  # Higher = build
            'technical_complexity': factors.technical_complexity,  # Higher = build
            'resource_availability': factors.resource_availability,  # Higher = build
            'time_to_value': 10 - factors.time_to_value,  # Lower urgency = build
            'regulatory_requirements': 10 - factors.regulatory_requirements,  # Lower = build
            'integration_complexity': factors.integration_complexity,  # Higher = build
            'data_uniqueness': factors.data_uniqueness  # Higher = build
        }

        # Calculate weighted build score
        build_score = sum(
            build_favorability[factor] * weight
            for factor, weight in self.weights.items()
        )

        # Buy score is inverse
        buy_score = 10 - build_score

        # Determine recommendation
        if build_score > 6.5:
            recommendation = "STRONG BUILD"
        elif build_score > 5.5:
            recommendation = "LEAN BUILD"
        elif build_score > 4.5:
            recommendation = "CONSIDER HYBRID"
        elif build_score > 3.5:
            recommendation = "LEAN BUY"
        else:
            recommendation = "STRONG BUY"

        return {
            'buy_score': round(buy_score, 2),
            'build_score': round(build_score, 2),
            'recommendation': recommendation,
            'confidence': round(abs(build_score - 5) * 20, 1)  # Confidence percentage
        }

    def analyze_scenarios(self, scenarios: List[Tuple[str, DecisionFactors]]) -> pd.DataFrame:
        """Analyze multiple scenarios and return comparison DataFrame"""
        results = []
        for name, factors in scenarios:
            scores = self.calculate_scores(factors)
            scores['scenario'] = name
            results.append(scores)

        return pd.DataFrame(results)

    def sensitivity_analysis(self, factors: DecisionFactors,
                           param: str, range_pct: float = 0.2) -> pd.DataFrame:
        """
        Perform sensitivity analysis on a single parameter

        Args:
            factors: Base decision factors
            param: Parameter to vary
            range_pct: Percentage to vary the parameter
        """
        base_value = getattr(factors, param)
        min_val = max(0, base_value * (1 - range_pct))
        max_val = min(10, base_value * (1 + range_pct))

        results = []
        for value in np.linspace(min_val, max_val, 11):
            test_factors = DecisionFactors(**asdict(factors))
            setattr(test_factors, param, value)
            scores = self.calculate_scores(test_factors)
            scores[param] = round(value, 2)
            results.append(scores)

        return pd.DataFrame(results)


def calculate_tco_comparison(
    build_costs: Dict[str, List[float]],
    buy_costs: Dict[str, List[float]],
    discount_rate: float = 0.08
) -> Dict[str, float]:
    """
    Calculate 5-year TCO comparison with NPV

    Args:
        build_costs: Dict with 'initial', 'annual_maintenance', 'annual_updates'
        buy_costs: Dict with 'implementation', 'annual_license', 'annual_support'
        discount_rate: Discount rate for NPV calculation
    """
    years = 5

    # Build TCO
    build_cashflows = [-build_costs['initial'][0]]  # Year 0
    for year in range(1, years):
        annual_cost = -(build_costs.get('annual_maintenance', [0])[0] +
                       build_costs.get('annual_updates', [0])[0])
        build_cashflows.append(annual_cost)

    # Buy TCO
    buy_cashflows = [-buy_costs['implementation'][0]]  # Year 0
    for year in range(1, years):
        annual_cost = -(buy_costs.get('annual_license', [0])[0] +
                       buy_costs.get('annual_support', [0])[0])
        buy_cashflows.append(annual_cost)

    # Calculate NPV
    build_npv = np.npv(discount_rate, build_cashflows)
    buy_npv = np.npv(discount_rate, buy_cashflows)

    return {
        'build_tco': round(sum(build_cashflows), 2),
        'buy_tco': round(sum(buy_cashflows), 2),
        'build_npv': round(build_npv, 2),
        'buy_npv': round(buy_npv, 2),
        'tco_recommendation': 'BUILD' if build_npv > buy_npv else 'BUY',
        'savings': round(abs(build_npv - buy_npv), 2)
    }


# Example usage
if __name__ == "__main__":
    # Example 1: Sepsis prediction model (Academic Medical Center)
    sepsis_factors = DecisionFactors(
        strategic_alignment=8.5,  # Core to research mission
        technical_complexity=7.0,  # Complex but manageable
        resource_availability=7.5,  # Strong data science team
        time_to_value=6.0,  # Moderate urgency
        regulatory_requirements=4.0,  # Internal use initially
        integration_complexity=6.5,  # Multiple data sources
        data_uniqueness=9.0  # Unique patient population
    )

    # Example 2: OR Scheduling (Regional Health System)
    or_scheduling_factors = DecisionFactors(
        strategic_alignment=3.0,  # Not a differentiator
        technical_complexity=4.0,  # Well-solved problem
        resource_availability=3.5,  # Limited IT resources
        time_to_value=8.5,  # Urgent need
        regulatory_requirements=2.0,  # Minimal
        integration_complexity=5.0,  # Standard EHR integration
        data_uniqueness=2.0  # Standard OR data
    )

    # Example 3: Population Health Platform
    pop_health_factors = DecisionFactors(
        strategic_alignment=6.0,  # Important but not unique
        technical_complexity=5.5,  # Moderate complexity
        resource_availability=5.0,  # Some resources available
        time_to_value=5.0,  # Medium-term project
        regulatory_requirements=6.0,  # HIPAA, etc.
        integration_complexity=7.0,  # Many data sources
        data_uniqueness=4.0  # Somewhat unique
    )

    # Run analysis
    analyzer = BuyVsBuildAnalyzer()

    scenarios = [
        ("Sepsis Prediction", sepsis_factors),
        ("OR Scheduling", or_scheduling_factors),
        ("Population Health", pop_health_factors)
    ]

    # Analyze all scenarios
    results_df = analyzer.analyze_scenarios(scenarios)
    print("Buy vs Build Analysis Results:")
    print("=" * 60)
    print(results_df.to_string(index=False))
    print()

    # TCO Comparison for Sepsis Model
    sepsis_build_costs = {
        'initial': [1500000],  # $1.5M development
        'annual_maintenance': [150000],  # $150K/year
        'annual_updates': [100000]  # $100K/year updates
    }

    sepsis_buy_costs = {
        'implementation': [400000],  # $400K implementation
        'annual_license': [200000],  # $200K/year
        'annual_support': [50000]  # $50K/year support
    }

    tco_result = calculate_tco_comparison(sepsis_build_costs, sepsis_buy_costs)
    print("\n5-Year TCO Comparison (Sepsis Model):")
    print("=" * 60)
    for key, value in tco_result.items():
        print(f"{key}: ${value:,.0f}" if 'tco' in key or 'npv' in key or 'savings' in key
              else f"{key}: {value}")

    # Sensitivity analysis
    print("\nSensitivity Analysis - Time to Value Impact:")
    print("=" * 60)
    sensitivity_df = analyzer.sensitivity_analysis(
        sepsis_factors, 'time_to_value', range_pct=0.3
    )
    print(sensitivity_df[['time_to_value', 'build_score', 'buy_score', 'recommendation']].to_string(index=False))