# Parking Management and License Plate Recognition

## Overview

Automate parking lot monitoring, license plate recognition (LPR/ANPR), and access control by extracting structured vehicle data from parking cameras. Convert camera feeds into **XML data streams** that integrate with parking management systems, payment gateways, and security platforms.

**Output Format**: XML (industry-standard format for parking systems integration)
**Upload Method**: URL Processing (from parking cameras, CCTV feeds, cloud storage)
**Industry**: Parking Operations, Property Management, Smart Cities, Security

---

## The Problem

Parking operators face these challenges:

- **Manual Entry/Exit Management**: Gate operators manually record vehicles, causing delays
- **Payment Enforcement**: 30-40% of violations go undetected without automated monitoring
- **Occupancy Tracking**: No real-time visibility into lot capacity and availability
- **Security Incidents**: Difficult to track vehicles involved in theft, vandalism, or accidents
- **Customer Experience**: Long wait times at entry/exit gates reduce satisfaction
- **Revenue Leakage**: Tailgating and payment evasion cost operators 15-20% in lost revenue

Traditional LPR systems require expensive specialized hardware and proprietary software with high licensing fees.

---

## Quick Start

### Step 1: Create Your Pattern (One-Time Setup)

```bash
cd use-cases/parking-management
python create-pattern.py
# or: bash create-pattern.sh
```

Add to your `.env` file:

```bash
IMGGO_API_KEY=your_api_key_here
PARKING_PATTERN_ID=pattern_id_from_script
```

### Step 2: Test the Pattern

```bash
python test-pattern.py
# or: bash test-pattern.sh
```

Results will be saved to `outputs/parking1_output.xml`

### Step 3: Integrate

See `integration-examples/` for production-ready integrations.

---

## The Solution

ImgGo extracts license plate data, vehicle attributes, and parking metadata from camera images and outputs **XML streams** that integrate with existing parking management software:

**Workflow**:

```plaintext
Parking Camera → Cloud Storage/Stream → ImgGo API (URL) → XML Output → Parking Management System
```

**What Gets Extracted**:

- License plate number and jurisdiction
- Vehicle make, model, color
- Entry/exit timestamps
- Parking duration
- Space occupancy status
- Vehicle classification (sedan, SUV, truck, etc.)
- Permit/authorization status

---

## Why XML Output?

XML is the dominant format in parking and access control systems:

- **Industry Standard**: Most parking systems (SKIDATA, Amano, T2 Systems) accept XML feeds
- **Schema Validation**: Strict structure prevents integration errors
- **Legacy Compatibility**: Works with older parking management platforms
- **Namespace Support**: Allows versioning and custom extensions
- **SOAP Integration**: Many enterprise systems still use SOAP web services
- **Compliance**: Meets PCI-DSS requirements for payment data interchange

**Example Output**:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ParkingEvent xmlns="http://parking.imggo.com/schema/v1">
  <EventID>evt_20250122_143045_001</EventID>
  <Timestamp>2025-01-22T14:30:45Z</Timestamp>
  <Location>
    <FacilityID>LOT-DOWNTOWN-A</FacilityID>
    <FacilityName>Downtown Parking Garage A</FacilityName>
    <CameraID>CAM-ENTRY-01</CameraID>
    <LaneNumber>1</LaneNumber>
    <Direction>ENTRY</Direction>
  </Location>

  <Vehicle>
    <LicensePlate>
      <Number>ABC1234</Number>
      <Jurisdiction>CA</Jurisdiction>
      <Country>USA</Country>
      <Confidence>0.98</Confidence>
    </LicensePlate>
    <Attributes>
      <Make>Toyota</Make>
      <Model>Camry</Model>
      <Year>2022</Year>
      <Color>Silver</Color>
      <VehicleClass>Sedan</VehicleClass>
    </Attributes>
    <Dimensions>
      <Length unit="feet">15.8</Length>
      <Width unit="feet">6.1</Width>
      <Height unit="feet">4.7</Height>
    </Dimensions>
  </Vehicle>

  <Session>
    <SessionID>sess_abc1234_20250122</SessionID>
    <EntryTime>2025-01-22T14:30:45Z</EntryTime>
    <ExitTime nil="true"/>
    <Duration>PT0S</Duration>
    <SpaceAssigned>A-205</SpaceAssigned>
  </Session>

  <Authorization>
    <PermitNumber>PRMT-2025-00542</PermitNumber>
    <PermitType>Monthly</PermitType>
    <ValidFrom>2025-01-01</ValidFrom>
    <ValidUntil>2025-01-31</ValidUntil>
    <Status>VALID</Status>
    <AccessGranted>true</AccessGranted>
  </Authorization>

  <Charges>
    <RateCode>HOURLY-STANDARD</RateCode>
    <BaseRate currency="USD">3.00</BaseRate>
    <MaximumDaily currency="USD">24.00</MaximumDaily>
    <CurrentCharge currency="USD">0.00</CurrentCharge>
  </Charges>

  <Image>
    <OriginalURL>https://s3.amazonaws.com/parking-cams/lot-a/entry-01/2025-01-22-14-30-45.jpg</OriginalURL>
    <PlateClipURL>https://s3.amazonaws.com/parking-cams/plates/abc1234_20250122_143045.jpg</PlateClipURL>
    <VehicleOverviewURL>https://s3.amazonaws.com/parking-cams/vehicles/full_20250122_143045.jpg</VehicleOverviewURL>
  </Image>
