# GDPR Data Anonymization and PII Detection

## Overview

Automate GDPR compliance by detecting and redacting Personally Identifiable Information (PII) from images and documents. Extract PII locations and categories into **structured JSON** for anonymization workflows and compliance audits.

**Output Format**: JSON (structured PII detection results with redaction coordinates)
**Upload Method**: Direct Upload (from compliance systems, document processors, data warehouses)
**Industry**: SaaS Platforms, Financial Services, Healthcare, HR Systems, Legal Discovery

---

## The Problem

Organizations handling EU customer data face critical GDPR challenges:

- **Manual Redaction**: Legal teams spend hours manually blacking out PII from documents
- **Incomplete Detection**: 15-20% of PII instances missed in manual review
- **Subject Access Requests**: Must locate and redact PII across thousands of documents in 30 days
- **Data Breach Risk**: Undetected PII in logs, screenshots, and documents
- **Audit Compliance**: Unable to prove comprehensive PII handling
- **Processing Cost**: $45-85 per document for legal review and redaction

Manual PII detection can't scale to GDPR's strict timelines and comprehensive requirements.

---

## The Solution

ImgGo detects all PII in images (screenshots, scanned documents, photos) and outputs **structured JSON** with PII categories, locations, and anonymization recommendations:

**Workflow**:
```
Document with PII (Direct Upload) → ImgGo API → JSON PII Map → Automated Redaction
```

