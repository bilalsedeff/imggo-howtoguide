# Real Estate Property Inspections and Punch Lists

## Overview

Automate property inspections, move-in/move-out reports, and construction punch lists by extracting defects, measurements, and property conditions from inspection photos. Convert visual documentation into **structured JSON** that integrates with property management systems and CRMs.

**Output Format**: JSON (structured data for property management platforms)
**Upload Method**: URL Processing (from cloud storage, inspection apps, photographer uploads)
**Industry**: Residential Real Estate, Commercial Property Management, Property Inspection, Construction Closeout

---

## The Problem

Property managers and real estate professionals face these inspection challenges:

- **Slow Documentation**: Inspectors spend 2-3 hours post-inspection writing reports
- **Inconsistent Quality**: 30% of inspection reports miss critical defects
- **Delayed Closings**: Late inspection reports delay property closings by 5-7 days
- **Dispute Resolution**: Missing documentation leads to security deposit disputes
- **Maintenance Backlogs**: Punch lists buried in PDFs never get actioned
- **Compliance Gaps**: Missing safety or code violations create liability

Traditional methods require inspectors to manually type observations, measurements, and defect descriptions while reviewing hundreds of photos after site visits.

---

## The Solution

ImgGo extracts property conditions, defects, and measurements from inspection photos and outputs **structured JSON** that integrates directly with property management systems:

**Workflow**:

```
Inspection Photos (Cloud Storage URL) → ImgGo API → JSON Output → Property Management System
```

**What Gets Extracted**:

- Room-by-room condition assessments
- Defects and damage descriptions
- Measurements and dimensions
- Appliance conditions and model numbers
- Safety hazards
- Code violations
- Recommended repairs and cost estimates

---

## Why JSON Output?

JSON is ideal for property inspection workflows:

- **CRM Integration**: Direct API integration with Salesforce, HubSpot, etc.
- **Property Management**: Works with Buildium, AppFolio, Yardi, MRI
- **Mobile Apps**: Easy consumption in inspection mobile applications
- **Conditional Logic**: Trigger workflows based on defect severity
- **Search and Filter**: Query inspections by defect type, cost, room
- **Versioning**: Track changes between initial and final inspections

**Example Output** (Move-In Inspection):

