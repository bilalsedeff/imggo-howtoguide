"""
Parking Management - Python Example
License Plate Recognition and parking event logging
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_parking_image(image_url: str) -> dict:
    """Process parking camera image and extract vehicle data"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("PARKING_PATTERN_ID", "pat_parking_lpr")

    print(f"\nProcessing parking image: {image_url}")

    result = client.process_image_url(
        image_url=image_url,
        pattern_id=PATTERN_ID
    )

    return result


def parse_xml_result(xml_string: str) -> dict:
    """Parse XML parking event"""
    root = ET.fromstring(xml_string)

    # Extract license plate info
    license_plate = root.find('.//LicensePlate/Number')
    jurisdiction = root.find('.//LicensePlate/Jurisdiction')
    timestamp = root.find('.//Timestamp')
    entry_lane = root.find('.//EntryLane')

    return {
        'license_plate': license_plate.text if license_plate is not None else None,
        'jurisdiction': jurisdiction.text if jurisdiction is not None else None,
        'timestamp': timestamp.text if timestamp is not None else None,
        'entry_lane': entry_lane.text if entry_lane is not None else None
    }


def log_to_parking_system(event: dict) -> None:
    """Send parking event to parking management system"""
    import requests

    PARKING_SYSTEM_URL = os.getenv("PARKING_SYSTEM_URL", "https://parking-api.example.com/events")
    PARKING_API_KEY = os.getenv("PARKING_API_KEY")

    if not PARKING_API_KEY:
        print("⚠ Parking system API key not set, skipping integration")
        return

    payload = {
        "license_plate": event['license_plate'],
        "jurisdiction": event['jurisdiction'],
        "entry_time": event['timestamp'],
        "entry_lane": event['entry_lane'],
        "event_type": "entry"
    }

    try:
        response = requests.post(
            PARKING_SYSTEM_URL,
            json=payload,
            headers={"Authorization": f"Bearer {PARKING_API_KEY}"},
            timeout=10
        )

        if response.status_code == 200:
            print(f"✓ Event logged to parking system")
        else:
            print(f"✗ Failed to log event: {response.text}")

    except Exception as e:
        print(f"✗ Error logging to parking system: {e}")


def main():
    print("="*60)
    print("PARKING MANAGEMENT - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    # Example parking camera URL
    image_url = "https://parking-camera.example.com/lane-1/latest.jpg"

    try:
        # Process parking image
        xml_result = process_parking_image(image_url)

        # Parse XML
        event = parse_xml_result(xml_result)

        # Display results
        print("\n" + "="*60)
        print("PARKING EVENT")
        print("="*60)
        print(f"License Plate: {event['license_plate']}")
        print(f"Jurisdiction: {event['jurisdiction']}")
        print(f"Entry Time: {event['timestamp']}")
        print(f"Entry Lane: {event['entry_lane']}")

        # Save XML
        output_file = f"parking_event_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        with open(output_file, 'w') as f:
            f.write(xml_result)
        print(f"\n✓ Saved to {output_file}")

        # Optional: Log to parking system
        # log_to_parking_system(event)

        print("\n✓ Parking event processing completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
