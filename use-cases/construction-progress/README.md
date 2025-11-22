# Construction Progress Tracking

## Overview

Automate construction site monitoring by extracting structured progress data from time-lapse photos, drone footage, and site cameras. Convert visual documentation into **YAML configuration files** that integrate with project management systems like Procore, Autodesk BIM 360, and Oracle Primavera.

**Output Format**: YAML (structured hierarchical data ideal for progress configs)
**Upload Method**: URL Processing (from site cameras, drones, cloud storage)
**Industry**: Construction, Real Estate Development, Infrastructure

---

## The Problem

Construction project managers face these challenges:

- **Manual Progress Reports**: Site supervisors spend 5-10 hours weekly creating progress reports
- **Delayed Updates**: Progress tracking lags actual site conditions by days or weeks
- **Inaccurate Billing**: Pay applications based on estimates rather than verified work
- **Safety Compliance**: Manual photo review for safety violations is inconsistent
- **Stakeholder Communication**: Owners and investors lack real-time visibility

Traditional methods require manual photo review, subjective assessments, and disconnected documentation systems.

---

## The Solution

ImgGo extracts structured progress data from construction photos and outputs **YAML files** that integrate directly with project management systems:

**Workflow**:

```plaintext
Site Camera/Drone → Cloud Storage → ImgGo API (URL) → YAML Output → Procore/BIM 360
```

**What Gets Extracted**:

- Work package completion percentages
- Material quantities and locations
- Equipment presence and utilization
- Safety compliance status
- Weather conditions
- Personnel headcount
- Milestone verification

---

## Why YAML Output?

YAML is ideal for construction progress tracking:

- **Hierarchical Structure**: Matches construction breakdown structures (WBS)
- **Human-Readable**: Easy for supervisors to review and validate
- **Configuration Format**: Direct import to project management tools
- **Version Control**: Git-friendly for tracking changes over time
- **Nested Data**: Supports complex relationships (zones → trades → tasks)

**Example Output**:

```yaml
project_id: "PRJ-2025-001"
site_name: "Downtown Office Complex"
capture_date: "2025-01-22T14:30:00Z"
weather_conditions:
  temperature: 72
  conditions: "Partly Cloudy"
  wind_speed: 8

zones:
  - zone_id: "ZONE-A-L3"
    description: "Third Floor - East Wing"
    overall_completion: 68.5

    work_packages:
      - package_id: "WP-HVAC-03"
        trade: "HVAC"
        description: "Ductwork Installation"
        status: "in_progress"
        completion_percent: 75
        scheduled_completion: 80
        variance: -5

        observations:
          - "Main trunk line installed"
          - "Branch ducts 60% complete"
          - "2 workers on site"

        materials:
          - item: "Sheet Metal Duct"
            quantity_installed: 450
            unit: "linear_feet"
          - item: "Diffusers"
            quantity_installed: 12
            unit: "units"

      - package_id: "WP-ELEC-03"
        trade: "Electrical"
        description: "Rough-In Wiring"
        status: "in_progress"
        completion_percent: 82
        scheduled_completion: 75
        variance: +7

        observations:
          - "Conduit runs complete"
          - "Wire pulling underway"
          - "3 electricians on site"

safety_observations:
  compliant: true
  violations: []
  ppe_compliance: 100
  fall_protection_present: true

equipment_on_site:
  - type: "Scissor Lift"
    count: 2
    status: "in_use"
  - type: "Material Hoist"
    count: 1
    status: "operational"

personnel_count:
  total: 18
  by_trade:
    HVAC: 2
    Electrical: 3
    Plumbing: 4
    Drywall: 6
    General: 3

milestones:
  - milestone_id: "MS-05"
    description: "Third Floor MEP Rough-In"
    target_date: "2025-01-30"
    status: "on_track"
    completion: 75
```

---

## Implementation Guide

### Step 1: Set Up Pattern

