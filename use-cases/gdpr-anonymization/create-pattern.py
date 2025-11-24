"""
Create ImgGo Pattern for GDPR Anonymization
"""

import os
import requests

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_pattern():
    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    # GDPR anonymization pattern - Text format
    # Based on ImgGo API: https://img-go.com/docs#api-endpoints
    # Text format requires plain_text_schema with # headings
    payload = {
        "name": "GDPR Data Anonymization - Text",
        "instructions": "Detect and list all PII in documents. Identify: names, emails, phone numbers, addresses, SSN, credit cards. List each type of PII found.",
        "format": "text",
        "plain_text_schema": "# Document Analysis\nDocument Type: [type]\n\n# PII Detected\n[pii_list]\n\n# Anonymization Required\n[anonymization_details]\n\n# Recommendations\n[recommendations]"
    }

    print("=" * 60)
    print("CREATING GDPR ANONYMIZATION PATTERN")
    print("=" * 60)
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/patterns",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload
        )

        print(f"Response Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Response: {response.text}")

        response.raise_for_status()

        pattern_id = response.json().get("data", {}).get("id")
        print(f"V Pattern created successfully!\n\nPattern ID: {pattern_id}\n")
        print(f"Add to .env:\nGDPR_PATTERN_ID={pattern_id}\n")

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")
        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None

if __name__ == "__main__":
    create_pattern()
