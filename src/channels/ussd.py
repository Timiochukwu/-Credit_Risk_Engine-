"""
USSD Integration for Feature Phones

Enables loan applications via USSD (*347#) for users without smartphones
"""

from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class USSDSessionState(Enum):
    """USSD session states"""
    START = "START"
    MAIN_MENU = "MAIN_MENU"
    NEW_LOAN = "NEW_LOAN"
    CHECK_STATUS = "CHECK_STATUS"
    MAKE_PAYMENT = "MAKE_PAYMENT"
    GET_BVN = "GET_BVN"
    GET_AMOUNT = "GET_AMOUNT"
    GET_TENURE = "GET_TENURE"
    CONFIRM = "CONFIRM"
    END = "END"


class USSDIntegration:
    """
    USSD interface for credit risk system

    Features:
    - Loan application via USSD
    - Status checking
    - Payment instructions
    - Balance inquiry
    - Works on all phones (2G compatible)

    Example USSD code: *347#
    """

    def __init__(self, shortcode: str = "*347#"):
        """
        Initialize USSD integration

        Args:
            shortcode: USSD shortcode
        """
        self.shortcode = shortcode
        self.sessions: Dict[str, Dict] = {}

    def handle_ussd_request(self, session_id: str, phone_number: str, text: str) -> Dict:
        """
        Handle incoming USSD request

        Args:
            session_id: USSD session ID
            phone_number: User's phone number
            text: User input

        Returns:
            USSD response
        """
        # Initialize session if new
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'phone_number': phone_number,
                'state': USSDSessionState.START,
                'data': {},
                'created_at': datetime.now().isoformat()
            }

        session = self.sessions[session_id]
        state = session['state']

        # Route based on current state
        if state == USSDSessionState.START:
            return self._show_main_menu(session_id)

        elif state == USSDSessionState.MAIN_MENU:
            return self._handle_main_menu(session_id, text)

        elif state == USSDSessionState.GET_BVN:
            return self._handle_bvn_input(session_id, text)

        elif state == USSDSessionState.GET_AMOUNT:
            return self._handle_amount_input(session_id, text)

        elif state == USSDSessionState.GET_TENURE:
            return self._handle_tenure_input(session_id, text)

        elif state == USSDSessionState.CONFIRM:
            return self._handle_confirmation(session_id, text)

        else:
            return self._show_main_menu(session_id)

    def _show_main_menu(self, session_id: str) -> Dict:
        """Show main menu"""
        self.sessions[session_id]['state'] = USSDSessionState.MAIN_MENU

        menu = (
            "Welcome to Credit Risk Engine\n"
            "1. Apply for loan\n"
            "2. Check loan status\n"
            "3. Make payment\n"
            "4. Balance inquiry\n"
            "0. Exit"
        )

        return {
            'type': 'CON',  # Continue
            'message': menu,
            'session_id': session_id
        }

    def _handle_main_menu(self, session_id: str, choice: str) -> Dict:
        """Handle main menu selection"""
        session = self.sessions[session_id]

        if choice == "1":
            # Apply for loan
            session['state'] = USSDSessionState.GET_BVN
            return {
                'type': 'CON',
                'message': "Apply for Loan\n\nEnter your 11-digit BVN:"
            }

        elif choice == "2":
            # Check status
            return self._check_loan_status(session_id)

        elif choice == "3":
            # Make payment
            return self._show_payment_instructions(session_id)

        elif choice == "4":
            # Balance inquiry
            return self._check_balance(session_id)

        elif choice == "0":
            # Exit
            return {
                'type': 'END',
                'message': "Thank you for using Credit Risk Engine"
            }

        else:
            return self._show_main_menu(session_id)

    def _handle_bvn_input(self, session_id: str, bvn: str) -> Dict:
        """Handle BVN input"""
        session = self.sessions[session_id]

        # Validate BVN format
        if len(bvn) != 11 or not bvn.isdigit():
            return {
                'type': 'CON',
                'message': "Invalid BVN format\n\nPlease enter your 11-digit BVN:"
            }

        session['data']['bvn'] = bvn
        session['state'] = USSDSessionState.GET_AMOUNT

        return {
            'type': 'CON',
            'message': "How much do you want to borrow?\n(Min: N50,000, Max: N5,000,000)"
        }

    def _handle_amount_input(self, session_id: str, amount_str: str) -> Dict:
        """Handle loan amount input"""
        session = self.sessions[session_id]

        try:
            amount = float(amount_str.replace(',', ''))

            if amount < 50_000 or amount > 5_000_000:
                return {
                    'type': 'CON',
                    'message': "Amount must be between N50,000 and N5,000,000\n\nEnter amount:"
                }

            session['data']['loan_amount'] = amount
            session['state'] = USSDSessionState.GET_TENURE

            return {
                'type': 'CON',
                'message': "Select loan duration:\n1. 3 months\n2. 6 months\n3. 12 months\n4. 24 months"
            }

        except ValueError:
            return {
                'type': 'CON',
                'message': "Invalid amount\n\nEnter loan amount:"
            }

    def _handle_tenure_input(self, session_id: str, tenure_choice: str) -> Dict:
        """Handle tenure selection"""
        session = self.sessions[session_id]

        tenure_map = {
            '1': 3,
            '2': 6,
            '3': 12,
            '4': 24
        }

        if tenure_choice not in tenure_map:
            return {
                'type': 'CON',
                'message': "Invalid choice\n\nSelect duration:\n1. 3 months\n2. 6 months\n3. 12 months\n4. 24 months"
            }

        tenure = tenure_map[tenure_choice]
        session['data']['tenure_months'] = tenure
        session['state'] = USSDSessionState.CONFIRM

        # Calculate estimated monthly payment
        amount = session['data']['loan_amount']
        interest_rate = 0.225  # 22.5% annual
        monthly_rate = interest_rate / 12
        monthly_payment = amount * monthly_rate * (1 + monthly_rate) ** tenure / \
                         ((1 + monthly_rate) ** tenure - 1)

        session['data']['monthly_payment'] = monthly_payment

        message = (
            f"Confirm Application:\n\n"
            f"Amount: N{amount:,.0f}\n"
            f"Duration: {tenure} months\n"
            f"Monthly: N{monthly_payment:,.0f}\n\n"
            f"1. Confirm\n"
            f"2. Cancel"
        )

        return {
            'type': 'CON',
            'message': message
        }

    def _handle_confirmation(self, session_id: str, choice: str) -> Dict:
        """Handle loan confirmation"""
        session = self.sessions[session_id]

        if choice == "1":
            # Confirm and submit application
            application_id = f"USSD_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # In production, submit to actual system
            # result = submit_loan_application(session['data'])

            message = (
                f"Application Submitted!\n\n"
                f"Reference: {application_id}\n\n"
                f"You will receive an SMS with the decision within 24 hours."
            )

            return {
                'type': 'END',
                'message': message
            }

        else:
            # Cancel
            return {
                'type': 'END',
                'message': "Application cancelled"
            }

    def _check_loan_status(self, session_id: str) -> Dict:
        """Check loan status"""
        session = self.sessions[session_id]
        phone = session['phone_number']

        # In production, look up actual status
        # status = get_loan_status(phone)

        message = (
            "Loan Status:\n\n"
            "Application ID: USSD20240315001\n"
            "Status: APPROVED\n"
            "Amount: N2,500,000\n"
            "Next Payment: N240,000\n"
            "Due: 01-Apr-2024"
        )

        return {
            'type': 'END',
            'message': message
        }

    def _show_payment_instructions(self, session_id: str) -> Dict:
        """Show payment instructions"""
        message = (
            "Payment Instructions:\n\n"
            "Bank: GTBank\n"
            "Account: 0123456789\n"
            "Account Name: Credit Risk Engine\n\n"
            "Use your phone number as reference"
        )

        return {
            'type': 'END',
            'message': message
        }

    def _check_balance(self, session_id: str) -> Dict:
        """Check loan balance"""
        message = (
            "Loan Balance:\n\n"
            "Outstanding: N1,980,000\n"
            "Paid: N520,000\n"
            "Remaining: 10/12 payments\n"
            "Next due: N240,000 on 01-Apr-2024"
        )

        return {
            'type': 'END',
            'message': message
        }


# Example usage
if __name__ == "__main__":
    ussd = USSDIntegration(shortcode="*347#")

    # Simulate USSD session
    print("=== USSD Loan Application ===\n")

    # User dials *347#
    response = ussd.handle_ussd_request(
        session_id="SESSION_001",
        phone_number="2348031234567",
        text=""
    )
    print(f"Response: {response['message']}\n")

    # User selects 1 (Apply for loan)
    response = ussd.handle_ussd_request(
        session_id="SESSION_001",
        phone_number="2348031234567",
        text="1"
    )
    print(f"Response: {response['message']}\n")

    # User enters BVN
    response = ussd.handle_ussd_request(
        session_id="SESSION_001",
        phone_number="2348031234567",
        text="12345678901"
    )
    print(f"Response: {response['message']}\n")