Create a pattern that extracts construction progress elements:

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "Construction Progress Tracker",
  "output_format": "yaml",
  "schema": {
    "project_id": "string",
    "site_name": "string",
    "capture_date": "datetime",
    "weather_conditions": {
      "temperature": "number",
      "conditions": "string",
      "wind_speed": "number"
    },
    "zones": [
      {
        "zone_id": "string",
        "description": "string",
        "overall_completion": "number",
        "work_packages": [
          {
            "package_id": "string",
            "trade": "string",
            "description": "string",
            "status": "enum[not_started,in_progress,completed,on_hold]",
            "completion_percent": "number",
            "scheduled_completion": "number",
            "variance": "number",
            "observations": ["string"],
            "materials": [
              {
                "item": "string",
                "quantity_installed": "number",
                "unit": "string"
              }
            ]
          }
        ]
      }
    ],
    "safety_observations": {
      "compliant": "boolean",
      "violations": ["string"],
      "ppe_compliance": "number",
      "fall_protection_present": "boolean"
    },
    "equipment_on_site": [
      {
        "type": "string",
        "count": "number",
        "status": "string"
      }
    ],
    "personnel_count": {
      "total": "number",
      "by_trade": {
        "HVAC": "number",
        "Electrical": "number",
        "Plumbing": "number",
        "Drywall": "number",
        "General": "number"
      }
    },
    "milestones": [
      {
        "milestone_id": "string",
        "description": "string",
        "target_date": "date",
        "status": "enum[on_track,at_risk,delayed,completed]",
        "completion": "number"
      }
    ]
  }
}
```

### Step 2: Process Site Photos from Camera URLs

Most construction sites use time-lapse cameras or drones that upload to cloud storage. Process these images directly from their URLs:

```python
import requests
import yaml
from datetime import datetime

IMGGO_API_KEY = "your_api_key"
IMGGO_PATTERN_ID = "pat_construction_xyz"

def process_site_photo(image_url, project_id, zone_id):
    """
    Process construction site photo from URL and return YAML progress data
    """
    # Submit image URL to ImgGo
    response = requests.post(
        f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
        headers={
            "Authorization": f"Bearer {IMGGO_API_KEY}",
            "Idempotency-Key": f"{project_id}-{zone_id}-{datetime.now().isoformat()}"
        },
        json={
            "image_url": image_url,
            "context": {
                "project_id": project_id,
                "zone_id": zone_id
            }
        }
    )

    job_id = response.json()["data"]["job_id"]

    # Poll for results
    import time
    for _ in range(30):
        result = requests.get(
            f"https://img-go.com/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {IMGGO_API_KEY}"}
        ).json()

        if result["data"]["status"] == "completed":
            # Result is already in YAML format
            yaml_output = result["data"]["result"]
            return yaml_output
        elif result["data"]["status"] == "failed":
            raise Exception(f"Processing failed: {result['data'].get('error')}")

        time.sleep(2)

    raise Exception("Processing timeout")


# Example: Process from time-lapse camera
camera_url = "https://s3.amazonaws.com/construction-site-cams/project-001/zone-a/2025-01-22-14-30.jpg"
yaml_data = process_site_photo(camera_url, "PRJ-2025-001", "ZONE-A-L3")

# Parse YAML
progress = yaml.safe_load(yaml_data)

print(f"Zone: {progress['zones'][0]['description']}")
print(f"Overall Completion: {progress['zones'][0]['overall_completion']}%")

for package in progress['zones'][0]['work_packages']:
    print(f"  {package['trade']}: {package['completion_percent']}% (variance: {package['variance']:+d}%)")
```

### Step 3: Integrate with Procore

Push progress updates directly to Procore project management:

```python
import requests
import yaml

PROCORE_API_KEY = "your_procore_api_key"
PROCORE_PROJECT_ID = "123456"

def update_procore_progress(yaml_data):
    """
    Update Procore work packages with progress from YAML
    """
    progress = yaml.safe_load(yaml_data)

    # Authenticate with Procore
    procore_headers = {
        "Authorization": f"Bearer {PROCORE_API_KEY}",
        "Procore-Company-Id": "789"
    }

    for zone in progress['zones']:
        for package in zone['work_packages']:
            # Update work package in Procore
            payload = {
                "work_order": {
                    "status": package['status'],
                    "percent_complete": package['completion_percent'],
                    "notes": "\n".join(package['observations']),
                    "updated_by": "ImgGo Automation"
                }
            }

            response = requests.patch(
                f"https://api.procore.com/rest/v1.0/work_orders/{package['package_id']}",
                headers=procore_headers,
                json=payload
            )

            print(f"Updated {package['package_id']}: {package['completion_percent']}%")

    # Update milestones
    for milestone in progress['milestones']:
        milestone_payload = {
            "milestone": {
                "status": milestone['status'],
                "percent_complete": milestone['completion']
            }
        }

        requests.patch(
            f"https://api.procore.com/rest/v1.0/milestones/{milestone['milestone_id']}",
            headers=procore_headers,
            json=milestone_payload
        )

