# Medical Records Digitization and Clinical Notes Extraction

## Overview

Automate medical records digitization by extracting patient information, clinical notes, and diagnostic findings from scanned documents and handwritten forms. Convert medical images into **structured plain text summaries** that integrate with Electronic Health Record (EHR) systems.

**Output Format**: Plain Text (narrative clinical summaries for EHR import)
**Upload Method**: Direct Upload (from hospital scanners, mobile apps, patient portals)
**Industry**: Healthcare, Hospitals, Clinics, Medical Billing, Health Information Management

---

## The Problem

Healthcare organizations face critical medical records challenges:

- **Paper Backlog**: Millions of legacy paper records need digitization
- **Manual Transcription**: Medical coders spend 6-8 hours daily transcribing records
- **Illegible Handwriting**: 20-30% of handwritten notes require clarification
- **Delayed Care**: Missing records delay treatment decisions by hours or days
- **Billing Errors**: Incomplete documentation leads to $125B annually in denied claims
- **Compliance Risks**: Missing HIPAA audit trails for paper record access

Manual digitization is slow, error-prone, and can't keep pace with regulatory requirements for electronic records.

---

## The Solution

ImgGo extracts patient data, clinical notes, and diagnostic findings from medical documents and outputs **plain text narratives** ready for EHR import:

**Workflow**:
```
Medical Document (Direct Upload) → ImgGo API → Plain Text Summary → EHR System
```

**What Gets Extracted**:
- Patient demographics
- Chief complaint and history
- Vital signs and measurements
- Medications and allergies
- Lab results and diagnostics
- Clinical assessments
- Treatment plans
- Provider signatures and dates

---

## Why Plain Text Output?

Plain text is ideal for clinical documentation:

- **EHR Compatible**: All EHR systems accept text-based notes
- **Human Readable**: Physicians can review and edit before finalizing
- **Audit Compliant**: Preserves clinical narrative for legal review
- **Copy-Paste Ready**: Easy transfer into progress notes
- **HL7 Integration**: Direct insertion into HL7 messages
- **Natural Language**: Maintains clinical context and reasoning

**Example Output**:
```
CLINICAL ENCOUNTER NOTE

Patient Name: Jane Smith
MRN: 12345678
DOB: 03/15/1982 (Age 42)
Date of Service: January 22, 2025
Provider: Dr. Michael Chen, MD (NPI: 1234567890)
Facility: Community Health Center - Downtown

CHIEF COMPLAINT:
Persistent cough and shortness of breath for 5 days

HISTORY OF PRESENT ILLNESS:
42-year-old female presents with 5-day history of productive cough with yellow sputum and progressive shortness of breath. Patient reports fever to 101.5°F at home, chills, and fatigue. Denies chest pain, hemoptysis, or recent travel. No known sick contacts. Symptoms worsening despite over-the-counter cough suppressants.

PAST MEDICAL HISTORY:
- Asthma (diagnosed 2010, well-controlled on inhaled corticosteroids)
- Hypertension (diagnosed 2018)
- Seasonal allergies

MEDICATIONS:
- Fluticasone inhaler 110mcg, 2 puffs BID
- Lisinopril 10mg PO daily
- Albuterol inhaler PRN

ALLERGIES:
- Penicillin (rash)
- Shellfish (anaphylaxis)

SOCIAL HISTORY:
- Non-smoker
- Occasional alcohol use (1-2 drinks per week)
- Works as elementary school teacher
- Lives with spouse and two children

VITAL SIGNS:
- Temperature: 100.8°F (oral)
- Blood Pressure: 138/86 mmHg
- Heart Rate: 92 bpm
- Respiratory Rate: 22 breaths/min
- Oxygen Saturation: 94% on room air
- Weight: 165 lbs

PHYSICAL EXAMINATION:
General: Alert and oriented, appears mildly ill, in no acute distress
HEENT: Oropharynx clear, no tonsillar exudates, TMs clear bilaterally
Neck: No lymphadenopathy, no JVD
Lungs: Decreased breath sounds right lower lobe, crackles noted, no wheezing
Heart: Regular rate and rhythm, no murmurs
Abdomen: Soft, non-tender, non-distended, normal bowel sounds
Extremities: No edema, pulses 2+ bilaterally

DIAGNOSTIC STUDIES:
Chest X-ray (2-view): Right lower lobe infiltrate consistent with pneumonia. No pleural effusion. Heart size normal.

Rapid Flu Test: Negative
Strep Test: Negative

ASSESSMENT:
1. Community-acquired pneumonia, right lower lobe
2. Asthma, stable
3. Hypertension, adequately controlled

PLAN:
1. Community-Acquired Pneumonia:
   - Start azithromycin 500mg PO day 1, then 250mg PO days 2-5 (patient reports penicillin allergy)
   - Supportive care: rest, hydration, antipyretics as needed
   - Follow-up chest X-ray in 6 weeks if symptoms persist
   - Return precautions given: if fever persists >3 days, worsening shortness of breath, or chest pain

2. Asthma:
   - Continue current inhaler regimen
   - May use albuterol inhaler Q4-6H PRN for cough/wheezing
   - Monitor for exacerbation given current respiratory infection

3. Hypertension:
   - Continue lisinopril 10mg daily
   - Recheck BP at follow-up visit

FOLLOW-UP:
Telephone follow-up in 3 days to assess symptom improvement. Return to clinic in 2 weeks or sooner if symptoms worsen.

PATIENT EDUCATION:
Discussed pneumonia diagnosis, importance of medication compliance, hydration, rest. Patient instructed to use humidifier, avoid irritants, and monitor temperature. Patient verbalized understanding and agreement with treatment plan.

TIME SPENT:
30 minutes face-to-face with patient, including history, examination, and counseling.

Electronically signed by:
Dr. Michael Chen, MD
January 22, 2025, 3:45 PM
```

