"""
Portfolio Risk Analytics
=========================

Bank-wide risk management and portfolio analysis.

Features:
- Concentration risk analysis
- Stress testing
- Expected loss calculations
- Capital adequacy (Basel III)
- Regulatory reporting for CBN
- Sector exposure analysis
- Geographic risk mapping

Nigerian Context:
- CBN regulatory requirements
- Oil sector concentration risks
- Regional economic variations
- Currency risk (Naira volatility)
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


class PortfolioRiskAnalyzer:
    """
    Comprehensive portfolio risk analysis for banks.
    """

    def __init__(self):
        """Initialize portfolio analyzer."""
        self.portfolio_data = None

    def analyze_portfolio(self, loans_df: pd.DataFrame) -> Dict:
        """
        Comprehensive portfolio analysis.

        Args:
            loans_df: DataFrame with all active loans

        Returns:
            Complete portfolio risk assessment
        """
        self.portfolio_data = loans_df

        analysis = {
            'summary': self._calculate_summary_stats(),
            'concentration_risk': self._analyze_concentration(),
            'expected_loss': self._calculate_expected_loss(),
            'stress_test': self._perform_stress_tests(),
            'capital_adequacy': self._assess_capital_adequacy(),
            'performance': self._analyze_performance(),
            'timestamp': datetime.now().isoformat()
        }

        return analysis

    def _calculate_summary_stats(self) -> Dict:
        """Calculate portfolio summary statistics."""
        df = self.portfolio_data

        return {
            'total_loans': len(df),
            'total_outstanding': float(df['loan_amount'].sum()),
            'average_loan_size': float(df['loan_amount'].mean()),
            'median_loan_size': float(df['loan_amount'].median()),
            'total_customers': df['customer_id'].nunique() if 'customer_id' in df.columns else len(df),
            'average_default_rate': float(df['defaulted'].mean()) if 'defaulted' in df.columns else 0.12,
            'total_interest_income': float(df['loan_amount'].sum() * 0.22 / 12)  # Simplified
        }

    def _analyze_concentration(self) -> Dict:
        """Analyze concentration risks."""
        df = self.portfolio_data

        concentration = {}

        # Sector concentration
        if 'employment_sector' in df.columns:
            sector_exposure = df.groupby('employment_sector')['loan_amount'].sum()
            total = sector_exposure.sum()

            concentration['sector'] = {
                'distribution': (sector_exposure / total * 100).to_dict(),
                'herfindahl_index': float((sector_exposure / total) ** 2).sum(),  # Concentration measure
                'top_sector': sector_exposure.idxmax(),
                'top_sector_percentage': float(sector_exposure.max() / total * 100),
                'risk_level': 'HIGH' if sector_exposure.max() / total > 0.25 else 'MEDIUM' if sector_exposure.max() / total > 0.15 else 'LOW'
            }

        # Geographic concentration
        if 'state' in df.columns:
            geo_exposure = df.groupby('state')['loan_amount'].sum()
            total = geo_exposure.sum()

            concentration['geographic'] = {
                'distribution': (geo_exposure / total * 100).to_dict(),
                'top_state': geo_exposure.idxmax(),
                'top_state_percentage': float(geo_exposure.max() / total * 100)
            }

        # Large exposures (single borrower limit)
        if 'customer_id' in df.columns:
            customer_exposure = df.groupby('customer_id')['loan_amount'].sum()
            large_exposures = customer_exposure[customer_exposure > total * 0.1]  # > 10% of portfolio

            concentration['large_exposures'] = {
                'count': len(large_exposures),
                'total_amount': float(large_exposures.sum()),
                'percentage': float(large_exposures.sum() / total * 100) if total > 0 else 0
            }

        return concentration

    def _calculate_expected_loss(self) -> Dict:
        """
        Calculate Expected Loss (EL) = PD × EAD × LGD

        Where:
        - PD = Probability of Default
        - EAD = Exposure at Default (loan amount)
        - LGD = Loss Given Default (1 - Recovery Rate)
        """
        df = self.portfolio_data

        # Assumptions
        avg_pd = 0.12  # 12% default rate for Nigeria
        avg_lgd = 0.80  # 80% loss given default (20% recovery)

        # If we have model predictions
        if 'default_probability' in df.columns:
            pd_values = df['default_probability']
        else:
            pd_values = avg_pd

        ead = df['loan_amount']  # Exposure at default
        lgd = avg_lgd  # Loss given default

        # Expected Loss per loan
        el_per_loan = pd_values * ead * lgd

        return {
            'total_expected_loss': float(el_per_loan.sum()),
            'expected_loss_rate': float(el_per_loan.sum() / ead.sum()) if ead.sum() > 0 else 0,
            'total_exposure': float(ead.sum()),
            'assumptions': {
                'probability_of_default': avg_pd,
                'loss_given_default': avg_lgd,
                'recovery_rate': 1 - avg_lgd
            }
        }

    def _perform_stress_tests(self) -> Dict:
        """
        Perform stress tests on portfolio.

        Scenarios:
        1. Oil price crash (affects Oil & Gas sector)
        2. Naira devaluation
        3. Economic recession
        4. Interest rate spike
        """
        df = self.portfolio_data
        base_default_rate = 0.12

        scenarios = {}

        # Scenario 1: Oil Price Crash (-50%)
        oil_sector_loans = df[df['employment_sector'] == 'Oil & Gas']['loan_amount'].sum() if 'employment_sector' in df.columns else 0
        oil_default_increase = 0.25  # Default rate increases to 37%

        scenarios['oil_price_crash'] = {
            'description': 'Oil price drops 50% (Brent < $40)',
            'affected_loans': float(oil_sector_loans),
            'affected_percentage': float(oil_sector_loans / df['loan_amount'].sum() * 100) if df['loan_amount'].sum() > 0 else 0,
            'default_rate_change': '+25%',
            'expected_additional_loss': float(oil_sector_loans * oil_default_increase * 0.80),
            'severity': 'HIGH' if oil_sector_loans / df['loan_amount'].sum() > 0.15 else 'MEDIUM'
        }

        # Scenario 2: Naira Devaluation (-30%)
        total_loans = df['loan_amount'].sum()
        forex_impact = 0.10  # 10% increase in defaults

        scenarios['naira_devaluation'] = {
            'description': 'Naira devalues 30% (USD/NGN > 1300)',
            'affected_loans': float(total_loans),
            'default_rate_change': '+10%',
            'expected_additional_loss': float(total_loans * forex_impact * 0.80),
            'severity': 'HIGH'
        }

        # Scenario 3: Economic Recession
        recession_impact = 0.15  # Default rate increases to 27%

        scenarios['economic_recession'] = {
            'description': 'GDP contraction of -5%',
            'affected_loans': float(total_loans),
            'default_rate_change': '+15%',
            'expected_additional_loss': float(total_loans * recession_impact * 0.80),
            'severity': 'CRITICAL'
        }

        # Combined scenario (worst case)
        combined_impact = 0.35  # 47% default rate

        scenarios['perfect_storm'] = {
            'description': 'Combined: Oil crash + Devaluation + Recession',
            'affected_loans': float(total_loans),
            'default_rate_change': '+35%',
            'expected_additional_loss': float(total_loans * combined_impact * 0.80),
            'severity': 'CATASTROPHIC'
        }

        return scenarios

    def _assess_capital_adequacy(self) -> Dict:
        """
        Assess capital adequacy per Basel III / CBN requirements.

        Nigerian banks must maintain CAR (Capital Adequacy Ratio) > 10%
        """
        df = self.portfolio_data

        # Simplified calculation
        total_risk_weighted_assets = df['loan_amount'].sum() * 1.0  # 100% risk weight for consumer loans
        tier_1_capital = total_risk_weighted_assets * 0.15  # Assume 15% Tier 1

        car = (tier_1_capital / total_risk_weighted_assets * 100) if total_risk_weighted_assets > 0 else 0

        return {
            'capital_adequacy_ratio': float(car),
            'tier_1_capital': float(tier_1_capital),
            'risk_weighted_assets': float(total_risk_weighted_assets),
            'minimum_required': 10.0,
            'cbn_compliant': car >= 10.0,
            'excess_capital': float(max(0, tier_1_capital - (total_risk_weighted_assets * 0.10)))
        }

    def _analyze_performance(self) -> Dict:
        """Analyze portfolio performance metrics."""
        df = self.portfolio_data

        performance = {}

        # Default rate by segment
        if 'employment_sector' in df.columns and 'defaulted' in df.columns:
            sector_defaults = df.groupby('employment_sector')['defaulted'].mean()
            performance['sector_default_rates'] = sector_defaults.to_dict()

        # Vintage analysis (if loan origination date available)
        if 'origination_date' in df.columns and 'defaulted' in df.columns:
            df['vintage'] = pd.to_datetime(df['origination_date']).dt.year
            vintage_defaults = df.groupby('vintage')['defaulted'].mean()
            performance['vintage_analysis'] = vintage_defaults.to_dict()

        # ROA (Return on Assets) - simplified
        total_outstanding = df['loan_amount'].sum()
        interest_income = total_outstanding * 0.22  # 22% average rate
        expected_losses = total_outstanding * 0.12 * 0.80
        net_income = interest_income - expected_losses

        performance['return_on_assets'] = float(net_income / total_outstanding * 100) if total_outstanding > 0 else 0

        return performance

    def generate_cbn_report(self, analysis: Dict) -> str:
        """
        Generate CBN regulatory report.

        Args:
            analysis: Portfolio analysis results

        Returns:
            Formatted CBN report
        """
        report = f"""
{'='*70}
  CENTRAL BANK OF NIGERIA (CBN)
  PORTFOLIO RISK REPORT
{'='*70}

