"""
Extract CSV Data from Images
Complete example showing how to convert images to CSV format
"""

import os
import sys
from pathlib import Path
import csv

# Add common utilities to path
sys.path.append(str(Path(__file__).parent.parent / "common"))

from imggo_client import ImgGoClient


def example_inventory_to_csv():
    """
    Example 1: Extract inventory counts as CSV
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Inventory Photo → CSV")
    print("="*60)

    client = ImgGoClient()

    # Pattern for inventory counting (CSV output)
    # Create at img-go.com/patterns with:
    # - Instructions: "Count all visible products, extract SKU, product name, and quantity on shelf"
    # - Output format: CSV
    # - CSV headers: SKU, Product_Name, Quantity, Location
    PATTERN_ID = "pat_inventory_csv"

    # Using construction image as example (pretend it's warehouse)
    inventory_path = Path(__file__).parent.parent.parent / "test-images" / "construction1.jpg"

    print(f"\nProcessing: {inventory_path.name}")

    try:
        result = client.process_image(
            image_path=str(inventory_path),
            pattern_id=PATTERN_ID
        )

        # Result is CSV string
        print("\nExtracted CSV:")
        print(result)

        # Save to file
        output_file = "inventory_count.csv"
        with open(output_file, 'w', newline='') as f:
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

        # Parse and display summary
        import io
        csv_data = csv.DictReader(io.StringIO(result))
        rows = list(csv_data)

        print(f"\nSummary: {len(rows)} items counted")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_inspection_to_csv():
    """
    Example 2: Food safety inspection results as CSV
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Inspection Photo → CSV Report")
    print("="*60)

    client = ImgGoClient()

    # Pattern for inspection violations
    # Instructions: "Identify all violations, extract violation code, description, and severity"
    # Output: CSV with headers: Violation_Code, Description, Severity, Location, Corrected
    PATTERN_ID = "pat_inspection_csv"

    # Using document classification image as example
    inspection_path = Path(__file__).parent.parent.parent / "test-images" / "document-classification2.png"

    print(f"\nProcessing: {inspection_path.name}")

    try:
        result = client.process_image(
            image_path=str(inspection_path),
            pattern_id=PATTERN_ID
        )

        print("\nInspection Report CSV:")
        print(result)

        # Save to file
        output_file = "inspection_report.csv"
        with open(output_file, 'w', newline='') as f:
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_expense_receipts_to_csv():
    """
    Example 3: Batch process expense receipts to CSV
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Multiple Receipts → Consolidated CSV")
    print("="*60)

    client = ImgGoClient()

    # Pattern for receipt extraction
    # Instructions: "Extract merchant, date, total amount, and category from receipt"
    # Output: CSV with headers: Date, Merchant, Category, Amount
    PATTERN_ID = "pat_receipt_csv"

    test_images_dir = Path(__file__).parent.parent.parent / "test-images"

    # Using invoice images as receipt examples
    receipt_images = list(test_images_dir.glob("invoice*.jpg"))[:3]

    print(f"\nProcessing {len(receipt_images)} receipts...")

    all_rows = []

    for img_path in receipt_images:
        print(f"\n  Processing: {img_path.name}... ", end='')

        try:
            result = client.process_image(
                image_path=str(img_path),
                pattern_id=PATTERN_ID
            )

            # Parse CSV result
            import io
            csv_data = csv.DictReader(io.StringIO(result))
            rows = list(csv_data)

            all_rows.extend(rows)

            print(f"✓ ({len(rows)} items)")

        except Exception as e:
            print(f"✗ ({e})")

    # Save consolidated CSV
    if all_rows:
        output_file = "expense_report_consolidated.csv"

        with open(output_file, 'w', newline='') as f:
            if all_rows:
                writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
                writer.writeheader()
                writer.writerows(all_rows)

        print(f"\n✓ Consolidated {len(all_rows)} expenses to {output_file}")

        # Calculate totals
        total = sum(float(row.get('Amount', 0) or 0) for row in all_rows)
        print(f"  Total Expenses: ${total:,.2f}")

    else:
        print("\n✗ No data to consolidate")


def example_csv_to_database():
    """
    Example 4: CSV result directly to database
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Image → CSV → SQLite Database")
    print("="*60)

    client = ImgGoClient()
    PATTERN_ID = "pat_inventory_csv"

    inventory_path = Path(__file__).parent.parent.parent / "test-images" / "construction1.jpg"

    print(f"\nProcessing: {inventory_path.name}")

    try:
        result = client.process_image(
            image_path=str(inventory_path),
            pattern_id=PATTERN_ID
        )

        # Create SQLite database
        import sqlite3
        import io

        db_file = "inventory.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT,
                product_name TEXT,
                quantity INTEGER,
                location TEXT,
                counted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Parse CSV and insert
        csv_data = csv.DictReader(io.StringIO(result))

        for row in csv_data:
            cursor.execute("""
                INSERT INTO inventory (sku, product_name, quantity, location)
                VALUES (?, ?, ?, ?)
            """, (
                row.get('SKU', ''),
                row.get('Product_Name', ''),
                row.get('Quantity', 0),
                row.get('Location', '')
            ))

        conn.commit()

        # Query results
        cursor.execute("SELECT COUNT(*) FROM inventory")
        count = cursor.fetchone()[0]

        print(f"\n✓ Imported {count} items to {db_file}")

        # Show sample
        cursor.execute("SELECT * FROM inventory LIMIT 3")
        print("\nSample rows:")
        for row in cursor.fetchall():
            print(f"  {row}")

        conn.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")


def main():
    """
    Run all CSV extraction examples
    """
    print("\n" + "="*60)
    print("IMAGE TO CSV CONVERSION EXAMPLES")
    print("Using ImgGo API to extract CSV data from images")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY environment variable not set")
        print("  Set it in .env file or export IMGGO_API_KEY=your_key")
        return

    # Run examples
    try:
        example_inventory_to_csv()
        example_inspection_to_csv()
        example_expense_receipts_to_csv()
        example_csv_to_database()

        print("\n" + "="*60)
        print("ALL CSV EXAMPLES COMPLETED")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