# Process and sync
yaml_data = process_site_photo(camera_url, "PRJ-2025-001", "ZONE-A-L3")
update_procore_progress(yaml_data)
```

### Step 4: Automated Daily Reports

Generate daily progress reports from time-lapse cameras:

```python
import schedule
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml

def generate_daily_report():
    """
    Process all zone cameras and generate consolidated report
    """
    zones = [
        {"id": "ZONE-A-L3", "camera": "https://s3.../zone-a-latest.jpg"},
        {"id": "ZONE-B-L3", "camera": "https://s3.../zone-b-latest.jpg"},
        {"id": "ZONE-C-L2", "camera": "https://s3.../zone-c-latest.jpg"}
    ]

    report_data = []

    for zone in zones:
        yaml_data = process_site_photo(zone['camera'], "PRJ-2025-001", zone['id'])
        progress = yaml.safe_load(yaml_data)
        report_data.append(progress)

    # Generate HTML report
    html_report = generate_html_report(report_data)

    # Email to stakeholders
    send_email(
        to=["pm@construction.com", "owner@development.com"],
        subject=f"Daily Progress Report - {datetime.now().strftime('%Y-%m-%d')}",
        html_body=html_report
    )

    print(f"Daily report sent at {datetime.now()}")

def generate_html_report(report_data):
    """
    Convert YAML data to HTML report
    """
    html = "<html><body><h1>Construction Progress Report</h1>"

    for zone_data in report_data:
        zone = zone_data['zones'][0]
        html += f"<h2>{zone['description']} - {zone['overall_completion']}%</h2>"
        html += "<table border='1'><tr><th>Trade</th><th>Completion</th><th>Variance</th><th>Status</th></tr>"

        for pkg in zone['work_packages']:
            variance_color = "green" if pkg['variance'] >= 0 else "red"
            html += f"<tr><td>{pkg['trade']}</td><td>{pkg['completion_percent']}%</td>"
            html += f"<td style='color:{variance_color}'>{pkg['variance']:+d}%</td>"
            html += f"<td>{pkg['status']}</td></tr>"

        html += "</table><br>"

        # Safety section
        safety = zone_data['safety_observations']
        safety_status = "PASS" if safety['compliant'] else "FAIL"
        html += f"<p><strong>Safety Status:</strong> {safety_status}</p>"

    html += "</body></html>"
    return html