REPORTING PERIOD: {datetime.now().strftime('%B %Y')}

PORTFOLIO SUMMARY
{'-'*70}
  Total Loans:              {analysis['summary']['total_loans']:,}
  Total Outstanding:        ₦{analysis['summary']['total_outstanding']:,.0f}
  Average Loan Size:        ₦{analysis['summary']['average_loan_size']:,.0f}
  Portfolio Default Rate:   {analysis['summary']['average_default_rate']:.2%}

CONCENTRATION RISK
{'-'*70}
  Top Sector:               {analysis['concentration_risk']['sector']['top_sector']}
  Top Sector Exposure:      {analysis['concentration_risk']['sector']['top_sector_percentage']:.1f}%
  Concentration Risk:       {analysis['concentration_risk']['sector']['risk_level']}
  Large Exposures (>10%):   {analysis['concentration_risk'].get('large_exposures', {}).get('count', 0)}

EXPECTED LOSS
{'-'*70}
  Total Expected Loss:      ₦{analysis['expected_loss']['total_expected_loss']:,.0f}
  Expected Loss Rate:       {analysis['expected_loss']['expected_loss_rate']:.2%}
  Total Exposure:           ₦{analysis['expected_loss']['total_exposure']:,.0f}

CAPITAL ADEQUACY (Basel III)
{'-'*70}
  Capital Adequacy Ratio:   {analysis['capital_adequacy']['capital_adequacy_ratio']:.2f}%
  Minimum Required (CBN):   {analysis['capital_adequacy']['minimum_required']:.2f}%
  CBN Compliant:            {'YES ✓' if analysis['capital_adequacy']['cbn_compliant'] else 'NO ✗'}
  Excess Capital:           ₦{analysis['capital_adequacy']['excess_capital']:,.0f}

