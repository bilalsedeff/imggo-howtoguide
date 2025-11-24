"""
Create ImgGo Pattern for Parking Management / License Plate Recognition
Extract license plate and vehicle data from parking camera images
"""

import os
import requests
import json

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_parking_pattern():
    """Create pattern for parking management"""

    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    url = f"{BASE_URL}/patterns"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Parking management pattern
    payload = {
        "name": "Parking Management - XML",
        "instructions": "Extract license plate number, vehicle make, model, color, type (car/truck/SUV), timestamp, and parking spot number if visible. Also detect if multiple vehicles are in frame.",
        "response_format": "xml",
        "xml_root_element": "ParkingEvent"
    }

    print("=" * 60)
    print("CREATING PARKING MANAGEMENT PATTERN")
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
        print(f"PARKING_PATTERN_ID={pattern_id}")
        print()

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")

        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None


if __name__ == "__main__":
    create_parking_pattern()
