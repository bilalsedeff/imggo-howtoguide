"""
Extract XML Data from Images
Complete example showing how to convert images to XML format
"""

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# Add common utilities to path
sys.path.append(str(Path(__file__).parent.parent / "common"))

from imggo_client import ImgGoClient


def example_parking_lpr_to_xml():
    """
    Example 1: License Plate Recognition → XML
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Parking Camera → XML Event")
    print("="*60)

    client = ImgGoClient()

    # Pattern for LPR (XML output)
    # Create at img-go.com/patterns with:
    # - Instructions: "Extract license plate number, vehicle make/model, timestamp"
    # - Output format: XML
    PATTERN_ID = "pat_parking_lpr_xml"

    parking_path = Path(__file__).parent.parent.parent / "test-images" / "parking1.jpg"

    print(f"\nProcessing: {parking_path.name}")

    try:
        result = client.process_image(
            image_path=str(parking_path),
            pattern_id=PATTERN_ID
        )

        # Result is XML string
        print("\nExtracted XML:")
        print(result)

        # Save to file
        output_file = "parking_event.xml"
        with open(output_file, 'w') as f:
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

        # Parse XML
        root = ET.fromstring(result)

        # Extract plate number
        plate = root.find(".//LicensePlate/Number")
        if plate is not None:
            print(f"\nLicense Plate: {plate.text}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_vin_extraction_to_xml():
    """
    Example 2: VIN Number Extraction → XML
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: VIN Photo → XML Data")
    print("="*60)

    client = ImgGoClient()

    # Pattern for VIN extraction
    # Instructions: "Extract VIN number and decode vehicle details (year, make, model)"
    # Output: XML format
    PATTERN_ID = "pat_vin_xml"

    # Using car plate image as example
    car_path = Path(__file__).parent.parent.parent / "test-images" / "car-plate1.jpg"

    print(f"\nProcessing: {car_path.name}")

    try:
        result = client.process_image(
            image_path=str(car_path),
            pattern_id=PATTERN_ID
        )

        print("\nVehicle XML:")
        print(result)

        # Save to file
        output_file = "vehicle_vin.xml"
        with open(output_file, 'w') as f:
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

        # Parse and validate VIN
        root = ET.fromstring(result)

        vin_element = root.find(".//VIN")
        if vin_element is not None:
            vin = vin_element.text
            print(f"\nVIN: {vin}")

            # VIN check digit validation
            if len(vin) == 17:
                print("✓ VIN length valid (17 characters)")
            else:
                print("✗ Invalid VIN length")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_invoice_to_xml_soap():
    """
    Example 3: Invoice → XML (SOAP-compatible format)
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Invoice → XML SOAP Message")
    print("="*60)

    client = ImgGoClient()

    # Pattern for invoice with XML/SOAP output
    # Instructions: "Extract invoice data in SOAP-compatible XML format"
    # Output: XML with SOAP envelope
    PATTERN_ID = "pat_invoice_xml_soap"

    invoice_path = Path(__file__).parent.parent.parent / "test-images" / "invoice1.jpg"

    print(f"\nProcessing: {invoice_path.name}")

    try:
        result = client.process_image(
            image_path=str(invoice_path),
            pattern_id=PATTERN_ID
        )

        print("\nSOAP XML:")
        print(result)

        # Save to file
        output_file = "invoice_soap.xml"
        with open(output_file, 'w') as f:
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

        # Parse SOAP message
        root = ET.fromstring(result)

        # Handle SOAP namespace
        namespaces = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/'}

        body = root.find('soap:Body', namespaces)
        if body is not None:
            print("\n✓ Valid SOAP message structure")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_xml_transformation():
    """
    Example 4: XML result → Transform and send to SOAP API
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Image → XML → SOAP API Integration")
    print("="*60)

    client = ImgGoClient()
    PATTERN_ID = "pat_parking_lpr_xml"

    parking_path = Path(__file__).parent.parent.parent / "test-images" / "parking2.jpg"

    print(f"\nProcessing: {parking_path.name}")

    try:
        result = client.process_image(
            image_path=str(parking_path),
            pattern_id=PATTERN_ID
        )

        # Transform XML for SOAP API
        root = ET.fromstring(result)

        # Create SOAP envelope
        soap_env = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        soap_env.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        soap_header = ET.SubElement(soap_env, '{http://schemas.xmlsoap.org/soap/envelope/}Header')

        soap_body = ET.SubElement(soap_env, '{http://schemas.xmlsoap.org/soap/envelope/}Body')

        # Add parking event to body
        soap_body.append(root)

        # Convert to string
        soap_xml = ET.tostring(soap_env, encoding='unicode', method='xml')

        print("\nTransformed SOAP Message:")
        print(soap_xml)

        # Save
        output_file = "parking_soap_request.xml"
        with open(output_file, 'w') as f:
            f.write(soap_xml)

        print(f"\n✓ Saved to {output_file}")

        # Simulate SOAP API call
        print("\nSimulating SOAP API call...")
        print("POST https://parking-system.example.com/api/events")
        print("Content-Type: text/xml; charset=utf-8")
        print("SOAPAction: 'http://example.com/ParkingEvent'")
        print("\n✓ Ready to send to SOAP endpoint")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_xml_validation():
    """
    Example 5: Validate XML against XSD schema
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: XML Validation Against Schema")
    print("="*60)

    # Create a sample XSD schema
    xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="ParkingEvent">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="EventID" type="xs:string"/>
                <xs:element name="Timestamp" type="xs:dateTime"/>
                <xs:element name="LicensePlate">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="Number" type="xs:string"/>
                            <xs:element name="State" type="xs:string"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''

    # Save XSD
    xsd_file = "parking_schema.xsd"
    with open(xsd_file, 'w') as f:
        f.write(xsd_content)

    print(f"Created XSD schema: {xsd_file}")

    # Try to validate (requires lxml library)
    try:
        from lxml import etree

        # Load schema
        schema_root = etree.XML(xsd_content.encode())
        schema = etree.XMLSchema(schema_root)

        # Load XML file
        xml_file = "parking_event.xml"

        if Path(xml_file).exists():
            with open(xml_file, 'r') as f:
                xml_doc = etree.parse(f)

            # Validate
            if schema.validate(xml_doc):
                print(f"\n✓ {xml_file} is valid against schema")
            else:
                print(f"\n✗ {xml_file} validation failed:")
                print(schema.error_log)

        else:
            print(f"\n✗ {xml_file} not found. Run example 1 first.")

    except ImportError:
        print("\n⚠ lxml not installed. Skipping validation")
        print("  Install with: pip install lxml")


def main():
    """
    Run all XML extraction examples
    """
    print("\n" + "="*60)
    print("IMAGE TO XML CONVERSION EXAMPLES")
    print("Using ImgGo API to extract XML data from images")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY environment variable not set")
        print("  Set it in .env file or export IMGGO_API_KEY=your_key")
        return

    # Run examples
    try:
        example_parking_lpr_to_xml()
        example_vin_extraction_to_xml()
        example_invoice_to_xml_soap()
        example_xml_transformation()
        example_xml_validation()

        print("\n" + "="*60)
        print("ALL XML EXAMPLES COMPLETED")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
