"""
Feature Engineering Module
===========================

This module creates additional features from raw data to improve model performance.

Feature Categories:
1. Financial Ratios (DTI, LTI, Credit Utilization)
2. Age-based Features (Life stage, working years left)
3. Credit History Features (Credit age, account maturity)
4. Interaction Features (Income × Employment, Education × Sector)
5. Risk Indicators (Red flags, protective factors)

Nigerian Context:
- Considers informal economy (many Nigerians have undocumented income)
- Accounts for extended family obligations (affects disposable income)
- Incorporates sector-specific risks (Oil & Gas volatility, etc.)
"""

import pandas as pd
import numpy as np
from typing import List
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import (
    DTI_THRESHOLD, CREDIT_UTILIZATION_THRESHOLD,
    PRIME_WORKING_AGE_START, PRIME_WORKING_AGE_END,
    MINIMUM_INCOME, MAXIMUM_AGE
)


class FeatureEngineer:
    """
    Creates engineered features for credit risk modeling.

    This class generates derived features that capture complex relationships
    and patterns in the data that raw features might miss.
    """

    def __init__(self):
        """Initialize feature engineer."""
        self.feature_names = []

    def create_financial_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create financial ratio features.

        These ratios are critical in credit risk assessment:
        - Debt-to-Income (DTI): How much of income goes to debt
        - Loan-to-Income (LTI): How large is the loan relative to annual income
        - Payment-to-Income: Monthly payment burden
        - Credit Utilization: How much credit is being used

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with new ratio features
        """
        df_new = df.copy()

        print("\n  Creating financial ratio features...")

        # 1. Debt-to-Income Ratio (already exists, but we'll ensure it's calculated)
        if 'debt_to_income_ratio' not in df_new.columns:
            df_new['debt_to_income_ratio'] = (
                (df_new['existing_monthly_debt'] + df_new['monthly_payment']) /
                df_new['monthly_income']
            )

        # 2. Loan-to-Annual-Income Ratio
        df_new['loan_to_annual_income'] = df_new['loan_amount'] / (df_new['monthly_income'] * 12)

        # 3. Payment-to-Income Ratio
        df_new['payment_to_income'] = df_new['monthly_payment'] / df_new['monthly_income']

        # 4. Existing Debt Ratio (before new loan)
        df_new['existing_debt_ratio'] = df_new['existing_monthly_debt'] / df_new['monthly_income']

        # 5. Savings Capacity (estimated monthly surplus after debts)
        df_new['monthly_surplus'] = df_new['monthly_income'] - df_new['existing_monthly_debt'] - df_new['monthly_payment']
        df_new['savings_capacity_ratio'] = df_new['monthly_surplus'] / df_new['monthly_income']

        # 6. Loan Burden (total loan amount as multiple of monthly income)
        df_new['loan_burden_months'] = df_new['loan_amount'] / df_new['monthly_payment']

        print(f"    ✓ Created 6 financial ratio features")

        return df_new

    def create_age_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create age-related features.

        Age is important in credit risk:
        - Young borrowers: Less stable, higher risk
        - Prime age (25-55): Most stable, lower risk
        - Near retirement: Fixed income concerns

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with age features
        """
        df_new = df.copy()

        print("\n  Creating age-related features...")

        # 1. Age group
        df_new['age_group'] = pd.cut(
            df_new['age'],
            bins=[0, 25, 35, 45, 55, 100],
            labels=['young', 'early_career', 'mid_career', 'senior', 'near_retirement']
        )

        # 2. Is prime working age (25-55)
        df_new['is_prime_age'] = (
            (df_new['age'] >= PRIME_WORKING_AGE_START) &
            (df_new['age'] <= PRIME_WORKING_AGE_END)
        ).astype(int)

        # 3. Years to retirement (assuming retirement at 60 in Nigeria)
        df_new['years_to_retirement'] = np.maximum(60 - df_new['age'], 0)

        # 4. Career stage score (0-1, peak at 40)
        # Younger and older borrowers get lower scores
        df_new['career_stage_score'] = 1 - np.abs(df_new['age'] - 40) / 40

        # 5. Can finish loan before retirement?
        df_new['loan_ends_before_retirement'] = (
            (df_new['age'] + df_new['loan_term_months'] / 12) < 60
        ).astype(int)

        print(f"    ✓ Created 5 age-related features")

        return df_new

    def create_employment_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create employment-related features.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with employment features
        """
        df_new = df.copy()

        print("\n  Creating employment features...")

        # 1. Employment stability score (based on years employed)
        df_new['employment_stability'] = np.clip(df_new['years_employed'] / 10, 0, 1)

        # 2. Is recently employed (< 2 years)
        df_new['is_recently_employed'] = (df_new['years_employed'] < 2).astype(int)

        # 3. Has long tenure (> 5 years)
        df_new['has_long_tenure'] = (df_new['years_employed'] > 5).astype(int)

        # 4. Employment to age ratio (started working early?)
        df_new['employment_age_ratio'] = df_new['years_employed'] / df_new['age']

        # 5. Sector risk score (some sectors are more volatile in Nigeria)
        # Oil & Gas: High paying but volatile
        # Government: Stable but lower paying
        # Technology: Growing but unstable
        sector_risk = {
            'Oil & Gas': 0.7,
            'Government': 0.2,
            'Banking & Finance': 0.3,
            'Technology': 0.6,
            'Telecommunications': 0.4,
            'Manufacturing': 0.5,
            'Agriculture': 0.6,
            'Healthcare': 0.3,
            'Education': 0.3,
            'Retail': 0.7,
            'Construction': 0.8,
            'Transportation': 0.7,
            'Real Estate': 0.6,
            'Hospitality': 0.8
        }
        df_new['sector_risk_score'] = df_new['employment_sector'].map(sector_risk).fillna(0.5)

        print(f"    ✓ Created 5 employment features")

        return df_new

    def create_credit_history_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create credit history features.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with credit features
        """
        df_new = df.copy()

        print("\n  Creating credit history features...")

        # 1. Credit maturity (how established is their credit history)
        df_new['credit_maturity_years'] = df_new['credit_history_months'] / 12

        # 2. Has established credit (> 2 years)
        df_new['has_established_credit'] = (df_new['credit_history_months'] >= 24).astype(int)

        # 3. Credit history to age ratio
        df_new['credit_to_age_ratio'] = df_new['credit_history_months'] / (df_new['age'] * 12)

        # 4. Average credit per line (if they have multiple credit lines)
        df_new['avg_credit_per_line'] = np.where(
            df_new['num_credit_lines'] > 0,
            df_new['existing_monthly_debt'] / df_new['num_credit_lines'],
            0
        )

        # 5. Credit line diversity score
        df_new['credit_diversity'] = np.clip(df_new['num_credit_lines'] / 5, 0, 1)

        # 6. Banking relationship strength
        df_new['banking_relationship_score'] = np.clip(df_new['account_age_years'] / 10, 0, 1)

        # 7. Has long banking relationship (> 5 years)
        df_new['has_long_bank_relationship'] = (df_new['account_age_years'] > 5).astype(int)

        print(f"    ✓ Created 7 credit history features")

        return df_new

    def create_loan_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create loan-specific features.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with loan features
        """
        df_new = df.copy()

        print("\n  Creating loan features...")

        # 1. Loan size category
        df_new['loan_size_category'] = pd.cut(
            df_new['loan_amount'],
            bins=[0, 500_000, 2_000_000, 10_000_000, float('inf')],
            labels=['micro', 'small', 'medium', 'large']
        )

        # 2. Is large loan (> ₦2M)
        df_new['is_large_loan'] = (df_new['loan_amount'] > 2_000_000).astype(int)

        # 3. Loan term category
        df_new['loan_term_category'] = pd.cut(
            df_new['loan_term_months'],
            bins=[0, 6, 12, 24, 60],
            labels=['very_short', 'short', 'medium', 'long']
        )

        # 4. Is long-term loan (> 24 months)
        df_new['is_long_term'] = (df_new['loan_term_months'] > 24).astype(int)

        # 5. Interest rate deviation from mean
        mean_rate = df_new['interest_rate'].mean()
        df_new['rate_deviation'] = df_new['interest_rate'] - mean_rate

        # 6. Is high interest rate (> 25%)
        df_new['is_high_interest'] = (df_new['interest_rate'] > 25).astype(int)

        # 7. Total interest paid over life of loan
        df_new['total_interest'] = (df_new['monthly_payment'] * df_new['loan_term_months']) - df_new['loan_amount']

        # 8. Interest as percentage of principal
        df_new['interest_to_principal'] = df_new['total_interest'] / df_new['loan_amount']

        print(f"    ✓ Created 8 loan features")

        return df_new

    def create_risk_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create risk indicator features (red flags and green flags).

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with risk indicators
        """
        df_new = df.copy()

        print("\n  Creating risk indicator features...")

        # RED FLAGS (increase default risk)
        red_flags = []

        # 1. High DTI (> 40%)
        df_new['red_flag_high_dti'] = (df_new['debt_to_income_ratio'] > DTI_THRESHOLD).astype(int)
        red_flags.append('red_flag_high_dti')

        # 2. Previous defaults
        df_new['red_flag_previous_default'] = df_new['previous_defaults']
        red_flags.append('red_flag_previous_default')

        # 3. Short credit history (< 1 year)
        df_new['red_flag_short_credit'] = (df_new['credit_history_months'] < 12).astype(int)
        red_flags.append('red_flag_short_credit')

        # 4. Low income (< ₦50k/month)
        df_new['red_flag_low_income'] = (df_new['monthly_income'] < 50_000).astype(int)
        red_flags.append('red_flag_low_income')

        # 5. Recently employed (< 1 year)
        df_new['red_flag_new_job'] = (df_new['years_employed'] < 1).astype(int)
        red_flags.append('red_flag_new_job')

        # 6. Very young (< 23)
        df_new['red_flag_very_young'] = (df_new['age'] < 23).astype(int)
        red_flags.append('red_flag_very_young')

        # Total red flags
        df_new['total_red_flags'] = df_new[red_flags].sum(axis=1)

        # GREEN FLAGS (decrease default risk)
        green_flags = []

        # 1. Low DTI (< 20%)
        df_new['green_flag_low_dti'] = (df_new['debt_to_income_ratio'] < 0.20).astype(int)
        green_flags.append('green_flag_low_dti')

        # 2. High income (> ₦500k/month)
        df_new['green_flag_high_income'] = (df_new['monthly_income'] > 500_000).astype(int)
        green_flags.append('green_flag_high_income')

        # 3. Long employment (> 5 years)
        df_new['green_flag_stable_employment'] = (df_new['years_employed'] > 5).astype(int)
        green_flags.append('green_flag_stable_employment')

        # 4. Established credit (> 3 years)
        df_new['green_flag_established_credit'] = (df_new['credit_history_months'] > 36).astype(int)
        green_flags.append('green_flag_established_credit')

        # 5. Prime age (25-55)
        df_new['green_flag_prime_age'] = df_new['is_prime_age']
        green_flags.append('green_flag_prime_age')

        # 6. Long bank relationship (> 5 years)
        df_new['green_flag_loyal_customer'] = df_new['has_long_bank_relationship']
        green_flags.append('green_flag_loyal_customer')

        # Total green flags
        df_new['total_green_flags'] = df_new[green_flags].sum(axis=1)

        # Net risk score (green flags - red flags)
        df_new['net_risk_score'] = df_new['total_green_flags'] - df_new['total_red_flags']

        print(f"    ✓ Created {len(red_flags)} red flags")
        print(f"    ✓ Created {len(green_flags)} green flags")
        print(f"    ✓ Created risk indicators")

        return df_new

    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features (combinations of existing features).

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with interaction features
        """
        df_new = df.copy()

        print("\n  Creating interaction features...")

        # 1. Income × Employment stability
        df_new['income_stability_score'] = df_new['monthly_income'] * df_new['employment_stability'] / 100000

        # 2. Age × Credit history (maturity score)
        df_new['maturity_score'] = (df_new['age'] / 65) * (df_new['credit_history_months'] / 120)

        # 3. Loan amount × DTI (total risk exposure)
        df_new['risk_exposure'] = df_new['loan_amount'] * df_new['debt_to_income_ratio'] / 1_000_000

        # 4. Income × Education (earning potential)
        # First, create education numeric if not already
        if df_new['education'].dtype == 'object':
            education_map = {'SSCE': 1, 'OND': 2, 'HND': 3, 'B.Sc': 4, 'M.Sc': 5, 'PhD': 6}
            df_new['education_numeric'] = df_new['education'].map(education_map)
        else:
            df_new['education_numeric'] = df_new['education']

        df_new['earning_potential'] = (df_new['monthly_income'] / 100000) * df_new['education_numeric']

        print(f"    ✓ Created 4 interaction features")

        return df_new

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering steps.

        Args:
            df: Raw DataFrame

        Returns:
            DataFrame with engineered features
        """
        print("\n" + "="*60)
        print("FEATURE ENGINEERING")
        print("="*60)

        original_features = len(df.columns)

        # Apply all feature engineering functions
        df_engineered = df.copy()
        df_engineered = self.create_financial_ratios(df_engineered)
        df_engineered = self.create_age_features(df_engineered)
        df_engineered = self.create_employment_features(df_engineered)
        df_engineered = self.create_credit_history_features(df_engineered)
        df_engineered = self.create_loan_features(df_engineered)
        df_engineered = self.create_risk_indicators(df_engineered)
        df_engineered = self.create_interaction_features(df_engineered)

        new_features = len(df_engineered.columns)

        print("\n" + "="*60)
        print("FEATURE ENGINEERING COMPLETE")
        print("="*60)
        print(f"  Original features: {original_features}")
        print(f"  New features: {new_features}")
        print(f"  Features added: {new_features - original_features}")
        print("="*60 + "\n")

        return df_engineered


def main():
    """Main function to demonstrate feature engineering."""
    from src.data.generate_data import NigerianLoanDataGenerator

    # Generate sample data
    print("Generating sample data...")
    generator = NigerianLoanDataGenerator(n_samples=1000)
    df = generator.generate()

    # Engineer features
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_features(df)

    print(f"\n✓ Feature engineering demonstration complete!")
    print(f"✓ Final dataset shape: {df_engineered.shape}")
    print(f"\nSample of new features:")
    new_cols = [
        'debt_to_income_ratio', 'loan_to_annual_income',
        'is_prime_age', 'employment_stability',
        'has_established_credit', 'total_red_flags',
        'total_green_flags', 'net_risk_score'
    ]
    print(df_engineered[new_cols].head())


if __name__ == "__main__":
    main()
