"""
Kafka Producer for Credit Risk Events
"""

import json
from typing import Dict
from datetime import datetime


class CreditRiskKafkaProducer:
    """Kafka producer for publishing credit risk events"""
    
    def __init__(self, bootstrap_servers=None):
        self.bootstrap_servers = bootstrap_servers or ['localhost:9092']
        self.producer = None
    
    def connect(self):
        """Connect to Kafka cluster"""
        # from kafka import KafkaProducer
        # self.producer = KafkaProducer(
        #     bootstrap_servers=self.bootstrap_servers,
        #     value_serializer=lambda v: json.dumps(v).encode('utf-8')
        # )
        print(f"Producer connected to Kafka: {self.bootstrap_servers}")
        return True
    
    def publish_credit_decision(self, decision: Dict):
        """Publish credit decision event"""
        event = {
            'event_type': 'credit_decision',
            'timestamp': datetime.now().isoformat(),
            'data': decision
        }
        # self.producer.send('credit_decisions', value=event)
        print(f"Published decision: {decision.get('application_id')}")
        return event
    
    def publish_fraud_alert(self, alert: Dict):
        """Publish fraud alert event"""
        event = {
            'event_type': 'fraud_alert',
            'timestamp': datetime.now().isoformat(),
            'data': alert
        }
        # self.producer.send('fraud_alerts', value=event)
        print(f"Published fraud alert: {alert.get('application_id')}")
        return event
    
    def close(self):
        """Close producer connection"""
        if self.producer:
            # self.producer.flush()
            # self.producer.close()
            print("Kafka producer closed")


if __name__ == "__main__":
    producer = CreditRiskKafkaProducer()
    producer.connect()
    
    decision = {
        'application_id': 'NGN001',
        'decision': 'APPROVE',
        'loan_amount': 2_500_000
    }
    producer.publish_credit_decision(decision)
