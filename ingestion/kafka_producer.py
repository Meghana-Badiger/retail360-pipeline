"""
kafka_producer.py
─────────────────
Simulates real-time order events by sending fake orders
to a Kafka topic every 2 seconds.

This is the PRODUCER — it generates and sends messages.

Run: python ingestion/kafka_producer.py
"""

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

fake = Faker()
random.seed(42)

# ── Connect to Kafka ──────────────────────────────────────────
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  # Kafka is running in Docker
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
    # value_serializer converts Python dict → JSON → bytes
    # Kafka only understands bytes, not Python objects
)

CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys"]
STATUSES   = ["completed", "completed", "completed", "pending", "cancelled"]

def generate_order():
    """Generates one fake order event."""
    return {
        "order_id":    fake.uuid4(),
        "customer_id": fake.uuid4(),
        "product":     fake.catch_phrase(),
        "category":    random.choice(CATEGORIES),
        "quantity":    random.randint(1, 10),
        "unit_price":  round(random.uniform(5, 500), 2),
        "status":      random.choice(STATUSES),
        "order_time":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    print("🚀 Kafka Producer started — sending orders every 2 seconds")
    print("   Press Ctrl+C to stop\n")

    count = 0
    while True:
        order = generate_order()

        # Send to Kafka topic called "orders"
        producer.send("orders", value=order)

        count += 1
        print(f"📦 Order #{count} sent → {order['category']} | "
              f"${order['unit_price']} | {order['status']}")

        time.sleep(2)  # wait 2 seconds before sending next order


if __name__ == "__main__":
    main()