# Schedule daily reports at 5 PM
schedule.every().day.at("17:00").do(generate_daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Integration Examples

### Autodesk BIM 360 Integration

```python
import requests
import yaml

BIM360_BASE_URL = "https://developer.api.autodesk.com"
BIM360_ACCESS_TOKEN = "your_access_token"

def sync_to_bim360(yaml_data):
    """
    Sync progress data to BIM 360 Field
    """
    progress = yaml.safe_load(yaml_data)

    headers = {
        "Authorization": f"Bearer {BIM360_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Create inspection record
    for zone in progress['zones']:
        inspection_payload = {
            "title": f"Progress Inspection - {zone['description']}",
            "inspection_date": progress['capture_date'],
            "status": "completed",
            "checklist_items": []
        }

        # Add work packages as checklist items
        for pkg in zone['work_packages']:
            inspection_payload['checklist_items'].append({
                "title": f"{pkg['trade']} - {pkg['description']}",
                "status": pkg['status'],
                "notes": "\n".join(pkg['observations']),
                "percent_complete": pkg['completion_percent']
            })

        # Post inspection
        response = requests.post(
            f"{BIM360_BASE_URL}/fieldapi/v1/inspections",
            headers=headers,
            json=inspection_payload
        )

        print(f"Created BIM 360 inspection: {response.json()['id']}")
```

### Oracle Primavera P6 Integration

```python
import zeep  # SOAP client for P6 API
import yaml

P6_WSDL_URL = "http://your-p6-server/p6ws/services/ActivityService?wsdl"
P6_USERNAME = "integration_user"
P6_PASSWORD = "password"

def update_p6_activities(yaml_data):
    """
    Update Primavera P6 activity progress
    """
    # Create SOAP client
    client = zeep.Client(wsdl=P6_WSDL_URL)

    # Authenticate
    session = client.service.Login(P6_USERNAME, P6_PASSWORD)

    progress = yaml.safe_load(yaml_data)

    for zone in progress['zones']:
        for pkg in zone['work_packages']:
            # Map package ID to P6 activity ID
            activity_id = pkg['package_id']

            # Update activity
            client.service.UpdateActivity(
                session=session,
                ActivityObjectId=activity_id,
                PercentComplete=pkg['completion_percent'],
                Status=pkg['status'].upper(),
                ActualStartDate=progress['capture_date'] if pkg['completion_percent'] > 0 else None
            )

            print(f"Updated P6 activity {activity_id}: {pkg['completion_percent']}%")

    client.service.Logout(session)
```

---

## Performance Metrics

### Time Savings

| Task | Manual Process | With ImgGo | Savings |
|------|----------------|------------|---------|
| Weekly progress report | 8 hours | 30 minutes | 93% |
| Photo review and annotation | 3 hours | 5 minutes | 97% |
| Work package updates | 2 hours | Automated | 100% |
| Safety compliance checks | 1 hour | 2 minutes | 97% |

**Total Weekly Savings**: 13.5 hours per project manager

### Accuracy Improvements

- **Progress Tracking**: ±5% accuracy (vs ±15% manual estimates)
- **Material Quantities**: ±2% variance (vs ±10% visual estimates)
- **Safety Compliance**: 100% photo coverage (vs 60% manual spot checks)
- **Billing Accuracy**: 98% verified work (vs 85% estimated)

### ROI Example

**200-unit residential project**:

- **Cost**: $1,200/month (API usage for 50 daily photos)
- **PM Time Saved**: 54 hours/month × $75/hour = $4,050
- **Reduced Rework**: $8,000/month (from early issue detection)
- **Faster Billing**: $15,000/month (improved cash flow from accurate pay apps)
- **Net Monthly Benefit**: $25,850
- **ROI**: 2,054%

---

## Advanced Features

### Drone Integration

Process aerial drone footage to track large-scale progress:

```python
import requests

def process_drone_footage(video_url, flight_plan_id):
    """
    Extract frames from drone video and process each
    """
    # Extract key frames (every 30 seconds)
    frames = extract_video_frames(video_url, interval=30)

    results = []

    for idx, frame_url in enumerate(frames):
        yaml_data = process_site_photo(
            frame_url,
            "PRJ-2025-001",
            f"AERIAL-{flight_plan_id}-{idx}"
        )
        results.append(yaml_data)

    # Consolidate results
    consolidated = consolidate_aerial_data(results)
    return consolidated
```

### Change Detection

Compare progress between time periods:

```python
import yaml
from deepdiff import DeepDiff

def detect_changes(previous_yaml, current_yaml):
    """
    Identify what changed between two progress snapshots
    """
    prev = yaml.safe_load(previous_yaml)
    curr = yaml.safe_load(current_yaml)

    diff = DeepDiff(prev, curr, ignore_order=True)

    # Extract meaningful changes
    changes = {
        "completion_increases": [],
        "status_changes": [],
        "new_observations": []
    }

    # Analyze differences
    if 'values_changed' in diff:
        for path, change in diff['values_changed'].items():
            if 'completion_percent' in path:
                changes['completion_increases'].append({
                    "package": extract_package_from_path(path),
                    "from": change['old_value'],
                    "to": change['new_value'],
                    "delta": change['new_value'] - change['old_value']
                })

    return changes

# Example usage
yesterday_yaml = process_site_photo(yesterday_camera_url, "PRJ-2025-001", "ZONE-A")
today_yaml = process_site_photo(today_camera_url, "PRJ-2025-001", "ZONE-A")

changes = detect_changes(yesterday_yaml, today_yaml)

for increase in changes['completion_increases']:
    print(f"{increase['package']}: +{increase['delta']}% progress")
```

### Safety Alert System

```python
import yaml
import requests

SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

def check_safety_compliance(yaml_data):
    """
    Scan for safety violations and alert immediately
    """
    progress = yaml.safe_load(yaml_data)
    safety = progress['safety_observations']

    if not safety['compliant'] or safety['violations']:
        # Send immediate alert
        alert = {
            "text": "SAFETY VIOLATION DETECTED",
            "attachments": [{
                "color": "danger",
                "title": f"Site: {progress['site_name']}",
                "fields": [
                    {
                        "title": "Violations",
                        "value": "\n".join(safety['violations']),
                        "short": False
                    },
                    {
                        "title": "PPE Compliance",
                        "value": f"{safety['ppe_compliance']}%",
                        "short": True
                    },
                    {
                        "title": "Time",
                        "value": progress['capture_date'],
                        "short": True
                    }
                ]
            }]
        }

        requests.post(SLACK_WEBHOOK, json=alert)

        # Also flag in project management system
        flag_safety_issue(progress['project_id'], safety['violations'])

# Run safety checks every hour
schedule.every().hour.do(lambda: check_safety_compliance(
    process_site_photo(camera_url, "PRJ-2025-001", "ZONE-A")
))
```

---

## Best Practices

### Camera Placement

- **Coverage**: Position cameras to capture 80%+ of active work areas
- **Angle**: 45-degree angle provides best depth perception
- **Frequency**: Time-lapse every 15-30 minutes during work hours
- **Backup**: Multiple cameras per zone for redundancy

### Data Quality

- **Lighting**: Schedule captures during daylight hours (7 AM - 5 PM)
- **Weather**: Flag photos during heavy rain/snow for manual review
- **Consistency**: Use fixed camera positions for accurate change detection
- **Context**: Include zone markers or QR codes in frame for auto-identification

### Validation

- **Spot Checks**: Manually verify 10% of automated measurements
- **Foreman Review**: Have trade foremen validate their work package data weekly
- **Tolerance Bands**: Set ±5% variance thresholds before flagging for review
- **Audit Trail**: Preserve original photos and YAML outputs for 7 years

### Integration

- **API Rate Limits**: Batch process off-peak hours to avoid limits
- **Webhooks**: Use webhooks for real-time updates instead of polling
- **Caching**: Cache YAML outputs locally before syncing to avoid duplicates
- **Error Handling**: Implement retry logic with exponential backoff

---

## Compliance and Security

### Data Retention

- **Photos**: Retain on secure cloud storage for project duration + 7 years
- **YAML Outputs**: Archive with project closeout documentation
- **Access Logs**: Maintain audit trail of all data access

### Privacy

- **Personnel**: Blur faces in photos if not required for headcount
- **Sensitive Areas**: Mask proprietary equipment or confidential zones
- **Third Parties**: Obtain consent before sharing progress data with subcontractors

### Standards Compliance

- **ISO 19650**: BIM information management workflows
- **OSHA**: Safety documentation and reporting requirements
- **AIA G702**: Progress billing and payment applications

---

## Troubleshooting

### Issue: Inaccurate Completion Percentages

**Solution**: Train the pattern with 20+ labeled examples showing various completion stages

### Issue: Missing Material Quantities

**Solution**: Ensure materials are visible and not obscured by equipment or workers

### Issue: Procore Sync Failures

**Solution**: Verify package IDs match between systems, check API credentials and rate limits

### Issue: Weather Affecting Image Quality

**Solution**: Implement weather-aware processing with confidence scoring:

```python
def should_process_photo(weather_conditions):
    """Skip processing in poor conditions"""
    if weather_conditions['visibility'] < 0.5:  # Heavy rain/fog
        return False
    if weather_conditions['light_level'] < 200:  # Too dark
        return False
    return True
```

---

## Related Use Cases

- [Real Estate Development](../real-estate) - Property inspection and punch lists
- [Quality Control](../quality-control) - Manufacturing quality assurance
- [Insurance Claims](../insurance-claims) - Damage assessment workflows

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- YAML Schema Reference: [https://img-go.com/docs/output-formats#yaml](https://img-go.com/docs/output-formats#yaml)
- Integration Help: <support@img-go.com>
