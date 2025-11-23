"""
Product Catalog - Python Integration Example
Extract product information and sync with e-commerce platforms
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_product_image(image_path: str) -> dict:
    """Process product image and extract catalog data"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("PRODUCT_CATALOG_PATTERN_ID", "pat_product_catalog_json")

    print(f"\nProcessing product image: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return json.loads(result) if isinstance(result, str) else result


def enrich_product_data(product: dict) -> dict:
    """Enrich product data with computed fields"""
    enriched = product.copy()

    # Generate SKU if missing
    if not enriched.get('sku'):
        brand = enriched.get('brand', 'UNK')[:3].upper()
        name = enriched.get('name', 'PRODUCT')[:3].upper()
        enriched['sku'] = f"{brand}{name}{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Calculate discounts
    if enriched.get('price') and enriched.get('compare_at_price'):
        price = float(enriched['price'])
        compare_price = float(enriched['compare_at_price'])
        if compare_price > price:
            discount = ((compare_price - price) / compare_price) * 100
            enriched['discount_percentage'] = round(discount, 1)

    # Set inventory status
    stock = enriched.get('stock_quantity', 0)
    if stock == 0:
        enriched['inventory_status'] = 'OUT_OF_STOCK'
    elif stock < 10:
        enriched['inventory_status'] = 'LOW_STOCK'
    else:
        enriched['inventory_status'] = 'IN_STOCK'

    return enriched


def sync_to_shopify(product: dict) -> dict:
    """Sync product to Shopify"""
    print("\n" + "="*60)
    print("SYNCING TO SHOPIFY")
    print("="*60)

    shopify_product = {
        "product": {
            "title": product.get('name'),
            "body_html": product.get('description', ''),
            "vendor": product.get('brand'),
            "product_type": product.get('category'),
            "tags": product.get('tags', []),
            "variants": [{
                "price": product.get('price'),
                "compare_at_price": product.get('compare_at_price'),
                "sku": product.get('sku'),
                "inventory_quantity": product.get('stock_quantity', 0),
                "weight": product.get('weight'),
                "weight_unit": product.get('weight_unit', 'kg')
            }]
        }
    }

    if 'image_url' in product:
        shopify_product['product']['images'] = [{"src": product['image_url']}]

    print(f"Product: {product.get('name')}")
    print(f"SKU: {product.get('sku')}")
    print(f"Price: ${product.get('price')}")

    # In production: POST to Shopify API
    # response = requests.post(
    #     'https://your-store.myshopify.com/admin/api/2024-01/products.json',
    #     headers={'X-Shopify-Access-Token': SHOPIFY_TOKEN},
    #     json=shopify_product
    # )

    print("\n✓ Product synced to Shopify (simulated)")
    return shopify_product


def sync_to_woocommerce(product: dict) -> dict:
    """Sync product to WooCommerce"""
    print("\n" + "="*60)
    print("SYNCING TO WOOCOMMERCE")
    print("="*60)

    woo_product = {
        "name": product.get('name'),
        "type": "simple",
        "regular_price": str(product.get('price', 0)),
        "sale_price": str(product.get('sale_price', '')),
        "description": product.get('description', ''),
        "short_description": product.get('short_description', ''),
        "sku": product.get('sku'),
        "manage_stock": True,
        "stock_quantity": product.get('stock_quantity', 0),
        "categories": [{"name": product.get('category')}],
        "tags": [{"name": tag} for tag in product.get('tags', [])]
    }

    if 'image_url' in product:
        woo_product['images'] = [{"src": product['image_url']}]

    print(f"Product: {product.get('name')}")
    print(f"Regular Price: ${product.get('price')}")

    # In production: POST to WooCommerce API
    # response = requests.post(
    #     'https://your-site.com/wp-json/wc/v3/products',
    #     auth=(CONSUMER_KEY, CONSUMER_SECRET),
    #     json=woo_product
    # )

    print("\n✓ Product synced to WooCommerce (simulated)")
    return woo_product


def generate_product_feed(product: dict) -> str:
    """Generate Google Shopping feed entry"""
    feed = []
    feed.append("GOOGLE SHOPPING FEED ENTRY")
    feed.append("=" * 60)
    feed.append(f"id: {product.get('sku')}")
    feed.append(f"title: {product.get('name')}")
    feed.append(f"description: {product.get('description', '')[:500]}")
    feed.append(f"link: https://your-store.com/products/{product.get('sku')}")
    feed.append(f"image_link: {product.get('image_url', '')}")
    feed.append(f"price: {product.get('price')} USD")
    feed.append(f"availability: {product.get('inventory_status', 'in stock')}")
    feed.append(f"brand: {product.get('brand')}")
    feed.append(f"condition: new")

    if 'gtin' in product:
        feed.append(f"gtin: {product['gtin']}")

    return "\n".join(feed)


def main():
    print("="*60)
    print("PRODUCT CATALOG - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "product1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        sys.exit(1)

    try:
        # Process product image
        product = process_product_image(str(test_image))

        # Save raw JSON
        output_file = "product_data.json"
        with open(output_file, 'w') as f:
            json.dump(product, f, indent=2)
        print(f"\n✓ Saved product data to {output_file}")

        # Enrich data
        enriched_product = enrich_product_data(product)

        print("\n" + "="*60)
        print("PRODUCT DETAILS")
        print("="*60)
        print(f"Name: {enriched_product.get('name')}")
        print(f"Brand: {enriched_product.get('brand')}")
        print(f"SKU: {enriched_product.get('sku')}")
        print(f"Price: ${enriched_product.get('price')}")
        print(f"Stock: {enriched_product.get('stock_quantity')} ({enriched_product.get('inventory_status')})")

        if 'discount_percentage' in enriched_product:
            print(f"Discount: {enriched_product['discount_percentage']}%")

        # Sync to platforms
        shopify_data = sync_to_shopify(enriched_product)
        woo_data = sync_to_woocommerce(enriched_product)

        # Generate feed
        feed = generate_product_feed(enriched_product)
        print("\n" + feed)

        # Save feed
        feed_file = "google_shopping_feed.txt"
        with open(feed_file, 'w') as f:
            f.write(feed)
        print(f"\n✓ Saved Google Shopping feed to {feed_file}")

        print("\n✓ Product catalog sync completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
