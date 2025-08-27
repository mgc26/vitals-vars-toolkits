#!/usr/bin/env python3
"""
A/B Testing Framework for Virtual Healthcare Avatar Deployments
Provides rigorous experimental design and safety monitoring
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import tt_ind_solve_power, zt_ind_solve_power
from typing import Dict, Tuple, List, Optional
import json
import datetime

class AvatarABTestingFramework:
    """Design and analyze A/B tests for avatar deployments with safety monitoring"""
    
    def __init__(self):
        """Initialize A/B testing framework"""
        self.safety_boundaries = {
            'escalation_rate': 0.10,  # Max 10% escalation to human
            'error_rate': 0.05,  # Max 5% critical errors
            'dropout_rate': 0.30,  # Max 30% patient dropout
            'satisfaction_threshold': 0.70  # Min 70% satisfaction
        }
        
    def calculate_sample_size(self,
                            metric_type: str,
                            baseline_value: float,
                            mde: float,  # Minimum detectable effect
                            alpha: float = 0.05,
                            power: float = 0.80,
                            one_sided: bool = False) -> Dict:
        """
        Calculate required sample size for different metric types
        
        Args:
            metric_type: 'continuous', 'binary', or 'time_to_event'
            baseline_value: Current/expected control group value
            mde: Minimum detectable effect size
            alpha: Type I error rate
            power: Statistical power
            one_sided: Whether test is one-sided
            
        Returns:
            Sample size calculations and test parameters
        """
        alternative = 'larger' if one_sided else 'two-sided'
        
        if metric_type == 'continuous':
            # For continuous outcomes (e.g., satisfaction scores)
            effect_size = mde / baseline_value  # Assume baseline_value is std dev
            n_per_group = tt_ind_solve_power(
                effect_size=effect_size,
                alpha=alpha,
                power=power,
                ratio=1.0,
                alternative=alternative
            )
        elif metric_type == 'binary':
            # For binary outcomes (e.g., readmission yes/no)
            p1 = baseline_value
            p2 = baseline_value * (1 - mde)  # Relative reduction
            
            # Use normal approximation
            p_pooled = (p1 + p2) / 2
            es = abs(p1 - p2) / np.sqrt(p_pooled * (1 - p_pooled))
            
            n_per_group = zt_ind_solve_power(
                effect_size=es,
                alpha=alpha,
                power=power,
                ratio=1.0,
                alternative=alternative
            )
        else:  # time_to_event
            # For survival analysis (e.g., time to readmission)
            # Simplified calculation using exponential assumption
            hazard_ratio = 1 - mde
            n_events = 4 * (stats.norm.ppf(1-alpha/2) + stats.norm.ppf(power))**2 / np.log(hazard_ratio)**2
            # Assuming 50% event rate
            n_per_group = n_events / (2 * 0.5)
        
        # Add buffer for attrition
        attrition_rate = 0.15
        n_adjusted = int(np.ceil(n_per_group / (1 - attrition_rate)))
        
        # Calculate study duration based on enrollment rate
        enrollment_rate = 10  # patients per week
        weeks_to_enroll = np.ceil(n_adjusted * 2 / enrollment_rate)
        
        return {
            'n_per_group': int(np.ceil(n_per_group)),
            'n_total': int(np.ceil(n_per_group * 2)),
            'n_adjusted_for_attrition': n_adjusted * 2,
            'effect_size': mde,
            'weeks_to_enroll': int(weeks_to_enroll),
            'statistical_power': power,
            'alpha': alpha,
            'metric_type': metric_type,
            'test_type': alternative
        }
    
    def design_stratified_randomization(self,
                                       n_patients: int,
                                       strata_vars: Dict[str, List],
                                       block_size: int = 4) -> pd.DataFrame:
        """
        Create stratified block randomization scheme
        
        Args:
            n_patients: Total number of patients
            strata_vars: Stratification variables and their levels
            block_size: Size of randomization blocks
            
        Returns:
            Randomization schedule
        """
        # Create all strata combinations
        strata_combinations = []
        for var, levels in strata_vars.items():
            if not strata_combinations:
                strata_combinations = [[level] for level in levels]
            else:
                new_combinations = []
                for combo in strata_combinations:
                    for level in levels:
                        new_combinations.append(combo + [level])
                strata_combinations = new_combinations
        
        # Calculate patients per stratum
        n_strata = len(strata_combinations)
        patients_per_stratum = n_patients // n_strata
        
        # Create randomization within each stratum
        randomization_schedule = []
        
        for i, stratum in enumerate(strata_combinations):
            stratum_dict = {list(strata_vars.keys())[j]: stratum[j] 
                           for j in range(len(stratum))}
            
            # Create blocks
            n_blocks = patients_per_stratum // block_size
            remainder = patients_per_stratum % block_size
            
            assignments = []
            for _ in range(n_blocks):
                block = ['Control'] * (block_size // 2) + ['Treatment'] * (block_size // 2)
                np.random.shuffle(block)
                assignments.extend(block)
            
            # Handle remainder
            if remainder > 0:
                partial_block = ['Control'] * (remainder // 2) + ['Treatment'] * (remainder - remainder // 2)
                np.random.shuffle(partial_block)
                assignments.extend(partial_block)
            
            # Add to schedule
            for j, assignment in enumerate(assignments):
                patient = {
                    'patient_id': f'P{i*patients_per_stratum + j + 1:04d}',
                    'stratum_id': i,
                    'assignment': assignment,
                    'enrollment_order': i * patients_per_stratum + j + 1
                }
                patient.update(stratum_dict)
                randomization_schedule.append(patient)
        
        return pd.DataFrame(randomization_schedule)
    
    def create_safety_monitoring_plan(self,
                                     n_patients: int,
                                     study_duration_weeks: int) -> Dict:
        """
        Create DSMB safety monitoring plan with stopping rules
        
        Args:
            n_patients: Total enrolled patients
            study_duration_weeks: Expected study duration
            
        Returns:
            Safety monitoring plan with review schedule
        """
        # O'Brien-Fleming boundaries for early stopping
        n_looks = min(5, study_duration_weeks // 4)  # Review every 4 weeks
        
        review_points = []
        for i in range(1, n_looks + 1):
            fraction = i / n_looks
            n_enrolled = int(n_patients * fraction)
            
            # Calculate stopping boundaries
            z_efficacy = stats.norm.ppf(0.975) * np.sqrt(n_looks / i)
            z_futility = -z_efficacy
            
            review = {
                'review_number': i,
                'week': i * 4,
                'n_enrolled': n_enrolled,
                'efficacy_boundary': z_efficacy,
                'futility_boundary': z_futility,
                'safety_rules': {
                    'escalation_rate': {
                        'threshold': self.safety_boundaries['escalation_rate'],
                        'action': 'Investigate if exceeded'
                    },
                    'error_rate': {
                        'threshold': self.safety_boundaries['error_rate'],
                        'action': 'Stop if exceeded'
                    },
                    'serious_adverse_events': {
                        'threshold': 'Any SAE related to intervention',
                        'action': 'Emergency DSMB meeting'
                    }
                }
            }
            review_points.append(review)
        
        return {
            'review_schedule': review_points,
            'stopping_rules': {
                'efficacy': 'Stop for success if test statistic exceeds efficacy boundary',
                'futility': 'Stop for futility if test statistic below futility boundary',
                'safety': 'Stop immediately for safety violations'
            },
            'dsmb_charter': {
                'members': ['Clinician', 'Statistician', 'Ethicist', 'Patient representative'],
                'review_frequency': 'Every 4 weeks for first 3 months, then monthly',
                'voting_rules': 'Majority vote for stopping decisions'
            }
        }
    
    def analyze_interim_results(self,
                               control_data: np.ndarray,
                               treatment_data: np.ndarray,
                               metric_type: str,
                               review_number: int,
                               total_reviews: int) -> Dict:
        """
        Perform interim analysis with appropriate adjustments
        
        Args:
            control_data: Control group outcomes
            treatment_data: Treatment group outcomes
            metric_type: Type of outcome metric
            review_number: Current review number
            total_reviews: Total planned reviews
            
        Returns:
            Interim analysis results with recommendations
        """
        # Calculate test statistic
        if metric_type == 'continuous':
            t_stat, p_value = stats.ttest_ind(treatment_data, control_data)
            effect_size = (treatment_data.mean() - control_data.mean()) / control_data.std()
            ci = stats.t.interval(0.95, len(control_data) + len(treatment_data) - 2,
                                 loc=treatment_data.mean() - control_data.mean(),
                                 scale=np.sqrt(treatment_data.var()/len(treatment_data) + 
                                             control_data.var()/len(control_data)))
        else:  # binary
            p1 = control_data.mean()
            p2 = treatment_data.mean()
            se = np.sqrt(p1*(1-p1)/len(control_data) + p2*(1-p2)/len(treatment_data))
            z_stat = (p2 - p1) / se
            p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
            t_stat = z_stat
            effect_size = p1 - p2
            ci = (effect_size - 1.96*se, effect_size + 1.96*se)
        
        # O'Brien-Fleming boundary
        z_boundary = stats.norm.ppf(0.975) * np.sqrt(total_reviews / review_number)
        
        # Conditional power (probability of success given current data)
        remaining_fraction = (total_reviews - review_number) / total_reviews
        conditional_power = stats.norm.cdf(
            (abs(t_stat) - z_boundary * np.sqrt(review_number/total_reviews)) / 
            np.sqrt(remaining_fraction)
        )
        
        # Safety checks
        safety_violations = []
        if hasattr(self, 'check_safety_metrics'):
            safety_violations = self.check_safety_metrics(control_data, treatment_data)
        
        # Recommendation
        if abs(t_stat) > z_boundary:
            recommendation = 'Stop for efficacy' if t_stat > 0 else 'Stop for harm'
        elif abs(t_stat) < -z_boundary:
            recommendation = 'Stop for futility'
        elif safety_violations:
            recommendation = f'Safety concern: {safety_violations}'
        elif conditional_power < 0.20:
            recommendation = 'Consider stopping for futility'
        else:
            recommendation = 'Continue study'
        
        return {
            'review_number': review_number,
            'n_control': len(control_data),
            'n_treatment': len(treatment_data),
            'test_statistic': t_stat,
            'p_value': p_value,
            'effect_size': effect_size,
            'confidence_interval': ci,
            'efficacy_boundary': z_boundary,
            'conditional_power': conditional_power,
            'recommendation': recommendation,
            'safety_violations': safety_violations
        }
    
    def generate_protocol_template(self,
                                  study_name: str,
                                  primary_outcome: str,
                                  use_case: str) -> str:
        """
        Generate A/B test protocol template
        
        Args:
            study_name: Name of the study
            primary_outcome: Primary outcome measure
            use_case: Avatar use case being tested
            
        Returns:
            Protocol template as markdown
        """
        template = f"""
