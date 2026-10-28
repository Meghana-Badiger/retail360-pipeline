"""
kafka_consumer.py
─────────────────
Reads real-time order events from Kafka topic "orders"
and processes them as they arrive.

This is the CONSUMER — it reads and processes messages.

Run: python ingestion/kafka_consumer.py
"""

import json
from kafka import KafkaConsumer

# ── Connect to Kafka and subscribe to "orders" topic ─────────
consumer = KafkaConsumer(
    "orders",                              # topic to read from
    bootstrap_servers=['localhost:9092'],   # Kafka in Docker
    auto_offset_reset='earliest',          # read from beginning
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    # value_deserializer converts bytes → JSON → Python dict
)


def main():
    print("👂 Kafka Consumer started — listening for orders...")
    print("   Press Ctrl+C to stop\n")

    total_revenue = 0
    order_count   = 0

    for message in consumer:
        order = message.value   # the actual order dict

        # Calculate revenue for this order
        revenue = order['quantity'] * order['unit_price']
        total_revenue += revenue
        order_count   += 1

        print(f"✅ Received order #{order_count}")
        print(f"   Category : {order['category']}")
        print(f"   Product  : {order['product']}")
        print(f"   Quantity : {order['quantity']}")
        print(f"   Price    : ${order['unit_price']}")
        print(f"   Revenue  : ${round(revenue, 2)}")
        print(f"   Status   : {order['status']}")
        print(f"   Time     : {order['order_time']}")
        print(f"   💰 Total revenue so far: ${round(total_revenue, 2)}")
        print("-" * 50)


if __name__ == "__main__":
    main()