STRESS TEST RESULTS
{'-'*70}
"""

        for scenario_name, scenario in analysis['stress_test'].items():
            report += f"\n  {scenario['description']}\n"
            report += f"    Severity:             {scenario['severity']}\n"
            report += f"    Additional Loss:      ₦{scenario['expected_additional_loss']:,.0f}\n"

        report += f"\n{'='*70}\n"
        report += "Report Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"
        report += f"{'='*70}\n"

        return report


def main():
    """Demo portfolio analytics."""
    print("\n" + "="*70)
    print(" "*20 + "PORTFOLIO RISK ANALYTICS DEMO")
    print("="*70)

    # Generate sample portfolio
    np.random.seed(42)
    n_loans = 1000

    portfolio_df = pd.DataFrame({
        'customer_id': [f'CUST{i:05d}' for i in range(n_loans)],
        'loan_amount': np.random.lognormal(14, 1, n_loans),  # Log-normal distribution
        'employment_sector': np.random.choice(
            ['Oil & Gas', 'Banking', 'Telecom', 'Manufacturing', 'Government'],
            n_loans,
            p=[0.25, 0.20, 0.15, 0.20, 0.20]
        ),
        'state': np.random.choice(['Lagos', 'Rivers', 'Kano', 'Abuja'], n_loans),
        'defaulted': np.random.binomial(1, 0.12, n_loans),
        'default_probability': np.random.beta(2, 8, n_loans)
    })

    # Analyze
    analyzer = PortfolioRiskAnalyzer()
    analysis = analyzer.analyze_portfolio(portfolio_df)

    # Generate CBN report
    report = analyzer.generate_cbn_report(analysis)
    print(report)

    print("✓ Portfolio Risk Analytics Implemented")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