# A/B Testing Protocol: {study_name}

## Study Overview
**Title**: {study_name}
**Use Case**: {use_case}
**Design**: Randomized controlled trial with 1:1 allocation
**Primary Outcome**: {primary_outcome}

## Eligibility Criteria

### Inclusion Criteria
- Age ≥ 18 years
- Diagnosis relevant to use case
- Ability to interact with technology
- English speaking (or available language)
- Informed consent obtained

### Exclusion Criteria
- Cognitive impairment (MMSE < 24)
- Active psychosis or severe mental illness
- No access to required technology
- Previous enrollment in avatar studies

## Randomization
- Stratified block randomization
- Stratification variables: Age group, risk category, technology comfort
- Block size: 4
- Allocation concealment via sealed envelopes

## Interventions

### Control Group
- Standard care per institutional protocols
- Usual discharge education or follow-up

### Treatment Group
- Standard care PLUS avatar intervention
- Frequency: Per use case protocol
- Duration: Study-specific

## Outcome Measures

### Primary Outcome
- {primary_outcome}
- Measured at: Baseline, 30 days, 90 days

### Secondary Outcomes
- Patient satisfaction (validated survey)
- Healthcare utilization
- Cost-effectiveness
- Staff time savings

### Safety Outcomes
- Escalation rate to human clinician
- Technical errors requiring intervention
- Adverse events possibly related to intervention

