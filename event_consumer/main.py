import time
import asyncio
import logging
from prometheus_client import Counter, start_http_server

from config.config import (
    get_settings, 
    create_consumer, 
    create_dlq_producer, 
    init_tracer,
    get_conn,
    ensure_table
)
from utils import process_batch

settings = get_settings()

logger = logging.getLogger("consumer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

consumer_lag = Counter("consumer_lag_total", "Consumer lag samples (approx)")

tracer = init_tracer(settings, service_name="event-consumer")


async def main():
    start_http_server(settings.METRICS_PORT)
    logger.info("metrics available on %s", settings.METRICS_PORT)

    consumer = create_consumer(settings)
    
    with get_conn() as conn:
        ensure_table(conn)

    batch = []
    batch_size = settings.BATCH_SIZE
    batch_timeout = settings.BATCH_TIMEOUT
    last_flush = time.time()

    dlq_producer = create_dlq_producer(settings)

    async def _process_batch_with_retry(batch_to_proc):
        """Process batch with async retry logic."""
        for attempt in range(3):
            try:
                await process_batch(batch_to_proc, get_conn)
                return
            except Exception as e:
                if attempt == 2:  
                    logger.exception("batch processing failed after retries, sending to DLQ: %s", e)
                    for failed_msg in batch_to_proc:
                        try:
                            payload = failed_msg.value.decode() if isinstance(failed_msg.value, (bytes, bytearray)) else failed_msg.value
                            dlq_producer.send(settings.KAFKA_TOPIC + "-dlq", payload)
                        except Exception:
                            logger.exception("failed to send to dlq")
                else:
                    wait_time = 2 ** attempt  
                    logger.warning(f"batch processing failed (attempt {attempt + 1}), retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)

    try:
        while True:
            for msg in consumer:
                batch.append(msg)
                consumer_lag.inc()
                now = time.time()
                if len(batch) >= batch_size or (now - last_flush) >= batch_timeout:
                    await _process_batch_with_retry(batch)
                    batch = []
                    last_flush = now
            
            if batch:
                await _process_batch_with_retry(batch)
                batch = []
            
            await asyncio.sleep(0.1) 
            
    except KeyboardInterrupt:
        logger.info("shutting down consumer")
    finally:
        consumer.close()
        dlq_producer.flush()
        dlq_producer.close()


if __name__ == "__main__":
    asyncio.run(main())
