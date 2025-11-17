"""
Early Warning System
====================

Predicts loan default BEFORE it happens, enabling proactive interventions.

Monitors:
- Repayment pattern changes
- Income fluctuations
- Account activity anomalies
- External economic factors
- Behavioral changes

Enables:
- Proactive customer outreach
- Loan restructuring offers
- Payment plan adjustments
- Loss prevention
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


class EarlyWarningSystem:
    """
    Early warning system for predicting imminent loan defaults.
    """

    def __init__(self):
        """Initialize early warning system."""
        self.risk_thresholds = {
            'LOW': 0.3,
            'MEDIUM': 0.5,
            'HIGH': 0.7,
            'CRITICAL': 0.9
        }

    def assess_loan_health(self, loan_data: Dict) -> Dict:
        """
        Assess health of an active loan.

        Args:
            loan_data: Current loan information

        Returns:
            Early warning assessment
        """
        warning_score = 0
        warning_signals = []

        # 1. Payment Pattern Analysis
        payment_signal = self._check_payment_patterns(loan_data)
        warning_score += payment_signal['score']
        if payment_signal['warning']:
            warning_signals.extend(payment_signal['signals'])

        # 2. Account Activity
        activity_signal = self._check_account_activity(loan_data)
        warning_score += activity_signal['score']
        if activity_signal['warning']:
            warning_signals.extend(activity_signal['signals'])

        # 3. Income Stability
        income_signal = self._check_income_stability(loan_data)
        warning_score += income_signal['score']
        if income_signal['warning']:
            warning_signals.extend(income_signal['signals'])

        # 4. External Factors
        external_signal = self._check_external_factors(loan_data)
        warning_score += external_signal['score']
        if external_signal['warning']:
            warning_signals.extend(external_signal['signals'])

        # Calculate risk level
        risk_level = self._get_risk_level(warning_score)

        # Generate recommendation
        recommendation = self._generate_recommendation(risk_level, warning_signals)

        return {
            'loan_id': loan_data.get('loan_id'),
            'customer_name': loan_data.get('customer_name'),
            'warning_score': warning_score,
            'risk_level': risk_level,
            'default_probability_3_months': self._predict_default_probability(warning_score),
            'warning_signals': warning_signals,
            'recommendation': recommendation,
            'action_required': risk_level in ['HIGH', 'CRITICAL'],
            'suggested_intervention': self._suggest_intervention(risk_level)
        }

    def _check_payment_patterns(self, loan_data: Dict) -> Dict:
        """Analyze payment pattern changes."""
        score = 0
        signals = []

        payment_history = loan_data.get('payment_history', [])

        if not payment_history:
            return {'score': 0, 'warning': False, 'signals': []}

        # Late payments increasing
        recent_late = sum(1 for p in payment_history[-3:] if p.get('days_late', 0) > 0)
        if recent_late >= 2:
            score += 30
            signals.append('Multiple late payments in last 3 months')

        # Payment amount decreasing
        recent_payments = [p.get('amount', 0) for p in payment_history[-3:]]
        if len(recent_payments) >= 2 and all(recent_payments[i] > recent_payments[i+1] for i in range(len(recent_payments)-1)):
            score += 20
            signals.append('Decreasing payment amounts')

        # Missed payments
        missed = sum(1 for p in payment_history[-6:] if p.get('status') == 'missed')
        if missed > 0:
            score += 40
            signals.append(f'{missed} missed payment(s) in last 6 months')

        return {
            'score': score,
            'warning': score > 0,
            'signals': signals
        }

    def _check_account_activity(self, loan_data: Dict) -> Dict:
        """Check for suspicious account activity."""
        score = 0
        signals = []

        # Declining balance
        current_balance = loan_data.get('account_balance', 0)
        avg_balance = loan_data.get('avg_monthly_balance', 0)

        if current_balance < avg_balance * 0.3:
            score += 25
            signals.append('Account balance critically low')

        # Increased debt elsewhere
        total_debt = loan_data.get('total_outstanding_debt', 0)
        previous_debt = loan_data.get('debt_3_months_ago', 0)

        if total_debt > previous_debt * 1.5:
            score += 30
            signals.append('Significant increase in total debt')

        # Multiple bounced checks
        bounced_checks = loan_data.get('bounced_checks_6months', 0)
        if bounced_checks > 0:
            score += 20 * bounced_checks
            signals.append(f'{bounced_checks} bounced check(s)')

        return {
            'score': score,
            'warning': score > 0,
            'signals': signals
        }

    def _check_income_stability(self, loan_data: Dict) -> Dict:
        """Check income stability."""
        score = 0
        signals = []

        # Income decreased
        current_income = loan_data.get('current_monthly_income', 0)
        initial_income = loan_data.get('income_at_application', 0)

        if current_income < initial_income * 0.7:
            score += 35
            signals.append('Income declined by >30%')

        # Irregular income pattern
        income_history = loan_data.get('income_history_6months', [])
        if income_history and len(income_history) >= 3:
            income_std = np.std(income_history)
            income_mean = np.mean(income_history)

            if income_mean > 0 and (income_std / income_mean) > 0.3:
                score += 20
                signals.append('Highly irregular income pattern')

        # Job loss
        if loan_data.get('employment_status') != 'employed':
            score += 50
            signals.append('⚠️ JOB LOSS DETECTED')

        return {
            'score': score,
            'warning': score > 0,
            'signals': signals
        }

    def _check_external_factors(self, loan_data: Dict) -> Dict:
        """Check external economic factors."""
        score = 0
        signals = []

        # Sector-specific risks (e.g., oil price crash affects Oil & Gas workers)
        sector = loan_data.get('employment_sector', '')

        if sector == 'Oil & Gas':
            # Mock: check if oil prices declining
            oil_price_declining = False  # Would fetch real data
            if oil_price_declining:
                score += 15
                signals.append('Sector risk: Oil prices declining')

        # Geographic risks
        state = loan_data.get('state', '')
        # Mock: check for economic issues in state
        # Would integrate with economic data APIs

        # Naira devaluation impact
        forex_exposure = loan_data.get('forex_exposure', False)
        if forex_exposure:
            score += 10
            signals.append('Currency risk: Naira volatility')

        return {
            'score': score,
            'warning': score > 0,
            'signals': signals
        }

    def _get_risk_level(self, score: int) -> str:
        """Map warning score to risk level."""
        if score < 30:
            return 'LOW'
        elif score < 60:
            return 'MEDIUM'
        elif score < 90:
            return 'HIGH'
        else:
            return 'CRITICAL'

    def _predict_default_probability(self, warning_score: int) -> float:
        """Predict probability of default in next 3 months."""
        # Logistic-like transformation
        return 1 / (1 + np.exp(-0.05 * (warning_score - 50)))

    def _generate_recommendation(self, risk_level: str, signals: List[str]) -> str:
        """Generate recommendation based on risk."""
        if risk_level == 'CRITICAL':
            return "IMMEDIATE ACTION REQUIRED: High risk of default. Contact customer immediately."
        elif risk_level == 'HIGH':
            return "URGENT: Schedule customer meeting to discuss loan status."
        elif risk_level == 'MEDIUM':
            return "MONITOR CLOSELY: Proactive outreach recommended."
        else:
            return "Continue normal monitoring."

    def _suggest_intervention(self, risk_level: str) -> Dict:
        """Suggest intervention strategies."""
        interventions = {
            'CRITICAL': {
                'actions': [
                    'Immediate phone call to customer',
                    'Offer loan restructuring',
                    'Discuss payment holiday option',
                    'Escalate to collections team'
                ],
                'priority': 'P0 - Immediate',
                'timeline': '24 hours'
            },
            'HIGH': {
                'actions': [
                    'Schedule customer meeting',
                    'Review financial situation',
                    'Offer payment plan adjustment',
                    'Provide financial counseling'
                ],
                'priority': 'P1 - Urgent',
                'timeline': '3-5 days'
            },
            'MEDIUM': {
                'actions': [
                    'Send payment reminder SMS',
                    'Offer WhatsApp check-in',
                    'Monitor for 2 weeks'
                ],
                'priority': 'P2 - High',
                'timeline': '1-2 weeks'
            },
            'LOW': {
                'actions': [
                    'Continue routine monitoring'
                ],
                'priority': 'P3 - Normal',
                'timeline': 'Monthly review'
            }
        }

        return interventions.get(risk_level, interventions['LOW'])

    def generate_report(self, assessment: Dict) -> str:
        """Generate early warning report."""
        report = f"""
{'='*70}
  EARLY WARNING SYSTEM REPORT
{'='*70}

