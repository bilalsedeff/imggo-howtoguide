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

    # Shelf audit pattern - JSON format
    # Based on ImgGo API: https://img-go.com/docs#api-endpoints
    # All properties must be in required array
    payload = {
        "name": "Retail Shelf Audit - JSON",
        "instructions": "Analyze the retail shelf image and extract: product brands, total facings count, unique SKUs count, and out-of-stock count.",
        "format": "json",
        "json_schema": {
            "type": "object",
            "properties": {
                "brands_detected": {"type": "string"},
                "total_facings": {"type": "number"},
                "unique_skus": {"type": "number"},
                "out_of_stock_count": {"type": "number"}
            },
            "required": ["brands_detected", "total_facings", "unique_skus", "out_of_stock_count"],
            "additionalProperties": False
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
