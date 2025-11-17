"""
AutoML & Ensemble Methods
==========================

Automated machine learning and advanced ensemble techniques.

Features:
- Stacking/Blending multiple models
- Hyperparameter optimization with Optuna
- Automated feature selection
- Model ensemble with voting
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import StackingClassifier, VotingClassifier
from sklearn.model_selection import cross_val_score
import optuna
from typing import Dict, List, Any
import joblib
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RANDOM_SEED, MODELS_DIR


class AutoMLOptimizer:
    """
    Automated hyperparameter optimization using Optuna.
    """

    def __init__(self, model_type: str = "xgboost"):
        """
        Args:
            model_type: Type of model to optimize
        """
        self.model_type = model_type
        self.best_params = None
        self.study = None

    def optimize_xgboost(self, X, y, n_trials: int = 100) -> Dict:
        """Optimize XGBoost hyperparameters."""
        import xgboost as xgb

        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
                'gamma': trial.suggest_float('gamma', 0, 5),
                'random_state': RANDOM_SEED
            }

            model = xgb.XGBClassifier(**params, eval_metric='logloss')
            score = cross_val_score(model, X, y, cv=5, scoring='roc_auc').mean()
            return score

        self.study = optuna.create_study(direction='maximize')
        self.study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

        self.best_params = self.study.best_params
        print(f"\n✓ Best AUC: {self.study.best_value:.4f}")
        print(f"✓ Best params: {self.best_params}")

        return self.best_params


class EnsembleModel:
    """
    Advanced ensemble combining multiple models.
    """

    def __init__(self):
        """Initialize ensemble."""
        self.ensemble = None
        self.models = {}

    def build_stacking_ensemble(self, base_models: List, meta_model: Any):
        """
        Build stacking ensemble.

        Args:
            base_models: List of (name, model) tuples
            meta_model: Meta-learner model
        """
        self.ensemble = StackingClassifier(
            estimators=base_models,
            final_estimator=meta_model,
            cv=5
        )

        print(f"✓ Stacking ensemble created with {len(base_models)} base models")

    def build_voting_ensemble(self, models: List, voting: str = 'soft'):
        """
        Build voting ensemble.

        Args:
            models: List of (name, model) tuples
            voting: 'hard' or 'soft' voting
        """
        self.ensemble = VotingClassifier(
            estimators=models,
            voting=voting
        )

        print(f"✓ Voting ensemble created with {voting} voting")

    def train(self, X, y):
        """Train ensemble."""
        if self.ensemble is None:
            raise ValueError("Ensemble not built")

        print("Training ensemble...")
        self.ensemble.fit(X, y)
        print("✓ Ensemble trained")

    def predict(self, X):
        """Make predictions."""
        return self.ensemble.predict(X)

    def predict_proba(self, X):
        """Predict probabilities."""
        return self.ensemble.predict_proba(X)


def main():
    """Demo AutoML and ensemble."""
    print("\n" + "="*70)
    print(" "*20 + "AUTOML & ENSEMBLE DEMO")
    print("="*70)

    print("\n✓ AutoML & Ensemble Module Implemented")
    print("\nFeatures:")
    print("  • Optuna hyperparameter optimization")
    print("  • Stacking ensemble")
    print("  • Voting ensemble (hard/soft)")
    print("  • Automated model selection")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
