"""
BVN & NIBSS Integration
========================

Bank Verification Number (BVN) and NIBSS Credit Bureau integration.

Features:
- BVN verification
- NIBSS credit history retrieval
- Cross-bank default checking
- Watchlist verification
- Real-time identity validation

This is CRITICAL for Nigerian banks - BVN is mandatory.
"""

import requests
import hashlib
from typing import Dict, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


class BVNService:
    """
    BVN (Bank Verification Number) integration service.

    Integrates with NIBSS API for identity verification and credit history.
    """

    def __init__(self, api_key: str = None, sandbox: bool = True):
        """
        Args:
            api_key: NIBSS API key
            sandbox: Use sandbox environment
        """
        self.api_key = api_key or "sandbox_key_12345"
        self.base_url = "https://sandbox.nibss-plc.com.ng" if sandbox else "https://api.nibss-plc.com.ng"

    def verify_bvn(self, bvn: str) -> Dict:
        """
        Verify BVN and get customer details.

        Args:
            bvn: 11-digit Bank Verification Number

        Returns:
            Customer details from NIBSS
        """
        # Validate BVN format
        if not self._validate_bvn_format(bvn):
            return {'error': 'Invalid BVN format', 'valid': False}

        # In production, this would call actual NIBSS API
        # For now, simulating response
        mock_response = {
            'bvn': bvn,
            'first_name': 'ADEBAYO',
            'last_name': 'OGUNLEYE',
            'date_of_birth': '1988-05-15',
            'phone_number': '08031234567',
            'enrollment_bank': 'GTBank',
            'enrollment_branch': 'Victoria Island',
            'image': 'base64_encoded_photo',
            'watch_listed': False,
            'valid': True,
            'verification_timestamp': datetime.now().isoformat()
        }

        print(f"✓ BVN {bvn} verified successfully")
        return mock_response

    def get_credit_history(self, bvn: str) -> Dict:
        """
        Get credit history from NIBSS Credit Bureau.

        Args:
            bvn: Bank Verification Number

        Returns:
            Credit history across all Nigerian banks
        """
        # In production: POST to NIBSS Credit Bureau API
        mock_credit_history = {
            'bvn': bvn,
            'credit_score': 720,  # 300-850 scale
            'total_loans': 3,
            'active_loans': 1,
            'defaulted_loans': 0,
            'total_loan_amount': 5_000_000,
            'outstanding_balance': 1_200_000,
            'payment_history': 'Good',
            'last_default_date': None,
            'banks_with_facilities': ['GTBank', 'Access Bank'],
            'enquiries_last_6_months': 2,
            'oldest_account_date': '2018-03-10',
            'credit_utilization': 0.32,
            'watch_list_status': 'Clear'
        }

        print(f"✓ Retrieved credit history for BVN {bvn}")
        return mock_credit_history

    def check_watchlist(self, bvn: str) -> Dict:
        """
        Check if BVN is on any watchlist.

        Args:
            bvn: Bank Verification Number

        Returns:
            Watchlist status
        """
        mock_watchlist = {
            'bvn': bvn,
            'is_watchlisted': False,
            'watchlist_reason': None,
            'watchlist_date': None,
            'cleared_date': None,
            'status': 'CLEAR'
        }

        return mock_watchlist

    def validate_identity(
        self,
        bvn: str,
        first_name: str,
        last_name: str,
        date_of_birth: str
    ) -> Dict:
        """
        Validate customer identity against BVN records.

        Args:
            bvn: Bank Verification Number
            first_name: Customer's first name
            last_name: Customer's last name
            date_of_birth: Date of birth (YYYY-MM-DD)

        Returns:
            Validation result
        """
        bvn_data = self.verify_bvn(bvn)

        if not bvn_data.get('valid'):
            return {'valid': False, 'reason': 'BVN not found'}

        # Check name match
        name_match = (
            bvn_data['first_name'].upper() == first_name.upper() and
            bvn_data['last_name'].upper() == last_name.upper()
        )

        # Check DOB match
        dob_match = bvn_data['date_of_birth'] == date_of_birth

        return {
            'valid': name_match and dob_match,
            'name_match': name_match,
            'dob_match': dob_match,
            'match_score': (int(name_match) + int(dob_match)) / 2
        }

    def enrich_application(self, application: Dict) -> Dict:
        """
        Enrich loan application with BVN data.

        Args:
            application: Loan application dictionary

        Returns:
            Enriched application
        """
        bvn = application.get('bvn')
        if not bvn:
            return application

        # Get BVN data
        bvn_data = self.verify_bvn(bvn)
        credit_history = self.get_credit_history(bvn)
        watchlist = self.check_watchlist(bvn)

        # Enrich application
        enriched = application.copy()
        enriched.update({
            'bvn_verified': bvn_data.get('valid', False),
            'bvn_phone': bvn_data.get('phone_number'),
            'credit_score': credit_history.get('credit_score'),
            'existing_loans_count': credit_history.get('active_loans', 0),
            'total_outstanding': credit_history.get('outstanding_balance', 0),
            'has_defaults': credit_history.get('defaulted_loans', 0) > 0,
            'is_watchlisted': watchlist.get('is_watchlisted', False),
            'credit_bureau_payment_history': credit_history.get('payment_history')
        })

        return enriched

    def _validate_bvn_format(self, bvn: str) -> bool:
        """Validate BVN format (11 digits)."""
        return bvn.isdigit() and len(bvn) == 11


class NIBSSIntegration:
    """
    Full NIBSS (Nigerian Inter-Bank Settlement System) integration.
    """

    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: NIBSS API credentials
        """
        self.api_key = api_key
        self.bvn_service = BVNService(api_key)

    def instant_payment_notification(self, account: str) -> Dict:
        """
        Get instant payment notifications (salary credits, etc.).

        Args:
            account: Account number

        Returns:
            Recent credits/debits
        """
        # Mock IPN data
        return {
            'account_number': account,
            'recent_credits': [
                {'amount': 450_000, 'narration': 'SALARY - MARCH', 'date': '2024-03-01'},
                {'amount': 450_000, 'narration': 'SALARY - FEBRUARY', 'date': '2024-02-01'},
            ],
            'consistent_salary': True,
            'average_monthly_credit': 450_000
        }

    def verify_account(self, account_number: str, bank_code: str) -> Dict:
        """
        Verify account number and get account name.

        Args:
            account_number: 10-digit account number
            bank_code: CBN bank code

        Returns:
            Account details
        """
        return {
            'account_number': account_number,
            'account_name': 'ADEBAYO OGUNLEYE',
            'bank_code': bank_code,
            'bank_name': 'GTBank',
            'valid': True
        }


def main():
    """Demo BVN integration."""
    print("\n" + "="*70)
    print(" "*20 + "BVN & NIBSS INTEGRATION DEMO")
    print("="*70)

    # Initialize service
    bvn_service = BVNService(sandbox=True)

    # Verify BVN
    result = bvn_service.verify_bvn("22334455667")
    print(f"\n✓ BVN Verification: {result['first_name']} {result['last_name']}")

    # Get credit history
    credit = bvn_service.get_credit_history("22334455667")
    print(f"✓ Credit Score: {credit['credit_score']}")
    print(f"✓ Active Loans: {credit['active_loans']}")

    # Check watchlist
    watchlist = bvn_service.check_watchlist("22334455667")
    print(f"✓ Watchlist Status: {watchlist['status']}")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
