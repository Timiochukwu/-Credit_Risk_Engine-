"""
What-If Analysis Tool
=====================

Interactive scenario analysis for loan officers.

Allows exploring:
- "What if income was ₦500k instead of ₦400k?"
- "What if loan term extended to 36 months?"
- "What collateral value would approve this loan?"
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


class WhatIfAnalyzer:
    """
    Interactive what-if scenario analysis.
    """

    def __init__(self, predictor):
        """
        Args:
            predictor: Trained CreditRiskPredictor instance
        """
        self.predictor = predictor

    def analyze_single_change(
        self,
        application: Dict,
        feature: str,
        values: List[float]
    ) -> pd.DataFrame:
        """
        Analyze impact of changing a single feature.

        Args:
            application: Base application
            feature: Feature to change
            values: List of values to test

        Returns:
            DataFrame with results
        """
        results = []

        for value in values:
            # Create modified application
            modified_app = application.copy()
            modified_app[feature] = value

            # Get prediction
            prediction = self.predictor.predict_single(modified_app)

            results.append({
                feature: value,
                'default_probability': prediction['default_probability'],
                'risk_category': prediction['risk_category'],
                'decision': prediction['decision']
            })

        return pd.DataFrame(results)

    def find_approval_threshold(
        self,
        application: Dict,
        feature: str,
        target_risk: float = 0.15
    ) -> Dict:
        """
        Find value of feature needed for approval.

        Args:
            application: Base application
            feature: Feature to optimize
            target_risk: Target default probability

        Returns:
            Optimal feature value and analysis
        """
        # Binary search for optimal value
        if feature == 'monthly_income':
            low, high = application[feature] * 0.5, application[feature] * 3
        elif feature == 'debt_to_income_ratio':
            low, high = 0.05, application[feature]
        elif feature == 'loan_amount':
            low, high = application[feature] * 0.5, application[feature] * 1.5
        else:
            low, high = 0, 100

        iterations = 0
        max_iterations = 20

        while iterations < max_iterations:
            mid = (low + high) / 2
            modified_app = application.copy()
            modified_app[feature] = mid

            prediction = self.predictor.predict_single(modified_app)
            current_risk = prediction['default_probability']

            if abs(current_risk - target_risk) < 0.01:
                break

            if current_risk > target_risk:
                # Need to reduce risk
                if feature in ['monthly_income']:
                    low = mid
                else:
                    high = mid
            else:
                if feature in ['monthly_income']:
                    high = mid
                else:
                    low = mid

            iterations += 1

        return {
            'feature': feature,
            'original_value': application[feature],
            'required_value': mid,
            'change_needed': mid - application[feature],
            'change_percent': ((mid - application[feature]) / application[feature]) * 100 if application[feature] != 0 else 0,
            'target_risk': target_risk,
            'achievable': abs(current_risk - target_risk) < 0.05
        }

    def compare_scenarios(
        self,
        application: Dict,
        scenarios: List[Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Compare multiple scenarios.

        Args:
            application: Base application
            scenarios: List of scenario modifications

        Returns:
            Comparison DataFrame
        """
        results = []

        # Base scenario
        base_pred = self.predictor.predict_single(application)
        results.append({
            'scenario': 'Base',
            'default_probability': base_pred['default_probability'],
            'risk_category': base_pred['risk_category'],
            'decision': base_pred['decision'],
            **{k: application.get(k, 0) for k in scenarios[0].keys()}
        })

        # Alternative scenarios
        for i, scenario in enumerate(scenarios, 1):
            modified_app = application.copy()
            modified_app.update(scenario)

            prediction = self.predictor.predict_single(modified_app)

            results.append({
                'scenario': f'Scenario {i}',
                'default_probability': prediction['default_probability'],
                'risk_category': prediction['risk_category'],
                'decision': prediction['decision'],
                **scenario
            })

        return pd.DataFrame(results)


def main():
    print("\n" + "="*70)
    print(" "*20 + "WHAT-IF ANALYSIS DEMO")
    print("="*70)
    print("\n✓ What-If Analysis Tool Implemented")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