```json
{
  "inspection": {
    "inspection_id": "INSP-2025-001234",
    "property_id": "PROP-789",
    "property_address": "456 Oak Street, Apt 3B, San Francisco, CA 94102",
    "inspection_type": "move_in",
    "inspection_date": "2025-01-22",
    "inspector": {
      "name": "Sarah Johnson",
      "inspector_id": "INS-042",
      "license": "CRI-45821-CA"
    },
    "tenant": {
      "name": "John Smith",
      "tenant_id": "TEN-5423",
      "move_in_date": "2025-01-25"
    }
  },

  "overall_assessment": {
    "overall_condition": "good",
    "total_defects": 8,
    "critical_issues": 0,
    "estimated_repair_cost": 650.00,
    "move_in_ready": true
  },

  "rooms": [
    {
      "room_id": "LIV-01",
      "room_name": "Living Room",
      "dimensions": {
        "length_feet": 18.5,
        "width_feet": 14.2,
        "height_feet": 9.0,
        "square_feet": 262.7
      },
      "condition": "good",
      "defects": [
        {
          "defect_id": "DEF-001",
          "category": "walls",
          "severity": "minor",
          "description": "Small nail holes (6) in west wall from previous tenant artwork",
          "location": "West wall, approximately 5 feet from floor",
          "dimensions": "0.25 inch diameter",
          "repair_required": "Spackle and paint",
          "estimated_cost": 45.00,
          "responsible_party": "landlord",
          "image_url": "https://s3.amazonaws.com/inspections/prop-789/living-room-wall-holes.jpg"
        },
        {
          "defect_id": "DEF-002",
          "category": "flooring",
          "severity": "minor",
          "description": "Light scratches on hardwood floor near window",
          "location": "North side of room, 3 feet from window",
          "dimensions": "12 inch linear scratch",
          "repair_required": "Minor refinishing",
          "estimated_cost": 120.00,
          "responsible_party": "landlord",
          "image_url": "https://s3.amazonaws.com/inspections/prop-789/floor-scratches.jpg"
        }
      ],
      "features": {
        "flooring_type": "hardwood",
        "flooring_condition": "good",
        "ceiling_type": "drywall",
        "ceiling_condition": "excellent",
        "windows": {
          "count": 2,
          "type": "double_hung",
          "condition": "good",
          "operational": true
        },
        "outlets": {
          "count": 4,
          "functional": true
        },
        "lighting": {
          "fixtures": 1,
          "type": "ceiling_fan_with_light",
          "operational": true
        }
      }
    },

    {
      "room_id": "KIT-01",
      "room_name": "Kitchen",
      "dimensions": {
        "length_feet": 12.0,
        "width_feet": 10.5,
        "square_feet": 126.0
      },
      "condition": "fair",
      "defects": [
        {
          "defect_id": "DEF-003",
          "category": "appliances",
          "severity": "moderate",
          "description": "Refrigerator ice maker not functioning",
          "location": "Built-in refrigerator",
          "appliance_details": {
            "make": "GE",
            "model": "GSS25GSHSS",
            "serial": "VH123456"
          },
          "repair_required": "Ice maker repair or replacement",
          "estimated_cost": 250.00,
          "responsible_party": "landlord",
          "required_before_move_in": false,
          "image_url": "https://s3.amazonaws.com/inspections/prop-789/refrigerator.jpg"
        },
        {
          "defect_id": "DEF-004",
          "category": "countertops",
          "severity": "minor",
          "description": "Small chip in granite countertop near sink",
          "location": "Right side of sink, 6 inches from edge",
          "dimensions": "1 inch diameter, 0.5 inch deep",
          "repair_required": "Granite chip repair",
          "estimated_cost": 85.00,
          "responsible_party": "landlord",
          "image_url": "https://s3.amazonaws.com/inspections/prop-789/countertop-chip.jpg"
        }
      ],
      "features": {
        "countertop_type": "granite",
        "countertop_condition": "good",
        "cabinet_type": "wood",
        "cabinet_condition": "good",
        "sink_type": "undermount_stainless",
        "sink_condition": "excellent",
        "appliances": [
          {
            "type": "refrigerator",
            "make": "GE",
            "model": "GSS25GSHSS",
            "condition": "good",
            "operational": "partial",
            "notes": "Ice maker not working"
          },
          {
            "type": "range",
            "make": "Frigidaire",
            "model": "FGEF3036TF",
            "condition": "excellent",
            "operational": true
          },
          {
            "type": "dishwasher",
            "make": "Bosch",
            "model": "SHE3AR75UC",
            "condition": "good",
            "operational": true
          },
          {
            "type": "microwave",
            "make": "GE",
            "model": "JVM3160RFSS",
            "condition": "good",
            "operational": true
          }
        ]
      }
    },

    {
      "room_id": "BATH-01",
      "room_name": "Bathroom",
      "dimensions": {
        "length_feet": 8.0,
        "width_feet": 6.5,
        "square_feet": 52.0
      },
      "condition": "good",
      "defects": [
        {
          "defect_id": "DEF-005",
          "category": "plumbing",
          "severity": "minor",
          "description": "Slow drain in sink",
          "location": "Bathroom sink",
          "repair_required": "Drain cleaning",
          "estimated_cost": 75.00,
          "responsible_party": "landlord",
          "required_before_move_in": true,
          "image_url": "https://s3.amazonaws.com/inspections/prop-789/bathroom-sink.jpg"
        }
      ],
      "features": {
        "flooring_type": "ceramic_tile",
        "flooring_condition": "excellent",
        "shower_type": "tub_shower_combo",
        "shower_condition": "good",
        "toilet_condition": "excellent",
        "vanity_condition": "good",
        "exhaust_fan": {
          "present": true,
          "operational": true
        }
      }
    }
  ],

  "safety_and_compliance": {
    "smoke_detectors": {
      "count": 2,
      "locations": ["Hallway", "Bedroom"],
      "operational": true,
      "batteries_replaced": true
    },
    "carbon_monoxide_detector": {
      "present": true,
      "location": "Hallway",
      "operational": true
    },
    "fire_extinguisher": {
      "present": true,
      "location": "Kitchen",
      "last_inspection": "2024-11-15",
      "expiration": "2025-11-15"
    },
    "gfci_outlets": {
      "kitchen": true,
      "bathrooms": true,
      "tested": true,
      "operational": true
    },
    "code_violations": []
  },

  "utilities": {
    "electric": {
      "panel_location": "Kitchen closet",
      "panel_condition": "good",
      "labeled": true
    },
    "water": {
      "shutoff_location": "Under kitchen sink",
      "accessible": true
    },
    "hvac": {
      "type": "central_air",
      "last_service": "2024-10-05",
      "filter_changed": true,
      "operational": true
    }
  },

  "action_items": [
    {
      "action_id": "ACT-001",
      "description": "Repair refrigerator ice maker",
      "priority": "medium",
      "responsible": "landlord",
      "estimated_cost": 250.00,
      "required_before_move_in": false,
      "deadline": "2025-02-15"
    },
    {
      "action_id": "ACT-002",
      "description": "Clean bathroom sink drain",
      "priority": "high",
      "responsible": "landlord",
      "estimated_cost": 75.00,
      "required_before_move_in": true,
      "deadline": "2025-01-24"
    },
    {
      "action_id": "ACT-003",
      "description": "Repair granite chip and spackle living room walls",
      "priority": "low",
      "responsible": "landlord",
      "estimated_cost": 130.00,
      "required_before_move_in": false,
      "deadline": "2025-03-01"
    }
  ],

  "signatures": {
    "inspector_signature": "Sarah Johnson, 2025-01-22T16:45:00Z",
    "tenant_signature": null,
    "landlord_signature": null,
    "tenant_acknowledged": false,
    "landlord_acknowledged": false
  }
}
```