---

## Implementation Guide

### Step 1: Create Medical Records Pattern

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "Medical Records - Clinical Notes Extractor",
  "output_format": "text",
  "instructions": "Extract all clinical information and generate comprehensive plain text clinical encounter note following standard medical documentation format",
  "schema": {
    "extract_sections": [
      "patient_demographics",
      "chief_complaint",
      "history_of_present_illness",
      "past_medical_history",
      "medications",
      "allergies",
      "vital_signs",
      "physical_examination",
      "diagnostic_studies",
      "assessment",
      "treatment_plan",
      "follow_up_instructions",
      "provider_signature"
    ],
    "format": "clinical_narrative",
    "compliance": "HIPAA"
  }
}
```

### Step 2: Direct Upload from Hospital Scanner (Python)

```python
import requests
import time
from datetime import datetime

IMGGO_API_KEY = "your_api_key"
IMGGO_PATTERN_ID = "pat_medical_records_xyz"

def digitize_medical_record(scanned_file_path, patient_mrn):
    """
    Upload scanned medical record and extract clinical text
    """
    # Read scanned file
    with open(scanned_file_path, 'rb') as f:
        files = {'file': f}

        # Upload directly to ImgGo
        response = requests.post(
            f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
            headers={
                "Authorization": f"Bearer {IMGGO_API_KEY}",
                "Idempotency-Key": f"mrn-{patient_mrn}-{datetime.now().timestamp()}"
            },
            files=files
        )

    job_id = response.json()["data"]["job_id"]

    # Poll for results
    clinical_text = poll_for_result(job_id)

    return clinical_text


def poll_for_result(job_id):
    """Poll until extraction completes"""
    for _ in range(60):  # Medical records may take longer
        result = requests.get(
            f"https://img-go.com/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {IMGGO_API_KEY}"}
        ).json()

        if result["data"]["status"] == "completed":
            return result["data"]["result"]
        elif result["data"]["status"] == "failed":
            raise Exception(f"Extraction failed: {result['data'].get('error')}")

        time.sleep(3)

    raise Exception("Extraction timeout")


# Example: Digitize scanned encounter form
clinical_text = digitize_medical_record(
    "/mnt/scanner/queue/encounter_form_20250122.pdf",
    "12345678"
)

print("=== Extracted Clinical Note ===")
print(clinical_text)

# Save to text file for review
with open(f"clinical_note_12345678_{datetime.now().strftime('%Y%m%d')}.txt", "w") as f:
    f.write(clinical_text)
```

### Step 3: EHR Integration (Epic/Cerner)

```python
import requests

# Epic FHIR API integration
EPIC_FHIR_BASE = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
EPIC_ACCESS_TOKEN = os.environ['EPIC_ACCESS_TOKEN']

