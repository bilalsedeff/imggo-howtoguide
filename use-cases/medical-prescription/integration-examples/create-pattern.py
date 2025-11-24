"""
Create ImgGo Pattern for Medical Prescription Processing
Extract prescription data from medical prescription images
"""

import os
import requests
import json

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_prescription_pattern():
    """Create pattern for prescription processing"""

    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    url = f"{BASE_URL}/patterns"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Prescription pattern - plain text format
    payload = {
        "name": "Medical Prescription - Plain Text",
        "instructions": "Extract all text from the medical prescription including: patient name, doctor name, clinic/hospital name, prescription date, medication names, dosages, frequency, duration, special instructions, and refill information. Format as readable plain text.",
        "response_format": "text"
    }

    print("=" * 60)
    print("CREATING PRESCRIPTION PROCESSING PATTERN")
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
        print(f"PRESCRIPTION_PATTERN_ID={pattern_id}")
        print()

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)

        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None


if __name__ == "__main__":
    create_prescription_pattern()
