# Food Safety Inspections and Health Code Compliance

## Overview

Automate restaurant and food service inspections by extracting health code violations, temperature readings, and facility conditions from inspection photos. Convert visual documentation into **CSV reports** that integrate with health department systems and compliance databases.

**Output Format**: CSV (universal format for health department databases and compliance tracking)
**Upload Method**: URL Processing (from cloud-uploaded inspection photos, tablet apps)
**Industry**: Food Service, Health Departments, Restaurant Chains, Commercial Kitchens, Food Manufacturing

---

## The Problem

Health inspectors and restaurant operators face these challenges:

- **Manual Report Writing**: Inspectors spend 45-60 minutes post-inspection writing reports
- **Inconsistent Documentation**: Violation descriptions vary between inspectors
- **Delayed Reporting**: Inspection reports reach restaurants 3-5 days after visit
- **Photo Backlog**: Thousands of inspection photos never analyzed for trends
- **Compliance Tracking**: No centralized way to track repeat violations across locations
- **Data Entry Errors**: 5-10% error rate transcribing violations into databases

Traditional inspection processes rely on handwritten notes, clipboard checklists, and manual data entry into health department systems.

---

## The Solution

ImgGo extracts violations, temperature readings, and facility conditions from inspection photos and outputs **CSV files** that import directly into health department databases:

**Workflow**:

```plaintext
Inspection Photos (Cloud URL) → ImgGo API → CSV Output → Health Department Database
```

**What Gets Extracted**:

- Health code violations with codes
- Temperature readings from thermometers
- Handwashing station compliance
- Food storage temperatures
- Pest evidence
- Cross-contamination risks
- Equipment cleanliness scores
- Date/time stamps

---

## Why CSV Output?

CSV is the standard format for health department reporting:

- **Universal Compatibility**: All health department systems accept CSV imports
- **Spreadsheet Ready**: Review in Excel/Google Sheets before submission
- **Batch Processing**: Process multiple locations simultaneously
- **Historical Tracking**: Easy to compare inspections over time
- **Compliance Reports**: Generate trend reports for regulatory agencies

**Example Output (restaurant_inspection_2025-01-22.csv)**:

```csv
Inspection_ID,Restaurant_Name,Address,Inspector_ID,Inspection_Date,Inspection_Time,Violation_Code,Violation_Category,Violation_Description,Severity,Location_In_Facility,Corrected_On_Site,Temperature_Reading,Critical_Violation,Photo_Evidence_URL,Notes
INS-2025-001234,Tasty Burgers Downtown,123 Main St,INSP-042,2025-01-22,14:30,2-102.11,Food Temperature,Cold holding temperature 48°F (should be ≤41°F),Critical,Walk-in cooler,No,48.2,Yes,https://s3.../walk-in-cooler.jpg,Potentially Hazardous Foods (PHF) held at improper temperature
INS-2025-001234,Tasty Burgers Downtown,123 Main St,INSP-042,2025-01-22,14:35,4-601.11,Equipment Cleaning,Grease buildup on hood filters,Non-Critical,Kitchen hood system,No,,No,https://s3.../hood-filters.jpg,Requires cleaning to prevent fire hazard
INS-2025-001234,Tasty Burgers Downtown,123 Main St,INSP-042,2025-01-22,14:40,5-501.115,Handwashing,Handwashing sink blocked by storage containers,Critical,Prep area,Yes,,Yes,https://s3.../handwash-sink.jpg,Corrected immediately - containers removed
INS-2025-001234,Tasty Burgers Downtown,123 Main St,INSP-042,2025-01-22,14:45,6-201.11,Pest Control,Evidence of rodent droppings near dry storage,Critical,Dry storage room,No,,Yes,https://s3.../rodent-droppings.jpg,Pest control company contacted
INS-2025-001234,Tasty Burgers Downtown,123 Main St,INSP-042,2025-01-22,14:50,3-306.11,Food Storage,Raw chicken stored above ready-to-eat salads,Critical,Prep cooler,Yes,,Yes,https://s3.../improper-storage.jpg,Corrected - chicken moved to bottom shelf
INS-2025-001234,Tasty Burgers Downtown,123 Main St,INSP-042,2025-01-22,14:55,4-204.112,Thermometers,No thermometer in reach-in cooler,Non-Critical,Front service line,No,,No,https://s3.../missing-thermometer.jpg,Thermometer to be installed within 7 days
INS-2025-001234,Tasty Burgers Downtown,123 Main St,INSP-042,2025-01-22,15:00,6-501.12,Facility Maintenance,Floor tiles cracked near dishwasher,Non-Critical,Dishwashing area,No,,No,https://s3.../cracked-tiles.jpg,Repair scheduled
```

