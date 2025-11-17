"""
Model Training Pipeline
========================

This module handles training multiple machine learning models for credit risk prediction.

Models Implemented:
1. XGBoost - Gradient Boosting (best for tabular data)
2. LightGBM - Fast gradient boosting
3. Random Forest - Ensemble learning
4. Logistic Regression - Baseline model

Nigerian Context:
- Models are tuned for imbalanced data (12% default rate)
- Feature importance helps identify key risk factors in Nigerian context
- Cross-validation ensures generalization across different regions/sectors
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
import xgboost as xgb
import lightgbm as lgb
import joblib
from datetime import datetime
from typing import Dict, Tuple, Any
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import MODEL_PARAMS, RANDOM_SEED, MODELS_DIR


class CreditRiskModelTrainer:
    """
    Train and manage multiple ML models for credit risk prediction.

    This class handles:
    - Training multiple model types
    - Hyperparameter tuning
    - Model comparison
    - Model persistence
    - Feature importance analysis
    """

    def __init__(self):
        """Initialize the model trainer."""
        self.models = {}
        self.model_scores = {}
        self.best_model_name = None
        self.feature_importance = {}

    def get_models(self) -> Dict[str, Any]:
        """
        Initialize all models with default parameters.

        Returns:
            Dictionary of model names and instances
        """
        models = {
            'xgboost': xgb.XGBClassifier(**MODEL_PARAMS['xgboost'], eval_metric='logloss'),
            'lightgbm': lgb.LGBMClassifier(**MODEL_PARAMS['lightgbm'], verbose=-1),
            'random_forest': RandomForestClassifier(**MODEL_PARAMS['random_forest']),
            'logistic_regression': LogisticRegression(
                random_state=RANDOM_SEED,
                max_iter=1000,
                class_weight='balanced'
            )
        }
        return models

    def train_single_model(
        self,
        model_name: str,
        model: Any,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame = None,
        y_val: pd.Series = None
    ) -> Tuple[Any, Dict]:
        """
        Train a single model.

        Args:
            model_name: Name of the model
            model: Model instance
            X_train: Training features
            y_train: Training target
            X_val: Validation features (optional)
            y_val: Validation target (optional)

        Returns:
            Tuple of (trained_model, training_info)
        """
        print(f"\n  Training {model_name}...")
        start_time = datetime.now()

        # Special handling for XGBoost and LightGBM with early stopping
        if model_name in ['xgboost', 'lightgbm'] and X_val is not None:
            if model_name == 'xgboost':
                model.fit(
                    X_train, y_train,
                    eval_set=[(X_val, y_val)],
                    verbose=False
                )
            else:  # lightgbm
                model.fit(
                    X_train, y_train,
                    eval_set=[(X_val, y_val)],
                    callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)]
                )
        else:
            model.fit(X_train, y_train)

        training_time = (datetime.now() - start_time).total_seconds()

        # Get training score
        train_score = model.score(X_train, y_train)

        # Get validation score if available
        val_score = model.score(X_val, y_val) if X_val is not None else None

        training_info = {
            'train_accuracy': train_score,
            'val_accuracy': val_score,
            'training_time_seconds': training_time,
            'model_params': model.get_params()
        }

        print(f"    ✓ Training accuracy: {train_score:.4f}")
        if val_score:
            print(f"    ✓ Validation accuracy: {val_score:.4f}")
        print(f"    ✓ Training time: {training_time:.2f}s")

        return model, training_info

    def cross_validate_model(
        self,
        model_name: str,
        model: Any,
        X: pd.DataFrame,
        y: pd.Series,
        cv: int = 5
    ) -> Dict:
        """
        Perform cross-validation on a model.

        Args:
            model_name: Name of the model
            model: Model instance
            X: Features
            y: Target
            cv: Number of cross-validation folds

        Returns:
            Dictionary with CV scores
        """
        print(f"\n  Cross-validating {model_name} ({cv} folds)...")

        # Use stratified K-fold to maintain class distribution
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=RANDOM_SEED)

        # Multiple scoring metrics
        scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']

        cv_results = {}
        for score_name in scoring:
            scores = cross_val_score(
                model, X, y,
                cv=skf,
                scoring=score_name,
                n_jobs=-1
            )
            cv_results[f'{score_name}_mean'] = scores.mean()
            cv_results[f'{score_name}_std'] = scores.std()

            print(f"    ✓ {score_name.upper()}: {scores.mean():.4f} (+/- {scores.std():.4f})")

        return cv_results

    def get_feature_importance(
        self,
        model_name: str,
        model: Any,
        feature_names: List[str]
    ) -> pd.DataFrame:
        """
        Extract feature importance from trained model.

        Args:
            model_name: Name of the model
            model: Trained model
            feature_names: List of feature names

        Returns:
            DataFrame with feature importances
        """
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # For logistic regression, use absolute coefficients
            importances = np.abs(model.coef_[0])
        else:
            return None

        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)

        return importance_df

    def train_all_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame = None,
        y_val: pd.Series = None,
        perform_cv: bool = True
    ) -> Dict:
        """
        Train all models and compare performance.

        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            perform_cv: Whether to perform cross-validation

        Returns:
            Dictionary with all model results
        """
        print("\n" + "="*70)
        print(" "*20 + "MODEL TRAINING PIPELINE")
        print("="*70)

        print(f"\nTraining on {len(X_train):,} samples with {len(X_train.columns)} features")
        print(f"Class distribution: {y_train.value_counts().to_dict()}")

        # Get all models
        models = self.get_models()
        results = {}

        # Train each model
        for model_name, model in models.items():
            print(f"\n{'─'*70}")
            print(f"Model: {model_name.upper()}")
            print(f"{'─'*70}")

            # Train model
            trained_model, training_info = self.train_single_model(
                model_name, model, X_train, y_train, X_val, y_val
            )

            # Cross-validation
            cv_results = {}
            if perform_cv:
                cv_results = self.cross_validate_model(
                    model_name, model, X_train, y_train
                )

            # Feature importance
            feature_importance = self.get_feature_importance(
                model_name, trained_model, X_train.columns.tolist()
            )

            # Store results
            self.models[model_name] = trained_model
            self.feature_importance[model_name] = feature_importance

            results[model_name] = {
                'model': trained_model,
                'training_info': training_info,
                'cv_results': cv_results,
                'feature_importance': feature_importance
            }

            # Store score for comparison
            if cv_results:
                self.model_scores[model_name] = cv_results['roc_auc_mean']
            elif training_info['val_accuracy']:
                self.model_scores[model_name] = training_info['val_accuracy']
            else:
                self.model_scores[model_name] = training_info['train_accuracy']

        # Identify best model
        self.best_model_name = max(self.model_scores, key=self.model_scores.get)

        print("\n" + "="*70)
        print(" "*25 + "TRAINING COMPLETE")
        print("="*70)
        print("\nModel Performance Summary:")
        for model_name, score in sorted(self.model_scores.items(), key=lambda x: x[1], reverse=True):
            print(f"  {model_name:20s}: {score:.4f}")
        print(f"\n  🏆 Best Model: {self.best_model_name.upper()} ({self.model_scores[self.best_model_name]:.4f})")
        print("="*70 + "\n")

        return results

    def get_best_model(self) -> Tuple[str, Any]:
        """
        Get the best performing model.

        Returns:
            Tuple of (model_name, model)
        """
        if not self.best_model_name:
            raise ValueError("No models trained yet. Run train_all_models() first.")

        return self.best_model_name, self.models[self.best_model_name]

    def display_feature_importance(self, model_name: str = None, top_n: int = 20):
        """
        Display feature importance for a model.

        Args:
            model_name: Name of model (uses best model if None)
            top_n: Number of top features to display
        """
        if model_name is None:
            model_name = self.best_model_name

        if model_name not in self.feature_importance:
            print(f"No feature importance available for {model_name}")
            return

        importance_df = self.feature_importance[model_name]

        if importance_df is None:
            print(f"Model {model_name} does not support feature importance")
            return

        print(f"\n{'='*70}")
        print(f"Top {top_n} Most Important Features - {model_name.upper()}")
        print(f"{'='*70}")

        for idx, row in importance_df.head(top_n).iterrows():
            bar_length = int(row['importance'] / importance_df['importance'].max() * 50)
            bar = '█' * bar_length
            print(f"  {row['feature']:30s} {'│'} {bar} {row['importance']:.4f}")

        print(f"{'='*70}\n")

    def save_models(self, save_dir: Path = None):
        """
        Save all trained models.

        Args:
            save_dir: Directory to save models
        """
        if save_dir is None:
            save_dir = MODELS_DIR

        save_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*70}")
        print("Saving Models")
        print(f"{'='*70}")

        for model_name, model in self.models.items():
            filepath = save_dir / f"{model_name}_model.pkl"
            joblib.dump(model, filepath)
            print(f"  ✓ Saved {model_name} to {filepath}")

        # Save feature importances
        for model_name, importance_df in self.feature_importance.items():
            if importance_df is not None:
                filepath = save_dir / f"{model_name}_feature_importance.csv"
                importance_df.to_csv(filepath, index=False)
                print(f"  ✓ Saved {model_name} feature importance to {filepath}")

        # Save model comparison
        comparison_df = pd.DataFrame({
            'model': list(self.model_scores.keys()),
            'score': list(self.model_scores.values())
        }).sort_values('score', ascending=False)

        comparison_filepath = save_dir / "model_comparison.csv"
        comparison_df.to_csv(comparison_filepath, index=False)
        print(f"  ✓ Saved model comparison to {comparison_filepath}")

        # Save best model metadata
        metadata = {
            'best_model': self.best_model_name,
            'best_score': self.model_scores[self.best_model_name],
            'timestamp': datetime.now().isoformat(),
            'all_scores': self.model_scores
        }
        metadata_filepath = save_dir / "model_metadata.pkl"
        joblib.dump(metadata, metadata_filepath)
        print(f"  ✓ Saved metadata to {metadata_filepath}")

        print(f"{'='*70}\n")

    @classmethod
    def load_model(cls, model_name: str, models_dir: Path = None) -> Any:
        """
        Load a trained model.

        Args:
            model_name: Name of the model to load
            models_dir: Directory containing models

        Returns:
            Loaded model
        """
        if models_dir is None:
            models_dir = MODELS_DIR

        filepath = models_dir / f"{model_name}_model.pkl"
        model = joblib.load(filepath)
        print(f"✓ Loaded {model_name} from {filepath}")
        return model


def main():
    """Main function to demonstrate model training."""
    from src.data.generate_data import NigerianLoanDataGenerator
    from src.data.preprocessing import DataPreprocessor
    from src.data.feature_engineering import FeatureEngineer

    print("\n" + "="*70)
    print(" "*15 + "NIGERIAN CREDIT RISK MODEL TRAINING")
    print("="*70)

    # Step 1: Generate data
    print("\n[1/4] Generating Nigerian loan data...")
    generator = NigerianLoanDataGenerator(n_samples=10000)
    df = generator.generate()

    # Step 2: Feature engineering
    print("\n[2/4] Engineering features...")
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_features(df)

    # Step 3: Preprocess data
    print("\n[3/4] Preprocessing data...")
    preprocessor = DataPreprocessor()
    processed_data = preprocessor.fit_transform(df_engineered, apply_smote=True)

    # Save preprocessor
    preprocessor.save()

    # Step 4: Train models
    print("\n[4/4] Training models...")
    trainer = CreditRiskModelTrainer()

    results = trainer.train_all_models(
        X_train=processed_data['X_train'],
        y_train=processed_data['y_train'],
        X_val=processed_data['X_val'],
        y_val=processed_data['y_val'],
        perform_cv=True
    )

    # Display feature importance for best model
    trainer.display_feature_importance(top_n=20)

    # Save all models
    trainer.save_models()

    print("\n" + "="*70)
    print(" "*20 + "TRAINING PIPELINE COMPLETE!")
    print("="*70)
    print(f"\n✓ Best Model: {trainer.best_model_name}")
    print(f"✓ Best Score: {trainer.model_scores[trainer.best_model_name]:.4f}")
    print(f"✓ Total Models Trained: {len(trainer.models)}")
    print(f"✓ Models saved to: {MODELS_DIR}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
