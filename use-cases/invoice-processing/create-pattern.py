"""
Create ImgGo Pattern for Invoice Processing
This script creates a pattern specifically for extracting invoice data
"""

import os
import requests
import json

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_invoice_pattern():
    """Create pattern for invoice extraction"""

    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        print("  Set it in .env file: IMGGO_API_KEY=your_key")
        return None

    url = f"{BASE_URL}/patterns"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Pattern configuration for invoice processing
    # Based on ImgGo API structure: https://img-go.com/docs#api-endpoints
    # Note: All properties in schema must be in required array
    payload = {
        "name": "Invoice Processing - JSON v2",
        "instructions": "Extract invoice data including vendor name, invoice number, date, and total amount.",
        "format": "json",
        "json_schema": {
            "type": "object",
            "properties": {
                "invoice_number": {"type": "string"},
                "vendor": {"type": "string"},
                "invoice_date": {"type": "string"},
                "total_amount": {"type": "number"}
            },
            "required": ["invoice_number", "vendor", "invoice_date", "total_amount"],
            "additionalProperties": False
        }
    }

    print("=" * 60)
    print("CREATING INVOICE PROCESSING PATTERN")
    print("=" * 60)
    print()
    print("Configuration:")
    print(f"  Name: {payload['name']}")
    print(f"  Format: {payload['format']}")
    print(f"  Instructions: {payload['instructions'][:80]}...")
    print()

    try:
        response = requests.post(url, headers=headers, json=payload)

        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        response.raise_for_status()

        data = response.json()
        pattern_id = data.get("data", {}).get("id")

        print("V Pattern created successfully!")
        print()
        print("Pattern ID:", pattern_id)
        print()
        print("Save this ID to your .env file:")
        print(f"INVOICE_PATTERN_ID={pattern_id}")
        print()
        print("Or use it directly in your code:")
        print(f'PATTERN_ID = "{pattern_id}"')
        print()
        print("=" * 60)

        # Save pattern ID to file
        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Pattern ID saved to pattern_id.txt")

        return pattern_id

    except requests.exceptions.HTTPError as e:
        print(f"X HTTP Error: {e}")
        if e.response:
            print(f"  Status: {e.response.status_code}")
            print(f"  Response: {e.response.text}")
            print(f"  Headers: {dict(e.response.headers)}")
    except Exception as e:
        print(f"X Error: {e}")

    return None


if __name__ == "__main__":
    create_invoice_pattern()
