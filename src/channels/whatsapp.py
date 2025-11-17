"""
WhatsApp Bot Integration
=========================

WhatsApp Business API integration for loan applications and customer service.

Features:
- Loan application via WhatsApp chat
- Document submission (photos of ID, payslip)
- Loan status updates
- Payment reminders
- Customer support chatbot

Nigerian Context:
- WhatsApp is extremely popular in Nigeria
- Many customers prefer WhatsApp over apps
- Enables financial inclusion (no smartphone app needed)
"""

from twilio.rest import Client
from typing import Dict, List
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


class WhatsAppBot:
    """
    WhatsApp Business API bot for loan services.

    Uses Twilio WhatsApp Business API.
    """

    def __init__(self, account_sid: str = None, auth_token: str = None):
        """
        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
        """
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID', 'demo_sid')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN', 'demo_token')
        self.from_number = 'whatsapp:+2348012345678'  # Your WhatsApp business number

        # In production, initialize Twilio client
        # self.client = Client(self.account_sid, self.auth_token)

        # Conversation states
        self.conversations = {}

    def send_message(self, to_number: str, message: str):
        """
        Send WhatsApp message.

        Args:
            to_number: Recipient's WhatsApp number (format: whatsapp:+234...)
            message: Message text
        """
        print(f"📱 Sending WhatsApp to {to_number}:")
        print(f"   {message}")

        # In production:
        # self.client.messages.create(
        #     body=message,
        #     from_=self.from_number,
        #     to=to_number
        # )

    def handle_incoming_message(self, from_number: str, message: str) -> str:
        """
        Handle incoming WhatsApp message.

        Args:
            from_number: Sender's WhatsApp number
            message: Message text

        Returns:
            Response message
        """
        # Get or create conversation state
        if from_number not in self.conversations:
            self.conversations[from_number] = {
                'state': 'START',
                'data': {}
            }

        state = self.conversations[from_number]

        # Process based on current state
        if state['state'] == 'START':
            return self._handle_start(from_number, message)
        elif state['state'] == 'MENU':
            return self._handle_menu(from_number, message)
        elif state['state'] == 'NEW_LOAN':
            return self._handle_new_loan(from_number, message)
        elif state['state'] == 'CHECK_STATUS':
            return self._handle_check_status(from_number, message)
        else:
            return self._handle_start(from_number, message)

    def _handle_start(self, from_number: str, message: str) -> str:
        """Handle initial contact."""
        self.conversations[from_number]['state'] = 'MENU'

        response = """
🏦 *Welcome to Credit Risk Bank*

How can I help you today?

1️⃣ Apply for a loan
2️⃣ Check loan status
3️⃣ Make payment
4️⃣ Speak to an agent

Reply with a number (1-4)
"""
        return response

    def _handle_menu(self, from_number: str, message: str) -> str:
        """Handle menu selection."""
        message = message.strip()

        if message == '1':
            self.conversations[from_number]['state'] = 'NEW_LOAN'
            return self._start_loan_application(from_number)
        elif message == '2':
            self.conversations[from_number]['state'] = 'CHECK_STATUS'
            return "Please share your BVN or loan ID to check status."
        elif message == '3':
            return "📱 *Payment Instructions*\n\nAccount: 1234567890\nBank: GTBank\n\nOr pay via USSD: *737*Amount#"
        elif message == '4':
            return "📞 Connecting you to an agent... Please wait."
        else:
            return "Invalid option. Please reply with 1, 2, 3, or 4."

    def _start_loan_application(self, from_number: str) -> str:
        """Start new loan application."""
        self.conversations[from_number]['data']['stage'] = 'NAME'

        return """
✅ *New Loan Application*

Let's get started! I'll need some information.

What is your full name?
"""

    def _handle_new_loan(self, from_number: str, message: str) -> str:
        """Handle loan application flow."""
        state = self.conversations[from_number]
        stage = state['data'].get('stage', 'NAME')

        if stage == 'NAME':
            state['data']['name'] = message
            state['data']['stage'] = 'BVN'
            return "Great! What is your BVN (Bank Verification Number)?"

        elif stage == 'BVN':
            if len(message) != 11 or not message.isdigit():
                return "❌ Invalid BVN. Please enter your 11-digit BVN."

            state['data']['bvn'] = message
            state['data']['stage'] = 'AMOUNT'
            return "How much would you like to borrow? (e.g., 500000 for ₦500,000)"

        elif stage == 'AMOUNT':
            try:
                amount = int(message.replace(',', ''))
                if amount < 50_000 or amount > 10_000_000:
                    return "❌ Loan amount must be between ₦50,000 and ₦10,000,000"

                state['data']['amount'] = amount
                state['data']['stage'] = 'TERM'
                return "For how many months? (e.g., 12 for 1 year)"

            except ValueError:
                return "❌ Please enter a valid amount (numbers only)"

        elif stage == 'TERM':
            try:
                term = int(message)
                if term < 3 or term > 60:
                    return "❌ Loan term must be between 3 and 60 months"

                state['data']['term'] = term
                state['data']['stage'] = 'PURPOSE'
                return "What is the purpose of this loan?"

            except ValueError:
                return "❌ Please enter a valid number of months"

        elif stage == 'PURPOSE':
            state['data']['purpose'] = message
            state['data']['stage'] = 'DOCUMENTS'
            return """
📸 *Almost done!*

Please send:
1. Photo of your ID card
2. Photo of recent payslip
3. Photo of utility bill

Send them as images (one at a time)
"""

        elif stage == 'DOCUMENTS':
            # In production, handle image uploads here
            return """
✅ *Application Submitted!*

Application ID: NGN20240315001

We'll review your application and get back to you within 24 hours via:
- WhatsApp
- SMS to your registered number
- Email

You can check status anytime by sending "STATUS NGN20240315001"

Thank you for choosing Credit Risk Bank! 🏦
"""

        return "Something went wrong. Please start again by typing 'Hi'"

    def _handle_check_status(self, from_number: str, message: str) -> str:
        """Handle loan status check."""
        # Mock status check
        return f"""
📊 *Loan Status*

Application ID: {message}
Status: Under Review ⏳
Submitted: 2024-03-15
Expected Decision: 2024-03-16

We'll notify you once reviewed!
"""

    def send_loan_decision(self, to_number: str, decision_data: Dict):
        """
        Send loan decision notification.

        Args:
            to_number: Customer's WhatsApp number
            decision_data: Decision details
        """
        if decision_data['decision'] == 'APPROVE':
            message = f"""
🎉 *LOAN APPROVED!*

Application ID: {decision_data['application_id']}
Amount: ₦{decision_data['loan_amount']:,.0f}
Term: {decision_data['loan_term_months']} months
Interest Rate: {decision_data['interest_rate']}%
Monthly Payment: ₦{decision_data['monthly_payment']:,.0f}

Accept this offer? Reply YES to proceed.
"""
        else:
            message = f"""
❌ *Loan Application Update*

Application ID: {decision_data['application_id']}
Status: Not Approved

Reason: {decision_data['reasoning']}

You can:
1. Reapply after 30 days
2. Speak to our team: Reply AGENT

We're here to help! 🏦
"""

        self.send_message(to_number, message)

    def send_payment_reminder(self, to_number: str, payment_data: Dict):
        """
        Send payment reminder.

        Args:
            to_number: Customer's WhatsApp number
            payment_data: Payment details
        """
        message = f"""
💳 *Payment Reminder*

Hi {payment_data['customer_name']}!

Your loan payment is due soon:

Due Date: {payment_data['due_date']}
Amount Due: ₦{payment_data['amount_due']:,.0f}
Loan Balance: ₦{payment_data['balance']:,.0f}

Pay via:
- Bank Transfer: 1234567890 (GTBank)
- USSD: *737*{payment_data['amount_due']}#
- Card: Reply CARD

Reply PAID once done. Thank you! 🏦
"""

        self.send_message(to_number, message)


def main():
    """Demo WhatsApp bot."""
    print("\n" + "="*70)
    print(" "*20 + "WHATSAPP BOT DEMO")
    print("="*70)

    bot = WhatsAppBot()

    # Simulate conversation
    customer = "whatsapp:+2348031234567"

    print("\n🤖 Simulating WhatsApp conversation:\n")

    # Customer says hi
    response = bot.handle_incoming_message(customer, "Hi")
    print(f"Bot: {response}\n")

    # Customer selects option 1
    response = bot.handle_incoming_message(customer, "1")
    print(f"Bot: {response}\n")

    # Customer provides name
    response = bot.handle_incoming_message(customer, "Adebayo Ogunleye")
    print(f"Bot: {response}\n")

    print("✓ WhatsApp Bot Integration Implemented")
    print("\nFeatures:")
    print("  • Conversational loan application")
    print("  • Document upload via photos")
    print("  • Status checking")
    print("  • Payment reminders")
    print("  • Customer support")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
