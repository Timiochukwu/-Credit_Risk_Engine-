"""
Central Bank of Nigeria (CBN) Compliance Engine

Implements CBN regulations for lending, risk management, and reporting.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json


class CBNRegulation(Enum):
    """CBN Regulatory Requirements"""
    # Credit Risk Management
    CREDIT_CONCENTRATION = "Single obligor limit: 20% of capital"
    PROVISIONING = "NPL provisioning: 90+ days overdue"
    CREDIT_SCORING = "Risk-based lending required"

    # KYC/AML
    BVN_MANDATORY = "BVN required for all accounts"
    CUSTOMER_DUE_DILIGENCE = "Enhanced due diligence for high-risk customers"
    TRANSACTION_MONITORING = "Monitor suspicious transactions"

    # Reporting
    CREDIT_REPORTING = "Monthly credit risk returns"
    NPL_REPORTING = "Non-performing loan reporting"
    REGULATORY_RETURNS = "Quarterly regulatory returns"

    # Capital Adequacy
    MINIMUM_CAR = "Minimum 10% Capital Adequacy Ratio for microfinance"
    MINIMUM_CAR_COMMERCIAL = "Minimum 15% Capital Adequacy Ratio for commercial banks"

    # Loan Classification
    LOAN_CLASSIFICATION = "Standard, Sub-standard, Doubtful, Lost"


class LoanClassification(Enum):
    """CBN Loan Classification"""
    STANDARD = "STANDARD"  # 0-30 days overdue
    SUBSTANDARD = "SUBSTANDARD"  # 31-90 days overdue
    DOUBTFUL = "DOUBTFUL"  # 91-180 days overdue
    LOST = "LOST"  # 180+ days overdue


class CBNComplianceEngine:
    """
    Central Bank of Nigeria (CBN) Compliance Engine

    Features:
    - Loan concentration limits
    - Provisioning requirements
    - Loan classification
    - Regulatory reporting
    - Risk weight calculations
    - BVN validation enforcement
    """

    def __init__(self, bank_type: str = "commercial"):
        """
        Initialize CBN compliance engine

        Args:
            bank_type: 'commercial', 'microfinance', or 'merchant'
        """
        self.bank_type = bank_type

        # Set minimum CAR based on bank type
        self.minimum_car = {
            'commercial': 0.15,  # 15%
            'microfinance': 0.10,  # 10%
            'merchant': 0.10  # 10%
        }.get(bank_type, 0.15)

        # Single obligor limit (as % of capital)
        self.single_obligor_limit = 0.20  # 20%

        # Large exposure threshold
        self.large_exposure_threshold = 0.10  # 10% of capital

    def validate_bvn_requirement(self, application: Dict) -> Dict:
        """
        Validate BVN requirement (CBN mandate)

        Args:
            application: Loan application data

        Returns:
            Validation result
        """
        bvn = application.get('bvn')

        if not bvn:
            return {
                'compliant': False,
                'regulation': 'BVN_MANDATORY',
                'message': 'BVN is mandatory for all loan applications (CBN requirement)',
                'action': 'REJECT'
            }

        # Validate BVN format (11 digits)
        if len(str(bvn)) != 11 or not str(bvn).isdigit():
            return {
                'compliant': False,
                'regulation': 'BVN_MANDATORY',
                'message': 'Invalid BVN format (must be 11 digits)',
                'action': 'REJECT'
            }

        return {
            'compliant': True,
            'regulation': 'BVN_MANDATORY',
            'message': 'BVN requirement satisfied'
        }

    def classify_loan(self, days_overdue: int) -> Dict:
        """
        Classify loan according to CBN standards

        Args:
            days_overdue: Number of days payment is overdue

        Returns:
            Loan classification
        """
        if days_overdue <= 30:
            classification = LoanClassification.STANDARD
            provision_rate = 0.01  # 1% provision
        elif days_overdue <= 90:
            classification = LoanClassification.SUBSTANDARD
            provision_rate = 0.10  # 10% provision
        elif days_overdue <= 180:
            classification = LoanClassification.DOUBTFUL
            provision_rate = 0.50  # 50% provision
        else:
            classification = LoanClassification.LOST
            provision_rate = 1.00  # 100% provision

        return {
            'classification': classification.value,
            'days_overdue': days_overdue,
            'provision_rate': provision_rate,
            'provision_percentage': f"{provision_rate * 100:.0f}%",
            'is_npl': days_overdue > 90,  # Non-performing loan
            'cbn_compliant': True
        }

    def calculate_provisioning(self, loan_portfolio: List[Dict]) -> Dict:
        """
        Calculate provisioning requirements

        Args:
            loan_portfolio: List of loans with outstanding balances

        Returns:
            Provisioning details
        """
        total_loans = 0
        total_provision = 0
        classification_breakdown = {
            'STANDARD': {'count': 0, 'amount': 0, 'provision': 0},
            'SUBSTANDARD': {'count': 0, 'amount': 0, 'provision': 0},
            'DOUBTFUL': {'count': 0, 'amount': 0, 'provision': 0},
            'LOST': {'count': 0, 'amount': 0, 'provision': 0}
        }

        for loan in loan_portfolio:
            outstanding = loan.get('outstanding_balance', 0)
            days_overdue = loan.get('days_overdue', 0)

            total_loans += outstanding

            # Classify and calculate provision
            classification = self.classify_loan(days_overdue)
            category = classification['classification']
            provision_amount = outstanding * classification['provision_rate']

            total_provision += provision_amount

            classification_breakdown[category]['count'] += 1
            classification_breakdown[category]['amount'] += outstanding
            classification_breakdown[category]['provision'] += provision_amount

        # Calculate NPL ratio
        npl_amount = sum(
            v['amount'] for k, v in classification_breakdown.items()
            if k in ['DOUBTFUL', 'LOST']
        )
        npl_ratio = npl_amount / total_loans if total_loans > 0 else 0

        return {
            'total_loan_portfolio': total_loans,
            'total_provision_required': total_provision,
            'provision_percentage': f"{(total_provision / total_loans * 100) if total_loans > 0 else 0:.2f}%",
            'npl_amount': npl_amount,
            'npl_ratio': f"{npl_ratio * 100:.2f}%",
            'classification_breakdown': classification_breakdown,
            'cbn_compliant': npl_ratio < 0.05,  # CBN prefers NPL < 5%
            'recommendation': 'ACCEPTABLE' if npl_ratio < 0.05 else 'HIGH_RISK'
        }

    def check_concentration_limit(
        self,
        loan_amount: float,
        borrower_id: str,
        existing_exposure: float,
        bank_capital: float
    ) -> Dict:
        """
        Check single obligor concentration limit (CBN 20% rule)

        Args:
            loan_amount: New loan amount
            borrower_id: Borrower identifier
            existing_exposure: Existing loans to this borrower
            bank_capital: Bank's total capital

        Returns:
            Concentration check result
        """
        total_exposure = existing_exposure + loan_amount
        exposure_percentage = total_exposure / bank_capital

        limit_exceeded = exposure_percentage > self.single_obligor_limit

        return {
            'borrower_id': borrower_id,
            'new_loan': loan_amount,
            'existing_exposure': existing_exposure,
            'total_exposure': total_exposure,
            'bank_capital': bank_capital,
            'exposure_percentage': f"{exposure_percentage * 100:.2f}%",
            'limit': f"{self.single_obligor_limit * 100:.0f}%",
            'limit_exceeded': limit_exceeded,
            'compliant': not limit_exceeded,
            'regulation': 'CREDIT_CONCENTRATION',
            'action': 'REJECT' if limit_exceeded else 'APPROVE',
            'message': f"Exposure {exposure_percentage*100:.1f}% {'exceeds' if limit_exceeded else 'within'} CBN limit of {self.single_obligor_limit*100:.0f}%"
        }

    def check_large_exposure(
        self,
        loan_amount: float,
        bank_capital: float
    ) -> Dict:
        """
        Check if loan is a large exposure (>10% of capital)

        Args:
            loan_amount: Loan amount
            bank_capital: Bank's total capital

        Returns:
            Large exposure check
        """
        exposure_percentage = loan_amount / bank_capital
        is_large_exposure = exposure_percentage > self.large_exposure_threshold

        return {
            'loan_amount': loan_amount,
            'bank_capital': bank_capital,
            'exposure_percentage': f"{exposure_percentage * 100:.2f}%",
            'threshold': f"{self.large_exposure_threshold * 100:.0f}%",
            'is_large_exposure': is_large_exposure,
            'requires_board_approval': is_large_exposure,
            'requires_cbn_reporting': is_large_exposure,
            'message': 'Large exposure - requires board approval and CBN reporting' if is_large_exposure else 'Normal exposure'
        }

    def calculate_risk_weight(self, loan_data: Dict) -> Dict:
        """
        Calculate risk weight for capital adequacy (Basel III / CBN)

        Args:
            loan_data: Loan details

        Returns:
            Risk weight calculation
        """
        # Risk weights based on loan type and collateral
        loan_type = loan_data.get('loan_type', 'unsecured')
        has_collateral = loan_data.get('has_collateral', False)
        collateral_type = loan_data.get('collateral_type')
        credit_rating = loan_data.get('credit_rating', 'unrated')

        # CBN/Basel III risk weights
        if loan_type == 'government':
            risk_weight = 0.0  # 0% for government securities
        elif has_collateral and collateral_type in ['cash', 'government_bonds']:
            risk_weight = 0.0  # 0% for cash collateral
        elif has_collateral and collateral_type in ['real_estate', 'mortgage']:
            risk_weight = 0.50  # 50% for mortgage
        elif credit_rating in ['AAA', 'AA']:
            risk_weight = 0.20  # 20% for high-rated corporates
        elif credit_rating in ['A', 'BBB']:
            risk_weight = 0.50  # 50% for medium-rated
        elif loan_type == 'sme':
            risk_weight = 0.75  # 75% for SME
        elif loan_type == 'retail':
            risk_weight = 0.75  # 75% for retail
        else:
            risk_weight = 1.00  # 100% for unrated/unsecured

        loan_amount = loan_data.get('loan_amount', 0)
        risk_weighted_assets = loan_amount * risk_weight

        return {
            'loan_amount': loan_amount,
            'loan_type': loan_type,
            'has_collateral': has_collateral,
            'credit_rating': credit_rating,
            'risk_weight': risk_weight,
            'risk_weight_percentage': f"{risk_weight * 100:.0f}%",
            'risk_weighted_assets': risk_weighted_assets,
            'capital_required': risk_weighted_assets * self.minimum_car,  # CAR × RWA
            'cbn_compliant': True
        }

    def check_capital_adequacy(
        self,
        total_capital: float,
        risk_weighted_assets: float
    ) -> Dict:
        """
        Check Capital Adequacy Ratio (CAR) compliance

        Args:
            total_capital: Bank's total capital
            risk_weighted_assets: Total risk-weighted assets

        Returns:
            CAR compliance check
        """
        car = total_capital / risk_weighted_assets if risk_weighted_assets > 0 else 0

        compliant = car >= self.minimum_car

        return {
            'total_capital': total_capital,
            'risk_weighted_assets': risk_weighted_assets,
            'capital_adequacy_ratio': f"{car * 100:.2f}%",
            'minimum_required': f"{self.minimum_car * 100:.0f}%",
            'excess_capital': total_capital - (risk_weighted_assets * self.minimum_car),
            'compliant': compliant,
            'bank_type': self.bank_type,
            'regulation': 'MINIMUM_CAR',
            'message': f"CAR {car*100:.2f}% {'meets' if compliant else 'below'} CBN minimum of {self.minimum_car*100:.0f}%"
        }

    def generate_regulatory_return(self, portfolio_data: Dict) -> Dict:
        """
        Generate CBN regulatory return

        Args:
            portfolio_data: Complete portfolio data

        Returns:
            Regulatory return report
        """
        return {
            'report_type': 'CBN_CREDIT_RISK_RETURN',
            'bank_name': portfolio_data.get('bank_name'),
            'reporting_period': datetime.now().strftime('%Y-%m'),
            'generated_at': datetime.now().isoformat(),

            'portfolio_summary': {
                'total_loans': portfolio_data.get('total_loans', 0),
                'total_outstanding': portfolio_data.get('total_outstanding', 0),
                'number_of_borrowers': portfolio_data.get('borrower_count', 0)
            },

            'loan_classification': self.calculate_provisioning(
                portfolio_data.get('loans', [])
            ),

            'capital_adequacy': self.check_capital_adequacy(
                total_capital=portfolio_data.get('total_capital', 0),
                risk_weighted_assets=portfolio_data.get('risk_weighted_assets', 0)
            ),

            'concentration_risk': {
                'top_10_exposures': portfolio_data.get('top_10_exposures', []),
                'large_exposures_count': portfolio_data.get('large_exposures_count', 0),
                'sector_concentration': portfolio_data.get('sector_concentration', {})
            },

            'compliance_status': 'COMPLIANT',
            'cbn_submission_deadline': (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
        }

    def validate_loan_application(
        self,
        application: Dict,
        bank_data: Dict
    ) -> Dict:
        """
        Complete CBN compliance validation for loan application

        Args:
            application: Loan application
            bank_data: Bank's financial data

        Returns:
            Comprehensive compliance check
        """
        validations = []

        # 1. BVN validation
        bvn_check = self.validate_bvn_requirement(application)
        validations.append(bvn_check)

        # 2. Concentration limit
        if 'borrower_id' in application:
            concentration_check = self.check_concentration_limit(
                loan_amount=application.get('loan_amount', 0),
                borrower_id=application['borrower_id'],
                existing_exposure=application.get('existing_exposure', 0),
                bank_capital=bank_data.get('total_capital', 1_000_000_000)
            )
            validations.append(concentration_check)

        # 3. Large exposure check
        large_exposure_check = self.check_large_exposure(
            loan_amount=application.get('loan_amount', 0),
            bank_capital=bank_data.get('total_capital', 1_000_000_000)
        )
        validations.append(large_exposure_check)

        # 4. Risk weight calculation
        risk_weight = self.calculate_risk_weight(application)
        validations.append(risk_weight)

        # Overall compliance
        all_compliant = all(
            v.get('compliant', True) or not v.get('limit_exceeded', False)
            for v in validations
        )

        return {
            'application_id': application.get('application_id'),
            'cbn_compliant': all_compliant,
            'validations': validations,
            'overall_status': 'APPROVED' if all_compliant else 'REJECTED',
            'timestamp': datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Initialize CBN compliance engine
    cbn = CBNComplianceEngine(bank_type='commercial')

    print("=== CBN Compliance Engine ===\n")

    # Test BVN validation
    application = {
        'application_id': 'NGN20240315001',
        'bvn': '12345678901',
        'loan_amount': 5_000_000,
        'borrower_id': 'BRW001',
        'existing_exposure': 10_000_000,
        'loan_type': 'retail',
        'has_collateral': False
    }

    bank_data = {
        'total_capital': 100_000_000,
        'risk_weighted_assets': 500_000_000
    }

    # Full validation
    result = cbn.validate_loan_application(application, bank_data)

    print("Loan Application Compliance Check:")
    print(json.dumps(result, indent=2, default=str))

    # Test loan classification
    print("\n=== Loan Classification ===")
    classification = cbn.classify_loan(days_overdue=45)
    print(json.dumps(classification, indent=2))

    # Test capital adequacy
    print("\n=== Capital Adequacy Check ===")
    car_check = cbn.check_capital_adequacy(
        total_capital=100_000_000,
        risk_weighted_assets=500_000_000
    )
    print(json.dumps(car_check, indent=2))
