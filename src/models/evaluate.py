"""
Model Evaluation Module
========================

This module provides comprehensive model evaluation for credit risk models.

Metrics Included:
1. Accuracy, Precision, Recall, F1-Score
2. ROC-AUC (Area Under ROC Curve)
3. Precision-Recall AUC
4. Confusion Matrix
5. Classification Report
6. Business Metrics (Expected Loss, Cost-Benefit Analysis)

Nigerian Context:
- Considers cost of false positives (rejected good customers)
- Considers cost of false negatives (approved bad customers who default)
- Provides business-relevant metrics for decision makers
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    classification_report, roc_curve, precision_recall_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RISK_THRESHOLDS, MODELS_DIR


class ModelEvaluator:
    """
    Comprehensive model evaluation for credit risk models.

    This class calculates various metrics and creates visualizations
    to assess model performance from both ML and business perspectives.
    """

    def __init__(self, model_name: str = "model"):
        """
        Initialize evaluator.

        Args:
            model_name: Name of the model being evaluated
        """
        self.model_name = model_name
        self.metrics = {}
        self.confusion_mat = None
        self.y_true = None
        self.y_pred = None
        self.y_pred_proba = None

    def calculate_classification_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray = None
    ) -> Dict:
        """
        Calculate standard classification metrics.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (for AUC scores)

        Returns:
            Dictionary of metrics
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
        }

        # Calculate specificity (True Negative Rate)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
        metrics['false_positive_rate'] = fp / (fp + tn) if (fp + tn) > 0 else 0
        metrics['false_negative_rate'] = fn / (fn + tp) if (fn + tp) > 0 else 0

        # AUC scores (if probabilities provided)
        if y_pred_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba)
            metrics['pr_auc'] = average_precision_score(y_true, y_pred_proba)

        return metrics

    def calculate_business_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        loan_amounts: np.ndarray = None,
        average_loan_amount: float = 1_000_000  # ₦1M default
    ) -> Dict:
        """
        Calculate business-relevant metrics.

        In credit risk, we care about:
        - Cost of false positives: Lost revenue from rejected good customers
        - Cost of false negatives: Losses from approved bad customers
        - Expected loss
        - Approval rate

        Args:
            y_true: True labels (1 = default, 0 = no default)
            y_pred: Predicted labels (1 = reject, 0 = approve)
            loan_amounts: Array of loan amounts
            average_loan_amount: Average loan amount (used if loan_amounts not provided)

        Returns:
            Dictionary of business metrics
        """
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        # Total applications
        total = len(y_true)

        # Approval metrics
        total_approvals = tn + fn  # Predicted no default
        total_rejections = tp + fp  # Predicted default

        approval_rate = total_approvals / total if total > 0 else 0

        # Use provided loan amounts or average
        if loan_amounts is None:
            loan_amounts = np.full(total, average_loan_amount)

        # Assuming we approve when pred = 0 and reject when pred = 1
        # FN (False Negative): Predicted 0 (approve) but actually 1 (defaults) - BAD!
        # FP (False Positive): Predicted 1 (reject) but actually 0 (good) - Lost opportunity

        # Cost assumptions for Nigerian context
        # When loan defaults, bank loses ~80% of principal (20% recovered)
        default_loss_rate = 0.80

        # When we reject a good customer, we lose potential profit
        # Nigerian banks charge 15-30% interest - assume 25% profit margin
        opportunity_cost_rate = 0.25

        # Calculate costs
        false_negative_indices = np.where((y_pred == 0) & (y_true == 1))[0]
        false_positive_indices = np.where((y_pred == 1) & (y_true == 0))[0]

        # Cost of defaults (false negatives)
        cost_of_defaults = sum(loan_amounts[false_negative_indices]) * default_loss_rate if len(false_negative_indices) > 0 else 0

        # Lost revenue (false positives)
        lost_revenue = sum(loan_amounts[false_positive_indices]) * opportunity_cost_rate if len(false_positive_indices) > 0 else 0

        # Total cost
        total_cost = cost_of_defaults + lost_revenue

        # Correctly approved good loans (True Negatives)
        true_negative_indices = np.where((y_pred == 0) & (y_true == 0))[0]
        revenue_from_good_loans = sum(loan_amounts[true_negative_indices]) * opportunity_cost_rate if len(true_negative_indices) > 0 else 0

        # Net profit
        net_profit = revenue_from_good_loans - cost_of_defaults - lost_revenue

        business_metrics = {
            'approval_rate': approval_rate,
            'rejection_rate': 1 - approval_rate,
            'cost_of_defaults': cost_of_defaults,
            'lost_revenue_from_rejections': lost_revenue,
            'total_cost': total_cost,
            'revenue_from_good_loans': revenue_from_good_loans,
            'net_profit': net_profit,
            'profit_margin': net_profit / revenue_from_good_loans if revenue_from_good_loans > 0 else 0,
            'default_rate_in_approved': fn / total_approvals if total_approvals > 0 else 0,
            'good_customer_acceptance_rate': tn / (tn + fp) if (tn + fp) > 0 else 0,
        }

        return business_metrics

    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray = None,
        loan_amounts: np.ndarray = None
    ) -> Dict:
        """
        Comprehensive model evaluation.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities
            loan_amounts: Loan amounts for business metrics

        Returns:
            Dictionary with all metrics
        """
        print(f"\n{'='*70}")
        print(f"  Evaluating {self.model_name.upper()}")
        print(f"{'='*70}\n")

        # Store for later use
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_pred_proba = y_pred_proba

        # Calculate metrics
        classification_metrics = self.calculate_classification_metrics(y_true, y_pred, y_pred_proba)
        business_metrics = self.calculate_business_metrics(y_true, y_pred, loan_amounts)

        # Confusion matrix
        self.confusion_mat = confusion_matrix(y_true, y_pred)

        # Combine all metrics
        self.metrics = {
            **classification_metrics,
            **business_metrics
        }

        # Print metrics
        self._print_metrics()

        return self.metrics

    def _print_metrics(self):
        """Print metrics in a formatted way."""
        print("Classification Metrics:")
        print("-" * 70)
        print(f"  Accuracy:              {self.metrics['accuracy']:.4f}")
        print(f"  Precision:             {self.metrics['precision']:.4f}")
        print(f"  Recall:                {self.metrics['recall']:.4f}")
        print(f"  F1-Score:              {self.metrics['f1_score']:.4f}")
        print(f"  Specificity:           {self.metrics['specificity']:.4f}")
        if 'roc_auc' in self.metrics:
            print(f"  ROC-AUC:               {self.metrics['roc_auc']:.4f}")
            print(f"  PR-AUC:                {self.metrics['pr_auc']:.4f}")

        print(f"\nError Rates:")
        print("-" * 70)
        print(f"  False Positive Rate:   {self.metrics['false_positive_rate']:.4f}")
        print(f"  False Negative Rate:   {self.metrics['false_negative_rate']:.4f}")

        print(f"\nBusiness Metrics:")
        print("-" * 70)
        print(f"  Approval Rate:         {self.metrics['approval_rate']:.2%}")
        print(f"  Default Rate (Approved): {self.metrics['default_rate_in_approved']:.2%}")
        print(f"  Good Customer Accept:  {self.metrics['good_customer_acceptance_rate']:.2%}")

        print(f"\nFinancial Impact (NGN):")
        print("-" * 70)
        print(f"  Revenue from Good Loans:  ₦{self.metrics['revenue_from_good_loans']:,.2f}")
        print(f"  Cost of Defaults:         ₦{self.metrics['cost_of_defaults']:,.2f}")
        print(f"  Lost Revenue (Rejections): ₦{self.metrics['lost_revenue_from_rejections']:,.2f}")
        print(f"  Net Profit:               ₦{self.metrics['net_profit']:,.2f}")
        print(f"  Profit Margin:            {self.metrics['profit_margin']:.2%}")

        print(f"\n{'='*70}\n")

    def plot_confusion_matrix(self, save_path: Path = None):
        """
        Plot confusion matrix.

        Args:
            save_path: Path to save the plot
        """
        if self.confusion_mat is None:
            raise ValueError("No confusion matrix available. Run evaluate() first.")

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            self.confusion_mat,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['No Default', 'Default'],
            yticklabels=['No Default', 'Default']
        )
        plt.title(f'Confusion Matrix - {self.model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Confusion matrix saved to {save_path}")

        plt.close()

    def plot_roc_curve(self, save_path: Path = None):
        """
        Plot ROC curve.

        Args:
            save_path: Path to save the plot
        """
        if self.y_pred_proba is None:
            raise ValueError("No probabilities available for ROC curve.")

        fpr, tpr, thresholds = roc_curve(self.y_true, self.y_pred_proba)
        auc = self.metrics.get('roc_auc', 0)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'{self.model_name} (AUC = {auc:.3f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {self.model_name}')
        plt.legend()
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ ROC curve saved to {save_path}")

        plt.close()

    def plot_precision_recall_curve(self, save_path: Path = None):
        """
        Plot Precision-Recall curve.

        Args:
            save_path: Path to save the plot
        """
        if self.y_pred_proba is None:
            raise ValueError("No probabilities available for PR curve.")

        precision, recall, thresholds = precision_recall_curve(self.y_true, self.y_pred_proba)
        pr_auc = self.metrics.get('pr_auc', 0)

        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, label=f'{self.model_name} (AUC = {pr_auc:.3f})', linewidth=2)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve - {self.model_name}')
        plt.legend()
        plt.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ PR curve saved to {save_path}")

        plt.close()

    def generate_evaluation_report(self, save_dir: Path = None) -> str:
        """
        Generate comprehensive evaluation report.

        Args:
            save_dir: Directory to save report

        Returns:
            Path to saved report
        """
        if save_dir is None:
            save_dir = MODELS_DIR / "evaluation_reports"

        save_dir.mkdir(parents=True, exist_ok=True)

        # Create plots
        self.plot_confusion_matrix(save_dir / f"{self.model_name}_confusion_matrix.png")
        if self.y_pred_proba is not None:
            self.plot_roc_curve(save_dir / f"{self.model_name}_roc_curve.png")
            self.plot_precision_recall_curve(save_dir / f"{self.model_name}_pr_curve.png")

        # Save metrics to CSV
        metrics_df = pd.DataFrame([self.metrics])
        metrics_path = save_dir / f"{self.model_name}_metrics.csv"
        metrics_df.to_csv(metrics_path, index=False)
        print(f"✓ Metrics saved to {metrics_path}")

        # Create text report
        report_path = save_dir / f"{self.model_name}_report.txt"
        with open(report_path, 'w') as f:
            f.write(f"{'='*70}\n")
            f.write(f"  CREDIT RISK MODEL EVALUATION REPORT\n")
            f.write(f"  Model: {self.model_name}\n")
            f.write(f"{'='*70}\n\n")

            f.write(classification_report(self.y_true, self.y_pred, target_names=['No Default', 'Default']))

            f.write(f"\n\nDetailed Metrics:\n")
            f.write(f"{'-'*70}\n")
            for key, value in self.metrics.items():
                if isinstance(value, float):
                    f.write(f"  {key:30s}: {value:.4f}\n")
                else:
                    f.write(f"  {key:30s}: {value}\n")

        print(f"✓ Report saved to {report_path}")

        return str(report_path)


def main():
    """Demonstration of model evaluation."""
    # This would typically be called with real model predictions
    # For demonstration, we'll create dummy data

    print("\n" + "="*70)
    print(" "*20 + "MODEL EVALUATION DEMO")
    print("="*70)

    # Create dummy predictions
    np.random.seed(42)
    n_samples = 1000

    y_true = np.random.binomial(1, 0.12, n_samples)  # 12% default rate
    y_pred_proba = np.random.beta(2, 8, n_samples)  # Realistic probabilities
    y_pred = (y_pred_proba > 0.5).astype(int)

    # Create evaluator
    evaluator = ModelEvaluator(model_name="demo_model")

    # Evaluate
    metrics = evaluator.evaluate(y_true, y_pred, y_pred_proba)

    # Generate report
    evaluator.generate_evaluation_report()

    print("\n✓ Evaluation complete!")


if __name__ == "__main__":
    main()
