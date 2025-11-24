"""
Create ImgGo Pattern for Kyc Verification
"""

import os
import requests

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_pattern():
    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    # KYC verification pattern - JSON format
    # Based on ImgGo API: https://img-go.com/docs#api-endpoints
    # All properties must be in required array
    payload = {
        "name": "KYC Document Verification - JSON",
        "instructions": "Extract data from KYC documents (ID cards, passports, driver licenses). Extract full name, date of birth, document number, and expiry date.",
        "format": "json",
        "json_schema": {
            "type": "object",
            "properties": {
                "full_name": {"type": "string"},
                "date_of_birth": {"type": "string"},
                "document_number": {"type": "string"},
                "expiry_date": {"type": "string"}
            },
            "required": ["full_name", "date_of_birth", "document_number", "expiry_date"],
            "additionalProperties": False
        }
    }

    print("=" * 60)
    print("CREATING KYC VERIFICATION PATTERN")
    print("=" * 60)
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/patterns",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()

        pattern_id = response.json().get("data", {}).get("id")
        print(f"V Pattern created successfully!\n\nPattern ID: {pattern_id}\n")
        print(f"Add to .env:\nKYC_PATTERN_ID={pattern_id}\n")

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")
        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None

if __name__ == "__main__":
    create_pattern()
