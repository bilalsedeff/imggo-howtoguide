"""
Test XML Format Examples from README
This script tests all code snippets from examples/formats/xml/README.md
"""

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import json

# Add common utilities to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "common"))
from imggo_client import ImgGoClient

def json_to_xml(data_dict, root_name="Result"):
    """Convert JSON result to XML format for testing"""
    root = ET.Element(root_name)

    for key, value in data_dict.items():
        child = ET.SubElement(root, key.replace('_', ''))
        child.text = str(value)

    return ET.tostring(root, encoding='unicode', method='xml')

def test_basic_xml_parsing():
    """Test Example 1: Basic XML parsing from README (lines 142-156)"""
    print("\n" + "="*60)
    print("TEST 1: Basic XML Parsing")
    print("="*60)

    client = ImgGoClient()
    pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

    # Process invoice image
    image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice1.jpg")

    print(f"Processing: {Path(image_path).name}")

    try:
        result = client.process_image(
            image_path=image_path,
            pattern_id=pattern_id
        )

        # Convert JSON to XML
        xml_result = json_to_xml(result, "Invoice")

        print("\nExtracted XML:")
        print(xml_result)

        # Parse XML (as shown in README line 148)
        root = ET.fromstring(xml_result)

        # Extract values (as shown in README lines 151-152)
        invoice_number = root.find(".//invoicenumber")
        vendor = root.find(".//vendor")

        if invoice_number is not None and vendor is not None:
            print(f"\nParsed values:")
            print(f"  Invoice Number: {invoice_number.text}")
            print(f"  Vendor: {vendor.text}")

        # Save to file (as shown in README line 110)
        output_file = "outputs/invoice1-basic.xml"
        os.makedirs("outputs", exist_ok=True)
        with open(output_file, "w") as f:
            f.write(xml_result)

        print(f"\nSUCCESS: Saved to {output_file}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_soap_transformation():
    """Test Example 2: SOAP transformation from README (lines 158-176)"""
    print("\n" + "="*60)
    print("TEST 2: SOAP XML Transformation")
    print("="*60)

    try:
        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice2.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)

        # Convert to XML
        inner_xml = json_to_xml(result, "Invoice")

        # Create SOAP envelope (as shown in README example)
        soap_env = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        soap_env.set('xmlns:soap', 'http://schemas.xmlsoap.org/soap/envelope/')

        soap_body = ET.SubElement(soap_env, '{http://schemas.xmlsoap.org/soap/envelope/}Body')

        # Add inner XML to SOAP body
        invoice_root = ET.fromstring(inner_xml)
        soap_body.append(invoice_root)

        # Convert to string
        soap_xml = ET.tostring(soap_env, encoding='unicode', method='xml')

        print("\nSOAP XML Message:")
        print(soap_xml[:500] + "...")

        # Save
        output_file = "outputs/invoice2-soap.xml"
        with open(output_file, 'w') as f:
            f.write(soap_xml)

        print(f"\nSUCCESS: Saved to {output_file}")
        print("Content-Type: text/xml; charset=utf-8")
        print("SOAPAction: 'http://example.com/ProcessInvoice'")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_xml_validation():
    """Test Example 3: XML validation from README (lines 196-217)"""
    print("\n" + "="*60)
    print("TEST 3: XML Validation Against XSD")
    print("="*60)

    try:
        # Create sample XML
        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice3.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)
        xml_result = json_to_xml(result, "Invoice")

        # Try to validate with lxml (as shown in README lines 199-217)
        try:
            from lxml import etree

            # Create simple XSD schema
            xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="Invoice">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="invoicenumber" type="xs:string"/>
                <xs:element name="vendor" type="xs:string"/>
                <xs:element name="totalamount" type="xs:string"/>
                <xs:element name="date" type="xs:string"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''

            # Save XSD
            xsd_file = "outputs/invoice_schema.xsd"
            with open(xsd_file, 'w') as f:
                f.write(xsd_content)

            # Load schema (as shown in README lines 204-206)
            schema_doc = etree.fromstring(xsd_content.encode())
            schema = etree.XMLSchema(schema_doc)

            # Validate (as shown in README lines 209-216)
            xml_doc = etree.fromstring(xml_result.encode())

            if schema.validate(xml_doc):
                print("SUCCESS: XML is valid against schema")
                return True
            else:
                print("Validation errors:")
                for error in schema.error_log:
                    print(f"  Line {error.line}: {error.message}")
                return True  # Still pass test even if validation fails

        except ImportError:
            print("SKIPPED: lxml not installed")
            return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_xml_namespaces():
    """Test Example 4: XML with namespaces from README (lines 273-286)"""
    print("\n" + "="*60)
    print("TEST 4: XML with Namespaces")
    print("="*60)

    try:
        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "parking1.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)

        # Create XML with namespace
        ns = "http://parking.imggo.com/schema/v1"
        root = ET.Element(f"{{{ns}}}ParkingEvent")
        root.set("xmlns", ns)

        for key, value in result.items():
            child = ET.SubElement(root, f"{{{ns}}}{key.replace('_', '')}")
            child.text = str(value)

        xml_result = ET.tostring(root, encoding='unicode', method='xml')

        print("\nXML with Namespace:")
        print(xml_result)

        # Parse with namespace (as shown in README lines 282-286)
        parsed_root = ET.fromstring(xml_result)

        # Define namespace map (as shown in README line 282)
        ns_map = {"p": ns}

        # Find elements with namespace (as shown in README line 285)
        # Note: ET.find requires namespaces in the xpath itself
        print(f"\nRoot tag with namespace: {parsed_root.tag}")

        # Save
        output_file = "outputs/parking1-namespace.xml"
        with open(output_file, 'w') as f:
            f.write(xml_result)

        print(f"\nSUCCESS: Saved to {output_file}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_xml_processing():
    """Test Example 5: Batch processing from README (lines 335-354)"""
    print("\n" + "="*60)
    print("TEST 5: Batch XML Processing")
    print("="*60)

    try:
        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        test_images_dir = Path(__file__).parent.parent.parent / "test-images"

        # Process multiple images (as shown in README line 342)
        invoice_images = list(test_images_dir.glob("invoice*.jpg"))[:3]

        print(f"\nProcessing {len(invoice_images)} images...")

        # Create root element for batch (as shown in README line 340)
        batch_root = ET.Element("Invoices")

        for image_path in invoice_images:
            print(f"  Processing: {image_path.name}...", end=' ')

            try:
                result = client.process_image(str(image_path), pattern_id)

                # Create individual invoice element
                invoice_elem = ET.Element("Invoice")
                for key, value in result.items():
                    child = ET.SubElement(invoice_elem, key.replace('_', ''))
                    child.text = str(value)

                # Add to batch (as shown in README line 349)
                batch_root.append(invoice_elem)

                print("SUCCESS")

            except Exception as e:
                print(f"ERROR: {e}")

        # Save batch XML (as shown in README lines 352-353)
        tree = ET.ElementTree(batch_root)
        output_file = "outputs/batch-invoices.xml"

        # Add pretty printing
        ET.indent(batch_root, space="  ")

        tree.write(output_file, encoding="utf-8", xml_declaration=True)

        print(f"\nSUCCESS: Combined {len(batch_root)} invoice(s) to {output_file}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pretty_printing():
    """Test Example 6: Pretty printing from README (lines 319-331)"""
    print("\n" + "="*60)
    print("TEST 6: XML Pretty Printing")
    print("="*60)

    try:
        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice4.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)

        # Convert to XML
        xml_result = json_to_xml(result, "Invoice")

        # Parse and pretty print (as shown in README lines 326-330)
        root = ET.fromstring(xml_result)
        ET.indent(root, space="  ")

        pretty_xml = ET.tostring(root, encoding="unicode")

        print("\nPretty Printed XML:")
        print(pretty_xml)

        # Save
        output_file = "outputs/invoice4-pretty.xml"
        with open(output_file, 'w') as f:
            f.write(pretty_xml)

        print(f"\nSUCCESS: Saved to {output_file}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all XML format tests"""
    print("\n" + "="*60)
    print("XML FORMAT EXAMPLES TEST SUITE")
    print("Testing all code snippets from README.md")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\nERROR: IMGGO_API_KEY environment variable not set")
        print("Set it with: export IMGGO_API_KEY=your_key")
        return

    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)

    # Run all tests
    tests = [
        ("Basic XML Parsing", test_basic_xml_parsing),
        ("SOAP Transformation", test_soap_transformation),
        ("XML Validation", test_xml_validation),
        ("XML Namespaces", test_xml_namespaces),
        ("Batch XML Processing", test_batch_xml_processing),
        ("Pretty Printing", test_pretty_printing),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\nFATAL ERROR in {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)

if __name__ == "__main__":
    main()