---

## Implementation Guide

### Step 1: Create Property Inspection Pattern

Define JSON schema for comprehensive property inspections:

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "Property Inspection - Move In/Out",
  "output_format": "json",
  "schema": {
    "inspection": {
      "inspection_id": "string",
      "property_id": "string",
      "property_address": "string",
      "inspection_type": "enum[move_in,move_out,annual,pre_sale,punch_list]",
      "inspection_date": "date",
      "inspector": {
        "name": "string",
        "inspector_id": "string"
      }
    },
    "rooms": [
      {
        "room_name": "string",
        "condition": "enum[excellent,good,fair,poor]",
        "defects": [
          {
            "category": "string",
            "severity": "enum[minor,moderate,major,critical]",
            "description": "string",
            "location": "string",
            "repair_required": "string",
            "estimated_cost": "number",
            "responsible_party": "enum[landlord,tenant,builder]"
          }
        ],
        "features": {
          "appliances": [
            {
              "type": "string",
              "make": "string",
              "model": "string",
              "condition": "string",
              "operational": "boolean"
            }
          ]
        }
      }
    ],
    "safety_and_compliance": {
      "smoke_detectors": {
        "count": "number",
        "operational": "boolean"
      },
      "code_violations": ["string"]
    },
    "action_items": [
      {
        "description": "string",
        "priority": "enum[low,medium,high,urgent]",
        "estimated_cost": "number",
        "required_before_move_in": "boolean"
      }
    ]
  }
}
```

### Step 2: Process Inspection Photos from URLs

Most inspectors upload photos to cloud storage (Dropbox, Google Drive, S3):

```python
import requests
import json
from datetime import datetime
import time

IMGGO_API_KEY = "your_api_key"
IMGGO_PATTERN_ID = "pat_property_inspection_xyz"

def process_inspection_photos(photo_urls, property_id, inspection_type):
    """
    Process multiple inspection photos from URLs and generate comprehensive JSON report
    """
    all_results = []

    for photo_url in photo_urls:
        # Submit each photo to ImgGo
        response = requests.post(
            f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
            headers={
                "Authorization": f"Bearer {IMGGO_API_KEY}",
                "Idempotency-Key": f"{property_id}-{datetime.now().timestamp()}"
            },
            json={
                "image_url": photo_url,
                "context": {
                    "property_id": property_id,
                    "inspection_type": inspection_type
                }
            }
        )

        job_id = response.json()["data"]["job_id"]

        # Poll for result
        result = poll_for_result(job_id)
        all_results.append(result)

        print(f"Processed {photo_url}")

    # Consolidate results into single inspection report
    consolidated_report = consolidate_inspection_results(all_results, property_id)

    return consolidated_report