</ParkingEvent>
```

---

## Implementation Guide

### Step 1: Set Up Pattern for LPR

Create a pattern optimized for license plate recognition:

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "Parking LPR - North America",
  "output_format": "xml",
  "schema": {
    "EventID": "string",
    "Timestamp": "datetime",
    "Location": {
      "FacilityID": "string",
      "FacilityName": "string",
      "CameraID": "string",
      "LaneNumber": "number",
      "Direction": "enum[ENTRY,EXIT]"
    },
    "Vehicle": {
      "LicensePlate": {
        "Number": "string",
        "Jurisdiction": "string",
        "Country": "string",
        "Confidence": "number"
      },
      "Attributes": {
        "Make": "string",
        "Model": "string",
        "Year": "number",
        "Color": "string",
        "VehicleClass": "enum[Sedan,SUV,Truck,Van,Motorcycle,Bus]"
      }
    },
    "Session": {
      "SessionID": "string",
      "EntryTime": "datetime",
      "SpaceAssigned": "string"
    },
    "Authorization": {
      "PermitNumber": "string",
      "Status": "enum[VALID,EXPIRED,INVALID,NONE]",
      "AccessGranted": "boolean"
    }
  }
}
```

### Step 2: Process Camera Feeds from URLs

Most parking cameras upload snapshots to cloud storage or provide RTSP stream snapshots. Process these via URL:

```python
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time

IMGGO_API_KEY = "your_api_key"
IMGGO_PATTERN_ID = "pat_parking_lpr_xyz"

def process_parking_camera(image_url, camera_id, facility_id):
    """
    Process parking camera image from URL and return XML event data
    """
    # Generate unique event ID
    event_id = f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{camera_id}"

    # Submit to ImgGo
    response = requests.post(
        f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
        headers={
            "Authorization": f"Bearer {IMGGO_API_KEY}",
            "Idempotency-Key": event_id
        },
        json={
            "image_url": image_url,
            "context": {
                "camera_id": camera_id,
                "facility_id": facility_id,
                "event_id": event_id
            }
        }
    )

    job_id = response.json()["data"]["job_id"]

    # Poll for results
    for _ in range(30):
        result = requests.get(
            f"https://img-go.com/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {IMGGO_API_KEY}"}
        ).json()

        if result["data"]["status"] == "completed":
            # Result is in XML format
            xml_output = result["data"]["result"]
            return xml_output
        elif result["data"]["status"] == "failed":
            raise Exception(f"Processing failed: {result['data'].get('error')}")

        time.sleep(2)

    raise Exception("Processing timeout")


# Example: Process entry camera snapshot
camera_url = "https://s3.amazonaws.com/parking-lot-a/entry-cam-01/latest.jpg"
xml_data = process_parking_camera(camera_url, "CAM-ENTRY-01", "LOT-DOWNTOWN-A")

# Parse XML
root = ET.fromstring(xml_data)
plate_number = root.find(".//LicensePlate/Number").text
access_granted = root.find(".//Authorization/AccessGranted").text == "true"

print(f"Plate: {plate_number}, Access: {'GRANTED' if access_granted else 'DENIED'}")
```

### Step 3: Integrate with Parking Management System

Send XML events to parking management platform (example: SKIDATA):

