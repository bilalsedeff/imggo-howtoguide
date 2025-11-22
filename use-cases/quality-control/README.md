# Manufacturing Quality Control Automation

Automate defect detection and inspection reports with image-to-YAML conversion for manufacturing quality systems.

## Business Problem

Manufacturing quality control faces significant challenges:

- **Manual inspections**: 15-30 minutes per product for detailed inspection
- **Inconsistent reporting**: Subjective defect descriptions vary by inspector
- **Data loss**: Paper inspection forms get lost or damaged
- **Delayed feedback**: Quality issues discovered hours or days after production
- **High costs**: Quality defects cost manufacturers $240 billion annually
- **Compliance gaps**: Missing or incomplete inspection documentation

**Industry impact**: 1-5% of manufactured products have quality defects, costing billions in recalls and rework.

## Solution: Image to YAML Quality Reports

Automated visual inspection with YAML output for manufacturing execution systems (MES):

1. **Capture**: Inspector photographs product at inspection station
2. **Upload**: Auto-sync to quality management system
3. **Detect**: AI identifies defects, measurements, compliance
4. **Report**: Generate YAML-formatted inspection report
5. **Alert**: Notify production team of critical defects
6. **Integrate**: Sync to MES, ERP, quality databases

**Result**: 70% faster inspections, 95% consistency, real-time quality tracking.

## What Gets Extracted

### YAML Output for Manufacturing Systems

Perfect for MES integration, human-readable configuration, and DevOps quality pipelines:

```yaml
inspection_report:
  product:
    sku: "WIDGET-A-2024"
    serial_number: "SN20250122-0451"
    batch_number: "BATCH-2025-W03"
    production_line: "Line-A3"
    production_date: "2025-01-22"

  inspection:
    inspector_id: "INS-042"
    inspection_station: "Final-QC-Station-2"
    inspection_timestamp: "2025-01-22T14:30:00Z"
    inspection_type: "final_quality_check"
    duration_seconds: 45

  measurements:
    dimensions:
      length_mm: 150.2
      width_mm: 75.1
      height_mm: 25.0
      tolerance_met: true
    weight:
      actual_grams: 245.3
      target_grams: 245.0
      variance_percent: 0.12
      within_tolerance: true

  visual_inspection:
    surface_finish:
      rating: "excellent"
      defects_found: false
    color_match:
      expected_color: "RAL-5005"
      actual_color: "RAL-5005"
      match: true
    label_quality:
      readable: true
      aligned: true
      defects: []

  defects:
    - defect_id: "DEF-2025-0122-001"
      type: "scratch"
      location: "top_surface"
      severity: "minor"
      size_mm: 2.3
      coordinates:
        x: 45
        y: 30
      action_required: "cosmetic_touch_up"
      impact: "visual_only"

  compliance:
    iso_9001: true
    rohs_compliant: true
    ce_marking_present: true
    safety_labels_present: true
    documentation_complete: true

  verdict:
    pass_fail: "pass_with_minor_defect"
    quality_score: 92
    recommended_action: "approve_for_shipping"
    notes: "Minor cosmetic defect within acceptable limits. No functional impact."

  metadata:
    image_urls:
      - "https://cdn.example.com/inspections/2025/01/22/img_001.jpg"
      - "https://cdn.example.com/inspections/2025/01/22/img_002.jpg"
    confidence_score: 0.96
    processing_time_ms: 2340
```

### JSON Alternative

For modern APIs and databases:

```json
{
  "product": {
    "sku": "WIDGET-A-2024",
    "serial_number": "SN20250122-0451"
  },
  "defects": [
    {
      "type": "scratch",
      "severity": "minor",
      "location": "top_surface"
    }
  ],
  "verdict": {
    "pass_fail": "pass",
    "quality_score": 92
  }
}
```

## Pattern Setup

### YAML Output Pattern

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quality Inspection Report - YAML",
    "output_format": "yaml",
    "instructions": "Analyze product image for quality control inspection. Identify any visible defects including scratches, dents, discoloration, misalignment, missing components, or damage. Measure visible dimensions if scale is present. Check for required labels, markings, and documentation. Assess surface finish quality. Generate comprehensive inspection report in YAML format suitable for manufacturing execution systems.",
    "yaml_structure": {
      "inspection_report": {
        "product": {},
        "inspection": {},
        "measurements": {},
        "defects": [],
        "compliance": {},
        "verdict": {}
      }
    }
  }'
