# E-Commerce Product Catalog Automation

## Overview

Automate product catalog creation by extracting product details, specifications, and attributes from product images. Convert visual product information into **structured JSON** for e-commerce platforms, marketplaces, and PIM systems.

**Output Format**: JSON (structured product data for e-commerce platforms)
**Upload Method**: URL Processing (from manufacturer websites, supplier feeds, cloud storage)
**Industry**: E-Commerce, Retail, Wholesale, Marketplace Operators, Dropshipping

---

## The Problem

E-commerce businesses face critical product cataloging challenges:

- **Manual Data Entry**: Catalog teams spend 15-20 minutes per SKU creating listings
- **Incomplete Information**: 40% of product listings missing key specifications
- **Supplier Data Chaos**: Receive product images with no structured data
- **Marketplace Compliance**: Each platform requires different attribute schemas
- **Time to Market**: New products take weeks to list across all channels
- **Accuracy Issues**: 25% of product specifications contain errors

Manual product catalog creation can't scale with growing SKU counts and marketplace expansion.

---

## The Solution

ImgGo extracts product details from images (packaging, spec sheets, product photos) and outputs **structured JSON** ready for e-commerce platform import:

**Workflow**:
```
Product Image URL → ImgGo API → JSON Product Data → Shopify/Amazon/PIM
```

**What Gets Extracted**:
- Product titles and descriptions
- Brand and manufacturer
- Model numbers and SKUs
- Dimensions and weight
- Materials and composition
- Colors and variants
- Certifications and compliance
- Pricing from packaging

---

## Why JSON Output?

JSON is the standard for modern e-commerce:

- **API-First**: Direct integration with Shopify, WooCommerce, Magento APIs
- **Marketplace Ready**: Easy transformation to Amazon, eBay, Walmart schemas
- **PIM Integration**: Works with Akeneo, Salsify, Informatica PIM systems
- **Multi-Channel**: Single source of truth for all sales channels
- **Variant Support**: Handle product variations (size, color) elegantly

