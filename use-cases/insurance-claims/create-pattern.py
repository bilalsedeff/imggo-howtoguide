"""
Create ImgGo Pattern for Insurance Claims
"""

import os
import requests

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_pattern():
    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    payload = {
        "name": "Insurance Claims - JSON",
        "instructions": "Analyze damage photos for insurance claims. Detect: damage type, severity, affected areas, estimated repair cost indicators, date if visible.",
        "response_format": "image_analysis",
        "schema": {"type": "object", "properties": {}, "required": []}
    }

    print("=" * 60)
    print("CREATING INSURANCE CLAIMS PATTERN")
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
        print(f"Add to .env:\nINSURANCE_CLAIMS_PATTERN_ID={pattern_id}\n")

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")
        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None

if __name__ == "__main__":
    create_pattern()