---

## Implementation Guide

### Step 1: Create Food Safety Pattern

Define CSV schema for health code violations:

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "Food Safety Inspection Extractor",
  "output_format": "csv",
  "csv_headers": [
    "Inspection_ID",
    "Restaurant_Name",
    "Address",
    "Inspector_ID",
    "Inspection_Date",
    "Inspection_Time",
    "Violation_Code",
    "Violation_Category",
    "Violation_Description",
    "Severity",
    "Location_In_Facility",
    "Corrected_On_Site",
    "Temperature_Reading",
    "Critical_Violation",
    "Photo_Evidence_URL",
    "Notes"
  ],
  "schema": {
    "violations": [
      {
        "Inspection_ID": "string",
        "Restaurant_Name": "string",
        "Address": "string",
        "Inspector_ID": "string",
        "Inspection_Date": "date",
        "Inspection_Time": "time",
        "Violation_Code": "string",
        "Violation_Category": "enum[Food Temperature,Equipment Cleaning,Handwashing,Pest Control,Food Storage,Thermometers,Facility Maintenance,Employee Hygiene]",
        "Violation_Description": "string",
        "Severity": "enum[Critical,Non-Critical]",
        "Location_In_Facility": "string",
        "Corrected_On_Site": "boolean",
        "Temperature_Reading": "number",
        "Critical_Violation": "boolean",
        "Photo_Evidence_URL": "string",
        "Notes": "string"
      }
    ]
  }
}
```

### Step 2: Process Inspection Photos from URLs

Health inspectors upload photos to tablets/phones which sync to cloud storage:

```python
import requests
import pandas as pd
from datetime import datetime
import time

IMGGO_API_KEY = "your_api_key"
IMGGO_PATTERN_ID = "pat_food_safety_xyz"

def process_inspection_photos(photo_urls, restaurant_info, inspector_id):
    """
    Process food safety inspection photos from cloud storage URLs
    """
    all_violations = []

    for photo_url in photo_urls:
        # Submit to ImgGo
        response = requests.post(
            f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
            headers={
                "Authorization": f"Bearer {IMGGO_API_KEY}",
                "Idempotency-Key": f"{restaurant_info['id']}-{datetime.now().timestamp()}"
            },
            json={
                "image_url": photo_url,
                "context": {
                    "restaurant_name": restaurant_info['name'],
                    "address": restaurant_info['address'],
                    "inspector_id": inspector_id,
                    "inspection_date": datetime.now().strftime('%Y-%m-%d')
                }
            }
        )

        job_id = response.json()["data"]["job_id"]

        # Poll for result
        result = poll_for_result(job_id)

        # Parse CSV result
        if result:
            # Result is CSV string
            violations_df = pd.read_csv(pd.StringIO(result))
            all_violations.append(violations_df)

        print(f"Processed {photo_url}")

    # Consolidate all violations
    if all_violations:
        consolidated = pd.concat(all_violations, ignore_index=True)
        return consolidated
    else:
        return pd.DataFrame()


def poll_for_result(job_id):
    """Poll ImgGo until job completes"""
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


# Example: Process inspection from cloud storage
restaurant = {
    'id': 'REST-789',
    'name': 'Tasty Burgers Downtown',
    'address': '123 Main St, San Francisco, CA'
}

inspection_photos = [
    "https://dropbox.com/inspections/rest-789/walk-in-cooler.jpg?dl=1",
    "https://dropbox.com/inspections/rest-789/hood-filters.jpg?dl=1",
    "https://dropbox.com/inspections/rest-789/handwash-sink.jpg?dl=1",
    "https://dropbox.com/inspections/rest-789/dry-storage.jpg?dl=1",
    "https://dropbox.com/inspections/rest-789/prep-cooler.jpg?dl=1"
]

violations_df = process_inspection_photos(inspection_photos, restaurant, "INSP-042")

# Save CSV report
output_filename = f"inspection_{restaurant['id']}_{datetime.now().strftime('%Y-%m-%d')}.csv"
violations_df.to_csv(output_filename, index=False)