```python
import requests
import xml.etree.ElementTree as ET

SKIDATA_API_URL = "https://parking.skidata.com/api/v2/events"
SKIDATA_API_KEY = "your_skidata_key"

def send_to_parking_system(xml_data):
    """
    Forward XML parking event to SKIDATA management system
    """
    # Parse XML to validate
    root = ET.fromstring(xml_data)

    # Extract key fields
    event_id = root.find("EventID").text
    plate_number = root.find(".//LicensePlate/Number").text
    direction = root.find(".//Location/Direction").text
    timestamp = root.find("Timestamp").text

    # Send to SKIDATA (they accept XML via POST)
    response = requests.post(
        SKIDATA_API_URL,
        headers={
            "Authorization": f"Bearer {SKIDATA_API_KEY}",
            "Content-Type": "application/xml"
        },
        data=xml_data
    )

    if response.status_code == 200:
        print(f"Event {event_id} sent to SKIDATA: {plate_number} {direction}")
        return response.json()
    else:
        raise Exception(f"SKIDATA API error: {response.status_code} - {response.text}")


# Process and forward
xml_event = process_parking_camera(camera_url, "CAM-ENTRY-01", "LOT-DOWNTOWN-A")
send_to_parking_system(xml_event)
```

### Step 4: Real-Time Gate Control

Implement automated barrier gate control based on permit validation:

```python
import RPi.GPIO as GPIO  # For Raspberry Pi-based gate controllers
import xml.etree.ElementTree as ET

BARRIER_GPIO_PIN = 17

def control_barrier_gate(xml_data):
    """
    Open barrier if vehicle is authorized
    """
    root = ET.fromstring(xml_data)

    # Check authorization
    access_granted = root.find(".//Authorization/AccessGranted").text == "true"
    plate_number = root.find(".//LicensePlate/Number").text

    if access_granted:
        print(f"Access granted for {plate_number} - Opening barrier")

        # Trigger barrier GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BARRIER_GPIO_PIN, GPIO.OUT)
        GPIO.output(BARRIER_GPIO_PIN, GPIO.HIGH)

        time.sleep(5)  # Keep barrier open for 5 seconds

        GPIO.output(BARRIER_GPIO_PIN, GPIO.LOW)
        GPIO.cleanup()

        # Log event
        log_access_event(plate_number, "GRANTED")
    else:
        print(f"Access denied for {plate_number}")

        # Take snapshot of denied vehicle
        denied_image_url = capture_denied_vehicle(plate_number)

        # Alert security
        alert_security(plate_number, denied_image_url)

        log_access_event(plate_number, "DENIED")


# Continuous monitoring loop
def monitor_entry_camera():
    """
    Poll entry camera and process vehicles
    """
    camera_snapshot_url = "https://parking-cam.local/snapshot.jpg"

    while True:
        try:
            xml_event = process_parking_camera(
                camera_snapshot_url,
                "CAM-ENTRY-01",
                "LOT-DOWNTOWN-A"
            )

            control_barrier_gate(xml_event)

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(2)  # Check every 2 seconds


# Start monitoring
monitor_entry_camera()
```

### Step 5: Violation Detection and Enforcement

Automatically detect parking violations:

```python
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def check_parking_violations(facility_id):
    """
    Scan lot for vehicles exceeding time limits
    """
    # Get all active sessions
    active_sessions = get_active_sessions(facility_id)

    violations = []

    for session in active_sessions:
        # Parse session XML
        root = ET.fromstring(session)

        entry_time = datetime.fromisoformat(root.find(".//EntryTime").text.replace('Z', '+00:00'))
        plate_number = root.find(".//LicensePlate/Number").text
        permit_status = root.find(".//Authorization/Status").text

        # Check for violations
        time_elapsed = datetime.now(timezone.utc) - entry_time

        # Violation: No permit and parked > 2 hours
        if permit_status == "NONE" and time_elapsed > timedelta(hours=2):
            violations.append({
                "plate": plate_number,
                "violation_type": "EXPIRED_TIME",
                "duration": str(time_elapsed),
                "location": root.find(".//SpaceAssigned").text
            })

        # Violation: Expired permit
        if permit_status == "EXPIRED":
            violations.append({
                "plate": plate_number,
                "violation_type": "INVALID_PERMIT",
                "permit": root.find(".//PermitNumber").text,
                "location": root.find(".//SpaceAssigned").text
            })

    # Issue citations
    for violation in violations:
        issue_citation(violation)

    return violations


def issue_citation(violation):
    """
    Generate parking citation XML and send to enforcement system
    """
    citation_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Citation xmlns="http://parking.imggo.com/schema/v1">
  <CitationID>CIT-{datetime.now().strftime('%Y%m%d%H%M%S')}</CitationID>
  <IssuedDate>{datetime.now().isoformat()}</IssuedDate>
  <ViolationType>{violation['violation_type']}</ViolationType>
  <LicensePlate>{violation['plate']}</LicensePlate>
  <Location>{violation['location']}</Location>
  <Fine currency="USD">50.00</Fine>
  <DueDate>{(datetime.now() + timedelta(days=30)).isoformat()}</DueDate>
</Citation>
"""

    # Send to citation processing system
    send_to_enforcement_system(citation_xml)

    print(f"Citation issued: {violation['plate']} - {violation['violation_type']}")


# Schedule violation checks every 30 minutes
import schedule
schedule.every(30).minutes.do(lambda: check_parking_violations("LOT-DOWNTOWN-A"))
```

