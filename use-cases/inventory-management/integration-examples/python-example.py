"""
Inventory Management - Python Example
Process warehouse photos and extract inventory data in CSV format
"""

import os
import sys
import csv
import io
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_inventory_count(image_path: str) -> str:
    """Process warehouse photo and get CSV inventory data"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("INVENTORY_PATTERN_ID", "pat_inventory_csv")

    print(f"\nProcessing inventory image: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return result  # CSV string


def parse_csv_inventory(csv_string: str) -> list:
    """Parse CSV inventory data"""
    reader = csv.DictReader(io.StringIO(csv_string))
    return list(reader)


def calculate_inventory_metrics(inventory: list) -> dict:
    """Calculate inventory metrics"""
    total_items = sum(int(item.get('quantity', 0)) for item in inventory)
    unique_skus = len(inventory)
    total_value = sum(
        int(item.get('quantity', 0)) * float(item.get('unit_price', 0))
        for item in inventory if 'unit_price' in item
    )

    return {
        'total_items': total_items,
        'unique_skus': unique_skus,
        'total_value': total_value
    }


def identify_low_stock(inventory: list, threshold: int = 10) -> list:
    """Identify low stock items"""
    low_stock = []

    for item in inventory:
        quantity = int(item.get('quantity', 0))
        if quantity < threshold:
            low_stock.append({
                'sku': item.get('sku'),
                'product_name': item.get('product_name'),
                'quantity': quantity,
                'location': item.get('location')
            })

    return low_stock


def main():
    print("="*60)
    print("INVENTORY MANAGEMENT - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "inventory1.jpg"

    if not test_image.exists():
        print(f"\n✗ Test image not found: {test_image}")
        sys.exit(1)

    try:
        # Process inventory
        csv_result = process_inventory_count(str(test_image))

        # Save CSV
        output_file = "inventory_count.csv"
        with open(output_file, 'w') as f:
            f.write(csv_result)
        print(f"\n✓ Saved CSV to {output_file}")

        # Parse and analyze
        inventory = parse_csv_inventory(csv_result)
        metrics = calculate_inventory_metrics(inventory)

        print("\n" + "="*60)
        print("INVENTORY METRICS")
        print("="*60)
        print(f"Total Items: {metrics['total_items']}")
        print(f"Unique SKUs: {metrics['unique_skus']}")
        print(f"Total Value: ${metrics['total_value']:,.2f}")

        # Check low stock
        low_stock = identify_low_stock(inventory)
        if low_stock:
            print(f"\n⚠ Low Stock Alert ({len(low_stock)} items):")
            for item in low_stock[:5]:
                print(f"  {item['sku']}: {item['quantity']} units in {item['location']}")

        print("\n✓ Inventory processing completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