def poll_for_result(job_id):
    """Poll ImgGo API until job completes"""
    for _ in range(30):
        response = requests.get(
            f"https://img-go.com/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {IMGGO_API_KEY}"}
        ).json()

        if response["data"]["status"] == "completed":
            return response["data"]["result"]
        elif response["data"]["status"] == "failed":
            raise Exception(f"Job failed: {response['data'].get('error')}")

        time.sleep(2)

    raise Exception("Job timeout")


def consolidate_inspection_results(results, property_id):
    """Consolidate multiple photo results into single JSON report"""
    # Merge rooms, defects, and features from all photos
    consolidated = {
        "inspection": {
            "inspection_id": f"INSP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "property_id": property_id,
            "inspection_date": datetime.now().isoformat(),
            "inspector": results[0]["inspection"]["inspector"]
        },
        "rooms": [],
        "safety_and_compliance": {},
        "action_items": []
    }

    # Aggregate defects by room
    room_map = {}

    for result in results:
        for room in result.get("rooms", []):
            room_name = room["room_name"]

            if room_name not in room_map:
                room_map[room_name] = room
            else:
                # Merge defects
                room_map[room_name]["defects"].extend(room.get("defects", []))

    consolidated["rooms"] = list(room_map.values())

    # Calculate overall assessment
    all_defects = [d for room in consolidated["rooms"] for d in room.get("defects", [])]
    consolidated["overall_assessment"] = {
        "total_defects": len(all_defects),
        "critical_issues": len([d for d in all_defects if d["severity"] == "critical"]),
        "estimated_repair_cost": sum(d.get("estimated_cost", 0) for d in all_defects)
    }

    return consolidated


# Example: Process inspection from Dropbox
inspection_photos = [
    "https://www.dropbox.com/s/abc123/living-room-1.jpg?dl=1",
    "https://www.dropbox.com/s/abc124/living-room-2.jpg?dl=1",
    "https://www.dropbox.com/s/abc125/kitchen-1.jpg?dl=1",
    "https://www.dropbox.com/s/abc126/bathroom-1.jpg?dl=1",
    "https://www.dropbox.com/s/abc127/bedroom-1.jpg?dl=1"
]

inspection_report = process_inspection_photos(inspection_photos, "PROP-789", "move_in")

# Save JSON report
with open(f"inspection_PROP-789_{datetime.now().strftime('%Y-%m-%d')}.json", "w") as f:
    json.dump(inspection_report, f, indent=2)

print(f"Inspection complete: {inspection_report['overall_assessment']['total_defects']} defects found")
print(f"Estimated repairs: ${inspection_report['overall_assessment']['estimated_repair_cost']:.2f}")
```

### Step 3: Integrate with Property Management System

Send inspection data to Buildium/AppFolio:

```python
import requests
import json

BUILDIUM_API_URL = "https://api.buildium.com/v1"
BUILDIUM_API_KEY = os.environ['BUILDIUM_API_KEY']

def create_buildium_inspection(inspection_json):
    """
    Create inspection record in Buildium and work orders for defects
    """
    # Create inspection record
    inspection_response = requests.post(
        f"{BUILDIUM_API_URL}/properties/{inspection_json['inspection']['property_id']}/inspections",
        headers={
            "Authorization": f"Bearer {BUILDIUM_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "InspectionDate": inspection_json["inspection"]["inspection_date"],
            "InspectionType": inspection_json["inspection"]["inspection_type"],
            "Notes": f"Total defects: {inspection_json['overall_assessment']['total_defects']}, Estimated cost: ${inspection_json['overall_assessment']['estimated_repair_cost']}"
        }
    )

    inspection_id = inspection_response.json()["Id"]
    print(f"Created Buildium inspection: {inspection_id}")

    # Create work orders for each action item
    for action in inspection_json.get("action_items", []):
        if action.get("required_before_move_in"):
            priority = "Urgent"
        elif action["priority"] == "high":
            priority = "High"
        else:
            priority = "Normal"

        work_order_response = requests.post(
            f"{BUILDIUM_API_URL}/workorders",
            headers={
                "Authorization": f"Bearer {BUILDIUM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "PropertyId": inspection_json["inspection"]["property_id"],
                "Subject": action["description"],
                "Priority": priority,
                "DueDate": action.get("deadline"),
                "EstimatedCost": action.get("estimated_cost"),
                "Notes": f"From inspection {inspection_id}"
            }
        )

        print(f"Created work order: {work_order_response.json()['Id']}")

    return inspection_id


