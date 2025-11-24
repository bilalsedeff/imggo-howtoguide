"""
Create ImgGo Pattern for Retail Shelf Audit
Extract product analytics from retail shelf images
"""

import os
import requests
import json

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_shelf_audit_pattern():
    """Create pattern for retail shelf audit"""

    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    url = f"{BASE_URL}/patterns"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Shelf audit pattern with structured JSON output
    payload = {
        "name": "Retail Shelf Audit - JSON",
        "instructions": "Analyze the retail shelf image and extract: all visible products with brand names, product count per brand (facings), shelf position, out-of-stock gaps, planogram compliance, price tags if visible, and promotional items. Calculate total facings, unique SKUs, and brand share percentages.",
        "response_format": "image_analysis",
        "schema": {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "brand": {"type": "string"},
                            "product_name": {"type": "string"},
                            "facings": {"type": "number"},
                            "shelf_level": {"type": "string"},
                            "position": {"type": "string"},
                            "price": {"type": "string"}
                        }
                    }
                },
                "total_facings": {"type": "number"},
                "unique_skus": {"type": "number"},
                "out_of_stock_count": {"type": "number"},
                "brand_share": {
                    "type": "object",
                    "additionalProperties": {"type": "number"}
                }
            },
            "required": ["products", "total_facings"]
        }
    }

    print("=" * 60)
    print("CREATING RETAIL SHELF AUDIT PATTERN")
    print("=" * 60)
    print()

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        pattern_id = data.get("data", {}).get("id")

        print("V Pattern created successfully!")
        print()
        print(f"Pattern ID: {pattern_id}")
        print()
        print("Add to .env:")
        print(f"SHELF_AUDIT_PATTERN_ID={pattern_id}")
        print()

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")

        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None


if __name__ == "__main__":
    create_shelf_audit_pattern()