# Generate summary
critical_violations = violations_df[violations_df['Critical_Violation'] == True]
non_critical = violations_df[violations_df['Critical_Violation'] == False]

print(f"\n=== Inspection Summary ===")
print(f"Restaurant: {restaurant['name']}")
print(f"Total Violations: {len(violations_df)}")
print(f"Critical: {len(critical_violations)}")
print(f"Non-Critical: {len(non_critical)}")
print(f"Corrected On-Site: {len(violations_df[violations_df['Corrected_On_Site'] == 'Yes'])}")
```

### Step 3: Health Department Database Import

Import CSV directly into health department compliance system:

```python
import psycopg2
import csv
from datetime import datetime

HEALTH_DEPT_DB = {
    'host': 'health-db.city.gov',
    'database': 'food_safety',
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD']
}

def import_inspection_to_health_dept(csv_file, inspection_score):
    """
    Import inspection CSV to health department database
    """
    conn = psycopg2.connect(**HEALTH_DEPT_DB)
    cursor = conn.cursor()

    # Read CSV
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        violations = list(reader)

    # Get or create inspection record
    cursor.execute("""
        INSERT INTO inspections (
            inspection_id, restaurant_name, address, inspector_id,
            inspection_date, total_violations, critical_violations,
            score, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        violations[0]['Inspection_ID'],
        violations[0]['Restaurant_Name'],
        violations[0]['Address'],
        violations[0]['Inspector_ID'],
        violations[0]['Inspection_Date'],
        len(violations),
        len([v for v in violations if v['Critical_Violation'] == 'True']),
        inspection_score,
        'completed'
    ))

    inspection_db_id = cursor.fetchone()[0]

    # Insert violations
    for violation in violations:
        cursor.execute("""
            INSERT INTO violations (
                inspection_id, violation_code, category, description,
                severity, location, corrected_on_site, temperature_reading,
                is_critical, photo_url, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            inspection_db_id,
            violation['Violation_Code'],
            violation['Violation_Category'],
            violation['Violation_Description'],
            violation['Severity'],
            violation['Location_In_Facility'],
            violation['Corrected_On_Site'] == 'Yes',
            float(violation['Temperature_Reading']) if violation['Temperature_Reading'] else None,
            violation['Critical_Violation'] == 'True',
            violation['Photo_Evidence_URL'],
            violation['Notes']
        ))

    conn.commit()

    # Check if restaurant needs re-inspection
    critical_uncorrected = [
        v for v in violations
        if v['Critical_Violation'] == 'True' and v['Corrected_On_Site'] != 'Yes'
    ]

    if critical_uncorrected:
        # Schedule follow-up inspection within 10 days
        cursor.execute("""
            INSERT INTO follow_up_inspections (
                restaurant_name, original_inspection_id, due_date,
                reason, status
            ) VALUES (%s, %s, CURRENT_DATE + INTERVAL '10 days', %s, 'scheduled')
        """, (
            violations[0]['Restaurant_Name'],
            inspection_db_id,
            f"{len(critical_uncorrected)} critical violations not corrected on-site"
        ))

        conn.commit()
        print(f"Follow-up inspection scheduled due to {len(critical_uncorrected)} critical violations")

    cursor.close()
    conn.close()

    print(f"Imported {len(violations)} violations to health department database")

    return inspection_db_id


# Calculate inspection score (100 - deductions)
def calculate_inspection_score(violations_df):
    """
    Calculate health inspection score based on violations
    """
    score = 100

    for _, violation in violations_df.iterrows():
        if violation['Critical_Violation']:
            if violation['Corrected_On_Site'] == 'Yes':
                score -= 2  # Minor deduction if corrected
            else:
                score -= 7  # Major deduction if not corrected
        else:
            score -= 1  # Non-critical deduction

    return max(0, score)