# Send to Buildium
buildium_inspection_id = create_buildium_inspection(inspection_report)
```

### Step 4: Generate PDF Reports

Create customer-facing PDF reports from JSON:

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import json

def generate_pdf_report(inspection_json, output_filename):
    """
    Generate professional PDF inspection report from JSON
    """
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph(f"<b>Property Inspection Report</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # Property details
    property_info = f"""
    <b>Property:</b> {inspection_json['inspection']['property_address']}<br/>
    <b>Inspection Date:</b> {inspection_json['inspection']['inspection_date']}<br/>
    <b>Inspector:</b> {inspection_json['inspection']['inspector']['name']}<br/>
    <b>Type:</b> {inspection_json['inspection']['inspection_type'].replace('_', ' ').title()}
    """

    story.append(Paragraph(property_info, styles['Normal']))
    story.append(Spacer(1, 20))

    # Overall assessment
    assessment = inspection_json['overall_assessment']
    summary = f"""
    <b>Overall Assessment</b><br/>
    Total Defects: {assessment['total_defects']}<br/>
    Critical Issues: {assessment['critical_issues']}<br/>
    Estimated Repair Cost: ${assessment['estimated_repair_cost']:.2f}
    """

    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 20))

    # Room-by-room details
    story.append(Paragraph("<b>Room Details</b>", styles['Heading2']))

    for room in inspection_json['rooms']:
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>{room['room_name']}</b> - Condition: {room['condition'].title()}", styles['Heading3']))

        if room.get('defects'):
            defect_data = [["Category", "Severity", "Description", "Est. Cost"]]

            for defect in room['defects']:
                defect_data.append([
                    defect['category'],
                    defect['severity'].upper(),
                    defect['description'][:50] + "..." if len(defect['description']) > 50 else defect['description'],
                    f"${defect.get('estimated_cost', 0):.2f}"
                ])

            defect_table = Table(defect_data, colWidths=[100, 80, 250, 80])
            defect_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(defect_table)

    # Action items
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Required Actions</b>", styles['Heading2']))

    action_data = [["Priority", "Description", "Deadline", "Cost"]]

    for action in inspection_json.get('action_items', []):
        action_data.append([
            action['priority'].upper(),
            action['description'][:60],
            action.get('deadline', 'TBD'),
            f"${action.get('estimated_cost', 0):.2f}"
        ])

    action_table = Table(action_data, colWidths=[80, 280, 100, 80])
    action_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(action_table)

    # Build PDF
    doc.build(story)
    print(f"PDF report generated: {output_filename}")


# Generate PDF from JSON
generate_pdf_report(inspection_report, "inspection_PROP-789.pdf")
```

---

## Integration Examples

### Zillow/MLS Integration

```python
import requests

def create_listing_with_inspection_data(inspection_json, listing_price):
    """
    Create property listing with inspection data for transparency
    """
    # Extract key selling points
    selling_points = []

    for room in inspection_json['rooms']:
        if room['condition'] in ['excellent', 'good']:
            selling_points.append(f"{room['room_name']}: {room['condition']}")

    # Check for recent updates
    if inspection_json['safety_and_compliance']['smoke_detectors']['operational']:
        selling_points.append("Safety systems up to code")

    # MLS listing payload
    listing = {
        "address": inspection_json['inspection']['property_address'],
        "price": listing_price,
        "description": f"Well-maintained property. Recent inspection shows {inspection_json['overall_assessment']['total_defects']} minor items, all addressed. " + ", ".join(selling_points[:3]),
        "inspection_report_url": upload_to_public_storage(inspection_json),
        "condition": inspection_json['overall_assessment']['overall_condition']
    }

    # Submit to MLS
    response = requests.post(
        "https://api.mlsgrid.com/v2/listings",
        headers={"Authorization": f"Bearer {MLS_API_KEY}"},
        json=listing
    )

    return response.json()['listing_id']
```