**What Gets Detected**:
- Names (full names, first/last separately)
- Email addresses
- Phone numbers
- Physical addresses
- National IDs (SSN, passport, driver's license)
- Financial data (credit cards, bank accounts)
- Biometric data (faces, fingerprints)
- IP addresses and device IDs
- Dates of birth
- Health information

---

## Why JSON Output?

JSON enables automated GDPR compliance workflows:

- **Programmatic Redaction**: Apply pixel masks to exact coordinates
- **Audit Trails**: Document what PII was found and how it was handled
- **Selective Anonymization**: Redact some fields while preserving others
- **Risk Scoring**: Calculate exposure based on PII types detected
- **Compliance Reporting**: Generate reports for DPOs and auditors

**Example Output**:
```json
{
  "document_id": "doc_20250122_screenshot_001",
  "analysis_timestamp": "2025-01-22T14:30:45Z",
  "gdpr_compliance_check": true,

  "summary": {
    "pii_detected": true,
    "total_pii_instances": 12,
    "risk_level": "high",
    "recommended_action": "redact_all_before_storage",
    "retention_policy_applicable": "7_years_financial_records"
  },

  "pii_categories_detected": [
    {
      "category": "full_name",
      "count": 3,
      "severity": "high",
      "gdpr_article": "Article 4(1) - Personal Data"
    },
    {
      "category": "email_address",
      "count": 2,
      "severity": "high",
      "gdpr_article": "Article 4(1) - Personal Data"
    },
    {
      "category": "phone_number",
      "count": 1,
      "severity": "medium",
      "gdpr_article": "Article 4(1) - Personal Data"
    },
    {
      "category": "national_id",
      "count": 1,
      "severity": "critical",
      "gdpr_article": "Article 9 - Special Category Data"
    },
    {
      "category": "credit_card",
      "count": 1,
      "severity": "critical",
      "gdpr_article": "Article 9 - Special Category Data"
    },
    {
      "category": "physical_address",
      "count": 2,
      "severity": "medium",
      "gdpr_article": "Article 4(1) - Personal Data"
    },
    {
      "category": "date_of_birth",
      "count": 1,
      "severity": "medium",
      "gdpr_article": "Article 4(1) - Personal Data"
    },
    {
      "category": "face_biometric",
      "count": 1,
      "severity": "critical",
      "gdpr_article": "Article 9 - Special Category Data (Biometric)"
    }
  ],

  "pii_instances": [
    {
      "instance_id": "pii_001",
      "category": "full_name",
      "detected_value": "John Michael Smith",
      "confidence": 0.98,
      "location": {
        "bounding_box": {
          "x": 150,
          "y": 230,
          "width": 180,
          "height": 25
        },
        "page": 1
      },
      "context": "appears in header section of invoice",
      "recommended_redaction": "full",
      "pseudonymization_option": "PERSON_1"
    },
    {
      "instance_id": "pii_002",
      "category": "email_address",
      "detected_value": "john.smith@example.com",
      "confidence": 0.99,
      "location": {
        "bounding_box": {
          "x": 150,
          "y": 265,
          "width": 220,
          "height": 20
        },
        "page": 1
      },
      "context": "contact information section",
      "recommended_redaction": "full",
      "pseudonymization_option": "EMAIL_1"
    },
    {
      "instance_id": "pii_003",
      "category": "phone_number",
      "detected_value": "+1 (555) 123-4567",
      "confidence": 0.96,
      "location": {
        "bounding_box": {
          "x": 150,
          "y": 295,
          "width": 160,
          "height": 20
        },
        "page": 1
      },
      "context": "contact information section",
      "recommended_redaction": "full",
      "pseudonymization_option": "PHONE_1"
    },
    {
      "instance_id": "pii_004",
      "category": "national_id",
      "detected_value": "123-45-6789",
      "national_id_type": "US_SSN",
      "confidence": 0.97,
      "location": {
        "bounding_box": {
          "x": 420,
          "y": 380,
          "width": 120,
          "height": 20
        },
        "page": 1
      },
      "context": "identification section",
      "recommended_redaction": "full",
      "pseudonymization_option": "XXX-XX-XXXX",
      "gdpr_special_category": true
    },
    {
      "instance_id": "pii_005",
      "category": "credit_card",
      "detected_value": "4532 1234 5678 9010",
      "card_type": "Visa",
      "confidence": 0.99,
      "location": {
        "bounding_box": {
          "x": 200,
          "y": 520,
          "width": 200,
          "height": 20
        },
        "page": 1
      },
      "context": "payment information",
      "recommended_redaction": "partial_last_4",
      "pseudonymization_option": "**** **** **** 9010",
      "pci_dss_applicable": true
    },
    {
      "instance_id": "pii_006",
      "category": "physical_address",
      "detected_value": "123 Main Street, Apartment 4B, San Francisco, CA 94102",
      "confidence": 0.94,
      "location": {
        "bounding_box": {
          "x": 150,
          "y": 325,
          "width": 350,
          "height": 45
        },
        "page": 1
      },
      "context": "billing address section",
      "recommended_redaction": "full",
      "pseudonymization_option": "[ADDRESS_REDACTED]"
    },
    {
      "instance_id": "pii_007",
      "category": "date_of_birth",
      "detected_value": "03/15/1982",
      "confidence": 0.91,
      "location": {
        "bounding_box": {
          "x": 420,
          "y": 410,
          "width": 90,
          "height": 20
        },
        "page": 1
      },
      "context": "personal information section",
      "recommended_redaction": "year_only",
      "pseudonymization_option": "XX/XX/1982"
    },
    {
      "instance_id": "pii_008",
      "category": "face_biometric",
      "confidence": 0.96,
      "location": {
        "bounding_box": {
          "x": 650,
          "y": 180,
          "width": 120,
          "height": 140
        },
        "page": 1
      },
      "context": "profile photo",
      "recommended_redaction": "blur_face",
      "gdpr_special_category": true,
      "biometric_template_extractable": true
    }
  ],

  "redaction_map": {
    "full_redaction_boxes": [
      {"x": 150, "y": 230, "width": 180, "height": 25},
      {"x": 150, "y": 265, "width": 220, "height": 20},
      {"x": 150, "y": 295, "width": 160, "height": 20},
      {"x": 420, "y": 380, "width": 120, "height": 20},
      {"x": 150, "y": 325, "width": 350, "height": 45}
    ],
    "partial_redaction_boxes": [
      {"x": 200, "y": 520, "width": 160, "height": 20, "show_last_chars": 4}
    ],
    "blur_regions": [
      {"x": 650, "y": 180, "width": 120, "height": 140, "blur_strength": "heavy"}
    ]
  },

  "compliance_metadata": {
    "data_subject_identifiable": true,
    "special_category_data_present": true,
    "requires_consent_tracking": true,
    "retention_policy_required": true,
    "cross_border_transfer": false,
    "right_to_erasure_applicable": true,
    "dpia_recommended": true
  },

  "recommended_actions": [
    {
      "action": "redact_pii",
      "priority": "immediate",
      "reason": "Special category data detected (SSN, biometric)"
    },
    {
      "action": "update_audit_log",
      "priority": "high",
      "reason": "GDPR Article 30 record of processing activities"
    },
    {
      "action": "notify_dpo",
      "priority": "high",
      "reason": "Special category data processing requires DPO review"
    },
    {
      "action": "verify_consent",
      "priority": "medium",
      "reason": "Check lawful basis for processing this personal data"
    }
  ]
}
```

---

## Implementation Guide

### Step 1: PII Detection Pattern

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "GDPR PII Detector and Anonymizer",
  "output_format": "json",
  "schema": {
    "pii_detected": "boolean",
    "pii_instances": [
      {
        "category": "enum[full_name,email,phone,ssn,credit_card,address,dob,ip_address,face_biometric]",
        "detected_value": "string",
        "confidence": "number",
        "location": {
          "bounding_box": {
            "x": "number",
            "y": "number",
            "width": "number",
            "height": "number"
          }
        },
        "recommended_redaction": "enum[full,partial,blur,pseudonymize]"
      }
    ]
  }
}
```

### Step 2: Automated Redaction Pipeline

```python
import requests
from PIL import Image, ImageDraw
import io