```

## Production Line Integration

### Raspberry Pi Inspection Station

```python
# inspection_station.py
import os
import yaml
import requests
from picamera import PiCamera
from datetime import datetime
import RPi.GPIO as GPIO

# Configuration
API_KEY = os.environ["IMGGO_API_KEY"]
PATTERN_ID = os.environ["IMGGO_PATTERN_ID"]
MES_ENDPOINT = os.environ["MES_API_ENDPOINT"]

# GPIO setup for triggers
TRIGGER_PIN = 17
PASS_LED = 27
FAIL_LED = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGGER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PASS_LED, GPIO.OUT)
GPIO.setup(FAIL_LED, GPIO.OUT)

camera = PiCamera()
camera.resolution = (1920, 1080)

class QualityInspectionStation:
    """Automated quality inspection station"""

    def __init__(self):
        self.inspection_count = 0
        self.pass_count = 0
        self.fail_count = 0

    def run(self):
        """Main inspection loop"""
        print("Quality Inspection Station Ready")

        while True:
            # Wait for trigger (product arrives at station)
            GPIO.wait_for_edge(TRIGGER_PIN, GPIO.FALLING)

            print("\nProduct detected. Starting inspection...")

            # Perform inspection
            result = self.inspect_product()

            # Update counters
            self.inspection_count += 1

            if result['verdict']['pass_fail'].startswith('pass'):
                self.pass_count += 1
                self.indicate_pass()
            else:
                self.fail_count += 1
                self.indicate_fail()

            # Display statistics
            print(f"\nInspection #{self.inspection_count}")
            print(f"Pass: {self.pass_count} | Fail: {self.fail_count}")
            print(f"Pass Rate: {(self.pass_count/self.inspection_count)*100:.1f}%")

    def inspect_product(self):
        """Capture and analyze product"""

        # Capture image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"/tmp/inspection_{timestamp}.jpg"

        camera.capture(image_path)
        print(f"Image captured: {image_path}")

        # Upload to CDN
        image_url = self.upload_to_cdn(image_path)

        # Process with ImgGo
        response = requests.post(
            f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"image_url": image_url}
        )

        job_id = response.json()["data"]["job_id"]

        # Poll for YAML results
        yaml_result = self.poll_job_result(job_id)

        # Parse YAML
        inspection_data = yaml.safe_load(yaml_result)

        # Send to MES
        self.sync_to_mes(inspection_data)

        # Cleanup
        os.remove(image_path)

        return inspection_data['inspection_report']

    def upload_to_cdn(self, image_path):
        """Upload image to cloud storage"""
        # Implementation depends on your CDN
        # Example: S3, Cloudinary, etc.
        pass

    def poll_job_result(self, job_id):
        """Poll for inspection results"""
        import time

        for attempt in range(30):
            response = requests.get(
                f"https://img-go.com/api/jobs/{job_id}",
                headers={"Authorization": f"Bearer {API_KEY}"}
            )

            data = response.json()["data"]

            if data["status"] == "completed":
                return data["result"]  # YAML string
            elif data["status"] == "failed":
                raise Exception("Inspection failed")

            time.sleep(2)

        raise Exception("Timeout")

    def sync_to_mes(self, inspection_data):
        """Sync inspection report to MES"""

        # Convert YAML data to MES format
        mes_payload = {
            'serial_number': inspection_data['inspection_report']['product']['serial_number'],
            'pass_fail': inspection_data['inspection_report']['verdict']['pass_fail'],
            'quality_score': inspection_data['inspection_report']['verdict']['quality_score'],
            'defects': inspection_data['inspection_report']['defects'],
            'timestamp': datetime.now().isoformat()
        }

        requests.post(
            MES_ENDPOINT,
            json=mes_payload,
            headers={'Authorization': f"Bearer {os.environ['MES_API_KEY']}"}
        )

    def indicate_pass(self):
        """Light up PASS LED"""
        GPIO.output(PASS_LED, GPIO.HIGH)
        GPIO.output(FAIL_LED, GPIO.LOW)
        time.sleep(2)
        GPIO.output(PASS_LED, GPIO.LOW)

    def indicate_fail(self):
        """Light up FAIL LED and sound alarm"""
        GPIO.output(FAIL_LED, GPIO.HIGH)
        GPIO.output(PASS_LED, GPIO.LOW)
        # Sound alarm/buzzer here
        time.sleep(2)
        GPIO.output(FAIL_LED, GPIO.LOW)

