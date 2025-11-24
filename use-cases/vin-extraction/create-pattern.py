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

    # VIN extraction pattern with structured JSON output
    payload = {
        "name": "VIN Extraction - JSON",
        "instructions": "Extract the Vehicle Identification Number (VIN) from the image. VIN is a 17-character alphanumeric code. Also extract vehicle make, model, and year if visible.",
        "response_format": "image_analysis",
        "schema": {
            "type": "object",
            "properties": {
                "vin": {
                    "type": "string",
                    "description": "17-character VIN code"
                },
                "make": {
                    "type": "string",
                    "description": "Vehicle manufacturer"
                },
                "model": {
                    "type": "string",
                    "description": "Vehicle model"
                },
                "year": {
                    "type": "number",
                    "description": "Model year"
                }
            },
            "required": ["vin"]
        }
    }

    print("=" * 60)
    print("CREATING VIN EXTRACTION PATTERN")
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
