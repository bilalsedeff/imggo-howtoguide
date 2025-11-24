"""
Simple Retail Shelf Audit Test
Test the pattern with a sample shelf image
"""

import os
import sys
import json
from pathlib import Path

# Add imggo_client to path
sys.path.append(str(Path(__file__).parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def main():
    print("="*60)
    print("TESTING RETAIL SHELF AUDIT PATTERN")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\nX Error: IMGGO_API_KEY not set")
        print("Please set your API key in .env file")
        sys.exit(1)

    # Check pattern ID
    pattern_id = os.getenv("SHELF_AUDIT_PATTERN_ID")
    if not pattern_id:
        print("\nX Error: SHELF_AUDIT_PATTERN_ID not set")
        print("Run create-pattern.py first to create a pattern")
        sys.exit(1)

    # Get test image
    test_image = Path(__file__).parent.parent.parent / "test-images" / "inventory1.jpg"

    if not test_image.exists():
        print(f"\nX Error: Test image not found: {test_image}")
        sys.exit(1)

    print(f"\nPattern ID: {pattern_id}")
    print(f"Test Image: {test_image.name}")
    print()

    try:
        # Process shelf image
        client = ImgGoClient()
        print("Processing shelf image...")

        result = client.process_image(
            image_path=str(test_image),
            pattern_id=pattern_id
        )

        print("V Processing completed!")
        print()

        # Save to outputs folder
        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        # Try to parse as JSON
        try:
            shelf_data = json.loads(result)
            output_file = outputs_dir / "shelf_audit_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(shelf_data, f, indent=2)

            print(f"V Output saved to: {output_file}")
            print()

            # Display summary
            print("="*60)
            print("SHELF AUDIT SUMMARY")
            print("="*60)
            print(f"Total Facings: {shelf_data.get('total_facings', 0)}")
            print(f"Unique SKUs: {shelf_data.get('unique_skus', 0)}")
            print(f"Out of Stock: {shelf_data.get('out_of_stock_count', 0)}")
            print(f"\nProducts: {len(shelf_data.get('products', []))}")
            for product in shelf_data.get('products', [])[:5]:
                print(f"  - {product.get('brand')}: {product.get('product_name')} ({product.get('facings')} facings)")
            print()

        except json.JSONDecodeError:
            # Not JSON, save as text
            output_file = outputs_dir / "shelf_audit_output.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)

            print(f"V Output saved to: {output_file}")
            print()

        print("V Test completed successfully!")

    except Exception as e:
        print(f"\nX Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
