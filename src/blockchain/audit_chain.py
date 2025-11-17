"""
Blockchain Audit Trail

Immutable record of all credit decisions and model changes.
Each block contains loan decisions, timestamps, and cryptographic hashes.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import pickle
import os


@dataclass
class Block:
    """Individual block in the blockchain"""
    index: int
    timestamp: str
    data: Dict[str, Any]
    previous_hash: str
    hash: str
    nonce: int = 0

    def to_dict(self) -> Dict:
        """Convert block to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert block to JSON"""
        return json.dumps(self.to_dict(), indent=2, default=str)


class BlockchainAuditTrail:
    """
    Blockchain-based audit trail for credit decisions.

    Features:
    - Immutable record of all decisions
    - Cryptographic verification
    - Tamper detection
    - Regulatory compliance
    - Model version tracking
    """

    def __init__(self, chain_file: str = "data/blockchain/credit_audit_chain.pkl"):
        """
        Initialize blockchain audit trail

        Args:
            chain_file: Path to store blockchain data
        """
        self.chain_file = chain_file
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []

        # Create directory if needed
        os.makedirs(os.path.dirname(chain_file), exist_ok=True)

        # Load existing chain or create genesis block
        if os.path.exists(chain_file):
            self.load_chain()
        else:
            self.create_genesis_block()

    def create_genesis_block(self) -> Block:
        """Create the first block in the chain"""
        genesis_data = {
            'type': 'GENESIS',
            'message': 'Nigerian Credit Risk Engine - Blockchain Audit Trail',
            'created_by': 'System',
            'cbn_compliance': 'Enabled',
            'version': '1.0'
        }

        genesis_block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            data=genesis_data,
            previous_hash="0",
            hash="",
            nonce=0
        )

        genesis_block.hash = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)
        self.save_chain()

        return genesis_block

    def calculate_hash(self, block: Block) -> str:
        """
        Calculate SHA-256 hash of block

        Args:
            block: Block to hash

        Returns:
            Hexadecimal hash string
        """
        block_string = json.dumps({
            'index': block.index,
            'timestamp': block.timestamp,
            'data': block.data,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce
        }, sort_keys=True, default=str)

        return hashlib.sha256(block_string.encode()).hexdigest()

    def add_block(self, data: Dict[str, Any], proof_of_work: bool = False) -> Block:
        """
        Add new block to the chain

        Args:
            data: Data to store in block
            proof_of_work: Whether to use proof-of-work (slower but more secure)

        Returns:
            Newly created block
        """
        previous_block = self.chain[-1]

        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now().isoformat(),
            data=data,
            previous_hash=previous_block.hash,
            hash="",
            nonce=0
        )

        if proof_of_work:
            new_block = self.proof_of_work(new_block)
        else:
            new_block.hash = self.calculate_hash(new_block)

        self.chain.append(new_block)
        self.save_chain()

        return new_block

    def proof_of_work(self, block: Block, difficulty: int = 4) -> Block:
        """
        Proof of work algorithm (mining)

        Args:
            block: Block to mine
            difficulty: Number of leading zeros required

        Returns:
            Block with valid hash
        """
        target = "0" * difficulty

        while True:
            block.hash = self.calculate_hash(block)

            if block.hash.startswith(target):
                return block

            block.nonce += 1

    def is_chain_valid(self) -> bool:
        """
        Verify integrity of blockchain

        Returns:
            True if chain is valid, False if tampered
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check if current block's hash is correct
            if current_block.hash != self.calculate_hash(current_block):
                return False

            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def record_loan_decision(self, application_id: str, decision_data: Dict) -> Block:
        """
        Record loan decision on blockchain

        Args:
            application_id: Unique application identifier
            decision_data: Decision details

        Returns:
            Block containing the decision
        """
        data = {
            'type': 'LOAN_DECISION',
            'application_id': application_id,
            'timestamp': datetime.now().isoformat(),
            'decision': decision_data.get('decision'),
            'default_probability': decision_data.get('default_probability'),
            'risk_category': decision_data.get('risk_category'),
            'model_version': decision_data.get('model_version', '1.0'),
            'loan_amount': decision_data.get('loan_amount'),
            'approved_amount': decision_data.get('approved_amount'),
            'interest_rate': decision_data.get('interest_rate'),
            'decision_maker': decision_data.get('decision_maker', 'ML_MODEL'),
            'override': decision_data.get('manual_override', False),
            'override_reason': decision_data.get('override_reason')
        }

        return self.add_block(data)

    def record_model_update(self, model_info: Dict) -> Block:
        """
        Record model update/retraining event

        Args:
            model_info: Model update details

        Returns:
            Block containing model update info
        """
        data = {
            'type': 'MODEL_UPDATE',
            'timestamp': datetime.now().isoformat(),
            'model_version': model_info.get('model_version'),
            'model_type': model_info.get('model_type'),
            'training_date': model_info.get('training_date'),
            'performance_metrics': model_info.get('metrics'),
            'training_data_size': model_info.get('data_size'),
            'feature_count': model_info.get('feature_count'),
            'deployed_by': model_info.get('deployed_by', 'System')
        }

        return self.add_block(data)

    def record_fraud_alert(self, fraud_data: Dict) -> Block:
        """
        Record fraud detection alert

        Args:
            fraud_data: Fraud alert details

        Returns:
            Block containing fraud alert
        """
        data = {
            'type': 'FRAUD_ALERT',
            'timestamp': datetime.now().isoformat(),
            'application_id': fraud_data.get('application_id'),
            'fraud_score': fraud_data.get('fraud_score'),
            'indicators': fraud_data.get('indicators'),
            'action_taken': fraud_data.get('action'),
            'bvn': fraud_data.get('bvn'),
            'device_id': fraud_data.get('device_id')
        }

        return self.add_block(data)

    def record_compliance_event(self, compliance_data: Dict) -> Block:
        """
        Record compliance/regulatory event

        Args:
            compliance_data: Compliance event details

        Returns:
            Block containing compliance record
        """
        data = {
            'type': 'COMPLIANCE',
            'timestamp': datetime.now().isoformat(),
            'event_type': compliance_data.get('event_type'),
            'regulation': compliance_data.get('regulation'),
            'status': compliance_data.get('status'),
            'details': compliance_data.get('details'),
            'auditor': compliance_data.get('auditor')
        }

        return self.add_block(data)

    def get_application_history(self, application_id: str) -> List[Block]:
        """
        Get all blockchain records for an application

        Args:
            application_id: Application ID

        Returns:
            List of blocks related to this application
        """
        history = []

        for block in self.chain:
            if block.data.get('application_id') == application_id:
                history.append(block)

        return history

    def get_model_history(self) -> List[Block]:
        """
        Get all model update records

        Returns:
            List of blocks with model updates
        """
        return [block for block in self.chain if block.data.get('type') == 'MODEL_UPDATE']

    def get_fraud_alerts(self, days: int = 30) -> List[Block]:
        """
        Get recent fraud alerts

        Args:
            days: Number of days to look back

        Returns:
            List of fraud alert blocks
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)

        fraud_blocks = []
        for block in self.chain:
            if block.data.get('type') == 'FRAUD_ALERT':
                block_time = datetime.fromisoformat(block.timestamp)
                if block_time >= cutoff:
                    fraud_blocks.append(block)

        return fraud_blocks

    def generate_audit_report(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        Generate audit report for date range

        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)

        Returns:
            Comprehensive audit report
        """
        # Filter blocks by date
        blocks = self.chain

        if start_date:
            start = datetime.fromisoformat(start_date)
            blocks = [b for b in blocks if datetime.fromisoformat(b.timestamp) >= start]

        if end_date:
            end = datetime.fromisoformat(end_date)
            blocks = [b for b in blocks if datetime.fromisoformat(b.timestamp) <= end]

        # Count by type
        type_counts = {}
        for block in blocks:
            block_type = block.data.get('type', 'UNKNOWN')
            type_counts[block_type] = type_counts.get(block_type, 0) + 1

        # Loan decisions
        loan_decisions = [b for b in blocks if b.data.get('type') == 'LOAN_DECISION']
        approved = sum(1 for b in loan_decisions if b.data.get('decision') == 'APPROVE')
        rejected = sum(1 for b in loan_decisions if b.data.get('decision') == 'REJECT')

        # Fraud alerts
        fraud_alerts = [b for b in blocks if b.data.get('type') == 'FRAUD_ALERT']

        return {
            'period': {
                'start': start_date or 'beginning',
                'end': end_date or 'present'
            },
            'total_blocks': len(blocks),
            'block_types': type_counts,
            'loan_decisions': {
                'total': len(loan_decisions),
                'approved': approved,
                'rejected': rejected,
                'approval_rate': f"{approved/len(loan_decisions)*100:.1f}%" if loan_decisions else "N/A"
            },
            'fraud_alerts': len(fraud_alerts),
            'model_updates': len([b for b in blocks if b.data.get('type') == 'MODEL_UPDATE']),
            'chain_integrity': 'VALID' if self.is_chain_valid() else 'COMPROMISED',
            'last_block_hash': self.chain[-1].hash if self.chain else None
        }

    def save_chain(self):
        """Save blockchain to disk"""
        with open(self.chain_file, 'wb') as f:
            pickle.dump(self.chain, f)

    def load_chain(self):
        """Load blockchain from disk"""
        with open(self.chain_file, 'rb') as f:
            self.chain = pickle.load(f)

    def export_to_json(self, output_file: str):
        """
        Export blockchain to JSON for auditing

        Args:
            output_file: Path to output JSON file
        """
        chain_data = [block.to_dict() for block in self.chain]

        with open(output_file, 'w') as f:
            json.dump(chain_data, f, indent=2, default=str)

    def __len__(self) -> int:
        """Return number of blocks"""
        return len(self.chain)

    def __getitem__(self, index: int) -> Block:
        """Get block by index"""
        return self.chain[index]


# Example usage
if __name__ == "__main__":
    # Initialize blockchain
    blockchain = BlockchainAuditTrail()

    print(f"Blockchain initialized with {len(blockchain)} blocks")
    print(f"Chain valid: {blockchain.is_chain_valid()}")

    # Record a loan decision
    decision = blockchain.record_loan_decision(
        application_id="NGN20240315001",
        decision_data={
            'decision': 'APPROVE',
            'default_probability': 0.12,
            'risk_category': 'MEDIUM',
            'loan_amount': 2_500_000,
            'approved_amount': 2_500_000,
            'interest_rate': 22.5
        }
    )

    print(f"\nDecision recorded in block #{decision.index}")
    print(f"Block hash: {decision.hash}")

    # Generate audit report
    report = blockchain.generate_audit_report()
    print("\nAudit Report:")
    print(json.dumps(report, indent=2))
