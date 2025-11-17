"""
KYC (Know Your Customer) / AML (Anti-Money Laundering) Validator

Implements CBN and international AML/CFT standards
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import re


class RiskRating(Enum):
    """Customer risk rating"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    PROHIBITED = "PROHIBITED"


class CustomerType(Enum):
    """Customer types"""
    INDIVIDUAL = "INDIVIDUAL"
    CORPORATE = "CORPORATE"
    PEP = "POLITICALLY_EXPOSED_PERSON"
    NGO = "NGO"
    HIGH_NET_WORTH = "HIGH_NET_WORTH"


class KYCAMLValidator:
    """
    KYC/AML Compliance Validator

    Features:
    - Customer due diligence (CDD)
    - Enhanced due diligence (EDD)
    - PEP screening
    - Sanctions list checking
    - Transaction monitoring
    - Suspicious activity detection
    """

    def __init__(self):
        """Initialize KYC/AML validator"""
        # Prohibited countries (FATF blacklist example)
        self.prohibited_countries = [
            'North Korea', 'Iran', 'Myanmar'
        ]

        # High-risk countries (FATF greylist example)
        self.high_risk_countries = [
            'Yemen', 'Syria', 'Pakistan', 'Uganda', 'South Sudan'
        ]

        # High-risk sectors
        self.high_risk_sectors = [
            'Money Transfer', 'Casino', 'Cryptocurrency', 'Precious Metals',
            'Real Estate', 'Art Dealing', 'Jewelry'
        ]

        # Transaction thresholds (CBN)
        self.reporting_threshold = 5_000_000  # ₦5M
        self.daily_transaction_limit = 10_000_000  # ₦10M

    def validate_bvn(self, bvn: str) -> Dict:
        """
        Validate BVN format

        Args:
            bvn: Bank Verification Number

        Returns:
            Validation result
        """
        if not bvn:
            return {
                'valid': False,
                'message': 'BVN is required'
            }

        # BVN is 11 digits
        if not re.match(r'^\d{11}$', str(bvn)):
            return {
                'valid': False,
                'message': 'BVN must be 11 digits'
            }

        return {
            'valid': True,
            'message': 'BVN format valid'
        }

    def validate_identity_documents(self, documents: Dict) -> Dict:
        """
        Validate identity documents

        Args:
            documents: Customer documents

        Returns:
            Validation result
        """
        required_docs = ['bvn', 'id_type', 'id_number']
        acceptable_ids = [
            'National ID', 'International Passport',
            'Drivers License', 'Voters Card'
        ]

        missing = [doc for doc in required_docs if doc not in documents]

        if missing:
            return {
                'valid': False,
                'missing_documents': missing,
                'message': f'Missing required documents: {", ".join(missing)}'
            }

        # Validate ID type
        id_type = documents.get('id_type')
        if id_type not in acceptable_ids:
            return {
                'valid': False,
                'message': f'ID type must be one of: {", ".join(acceptable_ids)}'
            }

        # Validate BVN
        bvn_check = self.validate_bvn(documents.get('bvn'))
        if not bvn_check['valid']:
            return bvn_check

        return {
            'valid': True,
            'message': 'All identity documents validated',
            'id_type': id_type
        }

    def assess_customer_risk(self, customer_data: Dict) -> Dict:
        """
        Assess customer risk rating

        Args:
            customer_data: Customer information

        Returns:
            Risk assessment
        """
        risk_score = 0
        risk_factors = []

        # 1. Customer type
        customer_type = customer_data.get('customer_type', 'INDIVIDUAL')
        if customer_type == 'PEP':
            risk_score += 30
            risk_factors.append('Politically Exposed Person')
        elif customer_type == 'HIGH_NET_WORTH':
            risk_score += 10
            risk_factors.append('High Net Worth Individual')

        # 2. Country risk
        country = customer_data.get('country', 'Nigeria')
        if country in self.prohibited_countries:
            risk_score += 100  # Automatic prohibition
            risk_factors.append(f'Prohibited country: {country}')
        elif country in self.high_risk_countries:
            risk_score += 25
            risk_factors.append(f'High-risk country: {country}')

        # 3. Sector risk
        sector = customer_data.get('employment_sector')
        if sector in self.high_risk_sectors:
            risk_score += 20
            risk_factors.append(f'High-risk sector: {sector}')

        # 4. Transaction history
        avg_monthly_transaction = customer_data.get('avg_monthly_transaction', 0)
        if avg_monthly_transaction > 50_000_000:  # ₦50M+/month
            risk_score += 15
            risk_factors.append('High transaction volume')

        # 5. Source of funds
        source_of_funds = customer_data.get('source_of_funds')
        suspicious_sources = ['Cash', 'Undisclosed', 'Inheritance', 'Gift']
        if source_of_funds in suspicious_sources:
            risk_score += 15
            risk_factors.append(f'Suspicious source of funds: {source_of_funds}')

        # 6. Age of relationship
        relationship_months = customer_data.get('relationship_months', 0)
        if relationship_months < 6:
            risk_score += 10
            risk_factors.append('New customer (<6 months)')

        # Determine risk rating
        if risk_score >= 80:
            risk_rating = RiskRating.PROHIBITED
            action = 'REJECT'
        elif risk_score >= 50:
            risk_rating = RiskRating.HIGH
            action = 'ENHANCED_DUE_DILIGENCE'
        elif risk_score >= 25:
            risk_rating = RiskRating.MEDIUM
            action = 'STANDARD_DUE_DILIGENCE'
        else:
            risk_rating = RiskRating.LOW
            action = 'SIMPLIFIED_DUE_DILIGENCE'

        return {
            'customer_id': customer_data.get('customer_id'),
            'risk_score': risk_score,
            'risk_rating': risk_rating.value,
            'risk_factors': risk_factors,
            'action_required': action,
            'requires_approval': risk_score >= 50,
            'monitoring_frequency': 'Daily' if risk_score >= 50 else 'Monthly' if risk_score >= 25 else 'Quarterly'
        }

    def screen_pep(self, customer_data: Dict) -> Dict:
        """
        Screen for Politically Exposed Persons

        Args:
            customer_data: Customer information

        Returns:
            PEP screening result
        """
        # In production, this would call an external PEP database
        # For now, we'll use keywords

        name = customer_data.get('name', '').lower()
        occupation = customer_data.get('occupation', '').lower()

        pep_keywords = [
            'minister', 'senator', 'governor', 'commissioner',
            'chairman', 'director-general', 'ambassador',
            'military', 'general', 'admiral', 'judge'
        ]

        is_pep = any(keyword in occupation for keyword in pep_keywords)

        # Check for family members of PEPs
        is_family_of_pep = customer_data.get('family_member_pep', False)

        return {
            'is_pep': is_pep,
            'is_family_of_pep': is_family_of_pep,
            'pep_category': occupation if is_pep else None,
            'requires_edd': is_pep or is_family_of_pep,
            'approval_level': 'BOARD' if is_pep else 'MANAGEMENT' if is_family_of_pep else 'BRANCH',
            'message': 'PEP detected - Enhanced Due Diligence required' if is_pep else 'Not a PEP'
        }

    def check_sanctions_list(self, customer_data: Dict) -> Dict:
        """
        Check against sanctions lists

        Args:
            customer_data: Customer information

        Returns:
            Sanctions check result
        """
        # In production, check against:
        # - UN Sanctions List
        # - OFAC (US Treasury)
        # - EU Sanctions List
        # - UK HM Treasury List
        # - Local Nigerian watchlists

        name = customer_data.get('name', '').lower()

        # Mock sanctions list
        sanctioned_entities = [
            'terrorist', 'fraud', 'money launderer'
        ]

        is_sanctioned = any(entity in name for entity in sanctioned_entities)

        return {
            'is_sanctioned': is_sanctioned,
            'lists_checked': ['UN', 'OFAC', 'EU', 'UK_HMT', 'CBN_Watchlist'],
            'action': 'BLOCK' if is_sanctioned else 'PROCEED',
            'message': 'Customer on sanctions list - TRANSACTION BLOCKED' if is_sanctioned else 'No sanctions match found'
        }

    def monitor_transaction(self, transaction: Dict, customer_history: List[Dict]) -> Dict:
        """
        Monitor transaction for suspicious activity

        Args:
            transaction: Current transaction
            customer_history: Customer's transaction history

        Returns:
            Monitoring result
        """
        alerts = []
        suspicion_score = 0

        amount = transaction.get('amount', 0)

        # 1. Check reporting threshold
        if amount >= self.reporting_threshold:
            alerts.append({
                'type': 'LARGE_TRANSACTION',
                'message': f'Transaction ₦{amount:,.0f} exceeds reporting threshold',
                'action': 'FILE_CTR'  # Currency Transaction Report
            })
            suspicion_score += 10

        # 2. Check for structuring (multiple transactions just below threshold)
        today_transactions = [
            t for t in customer_history
            if t.get('date') == transaction.get('date')
        ]
        total_today = sum(t.get('amount', 0) for t in today_transactions)

        if len(today_transactions) >= 3 and total_today >= self.reporting_threshold:
            alerts.append({
                'type': 'STRUCTURING',
                'message': f'{len(today_transactions)} transactions totaling ₦{total_today:,.0f}',
                'action': 'FILE_SAR'  # Suspicious Activity Report
            })
            suspicion_score += 30

        # 3. Check velocity (frequency of transactions)
        recent_count = len([
            t for t in customer_history[-10:]
            if t.get('amount', 0) > 1_000_000
        ])

        if recent_count >= 5:
            alerts.append({
                'type': 'HIGH_VELOCITY',
                'message': f'{recent_count} large transactions in recent period',
                'action': 'REVIEW'
            })
            suspicion_score += 15

        # 4. Check for round amounts (money laundering indicator)
        if amount % 1_000_000 == 0 and amount >= 5_000_000:
            alerts.append({
                'type': 'ROUND_AMOUNT',
                'message': 'Large round amount may indicate suspicious activity',
                'action': 'REVIEW'
            })
            suspicion_score += 10

        # 5. Check for unusual pattern
        if customer_history:
            avg_transaction = sum(t.get('amount', 0) for t in customer_history) / len(customer_history)

            if amount > avg_transaction * 10:  # 10x normal
                alerts.append({
                    'type': 'UNUSUAL_AMOUNT',
                    'message': f'Amount {amount/avg_transaction:.1f}x customer average',
                    'action': 'REVIEW'
                })
                suspicion_score += 20

        # Determine action
        if suspicion_score >= 50:
            action = 'BLOCK_AND_FILE_SAR'
        elif suspicion_score >= 30:
            action = 'HOLD_FOR_REVIEW'
        elif suspicion_score >= 15:
            action = 'FLAG_AND_MONITOR'
        else:
            action = 'APPROVE'

        return {
            'transaction_id': transaction.get('transaction_id'),
            'amount': amount,
            'suspicion_score': suspicion_score,
            'alerts': alerts,
            'action': action,
            'requires_sar': suspicion_score >= 30,
            'requires_ctr': amount >= self.reporting_threshold
        }

    def perform_kyc_check(self, customer_data: Dict) -> Dict:
        """
        Complete KYC/AML check

        Args:
            customer_data: Complete customer data

        Returns:
            Comprehensive KYC result
        """
        # 1. Identity validation
        identity_check = self.validate_identity_documents(customer_data.get('documents', {}))

        # 2. Risk assessment
        risk_assessment = self.assess_customer_risk(customer_data)

        # 3. PEP screening
        pep_check = self.screen_pep(customer_data)

        # 4. Sanctions check
        sanctions_check = self.check_sanctions_list(customer_data)

        # Overall decision
        all_checks_passed = (
            identity_check.get('valid', False) and
            not sanctions_check.get('is_sanctioned', False) and
            risk_assessment.get('risk_rating') != RiskRating.PROHIBITED.value
        )

        return {
            'customer_id': customer_data.get('customer_id'),
            'kyc_status': 'APPROVED' if all_checks_passed else 'REJECTED',
            'timestamp': datetime.now().isoformat(),
            'checks': {
                'identity': identity_check,
                'risk_assessment': risk_assessment,
                'pep_screening': pep_check,
                'sanctions': sanctions_check
            },
            'overall_compliant': all_checks_passed,
            'next_review_date': (datetime.now() + timedelta(days=365)).isoformat(),
            'enhanced_due_diligence_required': pep_check.get('requires_edd', False) or
                                               risk_assessment.get('risk_rating') == RiskRating.HIGH.value
        }


