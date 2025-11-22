# KYC Identity Verification Automation

Automate Know Your Customer (KYC) compliance with instant ID card, passport, and document verification via direct image upload.

## Business Problem

Financial institutions, crypto exchanges, and online platforms face KYC compliance challenges:

- **Manual verification**: 5-10 minutes per customer for document review
- **Human error**: 15-20% of manual entries contain mistakes
- **Slow onboarding**: 24-48 hour verification delays frustrate customers
- **Compliance risk**: Incomplete or incorrect data leads to regulatory fines
- **Fraud vulnerability**: Manual processes miss forged documents
- **High costs**: $150-200 million spent annually on KYC compliance (large banks)

**Regulatory pressure**: Financial Action Task Force (FATF) requires robust KYC processes globally.

## Solution: Direct Upload Image Verification

Instant ID verification with AI-powered document recognition:

1. **Capture**: User uploads ID via web form or mobile app
2. **Extract**: OCR extracts all text fields from document
3. **Validate**: Check document authenticity, expiration, format
4. **Verify**: Match against databases, sanctions lists
5. **Store**: Encrypted storage for compliance audit trail
6. **Approve**: Instant approval for low-risk cases

**Result**: 95%+ accuracy, sub-60-second verification, 90% cost reduction.

## What Gets Extracted

### From Driver's License

```json
{
  "document_type": "drivers_license",
  "document_number": "D1234567",
  "issuing_country": "USA",
  "issuing_state": "California",
  "personal_info": {
    "full_name": "JOHNSON, SARAH MARIE",
    "date_of_birth": "1985-03-15",
    "gender": "F",
    "height": "5'06\"",
    "eye_color": "BRN",
    "address": "123 Main Street, Los Angeles, CA 90001"
  },
  "document_dates": {
    "issue_date": "2020-03-15",
    "expiration_date": "2028-03-15"
  },
  "verification": {
    "is_expired": false,
    "age": 39,
    "is_adult": true
  }
}
```

### From Passport

```json
{
  "document_type": "passport",
  "passport_number": "P12345678",
  "issuing_country": "USA",
  "nationality": "UNITED STATES OF AMERICA",
  "personal_info": {
    "surname": "JOHNSON",
    "given_names": "SARAH MARIE",
    "date_of_birth": "1985-03-15",
    "gender": "F",
    "place_of_birth": "NEW YORK, USA"
  },
  "document_dates": {
    "issue_date": "2019-06-10",
    "expiration_date": "2029-06-10"
  },
  "mrz_data": "P<USAJOHNSON<<SARAH<MARIE<<<<<<<<<<<<<<<P12345678...",
  "verification": {
    "is_expired": false,
    "mrz_verified": true
  }
}
```

## Pattern Setup

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "KYC Document Verifier",
    "output_format": "json",
    "instructions": "Extract all information from government-issued ID document. Identify document type (drivers license, passport, national ID, residence permit). Extract full name, date of birth, document number, issuing country/state, gender, address if present, issue and expiration dates. For passports, extract MRZ (machine-readable zone) data. Calculate age and flag if document is expired.",
    "schema": {
      "document_type": "string",
      "document_number": "string",
      "issuing_country": "string",
      "personal_info": {
        "full_name": "string",
        "date_of_birth": "date",
        "gender": "string",
        "address": "string"
      },
      "document_dates": {
        "issue_date": "date",
        "expiration_date": "date"
      },
      "verification": {
        "is_expired": "boolean",
        "age": "number"
      }
    }
  }'
```

## Direct Upload Implementation

### Web Form Upload (React)

```javascript
// KYCUploadForm.jsx
import React, { useState } from 'react';
import axios from 'axios';