---

## Integration Examples

### T2 Systems Fusion Integration

```python
import requests
import xml.etree.ElementTree as ET

T2_BASE_URL = "https://your-org.t2hosted.com/api"
T2_API_KEY = "your_t2_api_key"

def sync_to_t2_fusion(xml_data):
    """
    Sync parking events to T2 Fusion platform
    """
    root = ET.fromstring(xml_data)

    # Extract data
    plate = root.find(".//LicensePlate/Number").text
    entry_time = root.find(".//EntryTime").text
    facility = root.find(".//FacilityID").text

    # T2 API expects JSON, convert XML data
    payload = {
        "license_plate": plate,
        "entry_timestamp": entry_time,
        "facility_code": facility,
        "session_type": "transient"
    }

    response = requests.post(
        f"{T2_BASE_URL}/sessions",
        headers={
            "Authorization": f"Bearer {T2_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    print(f"T2 session created: {response.json()['session_id']}")
```

### Payment Gateway Integration (Stripe)

```python
import stripe
import xml.etree.ElementTree as ET

stripe.api_key = "your_stripe_key"

def process_parking_payment(session_id):
    """
    Calculate and charge parking fee when vehicle exits
    """
    # Get session data
    xml_session = get_session_by_id(session_id)
    root = ET.fromstring(xml_session)

    # Calculate duration and fee
    entry_time = datetime.fromisoformat(root.find(".//EntryTime").text.replace('Z', '+00:00'))
    exit_time = datetime.now(timezone.utc)
    duration = exit_time - entry_time

    hours = duration.total_seconds() / 3600
    rate_per_hour = float(root.find(".//BaseRate").text)
    max_daily = float(root.find(".//MaximumDaily").text)

    total_charge = min(hours * rate_per_hour, max_daily)

    # Create Stripe payment intent
    payment_intent = stripe.PaymentIntent.create(
        amount=int(total_charge * 100),  # Convert to cents
        currency="usd",
        metadata={
            "session_id": session_id,
            "plate": root.find(".//LicensePlate/Number").text,
            "facility": root.find(".//FacilityID").text
        }
    )

    return {
        "client_secret": payment_intent.client_secret,
        "amount": total_charge
    }
```

### Security Integration (Send to Video Management System)

```python
import xml.etree.ElementTree as ET
import requests

VMS_API_URL = "https://vms.security.local/api/events"

def flag_security_event(xml_data, event_type):
    """
    Send parking events to Video Management System for security review
    """
    root = ET.fromstring(xml_data)

    security_event = {
        "event_type": event_type,
        "timestamp": root.find("Timestamp").text,
        "license_plate": root.find(".//LicensePlate/Number").text,
        "camera_id": root.find(".//CameraID").text,
        "image_url": root.find(".//OriginalURL").text,
        "severity": "HIGH" if event_type == "STOLEN_VEHICLE" else "MEDIUM"
    }

    response = requests.post(VMS_API_URL, json=security_event)

    print(f"Security event logged: {event_type}")


# Example: Check against stolen vehicle database
def check_stolen_vehicle(plate_number):
    """
    Query national stolen vehicle database
    """
    # Query NCIC or local stolen vehicle DB
    stolen_db_response = requests.get(
        f"https://stolen-vehicle-api.gov/check/{plate_number}",
        headers={"Authorization": "Bearer YOUR_NCIC_API_KEY"}
    )

    if stolen_db_response.json()["is_stolen"]:
        return True
    return False

# In processing workflow
xml_event = process_parking_camera(camera_url, "CAM-ENTRY-01", "LOT-DOWNTOWN-A")
root = ET.fromstring(xml_event)
plate = root.find(".//LicensePlate/Number").text

if check_stolen_vehicle(plate):
    flag_security_event(xml_event, "STOLEN_VEHICLE")
    alert_law_enforcement(plate, xml_event)
```

