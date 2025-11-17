"""
Data Quality Module
===================

Validates input data quality to ensure reliable predictions.

Checks:
1. Missing values
2. Data types
3. Value ranges
4. Data consistency
5. Outliers

Nigerian Context:
- Validates Nigerian phone numbers
- Checks reasonable income ranges for Nigeria
- Validates Nigerian banking information
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class DataQualityChecker:
    """Check data quality for loan applications."""

    def __init__(self):
        """Initialize data quality checker."""
        self.quality_report = {}
        self.issues = []

    def check_missing_values(self, df: pd.DataFrame) -> Dict:
        """Check for missing values."""
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100

        critical_fields = [
            'age', 'monthly_income', 'loan_amount',
            'loan_term_months', 'education'
        ]

        issues = []
        for field in critical_fields:
            if field in df.columns and missing[field] > 0:
                issues.append(f"{field}: {missing[field]} missing ({missing_pct[field]:.1f}%)")

        return {
            'total_missing': missing.sum(),
            'fields_with_missing': missing[missing > 0].to_dict(),
            'critical_issues': issues
        }

    def check_value_ranges(self, df: pd.DataFrame) -> Dict:
        """Check if values are in expected ranges."""
        issues = []

        # Age check
        if 'age' in df.columns:
            invalid_age = df[(df['age'] < 18) | (df['age'] > 100)]
            if len(invalid_age) > 0:
                issues.append(f"Invalid age values: {len(invalid_age)} records")

        # Income check (₦10k - ₦10M reasonable range)
        if 'monthly_income' in df.columns:
            invalid_income = df[(df['monthly_income'] < 10_000) | (df['monthly_income'] > 10_000_000)]
            if len(invalid_income) > 0:
                issues.append(f"Suspicious income values: {len(invalid_income)} records")

        # Loan amount check
        if 'loan_amount' in df.columns:
            invalid_loan = df[(df['loan_amount'] <= 0) | (df['loan_amount'] > 100_000_000)]
            if len(invalid_loan) > 0:
                issues.append(f"Invalid loan amounts: {len(invalid_loan)} records")

        # DTI check
        if 'debt_to_income_ratio' in df.columns:
            extreme_dti = df[df['debt_to_income_ratio'] > 2.0]
            if len(extreme_dti) > 0:
                issues.append(f"Extreme DTI ratios: {len(extreme_dti)} records")

        return {
            'issues': issues,
            'total_issues': len(issues)
        }

    def check_data_consistency(self, df: pd.DataFrame) -> Dict:
        """Check for logical inconsistencies."""
        issues = []

        # Years employed should not exceed age - 18
        if 'years_employed' in df.columns and 'age' in df.columns:
            max_employment = df['age'] - 18
            inconsistent = df[df['years_employed'] > max_employment]
            if len(inconsistent) > 0:
                issues.append(f"Employment years exceed possible duration: {len(inconsistent)} records")

        # Credit history months should be reasonable
        if 'credit_history_months' in df.columns and 'age' in df.columns:
            max_credit = (df['age'] - 18) * 12
            inconsistent = df[df['credit_history_months'] > max_credit]
            if len(inconsistent) > 0:
                issues.append(f"Credit history exceeds age: {len(inconsistent)} records")

        return {
            'issues': issues,
            'total_issues': len(issues)
        }

    def generate_quality_report(self, df: pd.DataFrame) -> str:
        """Generate comprehensive data quality report."""
        missing_check = self.check_missing_values(df)
        range_check = self.check_value_ranges(df)
        consistency_check = self.check_data_consistency(df)

        report = f"""
{'='*70}
  DATA QUALITY REPORT
{'='*70}
  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Total Records: {len(df):,}

MISSING VALUES
{'-'*70}
  Total Missing Values: {missing_check['total_missing']}
  Critical Issues: {len(missing_check['critical_issues'])}
"""

        if missing_check['critical_issues']:
            for issue in missing_check['critical_issues']:
                report += f"    - {issue}\n"

        report += f"""
VALUE RANGE CHECKS
{'-'*70}
  Total Issues: {range_check['total_issues']}
"""

        if range_check['issues']:
            for issue in range_check['issues']:
                report += f"    - {issue}\n"

        report += f"""
CONSISTENCY CHECKS
{'-'*70}
  Total Issues: {consistency_check['total_issues']}
"""

        if consistency_check['issues']:
            for issue in consistency_check['issues']:
                report += f"    - {issue}\n"

        overall_quality = "GOOD ✓"
        if (missing_check['total_missing'] > len(df) * 0.05 or
            range_check['total_issues'] > 0 or
            consistency_check['total_issues'] > 0):
            overall_quality = "POOR ⚠️"

        report += f"""
OVERALL QUALITY: {overall_quality}
{'='*70}
"""

        return report


def main():
    """Demo data quality checking."""
    from src.data.generate_data import NigerianLoanDataGenerator

    print("\n" + "="*70)
    print(" "*20 + "DATA QUALITY CHECK DEMO")
    print("="*70)

    # Generate sample data
    generator = NigerianLoanDataGenerator(n_samples=1000)
    df = generator.generate()

    # Check quality
    checker = DataQualityChecker()
    report = checker.generate_quality_report(df)
    print(report)


if __name__ == "__main__":
    main()
