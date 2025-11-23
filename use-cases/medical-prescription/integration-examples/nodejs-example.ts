/**
 * Medical Prescription Processing - TypeScript Integration Example
 * Extract prescription data from images and integrate with pharmacy systems
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const PRESCRIPTION_PATTERN_ID = process.env.PRESCRIPTION_PATTERN_ID || 'pat_prescription_text';

interface JobResponse {
  success: boolean;
  data: {
    job_id: string;
    status: string;
  };
}

interface JobResult {
  success: boolean;
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    result?: string; // Plain text prescription
    error?: string;
  };
}

interface Prescription {
  patient_name: string | null;
  patient_dob: string | null;
  prescriber: string | null;
  prescriber_license: string | null;
  date_written: string | null;
  medications: string[];
  pharmacy_notes: string | null;
}

interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
}

interface PharmacyPayload {
  patient: {
    name: string | null;
    dob: string | null;
  };
  prescriber: {
    name: string | null;
    license: string | null;
  };
  prescription_date: string | null;
  medications: string[];
  notes: string | null;
}

async function uploadPrescription(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) {
    throw new Error('IMGGO_API_KEY not set');
  }

  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  console.log(`\nUploading prescription: ${path.basename(imagePath)}`);

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${PRESCRIPTION_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `prescription-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}

async function waitForResult(jobId: string, maxAttempts: number = 60): Promise<string> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const response = await axios.get<JobResult>(
      `${IMGGO_BASE_URL}/jobs/${jobId}`,
      {
        headers: {
          'Authorization': `Bearer ${IMGGO_API_KEY}`,
        },
      }
    );

    const { status, result, error } = response.data.data;

    if (status === 'completed') {
      if (!result) {
        throw new Error('No result in completed job');
      }
      return result;
    }

    if (status === 'failed') {
      throw new Error(`Job failed: ${error || 'Unknown error'}`);
    }

    console.log(`Attempt ${attempt}/${maxAttempts}: Status = ${status}`);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error('Timeout waiting for job completion');
}

function parsePrescriptionText(text: string): Prescription {
  const prescription: Prescription = {
    patient_name: null,
    patient_dob: null,
    prescriber: null,
    prescriber_license: null,
    date_written: null,
    medications: [],
    pharmacy_notes: null,
  };

  // Extract patient name
  const patientMatch = text.match(/(?:Patient|Name):\s*([^\n]+)/i);
  if (patientMatch) {
    prescription.patient_name = patientMatch[1].trim();
  }

  // Extract date of birth
  const dobMatch = text.match(/(?:DOB|Date of Birth):\s*([^\n]+)/i);
  if (dobMatch) {
    prescription.patient_dob = dobMatch[1].trim();
  }

  // Extract prescriber
  const prescriberMatch = text.match(/(?:Prescriber|Doctor|Physician):\s*([^\n]+)/i);
  if (prescriberMatch) {
    prescription.prescriber = prescriberMatch[1].trim();
  }

  // Extract license number
  const licenseMatch = text.match(/(?:License|DEA|NPI):\s*([^\n]+)/i);
  if (licenseMatch) {
    prescription.prescriber_license = licenseMatch[1].trim();
  }

  // Extract prescription date
  const dateMatch = text.match(/Date:\s*([^\n]+)/i);
  if (dateMatch) {
    prescription.date_written = dateMatch[1].trim();
  }

  // Extract medications
  const medPatterns = [
    /(\w+)\s+(\d+\s*mg)\s+([^\n]+)/gi,
    /Rx:\s*([^\n]+)/gi,
    /Medication:\s*([^\n]+)/gi,
  ];

  for (const pattern of medPatterns) {
    const matches = text.matchAll(pattern);
    for (const match of matches) {
      prescription.medications.push(match[0].trim());
    }
  }

  // Extract pharmacy notes
  const notesMatch = text.match(/(?:Notes|Instructions|Directions):\s*([^\n]+)/i);
  if (notesMatch) {
    prescription.pharmacy_notes = notesMatch[1].trim();
  }

  return prescription;
}

function validatePrescription(prescription: Prescription): ValidationResult {
  const validation: ValidationResult = {
    is_valid: true,
    errors: [],
    warnings: [],
  };

  // Check required fields
  if (!prescription.patient_name) {
    validation.is_valid = false;
    validation.errors.push('Missing patient name');
  }

  if (!prescription.prescriber) {
    validation.is_valid = false;
    validation.errors.push('Missing prescriber information');
  }

  if (prescription.medications.length === 0) {
    validation.is_valid = false;
    validation.errors.push('No medications found');
  }

  // Check prescriber license
  if (!prescription.prescriber_license) {
    validation.warnings.push('Prescriber license number not found - manual verification required');
  }

  // Check prescription date
  if (!prescription.date_written) {
    validation.warnings.push('Prescription date not found');
  }

  return validation;
}

async function saveToPharmacySystem(prescription: Prescription): Promise<boolean> {
  console.log('\n' + '='.repeat(60));
  console.log('SAVING TO PHARMACY SYSTEM');
  console.log('='.repeat(60));

  const payload: PharmacyPayload = {
    patient: {
      name: prescription.patient_name,
      dob: prescription.patient_dob,
    },
    prescriber: {
      name: prescription.prescriber,
      license: prescription.prescriber_license,
    },
    prescription_date: prescription.date_written,
    medications: prescription.medications,
    notes: prescription.pharmacy_notes,
  };

  console.log('API Payload prepared:');
  console.log(JSON.stringify(payload, null, 2));

  // In production, integrate with pharmacy system API
  // const response = await axios.post('https://pharmacy-system.example.com/api/prescriptions', payload);

  console.log('\n✓ Prescription saved to pharmacy system (simulated)');
  return true;
}

function generateFillInstructions(prescription: Prescription): string {
  const lines: string[] = [];

  lines.push('PHARMACIST FILL INSTRUCTIONS');
  lines.push('='.repeat(60));
  lines.push(`Patient: ${prescription.patient_name}`);
  lines.push(`DOB: ${prescription.patient_dob}`);
  lines.push('');
  lines.push(`Prescriber: ${prescription.prescriber}`);
  lines.push(`License: ${prescription.prescriber_license}`);
  lines.push(`Date: ${prescription.date_written}`);
  lines.push('');
  lines.push('MEDICATIONS TO FILL:');

  prescription.medications.forEach((med, index) => {
    lines.push(`  ${index + 1}. ${med}`);
  });

  if (prescription.pharmacy_notes) {
    lines.push('');
    lines.push(`Notes: ${prescription.pharmacy_notes}`);
  }

  lines.push('');
  lines.push('VERIFICATION CHECKLIST:');
  lines.push('  [ ] Patient ID verified');
  lines.push('  [ ] Insurance checked');
  lines.push('  [ ] Drug interactions reviewed');
  lines.push('  [ ] Prescriber credentials confirmed');
  lines.push('  [ ] Patient counseling completed');

  return lines.join('\n');
}

async function main() {
  console.log('='.repeat(60));
  console.log('MEDICAL PRESCRIPTION PROCESSING - TYPESCRIPT EXAMPLE');
  console.log('='.repeat(60));

  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/medical-prescription1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n⚠ Test image not found: ${testImage}`);
    console.error('Using placeholder for demonstration');
    process.exit(1);
  }

  try {
    // Upload and process prescription
    const jobId = await uploadPrescription(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const prescriptionText = await waitForResult(jobId);
    console.log('✓ Processing completed');

    // Save raw text
    const outputFile = 'prescription_raw.txt';
    fs.writeFileSync(outputFile, prescriptionText);
    console.log(`\n✓ Saved raw text to ${outputFile}`);

    // Parse prescription
    const prescription = parsePrescriptionText(prescriptionText);

    console.log('\n' + '='.repeat(60));
    console.log('EXTRACTED PRESCRIPTION DATA');
    console.log('='.repeat(60));
    console.log(`Patient: ${prescription.patient_name}`);
    console.log(`DOB: ${prescription.patient_dob}`);
    console.log(`Prescriber: ${prescription.prescriber}`);
    console.log(`License: ${prescription.prescriber_license}`);
    console.log(`Date: ${prescription.date_written}`);
    console.log(`\nMedications (${prescription.medications.length}):`);
    prescription.medications.forEach(med => {
      console.log(`  - ${med}`);
    });

    // Validate prescription
    const validation = validatePrescription(prescription);

    console.log('\n' + '='.repeat(60));
    console.log('VALIDATION RESULTS');
    console.log('='.repeat(60));
    console.log(`Valid: ${validation.is_valid ? '✓' : '✗'}`);

    if (validation.errors.length > 0) {
      console.log(`\nErrors (${validation.errors.length}):`);
      validation.errors.forEach(error => {
        console.log(`  ✗ ${error}`);
      });
    }

    if (validation.warnings.length > 0) {
      console.log(`\nWarnings (${validation.warnings.length}):`);
      validation.warnings.forEach(warning => {
        console.log(`  ⚠ ${warning}`);
      });
    }

    // Generate fill instructions
    if (validation.is_valid) {
      const fillInstructions = generateFillInstructions(prescription);
      console.log('\n' + fillInstructions);

      // Save to pharmacy system
      await saveToPharmacySystem(prescription);

      // Save fill instructions
      const instructionsFile = 'fill_instructions.txt';
      fs.writeFileSync(instructionsFile, fillInstructions);
      console.log(`\n✓ Saved fill instructions to ${instructionsFile}`);
    } else {
      console.log('\n⚠ Prescription requires manual review before processing');
    }

    console.log('\n✓ Prescription processing completed!');

  } catch (error) {
    console.error(`\n✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
