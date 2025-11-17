"""
Blockchain Integration Module

Provides immutable audit trails and smart contract enforcement
for credit risk decisions.
"""

from .audit_chain import BlockchainAuditTrail, Block
from .smart_contracts import LoanContract, SmartContractEngine

__all__ = [
    'BlockchainAuditTrail',
    'Block',
    'LoanContract',
    'SmartContractEngine'
]