const KYCUploadForm = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [verifying, setVerifying] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!allowedTypes.includes(selectedFile.type)) {
      alert('Only JPG and PNG files are allowed');
      return;
    }

    // Validate file size (max 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }

    setFile(selectedFile);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(selectedFile);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert('Please select a file');
      return;
    }

    setVerifying(true);

    try {
      // Create FormData for multipart upload
      const formData = new FormData();
      formData.append('file', file);

      // Direct upload to ImgGo
      const uploadResponse = await axios.post(
        `https://img-go.com/api/patterns/${process.env.REACT_APP_PATTERN_ID}/ingest`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${process.env.REACT_APP_API_KEY}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      const jobId = uploadResponse.data.data.job_id;

      // Poll for results
      const verificationResult = await pollJobResult(jobId);

      // Verify document
      const validated = await validateDocument(verificationResult);

      setResult(validated);

      // Store in backend
      await submitToBackend(validated);

    } catch (error) {
      console.error('Verification error:', error);
      alert('Verification failed. Please try again.');
    } finally {
      setVerifying(false);
    }
  };

  const pollJobResult = async (jobId) => {
    let attempts = 0;
    const maxAttempts = 30;

    while (attempts < maxAttempts) {
      const response = await axios.get(
        `https://img-go.com/api/jobs/${jobId}`,
        {
          headers: {
            'Authorization': `Bearer ${process.env.REACT_APP_API_KEY}`
          }
        }
      );

      const data = response.data.data;

      if (data.status === 'completed') {
        return data.result;
      } else if (data.status === 'failed') {
        throw new Error('Verification failed');
      }

      await new Promise(resolve => setTimeout(resolve, 2000));
      attempts++;
    }

    throw new Error('Verification timeout');
  };

  const validateDocument = async (extractedData) => {
    // Client-side validation
    const errors = [];

    // Check if expired
    if (extractedData.verification?.is_expired) {
      errors.push('Document is expired');
    }

    // Check age requirement (18+)
    if (extractedData.verification?.age < 18) {
      errors.push('Must be 18 or older');
    }

    // Check required fields
    if (!extractedData.personal_info?.full_name) {
      errors.push('Name not found');
    }

    if (!extractedData.personal_info?.date_of_birth) {
      errors.push('Date of birth not found');
    }

    return {
      ...extractedData,
      validation: {
        is_valid: errors.length === 0,
        errors: errors
      }
    };
  };

  const submitToBackend = async (data) => {
    // Send to backend for storage and further processing
    await axios.post('/api/kyc/submit', {
      document_data: data,
      user_id: getCurrentUserId()
    });
  };

  return (
    <div className="kyc-upload-form">
      <h2>Identity Verification</h2>
      <p>Upload a clear photo of your government-issued ID</p>

      <form onSubmit={handleSubmit}>
        <div className="upload-area">
          {preview ? (
            <img src={preview} alt="ID Preview" />
          ) : (
            <div className="placeholder">
              <p>Click or drag to upload</p>
              <p className="hint">Supported: JPG, PNG (max 10MB)</p>
            </div>
          )}
          <input
            type="file"
            accept="image/jpeg,image/png,image/jpg"
            onChange={handleFileChange}
            disabled={verifying}
          />
        </div>

        <button type="submit" disabled={!file || verifying}>
          {verifying ? 'Verifying...' : 'Verify Identity'}
        </button>
      </form>

      {result && (
        <div className="result">
          {result.validation.is_valid ? (
            <div className="success">
              <h3>✓ Verification Successful</h3>
              <p>Name: {result.personal_info.full_name}</p>
              <p>DOB: {result.personal_info.date_of_birth}</p>
              <p>Document: {result.document_type} ({result.document_number})</p>
            </div>
          ) : (
            <div className="error">
              <h3>✗ Verification Failed</h3>
              <ul>
                {result.validation.errors.map((error, idx) => (
                  <li key={idx}>{error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default KYCUploadForm;
```

### Backend Processing (Node.js)

```javascript
// kyc-verification.js
const express = require('express');
const multer = require('multer');
const axios = require('axios');
const crypto = require('crypto');
const fs = require('fs');

const router = express.Router();

// Configure multer for file uploads
const upload = multer({
  dest: '/tmp/uploads/',
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  }
});

router.post('/api/kyc/verify', upload.single('document'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  try {
    // Upload to ImgGo
    const formData = new FormData();
    formData.append('file', fs.createReadStream(req.file.path));

    const uploadResponse = await axios.post(
      `https://img-go.com/api/patterns/${process.env.PATTERN_ID}/ingest`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${process.env.IMGGO_API_KEY}`,
          ...formData.getHeaders()
        }
      }
    );

    const jobId = uploadResponse.data.data.job_id;

    // Poll for results
    const extractedData = await pollJobResult(jobId);

    // Validate document
    const validation = validateDocument(extractedData);

    if (!validation.is_valid) {
      return res.status(422).json({
        success: false,
        errors: validation.errors
      });
    }

    // Check against sanctions lists
    const sanctionsCheck = await checkSanctionsList(
      extractedData.personal_info.full_name,
      extractedData.personal_info.date_of_birth
    );

    if (sanctionsCheck.is_sanctioned) {
      return res.status(403).json({
        success: false,
        error: 'Person appears on sanctions list',
        reason: sanctionsCheck.reason
      });
    }

    // Store in database (encrypted)
    const verificationId = await storeVerification({
      user_id: req.body.user_id,
      document_data: encryptData(extractedData),
      verification_status: 'approved',
      verified_at: new Date()
    });

    // Cleanup uploaded file
    fs.unlinkSync(req.file.path);

    res.json({
      success: true,
      verification_id: verificationId,
      status: 'approved',
      verified_fields: {
        name: extractedData.personal_info.full_name,
        dob: extractedData.personal_info.date_of_birth,
        document_type: extractedData.document_type
      }
    });

  } catch (error) {
    console.error('KYC verification error:', error);
    res.status(500).json({ error: 'Verification failed' });
  }
});

function validateDocument(data) {
  const errors = [];

  // Required fields
  if (!data.personal_info?.full_name) {
    errors.push('Name not found on document');
  }

  if (!data.personal_info?.date_of_birth) {
    errors.push('Date of birth not found');
  }

  if (!data.document_number) {
    errors.push('Document number not found');
  }

  // Check expiration
  if (data.verification?.is_expired) {
    errors.push('Document is expired');
  }

  // Age verification (18+)
  if (data.verification?.age < 18) {
    errors.push('Must be 18 or older');
  }

  // Document quality check
  if (data.confidence && data.confidence < 0.85) {
    errors.push('Document image quality too low. Please upload a clearer photo.');
  }

  return {
    is_valid: errors.length === 0,
    errors: errors
  };
}

async function checkSanctionsList(name, dob) {
  // Integrate with OFAC, UN, EU sanctions lists
  // This is a simplified example
  try {
    const response = await axios.post('https://sanctions-api.example.com/check', {
      name: name,
      dob: dob
    });

    return {
      is_sanctioned: response.data.match,
      reason: response.data.reason
    };
  } catch (error) {
    console.error('Sanctions check error:', error);
    return { is_sanctioned: false };
  }
}

function encryptData(data) {
  const algorithm = 'aes-256-gcm';
  const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
  const iv = crypto.randomBytes(16);

  const cipher = crypto.createCipheriv(algorithm, key, iv);

  let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
  encrypted += cipher.final('hex');

  const authTag = cipher.getAuthTag();

  return {
    encrypted: encrypted,
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex')
  };
}

module.exports = router;
```

## Database Schema

```sql
CREATE TABLE kyc_verifications (
    verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    document_type VARCHAR(50),
    document_number_hash VARCHAR(64), -- Hashed for privacy
    full_name_encrypted BYTEA,
    dob_encrypted BYTEA,
    document_data_encrypted BYTEA,
    verification_status VARCHAR(20) DEFAULT 'pending',
    verified_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE kyc_audit_log (
    log_id SERIAL PRIMARY KEY,
    verification_id UUID REFERENCES kyc_verifications(verification_id),
    action VARCHAR(50),
    performed_by VARCHAR(100),
    ip_address INET,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kyc_user ON kyc_verifications(user_id);
CREATE INDEX idx_kyc_status ON kyc_verifications(verification_status);
```

## Compliance & Security

### Data Privacy (GDPR)

```javascript
// Implement right to deletion
router.delete('/api/kyc/:verificationId', async (req, res) => {
  const { verificationId } = req.params;

  // Audit log
  await logAction(verificationId, 'data_deletion_requested', req.user.id);

  // Delete from database
  await db.query(
    'DELETE FROM kyc_verifications WHERE verification_id = $1 AND user_id = $2',
    [verificationId, req.user.id]
  );

  res.json({ success: true });
});

// Data retention policy (auto-delete after 7 years)
async function enforceRetentionPolicy() {
  await db.query(`
    DELETE FROM kyc_verifications
    WHERE created_at < NOW() - INTERVAL '7 years'
  `);
}
```

### Liveness Detection

Prevent photo-of-photo fraud:

```javascript
// Request liveness check during upload
const KYCWithLiveness = () => {
  const requestLivenessCheck = async () => {
    // Prompt user to take selfie with specific gesture
    const selfie = await captureWithGesture('smile');

    // Compare with ID photo
    const match = await compareFaces(idPhoto, selfie);

    if (match.confidence < 0.9) {
      throw new Error('Liveness check failed');
    }
  };
};
```

## Real-World Use Cases

### Cryptocurrency Exchange

```javascript
// Multi-tier verification
const verificationTiers = {
  tier1: {
    maxDailyLimit: 1000,
    requirements: ['id_verification']
  },
  tier2: {
    maxDailyLimit: 10000,
    requirements: ['id_verification', 'proof_of_address']
  },
  tier3: {
    maxDailyLimit: 100000,
    requirements: ['id_verification', 'proof_of_address', 'selfie_verification']
  }
};
```

### Banking Onboarding

```javascript
// Complete digital onboarding workflow
async function digitalOnboarding(userId) {
  // Step 1: ID verification
  const idVerification = await verifyIdentityDocument(userId);

  // Step 2: Address verification
  const addressVerification = await verifyProofOfAddress(userId);

  // Step 3: Credit check
  const creditCheck = await runCreditCheck(userId);

  // Step 4: Account creation
  if (allChecksPass([idVerification, addressVerification, creditCheck])) {
    await createBankAccount(userId);
    await sendWelcomeEmail(userId);
  }
}
```

## Performance Metrics

| Metric | Manual Review | Automated |
|--------|---------------|-----------|
| Verification Time | 5-10 minutes | 30-60 seconds |
| Accuracy | 80-85% | 95-98% |
| Cost per Verification | $15-25 | $0.50-2 |
| False Positive Rate | 10-15% | <3% |
| Customer Drop-off | 40-60% | 15-20% |

## Integration Examples

Available in `integration-examples/`:

- [React Web Form](./integration-examples/react-kyc-upload.jsx)
- [Node.js Backend](./integration-examples/nodejs-kyc-verification.js)
- [Python Flask API](./integration-examples/python-kyc-flask.py)
- [Mobile SDK (React Native)](./integration-examples/react-native-kyc.js)

## Next Steps

- Explore [Medical Prescription](../medical-prescription) for healthcare verification
- Review [Direct Upload Examples](../../examples/direct-upload)
- Set up [Encryption Best Practices](../../integration-guides/encryption.md)

---

**SEO Keywords**: ID verification API, KYC automation, passport OCR, drivers license verification, direct image upload verification, identity document processing

**Sources**:
- [ID Verification API](https://www.idanalyzer.com/)
- [KYC Automation Guide](https://www.klippa.com/en/blog/information/automated-kyc-checks/)
- [OCR for KYC](https://sumsub.com/blog/optical-character-recognition/)
