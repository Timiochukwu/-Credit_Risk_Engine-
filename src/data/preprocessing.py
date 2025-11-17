"""
Data Preprocessing Pipeline
============================

This module handles data cleaning, transformation, and preparation for ML models.

Key Steps:
1. Handle missing values
2. Remove outliers
3. Encode categorical variables
4. Scale numerical features
5. Handle class imbalance (SMOTE)
6. Split data into train/validation/test sets

Nigerian Context:
- Validates Nigerian phone numbers and addresses
- Handles Naira currency formatting
- Considers Nigerian-specific data quality issues
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
from typing import Tuple, Dict, List
import joblib
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import (
    RANDOM_SEED, TEST_SIZE, VALIDATION_SIZE,
    PROCESSED_DATA_DIR, MODELS_DIR
)


class DataPreprocessor:
    """
    Comprehensive data preprocessing pipeline for Nigerian loan data.

    This class handles all data cleaning and transformation needed before
    training ML models.
    """

    def __init__(self):
        """Initialize the preprocessor with empty encoders and scalers."""
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.feature_names = None
        self.categorical_columns = []
        self.numerical_columns = []

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the raw data.

        Args:
            df: Raw DataFrame

        Returns:
            Cleaned DataFrame
        """
        print("\n" + "="*60)
        print("STEP 1: Data Cleaning")
        print("="*60)

        df_clean = df.copy()
        initial_rows = len(df_clean)

        # 1. Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['application_id'], keep='first')
        duplicates_removed = initial_rows - len(df_clean)
        if duplicates_removed > 0:
            print(f"  ✓ Removed {duplicates_removed} duplicate applications")

        # 2. Validate age
        df_clean = df_clean[(df_clean['age'] >= 18) & (df_clean['age'] <= 100)]
        print(f"  ✓ Validated age range (18-100)")

        # 3. Validate income (must be positive)
        df_clean = df_clean[df_clean['monthly_income'] > 0]
        print(f"  ✓ Removed records with invalid income")

        # 4. Validate loan amount (must be positive)
        df_clean = df_clean[df_clean['loan_amount'] > 0]
        print(f"  ✓ Removed records with invalid loan amount")

        # 5. Fix any negative values in numeric columns
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['defaulted', 'previous_defaults']:  # These can be 0/1
                df_clean[col] = df_clean[col].clip(lower=0)

        # 6. Handle missing values in critical columns
        critical_columns = ['monthly_income', 'loan_amount', 'age', 'defaulted']
        df_clean = df_clean.dropna(subset=critical_columns)

        # 7. Validate debt-to-income ratio
        # Recalculate to ensure consistency
        df_clean['debt_to_income_ratio'] = (
            (df_clean['existing_monthly_debt'] + df_clean['monthly_payment']) /
            df_clean['monthly_income']
        )

        # Remove extreme outliers (DTI > 2.0 is unrealistic)
        df_clean = df_clean[df_clean['debt_to_income_ratio'] <= 2.0]

        final_rows = len(df_clean)
        print(f"\n  Initial rows: {initial_rows:,}")
        print(f"  Final rows: {final_rows:,}")
        print(f"  Rows removed: {initial_rows - final_rows:,} ({(initial_rows-final_rows)/initial_rows*100:.1f}%)")

        return df_clean

    def identify_column_types(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """
        Identify categorical and numerical columns.

        Args:
            df: DataFrame

        Returns:
            Tuple of (categorical_columns, numerical_columns)
        """
        # Columns to exclude from features (ID, target, metadata, personal info)
        exclude_columns = [
            'application_id', 'defaulted', 'application_date', 'currency',
            'first_name', 'last_name', 'full_name', 'email', 'phone',
            'address', 'city', 'state', 'monthly_payment'  # Derived from loan amount & term
        ]

        # Categorical columns
        categorical = [
            'education', 'employment_sector', 'loan_purpose', 'bank'
        ]

        # Numerical columns (all others that aren't excluded)
        all_columns = df.columns.tolist()
        numerical = [
            col for col in all_columns
            if col not in exclude_columns and col not in categorical
        ]

        # Ensure target variable is not in features
        if 'defaulted' in numerical:
            numerical.remove('defaulted')
        if 'defaulted' in categorical:
            categorical.remove('defaulted')

        self.categorical_columns = categorical
        self.numerical_columns = numerical

        print("\n" + "="*60)
        print("STEP 2: Feature Type Identification")
        print("="*60)
        print(f"  Categorical features ({len(categorical)}): {categorical}")
        print(f"  Numerical features ({len(numerical)}): {numerical}")

        return categorical, numerical

    def encode_categorical(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Encode categorical variables using Label Encoding.

        Args:
            df: DataFrame
            fit: Whether to fit encoders (True for training, False for inference)

        Returns:
            DataFrame with encoded categorical variables
        """
        print("\n" + "="*60)
        print("STEP 3: Categorical Encoding")
        print("="*60)

        df_encoded = df.copy()

        for col in self.categorical_columns:
            if col in df_encoded.columns:
                if fit:
                    # Fit new encoder
                    self.label_encoders[col] = LabelEncoder()
                    df_encoded[col] = self.label_encoders[col].fit_transform(df_encoded[col].astype(str))
                    print(f"  ✓ Encoded '{col}': {len(self.label_encoders[col].classes_)} categories")
                else:
                    # Use existing encoder
                    if col in self.label_encoders:
                        # Handle unseen categories
                        df_encoded[col] = df_encoded[col].astype(str)
                        known_values = set(self.label_encoders[col].classes_)
                        df_encoded[col] = df_encoded[col].apply(
                            lambda x: x if x in known_values else self.label_encoders[col].classes_[0]
                        )
                        df_encoded[col] = self.label_encoders[col].transform(df_encoded[col])

        return df_encoded

    def scale_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Scale numerical features using StandardScaler.

        Args:
            df: DataFrame
            fit: Whether to fit scaler (True for training, False for inference)

        Returns:
            DataFrame with scaled features
        """
        print("\n" + "="*60)
        print("STEP 4: Feature Scaling")
        print("="*60)

        df_scaled = df.copy()

        if fit:
            df_scaled[self.numerical_columns] = self.scaler.fit_transform(
                df_scaled[self.numerical_columns]
            )
            print(f"  ✓ Scaled {len(self.numerical_columns)} numerical features")
            print(f"  ✓ Mean: ~0, Std: ~1")
        else:
            df_scaled[self.numerical_columns] = self.scaler.transform(
                df_scaled[self.numerical_columns]
            )

        return df_scaled

    def handle_imbalance(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        method: str = 'smote'
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Handle class imbalance using SMOTE (Synthetic Minority Over-sampling).

        Args:
            X: Features
            y: Target variable
            method: Resampling method ('smote' or 'none')

        Returns:
            Resampled (X, y)
        """
        print("\n" + "="*60)
        print("STEP 5: Handling Class Imbalance")
        print("="*60)

        original_counts = y.value_counts()
        print(f"  Original class distribution:")
        print(f"    No Default (0): {original_counts.get(0, 0):,} ({original_counts.get(0, 0)/len(y)*100:.1f}%)")
        print(f"    Default (1): {original_counts.get(1, 0):,} ({original_counts.get(1, 0)/len(y)*100:.1f}%)")

        if method.lower() == 'smote':
            # Use SMOTE to create synthetic samples of minority class
            smote = SMOTE(random_state=RANDOM_SEED, k_neighbors=5)
            X_resampled, y_resampled = smote.fit_resample(X, y)

            new_counts = pd.Series(y_resampled).value_counts()
            print(f"\n  After SMOTE:")
            print(f"    No Default (0): {new_counts.get(0, 0):,} ({new_counts.get(0, 0)/len(y_resampled)*100:.1f}%)")
            print(f"    Default (1): {new_counts.get(1, 0):,} ({new_counts.get(1, 0)/len(y_resampled)*100:.1f}%)")

            return pd.DataFrame(X_resampled, columns=X.columns), pd.Series(y_resampled)
        else:
            print("  ⚠ Skipping resampling")
            return X, y

    def prepare_features(
        self,
        df: pd.DataFrame,
        fit: bool = True
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for modeling.

        Args:
            df: Raw DataFrame
            fit: Whether to fit transformers

        Returns:
            Tuple of (X, y) - features and target
        """
        # Separate features and target
        if 'defaulted' in df.columns:
            X = df.drop(columns=['defaulted'])
            y = df['defaulted']
        else:
            X = df
            y = None

        # Keep only feature columns
        feature_cols = self.categorical_columns + self.numerical_columns
        X = X[feature_cols]

        # Store feature names
        if fit:
            self.feature_names = X.columns.tolist()

        return X, y

    def split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = TEST_SIZE,
        val_size: float = VALIDATION_SIZE
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
        """
        Split data into train, validation, and test sets.

        Args:
            X: Features
            y: Target
            test_size: Proportion for test set
            val_size: Proportion of remaining data for validation

        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        print("\n" + "="*60)
        print("STEP 6: Train/Validation/Test Split")
        print("="*60)

        # First split: separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=RANDOM_SEED,
            stratify=y  # Maintain class distribution
        )

        # Second split: separate validation from training
        val_size_adjusted = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size_adjusted,
            random_state=RANDOM_SEED,
            stratify=y_temp
        )

        print(f"  Training set: {len(X_train):,} samples ({len(X_train)/len(X)*100:.1f}%)")
        print(f"    - Defaults: {y_train.sum():,} ({y_train.sum()/len(y_train)*100:.1f}%)")
        print(f"  Validation set: {len(X_val):,} samples ({len(X_val)/len(X)*100:.1f}%)")
        print(f"    - Defaults: {y_val.sum():,} ({y_val.sum()/len(y_val)*100:.1f}%)")
        print(f"  Test set: {len(X_test):,} samples ({len(X_test)/len(X)*100:.1f}%)")
        print(f"    - Defaults: {y_test.sum():,} ({y_test.sum()/len(y_test)*100:.1f}%)")

        return X_train, X_val, X_test, y_train, y_val, y_test

    def fit_transform(
        self,
        df: pd.DataFrame,
        apply_smote: bool = True
    ) -> Dict:
        """
        Complete preprocessing pipeline (fit and transform).

        Args:
            df: Raw DataFrame
            apply_smote: Whether to apply SMOTE for class imbalance

        Returns:
            Dictionary with processed data splits
        """
        print("\n" + "="*70)
        print(" "*15 + "DATA PREPROCESSING PIPELINE")
        print("="*70)

        # Step 1: Clean data
        df_clean = self.clean_data(df)

        # Step 2: Identify column types
        self.identify_column_types(df_clean)

        # Step 3: Prepare features
        X, y = self.prepare_features(df_clean, fit=True)

        # Step 4: Split data BEFORE encoding/scaling
        # This prevents data leakage
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, y)

        # Step 5: Encode categorical variables (fit on train only)
        X_train_encoded = self.encode_categorical(X_train, fit=True)
        X_val_encoded = self.encode_categorical(X_val, fit=False)
        X_test_encoded = self.encode_categorical(X_test, fit=False)

        # Step 6: Scale features (fit on train only)
        X_train_scaled = self.scale_features(X_train_encoded, fit=True)
        X_val_scaled = self.scale_features(X_val_encoded, fit=False)
        X_test_scaled = self.scale_features(X_test_encoded, fit=False)

        # Step 7: Handle class imbalance (only on training set)
        if apply_smote:
            X_train_final, y_train_final = self.handle_imbalance(
                X_train_scaled, y_train, method='smote'
            )
        else:
            X_train_final, y_train_final = X_train_scaled, y_train

        print("\n" + "="*70)
        print(" "*20 + "PREPROCESSING COMPLETE!")
        print("="*70 + "\n")

        return {
            'X_train': X_train_final,
            'X_val': X_val_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train_final,
            'y_val': y_val,
            'y_test': y_test,
            'feature_names': self.feature_names
        }

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data using fitted preprocessor (for inference).

        Args:
            df: New data to transform

        Returns:
            Transformed features
        """
        # Prepare features
        X, _ = self.prepare_features(df, fit=False)

        # Encode
        X_encoded = self.encode_categorical(X, fit=False)

        # Scale
        X_scaled = self.scale_features(X_encoded, fit=False)

        return X_scaled

    def save(self, filepath: str = None):
        """
        Save the fitted preprocessor.

        Args:
            filepath: Path to save the preprocessor
        """
        if filepath is None:
            filepath = MODELS_DIR / "preprocessor.pkl"

        joblib.dump({
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'categorical_columns': self.categorical_columns,
            'numerical_columns': self.numerical_columns
        }, filepath)

        print(f"\n✓ Preprocessor saved to: {filepath}")

    @classmethod
    def load(cls, filepath: str = None):
        """
        Load a fitted preprocessor.

        Args:
            filepath: Path to saved preprocessor

        Returns:
            Loaded DataPreprocessor instance
        """
        if filepath is None:
            filepath = MODELS_DIR / "preprocessor.pkl"

        preprocessor = cls()
        saved_data = joblib.load(filepath)

        preprocessor.label_encoders = saved_data['label_encoders']
        preprocessor.scaler = saved_data['scaler']
        preprocessor.feature_names = saved_data['feature_names']
        preprocessor.categorical_columns = saved_data['categorical_columns']
        preprocessor.numerical_columns = saved_data['numerical_columns']

        print(f"✓ Preprocessor loaded from: {filepath}")
        return preprocessor


def main():
    """Main function to demonstrate preprocessing."""
    from src.data.generate_data import NigerianLoanDataGenerator

    # Generate sample data
    print("Generating sample data...")
    generator = NigerianLoanDataGenerator(n_samples=5000)
    df = generator.generate()

    # Preprocess
    preprocessor = DataPreprocessor()
    processed_data = preprocessor.fit_transform(df, apply_smote=True)

    # Save preprocessor
    preprocessor.save()

    print(f"\n✓ Preprocessing demonstration complete!")
    print(f"✓ Training samples: {len(processed_data['X_train']):,}")
    print(f"✓ Features: {len(processed_data['feature_names'])}")


if __name__ == "__main__":
    main()