# Import to database
score = calculate_inspection_score(violations_df)
import_inspection_to_health_dept(output_filename, score)
```

### Step 4: Restaurant Notification System

Automatically notify restaurants of inspection results:

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd

def notify_restaurant_of_inspection(violations_csv, restaurant_email, score):
    """
    Email inspection report to restaurant management
    """
    # Load violations
    violations_df = pd.read_csv(violations_csv)

    # Generate HTML report
    html_report = generate_html_inspection_report(violations_df, score)

    # Create email
    msg = MIMEMultipart()
    msg['From'] = 'health.inspector@city.gov'
    msg['To'] = restaurant_email
    msg['Subject'] = f"Health Inspection Results - Score: {score}/100"

    # Email body
    body = f"""
Dear Restaurant Manager,

Your facility recently underwent a routine health inspection. Please review the attached report and take immediate action on any critical violations that were not corrected on-site.

Inspection Summary:
- Total Violations: {len(violations_df)}
- Critical Violations: {len(violations_df[violations_df['Critical_Violation'] == True])}
- Score: {score}/100

{"IMPORTANT: Follow-up inspection required within 10 days due to uncorrected critical violations." if score < 70 else ""}

Please review the detailed report below and take corrective action.

{html_report}

If you have questions or wish to appeal any violations, please contact our office within 10 business days.

Sincerely,
City Health Department
    """

    msg.attach(MIMEText(body, 'html'))

    # Attach CSV
    with open(violations_csv, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='csv')
        attachment.add_header('Content-Disposition', 'attachment', filename=violations_csv)
        msg.attach(attachment)

    # Send email
    with smtplib.SMTP('smtp.city.gov', 587) as server:
        server.starttls()
        server.login(os.environ['SMTP_USER'], os.environ['SMTP_PASSWORD'])
        server.send_message(msg)

    print(f"Inspection report emailed to {restaurant_email}")


def generate_html_inspection_report(violations_df, score):
    """Generate HTML table of violations"""
    # Determine grade
    if score >= 90:
        grade = "A"
        grade_color = "green"
    elif score >= 80:
        grade = "B"
        grade_color = "orange"
    else:
        grade = "C"
        grade_color = "red"

    html = f"""
    <html>
    <body>
        <h2>Health Inspection Report</h2>
        <div style="background-color: {grade_color}; color: white; padding: 20px; font-size: 24px; text-align: center;">
            Grade: {grade} | Score: {score}/100
        </div>
        <br>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
            <tr style="background-color: #cccccc;">
                <th>Violation Code</th>
                <th>Category</th>
                <th>Description</th>
                <th>Severity</th>
                <th>Location</th>
                <th>Corrected</th>
            </tr>
    """

    for _, row in violations_df.iterrows():
        severity_color = "red" if row['Critical_Violation'] else "orange"
        corrected = "✓ Yes" if row['Corrected_On_Site'] == 'Yes' else "✗ No"

        html += f"""
            <tr>
                <td>{row['Violation_Code']}</td>
                <td>{row['Violation_Category']}</td>
                <td>{row['Violation_Description']}</td>
                <td style="color: {severity_color}; font-weight: bold;">{row['Severity']}</td>
                <td>{row['Location_In_Facility']}</td>
                <td>{corrected}</td>
            </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return html


# Send notification
notify_restaurant_of_inspection(
    output_filename,
    "manager@tastyburgers.com",
    score
)
```

---

## Integration Examples

### Public Health Dashboard

```python
import plotly.express as px
import pandas as pd

def generate_public_health_dashboard():
    """
    Generate public dashboard showing inspection trends
    """
    # Load all inspections from past year
    conn = psycopg2.connect(**HEALTH_DEPT_DB)

    inspections = pd.read_sql("""
        SELECT
            i.inspection_date,
            i.restaurant_name,
            i.score,
            COUNT(v.id) as total_violations,
            SUM(CASE WHEN v.is_critical THEN 1 ELSE 0 END) as critical_violations
        FROM inspections i
        LEFT JOIN violations v ON i.id = v.inspection_id
        WHERE i.inspection_date >= CURRENT_DATE - INTERVAL '1 year'
        GROUP BY i.id, i.inspection_date, i.restaurant_name, i.score
        ORDER BY i.inspection_date DESC
    """, conn)

    # Average score trend over time
    monthly_avg = inspections.groupby(
        pd.Grouper(key='inspection_date', freq='M')
    )['score'].mean()

    fig = px.line(
        monthly_avg,
        title="Average Inspection Scores - Last 12 Months",
        labels={'value': 'Average Score', 'inspection_date': 'Month'}
    )

    fig.write_html('public_health_dashboard.html')

    # Violation category breakdown
    violation_categories = pd.read_sql("""
        SELECT category, COUNT(*) as count
        FROM violations
        WHERE inspection_id IN (
            SELECT id FROM inspections
            WHERE inspection_date >= CURRENT_DATE - INTERVAL '1 year'
        )
        GROUP BY category
        ORDER BY count DESC
    """, conn)

    fig2 = px.bar(
        violation_categories,
        x='category',
        y='count',
        title="Most Common Violations - Last 12 Months"
    )

    fig2.write_html('violations_breakdown.html')

    conn.close()
```

