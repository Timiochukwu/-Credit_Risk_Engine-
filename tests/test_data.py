"""
Tests for Data Generation and Preprocessing
============================================
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data.generate_data import NigerianLoanDataGenerator
from src.data.preprocessing import DataPreprocessor
from src.data.feature_engineering import FeatureEngineer


class TestDataGeneration:
    """Test suite for data generation."""

    def test_data_generation(self):
        """Test that data is generated correctly."""
        generator = NigerianLoanDataGenerator(n_samples=100)
        df = generator.generate()

        assert len(df) == 100
        assert 'defaulted' in df.columns
        assert 'loan_amount' in df.columns
        assert 'monthly_income' in df.columns

    def test_default_rate(self):
        """Test that default rate is reasonable."""
        generator = NigerianLoanDataGenerator(n_samples=1000, default_rate=0.12)
        df = generator.generate()

        actual_default_rate = df['defaulted'].mean()
        assert 0.08 < actual_default_rate < 0.16  # Within reasonable range

    def test_nigerian_names(self):
        """Test that Nigerian names are generated."""
        generator = NigerianLoanDataGenerator(n_samples=10)
        df = generator.generate()

        assert all(df['full_name'].str.len() > 0)
        assert all(df['first_name'].str.len() > 0)
        assert all(df['last_name'].str.len() > 0)


class TestPreprocessing:
    """Test suite for data preprocessing."""

    def test_preprocessing_pipeline(self):
        """Test complete preprocessing pipeline."""
        # Generate data
        generator = NigerianLoanDataGenerator(n_samples=200)
        df = generator.generate()

        # Preprocess
        preprocessor = DataPreprocessor()
        processed = preprocessor.fit_transform(df, apply_smote=False)

        assert 'X_train' in processed
        assert 'y_train' in processed
        assert len(processed['X_train']) > 0

    def test_scaling(self):
        """Test that features are scaled."""
        generator = NigerianLoanDataGenerator(n_samples=100)
        df = generator.generate()

        preprocessor = DataPreprocessor()
        processed = preprocessor.fit_transform(df, apply_smote=False)

        # Check that scaled features have mean ~0 and std ~1
        mean = processed['X_train'].mean().mean()
        assert -0.5 < mean < 0.5


class TestFeatureEngineering:
    """Test suite for feature engineering."""

    def test_feature_engineering(self):
        """Test that features are engineered correctly."""
        generator = NigerianLoanDataGenerator(n_samples=100)
        df = generator.generate()

        engineer = FeatureEngineer()
        df_engineered = engineer.engineer_features(df)

        # Check new features exist
        assert 'debt_to_income_ratio' in df_engineered.columns
        assert 'is_prime_age' in df_engineered.columns
        assert 'total_red_flags' in df_engineered.columns

    def test_risk_indicators(self):
        """Test risk indicator creation."""
        generator = NigerianLoanDataGenerator(n_samples=100)
        df = generator.generate()

        engineer = FeatureEngineer()
        df_engineered = engineer.engineer_features(df)

        assert 'total_red_flags' in df_engineered.columns
        assert 'total_green_flags' in df_engineered.columns
        assert df_engineered['total_red_flags'].min() >= 0
        assert df_engineered['total_green_flags'].min() >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