**Example Output**:
```json
{
  "product": {
    "sku": "CHAIR-ERG-BLK-001",
    "brand": "ErgoComfort",
    "manufacturer": "Office Solutions Inc.",
    "title": "ErgoComfort Executive Mesh Office Chair with Lumbar Support",
    "short_description": "Premium ergonomic office chair with adjustable lumbar support, breathable mesh back, and 360° swivel base",

    "long_description": "The ErgoComfort Executive Office Chair combines superior comfort with modern design. Features include adjustable lumbar support for lower back relief, breathable mesh backrest for all-day comfort, padded armrests, pneumatic seat height adjustment, and smooth-rolling casters suitable for carpeted and hard floors. Perfect for home offices and corporate environments.",

    "category_hierarchy": [
      "Furniture",
      "Office Furniture",
      "Office Chairs",
      "Ergonomic Chairs"
    ],

    "attributes": {
      "color": "Black",
      "material_back": "Breathable mesh",
      "material_seat": "High-density foam with fabric upholstery",
      "material_base": "Reinforced nylon",
      "weight_capacity_lbs": 300,
      "seat_height_range": "17-21 inches",
      "armrests": "Adjustable height and width",
      "lumbar_support": "Adjustable",
      "swivel": "360 degrees",
      "tilt_mechanism": "Synchro-tilt with tension control",
      "casters": "Dual-wheel, carpet safe",
      "assembly_required": true,
      "warranty_years": 5
    },

    "dimensions": {
      "assembled": {
        "height_inches": 45.5,
        "width_inches": 26.0,
        "depth_inches": 25.5
      },
      "seat": {
        "width_inches": 20.0,
        "depth_inches": 19.5
      },
      "package": {
        "length_inches": 30,
        "width_inches": 24,
        "height_inches": 12,
        "weight_lbs": 42.3
      }
    },

    "pricing": {
      "msrp_usd": 299.99,
      "map_usd": 249.99,
      "cost_usd": 120.00,
      "currency": "USD"
    },

    "inventory": {
      "upc": "012345678901",
      "ean": "0123456789012",
      "asin": "B08XYZ1234",
      "mpn": "EC-EXEC-BLK-001"
    },

    "certifications": [
      {
        "type": "BIFMA",
        "description": "Meets BIFMA X5.1 office seating standards"
      },
      {
        "type": "GREENGUARD",
        "description": "GREENGUARD certified for low chemical emissions"
      }
    ],

    "variants": [
      {
        "sku": "CHAIR-ERG-BLK-001",
        "color": "Black",
        "availability": "in_stock",
        "image_url": "https://cdn.example.com/chair-black.jpg"
      },
      {
        "sku": "CHAIR-ERG-GRY-001",
        "color": "Gray",
        "availability": "in_stock",
        "image_url": "https://cdn.example.com/chair-gray.jpg"
      }
    ],

    "images": [
      {
        "url": "https://cdn.example.com/chair-main.jpg",
        "type": "main",
        "alt_text": "ErgoComfort Executive Office Chair - Front View"
      },
      {
        "url": "https://cdn.example.com/chair-side.jpg",
        "type": "additional",
        "alt_text": "ErgoComfort Executive Office Chair - Side View"
      },
      {
        "url": "https://cdn.example.com/chair-lumbar.jpg",
        "type": "detail",
        "alt_text": "Adjustable Lumbar Support Detail"
      }
    ],

    "seo": {
      "meta_title": "ErgoComfort Executive Mesh Office Chair | Adjustable Lumbar Support",
      "meta_description": "Premium ergonomic office chair with breathable mesh, adjustable lumbar support, 300lb capacity. BIFMA certified. Free shipping on orders over $100.",
      "keywords": ["ergonomic office chair", "mesh office chair", "lumbar support chair", "executive chair", "home office chair"]
    },

    "shipping": {
      "free_shipping_eligible": true,
      "ships_from": "USA",
      "estimated_delivery_days": 5,
      "dimensional_weight_lbs": 45,
      "fragile": false,
      "requires_signature": false
    },

    "compliance": {
      "prop_65_warning": false,
      "country_of_origin": "China",
      "hts_code": "9401.80.4015"
    }
  }
}
```

---

## Implementation Guide

### Step 1: Product Data Extraction Pattern

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "E-Commerce Product Catalog Extractor",
  "output_format": "json",
  "schema": {
    "product": {
      "sku": "string",
      "brand": "string",
      "title": "string",
      "short_description": "string",
      "long_description": "string",
      "category_hierarchy": ["string"],
      "attributes": {
        "color": "string",
        "material": "string",
        "size": "string"
      },
      "dimensions": {
        "height_inches": "number",
        "width_inches": "number",
        "depth_inches": "number"
      },
      "pricing": {
        "msrp_usd": "number"
      },
      "images": [
        {
          "url": "string",
          "type": "enum[main,additional,detail]"
        }
      ]
    }
  }
}
```

### Step 2: Bulk Catalog Processing from URLs

```python
import requests
import json
import time
import pandas as pd

IMGGO_API_KEY = "your_api_key"
IMGGO_PATTERN_ID = "pat_product_catalog_xyz"

def extract_product_from_url(product_image_url):
    """
    Extract product data from image URL (manufacturer site, supplier feed, etc.)
    """
    response = requests.post(
        f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
        headers={
            "Authorization": f"Bearer {IMGGO_API_KEY}",
            "Idempotency-Key": f"product-{product_image_url.split('/')[-1]}"
        },
        json={
            "image_url": product_image_url
        }
    )

    job_id = response.json()["data"]["job_id"]

    # Poll for result
    for _ in range(30):
        result = requests.get(
            f"https://img-go.com/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {IMGGO_API_KEY}"}
        ).json()

        if result["data"]["status"] == "completed":
            return result["data"]["result"]
        elif result["data"]["status"] == "failed":
            raise Exception(f"Extraction failed: {result['data'].get('error')}")

        time.sleep(2)

    raise Exception("Extraction timeout")


