"""
Prediction Service
==================

This module provides prediction capabilities for the credit risk model.

Features:
- Load trained models and preprocessors
- Make predictions on new loan applications
- Provide risk scores and recommendations
- Batch prediction support
- Risk categorization

Nigerian Context:
- Returns risk scores in Nigerian banking context
- Provides actionable recommendations
- Considers Nigerian-specific risk factors
"""

import pandas as pd
import numpy as np
import joblib
from typing import Dict, List, Union, Tuple
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RISK_THRESHOLDS, MODELS_DIR
from src.data.preprocessing import DataPreprocessor
from src.data.feature_engineering import FeatureEngineer


class CreditRiskPredictor:
    """
    Production-ready prediction service for credit risk assessment.

    This class loads trained models and provides predictions with
    risk categorization and recommendations.
    """

    def __init__(
        self,
        model_path: str = None,
        preprocessor_path: str = None,
        model_name: str = "xgboost"
    ):
        """
        Initialize predictor with trained model and preprocessor.

        Args:
            model_path: Path to trained model file
            preprocessor_path: Path to fitted preprocessor
            model_name: Name of model to use
        """
        self.model_name = model_name

        # Load model
        if model_path is None:
            model_path = MODELS_DIR / f"{model_name}_model.pkl"

        self.model = joblib.load(model_path)
        print(f"✓ Loaded model from {model_path}")

        # Load preprocessor
        if preprocessor_path is None:
            preprocessor_path = MODELS_DIR / "preprocessor.pkl"

        self.preprocessor = DataPreprocessor.load(preprocessor_path)
        print(f"✓ Loaded preprocessor from {preprocessor_path}")

        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer()

    def categorize_risk(self, probability: float) -> str:
        """
        Categorize default probability into risk levels.

        Args:
            probability: Default probability (0-1)

        Returns:
            Risk category string
        """
        if probability < RISK_THRESHOLDS['very_low']:
            return "VERY_LOW"
        elif probability < RISK_THRESHOLDS['low']:
            return "LOW"
        elif probability < RISK_THRESHOLDS['medium']:
            return "MEDIUM"
        elif probability < RISK_THRESHOLDS['high']:
            return "HIGH"
        else:
            return "VERY_HIGH"

    def get_recommendation(self, risk_category: str, probability: float) -> Dict:
        """
        Get loan decision recommendation based on risk.

        Args:
            risk_category: Risk category
            probability: Default probability

        Returns:
            Dictionary with recommendation and reasoning
        """
        recommendations = {
            "VERY_LOW": {
                "decision": "APPROVE",
                "terms": "Standard terms - Best interest rate",
                "reasoning": f"Excellent credit profile with very low default risk ({probability:.1%})",
                "suggested_action": "Auto-approve with premium customer benefits"
            },
            "LOW": {
                "decision": "APPROVE",
                "terms": "Standard terms",
                "reasoning": f"Good credit profile with low default risk ({probability:.1%})",
                "suggested_action": "Auto-approve with standard terms"
            },
            "MEDIUM": {
                "decision": "APPROVE_WITH_CONDITIONS",
                "terms": "Higher interest rate or require collateral",
                "reasoning": f"Moderate default risk ({probability:.1%})",
                "suggested_action": "Approve with risk-adjusted pricing or additional security"
            },
            "HIGH": {
                "decision": "MANUAL_REVIEW",
                "terms": "Requires senior management approval",
                "reasoning": f"High default risk ({probability:.1%})",
                "suggested_action": "Flag for manual review - verify income and employment"
            },
            "VERY_HIGH": {
                "decision": "REJECT",
                "terms": "Loan application rejected",
                "reasoning": f"Very high default risk ({probability:.1%})",
                "suggested_action": "Reject application - offer financial literacy program"
            }
        }

        return recommendations.get(risk_category, recommendations["HIGH"])

    def predict_single(self, application: Dict) -> Dict:
        """
        Make prediction for a single loan application.

        Args:
            application: Dictionary with loan application details

        Returns:
            Dictionary with prediction results
        """
        # Convert to DataFrame
        df = pd.DataFrame([application])

        # Engineer features
        df_engineered = self.feature_engineer.engineer_features(df)

        # Preprocess
        X = self.preprocessor.transform(df_engineered)

        # Get prediction probability
        probability = self.model.predict_proba(X)[0][1]  # Probability of default

        # Get binary prediction
        prediction = self.model.predict(X)[0]

        # Categorize risk
        risk_category = self.categorize_risk(probability)

        # Get recommendation
        recommendation = self.get_recommendation(risk_category, probability)

        # Compile results
        result = {
            "application_id": application.get("application_id", "N/A"),
            "applicant_name": application.get("full_name", "N/A"),
            "loan_amount": application.get("loan_amount", 0),
            "default_probability": round(probability, 4),
            "default_probability_percent": f"{probability * 100:.2f}%",
            "predicted_default": bool(prediction),
            "risk_category": risk_category,
            "decision": recommendation["decision"],
            "terms": recommendation["terms"],
            "reasoning": recommendation["reasoning"],
            "suggested_action": recommendation["suggested_action"]
        }

        return result

    def predict_batch(self, applications: List[Dict]) -> pd.DataFrame:
        """
        Make predictions for multiple loan applications.

        Args:
            applications: List of application dictionaries

        Returns:
            DataFrame with prediction results
        """
        results = []

        print(f"\nProcessing {len(applications)} loan applications...")

        for i, application in enumerate(applications):
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(applications)} applications...")

            result = self.predict_single(application)
            results.append(result)

        results_df = pd.DataFrame(results)

        print(f"\n✓ Completed predictions for {len(applications)} applications")
        print(f"\nRisk Distribution:")
        print(results_df['risk_category'].value_counts().sort_index())

        return results_df

    def explain_prediction(self, application: Dict, top_n: int = 10) -> Dict:
        """
        Explain prediction by showing feature contributions.

        Args:
            application: Loan application dictionary
            top_n: Number of top contributing features to show

        Returns:
            Dictionary with explanation
        """
        # Get prediction
        prediction_result = self.predict_single(application)

        # For tree-based models, we can get feature importance
        # This is a simplified version - in production, use SHAP or LIME
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = self.model.feature_importances_
            feature_names = self.preprocessor.feature_names

            # Get top features
            top_indices = np.argsort(feature_importance)[-top_n:][::-1]
            top_features = [
                {
                    'feature': feature_names[i],
                    'importance': float(feature_importance[i])
                }
                for i in top_indices
            ]

            prediction_result['top_contributing_features'] = top_features

        return prediction_result

    def generate_prediction_report(
        self,
        application: Dict,
        save_path: Path = None
    ) -> str:
        """
        Generate detailed prediction report for an application.

        Args:
            application: Loan application dictionary
            save_path: Path to save report

        Returns:
            Report as formatted string
        """
        result = self.explain_prediction(application)

        report = f"""
{'='*70}
  NIGERIAN CREDIT RISK ASSESSMENT REPORT
{'='*70}

APPLICATION DETAILS
{'-'*70}
  Application ID:        {result['application_id']}
  Applicant Name:        {result['applicant_name']}
  Loan Amount:           ₦{result['loan_amount']:,.2f}

RISK ASSESSMENT
{'-'*70}
  Default Probability:   {result['default_probability_percent']}
  Risk Category:         {result['risk_category']}

DECISION
{'-'*70}
  Recommendation:        {result['decision']}
  Proposed Terms:        {result['terms']}

REASONING
{'-'*70}
  {result['reasoning']}

SUGGESTED ACTION
{'-'*70}
  {result['suggested_action']}
"""

        if 'top_contributing_features' in result:
            report += f"""
TOP RISK FACTORS
{'-'*70}
"""
            for i, feature in enumerate(result['top_contributing_features'], 1):
                report += f"  {i:2d}. {feature['feature']:30s} (Importance: {feature['importance']:.4f})\n"

        report += f"\n{'='*70}\n"

        # Save if path provided
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)
            print(f"✓ Report saved to {save_path}")

        return report


