"""
Create ImgGo Pattern for Food Safety
"""

import os
import requests

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_pattern():
    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    # Food safety pattern - YAML format
    # Based on ImgGo API: https://img-go.com/docs#api-endpoints
    payload = {
        "name": "Food Safety Inspection - YAML",
        "instructions": "Inspect food handling areas for safety violations. Identify violations found, cleanliness score (1-10), and overall compliance status.",
        "format": "yaml",
        "yaml_schema": "violations_found: array\ncleanliness_score: number\ncompliance_status: string\nrecommendations: string"
    }

    print("=" * 60)
    print("CREATING FOOD SAFETY PATTERN")
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
        print(f"Add to .env:\nFOOD_SAFETY_PATTERN_ID={pattern_id}\n")

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")
        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None

if __name__ == "__main__":
    create_pattern()
