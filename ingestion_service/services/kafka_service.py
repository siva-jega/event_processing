import json
import logging
from aiokafka import AIOKafkaProducer

from config.config import get_settings

settings = get_settings()
logger = logging.getLogger("ingestion")


class KafkaService:
    """Singleton service for Kafka operations."""

    _instance = None
    _producer: AIOKafkaProducer | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def set_producer(cls, prod: AIOKafkaProducer):
        """Set the Kafka producer instance."""
        cls._producer = prod

    @classmethod
    async def send_event_to_kafka(cls, payload: dict):
        """Send message to Kafka without waiting for confirmation."""
        try:
            if cls._producer is None:
                logger.warning("producer not ready")
                return
            fut = cls._producer.send_and_wait(settings.KAFKA_TOPIC, json.dumps(payload).encode("utf-8"))
            await fut
        except Exception:
            logger.exception("failed to send message to kafka")


# Global instance for convenience
kafka_service = KafkaService()