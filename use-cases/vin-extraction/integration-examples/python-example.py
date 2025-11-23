"""
VIN Extraction - Python Integration Example
Extract vehicle identification data from images in XML format
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_vin_image(image_path: str) -> str:
    """Process vehicle image and extract VIN data as XML"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("VIN_PATTERN_ID", "pat_vin_xml")

    print(f"\nProcessing VIN image: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return result  # XML string


def parse_vin_xml(xml_string: str) -> dict:
    """Parse XML VIN data"""
    root = ET.fromstring(xml_string)

    vin_data = {
        'vin_number': root.find('.//VINNumber').text if root.find('.//VINNumber') is not None else None,
        'make': root.find('.//Make').text if root.find('.//Make') is not None else None,
        'model': root.find('.//Model').text if root.find('.//Model') is not None else None,
        'year': root.find('.//Year').text if root.find('.//Year') is not None else None,
        'color': root.find('.//Color').text if root.find('.//Color') is not None else None,
        'license_plate': root.find('.//LicensePlate').text if root.find('.//LicensePlate') is not None else None,
        'odometer': root.find('.//Odometer').text if root.find('.//Odometer') is not None else None
    }

    return vin_data


def decode_vin(vin: str) -> dict:
    """Decode VIN number to extract vehicle information"""
    if not vin or len(vin) != 17:
        return {'valid': False, 'error': 'Invalid VIN length'}

    # Simplified VIN decoding (production should use NHTSA API or similar)
    decoded = {
        'valid': True,
        'wmi': vin[0:3],  # World Manufacturer Identifier
        'vds': vin[3:9],  # Vehicle Descriptor Section
        'vis': vin[9:17], # Vehicle Identifier Section
        'country': decode_country_code(vin[0]),
        'manufacturer': decode_manufacturer(vin[0:3]),
        'model_year': decode_model_year(vin[9]),
        'plant_code': vin[10]
    }

    return decoded


def decode_country_code(code: str) -> str:
    """Decode first character to determine country of origin"""
    country_map = {
        '1': 'United States', '2': 'Canada', '3': 'Mexico',
        'J': 'Japan', 'K': 'South Korea', 'L': 'China',
        'S': 'United Kingdom', 'V': 'Spain', 'W': 'Germany',
        'Z': 'Italy'
    }
    return country_map.get(code, 'Unknown')


def decode_manufacturer(wmi: str) -> str:
    """Decode WMI to determine manufacturer"""
    manufacturer_map = {
        '1FA': 'Ford', '1G1': 'Chevrolet', '1HD': 'Harley-Davidson',
        '1HG': 'Honda', '1N4': 'Nissan', '2HM': 'Hyundai',
        '3VW': 'Volkswagen', '5YJ': 'Tesla', 'JHM': 'Honda',
        'JTD': 'Toyota', 'WBA': 'BMW', 'WDB': 'Mercedes-Benz'
    }
    return manufacturer_map.get(wmi, 'Unknown')


def decode_model_year(code: str) -> str:
    """Decode 10th character to determine model year"""
    year_map = {
        'A': '2010', 'B': '2011', 'C': '2012', 'D': '2013',
        'E': '2014', 'F': '2015', 'G': '2016', 'H': '2017',
        'J': '2018', 'K': '2019', 'L': '2020', 'M': '2021',
        'N': '2022', 'P': '2023', 'R': '2024', 'S': '2025'
    }
    return year_map.get(code, 'Unknown')


def save_to_fleet_system(vin_data: dict, decoded: dict) -> bool:
    """Save vehicle to fleet management system"""
    print("\n" + "="*60)
    print("SAVING TO FLEET MANAGEMENT SYSTEM")
    print("="*60)

    payload = {
        'vehicle': {
            'vin': vin_data['vin_number'],
            'make': vin_data['make'] or decoded.get('manufacturer'),
            'model': vin_data['model'],
            'year': vin_data['year'] or decoded.get('model_year'),
            'color': vin_data['color'],
            'license_plate': vin_data['license_plate'],
            'odometer': vin_data['odometer'],
            'country_of_origin': decoded.get('country')
        }
    }

    print("Fleet System Payload:")
    print(payload)

    # In production: integrate with fleet management API

    print("\n✓ Vehicle saved to fleet system (simulated)")
    return True


def main():
    print("="*60)
    print("VIN EXTRACTION - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "vin1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        sys.exit(1)

    try:
        # Process VIN image
        xml_result = process_vin_image(str(test_image))

        # Save raw XML
        output_file = "vin_data.xml"
        with open(output_file, 'w') as f:
            f.write(xml_result)
        print(f"\n✓ Saved XML to {output_file}")

        # Parse XML
        vin_data = parse_vin_xml(xml_result)

        print("\n" + "="*60)
        print("EXTRACTED VIN DATA")
        print("="*60)
        for key, value in vin_data.items():
            print(f"{key}: {value}")

        # Decode VIN
        if vin_data['vin_number']:
            decoded = decode_vin(vin_data['vin_number'])

            print("\n" + "="*60)
            print("DECODED VIN INFORMATION")
            print("="*60)
            for key, value in decoded.items():
                print(f"{key}: {value}")

            # Save to fleet system
            save_to_fleet_system(vin_data, decoded)

        print("\n✓ VIN extraction completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