if __name__ == "__main__":
    try:
        station = QualityInspectionStation()
        station.run()
    except KeyboardInterrupt:
        GPIO.cleanup()
```

### YAML Configuration for DevOps Quality Pipelines

```yaml
# quality_pipeline.yaml
quality_control:
  pipeline_name: "Product-A Final Inspection"
  version: "2.0"

  inspection_criteria:
    dimensions:
      length:
        min_mm: 149.5
        max_mm: 150.5
        tolerance: 0.5
      width:
        min_mm: 74.5
        max_mm: 75.5
        tolerance: 0.5

    visual_defects:
      critical:
        - type: "crack"
          severity: "critical"
          action: "reject"
        - type: "missing_component"
          severity: "critical"
          action: "reject"

      major:
        - type: "dent"
          max_size_mm: 5
          severity: "major"
          action: "rework"

      minor:
        - type: "scratch"
          max_size_mm: 2
          severity: "minor"
          action: "approve_with_note"

  compliance_checks:
    required_labels:
      - "serial_number"
      - "production_date"
      - "ce_marking"
      - "rohs_compliance"

  pass_thresholds:
    minimum_quality_score: 85
    max_minor_defects: 2
    max_major_defects: 0
    max_critical_defects: 0

  notifications:
    critical_defect:
      channels:
        - type: "slack"
          webhook: "${SLACK_WEBHOOK_CRITICAL}"
        - type: "email"
          recipients: ["quality-manager@company.com"]
        - type: "sms"
          numbers: ["+1-555-0100"]

    daily_summary:
      schedule: "0 17 * * *"  # 5 PM daily
      recipients: ["production-team@company.com"]
```

## Real-Time Quality Dashboard

```python
# quality_dashboard.py
from flask import Flask, render_template, jsonify
import yaml
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/quality/stats')
def quality_stats():
    """Real-time quality statistics"""

    # Get today's inspections from database
    today = datetime.now().date()
    inspections = get_inspections_since(today)

    stats = {
        'total_inspections': len(inspections),
        'pass_count': sum(1 for i in inspections if i['pass_fail'].startswith('pass')),
        'fail_count': sum(1 for i in inspections if i['pass_fail'] == 'fail'),
        'average_quality_score': sum(i['quality_score'] for i in inspections) / len(inspections) if inspections else 0,
        'defect_breakdown': calculate_defect_breakdown(inspections),
        'hourly_trend': calculate_hourly_trend(inspections)
    }

    return jsonify(stats)

@app.route('/api/quality/defects/trend')
def defect_trend():
    """Defect trends over time"""

    # Get last 30 days
    start_date = datetime.now() - timedelta(days=30)
    inspections = get_inspections_since(start_date)

    # Group by defect type
    defect_counts = {}
    for inspection in inspections:
        for defect in inspection['defects']:
            defect_type = defect['type']
            defect_counts[defect_type] = defect_counts.get(defect_type, 0) + 1

    return jsonify({
        'period': '30_days',
        'defect_types': defect_counts,
        'total_defects': sum(defect_counts.values())
    })

@app.route('/api/quality/export/yaml')
def export_quality_report():
    """Export quality report as YAML"""

    today = datetime.now().date()
    inspections = get_inspections_since(today)

    report = {
        'quality_report': {
            'generated_at': datetime.now().isoformat(),
            'period': str(today),
            'summary': {
                'total_inspections': len(inspections),
                'pass_rate': (sum(1 for i in inspections if i['pass_fail'].startswith('pass')) / len(inspections)) * 100 if inspections else 0
            },
            'inspections': inspections
        }
    }

    yaml_output = yaml.dump(report, default_flow_style=False)

    return yaml_output, 200, {
        'Content-Type': 'application/x-yaml',
        'Content-Disposition': f'attachment; filename=quality_report_{today}.yaml'
    }

