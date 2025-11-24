# Medical Prescription Processing

Convert handwritten or printed prescription images to structured text for pharmacy management systems and electronic health records.

## Business Problem

Pharmacies and healthcare providers struggle with prescription processing:

- **Handwriting errors**: Misread prescriptions lead to medication errors
- **Manual data entry**: 3-5 minutes per prescription for manual transcription
- **Delayed fulfillment**: Long wait times frustrate patients
- **Compliance risks**: Incomplete or illegible prescriptions cause legal issues
- **Lost prescriptions**: Paper prescriptions get misplaced or damaged

**Impact**: Medical errors from illegible prescriptions cause 7,000+ deaths annually in the US.

## Solution: Image to Plain Text Extraction

Automated prescription digitization with AI-powered OCR:

1. **Capture**: Patient or pharmacist photographs prescription
2. **Upload**: Direct image upload via mobile app or scanner
3. **Extract**: Convert to plain text or structured data
4. **Validate**: Check against drug databases and dosage rules
5. **Integrate**: Sync to pharmacy management system (PioneerRx, QS/1, Liberty)
6. **Dispense**: Pharmacist verifies and fills prescription

**Result**: 90% faster processing, 50% reduction in transcription errors, better patient safety.

## Quick Start

### Step 1: Create Your Pattern (One-Time Setup)

Choose your preferred method to create the pattern:

#### Option A: Using Python Script

```bash
cd use-cases/medical-prescription
python create-pattern.py
```

#### Option B: Using curl Script

```bash
cd use-cases/medical-prescription
bash create-pattern.sh
```

Both scripts will:

- Create a pattern optimized for prescription processing
- Save the Pattern ID to `pattern_id.txt`
- Display instructions for adding it to your `.env` file

#### Add to your .env file

```bash
IMGGO_API_KEY=your_api_key_here
PRESCRIPTION_PATTERN_ID=pattern_id_from_script
```

### Step 2: Test the Pattern

Test with a sample prescription:

```bash
# Python
python test-pattern.py

# curl
bash test-pattern.sh
```

Results will be saved to `outputs/prescription1_output.txt`

### Step 3: Integrate with Your System

See the `integration-examples/` folder for production-ready integrations:

- [Python Pharmacy Integration](./integration-examples/python-example.py) - Full pharmacy workflow
- [TypeScript/Node.js](./integration-examples/nodejs-example.ts) - Express.js webhook server

## What Gets Extracted

### Plain Text Output (Human-Readable)

Perfect for pharmacist review and patient documentation:

```text
Prescription for: Sarah Johnson
Date of Birth: 03/15/1985
Date: January 21, 2025

Medication: Amoxicillin 500mg capsules
Dosage: Take one capsule by mouth three times daily with food
Quantity: #30 capsules
Duration: 10 days
Refills: None

Prescriber: Dr. Michael Chen, MD
DEA Number: BC1234563
Signature: [Present]

Special Instructions: Complete full course even if symptoms improve.
May cause drowsiness. Avoid alcohol.
```

### Structured JSON Output-1

For direct integration with pharmacy systems:

```json
{
  "patient": {
    "full_name": "Sarah Johnson",
    "date_of_birth": "1985-03-15"
  },
  "prescription_date": "2025-01-21",
  "medications": [
    {
      "drug_name": "Amoxicillin",
      "strength": "500mg",
      "form": "capsules",
      "dosage": "Take one capsule by mouth three times daily with food",
      "quantity": 30,
      "duration_days": 10,
      "refills": 0
    }
  ],
  "prescriber": {
    "name": "Dr. Michael Chen",
    "credentials": "MD",
    "dea_number": "BC1234563",
    "signature_present": true
  },
  "special_instructions": "Complete full course even if symptoms improve. May cause drowsiness. Avoid alcohol."
}
```

## Pattern Setup

### Plain Text Output

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prescription to Text",
    "output_format": "text",
    "instructions": "Extract prescription details in human-readable format. Include patient name and DOB, prescription date, medication name, strength, form (tablets/capsules/liquid), dosage instructions, quantity, duration, refills, prescriber name and credentials, DEA number if present, and any special instructions or warnings. Format as clear, readable text suitable for pharmacist review."
  }'
