"""
Create ImgGo Pattern for Content Moderation
Detect inappropriate content in images
"""

import os
import requests

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_moderation_pattern():
    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    # Based on ImgGo API: format must be json, yaml, xml, csv, or text
    # All properties must be in required array
    payload = {
        "name": "Content Moderation - JSON",
        "instructions": "Analyze image for inappropriate content. Detect: violence, adult content, hate symbols, weapons, drugs, self-harm. Return safety assessment and flagged categories.",
        "format": "json",
        "json_schema": {
            "type": "object",
            "properties": {
                "is_safe": {"type": "boolean"},
                "risk_level": {"type": "string"},
                "flagged_categories": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["is_safe", "risk_level", "flagged_categories", "confidence"],
            "additionalProperties": False
        }
    }

    print("=" * 60)
    print("CREATING CONTENT MODERATION PATTERN")
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
        print(f"Add to .env:\nCONTENT_MODERATION_PATTERN_ID={pattern_id}\n")

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")
        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None

if __name__ == "__main__":
    create_moderation_pattern()