### Chain Restaurant Compliance Tracking

```python
def track_multi_location_compliance(chain_name):
    """
    Track compliance across all locations of a restaurant chain
    """
    conn = psycopg2.connect(**HEALTH_DEPT_DB)

    locations = pd.read_sql("""
        SELECT
            restaurant_name,
            address,
            AVG(score) as avg_score,
            COUNT(*) as inspection_count,
            SUM(critical_violations) as total_critical_violations,
            MAX(inspection_date) as last_inspection
        FROM inspections
        WHERE restaurant_name LIKE %s
        AND inspection_date >= CURRENT_DATE - INTERVAL '1 year'
        GROUP BY restaurant_name, address
        ORDER BY avg_score ASC
    """, conn, params=(f'{chain_name}%',))

    # Identify underperforming locations
    underperforming = locations[locations['avg_score'] < 85]

    print(f"\n=== {chain_name} Compliance Report ===")
    print(f"Total Locations: {len(locations)}")
    print(f"Average Score: {locations['avg_score'].mean():.1f}/100")
    print(f"Locations Below 85: {len(underperforming)}")

    if len(underperforming) > 0:
        print("\nUnderperforming Locations:")
        print(underperforming.to_string())

        # Alert corporate
        send_chain_compliance_alert(chain_name, underperforming)

    conn.close()

    return locations
```

---

## Performance Metrics

### Time Savings

| Task | Manual Process | With ImgGo | Savings |
|------|----------------|------------|---------|
| Document violations | 40 minutes | 3 minutes | 93% |
| Write inspection report | 25 minutes | Automated | 100% |
| Enter violations into database | 20 minutes | Automated | 100% |
| Generate restaurant notification | 15 minutes | Automated | 100% |
| **Total per inspection** | **100 minutes** | **3 minutes** | **97%** |

### Business Impact

**County health department** (500 inspections/month):

- **Inspector Productivity**: $180,000/year (800 hours saved monthly × $18/hour × 12)
- **Faster Reporting**: Same-day reports (vs 3-5 days delay)
- **Better Compliance**: 22% increase in violation correction rate
- **Public Health**: 35% faster response to critical violations
- **Database Accuracy**: 95% reduction in data entry errors
- **Total Annual Benefit**: $250,000
- **ImgGo Cost**: $18,000/year
- **ROI**: 1,289%

---

## Best Practices

### Photo Guidelines

- **Temperature Gauges**: Close-up shots showing exact readings
- **Equipment**: Capture entire piece of equipment plus close-ups of issues
- **Storage**: Show entire storage area context, not just violation
- **Timestamps**: Use camera with GPS and timestamp enabled

### Inspection Process

- **Consistency**: Take same angles/positions across all inspections
- **Documentation**: Photo every violation before and after correction
- **Verification**: Spot-check 10% of AI-extracted violations manually
- **Backup**: Keep original photos for 3 years minimum

### Database Management

- **Validation**: Verify CSV data before importing to health dept system
- **Archives**: Retain CSV files alongside official reports
- **Privacy**: Redact business-sensitive information from public reports
- **Appeals**: Document photo evidence for all critical violations

---

## Troubleshooting

### Issue: Temperature Readings Not Extracted

**Solution**: Ensure thermometer face is clear and in focus, avoid glare, take multiple angles

### Issue: Violation Codes Incorrect

**Solution**: Train pattern with health department's specific code system, provide code mapping

### Issue: False Violations Detected

**Solution**: Lower confidence threshold, implement human verification for borderline cases

---

## Related Use Cases

- [Quality Control](../quality-control) - Manufacturing inspection automation
- [Construction Progress](../construction-progress) - Site safety compliance
- [Field Service](../field-service) - Equipment inspection documentation

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- CSV Output Guide: [https://img-go.com/docs/output-formats#csv](https://img-go.com/docs/output-formats#csv)
- Integration Help: <support@img-go.com>
