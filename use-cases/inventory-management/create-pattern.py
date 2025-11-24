"""
Create ImgGo Pattern for Inventory Management
Extract product counts and inventory data from warehouse images
"""

import os
import requests
import json

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_inventory_pattern():
    """Create pattern for inventory management"""

    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    url = f"{BASE_URL}/patterns"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Based on ImgGo API: format must be json, yaml, xml, csv, or text
    payload = {
        "name": "Inventory Management - CSV",
        "instructions": "Count all visible products/items in the image. Identify product types, quantities, conditions (new/damaged), and location if visible.",
        "format": "csv",
        "csv_schema": "item_type,quantity,condition,location,notes"
    }

    print("=" * 60)
    print("CREATING INVENTORY MANAGEMENT PATTERN")
    print("=" * 60)
    print()

    try:
        response = requests.post(url, headers=headers, json=payload)

        print(f"Response Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Response: {response.text}")

        response.raise_for_status()

        data = response.json()
        pattern_id = data.get("data", {}).get("id")

        print("V Pattern created successfully!")
        print()
        print(f"Pattern ID: {pattern_id}")
        print()
        print("Add to .env:")
        print(f"INVENTORY_PATTERN_ID={pattern_id}")
        print()

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")

        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None


if __name__ == "__main__":
    create_inventory_pattern()