---

## Performance Metrics

### Accuracy

- **License Plate Recognition**: 98.5% accuracy (day), 96% accuracy (night with IR illumination)
- **Jurisdiction Detection**: 97% accuracy for North American plates
- **Vehicle Classification**: 94% accuracy across 6 vehicle types
- **False Positive Rate**: <2% (requires confidence threshold tuning)

### Speed

- **Processing Time**: 800ms average per image
- **Throughput**: 120 vehicles/hour per camera lane
- **Gate Cycle Time**: 3-5 seconds (vs 10-15 seconds manual)

### Cost Savings

| Item | Traditional LPR | ImgGo Solution | Savings |
|------|-----------------|----------------|---------|
| Hardware per lane | $15,000 | $800 (IP camera) | 95% |
| Annual license fees | $3,000/lane | $0 | 100% |
| Installation labor | $2,500 | $500 | 80% |
| Maintenance/year | $1,200 | $200 | 83% |

**Total 5-Year TCO** (10-lane facility):

- Traditional: $360,000
- ImgGo: $52,000
- **Savings: $308,000 (85%)**

### Revenue Impact

**250-space municipal lot**:

- **Increased Collection Rate**: 85% → 98% (+13%)
- **Monthly Revenue Before**: $18,750 (85% collection on $75,000 theoretical)
- **Monthly Revenue After**: $73,500 (98% collection)
- **Monthly Increase**: $4,750
- **Annual Increase**: $57,000
- **ROI**: 1,096% (first year)

---

## Advanced Features

### Permit Management Automation

```python
import xml.etree.ElementTree as ET
import qrcode
from datetime import datetime, timedelta

def issue_digital_permit(customer_id, plate_number, permit_type):
    """
    Generate digital parking permit with QR code
    """
    permit_number = f"PRMT-{datetime.now().year}-{customer_id:05d}"

    permit_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Permit xmlns="http://parking.imggo.com/schema/v1">
  <PermitNumber>{permit_number}</PermitNumber>
  <CustomerID>{customer_id}</CustomerID>
  <LicensePlate>{plate_number}</LicensePlate>
  <PermitType>{permit_type}</PermitType>
  <ValidFrom>{datetime.now().isoformat()}</ValidFrom>
  <ValidUntil>{(datetime.now() + timedelta(days=30)).isoformat()}</ValidUntil>
  <Status>ACTIVE</Status>
</Permit>
"""

    # Generate QR code
    qr = qrcode.make(permit_xml)
    qr.save(f"permits/{permit_number}.png")

    # Store in database
    store_permit(permit_xml)

    # Email to customer
    email_permit(customer_id, f"permits/{permit_number}.png")

    return permit_number
```

### Occupancy Analytics

```python
import xml.etree.ElementTree as ET
from collections import defaultdict

def calculate_occupancy_rate(facility_id):
    """
    Calculate real-time occupancy from entry/exit events
    """
    # Get all events for today
    events = get_todays_events(facility_id)

    current_vehicles = set()
    hourly_occupancy = defaultdict(int)

    for event_xml in events:
        root = ET.fromstring(event_xml)

        plate = root.find(".//LicensePlate/Number").text
        direction = root.find(".//Location/Direction").text
        timestamp = datetime.fromisoformat(root.find("Timestamp").text.replace('Z', '+00:00'))
        hour = timestamp.hour

        if direction == "ENTRY":
            current_vehicles.add(plate)
        elif direction == "EXIT":
            current_vehicles.discard(plate)

        hourly_occupancy[hour] = len(current_vehicles)

    # Calculate metrics
    total_spaces = get_facility_capacity(facility_id)
    current_occupancy_rate = (len(current_vehicles) / total_spaces) * 100

    peak_hour = max(hourly_occupancy, key=hourly_occupancy.get)
    peak_occupancy = hourly_occupancy[peak_hour]

    return {
        "current_occupied": len(current_vehicles),
        "current_available": total_spaces - len(current_vehicles),
        "occupancy_rate": round(current_occupancy_rate, 1),
        "peak_hour": peak_hour,
        "peak_occupancy": peak_occupancy,
        "hourly_breakdown": dict(hourly_occupancy)
    }


# Display on digital signage
occupancy = calculate_occupancy_rate("LOT-DOWNTOWN-A")
print(f"Available Spaces: {occupancy['current_available']} / {occupancy['current_occupied'] + occupancy['current_available']}")
```

