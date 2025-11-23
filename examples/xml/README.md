# XML Output Examples

Complete working examples for converting images to XML using ImgGo API.

## What is XML Output?

XML (eXtensible Markup Language) is essential for:
- Legacy enterprise systems
- SOAP web services
- Industry standards (HL7, EDI, ACORD)
- Government systems
- XML-based APIs and protocols

## Examples Included

### 1. Parking License Plate Recognition
Extract vehicle data in XML format for parking systems.

**Use case**: Parking management, access control

**Output example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ParkingEvent>
  <EventID>evt_20250122_143045_001</EventID>
  <LicensePlate>
    <Number>ABC1234</Number>
    <Jurisdiction>CA</Jurisdiction>
  </LicensePlate>
  <Timestamp>2025-01-22T14:30:45Z</Timestamp>
</ParkingEvent>
```

### 2. VIN Extraction
Extract Vehicle Identification Numbers in XML.

**Use case**: Auto dealerships, DMV systems

**Output example**:
```xml
<VehicleData>
  <VIN>1HGCM82633A123456</VIN>
  <Make>Honda</Make>
  <Model>Accord</Model>
  <Year>2025</Year>
</VehicleData>
```

### 3. Invoice to SOAP XML
Convert invoice images to SOAP-compatible XML messages.

**Use case**: Legacy accounting systems, ERP integration

**Output example**:
```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <Invoice>
      <InvoiceNumber>INV-2025-001</InvoiceNumber>
      <Vendor>Acme Corp</Vendor>
      <Total>1250.00</Total>
    </Invoice>
  </soap:Body>
</soap:Envelope>
```

### 4. XML Transformation
Transform extracted XML using XSLT.

**Use case**: Format conversion, data mapping

### 5. XML Validation
Validate XML against XSD schemas.

**Use case**: Compliance, data quality

## Running the Examples

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export IMGGO_API_KEY="your_api_key_here"
```

### Run All Examples

```bash
python image-to-xml.py
```

### Process Single Image

```python
from imggo_client import ImgGoClient

client = ImgGoClient()
xml_result = client.process_image(
    image_path="parking.jpg",
    pattern_id="pat_parking_xml"
)

# xml_result is an XML string
print(xml_result)

# Save to file
with open("parking_event.xml", "w") as f:
    f.write(xml_result)
```

## Pattern Setup