def bulk_catalog_from_supplier_feed(supplier_csv):
    """
    Process entire supplier catalog from CSV with image URLs
    """
    # Read supplier feed
    supplier_data = pd.read_csv(supplier_csv)

    products = []

    for idx, row in supplier_data.iterrows():
        try:
            print(f"Processing {idx+1}/{len(supplier_data)}: {row['product_image_url']}")

            # Extract product data
            product_json = extract_product_from_url(row['product_image_url'])

            # Parse JSON
            product = json.loads(product_json)

            # Enrich with supplier data
            product['product']['supplier'] = {
                'name': row['supplier_name'],
                'id': row['supplier_id'],
                'cost': row['wholesale_cost']
            }

            products.append(product)

            # Rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"Error processing {row['product_image_url']}: {e}")

    # Save consolidated catalog
    with open('catalog_enriched.json', 'w') as f:
        json.dump(products, f, indent=2)

    print(f"\nProcessed {len(products)} products successfully")

    return products


# Example: Process supplier catalog
products = bulk_catalog_from_supplier_feed('supplier_feed.csv')
```

### Step 3: Shopify Integration

```python
import shopify

SHOPIFY_SHOP_URL = "your-store.myshopify.com"
SHOPIFY_API_KEY = os.environ['SHOPIFY_API_KEY']
SHOPIFY_PASSWORD = os.environ['SHOPIFY_PASSWORD']

shopify.ShopifyResource.set_site(
    f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOPIFY_SHOP_URL}/admin"
)

def import_to_shopify(product_json):
    """
    Import product to Shopify from extracted JSON
    """
    product_data = product_json['product']

    # Create Shopify product
    new_product = shopify.Product()
    new_product.title = product_data['title']
    new_product.body_html = product_data['long_description']
    new_product.vendor = product_data['brand']
    new_product.product_type = product_data['category_hierarchy'][-1]

    # Add variants
    new_product.variants = []

    for variant_data in product_data.get('variants', [{'sku': product_data['sku']}]):
        variant = shopify.Variant()
        variant.sku = variant_data['sku']
        variant.price = product_data['pricing']['msrp_usd']
        variant.inventory_management = "shopify"
        variant.inventory_policy = "deny"

        # Add variant options (color, size, etc.)
        variant.option1 = variant_data.get('color', 'Default')

        new_product.variants.append(variant)

    # Add images
    new_product.images = []

    for img_data in product_data.get('images', []):
        image = shopify.Image()
        image.src = img_data['url']
        image.alt = img_data.get('alt_text', product_data['title'])
        new_product.images.append(image)

    # Add metafields for additional attributes
    new_product.metafields = []

    for key, value in product_data.get('attributes', {}).items():
        metafield = shopify.Metafield()
        metafield.namespace = "product_specs"
        metafield.key = key
        metafield.value = str(value)
        metafield.value_type = "string"
        new_product.metafields.append(metafield)

    # Save to Shopify
    if new_product.save():
        print(f"Created Shopify product: {new_product.title} (ID: {new_product.id})")
        return new_product.id
    else:
        raise Exception(f"Shopify import failed: {new_product.errors.full_messages()}")


# Import all products to Shopify
for product in products:
    try:
        shopify_id = import_to_shopify(product)
    except Exception as e:
        print(f"Error importing {product['product']['title']}: {e}")
```

### Step 4: Amazon Marketplace Feed

```python
import xml.etree.ElementTree as ET