```

### Structured JSON Output-2

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prescription Data Extractor",
    "output_format": "json",
    "instructions": "Extract all prescription details including patient info, medications with dosage, prescriber details, and special instructions.",
    "schema": {
      "patient": {
        "full_name": "string",
        "date_of_birth": "date"
      },
      "prescription_date": "date",
      "medications": [
        {
          "drug_name": "string",
          "strength": "string",
          "form": "string",
          "dosage": "string",
          "quantity": "number",
          "duration_days": "number",
          "refills": "number"
        }
      ],
      "prescriber": {
        "name": "string",
        "credentials": "string",
        "dea_number": "string",
        "signature_present": "boolean"
      },
      "special_instructions": "string"
    }
  }'
```

## Direct Image Upload Example

### Mobile App Integration (React Native)

```javascript
// PrescriptionCapture.js
import React, { useState } from 'react';
import { View, Button, Text, Image } from 'react-native';
import { launchCamera } from 'react-native-image-picker';
import axios from 'axios';

const PrescriptionCapture = () => {
  const [prescription, setPrescription] = useState(null);
  const [processing, setProcessing] = useState(false);

  const captureAndProcess = async () => {
    // Launch camera
    const result = await launchCamera({
      mediaType: 'photo',
      quality: 0.8,
      includeBase64: false
    });

    if (result.didCancel) return;

    const photo = result.assets[0];
    setProcessing(true);

    try {
      // Create form data for direct upload
      const formData = new FormData();
      formData.append('file', {
        uri: photo.uri,
        type: 'image/jpeg',
        name: 'prescription.jpg'
      });

      // Upload directly to API
      const response = await axios.post(
        `https://img-go.com/api/patterns/${PATTERN_ID}/ingest`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      const jobId = response.data.data.job_id;

      // Poll for results
      const result = await pollJobResult(jobId);

      setPrescription(result);

      // Navigate to verification screen
      navigation.navigate('PrescriptionVerification', {
        prescription: result,
        originalImage: photo.uri
      });

    } catch (error) {
      console.error('Processing error:', error);
      Alert.alert('Error', 'Failed to process prescription');
    } finally {
      setProcessing(false);
    }
  };

  const pollJobResult = async (jobId) => {
    let attempts = 0;
    const maxAttempts = 30;

    while (attempts < maxAttempts) {
      const response = await axios.get(
        `https://img-go.com/api/jobs/${jobId}`,
        {
          headers: { 'Authorization': `Bearer ${API_KEY}` }
        }
      );

      const data = response.data.data;

      if (data.status === 'completed') {
        return data.result;
      } else if (data.status === 'failed') {
        throw new Error('Processing failed');
      }

      await new Promise(resolve => setTimeout(resolve, 2000));
      attempts++;
    }

    throw new Error('Processing timeout');
  };

  return (
    <View style={styles.container}>
      <Button
        title={processing ? "Processing..." : "Scan Prescription"}
        onPress={captureAndProcess}
        disabled={processing}
      />
      {prescription && (
        <View>
          <Text>Patient: {prescription.patient.full_name}</Text>
          <Text>Medication: {prescription.medications[0].drug_name}</Text>
        </View>
      )}
    </View>
  );
};

export default PrescriptionCapture;
```

### Python Backend (Flask)

```python
import os
from flask import Flask, request, jsonify
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

API_KEY = os.environ["IMGGO_API_KEY"]
PATTERN_ID = os.environ["IMGGO_PATTERN_ID"]
UPLOAD_FOLDER = '/tmp/prescriptions'

@app.route('/api/prescription/upload', methods=['POST'])
def upload_prescription():
    """Handle direct prescription image upload"""

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Validate file type
    allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf'}
    ext = file.filename.rsplit('.', 1)[1].lower()

    if ext not in allowed_extensions:
        return jsonify({'error': 'Invalid file type'}), 400

    # Save temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # Upload to ImgGo via multipart form-data
        with open(filepath, 'rb') as f:
            files = {'file': f}

            response = requests.post(
                f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
                headers={"Authorization": f"Bearer {API_KEY}"},
                files=files
            )

        job_id = response.json()["data"]["job_id"]

        # Poll for results
        result = poll_job_result(job_id)

        # Validate prescription data
        validation = validate_prescription(result)

        if not validation['is_valid']:
            return jsonify({
                'success': False,
                'errors': validation['errors']
            }), 422

        # Store in database
        prescription_id = store_prescription(result)

        return jsonify({
            'success': True,
            'prescription_id': prescription_id,
            'data': result
        })

    finally:
        # Cleanup temporary file
        os.remove(filepath)

