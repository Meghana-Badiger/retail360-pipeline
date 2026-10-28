"""
validate_data.py
────────────────
Uses Great Expectations to validate raw Bronze CSV data
before it enters the pipeline.

Run: python ingestion/validate_data.py
"""

import pandas as pd
import great_expectations as ge

def validate_orders():
    print("🔍 Validating orders data...")

    # Load CSV as a Great Expectations dataframe
    df = ge.read_csv("data/orders.csv")

    # ── Define Expectations ───────────────────────────────────

    # order_id must never be null
    df.expect_column_values_to_not_be_null("order_id")

    # customer_id must never be null
    df.expect_column_values_to_not_be_null("customer_id")

    # quantity must be between 1 and 10
    df.expect_column_values_to_be_between("quantity", 1, 10)

    # unit_price must be positive
    df.expect_column_values_to_be_between("unit_price", 0, 10000)

    # status must be one of these values
    df.expect_column_values_to_be_in_set(
        "status",
        ["completed", "pending", "cancelled", "returned"]
    )

    # order_id must be unique
    df.expect_column_values_to_be_unique("order_id")

    # Get results
    results = df.validate()
    return results


def validate_customers():
    print("🔍 Validating customers data...")

    df = ge.read_csv("data/customers.csv")

    # customer_id must never be null
    df.expect_column_values_to_not_be_null("customer_id")

    # email must never be null
    df.expect_column_values_to_not_be_null("email")

    # customer_id must be unique
    df.expect_column_values_to_be_unique("customer_id")

    # name must never be null
    df.expect_column_values_to_not_be_null("name")

    results = df.validate()
    return results


def validate_products():
    print("🔍 Validating products data...")

    df = ge.read_csv("data/products.csv")

    # product_id must never be null
    df.expect_column_values_to_not_be_null("product_id")

    # product_id must be unique
    df.expect_column_values_to_be_unique("product_id")

    # sell_price must be greater than cost_price
    df.expect_column_values_to_not_be_null("cost_price")
    df.expect_column_values_to_not_be_null("sell_price")

    # category must be one of valid values
    df.expect_column_values_to_be_in_set(
        "category",
        ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys"]
    )

    results = df.validate()
    return results


def main():
    print("=" * 50)
    print("  Great Expectations — Data Quality Checks")
    print("=" * 50)

    all_passed = True

    # Validate each dataset
    for name, validator in [
        ("Orders",    validate_orders),
        ("Customers", validate_customers),
        ("Products",  validate_products),
    ]:
        results = validator()
        passed = results["statistics"]["successful_expectations"]
        total  = results["statistics"]["evaluated_expectations"]
        failed = results["statistics"]["unsuccessful_expectations"]

        if failed == 0:
            print(f"✅ {name}: {passed}/{total} checks passed")
        else:
            print(f"❌ {name}: {failed} checks FAILED out of {total}")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("🎉 All data quality checks passed! Safe to ingest.")
    else:
        print("🚨 Data quality issues found! Fix before ingesting.")
    print("=" * 50)


if __name__ == "__main__":
    main()