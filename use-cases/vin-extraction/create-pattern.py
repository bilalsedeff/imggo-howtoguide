"""
Create ImgGo Pattern for VIN Extraction
Extract Vehicle Identification Numbers from images
"""

import os
import requests
import json

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_vin_pattern():
    """Create pattern for VIN extraction"""

    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    url = f"{BASE_URL}/patterns"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # VIN extraction pattern with CSV output format
    # Based on ImgGo API structure: https://img-go.com/docs#api-endpoints
    payload = {
        "name": "VIN Extraction - CSV",
        "instructions": "Extract the Vehicle Identification Number (VIN) from the image. VIN is a 17-character alphanumeric code. Also extract vehicle make, model, and year if visible. Output as CSV with headers: vin,make,model,year",
        "format": "csv",
        "csv_schema": "vin,make,model,year"
    }

    print("=" * 60)
    print("CREATING VIN EXTRACTION PATTERN")
    print("=" * 60)
    print()

    try:
        response = requests.post(url, headers=headers, json=payload)

        print(f"Response Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Response Body: {response.text}")

        response.raise_for_status()

        data = response.json()
        pattern_id = data.get("data", {}).get("id")

        print("V Pattern created successfully!")
        print()
        print(f"Pattern ID: {pattern_id}")
        print()
        print("Add to .env:")
        print(f"VIN_PATTERN_ID={pattern_id}")
        print()

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)

        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None


if __name__ == "__main__":
    create_vin_pattern()