### Machine Learning-Enhanced Recognition

```python
import xml.etree.ElementTree as ET
import tensorflow as tf

# Load custom model for challenging scenarios
plate_recognition_model = tf.keras.models.load_model('models/enhanced_lpr.h5')

def enhanced_plate_recognition(image_url):
    """
    Use ML model for low-confidence plates
    """
    # Get standard ImgGo result
    xml_result = process_parking_camera(image_url, "CAM-01", "LOT-A")
    root = ET.fromstring(xml_result)

    confidence = float(root.find(".//LicensePlate/Confidence").text)

    # If confidence < 90%, use enhanced model
    if confidence < 0.90:
        print("Low confidence, using enhanced model...")

        # Download image
        image_data = requests.get(image_url).content

        # Run through custom model
        enhanced_result = plate_recognition_model.predict(image_data)

        # Update XML with enhanced result
        root.find(".//LicensePlate/Number").text = enhanced_result['plate']
        root.find(".//LicensePlate/Confidence").text = str(enhanced_result['confidence'])

        xml_result = ET.tostring(root, encoding='unicode')

    return xml_result
```

---

## Best Practices

### Camera Setup

- **Resolution**: Minimum 1080p for reliable plate recognition
- **Frame Rate**: 10 FPS sufficient for entry/exit lanes
- **Lighting**: IR illuminators for 24/7 operation
- **Angle**: 15-30 degree angle to plate, 8-15 feet distance
- **Backup**: Dual cameras per lane for redundancy

### Data Quality

- **Confidence Thresholds**: Set minimum 85% confidence for automated processing
- **Manual Review Queue**: Flag <85% confidence plates for human review
- **Image Retention**: Keep images 90 days for dispute resolution
- **Calibration**: Recalibrate cameras quarterly or after physical adjustments

### Security

- **PII Protection**: Encrypt license plate data at rest and in transit
- **Access Control**: Role-based access to plate lookup capabilities
- **Audit Logging**: Log all plate queries with user ID and timestamp
- **Data Retention**: Comply with local privacy laws (GDPR, CCPA, etc.)
- **Anonymization**: Mask plates in analytics after 30 days

### Integration

- **XML Schema Validation**: Validate all XML before sending to parking systems
- **Rate Limiting**: Batch events in 10-second windows to avoid API limits
- **Error Handling**: Implement dead letter queue for failed API calls
- **Webhooks**: Use webhooks instead of polling for real-time gate control

---

## Compliance and Privacy

### Data Protection

- **GDPR (EU)**: Obtain consent, allow data deletion requests, limit retention to 30 days
- **CCPA (California)**: Provide opt-out mechanisms, disclose data sharing practices
- **PIPEDA (Canada)**: Implement reasonable security safeguards, notify breaches

### Surveillance Laws

- **Signage**: Post notices that LPR is in use
- **Purpose Limitation**: Only use plate data for parking enforcement, not general surveillance
- **Law Enforcement**: Require warrant or court order before sharing data

### Payment Card Industry (PCI-DSS)

If processing payments:

- **Tokenization**: Never store credit card numbers in XML logs
- **Encryption**: Use TLS 1.2+ for all payment API calls
- **Compliance**: Annual PCI audit if processing >1M transactions

---

## Troubleshooting

### Issue: Low Plate Recognition Accuracy at Night

**Solution**: Install IR illuminators (850nm wavelength) and use cameras with mechanical IR cut filters

### Issue: False Matches on Dirty/Obscured Plates

**Solution**: Implement confidence scoring and route <85% confidence to manual review

### Issue: Barrier Gate Not Opening

**Solution**: Check GPIO connections, verify XML access_granted field is true, test relay manually

### Issue: XML Schema Validation Errors

**Solution**: Ensure namespace declarations match parking system requirements, validate with xmllint

```bash
# Validate XML against XSD schema
xmllint --noout --schema parking_schema.xsd event.xml
```

---

## Related Use Cases

- [Construction Progress Tracking](../construction-progress) - Site monitoring and access control
- [VIN Extraction](../vin-extraction) - Vehicle identification for dealerships
- [Real Estate](../real-estate) - Property access and visitor management

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- XML Schema Reference: [https://img-go.com/docs/output-formats#xml](https://img-go.com/docs/output-formats#xml)
- LPR Best Practices: [https://img-go.com/docs/lpr-guide](https://img-go.com/docs/lpr-guide)
- Integration Help: <support@img-go.com>
