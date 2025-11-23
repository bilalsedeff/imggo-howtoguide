"""
Retail Shelf Audit - Python Example
Process shelf photos and extract product analytics
"""

import os
import sys
import json
from pathlib import Path

# Add common client to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_shelf_audit(image_url: str) -> dict:
    """
    Process a shelf photo and extract product analytics

    Args:
        image_url: Public URL to shelf photo

    Returns:
        Shelf analytics data in JSON format
    """
    client = ImgGoClient()

    # Pattern for retail shelf audit
    # Create at img-go.com/patterns with:
    # - Instructions: "Identify all products, count facings, calculate brand share, detect out-of-stock"
    # - Output format: JSON
    PATTERN_ID = os.getenv("SHELF_AUDIT_PATTERN_ID", "pat_shelf_audit")

    print(f"\nProcessing shelf image: {image_url}")

    try:
        result = client.process_image_url(
            image_url=image_url,
            pattern_id=PATTERN_ID
        )

        return result

    except Exception as e:
        print(f"Error processing shelf audit: {e}")
        raise


def display_analytics(analytics: dict) -> None:
    """Display shelf analytics in readable format"""

    print("\n" + "="*60)
    print("SHELF AUDIT ANALYTICS")
    print("="*60)

    # Overall metrics
    print(f"\nTotal Products: {analytics.get('total_facings', 0)}")
    print(f"Unique SKUs: {len(analytics.get('products', []))}")
    print(f"Out of Stock Items: {analytics.get('out_of_stock_count', 0)}")

    # Brand share
    if 'brand_share' in analytics:
        print("\nBrand Share:")
        for brand, percentage in analytics['brand_share'].items():
            print(f"  {brand}: {percentage:.1f}%")

    # Products detail
    if 'products' in analytics:
        print(f"\nProducts Detected ({len(analytics['products'])} items):")
        for i, product in enumerate(analytics['products'][:5], 1):  # Show first 5
            print(f"\n  {i}. {product.get('name', 'Unknown')}")
            print(f"     Brand: {product.get('brand', 'Unknown')}")
            print(f"     Facings: {product.get('facing_count', 0)}")
            print(f"     Price Visible: {'Yes' if product.get('price_visible') else 'No'}")

        if len(analytics['products']) > 5:
            print(f"\n  ... and {len(analytics['products']) - 5} more products")

    # Planogram compliance
    if 'planogram_compliance' in analytics:
        compliance = analytics['planogram_compliance']
        print(f"\nPlanogram Compliance: {compliance.get('score', 0):.1f}%")
        if 'issues' in compliance:
            print(f"  Issues: {', '.join(compliance['issues'])}")


def save_to_database(analytics: dict, store_id: str, location: str) -> None:
    """
    Save shelf audit results to database

    This is a placeholder - replace with your actual database logic
    """
    import psycopg2
    from datetime import datetime

    # Database connection
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "retail_analytics"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )

    cursor = conn.cursor()

    # Insert audit record
    cursor.execute("""
        INSERT INTO shelf_audits (
            store_id,
            location,
            total_facings,
            unique_skus,
            out_of_stock_count,
            planogram_compliance_score,
            audit_data,
            audit_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        store_id,
        location,
        analytics.get('total_facings', 0),
        len(analytics.get('products', [])),
        analytics.get('out_of_stock_count', 0),
        analytics.get('planogram_compliance', {}).get('score', 0),
        json.dumps(analytics),
        datetime.now()
    ))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✓ Saved to database: Store {store_id}, Location {location}")


def main():
    """Run shelf audit example"""

    print("="*60)
    print("RETAIL SHELF AUDIT - PYTHON EXAMPLE")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY environment variable not set")
        print("  Set it in .env file or export IMGGO_API_KEY=your_key")
        sys.exit(1)

    # Example shelf image URL
    # In production, this would come from your store cameras or mobile app
    image_url = "https://example.com/shelf-photos/store-123-aisle-5.jpg"

    # You can also use local images from test-images
    # For local images, use the direct upload method:
    # test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "shelf-audit1.jpg"
    # if test_image.exists():
    #     client = ImgGoClient()
    #     result = client.process_image(str(test_image), PATTERN_ID)

    try:
        # Process shelf photo
        analytics = process_shelf_audit(image_url)

        # Display results
        display_analytics(analytics)

        # Save to file
        output_file = "shelf_audit_result.json"
        with open(output_file, 'w') as f:
            json.dump(analytics, f, indent=2)
        print(f"\n✓ Results saved to {output_file}")

        # Optional: Save to database
        # save_to_database(analytics, store_id="STORE-123", location="Aisle 5")

        print("\n✓ Shelf audit completed successfully!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