## Sample Size
- Calculated based on primary outcome
- Alpha = 0.05, Power = 0.80
- Adjust for 15% attrition

## Statistical Analysis

### Primary Analysis
- Intent-to-treat principle
- Between-group comparison using appropriate test
- 95% confidence intervals

### Secondary Analyses
- Per-protocol analysis
- Subgroup analyses (pre-specified)
- Sensitivity analyses for missing data

## Safety Monitoring
- DSMB review every 4 weeks initially
- Stopping rules for safety and futility
- Real-time adverse event reporting

## Data Management
- REDCap or equivalent for data capture
- Daily backups
- Audit trail maintenance

## Timeline
- Enrollment: X weeks
- Follow-up: Y weeks
- Analysis: Z weeks
- Total duration: X+Y+Z weeks

## Regulatory
- IRB approval required
- HIPAA compliance
- Clinical trial registration

## References
[Include relevant citations]
        """
        
        return template


def demonstrate_ab_testing():
    """Demonstrate A/B testing framework usage"""
    framework = AvatarABTestingFramework()
    
    print("="*60)
    print("AVATAR A/B TESTING FRAMEWORK DEMONSTRATION")
    print("="*60)
    
    # 1. Sample size calculation
    print("\n1. Sample Size Calculation for Readmission Reduction:")
    sample_size = framework.calculate_sample_size(
        metric_type='binary',
        baseline_value=0.18,  # 18% baseline readmission
        mde=0.30,  # 30% relative reduction
        alpha=0.05,
        power=0.80
    )
    
    for key, value in sample_size.items():
        print(f"   {key}: {value}")
    
    # 2. Randomization scheme
    print("\n2. Stratified Randomization (first 10 patients):")
    randomization = framework.design_stratified_randomization(
        n_patients=100,
        strata_vars={
            'age_group': ['<65', '>=65'],
            'risk_level': ['low', 'high']
        },
        block_size=4
    )
    print(randomization.head(10).to_string())
    
    # 3. Safety monitoring plan
    print("\n3. Safety Monitoring Plan:")
    safety_plan = framework.create_safety_monitoring_plan(
        n_patients=sample_size['n_total'],
        study_duration_weeks=16
    )
    
    print("   Review Schedule:")
    for review in safety_plan['review_schedule'][:3]:
        print(f"      Week {review['week']}: n={review['n_enrolled']}, "
              f"z-boundary={review['efficacy_boundary']:.2f}")
    
    # 4. Interim analysis simulation
    print("\n4. Simulated Interim Analysis:")
    np.random.seed(42)
    control_outcomes = np.random.binomial(1, 0.18, 50)  # 18% event rate
    treatment_outcomes = np.random.binomial(1, 0.126, 50)  # 30% reduction
    
    interim_results = framework.analyze_interim_results(
        control_data=control_outcomes,
        treatment_data=treatment_outcomes,
        metric_type='binary',
        review_number=2,
        total_reviews=4
    )
    
    print(f"   Effect size: {interim_results['effect_size']:.3f}")
    print(f"   P-value: {interim_results['p_value']:.4f}")
    print(f"   Conditional power: {interim_results['conditional_power']:.2%}")
    print(f"   Recommendation: {interim_results['recommendation']}")


if __name__ == '__main__':
    demonstrate_ab_testing()