IMGGO_API_KEY = "your_api_key"
IMGGO_PATTERN_ID = "pat_gdpr_pii_xyz"

def detect_and_redact_pii(image_path, output_path):
    """
    Detect PII in image and create anonymized version
    """
    # Upload to ImgGo for PII detection
    with open(image_path, 'rb') as f:
        response = requests.post(
            f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
            headers={
                "Authorization": f"Bearer {IMGGO_API_KEY}",
                "Content-Type": "multipart/form-data"
            },
            files={'file': f}
        )

    job_id = response.json()["data"]["job_id"]

    # Poll for PII detection results
    pii_data = poll_for_result(job_id)

    # Parse JSON
    import json
    pii_map = json.loads(pii_data)

    # Apply redactions to image
    redacted_image = apply_redactions(image_path, pii_map)

    # Save anonymized image
    redacted_image.save(output_path)

    # Log to compliance audit trail
    log_pii_redaction(pii_map, image_path, output_path)

    print(f"Redacted {pii_map['summary']['total_pii_instances']} PII instances")
    print(f"Anonymized image saved to: {output_path}")

    return pii_map


def apply_redactions(image_path, pii_map):
    """
    Apply black boxes and blur to PII locations
    """
    # Load original image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Apply full redaction boxes (black rectangles)
    for box in pii_map['redaction_map']['full_redaction_boxes']:
        draw.rectangle(
            [box['x'], box['y'], box['x'] + box['width'], box['y'] + box['height']],
            fill='black'
        )

    # Apply partial redactions (show last 4 digits of credit cards)
    for box in pii_map['redaction_map'].get('partial_redaction_boxes', []):
        # Redact all but last portion
        redact_width = box['width'] - (box.get('show_last_chars', 4) * 8)
        draw.rectangle(
            [box['x'], box['y'], box['x'] + redact_width, box['y'] + box['height']],
            fill='black'
        )

    # Apply blur to faces
    from PIL import ImageFilter

    for region in pii_map['redaction_map'].get('blur_regions', []):
        # Extract region
        bbox = (region['x'], region['y'],
                region['x'] + region['width'],
                region['y'] + region['height'])

        face_region = img.crop(bbox)

        # Apply heavy blur
        blurred = face_region.filter(ImageFilter.GaussianBlur(radius=20))

        # Paste back
        img.paste(blurred, bbox)

    return img


def log_pii_redaction(pii_map, original_path, redacted_path):
    """
    Log redaction to GDPR compliance database
    """
    import psycopg2

    conn = psycopg2.connect(os.environ['COMPLIANCE_DB_URL'])
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO gdpr_pii_redactions (
            document_id, original_path, redacted_path,
            pii_instances_count, special_category_data,
            redaction_timestamp, risk_level
        ) VALUES (%s, %s, %s, %s, %s, NOW(), %s)
    """, (
        pii_map['document_id'],
        original_path,
        redacted_path,
        pii_map['summary']['total_pii_instances'],
        pii_map['compliance_metadata']['special_category_data_present'],
        pii_map['summary']['risk_level']
    ))

    # Log each PII instance
    for pii in pii_map['pii_instances']:
        cursor.execute("""
            INSERT INTO pii_instances_log (
                document_id, category, confidence, gdpr_article, redaction_applied
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            pii_map['document_id'],
            pii['category'],
            pii['confidence'],
            next((cat['gdpr_article'] for cat in pii_map['pii_categories_detected']
                  if cat['category'] == pii['category']), None),
            True
        ))

    conn.commit()
    cursor.close()
    conn.close()