def validate_prescription(data):
    """Validate extracted prescription data"""
    errors = []

    # Check required fields
    if not data.get('patient', {}).get('full_name'):
        errors.append("Patient name is missing")

    if not data.get('medications') or len(data['medications']) == 0:
        errors.append("No medications found")

    if not data.get('prescriber', {}).get('name'):
        errors.append("Prescriber name is missing")

    # Check DEA number format (if present)
    dea = data.get('prescriber', {}).get('dea_number')
    if dea and not is_valid_dea_number(dea):
        errors.append("Invalid DEA number format")

    # Check for controlled substances
    for med in data.get('medications', []):
        if is_controlled_substance(med['drug_name']):
            if not dea:
                errors.append(f"{med['drug_name']} requires DEA number")

    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def is_valid_dea_number(dea):
    """Validate DEA number format"""
    import re
    # DEA format: 2 letters + 7 digits
    return bool(re.match(r'^[A-Z]{2}\d{7}$', dea))

def is_controlled_substance(drug_name):
    """Check if drug is controlled substance"""
    controlled_drugs = [
        'oxycodone', 'hydrocodone', 'morphine', 'fentanyl',
        'adderall', 'alprazolam', 'diazepam'
    ]
    return any(drug.lower() in drug_name.lower() for drug in controlled_drugs)

def store_prescription(data):
    """Store prescription in database"""
    import psycopg2

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO prescriptions (
            patient_name, patient_dob, prescription_date,
            prescriber_name, dea_number, raw_data
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING prescription_id
    """, (
        data['patient']['full_name'],
        data['patient']['date_of_birth'],
        data['prescription_date'],
        data['prescriber']['name'],
        data['prescriber'].get('dea_number'),
        psycopg2.extras.Json(data)
    ))

    prescription_id = cur.fetchone()[0]

    # Insert medications
    for med in data['medications']:
        cur.execute("""
            INSERT INTO prescription_medications (
                prescription_id, drug_name, strength, dosage, quantity, refills
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            prescription_id,
            med['drug_name'],
            med['strength'],
            med['dosage'],
            med['quantity'],
            med['refills']
        ))

    conn.commit()
    cur.close()
    conn.close()

    return prescription_id

if __name__ == '__main__':
    app.run(port=5000)
