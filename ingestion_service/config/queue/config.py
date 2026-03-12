from aiokafka import AIOKafkaProducer
import logging

logger = logging.getLogger("ingestion")


async def init_kafka_producer(settings, kafka_service):
    """Initialize Kafka producer and inject into kafka_service.
    
    Args:
        settings: Settings object with Kafka configuration
        kafka_service: KafkaService singleton instance
        
    Returns:
        AIOKafkaProducer: Started producer instance
    """
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_SERVER)
    await producer.start()
    kafka_service.set_producer(producer)
    logger.info("aiokafka producer started")
    return producer
