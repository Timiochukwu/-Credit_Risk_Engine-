"""
Alternative Data Integration
=============================

Nigerian-specific alternative data sources for credit scoring.

Data Sources:
- Mobile money transactions (Paga, OPay, Flutterwave)
- Airtime purchase patterns
- Utility bill payments (PHCN, water)
- Social media footprint
- Market trader associations
- Informal savings groups (Ajo, Esusu)

Nigerian Context:
- Many Nigerians are "credit invisible" (no formal credit history)
- Alternative data enables financial inclusion
- Mobile money is prevalent (Paga, OPay, Palmpay)
"""

import requests
from typing import Dict
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


class AlternativeDataEngine:
    """
    Integrate alternative data sources for enhanced credit scoring.
    """

    def __init__(self, api_keys: Dict = None):
        """
        Args:
            api_keys: API keys for various data providers
        """
        self.api_keys = api_keys or {}

    def get_mobile_money_score(self, phone_number: str) -> Dict:
        """
        Get mobile money transaction score.

        Integrations: Paga, OPay, Flutterwave, Paystack

        Args:
            phone_number: Customer's phone number

        Returns:
            Mobile money score and insights
        """
        # In production: Call Paystack, Flutterwave APIs
        # For now, mock data

        mock_data = {
            'phone_number': phone_number,
            'provider': 'OPay',
            'account_age_days': 456,
            'transaction_count_6months': 127,
            'total_inflow_6months': 2_340_000,
            'total_outflow_6months': 2_100_000,
            'average_monthly_inflow': 390_000,
            'consistent_income': True,
            'bounced_transactions': 0,
            'airtime_purchases_6months': 42,
            'average_airtime_purchase': 2_500,
            'utility_payments': [
                {'type': 'Electricity', 'amount': 15_000, 'date': '2024-03-01'},
                {'type': 'Electricity', 'amount': 15_000, 'date': '2024-02-01'},
                {'type': 'Water', 'amount': 3_000, 'date': '2024-03-05'},
            ],
            'payment_reliability': 0.92,  # 92% on-time payments
            'mobile_money_score': 78,  # 0-100 scale
            'risk_level': 'LOW'
        }

        return mock_data

    def get_utility_payment_history(self, customer_id: str) -> Dict:
        """
        Get utility payment history (PHCN electricity, water).

        Args:
            customer_id: Customer identifier

        Returns:
            Utility payment history
        """
        mock_data = {
            'customer_id': customer_id,
            'electricity_provider': 'IKEDC',  # Ikeja Electric
            'payments_12months': [
                {'month': '2024-03', 'amount': 15_000, 'paid_on_time': True},
                {'month': '2024-02', 'amount': 15_000, 'paid_on_time': True},
                {'month': '2024-01', 'amount': 15_000, 'paid_on_time': False},
                # ... more months
            ],
            'total_paid_12months': 180_000,
            'on_time_payment_rate': 0.85,
            'has_arrears': False,
            'utility_score': 75
        }

        return mock_data

    def get_informal_savings_data(self, phone: str) -> Dict:
        """
        Get informal savings group (Ajo/Esusu) participation data.

        Many Nigerians participate in rotating savings groups.

        Args:
            phone: Phone number

        Returns:
            Informal savings history
        """
        mock_data = {
            'participates_in_ajo': True,
            'ajo_group_name': 'Victoria Island Traders Association',
            'monthly_contribution': 20_000,
            'contribution_history_months': 18,
            'missed_contributions': 0,
            'received_payouts': 2,
            'total_contributed': 360_000,
            'trustworthiness_score': 95,  # Very high
            'social_collateral': 'Strong'
        }

        return mock_data

    def get_social_media_score(self, email: str = None, phone: str = None) -> Dict:
        """
        Social media footprint analysis (LinkedIn, Twitter).

        Args:
            email: Email address
            phone: Phone number

        Returns:
            Social media insights
        """
        mock_data = {
            'linkedin_profile': True,
            'linkedin_connections': 523,
            'employment_verified': True,
            'professional_recommendations': 12,
            'twitter_account_age_months': 84,
            'twitter_followers': 1250,
            'social_score': 65,
            'fraud_risk': 'LOW'
        }

        return mock_data

    def enrich_with_alternative_data(self, application: Dict) -> Dict:
        """
        Enrich loan application with all alternative data.

        Args:
            application: Base loan application

        Returns:
            Enriched application
        """
        enriched = application.copy()

        # Get mobile money data
        if 'phone' in application:
            mobile_data = self.get_mobile_money_score(application['phone'])
            enriched.update({
                'mobile_money_score': mobile_data['mobile_money_score'],
                'transaction_count_6m': mobile_data['transaction_count_6months'],
                'average_monthly_inflow': mobile_data['average_monthly_inflow'],
                'payment_reliability': mobile_data['payment_reliability']
            })

        # Get utility data
        utility_data = self.get_utility_payment_history(application.get('customer_id', 'N/A'))
        enriched.update({
            'utility_score': utility_data['utility_score'],
            'utility_on_time_rate': utility_data['on_time_payment_rate']
        })

        # Get informal savings
        ajo_data = self.get_informal_savings_data(application.get('phone', ''))
        enriched.update({
            'participates_in_ajo': ajo_data['participates_in_ajo'],
            'ajo_contribution_months': ajo_data['contribution_history_months'],
            'social_collateral_score': ajo_data['trustworthiness_score']
        })

        # Get social media
        social_data = self.get_social_media_score(
            email=application.get('email'),
            phone=application.get('phone')
        )
        enriched.update({
            'social_media_score': social_data['social_score'],
            'employment_verified_social': social_data['employment_verified']
        })

        # Calculate composite alternative data score
        enriched['alternative_data_score'] = (
            mobile_data['mobile_money_score'] * 0.4 +
            utility_data['utility_score'] * 0.2 +
            ajo_data['trustworthiness_score'] * 0.3 +
            social_data['social_score'] * 0.1
        )

        return enriched


def main():
    """Demo alternative data integration."""
    print("\n" + "="*70)
    print(" "*15 + "ALTERNATIVE DATA INTEGRATION DEMO")
    print("="*70)

    engine = AlternativeDataEngine()

    # Test application
    app = {
        'customer_id': 'CUST12345',
        'phone': '08031234567',
        'email': 'test@example.com'
    }

    # Enrich
    enriched = engine.enrich_with_alternative_data(app)

    print(f"\n✓ Alternative Data Score: {enriched['alternative_data_score']:.1f}/100")
    print(f"  • Mobile Money Score: {enriched['mobile_money_score']}")
    print(f"  • Utility Score: {enriched['utility_score']}")
    print(f"  • Ajo Participation: {enriched['participates_in_ajo']}")
    print(f"  • Social Media Score: {enriched['social_media_score']}")

    print("\n✓ Alternative Data Integration Implemented")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
