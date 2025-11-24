"""
Test CSV Format Examples from README
This script tests all code snippets from examples/formats/csv/README.md
"""

import os
import sys
from pathlib import Path
import csv
import io
import json

# Add common utilities to path
# examples/formats/csv -> examples/formats -> examples -> common
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "common"))
from imggo_client import ImgGoClient

def json_to_csv(data_dict, headers=None):
    """Convert JSON result to CSV format for testing"""
    if not headers:
        headers = list(data_dict.keys())

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerow(data_dict)

    return output.getvalue()

def test_basic_csv_processing():
    """Test Example 1: Basic CSV processing from README (lines 86-100)"""
    print("\n" + "="*60)
    print("TEST 1: Basic CSV Processing")
    print("="*60)

    client = ImgGoClient()
    pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"  # Using invoice pattern

    # Process an invoice image
    image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice1.jpg")

    print(f"Processing: {Path(image_path).name}")

    try:
        result = client.process_image(
            image_path=image_path,
            pattern_id=pattern_id
        )

        # Convert JSON result to CSV format
        csv_result = json_to_csv(result)

        print("\nExtracted CSV:")
        print(csv_result)

        # Save to file (as shown in README line 98)
        output_file = "examples/formats/csv/outputs/invoice1-basic.csv"
        with open(output_file, "w") as f:
            f.write(csv_result)

        print(f"SUCCESS: Saved to {output_file}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pandas_integration():
    """Test Example 2: Pandas integration from README (lines 128-139)"""
    print("\n" + "="*60)
    print("TEST 2: Pandas Integration")
    print("="*60)

    try:
        import pandas as pd

        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice2.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)

        # Convert to CSV then read with pandas
        csv_result = json_to_csv(result)

        # Read CSV string into DataFrame (as shown in README line 135)
        df = pd.read_csv(io.StringIO(csv_result))

        print("\nDataFrame Info:")
        print(df.info())
        print("\nDataFrame Head:")
        print(df.head())

        # Save DataFrame
        output_file = "examples/formats/csv/outputs/invoice2-pandas.csv"
        df.to_csv(output_file, index=False)

        print(f"\nSUCCESS: Saved to {output_file}")
        return True

    except ImportError:
        print("SKIPPED: pandas not installed")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sqlite_integration():
    """Test Example 3: SQLite integration from README (lines 189-220)"""
    print("\n" + "="*60)
    print("TEST 3: SQLite Integration")
    print("="*60)

    try:
        import sqlite3

        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice3.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)

        # Convert to CSV
        csv_result = json_to_csv(result)

        # Create SQLite database
        db_file = "examples/formats/csv/outputs/invoices.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table (as shown in README line 200-208)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT,
                vendor TEXT,
                total_amount REAL,
                date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Import CSV (as shown in README line 211-225)
        csv_data = csv.DictReader(io.StringIO(csv_result))

        for row in csv_data:
            cursor.execute("""
                INSERT INTO invoices (invoice_number, vendor, total_amount, date)
                VALUES (?, ?, ?, ?)
            """, (
                row.get('invoice_number', ''),
                row.get('vendor', ''),
                float(row.get('total_amount', 0) or 0),
                row.get('date', '')
            ))

        conn.commit()

        # Query results
        cursor.execute("SELECT COUNT(*) FROM invoices")
        count = cursor.fetchone()[0]

        print(f"\nImported {count} invoice(s) to database")

        # Show sample (as shown in README line 236-239)
        cursor.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT 3")
        print("\nSample rows:")
        for row in cursor.fetchall():
            print(f"  {row}")

        conn.close()

        print(f"\nSUCCESS: Database saved to {db_file}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_processing():
    """Test Example 4: Batch processing from README (lines 295-312)"""
    print("\n" + "="*60)
    print("TEST 4: Batch Processing")
    print("="*60)

    try:
        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        test_images_dir = Path(__file__).parent.parent.parent / "test-images"

        # Process multiple invoice images (as shown in README line 301)
        invoice_images = list(test_images_dir.glob("invoice*.jpg"))[:3]

        print(f"\nProcessing {len(invoice_images)} images...")

        all_data = []

        for image_path in invoice_images:
            print(f"  Processing: {image_path.name}...", end=' ')

            try:
                result = client.process_image(str(image_path), pattern_id)
                csv_result = json_to_csv(result)

                # Parse CSV (as shown in README line 303)
                reader = csv.DictReader(io.StringIO(csv_result))
                rows = list(reader)
                all_data.extend(rows)

                print(f"SUCCESS ({len(rows)} row(s))")

            except Exception as e:
                print(f"ERROR: {e}")

        # Combine all results (as shown in README line 307-308)
        if all_data:
            output_file = "examples/formats/csv/outputs/batch-combined.csv"

            with open(output_file, 'w', newline='') as f:
                if all_data:
                    writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
                    writer.writeheader()
                    writer.writerows(all_data)

            print(f"\nSUCCESS: Combined {len(all_data)} row(s) to {output_file}")

            # Calculate totals (as shown in README line 165-166)
            total = sum(float(row.get('total_amount', 0) or 0) for row in all_data)
            print(f"Total Amount: ${total:,.2f}")

            return True
        else:
            print("\nNo data processed")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_validation():
    """Test Example 5: CSV validation from README (lines 261-283)"""
    print("\n" + "="*60)
    print("TEST 5: CSV Validation")
    print("="*60)

    try:
        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice4.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)
        csv_result = json_to_csv(result)

        # Validate CSV structure (as shown in README line 269)
        reader = csv.reader(io.StringIO(csv_result))
        rows = list(reader)

        if len(rows) < 2:
            raise ValueError("CSV has no data rows")

        # Check column count (as shown in README line 276-279)
        header = rows[0]
        print(f"\nHeader columns: {', '.join(header)}")

        for i, row in enumerate(rows[1:], start=2):
            if len(row) != len(header):
                print(f"WARNING: Row {i} has {len(row)} columns, expected {len(header)}")
            else:
                print(f"Row {i}: OK ({len(row)} columns)")

        print(f"\nSUCCESS: CSV validation passed")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Run all CSV format tests"""
    print("\n" + "="*60)
    print("CSV FORMAT EXAMPLES TEST SUITE")
    print("Testing all code snippets from README.md")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\nERROR: IMGGO_API_KEY environment variable not set")
        print("Set it with: export IMGGO_API_KEY=your_key")
        return

    # Create outputs directory
    os.makedirs("examples/formats/csv/outputs", exist_ok=True)

    # Run all tests
    tests = [
        ("Basic CSV Processing", test_basic_csv_processing),
        ("Pandas Integration", test_pandas_integration),
        ("SQLite Integration", test_sqlite_integration),
        ("Batch Processing", test_batch_processing),
        ("CSV Validation", test_csv_validation),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\nFATAL ERROR in {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)

if __name__ == "__main__":
    main()