def generate_amazon_feed(products):
    """
    Generate Amazon MWS product feed XML from extracted JSON
    """
    envelope = ET.Element('AmazonEnvelope')
    envelope.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    header = ET.SubElement(envelope, 'Header')
    ET.SubElement(header, 'DocumentVersion').text = '1.01'
    ET.SubElement(header, 'MerchantIdentifier').text = os.environ['AMAZON_MERCHANT_ID']

    ET.SubElement(envelope, 'MessageType').text = 'Product'

    for idx, product_json in enumerate(products):
        product = product_json['product']

        message = ET.SubElement(envelope, 'Message')
        ET.SubElement(message, 'MessageID').text = str(idx + 1)

        product_elem = ET.SubElement(message, 'Product')
        ET.SubElement(product_elem, 'SKU').text = product['sku']

        standard_id = ET.SubElement(product_elem, 'StandardProductID')
        ET.SubElement(standard_id, 'Type').text = 'UPC'
        ET.SubElement(standard_id, 'Value').text = product['inventory']['upc']

        desc_data = ET.SubElement(product_elem, 'DescriptionData')
        ET.SubElement(desc_data, 'Title').text = product['title']
        ET.SubElement(desc_data, 'Brand').text = product['brand']
        ET.SubElement(desc_data, 'Description').text = product['long_description']

        # Add bullet points from attributes
        for key, value in list(product['attributes'].items())[:5]:
            ET.SubElement(desc_data, 'BulletPoint').text = f"{key.replace('_', ' ').title()}: {value}"

        # Dimensions
        dims = ET.SubElement(desc_data, 'ItemDimensions')
        ET.SubElement(dims, 'Length', Units='inches').text = str(product['dimensions']['package']['length_inches'])
        ET.SubElement(dims, 'Width', Units='inches').text = str(product['dimensions']['package']['width_inches'])
        ET.SubElement(dims, 'Height', Units='inches').text = str(product['dimensions']['package']['height_inches'])
        ET.SubElement(dims, 'Weight', Units='pounds').text = str(product['dimensions']['package']['weight_lbs'])

    # Write XML file
    tree = ET.ElementTree(envelope)
    tree.write('amazon_product_feed.xml', encoding='utf-8', xml_declaration=True)

    print("Amazon product feed generated: amazon_product_feed.xml")


# Generate Amazon feed
generate_amazon_feed(products)
```

---

## Performance Metrics

### Cataloging Speed

| Task | Manual Process | With ImgGo | Savings |
|------|----------------|------------|---------|
| Find product specs | 8 minutes | Automated | 100% |
| Write descriptions | 10 minutes | Automated | 100% |
| Extract dimensions | 5 minutes | Automated | 100% |
| Format for platform | 7 minutes | Automated | 100% |
| **Total per SKU** | **30 minutes** | **2 minutes** | **93%** |

### Business Impact

**E-commerce seller** (500 new SKUs/month):

- **Catalog Team Savings**: $180,000/year (234 hours saved monthly × $64/hour × 12)
- **Time to Market**: 10× faster (launch products same day vs 3 weeks)
- **Listing Quality**: 50% reduction in incomplete product listings
- **Marketplace Expansion**: Can now list on 3× more platforms
- **Total Annual Benefit**: $350,000
- **ImgGo Cost**: $24,000/year
- **ROI**: 1,358%

---

## Best Practices

### Image Quality

- **Product Photos**: High-resolution images with packaging visible
- **Spec Sheets**: Clear PDF or image of manufacturer specifications
- **Multiple Angles**: Front, side, back, packaging for complete data

### Data Validation

- **Human Review**: QA team reviews 100% of first 50 SKUs, then 10% ongoing
- **Required Fields**: Validate all mandatory marketplace fields populated
- **Pricing**: Verify MSRP and MAP pricing match manufacturer data

---

## Related Use Cases

- [Inventory Management](../inventory-management) - Stock counting and warehouse automation
- [Retail Shelf Audit](../retail-shelf-audit) - Product placement verification
- [Document Classification](../document-classification) - Catalog PDF processing

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- JSON Schema Guide: [https://img-go.com/docs/output-formats#json](https://img-go.com/docs/output-formats#json)
- Integration Help: support@img-go.com
