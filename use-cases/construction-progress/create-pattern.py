"""
Create ImgGo Pattern for Construction Progress
"""

import os
import requests

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_pattern():
    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    # YAML output format for construction progress
    # Based on ImgGo API structure: https://img-go.com/docs#api-endpoints
    payload = {
        "name": "Construction Progress - YAML",
        "instructions": "Document construction site progress. Identify: completed work phases, equipment present, worker count, safety compliance, weather conditions. Output as YAML with clear key-value pairs.",
        "format": "yaml",
        "yaml_schema": "project_phase: string\ncompletion_percentage: number\nequipment_present: array\nworker_count: number\nsafety_compliant: boolean\nweather: string"
    }

    print("=" * 60)
    print("CREATING CONSTRUCTION PROGRESS PATTERN")
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
            print(f"Response Body: {response.text}")

        response.raise_for_status()

        pattern_id = response.json().get("data", {}).get("id")
        print(f"V Pattern created successfully!\n\nPattern ID: {pattern_id}\n")
        print(f"Add to .env:\nCONSTRUCTION_PATTERN_ID={pattern_id}\n")

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")
        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None

if __name__ == "__main__":
    create_pattern()