# Example usage
if __name__ == "__main__":
    import json

    validator = KYCAMLValidator()

    # Test customer
    customer = {
        'customer_id': 'CUST001',
        'name': 'Adebayo Ogunleye',
        'country': 'Nigeria',
        'customer_type': 'INDIVIDUAL',
        'occupation': 'Software Engineer',
        'employment_sector': 'Technology',
        'avg_monthly_transaction': 2_000_000,
        'source_of_funds': 'Salary',
        'relationship_months': 24,
        'documents': {
            'bvn': '12345678901',
            'id_type': 'National ID',
            'id_number': 'NG12345678'
        }
    }

    # Perform KYC
    result = validator.perform_kyc_check(customer)
    print("KYC/AML Check Result:")
    print(json.dumps(result, indent=2, default=str))

    # Test transaction monitoring
    print("\n=== Transaction Monitoring ===")
    transaction = {
        'transaction_id': 'TXN001',
        'amount': 6_000_000,
        'date': datetime.now().strftime('%Y-%m-%d')
    }

    history = [
        {'amount': 500_000, 'date': datetime.now().strftime('%Y-%m-%d')},
        {'amount': 750_000, 'date': datetime.now().strftime('%Y-%m-%d')},
        {'amount': 1_000_000, 'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}
    ]

    monitoring_result = validator.monitor_transaction(transaction, history)
    print(json.dumps(monitoring_result, indent=2, default=str))
