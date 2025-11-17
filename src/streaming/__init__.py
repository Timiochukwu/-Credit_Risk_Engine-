"""
Streaming Data Processing Module

Real-time data streaming with Apache Kafka
"""

from .kafka_consumer import CreditRiskKafkaConsumer
from .kafka_producer import CreditRiskKafkaProducer
from .stream_processor import StreamProcessor

__all__ = ['CreditRiskKafkaConsumer', 'CreditRiskKafkaProducer', 'StreamProcessor']