# Example: Redact PII from screenshot
pii_map = detect_and_redact_pii(
    'screenshot_with_customer_data.png',
    'screenshot_anonymized.png'
)
```

### Step 3: Subject Access Request (SAR) Automation

```python
def process_sar_request(data_subject_email):
    """
    Process GDPR Subject Access Request - find and redact all documents
    """
    # Find all documents containing this email
    documents = find_documents_with_pii(data_subject_email)

    sar_package = {
        'data_subject': data_subject_email,
        'request_date': datetime.now().isoformat(),
        'documents_found': len(documents),
        'documents': []
    }

    for doc in documents:
        # Detect PII in document
        pii_map = detect_and_redact_pii(doc['path'], f"redacted_{doc['id']}.png")

        # Check if data subject's PII is in this document
        subject_pii_found = any(
            data_subject_email.lower() in pii['detected_value'].lower()
            for pii in pii_map['pii_instances']
            if pii['category'] == 'email_address'
        )

        if subject_pii_found:
            sar_package['documents'].append({
                'document_id': doc['id'],
                'document_type': doc['type'],
                'created_date': doc['created_at'],
                'pii_instances': len(pii_map['pii_instances']),
                'download_url': f"https://sar.company.com/download/{doc['id']}"
            })

    # Generate SAR response PDF
    generate_sar_pdf(sar_package)

    # Send to data subject within 30 days
    send_sar_response(data_subject_email, sar_package)

    return sar_package
```

### Step 4: Data Breach Notification

```python
def assess_data_breach_risk(compromised_documents):
    """
    Analyze PII in breached documents and generate breach notification
    """
    affected_individuals = set()
    special_category_exposed = False
    pii_categories_exposed = set()

    for doc_path in compromised_documents:
        pii_map = detect_pii_only(doc_path)  # Don't redact, just detect

        # Collect affected individuals
        for pii in pii_map['pii_instances']:
            if pii['category'] == 'email_address':
                affected_individuals.add(pii['detected_value'])
            elif pii.get('gdpr_special_category'):
                special_category_exposed = True

            pii_categories_exposed.add(pii['category'])

    # Determine if notification required (Article 33/34)
    breach_severity = {
        'affected_individuals_count': len(affected_individuals),
        'special_category_data': special_category_exposed,
        'pii_categories': list(pii_categories_exposed),
        'notification_required': len(affected_individuals) > 0 or special_category_exposed,
        'supervisory_authority_72h_deadline': special_category_exposed,
        'individual_notification_required': special_category_exposed
    }

    if breach_severity['notification_required']:
        # Notify DPO and legal
        notify_dpo_of_breach(breach_severity)

        if breach_severity['supervisory_authority_72h_deadline']:
            # Must notify supervisory authority within 72 hours
            notify_supervisory_authority(breach_severity)

    return breach_severity
```

---

## Performance Metrics

### Redaction Speed

| Task | Manual Process | With ImgGo | Savings |
|------|----------------|------------|---------|
| Identify PII | 15 minutes | 30 seconds | 97% |
| Apply redactions | 20 minutes | Automated | 100% |
| Quality review | 10 minutes | 2 minutes | 80% |
| **Total per document** | **45 minutes** | **2.5 minutes** | **94%** |

### Business Impact

**SaaS company** (1,000 SAR requests/year):

- **Legal Team Savings**: $1.8M/year (750 hours saved × $120/hour × 12 months)
- **Compliance Risk**: 99% reduction in missed PII
- **Breach Response**: 10× faster breach assessment
- **GDPR Fines Avoided**: Potential €20M fine avoided through proper PII handling
- **Total Annual Benefit**: $2.5M+
- **ImgGo Cost**: $60K/year
- **ROI**: 4,067%

---

## Best Practices

### Detection Accuracy

- **Human Validation**: Review 100% of special category data detections
- **False Positives**: Acceptable to over-detect and redact conservatively
- **Context Awareness**: Consider document type when determining PII sensitivity

### Audit Requirements

- **Log Everything**: Record every PII detection and redaction action
- **Retention**: Keep audit logs for 7 years minimum
- **Access Control**: Restrict access to PII logs to DPO and compliance team

---

## Related Use Cases

- [KYC Verification](../kyc-verification) - Identity verification with PII handling
- [Content Moderation](../content-moderation) - Safety detection in user content
- [Medical Records](../medical-records) - Protected health information handling

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- GDPR Compliance: [https://img-go.com/gdpr](https://img-go.com/gdpr)
- Integration Help: support@img-go.com