def import_to_epic(clinical_text, patient_mrn):
    """
    Import clinical note to Epic EHR using FHIR DocumentReference
    """
    # Create FHIR DocumentReference resource
    document_reference = {
        "resourceType": "DocumentReference",
        "status": "current",
        "type": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "34133-9",
                "display": "Summarization of Episode Note"
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_mrn}"
        },
        "date": datetime.now().isoformat(),
        "author": [{
            "display": "ImgGo Medical Records Digitization"
        }],
        "description": "Digitized clinical encounter note",
        "content": [{
            "attachment": {
                "contentType": "text/plain",
                "data": base64.b64encode(clinical_text.encode()).decode()
            }
        }]
    }

    # Post to Epic FHIR API
    response = requests.post(
        f"{EPIC_FHIR_BASE}/DocumentReference",
        headers={
            "Authorization": f"Bearer {EPIC_ACCESS_TOKEN}",
            "Content-Type": "application/fhir+json"
        },
        json=document_reference
    )

    if response.status_code == 201:
        print(f"Clinical note imported to Epic for patient {patient_mrn}")
        return response.json()['id']
    else:
        raise Exception(f"Epic import failed: {response.status_code} - {response.text}")


# Import to Epic
epic_doc_id = import_to_epic(clinical_text, "12345678")
```

### Step 4: Medical Billing Integration

Extract billing codes from clinical text:

```python
import re

def extract_billing_codes(clinical_text):
    """
    Extract ICD-10 and CPT codes from clinical assessment
    """
    codes = {
        "icd10": [],
        "cpt": []
    }

    # Common diagnosis mapping (simplified example)
    diagnosis_mapping = {
        "pneumonia": "J18.9",
        "asthma": "J45.909",
        "hypertension": "I10"
    }

    # Extract diagnoses from assessment section
    assessment_match = re.search(r'ASSESSMENT:(.*?)PLAN:', clinical_text, re.DOTALL)

    if assessment_match:
        assessment = assessment_match.group(1).lower()

        for condition, icd_code in diagnosis_mapping.items():
            if condition in assessment:
                codes["icd10"].append({
                    "code": icd_code,
                    "description": condition.title()
                })

    # Extract CPT codes based on encounter type
    if "30 minutes face-to-face" in clinical_text:
        codes["cpt"].append({
            "code": "99214",
            "description": "Office visit, established patient, moderate complexity"
        })

    return codes


# Extract codes for billing
billing_codes = extract_billing_codes(clinical_text)

print("\n=== Billing Codes ===")
print("ICD-10 Diagnoses:")
for code in billing_codes["icd10"]:
    print(f"  {code['code']}: {code['description']}")

print("\nCPT Procedures:")
for code in billing_codes["cpt"]:
    print(f"  {code['code']}: {code['description']}")
```

---

## Performance Metrics

### Digitization Speed

| Task | Manual Process | With ImgGo | Savings |
|------|----------------|------------|---------|
| Read handwritten note | 10 minutes | 2 minutes | 80% |
| Transcribe to text | 25 minutes | Automated | 100% |
| Review and edit | 10 minutes | 5 minutes | 50% |
| Import to EHR | 5 minutes | Automated | 100% |
| **Total per record** | **50 minutes** | **7 minutes** | **86%** |

### Business Impact

**Hospital with 500 patient encounters daily**:

- **Medical Coder Productivity**: $1.2M/year (saved 35 hours/day × $65/hour × 250 days)
- **Faster Billing**: $800K/year (3-day faster claim submission improves cash flow)
- **Accuracy**: 40% reduction in claim denials from incomplete documentation
- **Compliance**: 100% digital records for audits
- **Total Annual Benefit**: $2.5M
- **ImgGo Cost**: $90K/year
- **ROI**: 2,678%

---

## Best Practices

### HIPAA Compliance

- **Encryption**: All uploads via TLS 1.3, data encrypted at rest
- **Access Logging**: Log all document access with user ID and timestamp
- **De-identification**: Optionally redact PHI for research use
- **BAA Required**: Business Associate Agreement with ImgGo

### Quality Assurance

- **Human Review**: Physician reviews 100% of extracted notes before signing
- **Spot Audits**: Quality team audits 10% of digitized records monthly
- **Feedback Loop**: Submit corrections to improve extraction accuracy

---

## Related Use Cases

- [Medical Prescription](../medical-prescription) - Prescription text extraction
- [KYC Verification](../kyc-verification) - ID verification for patient registration
- [Insurance Claims](../insurance-claims) - Medical claim documentation

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- HIPAA Compliance: [https://img-go.com/hipaa](https://img-go.com/hipaa)
- Integration Help: support@img-go.com