if __name__ == '__main__':
    app.run(port=5000)
```

## Integration with MES Systems

### SAP MES Integration

```python
def sync_to_sap_mes(inspection_yaml):
    """Sync YAML inspection data to SAP MES"""

    import xmlrpc.client

    # Parse YAML
    inspection = yaml.safe_load(inspection_yaml)['inspection_report']

    # SAP MES connection
    sap = xmlrpc.client.ServerProxy(os.environ["SAP_MES_ENDPOINT"])

    # Create inspection record
    result = sap.createQualityInspection({
        'MaterialNumber': inspection['product']['sku'],
        'SerialNumber': inspection['product']['serial_number'],
        'InspectionLot': inspection['product']['batch_number'],
        'InspectionResult': 'PASS' if inspection['verdict']['pass_fail'].startswith('pass') else 'FAIL',
        'QualityScore': inspection['verdict']['quality_score'],
        'Defects': [
            {
                'DefectCode': defect['type'].upper(),
                'DefectDescription': f"{defect['severity']} {defect['type']} at {defect['location']}",
                'ActionRequired': defect.get('action_required', 'none')
            }
            for defect in inspection['defects']
        ]
    })

    return result
```

## Performance Metrics

| Metric | Manual Inspection | Automated YAML QC |
|--------|-------------------|-------------------|
| Inspection Time | 15-30 minutes | 2-3 minutes |
| Consistency | 70-80% | 95%+ |
| Data Accuracy | 85% | 98% |
| Report Generation | Manual forms (30 min) | Instant YAML output |
| MES Integration | Manual entry (15 min) | Automated (seconds) |
| Defect Detection Rate | 80-85% | 92-96% |

## Use Cases by Industry

### Electronics Manufacturing
- PCB inspection for solder defects
- Component placement verification
- Label and marking compliance

### Automotive
- Paint finish quality checks
- Assembly verification
- Part dimension validation

### Pharmaceuticals
- Tablet visual inspection
- Packaging integrity checks
- Label verification

### Food & Beverage
- Product appearance checks
- Packaging defects
- Label compliance

## Integration Examples

Available in `integration-examples/`:

- [Raspberry Pi Inspection Station](./integration-examples/raspberry-pi-station.py)
- [SAP MES Integration](./integration-examples/sap-mes-sync.py)
- [Quality Dashboard](./integration-examples/flask-dashboard.py)
- [YAML to XML Converter](./integration-examples/yaml-to-xml.py)

## Troubleshooting

### Issue: Defects Not Detected

**Solutions**:
- Improve lighting at inspection station (uniform, diffused light)
- Use higher resolution camera (minimum 1920x1080)
- Adjust camera angle for better defect visibility
- Add specific defect examples to pattern training

### Issue: YAML Parsing Errors

**Solution**: Validate YAML structure:

```python
import yaml
from jsonschema import validate

def validate_inspection_yaml(yaml_string):
    """Validate YAML structure against schema"""

    try:
        data = yaml.safe_load(yaml_string)

        # Define expected schema
        schema = {
            'type': 'object',
            'required': ['inspection_report'],
            'properties': {
                'inspection_report': {
                    'type': 'object',
                    'required': ['product', 'verdict']
                }
            }
        }

        validate(instance=data, schema=schema)
        return {'valid': True}

    except yaml.YAMLError as e:
        return {'valid': False, 'error': str(e)}
```

## Next Steps

- Explore [Construction Tracking](../construction-tracking) for progress reports
- Review [YAML Processing](../../integration-guides/yaml-processing.md)
- Set up [MES Integration](../../integration-guides/mes-systems.md)

---

**SEO Keywords**: quality control automation, image to YAML, manufacturing inspection automation, defect detection AI, MES integration

**Sources**:
- [Quality Control Automation](https://www.scnsoft.com/manufacturing/quality-control)
- [Manufacturing AI](https://www.netsolutions.com/insights/manufacturing-ai/)
