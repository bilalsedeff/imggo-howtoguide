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

    payload = {
        "name": "Content Moderation - JSON",
        "instructions": "Analyze image for inappropriate content. Detect: violence, adult content, hate symbols, weapons, drugs, self-harm. Return confidence scores and flagged categories.",
        "response_format": "image_analysis",
        "schema": {
            "type": "object",
            "properties": {
                "is_safe": {"type": "boolean"},
                "risk_level": {"type": "string", "enum": ["safe", "warning", "unsafe"]},
                "flagged_categories": {"type": "array", "items": {"type": "string"}},
                "confidence_scores": {"type": "object"}
            }
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
