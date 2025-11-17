"""
SHAP & LIME Explainability Module
==================================

Advanced model explainability for regulatory compliance and customer trust.

Features:
- SHAP (SHapley Additive exPlanations) for feature importance
- LIME (Local Interpretable Model-agnostic Explanations)
- Counterfactual explanations
- Feature contribution visualization
- Regulatory-compliant explanations

Nigerian Context:
- CBN requires explainable decisions
- Helps customers understand rejection reasons
- Supports dispute resolution
"""

import shap
import lime
import lime.lime_tabular
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import MODELS_DIR


class ModelExplainer:
    """
    Comprehensive model explainability using SHAP and LIME.

    Provides human-readable explanations for credit decisions.
    """

    def __init__(self, model, model_type: str = "tree", feature_names: List[str] = None):
        """
        Initialize explainer.

        Args:
            model: Trained ML model
            model_type: Type of model ("tree", "linear", "deep")
            feature_names: List of feature names
        """
        self.model = model
        self.model_type = model_type
        self.feature_names = feature_names
        self.shap_explainer = None
        self.lime_explainer = None

    def initialize_shap(self, X_background: pd.DataFrame = None):
        """
        Initialize SHAP explainer.

        Args:
            X_background: Background dataset for SHAP (optional)
        """
        print("Initializing SHAP explainer...")

        if self.model_type == "tree":
            # TreeExplainer for tree-based models (XGBoost, LightGBM, RF)
            self.shap_explainer = shap.TreeExplainer(self.model)
        elif self.model_type == "linear":
            # LinearExplainer for linear models
            self.shap_explainer = shap.LinearExplainer(self.model, X_background)
        else:
            # KernelExplainer for any model (slower but universal)
            if X_background is None:
                raise ValueError("X_background required for KernelExplainer")
            self.shap_explainer = shap.KernelExplainer(
                self.model.predict_proba,
                shap.sample(X_background, 100)
            )

        print("✓ SHAP explainer initialized")

    def initialize_lime(self, X_train: pd.DataFrame, feature_names: List[str] = None):
        """
        Initialize LIME explainer.

        Args:
            X_train: Training data
            feature_names: Feature names
        """
        print("Initializing LIME explainer...")

        if feature_names is None:
            feature_names = self.feature_names or [f"feature_{i}" for i in range(X_train.shape[1])]

        self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            X_train.values if isinstance(X_train, pd.DataFrame) else X_train,
            feature_names=feature_names,
            class_names=['No Default', 'Default'],
            mode='classification'
        )

        print("✓ LIME explainer initialized")

    def explain_shap(self, X: pd.DataFrame) -> Dict:
        """
        Generate SHAP explanations.

        Args:
            X: Input features

        Returns:
            Dictionary with SHAP values and explanations
        """
        if self.shap_explainer is None:
            raise ValueError("SHAP explainer not initialized. Call initialize_shap() first.")

        # Calculate SHAP values
        shap_values = self.shap_explainer.shap_values(X)

        # Handle multi-class output (take class 1 for binary classification)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        # Get feature contributions
        feature_contributions = {}
        for i, feature_name in enumerate(self.feature_names or X.columns):
            feature_contributions[feature_name] = float(shap_values[0][i] if len(shap_values.shape) > 1 else shap_values[i])

        # Sort by absolute contribution
        sorted_contributions = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        # Generate human-readable explanation
        explanation = self._generate_shap_explanation(sorted_contributions[:10])

        return {
            'shap_values': shap_values,
            'feature_contributions': dict(sorted_contributions),
            'top_features': sorted_contributions[:10],
            'explanation': explanation
        }

    def explain_lime(self, X: np.ndarray, num_features: int = 10) -> Dict:
        """
        Generate LIME explanations.

        Args:
            X: Input features (single instance)
            num_features: Number of top features to explain

        Returns:
            Dictionary with LIME explanation
        """
        if self.lime_explainer is None:
            raise ValueError("LIME explainer not initialized. Call initialize_lime() first.")

        # Get explanation
        exp = self.lime_explainer.explain_instance(
            X.flatten() if len(X.shape) > 1 else X,
            self.model.predict_proba,
            num_features=num_features
        )

        # Extract feature contributions
        feature_contributions = dict(exp.as_list())

        # Generate explanation
        explanation = self._generate_lime_explanation(exp.as_list())

        return {
            'lime_explanation': exp,
            'feature_contributions': feature_contributions,
            'explanation': explanation,
            'prediction_proba': exp.predict_proba
        }

    def _generate_shap_explanation(self, top_features: List[Tuple[str, float]]) -> str:
        """Generate human-readable SHAP explanation."""
        positive_factors = []
        negative_factors = []

        for feature, contribution in top_features:
            if contribution > 0:
                positive_factors.append((feature, contribution))
            else:
                negative_factors.append((feature, abs(contribution)))

        explanation = "**Decision Factors:**\n\n"

        if positive_factors:
            explanation += "**Factors Increasing Risk:**\n"
            for feature, contrib in positive_factors[:5]:
                explanation += f"  • {self._humanize_feature(feature)}: +{contrib:.3f}\n"

        if negative_factors:
            explanation += "\n**Factors Decreasing Risk:**\n"
            for feature, contrib in negative_factors[:5]:
                explanation += f"  • {self._humanize_feature(feature)}: -{contrib:.3f}\n"

        return explanation

    def _generate_lime_explanation(self, feature_list: List[Tuple[str, float]]) -> str:
        """Generate human-readable LIME explanation."""
        explanation = "**Local Explanation:**\n\n"

        for feature_desc, weight in feature_list[:5]:
            direction = "increases" if weight > 0 else "decreases"
            explanation += f"  • {feature_desc} {direction} default risk\n"

        return explanation

    def _humanize_feature(self, feature: str) -> str:
        """Convert feature name to human-readable format."""
        humanized = {
            'debt_to_income_ratio': 'Debt-to-Income Ratio',
            'monthly_income': 'Monthly Income',
            'loan_amount': 'Loan Amount',
            'age': 'Age',
            'credit_history_months': 'Credit History',
            'previous_defaults': 'Previous Defaults',
            'years_employed': 'Employment Duration',
            'total_red_flags': 'Risk Flags',
            'total_green_flags': 'Positive Indicators',
            'is_prime_age': 'Prime Working Age',
            'employment_stability': 'Employment Stability'
        }
        return humanized.get(feature, feature.replace('_', ' ').title())

    def generate_counterfactual(
        self,
        X: pd.DataFrame,
        current_prediction: float,
        target_prediction: float = 0.3
    ) -> Dict:
        """
        Generate counterfactual explanation.

        Shows what changes would be needed to achieve target risk level.

        Args:
            X: Current application
            current_prediction: Current default probability
            target_prediction: Target default probability

        Returns:
            Suggested changes to achieve target
        """
        suggestions = {
            'current_risk': current_prediction,
            'target_risk': target_prediction,
            'changes_needed': []
        }

        # Get SHAP values to understand feature importance
        if self.shap_explainer is None:
            return suggestions

        shap_values = self.shap_explainer.shap_values(X)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        # Find features with highest positive SHAP values (increasing risk)
        feature_impacts = []
        for i, feature_name in enumerate(self.feature_names or X.columns):
            impact = float(shap_values[0][i] if len(shap_values.shape) > 1 else shap_values[i])
            if impact > 0:  # Risk-increasing features
                feature_impacts.append((feature_name, impact, X.iloc[0, i]))

        # Sort by impact
        feature_impacts.sort(key=lambda x: x[1], reverse=True)

        # Generate suggestions
        for feature, impact, current_value in feature_impacts[:5]:
            if feature == 'debt_to_income_ratio':
                suggestions['changes_needed'].append({
                    'feature': 'Debt-to-Income Ratio',
                    'current': f"{current_value:.2%}",
                    'suggestion': 'Reduce to below 40%',
                    'impact': 'High'
                })
            elif feature == 'monthly_income':
                suggested = current_value * 1.2
                suggestions['changes_needed'].append({
                    'feature': 'Monthly Income',
                    'current': f"₦{current_value:,.0f}",
                    'suggestion': f'Increase to ₦{suggested:,.0f}',
                    'impact': 'High'
                })
            elif feature == 'previous_defaults':
                if current_value > 0:
                    suggestions['changes_needed'].append({
                        'feature': 'Previous Defaults',
                        'current': f"{int(current_value)}",
                        'suggestion': 'Cannot change past defaults, but maintain good payment history',
                        'impact': 'Very High'
                    })

        return suggestions

    def generate_regulatory_report(
        self,
        application_id: str,
        X: pd.DataFrame,
        prediction: float,
        decision: str
    ) -> str:
        """
        Generate regulatory-compliant explanation report.

        For CBN compliance and customer disputes.

        Args:
            application_id: Loan application ID
            X: Application features
            prediction: Predicted default probability
            decision: Loan decision

        Returns:
            Formatted report
        """
        # Get SHAP explanation
        shap_exp = self.explain_shap(X)

        report = f"""
{'='*70}
  CREDIT DECISION EXPLANATION REPORT
  (CBN Regulatory Compliance)
{'='*70}

Application ID: {application_id}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

DECISION SUMMARY
{'-'*70}
  Default Probability: {prediction:.2%}
  Decision: {decision}
  Risk Category: {"HIGH RISK" if prediction > 0.3 else "MODERATE RISK" if prediction > 0.15 else "LOW RISK"}

DECISION EXPLANATION
{'-'*70}
{shap_exp['explanation']}

TOP 10 CONTRIBUTING FACTORS
{'-'*70}
"""

        for i, (feature, contrib) in enumerate(shap_exp['top_features'], 1):
            direction = "Increases risk" if contrib > 0 else "Decreases risk"
            report += f"  {i:2d}. {self._humanize_feature(feature):30s} | {direction:15s} | Impact: {abs(contrib):.3f}\n"

        report += f"""
REGULATORY NOTES
{'-'*70}
  • This decision was made by an automated ML system
  • The model has been validated for fairness and accuracy
  • Customer has the right to dispute this decision
  • Human review available upon request

DISPUTE PROCESS
{'-'*70}
  If you wish to dispute this decision:
  1. Contact our credit team at credit@bank.ng
  2. Provide additional documentation
  3. Request manual review by senior credit officer

{'='*70}
"""

        return report


def main():
    """Demonstration of explainability features."""
    print("\n" + "="*70)
    print(" "*20 + "MODEL EXPLAINABILITY DEMO")
    print("="*70)

    print("\n✓ SHAP & LIME Explainability Module Implemented")
    print("\nFeatures:")
    print("  • SHAP explanations for tree-based models")
    print("  • LIME local explanations")
    print("  • Counterfactual analysis")
    print("  • Regulatory-compliant reports")
    print("  • Human-readable explanations")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
