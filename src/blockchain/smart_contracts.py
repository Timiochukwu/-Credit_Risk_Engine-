"""
Smart Contracts for Loan Agreements

Automated enforcement of loan terms and conditions.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json


class ContractStatus(Enum):
    """Contract status states"""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    FULFILLED = "FULFILLED"
    DEFAULTED = "DEFAULTED"
    CANCELLED = "CANCELLED"


class PaymentStatus(Enum):
    """Payment status"""
    PENDING = "PENDING"
    PAID = "PAID"
    LATE = "LATE"
    MISSED = "MISSED"


@dataclass
class LoanContract:
    """Smart contract for loan agreement"""
    contract_id: str
    application_id: str
    borrower_bvn: str
    borrower_name: str
    loan_amount: float
    interest_rate: float
    tenure_months: int
    monthly_payment: float
    start_date: str
    end_date: str
    status: str = ContractStatus.PENDING.value
    collateral: Optional[Dict] = None
    guarantor: Optional[Dict] = None
    terms: Optional[Dict] = None
    payment_schedule: Optional[List[Dict]] = None
    created_at: str = None
    activated_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), indent=2, default=str)


class SmartContractEngine:
    """
    Smart contract engine for loan management.

    Features:
    - Automated contract creation
    - Payment schedule generation
    - Automatic payment verification
    - Late payment detection
    - Default triggers
    - Early settlement calculations
    """

    def __init__(self):
        """Initialize smart contract engine"""
        self.contracts: Dict[str, LoanContract] = {}
        self.payment_history: Dict[str, List[Dict]] = {}

    def create_contract(
        self,
        application_id: str,
        borrower_data: Dict,
        loan_terms: Dict,
        collateral: Optional[Dict] = None,
        guarantor: Optional[Dict] = None
    ) -> LoanContract:
        """
        Create a new loan smart contract

        Args:
            application_id: Loan application ID
            borrower_data: Borrower information
            loan_terms: Loan terms and conditions
            collateral: Collateral details (optional)
            guarantor: Guarantor details (optional)

        Returns:
            LoanContract object
        """
        contract_id = f"CONTRACT_{application_id}"

        # Calculate monthly payment
        loan_amount = loan_terms['loan_amount']
        annual_rate = loan_terms['interest_rate'] / 100
        monthly_rate = annual_rate / 12
        tenure = loan_terms['tenure_months']

        # Calculate EMI using formula: P * r * (1+r)^n / ((1+r)^n - 1)
        if monthly_rate > 0:
            monthly_payment = loan_amount * monthly_rate * \
                             (1 + monthly_rate) ** tenure / \
                             ((1 + monthly_rate) ** tenure - 1)
        else:
            monthly_payment = loan_amount / tenure

        # Calculate dates
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30 * tenure)

        # Generate payment schedule
        payment_schedule = self._generate_payment_schedule(
            loan_amount=loan_amount,
            monthly_payment=monthly_payment,
            monthly_rate=monthly_rate,
            tenure=tenure,
            start_date=start_date
        )

        # Create contract
        contract = LoanContract(
            contract_id=contract_id,
            application_id=application_id,
            borrower_bvn=borrower_data['bvn'],
            borrower_name=borrower_data['name'],
            loan_amount=loan_amount,
            interest_rate=loan_terms['interest_rate'],
            tenure_months=tenure,
            monthly_payment=monthly_payment,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            collateral=collateral,
            guarantor=guarantor,
            terms=loan_terms,
            payment_schedule=payment_schedule
        )

        self.contracts[contract_id] = contract
        self.payment_history[contract_id] = []

        return contract

    def _generate_payment_schedule(
        self,
        loan_amount: float,
        monthly_payment: float,
        monthly_rate: float,
        tenure: int,
        start_date: datetime
    ) -> List[Dict]:
        """
        Generate amortization schedule

        Args:
            loan_amount: Principal amount
            monthly_payment: Monthly EMI
            monthly_rate: Monthly interest rate
            tenure: Loan tenure in months
            start_date: Loan start date

        Returns:
            List of payment schedules
        """
        schedule = []
        balance = loan_amount

        for month in range(1, tenure + 1):
            # Calculate interest and principal
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            balance -= principal

            # Due date (first of each month)
            due_date = start_date + timedelta(days=30 * month)

            schedule.append({
                'payment_number': month,
                'due_date': due_date.isoformat(),
                'payment_amount': round(monthly_payment, 2),
                'principal': round(principal, 2),
                'interest': round(interest, 2),
                'balance': round(max(0, balance), 2),
                'status': PaymentStatus.PENDING.value
            })

        return schedule

    def activate_contract(self, contract_id: str) -> bool:
        """
        Activate contract after disbursement

        Args:
            contract_id: Contract ID

        Returns:
            True if activated successfully
        """
        if contract_id not in self.contracts:
            return False

        contract = self.contracts[contract_id]
        contract.status = ContractStatus.ACTIVE.value
        contract.activated_at = datetime.now().isoformat()

        return True

    def record_payment(
        self,
        contract_id: str,
        payment_number: int,
        amount_paid: float,
        payment_date: str,
        payment_method: str
    ) -> Dict:
        """
        Record a loan payment

        Args:
            contract_id: Contract ID
            payment_number: Payment number (1-N)
            amount_paid: Amount paid
            payment_date: Date of payment
            payment_method: Payment method

        Returns:
            Payment result
        """
        if contract_id not in self.contracts:
            return {'success': False, 'error': 'Contract not found'}

        contract = self.contracts[contract_id]
        schedule = contract.payment_schedule

        if payment_number > len(schedule):
            return {'success': False, 'error': 'Invalid payment number'}

        payment = schedule[payment_number - 1]
        expected_amount = payment['payment_amount']
        due_date = datetime.fromisoformat(payment['due_date'])
        paid_date = datetime.fromisoformat(payment_date)

        # Check if late
        days_late = (paid_date - due_date).days
        is_late = days_late > 0

        # Calculate late fee
        late_fee = 0
        if is_late:
            # 2% late fee per month (Nigerian typical)
            late_fee = expected_amount * 0.02 * (days_late / 30)

        # Update payment status
        if amount_paid >= expected_amount:
            payment['status'] = PaymentStatus.LATE.value if is_late else PaymentStatus.PAID.value
            payment['paid_date'] = payment_date
            payment['amount_paid'] = amount_paid
            payment['late_fee'] = round(late_fee, 2)
            payment['days_late'] = days_late

            # Record in history
            self.payment_history[contract_id].append({
                'payment_number': payment_number,
                'amount': amount_paid,
                'date': payment_date,
                'method': payment_method,
                'late': is_late,
                'late_fee': round(late_fee, 2)
            })

            # Check if loan is fully paid
            all_paid = all(p['status'] in [PaymentStatus.PAID.value, PaymentStatus.LATE.value]
                          for p in schedule)

            if all_paid:
                contract.status = ContractStatus.FULFILLED.value

            return {
                'success': True,
                'payment_number': payment_number,
                'amount_paid': amount_paid,
                'late': is_late,
                'late_fee': round(late_fee, 2),
                'remaining_balance': payment['balance'],
                'contract_status': contract.status
            }
        else:
            return {
                'success': False,
                'error': 'Insufficient payment',
                'expected': expected_amount,
                'paid': amount_paid,
                'shortfall': expected_amount - amount_paid
            }

    def check_late_payments(self, contract_id: str) -> List[Dict]:
        """
        Check for late/missed payments

        Args:
            contract_id: Contract ID

        Returns:
            List of late payments
        """
        if contract_id not in self.contracts:
            return []

        contract = self.contracts[contract_id]
        now = datetime.now()
        late_payments = []

        for payment in contract.payment_schedule:
            if payment['status'] == PaymentStatus.PENDING.value:
                due_date = datetime.fromisoformat(payment['due_date'])
                days_overdue = (now - due_date).days

                if days_overdue > 0:
                    late_payments.append({
                        'payment_number': payment['payment_number'],
                        'due_date': payment['due_date'],
                        'amount': payment['payment_amount'],
                        'days_overdue': days_overdue,
                        'late_fee': round(payment['payment_amount'] * 0.02 * (days_overdue / 30), 2)
                    })

        return late_payments

    def calculate_early_settlement(self, contract_id: str) -> Optional[Dict]:
        """
        Calculate early settlement amount

        Args:
            contract_id: Contract ID

        Returns:
            Settlement details
        """
        if contract_id not in self.contracts:
            return None

        contract = self.contracts[contract_id]

        # Calculate remaining principal
        remaining_principal = sum(
            p['principal'] for p in contract.payment_schedule
            if p['status'] == PaymentStatus.PENDING.value
        )

        # Calculate remaining interest
        remaining_interest = sum(
            p['interest'] for p in contract.payment_schedule
            if p['status'] == PaymentStatus.PENDING.value
        )

        # Early settlement discount (50% of remaining interest - typical in Nigeria)
        discount = remaining_interest * 0.50

        settlement_amount = remaining_principal + remaining_interest - discount

        return {
            'contract_id': contract_id,
            'remaining_principal': round(remaining_principal, 2),
            'remaining_interest': round(remaining_interest, 2),
            'discount': round(discount, 2),
            'settlement_amount': round(settlement_amount, 2),
            'savings': round(discount, 2)
        }

    def trigger_default(self, contract_id: str, reason: str) -> bool:
        """
        Mark contract as defaulted

        Args:
            contract_id: Contract ID
            reason: Default reason

        Returns:
            True if marked as defaulted
        """
        if contract_id not in self.contracts:
            return False

        contract = self.contracts[contract_id]
        contract.status = ContractStatus.DEFAULTED.value

        # Record default event
        self.payment_history[contract_id].append({
            'event': 'DEFAULT',
            'timestamp': datetime.now().isoformat(),
            'reason': reason
        })

        return True

    def get_contract_summary(self, contract_id: str) -> Optional[Dict]:
        """
        Get contract summary

        Args:
            contract_id: Contract ID

        Returns:
            Contract summary
        """
        if contract_id not in self.contracts:
            return None

        contract = self.contracts[contract_id]

        paid_payments = [p for p in contract.payment_schedule
                        if p['status'] in [PaymentStatus.PAID.value, PaymentStatus.LATE.value]]

        pending_payments = [p for p in contract.payment_schedule
                           if p['status'] == PaymentStatus.PENDING.value]

        total_paid = sum(p.get('amount_paid', 0) for p in paid_payments)
        total_remaining = sum(p['payment_amount'] for p in pending_payments)

        return {
            'contract_id': contract_id,
            'application_id': contract.application_id,
            'borrower': contract.borrower_name,
            'bvn': contract.borrower_bvn,
            'status': contract.status,
            'loan_amount': contract.loan_amount,
            'monthly_payment': contract.monthly_payment,
            'tenure': contract.tenure_months,
            'payments': {
                'total': len(contract.payment_schedule),
                'paid': len(paid_payments),
                'pending': len(pending_payments),
                'late': len([p for p in paid_payments if p.get('days_late', 0) > 0])
            },
            'amounts': {
                'total_paid': round(total_paid, 2),
                'total_remaining': round(total_remaining, 2),
                'progress': f"{len(paid_payments)/len(contract.payment_schedule)*100:.1f}%"
            },
            'late_payments': self.check_late_payments(contract_id),
            'start_date': contract.start_date,
            'end_date': contract.end_date
        }

    def get_all_active_contracts(self) -> List[str]:
        """
        Get all active contract IDs

        Returns:
            List of active contract IDs
        """
        return [
            cid for cid, contract in self.contracts.items()
            if contract.status == ContractStatus.ACTIVE.value
        ]

    def get_contracts_at_risk(self) -> List[Dict]:
        """
        Get contracts at risk of default

        Returns:
            List of risky contracts
        """
        at_risk = []

        for contract_id in self.get_all_active_contracts():
            late_payments = self.check_late_payments(contract_id)

            # At risk if 2+ late payments or 1 payment >30 days late
            if len(late_payments) >= 2 or \
               any(p['days_overdue'] > 30 for p in late_payments):

                summary = self.get_contract_summary(contract_id)
                summary['late_payment_count'] = len(late_payments)
                summary['max_days_overdue'] = max([p['days_overdue'] for p in late_payments], default=0)

                at_risk.append(summary)

        return at_risk


# Example usage
if __name__ == "__main__":
    engine = SmartContractEngine()

    # Create contract
    contract = engine.create_contract(
        application_id="NGN20240315001",
        borrower_data={
            'bvn': '12345678901',
            'name': 'Adebayo Ogunleye'
        },
        loan_terms={
            'loan_amount': 2_500_000,
            'interest_rate': 22.5,
            'tenure_months': 12
        }
    )

    print("Smart Contract Created:")
    print(f"Contract ID: {contract.contract_id}")
    print(f"Monthly Payment: ₦{contract.monthly_payment:,.2f}")
    print(f"Status: {contract.status}")

    # Activate contract
    engine.activate_contract(contract.contract_id)
    print(f"\nContract activated!")

    # Check summary
    summary = engine.get_contract_summary(contract.contract_id)
    print(f"\nContract Summary:")
    print(json.dumps(summary, indent=2, default=str))