Create XML patterns at [img-go.com/patterns](https://img-go.com/patterns):

1. Click "New Pattern"
2. Select **XML** as output format
3. Define XML structure in instructions
4. Specify namespace if needed
5. Publish and copy Pattern ID

**Example instructions**:
```
Extract parking event in XML format with this structure:
- Root element: ParkingEvent
- EventID: Unique event identifier
- LicensePlate element containing:
  - Number: License plate text
  - Jurisdiction: State/province code
- Timestamp: ISO 8601 format
- EntryLane: Lane number

Use namespace: http://parking.imggo.com/schema/v1
```

## Integration Examples

### Parse and Process XML

```python
import xml.etree.ElementTree as ET

xml_result = client.process_image("data.jpg", "pat_xml")

# Parse XML
root = ET.fromstring(xml_result)

# Extract values
license_plate = root.find(".//LicensePlate/Number").text
timestamp = root.find(".//Timestamp").text

print(f"License Plate: {license_plate}")
print(f"Time: {timestamp}")
```

### Send to SOAP API

```python
import requests

xml_result = client.process_image("invoice.jpg", "pat_invoice_soap")

# Send SOAP request
response = requests.post(
    "https://api.legacy-system.com/soap/invoices",
    data=xml_result,
    headers={
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://legacy-system.com/ProcessInvoice"
    }
)

print(f"SOAP Response: {response.text}")
```

### Transform with XSLT

```python
from lxml import etree

xml_result = client.process_image("data.jpg", "pat_xml")

# Load XSLT
xslt_doc = etree.parse("transform.xslt")
transform = etree.XSLT(xslt_doc)

# Apply transformation
xml_doc = etree.fromstring(xml_result.encode())
result = transform(xml_doc)

print(str(result))
```

### Validate Against XSD

```python
from lxml import etree

xml_result = client.process_image("parking.jpg", "pat_parking")

# Load XSD schema
with open("parking_schema.xsd", "r") as f:
    schema_doc = etree.parse(f)
    schema = etree.XMLSchema(schema_doc)

# Validate
xml_doc = etree.fromstring(xml_result.encode())

if schema.validate(xml_doc):
    print("✓ XML is valid")
else:
    print("✗ Validation errors:")
    for error in schema.error_log:
        print(f"  Line {error.line}: {error.message}")
```

### Save to XML Database

```python
from lxml import etree
import psycopg2

xml_result = client.process_image("data.jpg", "pat_data")

# Store in PostgreSQL XML column
conn = psycopg2.connect("dbname=mydb user=postgres")
cur = conn.cursor()

cur.execute(
    "INSERT INTO documents (data_xml, created_at) VALUES (%s, NOW())",
    (xml_result,)
)

conn.commit()
```

## Common Use Cases

- **Parking Systems**: LPR data in standard XML format
- **Healthcare**: HL7 messages, medical records
- **Insurance**: ACORD XML for policy data
- **Banking**: ISO 20022 payment messages
- **Government**: XML-based form submissions
- **EDI**: Electronic Data Interchange
- **Manufacturing**: MES system integration
- **Real Estate**: RESO XML property data
- **Legal**: Court filing XML formats
- **Logistics**: Shipping manifest XML

## XML Namespaces

### Default Namespace

```python
# In pattern instructions:
"Use default namespace: http://example.com/schema/v1"
```

### Multiple Namespaces

```python
# In pattern instructions:
"""
Use namespaces:
- Default: http://example.com/data
- soap: http://schemas.xmlsoap.org/soap/envelope/
- xsi: http://www.w3.org/2001/XMLSchema-instance
"""
```

### Parse with Namespace

```python
import xml.etree.ElementTree as ET

xml_result = client.process_image("data.jpg", "pat_ns_xml")
root = ET.fromstring(xml_result)

# Define namespace map
ns = {"p": "http://parking.imggo.com/schema/v1"}

# Find elements with namespace
plate = root.find(".//p:LicensePlate/p:Number", ns).text
```

## Error Handling

```python
import xml.etree.ElementTree as ET

try:
    xml_result = client.process_image("data.jpg", "pat_xml")

    # Validate it's well-formed XML
    try:
        root = ET.fromstring(xml_result)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML: {e}")

    # Check required elements
    if root.find(".//LicensePlate") is None:
        raise ValueError("Missing required LicensePlate element")

except Exception as e:
    print(f"Error processing XML: {e}")
```

## Best Practices

1. **Define clear structure**: Specify element hierarchy in instructions
2. **Use namespaces**: Add xmlns for standard compliance
3. **Validate output**: Check against XSD schemas
4. **Handle special characters**: XML entities (&lt;, &gt;, &amp;)
5. **Pretty print**: Use indentation for readability

## Pretty Printing

```python
import xml.etree.ElementTree as ET

xml_result = client.process_image("data.jpg", "pat_xml")

# Parse and pretty print
root = ET.fromstring(xml_result)
ET.indent(root, space="  ")

pretty_xml = ET.tostring(root, encoding="unicode")
print(pretty_xml)
```

## Batch Processing

```python
import glob
import xml.etree.ElementTree as ET

# Create root element for batch
batch_root = ET.Element("ParkingEvents")

for image_path in glob.glob("images/*.jpg"):
    xml_result = client.process_image(image_path, "pat_parking")

    # Parse individual event
    event = ET.fromstring(xml_result)

    # Add to batch
    batch_root.append(event)

# Save batch XML
tree = ET.ElementTree(batch_root)
tree.write("batch_events.xml", encoding="utf-8", xml_declaration=True)
```

## Support

- [ImgGo API Documentation](https://img-go.com/docs)
- [XML Format Guide](https://img-go.com/docs/output-formats/xml)
- Email: support@img-go.com
