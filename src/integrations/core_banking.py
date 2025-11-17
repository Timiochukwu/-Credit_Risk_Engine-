"""
Core Banking System Integration

Integrates with major core banking systems used in Nigerian banks:
- Finacle (Infosys)
- T24 (Temenos)
- BankOne (FSS)
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class CoreBankingSystem(Enum):
    """Supported core banking systems"""
    FINACLE = "FINACLE"
    T24 = "T24"
    BANKONE = "BANKONE"
    FLEXCUBE = "FLEXCUBE"


class FinacleIntegration:
    """
    Finacle Core Banking Integration

    Finacle is widely used by Nigerian banks including:
    - Union Bank
    - Polaris Bank
    - Fidelity Bank
    """

    def __init__(self, api_url: str, api_key: str):
        """
        Initialize Finacle integration

        Args:
            api_url: Finacle API endpoint
            api_key: API authentication key
        """
        self.api_url = api_url
        self.api_key = api_key
        self.system_name = "FINACLE"

    def get_customer_details(self, customer_id: str) -> Dict:
        """
        Retrieve customer details from Finacle

        Args:
            customer_id: Customer ID

        Returns:
            Customer information
        """
        # In production, make actual API call
        # response = requests.post(
        #     f"{self.api_url}/customer/inquiry",
        #     headers={'Authorization': f'Bearer {self.api_key}'},
        #     json={'customerId': customer_id}
        # )

        # Mock response
        return {
            'customer_id': customer_id,
            'account_number': '0123456789',
            'full_name': 'Adebayo Ogunleye',
            'bvn': '12345678901',
            'phone': '08031234567',
            'email': 'adebayo@example.com',
            'account_status': 'ACTIVE',
            'account_type': 'SAVINGS',
            'branch_code': 'NG001',
            'relationship_officer': 'Chiamaka Nwosu',
            'kyc_status': 'COMPLETED',
            'risk_rating': 'LOW',
            'source_system': self.system_name
        }

    def get_account_balance(self, account_number: str) -> Dict:
        """
        Get account balance

        Args:
            account_number: Account number

        Returns:
            Balance information
        """
        return {
            'account_number': account_number,
            'available_balance': 1_450_000,
            'ledger_balance': 1_500_000,
            'currency': 'NGN',
            'last_transaction_date': datetime.now().isoformat(),
            'source_system': self.system_name
        }

    def get_transaction_history(
        self,
        account_number: str,
        days: int = 90
    ) -> List[Dict]:
        """
        Get transaction history

        Args:
            account_number: Account number
            days: Number of days to retrieve

        Returns:
            List of transactions
        """
        # Mock transactions
        return [
            {
                'transaction_id': 'FIN001',
                'date': '2024-03-15',
                'type': 'CREDIT',
                'amount': 450_000,
                'description': 'Salary',
                'balance_after': 1_500_000
            },
            {
                'transaction_id': 'FIN002',
                'date': '2024-03-14',
                'type': 'DEBIT',
                'amount': 50_000,
                'description': 'ATM Withdrawal',
                'balance_after': 1_050_000
            }
        ]

    def create_loan_account(self, loan_data: Dict) -> Dict:
        """
        Create loan account in Finacle

        Args:
            loan_data: Loan account details

        Returns:
            Created loan account details
        """
        loan_account_number = f"LN{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return {
            'status': 'success',
            'loan_account_number': loan_account_number,
            'customer_id': loan_data.get('customer_id'),
            'loan_amount': loan_data.get('loan_amount'),
            'interest_rate': loan_data.get('interest_rate'),
            'tenure_months': loan_data.get('tenure_months'),
            'disbursement_account': loan_data.get('disbursement_account'),
            'created_at': datetime.now().isoformat(),
            'source_system': self.system_name
        }

    def disburse_loan(self, loan_account: str, disbursement_account: str, amount: float) -> Dict:
        """
        Disburse loan amount

        Args:
            loan_account: Loan account number
            disbursement_account: Customer account for disbursement
            amount: Loan amount

        Returns:
            Disbursement result
        """
        transaction_ref = f"DISB{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return {
            'status': 'success',
            'transaction_reference': transaction_ref,
            'loan_account': loan_account,
            'disbursement_account': disbursement_account,
            'amount': amount,
            'disbursed_at': datetime.now().isoformat(),
            'source_system': self.system_name
        }


class T24Integration:
    """
    T24 (Temenos) Core Banking Integration

    T24 is used by Nigerian banks including:
    - First Bank of Nigeria
    - UBA (United Bank for Africa)
    - Access Bank
    """

    def __init__(self, api_url: str, username: str, password: str):
        """
        Initialize T24 integration

        Args:
            api_url: T24 API endpoint
            username: API username
            password: API password
        """
        self.api_url = api_url
        self.username = username
        self.password = password
        self.system_name = "T24"

    def inquiry_customer(self, customer_id: str) -> Dict:
        """
        T24 customer inquiry

        Args:
            customer_id: Customer ID

        Returns:
            Customer details
        """
        return {
            'customer_number': customer_id,
            'customer_name': 'Ifeoma Okeke',
            'sector': 'INDIVIDUAL',
            'residence': 'RESIDENT',
            'nationality': 'NG',
            'date_of_birth': '1988-05-20',
            'bvn': '98765432109',
            'phone': '+2348091234567',
            'email': 'ifeoma@example.com',
            'kyc_complete': True,
            'source_system': self.system_name
        }

    def get_customer_accounts(self, customer_id: str) -> List[Dict]:
        """
        Get all accounts for customer

        Args:
            customer_id: Customer ID

        Returns:
            List of accounts
        """
        return [
            {
                'account_number': '1234567890',
                'account_title': 'Ifeoma Okeke',
                'product_line': 'SAVINGS',
                'currency': 'NGN',
                'available_balance': 2_350_000,
                'status': 'ACTIVE'
            },
            {
                'account_number': '1234567891',
                'account_title': 'Ifeoma Okeke',
                'product_line': 'CURRENT',
                'currency': 'NGN',
                'available_balance': 890_000,
                'status': 'ACTIVE'
            }
        ]

    def create_loan_arrangement(self, loan_details: Dict) -> Dict:
        """
        Create loan arrangement in T24

        Args:
            loan_details: Loan details

        Returns:
            Loan arrangement ID
        """
        arrangement_id = f"AA{datetime.now().strftime('%y%m')}0001"

        return {
            'status': 'success',
            'arrangement_id': arrangement_id,
            'product_id': 'PERSONAL.LOAN',
            'customer': loan_details.get('customer_id'),
            'currency': 'NGN',
            'amount': loan_details.get('loan_amount'),
            'term': f"{loan_details.get('tenure_months', 12)}M",
            'interest_rate': loan_details.get('interest_rate'),
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'source_system': self.system_name
        }


class BankOneIntegration:
    """
    BankOne (FSS) Core Banking Integration

    BankOne is used by Nigerian banks including:
    - Sterling Bank
    - Unity Bank
    - Heritage Bank
    """

    def __init__(self, base_url: str, tenant_id: str, api_key: str):
        """
        Initialize BankOne integration

        Args:
            base_url: BankOne API base URL
            tenant_id: Tenant identifier
            api_key: API key
        """
        self.base_url = base_url
        self.tenant_id = tenant_id
        self.api_key = api_key
        self.system_name = "BANKONE"

    def get_customer_profile(self, customer_id: str) -> Dict:
        """
        Get customer profile

        Args:
            customer_id: Customer ID

        Returns:
            Customer profile
        """
        return {
            'customer_id': customer_id,
            'first_name': 'Chukwuemeka',
            'last_name': 'Nnamdi',
            'middle_name': 'Ikenna',
            'date_of_birth': '1985-08-15',
            'gender': 'MALE',
            'bvn': '45678912345',
            'phone_primary': '08071234567',
            'email': 'chukwuemeka@example.com',
            'address': '45 Awolowo Road, Ikoyi, Lagos',
            'occupation': 'Software Engineer',
            'employer': 'Tech Company Ltd',
            'monthly_income': 750_000,
            'identification_type': 'National ID',
            'identification_number': 'NG123456789',
            'customer_category': 'RETAIL',
            'source_system': self.system_name
        }

    def fetch_account_statement(self, account_number: str, start_date: str, end_date: str) -> Dict:
        """
        Fetch account statement

        Args:
            account_number: Account number
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Account statement
        """
        return {
            'account_number': account_number,
            'account_name': 'Chukwuemeka Nnamdi',
            'period': {
                'start': start_date,
                'end': end_date
            },
            'opening_balance': 1_200_000,
            'closing_balance': 1_450_000,
            'total_credits': 850_000,
            'total_debits': 600_000,
            'transactions': [
                {
                    'date': '2024-03-15',
                    'description': 'Salary',
                    'credit': 750_000,
                    'debit': 0,
                    'balance': 1_950_000
                },
                {
                    'date': '2024-03-16',
                    'description': 'POS Purchase',
                    'credit': 0,
                    'debit': 500_000,
                    'balance': 1_450_000
                }
            ],
            'source_system': self.system_name
        }

    def initiate_loan_booking(self, loan_request: Dict) -> Dict:
        """
        Initiate loan booking

        Args:
            loan_request: Loan request details

        Returns:
            Booking confirmation
        """
        loan_id = f"LOAN{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return {
            'status': 'PENDING_APPROVAL',
            'loan_id': loan_id,
            'customer_id': loan_request.get('customer_id'),
            'loan_product': loan_request.get('loan_product', 'PERSONAL_LOAN'),
            'principal_amount': loan_request.get('loan_amount'),
            'interest_rate': loan_request.get('interest_rate'),
            'tenure_months': loan_request.get('tenure_months'),
            'repayment_account': loan_request.get('repayment_account'),
            'workflow_status': 'AWAITING_CREDIT_APPROVAL',
            'created_at': datetime.now().isoformat(),
            'source_system': self.system_name
        }


class CoreBankingIntegrationManager:
    """
    Unified manager for all core banking integrations

    Provides single interface to interact with multiple core banking systems
    """

    def __init__(self):
        """Initialize integration manager"""
        self.integrations: Dict[str, object] = {}

    def register_integration(self, system: CoreBankingSystem, integration: object):
        """
        Register a core banking integration

        Args:
            system: Core banking system type
            integration: Integration instance
        """
        self.integrations[system.value] = integration

    def get_customer_data(self, system: CoreBankingSystem, customer_id: str) -> Dict:
        """
        Get customer data from any system

        Args:
            system: Core banking system
            customer_id: Customer ID

        Returns:
            Customer data
        """
        integration = self.integrations.get(system.value)

        if not integration:
            return {'error': f'Integration for {system.value} not configured'}

        if isinstance(integration, FinacleIntegration):
            return integration.get_customer_details(customer_id)
        elif isinstance(integration, T24Integration):
            return integration.inquiry_customer(customer_id)
        elif isinstance(integration, BankOneIntegration):
            return integration.get_customer_profile(customer_id)

        return {'error': 'Unknown integration type'}


# Example usage
if __name__ == "__main__":
    # Initialize integrations
    finacle = FinacleIntegration(
        api_url="https://finacle.bank.com/api",
        api_key="finacle_key_123"
    )

    t24 = T24Integration(
        api_url="https://t24.bank.com/api",
        username="t24_user",
        password="t24_pass"
    )

    bankone = BankOneIntegration(
        base_url="https://bankone.bank.com/api",
        tenant_id="TENANT001",
        api_key="bankone_key_123"
    )

    # Test Finacle
    print("=== Finacle Integration ===")
    customer = finacle.get_customer_details("CUST001")
    print(json.dumps(customer, indent=2))

    balance = finacle.get_account_balance("0123456789")
    print(json.dumps(balance, indent=2))

    # Test T24
    print("\n=== T24 Integration ===")
    t24_customer = t24.inquiry_customer("CUST002")
    print(json.dumps(t24_customer, indent=2))

    # Test BankOne
    print("\n=== BankOne Integration ===")
    bankone_customer = bankone.get_customer_profile("CUST003")
    print(json.dumps(bankone_customer, indent=2))

    # Unified manager
    print("\n=== Unified Manager ===")
    manager = CoreBankingIntegrationManager()
    manager.register_integration(CoreBankingSystem.FINACLE, finacle)
    manager.register_integration(CoreBankingSystem.T24, t24)
    manager.register_integration(CoreBankingSystem.BANKONE, bankone)

    # Get customer from any system
    data = manager.get_customer_data(CoreBankingSystem.FINACLE, "CUST001")
    print(json.dumps(data, indent=2))