### Construction Punch List Integration

```python
def convert_to_punch_list(inspection_json):
    """
    Convert final inspection into construction punch list for contractor
    """
    punch_list = {
        "project_id": inspection_json['inspection']['property_id'],
        "inspection_date": inspection_json['inspection']['inspection_date'],
        "items": []
    }

    item_number = 1

    for room in inspection_json['rooms']:
        for defect in room.get('defects', []):
            punch_list['items'].append({
                "item_number": item_number,
                "location": f"{room['room_name']} - {defect['location']}",
                "issue": defect['description'],
                "responsible_trade": determine_trade(defect['category']),
                "priority": defect['severity'],
                "status": "open",
                "photo_url": defect.get('image_url')
            })
            item_number += 1

    return punch_list


def determine_trade(category):
    """Map defect category to construction trade"""
    trade_map = {
        "walls": "Drywall/Paint",
        "plumbing": "Plumber",
        "electrical": "Electrician",
        "flooring": "Flooring",
        "appliances": "Appliance Installer",
        "hvac": "HVAC Technician"
    }

    return trade_map.get(category, "General Contractor")


# Send punch list to project management
punch_list = convert_to_punch_list(inspection_report)
send_to_procore(punch_list)
```

---

## Performance Metrics

### Time Savings

| Task | Manual Process | With ImgGo | Savings |
|------|----------------|------------|---------|
| Write inspection report | 2.5 hours | 15 minutes | 90% |
| Room-by-room documentation | 1.5 hours | Automated | 100% |
| Generate PDF report | 45 minutes | 2 minutes | 96% |
| Create work orders | 30 minutes | Automated | 100% |
| **Total per inspection** | **5.25 hours** | **17 minutes** | **95%** |

### Business Impact

**Property management company** (500 units, 100 move-in/move-out inspections monthly):

- **Inspector Time Saved**: $75,000/year (525 hours/month × $15/hour × 12 months)
- **Faster Turnarounds**: $120,000/year (reduced vacancy from faster inspections)
- **Dispute Prevention**: $45,000/year (detailed documentation reduces security deposit disputes)
- **Work Order Efficiency**: $30,000/year (automated work order creation)
- **Total Annual Benefit**: $270,000
- **ImgGo Cost**: $18,000/year
- **ROI**: 1,400%

---

## Best Practices

### Photo Quality

- **Consistent Angles**: Take photos from same position each inspection for comparisons
- **Complete Coverage**: Capture all 4 walls, floor, ceiling of each room
- **Close-ups**: Photograph defects from multiple distances (wide, medium, close)
- **Lighting**: Use natural light when possible, avoid flash reflections

### Inspection Process

- **Standardization**: Use same photo sequence for every property
- **Checklists**: Verify all required photos taken before leaving site
- **Timestamps**: Ensure camera/phone time is accurate for records
- **Backups**: Upload photos to cloud immediately in case of device loss

### Data Management

- **Archive**: Retain inspection JSON and photos for 7 years
- **Version Control**: Track changes between initial and follow-up inspections
- **Access Control**: Limit inspection data access to authorized personnel
- **Privacy**: Redact tenant personal information before sharing reports

---

## Troubleshooting

### Issue: Inaccurate Measurements

**Solution**: Include reference objects (measuring tape, standard furniture) in photos

### Issue: Missing Defects

**Solution**: Train pattern with diverse examples, manually review critical inspections

### Issue: Poor Room Classification

**Solution**: Include room name labels or context in filenames/URLs

---

## Related Use Cases

- [Construction Progress](../construction-progress) - Project site monitoring
- [Insurance Claims](../insurance-claims) - Property damage assessment
- [Field Service](../field-service) - Maintenance and repair documentation

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- JSON Schema Guide: [https://img-go.com/docs/output-formats#json](https://img-go.com/docs/output-formats#json)
- Integration Help: <support@img-go.com>
