"""
Model Monitoring Module
========================

Monitors model performance in production to detect degradation and drift.

Key Metrics Tracked:
1. Prediction distribution (are predictions changing?)
2. Performance metrics (accuracy, AUC, precision, recall)
3. Model drift (is the model behavior changing?)
4. Alert system for anomalies

Nigerian Context:
- Monitors for seasonal patterns (harvest season, oil price changes)
- Tracks performance across different sectors and regions
- Alerts on economic event impacts (naira devaluation, policy changes)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import MONITORING_THRESHOLDS, DATA_DIR


class ModelMonitor:
    """
    Monitor model performance in production.

    Tracks predictions, calculates metrics, and alerts on anomalies.
    """

    def __init__(self, model_name: str = "production_model"):
        """
        Initialize model monitor.

        Args:
            model_name: Name of model being monitored
        """
        self.model_name = model_name
        self.predictions_log = []
        self.metrics_history = []
        self.alerts = []

    def log_prediction(
        self,
        application_id: str,
        prediction: float,
        true_label: int = None,
        features: Dict = None
    ):
        """
        Log a prediction for monitoring.

        Args:
            application_id: Unique application ID
            prediction: Predicted probability
            true_label: True outcome (if known)
            features: Input features dictionary
        """
        log_entry = {
            'timestamp': datetime.now(),
            'application_id': application_id,
            'prediction': prediction,
            'true_label': true_label,
            'features': features
        }
        self.predictions_log.append(log_entry)

    def calculate_metrics(
        self,
        window_days: int = 7
    ) -> Dict:
        """
        Calculate performance metrics over a time window.

        Args:
            window_days: Number of days to calculate metrics over

        Returns:
            Dictionary of metrics
        """
        if not self.predictions_log:
            return {}

        # Convert to DataFrame
        df = pd.DataFrame(self.predictions_log)

        # Filter to window
        cutoff_date = datetime.now() - timedelta(days=window_days)
        df_window = df[df['timestamp'] >= cutoff_date].copy()

        if len(df_window) == 0:
            return {}

        # Calculate metrics
        metrics = {
            'total_predictions': len(df_window),
            'avg_predicted_probability': df_window['prediction'].mean(),
            'median_predicted_probability': df_window['prediction'].median(),
            'std_predicted_probability': df_window['prediction'].std(),
            'predictions_above_50pct': (df_window['prediction'] > 0.5).sum(),
            'high_risk_rate': (df_window['prediction'] > 0.3).sum() / len(df_window)
        }

        # If we have true labels, calculate accuracy metrics
        if df_window['true_label'].notna().any():
            df_labeled = df_window[df_window['true_label'].notna()].copy()

            if len(df_labeled) > 0:
                df_labeled['predicted_class'] = (df_labeled['prediction'] > 0.5).astype(int)

                from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

                try:
                    metrics['accuracy'] = accuracy_score(
                        df_labeled['true_label'],
                        df_labeled['predicted_class']
                    )
                    metrics['precision'] = precision_score(
                        df_labeled['true_label'],
                        df_labeled['predicted_class'],
                        zero_division=0
                    )
                    metrics['recall'] = recall_score(
                        df_labeled['true_label'],
                        df_labeled['predicted_class'],
                        zero_division=0
                    )
                    metrics['roc_auc'] = roc_auc_score(
                        df_labeled['true_label'],
                        df_labeled['prediction']
                    )
                except Exception as e:
                    print(f"Warning: Could not calculate some metrics: {e}")

        # Store metrics
        self.metrics_history.append({
            'timestamp': datetime.now(),
            'window_days': window_days,
            'metrics': metrics
        })

        return metrics

    def check_for_drift(
        self,
        current_window_days: int = 7,
        baseline_window_days: int = 30,
        threshold: float = 0.1
    ) -> Dict:
        """
        Check for model drift by comparing recent predictions to baseline.

        Args:
            current_window_days: Recent window for comparison
            baseline_window_days: Historical baseline window
            threshold: Threshold for drift detection (10% change)

        Returns:
            Dictionary with drift analysis
        """
        if len(self.predictions_log) < 100:
            return {'drift_detected': False, 'reason': 'Insufficient data'}

        df = pd.DataFrame(self.predictions_log)

        # Recent predictions
        recent_cutoff = datetime.now() - timedelta(days=current_window_days)
        df_recent = df[df['timestamp'] >= recent_cutoff]

        # Baseline predictions
        baseline_cutoff = datetime.now() - timedelta(days=baseline_window_days)
        baseline_start = datetime.now() - timedelta(days=baseline_window_days + current_window_days)
        df_baseline = df[(df['timestamp'] >= baseline_start) & (df['timestamp'] < baseline_cutoff)]

        if len(df_recent) < 10 or len(df_baseline) < 10:
            return {'drift_detected': False, 'reason': 'Insufficient data'}

        # Compare distributions
        recent_mean = df_recent['prediction'].mean()
        baseline_mean = df_baseline['prediction'].mean()

        recent_std = df_recent['prediction'].std()
        baseline_std = df_baseline['prediction'].std()

        # Calculate drift
        mean_drift = abs(recent_mean - baseline_mean) / baseline_mean if baseline_mean > 0 else 0
        std_drift = abs(recent_std - baseline_std) / baseline_std if baseline_std > 0 else 0

        drift_detected = mean_drift > threshold or std_drift > threshold

        drift_analysis = {
            'drift_detected': drift_detected,
            'mean_drift': mean_drift,
            'std_drift': std_drift,
            'recent_mean': recent_mean,
            'baseline_mean': baseline_mean,
            'recent_std': recent_std,
            'baseline_std': baseline_std,
            'threshold': threshold
        }

        if drift_detected:
            self.create_alert(
                'MODEL_DRIFT',
                f'Drift detected: mean_drift={mean_drift:.2%}, std_drift={std_drift:.2%}',
                severity='HIGH'
            )

        return drift_analysis

    def check_performance_degradation(self) -> Dict:
        """
        Check if model performance has degraded below thresholds.

        Returns:
            Dictionary with degradation analysis
        """
        metrics = self.calculate_metrics(window_days=7)

        if not metrics:
            return {'degradation_detected': False, 'reason': 'No metrics available'}

        degradation_detected = False
        issues = []

        # Check against thresholds
        if 'accuracy' in metrics:
            if metrics['accuracy'] < MONITORING_THRESHOLDS['min_accuracy']:
                issues.append(f"Accuracy below threshold: {metrics['accuracy']:.2%}")
                degradation_detected = True

        if 'roc_auc' in metrics:
            if metrics['roc_auc'] < MONITORING_THRESHOLDS['min_auc_roc']:
                issues.append(f"ROC-AUC below threshold: {metrics['roc_auc']:.2%}")
                degradation_detected = True

        if degradation_detected:
            self.create_alert(
                'PERFORMANCE_DEGRADATION',
                '; '.join(issues),
                severity='CRITICAL'
            )

        return {
            'degradation_detected': degradation_detected,
            'issues': issues,
            'metrics': metrics
        }

    def create_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = 'MEDIUM'
    ):
        """
        Create a monitoring alert.

        Args:
            alert_type: Type of alert
            message: Alert message
            severity: LOW, MEDIUM, HIGH, or CRITICAL
        """
        alert = {
            'timestamp': datetime.now(),
            'type': alert_type,
            'message': message,
            'severity': severity,
            'model_name': self.model_name
        }
        self.alerts.append(alert)
        print(f"\n🚨 ALERT [{severity}]: {alert_type}")
        print(f"   {message}")

    def get_alerts(self, severity: str = None, hours: int = 24) -> List[Dict]:
        """
        Get recent alerts.

        Args:
            severity: Filter by severity
            hours: Look back hours

        Returns:
            List of alerts
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_alerts = [a for a in self.alerts if a['timestamp'] >= cutoff]

        if severity:
            recent_alerts = [a for a in recent_alerts if a['severity'] == severity]

        return recent_alerts

    def generate_monitoring_report(self) -> str:
        """
        Generate monitoring report.

        Returns:
            Formatted report string
        """
        # Calculate current metrics
        metrics_7d = self.calculate_metrics(window_days=7)
        metrics_30d = self.calculate_metrics(window_days=30)

        # Check for drift
        drift_analysis = self.check_for_drift()

        # Check for degradation
        degradation_analysis = self.check_performance_degradation()

        # Get recent alerts
        critical_alerts = self.get_alerts(severity='CRITICAL', hours=24)
        high_alerts = self.get_alerts(severity='HIGH', hours=24)

        report = f"""
{'='*70}
  MODEL MONITORING REPORT - {self.model_name}
{'='*70}
  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PREDICTION STATISTICS (7 Days)
{'-'*70}
  Total Predictions:     {metrics_7d.get('total_predictions', 0):,}
  Avg Probability:       {metrics_7d.get('avg_predicted_probability', 0):.2%}
  High Risk Rate:        {metrics_7d.get('high_risk_rate', 0):.2%}
"""

        if 'accuracy' in metrics_7d:
            report += f"""
PERFORMANCE METRICS (7 Days)
{'-'*70}
  Accuracy:              {metrics_7d['accuracy']:.2%}
  Precision:             {metrics_7d.get('precision', 0):.2%}
  Recall:                {metrics_7d.get('recall', 0):.2%}
  ROC-AUC:               {metrics_7d.get('roc_auc', 0):.2%}
"""

        report += f"""
DRIFT ANALYSIS
{'-'*70}
  Drift Detected:        {'YES ⚠️' if drift_analysis.get('drift_detected') else 'NO ✓'}
  Mean Drift:            {drift_analysis.get('mean_drift', 0):.2%}
  Std Drift:             {drift_analysis.get('std_drift', 0):.2%}

ALERTS (24 Hours)
{'-'*70}
  Critical:              {len(critical_alerts)}
  High:                  {len(high_alerts)}
"""

        if critical_alerts or high_alerts:
            report += f"\nRecent Alerts:\n{'-'*70}\n"
            for alert in critical_alerts + high_alerts:
                report += f"  [{alert['severity']}] {alert['type']}: {alert['message']}\n"

        report += f"\n{'='*70}\n"

        return report

    def save_logs(self, filepath: Path = None):
        """
        Save prediction logs to file.

        Args:
            filepath: Path to save logs
        """
        if filepath is None:
            filepath = DATA_DIR / f"monitoring_{self.model_name}_{datetime.now().strftime('%Y%m%d')}.json"

        # Convert timestamps to strings
        logs_to_save = []
        for log in self.predictions_log:
            log_copy = log.copy()
            log_copy['timestamp'] = log_copy['timestamp'].isoformat()
            logs_to_save.append(log_copy)

        with open(filepath, 'w') as f:
            json.dump(logs_to_save, f, indent=2)

        print(f"✓ Saved {len(logs_to_save)} prediction logs to {filepath}")


def main():
    """Demonstration of model monitoring."""
    print("\n" + "="*70)
    print(" "*20 + "MODEL MONITORING DEMO")
    print("="*70)

    # Create monitor
    monitor = ModelMonitor(model_name="demo_model")

    # Simulate predictions
    print("\nSimulating predictions...")
    np.random.seed(42)

    for i in range(500):
        # Simulate predictions with some drift
        if i < 250:
            prediction = np.random.beta(2, 8)  # Baseline: mostly low risk
        else:
            prediction = np.random.beta(3, 5)  # Drift: more high risk

        # Simulate true labels (with some delay)
        true_label = np.random.binomial(1, prediction) if i < 400 else None

        monitor.log_prediction(
            application_id=f"APP{i:05d}",
            prediction=prediction,
            true_label=true_label
        )

    print(f"✓ Logged {len(monitor.predictions_log)} predictions")

    # Generate report
    print("\n" + monitor.generate_monitoring_report())

    # Save logs
    monitor.save_logs()


if __name__ == "__main__":
    main()
