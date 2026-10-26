"""
generate_data.py
────────────────
Generates fake e-commerce data and saves as CSV files in /data folder.
This simulates the raw data source for our pipeline.

Run: python ingestion/generate_data.py
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

# ── Setup ─────────────────────────────────────────────────────
fake = Faker()
Faker.seed(42)        # seed = same data every time you run it
random.seed(42)       # makes results reproducible

OUTPUT_DIR = "data"   # where CSV files will be saved
os.makedirs(OUTPUT_DIR, exist_ok=True)  # create folder if it doesn't exist


# ── 1. Generate Customers ─────────────────────────────────────
def generate_customers(n=500):
    """
    Creates n fake customers.
    Each customer has an ID, name, email, location, signup date.
    """
    customers = []
    for _ in range(n):
        customers.append({
            "customer_id": fake.uuid4(),           # unique ID like "a3f2-..."
            "name":        fake.name(),            # "John Smith"
            "email":       fake.email(),           # "john@example.com"
            "city":        fake.city(),            # "Austin"
            "country":     fake.country(),         # "United States"
            "signup_date": fake.date_between(      # random date in last 3 years
                start_date="-3y",
                end_date="today"
            ),
        })
    return pd.DataFrame(customers)


# ── 2. Generate Products ──────────────────────────────────────
CATEGORIES = [
    "Electronics", "Clothing", "Home & Garden",
    "Sports", "Books", "Toys"
]

def generate_products(n=100):
    """
    Creates n fake products.
    Each product has an ID, name, category, cost and sell price.
    """
    products = []
    for _ in range(n):
        cost = round(random.uniform(5, 500), 2)   # random cost between ₹5-500
        products.append({
            "product_id":   fake.uuid4(),
            "product_name": fake.catch_phrase(),   # "Innovative data solution"
            "category":     random.choice(CATEGORIES),
            "cost_price":   cost,
            "sell_price":   round(cost * random.uniform(1.2, 2.5), 2),  # markup
        })
    return pd.DataFrame(products)


# ── 3. Generate Orders ────────────────────────────────────────
STATUSES = [
    "completed", "completed", "completed",  # more completed = realistic
    "returned", "cancelled", "pending"
]

def generate_orders(customers, products, n=2000):
    """
    Creates n fake orders.
    Each order links a customer to a product with quantity and price.
    """
    orders = []
    start_date = datetime.now() - timedelta(days=365)  # last 1 year of orders

    for _ in range(n):
        orders.append({
            "order_id":    fake.uuid4(),
            "customer_id": random.choice(customers["customer_id"].tolist()),
            "product_id":  random.choice(products["product_id"].tolist()),
            "quantity":    random.randint(1, 10),
            "unit_price":  round(random.uniform(5, 500), 2),
            "order_date":  start_date + timedelta(
                seconds=random.randint(0, 365 * 24 * 3600)
            ),
            "status":      random.choice(STATUSES),
        })
    return pd.DataFrame(orders)


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("⚙️  Generating customers...")
    customers = generate_customers(500)
    customers.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
    print(f"   ✅ {len(customers)} customers saved to data/customers.csv")

    print("⚙️  Generating products...")
    products = generate_products(100)
    products.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)
    print(f"   ✅ {len(products)} products saved to data/products.csv")

    print("⚙️  Generating orders...")
    orders = generate_orders(customers, products, 2000)
    orders.to_csv(f"{OUTPUT_DIR}/orders.csv", index=False)
    print(f"   ✅ {len(orders)} orders saved to data/orders.csv")

    print("\n🎉 All data generated successfully!")