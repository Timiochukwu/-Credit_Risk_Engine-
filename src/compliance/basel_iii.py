"""
Basel III Capital Adequacy Calculator

Implements Basel III requirements for Nigerian banks
"""

from typing import Dict, List
from datetime import datetime


class BaselIIICalculator:
    """
    Basel III capital adequacy calculations

    Components:
    - Common Equity Tier 1 (CET1)
    - Additional Tier 1 (AT1)
    - Tier 2
    - Risk-weighted assets (RWA)
    - Leverage ratio
    - Liquidity ratios (LCR, NSFR)
    """

    def __init__(self):
        """Initialize Basel III calculator"""
        # Minimum requirements
        self.minimum_cet1_ratio = 0.045  # 4.5%
        self.minimum_tier1_ratio = 0.06  # 6%
        self.minimum_total_capital_ratio = 0.08  # 8%
        self.capital_conservation_buffer = 0.025  # 2.5%
        self.minimum_leverage_ratio = 0.03  # 3%

    def calculate_cet1_capital(self, bank_data: Dict) -> float:
        """
        Calculate Common Equity Tier 1 capital

        Args:
            bank_data: Bank financial data

        Returns:
            CET1 capital amount
        """
        # CET1 = Share capital + Retained earnings + Other comprehensive income
        # Less: Goodwill, Intangibles, Deferred tax assets

        cet1 = (
            bank_data.get('share_capital', 0) +
            bank_data.get('retained_earnings', 0) +
            bank_data.get('reserves', 0) -
            bank_data.get('goodwill', 0) -
            bank_data.get('intangibles', 0) -
            bank_data.get('deferred_tax_assets', 0)
        )

        return max(0, cet1)

    def calculate_tier1_capital(self, bank_data: Dict) -> float:
        """
        Calculate Total Tier 1 capital

        Args:
            bank_data: Bank financial data

        Returns:
            Tier 1 capital amount
        """
        # Tier 1 = CET1 + Additional Tier 1 (AT1)
        cet1 = self.calculate_cet1_capital(bank_data)
        at1 = bank_data.get('additional_tier1', 0)  # Perpetual bonds, etc.

        return cet1 + at1

    def calculate_total_capital(self, bank_data: Dict) -> float:
        """
        Calculate Total Capital

        Args:
            bank_data: Bank financial data

        Returns:
            Total capital amount
        """
        # Total Capital = Tier 1 + Tier 2
        tier1 = self.calculate_tier1_capital(bank_data)
        tier2 = bank_data.get('tier2_capital', 0)  # Subordinated debt, etc.

        return tier1 + tier2

    def calculate_risk_weighted_assets(self, assets: List[Dict]) -> Dict:
        """
        Calculate risk-weighted assets

        Args:
            assets: List of assets with amounts and risk weights

        Returns:
            RWA breakdown
        """
        total_rwa = 0
        breakdown = {}

        for asset in assets:
            asset_type = asset.get('type', 'other')
            amount = asset.get('amount', 0)
            risk_weight = asset.get('risk_weight', 1.0)

            rwa = amount * risk_weight
            total_rwa += rwa

            if asset_type not in breakdown:
                breakdown[asset_type] = {'amount': 0, 'rwa': 0}

            breakdown[asset_type]['amount'] += amount
            breakdown[asset_type]['rwa'] += rwa

        return {
            'total_rwa': total_rwa,
            'breakdown': breakdown
        }

    def calculate_capital_ratios(self, bank_data: Dict, assets: List[Dict]) -> Dict:
        """
        Calculate all Basel III capital ratios

        Args:
            bank_data: Bank financial data
            assets: Asset portfolio

        Returns:
            All capital ratios
        """
        # Calculate capitals
        cet1 = self.calculate_cet1_capital(bank_data)
        tier1 = self.calculate_tier1_capital(bank_data)
        total_capital = self.calculate_total_capital(bank_data)

        # Calculate RWA
        rwa_result = self.calculate_risk_weighted_assets(assets)
        total_rwa = rwa_result['total_rwa']

        # Calculate ratios
        cet1_ratio = cet1 / total_rwa if total_rwa > 0 else 0
        tier1_ratio = tier1 / total_rwa if total_rwa > 0 else 0
        total_capital_ratio = total_capital / total_rwa if total_rwa > 0 else 0

        # Check compliance
        cet1_compliant = cet1_ratio >= (self.minimum_cet1_ratio + self.capital_conservation_buffer)
        tier1_compliant = tier1_ratio >= self.minimum_tier1_ratio
        total_compliant = total_capital_ratio >= self.minimum_total_capital_ratio

        return {
            'capital': {
                'cet1': cet1,
                'tier1': tier1,
                'total': total_capital
            },
            'rwa': total_rwa,
            'ratios': {
                'cet1_ratio': f"{cet1_ratio * 100:.2f}%",
                'tier1_ratio': f"{tier1_ratio * 100:.2f}%",
                'total_capital_ratio': f"{total_capital_ratio * 100:.2f}%"
            },
            'requirements': {
                'minimum_cet1': f"{(self.minimum_cet1_ratio + self.capital_conservation_buffer) * 100:.2f}%",
                'minimum_tier1': f"{self.minimum_tier1_ratio * 100:.2f}%",
                'minimum_total': f"{self.minimum_total_capital_ratio * 100:.2f}%"
            },
            'compliance': {
                'cet1_compliant': cet1_compliant,
                'tier1_compliant': tier1_compliant,
                'total_compliant': total_compliant,
                'overall_compliant': cet1_compliant and tier1_compliant and total_compliant
            },
            'capital_surplus': {
                'cet1': cet1 - (total_rwa * (self.minimum_cet1_ratio + self.capital_conservation_buffer)),
                'tier1': tier1 - (total_rwa * self.minimum_tier1_ratio),
                'total': total_capital - (total_rwa * self.minimum_total_capital_ratio)
            }
        }

    def calculate_leverage_ratio(self, bank_data: Dict) -> Dict:
        """
        Calculate Basel III leverage ratio

        Args:
            bank_data: Bank financial data

        Returns:
            Leverage ratio
        """
        tier1 = self.calculate_tier1_capital(bank_data)
        total_exposure = bank_data.get('total_exposure', 0)

        leverage_ratio = tier1 / total_exposure if total_exposure > 0 else 0
        compliant = leverage_ratio >= self.minimum_leverage_ratio

        return {
            'tier1_capital': tier1,
            'total_exposure': total_exposure,
            'leverage_ratio': f"{leverage_ratio * 100:.2f}%",
            'minimum_required': f"{self.minimum_leverage_ratio * 100:.0f}%",
            'compliant': compliant,
            'message': f"Leverage ratio {'meets' if compliant else 'below'} Basel III minimum"
        }