def main():
    """Demonstration of prediction service."""
    print("\n" + "="*70)
    print(" "*20 + "CREDIT RISK PREDICTION DEMO")
    print("="*70)

    # Sample Nigerian loan application
    sample_application = {
        "application_id": "NGN001234",
        "full_name": "Adebayo Ogunleye",
        "age": 35,
        "education": "B.Sc",
        "employment_sector": "Banking & Finance",
        "years_employed": 8.5,
        "monthly_income": 450_000,
        "existing_monthly_debt": 80_000,
        "credit_history_months": 48,
        "num_credit_lines": 2,
        "previous_defaults": 0,
        "bank": "GTBank",
        "account_age_years": 6.0,
        "loan_amount": 2_500_000,
        "loan_term_months": 24,
        "loan_purpose": "Business Expansion",
        "interest_rate": 22.0,
        "monthly_payment": 129_000
    }

    try:
        # Initialize predictor (will fail if model not trained yet)
        predictor = CreditRiskPredictor(model_name="xgboost")

        # Make prediction
        print("\n" + "-"*70)
        print("Making prediction for sample application...")
        print("-"*70)

        result = predictor.predict_single(sample_application)

        # Print results
        print(f"\nApplication ID: {result['application_id']}")
        print(f"Applicant: {result['applicant_name']}")
        print(f"Loan Amount: ₦{result['loan_amount']:,.2f}")
        print(f"\nDefault Probability: {result['default_probability_percent']}")
        print(f"Risk Category: {result['risk_category']}")
        print(f"Decision: {result['decision']}")
        print(f"Reasoning: {result['reasoning']}")

        # Generate report
        print("\n" + "-"*70)
        print("Generating detailed report...")
        print("-"*70)

        report = predictor.generate_prediction_report(sample_application)
        print(report)

    except FileNotFoundError:
        print("\n⚠ Models not found. Please train models first using:")
        print("  python src/models/train.py")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