LOAN INFORMATION
{'-'*70}
  Loan ID:           {assessment['loan_id']}
  Customer:          {assessment['customer_name']}

RISK ASSESSMENT
{'-'*70}
  Warning Score:     {assessment['warning_score']}/100
  Risk Level:        {assessment['risk_level']}
  Default Prob (3mo): {assessment['default_probability_3_months']:.1%}
  Action Required:   {'YES ⚠️' if assessment['action_required'] else 'NO'}

WARNING SIGNALS
{'-'*70}
"""

        if assessment['warning_signals']:
            for i, signal in enumerate(assessment['warning_signals'], 1):
                report += f"  {i}. {signal}\n"
        else:
            report += "  None ✓\n"

        intervention = assessment['suggested_intervention']
        report += f"""
RECOMMENDED INTERVENTION
{'-'*70}
  Priority:          {intervention['priority']}
  Timeline:          {intervention['timeline']}

  Actions:
"""

        for action in intervention['actions']:
            report += f"  • {action}\n"

        report += f"\n{'='*70}\n"

        return report


def main():
    """Demo early warning system."""
    print("\n" + "="*70)
    print(" "*20 + "EARLY WARNING SYSTEM DEMO")
    print("="*70)

    ews = EarlyWarningSystem()

    # Test loan with warning signals
    test_loan = {
        'loan_id': 'LN20240101',
        'customer_name': 'Adebayo Ogunleye',
        'payment_history': [
            {'amount': 100_000, 'days_late': 0, 'status': 'paid'},
            {'amount': 100_000, 'days_late': 5, 'status': 'paid'},
            {'amount': 80_000, 'days_late': 10, 'status': 'paid'},
            {'amount': 0, 'days_late': 0, 'status': 'missed'},
        ],
        'account_balance': 50_000,
        'avg_monthly_balance': 300_000,
        'total_outstanding_debt': 2_000_000,
        'debt_3_months_ago': 1_000_000,
        'current_monthly_income': 300_000,
        'income_at_application': 500_000,
        'employment_status': 'employed',
        'employment_sector': 'Oil & Gas',
        'state': 'Lagos'
    }

    # Assess
    assessment = ews.assess_loan_health(test_loan)

    # Print report
    report = ews.generate_report(assessment)
    print(report)

    print("✓ Early Warning System Implemented")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