# Example usage
if __name__ == "__main__":
    import json

    basel = BaselIIICalculator()

    # Sample bank data
    bank_data = {
        'share_capital': 50_000_000_000,
        'retained_earnings': 30_000_000_000,
        'reserves': 20_000_000_000,
        'goodwill': 5_000_000_000,
        'intangibles': 2_000_000_000,
        'deferred_tax_assets': 3_000_000_000,
        'additional_tier1': 10_000_000_000,
        'tier2_capital': 15_000_000_000,
        'total_exposure': 800_000_000_000
    }

    # Sample assets
    assets = [
        {'type': 'government_securities', 'amount': 100_000_000_000, 'risk_weight': 0.0},
        {'type': 'mortgage_loans', 'amount': 200_000_000_000, 'risk_weight': 0.5},
        {'type': 'corporate_loans', 'amount': 300_000_000_000, 'risk_weight': 1.0},
        {'type': 'retail_loans', 'amount': 150_000_000_000, 'risk_weight': 0.75},
        {'type': 'other_assets', 'amount': 50_000_000_000, 'risk_weight': 1.0}
    ]

    # Calculate ratios
    ratios = basel.calculate_capital_ratios(bank_data, assets)
    print("Basel III Capital Ratios:")
    print(json.dumps(ratios, indent=2, default=str))

    # Calculate leverage ratio
    leverage = basel.calculate_leverage_ratio(bank_data)
    print("\nLeverage Ratio:")
    print(json.dumps(leverage, indent=2))
