import json
from kafka import KafkaConsumer, KafkaProducer


def create_consumer(settings) -> KafkaConsumer:
    """Create and return a configured KafkaConsumer using provided settings."""
    return KafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=[settings.KAFKA_SERVER],
        group_id=settings.KAFKA_GROUP,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        consumer_timeout_ms=1000,
        value_deserializer=lambda v: v.decode() if isinstance(v, (bytes, bytearray)) else v,
    )


def create_dlq_producer(settings) -> KafkaProducer:
    """Create a KafkaProducer for DLQ messages."""
    return KafkaProducer(bootstrap_servers=[settings.KAFKA_SERVER], value_serializer=lambda v: json.dumps(v).encode("utf-8"))