```

## Database Schema

```sql
CREATE TABLE prescriptions (
    prescription_id SERIAL PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL,
    patient_dob DATE,
    prescription_date DATE NOT NULL,
    prescriber_name VARCHAR(255) NOT NULL,
    dea_number VARCHAR(20),
    status VARCHAR(50) DEFAULT 'pending',
    filled_at TIMESTAMP,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prescription_medications (
    medication_id SERIAL PRIMARY KEY,
    prescription_id INTEGER REFERENCES prescriptions(prescription_id),
    drug_name VARCHAR(255) NOT NULL,
    strength VARCHAR(50),
    dosage TEXT,
    quantity INTEGER,
    refills INTEGER DEFAULT 0
);

CREATE INDEX idx_prescriptions_patient ON prescriptions(patient_name);
CREATE INDEX idx_prescriptions_date ON prescriptions(prescription_date);
CREATE INDEX idx_prescriptions_status ON prescriptions(status);
```

## Compliance & Safety

### HIPAA Compliance

Ensure prescription images are handled securely:

```python
# Encrypt at rest
from cryptography.fernet import Fernet

def encrypt_prescription_data(data):
    """Encrypt sensitive prescription data"""
    key = os.environ["ENCRYPTION_KEY"]
    f = Fernet(key)
    encrypted = f.encrypt(json.dumps(data).encode())
    return encrypted

# Audit logging
def log_prescription_access(user_id, prescription_id, action):
    """Log all prescription access for HIPAA compliance"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'prescription_id': prescription_id,
        'action': action,
        'ip_address': request.remote_addr
    }
    audit_logger.info(json.dumps(log_entry))
```

### Drug Interaction Checks

```python
def check_drug_interactions(new_medications, patient_id):
    """Check for drug interactions with patient's current medications"""
    current_meds = get_patient_current_medications(patient_id)

    interactions = []

    for new_med in new_medications:
        for current_med in current_meds:
            interaction = check_interaction_database(
                new_med['drug_name'],
                current_med['drug_name']
            )

            if interaction:
                interactions.append({
                    'drug1': new_med['drug_name'],
                    'drug2': current_med['drug_name'],
                    'severity': interaction['severity'],
                    'description': interaction['description']
                })

    return interactions
```

## Integration Examples

Complete examples in `integration-examples/`:

- [React Native Mobile App](./integration-examples/react-native-prescription-app.js) - Camera capture and upload
- [Python Flask API](./integration-examples/python-flask-prescription-api.py) - Backend processing
- [Pharmacy System Integration](./integration-examples/pioneerrx-integration.py) - PioneerRx API sync
- [Node.js Express Server](./integration-examples/nodejs-express-prescription.js) - Direct upload handler

## Real-World Implementation

### Pharmacy Workflow

```plaintext
1. Patient drops off prescription (photo or paper)
2. Technician scans/photographs prescription
3. System extracts data automatically
4. Pharmacist reviews and verifies on screen
5. System checks insurance, interactions, inventory
6. Prescription queued for filling
7. Patient notified via SMS when ready

Processing time: 2 minutes (vs 8 minutes manual)
```

### Telemedicine Integration

```python
@app.route('/api/telemedicine/prescription', methods=['POST'])
def telemedicine_prescription():
    """Process prescription from telemedicine visit"""

    # Receive prescription image from telemedicine platform
    prescription_image_url = request.json['prescription_url']
    patient_id = request.json['patient_id']
    visit_id = request.json['visit_id']

    # Process via URL (no download needed)
    response = requests.post(
        f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"image_url": prescription_image_url}
    )

    job_id = response.json()["data"]["job_id"]
    result = poll_job_result(job_id)

    # Link to patient and visit
    prescription_id = store_prescription(result)
    link_to_visit(prescription_id, visit_id)

    # Send to patient's preferred pharmacy
    send_to_pharmacy(prescription_id, patient_id)

    return jsonify({'prescription_id': prescription_id})
```

## Performance Metrics

| Metric | Manual Entry | Automated |
|--------|-------------|-----------|
| Processing Time | 3-5 minutes | 20-40 seconds |
| Transcription Errors | 5-10% | <2% |
| Patient Wait Time | 15-30 minutes | 5-10 minutes |
| Pharmacist Productivity | 12 Rx/hour | 30+ Rx/hour |
| Cost per Prescription | $3.50 | $0.80 |

## Troubleshooting

### Issue: Handwriting Not Recognized

**Solutions**:

- Request clearer image (better lighting, focus)
- Ask prescriber to print prescriptions
- Flag for manual review if confidence < 85%

### Issue: Missing DEA Number

**Solution**: Pattern instructions:

```plaintext
"Extract DEA number if present. For controlled substances, flag if DEA number is missing or illegible."
```

### Issue: Ambiguous Dosage

**Solution**: Implement pharmacist verification:

```python
if result.get('confidence', 100) < 90:
    flag_for_pharmacist_review(prescription_id, "Low confidence on dosage")
```

## Next Steps

- Explore [Insurance Claims](../insurance-claims) for photo-based workflows
- Review [KYC Verification](../kyc-verification) for ID card processing
- Set up [Direct Upload](../../examples/direct-upload) examples

---

**SEO Keywords**: prescription image to text, handwritten prescription OCR, pharmacy automation, prescription digitization, medical OCR, rx image processing

**Sources**:

- [Prescription OCR Guide](https://www.v7labs.com/blog/prescription-reader-ocr-complete-guide-to-healthcare-document-automation)
- [Medical Prescription Automation](https://www.affinda.com/documents/medical-prescription)
