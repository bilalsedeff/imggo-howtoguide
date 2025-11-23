/**
 * Insurance Claims Processing - TypeScript Integration Example
 * Extract claims data from images and integrate with claims management systems
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const INSURANCE_CLAIMS_PATTERN_ID = process.env.INSURANCE_CLAIMS_PATTERN_ID || 'pat_insurance_claim_json';

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
    result?: ClaimData;
    error?: string;
  };
}

interface LineItem {
  description: string;
  amount: number;
  quantity?: number;
}

interface ContactInfo {
  phone?: string;
  email?: string;
  address?: string;
}

interface ClaimData {
  claim_number: string;
  policy_number: string;
  claimant_name: string;
  claim_type: string;
  incident_date: string;
  incident_location?: string;
  description?: string;
  line_items?: LineItem[];
  contact_info?: ContactInfo;
}

interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  risk_flags: string[];
}

interface Assignment {
  adjuster_id: string | null;
  adjuster_name: string | null;
  team: string | null;
}

async function uploadClaim(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) {
    throw new Error('IMGGO_API_KEY not set');
  }

  const formData = new FormData();
  formData.append('file', fs.createReadStream(imagePath));

  console.log(`\nUploading insurance claim: ${path.basename(imagePath)}`);

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${INSURANCE_CLAIMS_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `claim-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}

async function waitForResult(jobId: string, maxAttempts: number = 60): Promise<ClaimData> {
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

function calculateClaimTotal(claimData: ClaimData): number {
  const lineItems = claimData.line_items || [];

  return lineItems.reduce((total, item) => {
    const amount = item.amount || 0;
    const quantity = item.quantity || 1;
    return total + (amount * quantity);
  }, 0);
}

function validateClaim(claimData: ClaimData): ValidationResult {
  const validation: ValidationResult = {
    is_valid: true,
    errors: [],
    warnings: [],
    risk_flags: [],
  };

  // Required fields check
  const requiredFields: (keyof ClaimData)[] = [
    'claim_number',
    'claimant_name',
    'incident_date',
    'claim_type'
  ];

  for (const field of requiredFields) {
    if (!claimData[field]) {
      validation.is_valid = false;
      validation.errors.push(`Missing required field: ${field}`);
    }
  }

  // Policy validation
  if (claimData.policy_number) {
    if (claimData.policy_number.length < 5) {
      validation.errors.push('Invalid policy number');
      validation.is_valid = false;
    }
  } else {
    validation.errors.push('Missing policy number');
    validation.is_valid = false;
  }

  // Incident date validation
  if (claimData.incident_date) {
    try {
      const incidentDate = new Date(claimData.incident_date);
      const daysSinceIncident = Math.floor(
        (Date.now() - incidentDate.getTime()) / (1000 * 60 * 60 * 24)
      );

      if (daysSinceIncident < 0) {
        validation.errors.push('Incident date cannot be in the future');
        validation.is_valid = false;
      } else if (daysSinceIncident > 365) {
        validation.warnings.push(
          `Claim filed ${daysSinceIncident} days after incident - requires review`
        );
      }
    } catch (error) {
      validation.errors.push('Invalid incident date format');
      validation.is_valid = false;
    }
  }

  // Claim amount validation
  const totalAmount = calculateClaimTotal(claimData);

  if (totalAmount === 0) {
    validation.errors.push('Claim amount is zero');
    validation.is_valid = false;
  } else if (totalAmount > 50000) {
    validation.risk_flags.push(
      `High value claim: $${totalAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })} - requires senior adjuster review`
    );
  }

  // Fraud detection indicators
  if (claimData.description) {
    const description = claimData.description.toLowerCase();
    const fraudKeywords = ['fire', 'total loss', 'stolen', 'vandalism'];

    const matchedKeywords = fraudKeywords.filter(kw => description.includes(kw));
    if (matchedKeywords.length > 0) {
      validation.risk_flags.push(
        `Requires fraud review - Keywords: ${matchedKeywords.join(', ')}`
      );
    }
  }

  return validation;
}

function determineClaimPriority(claimData: ClaimData, validation: ValidationResult): string {
  const totalAmount = calculateClaimTotal(claimData);
  const claimType = claimData.claim_type.toLowerCase();

  // High priority cases
  if (validation.risk_flags.some(flag => flag.toLowerCase().includes('fraud'))) {
    return 'HIGH - Fraud Review Required';
  }

  if (totalAmount > 100000) {
    return 'HIGH - Large Claim';
  }

  if (['injury', 'medical', 'death'].includes(claimType)) {
    return 'HIGH - Medical/Injury Claim';
  }

  // Medium priority
  if (totalAmount > 10000) {
    return 'MEDIUM';
  }

  if (validation.warnings.length > 0) {
    return 'MEDIUM';
  }

  // Low priority
  return 'LOW - Standard Processing';
}

function assignAdjuster(claimData: ClaimData, priority: string): Assignment {
  const claimType = claimData.claim_type.toLowerCase();

  const assignment: Assignment = {
    adjuster_id: null,
    adjuster_name: null,
    team: null,
  };

  if (priority.includes('HIGH')) {
    assignment.team = 'Senior Adjusters';
    assignment.adjuster_name = 'Senior Team (Auto-assign)';
  } else if (['auto', 'vehicle'].includes(claimType)) {
    assignment.team = 'Auto Claims';
    assignment.adjuster_name = 'Auto Team (Auto-assign)';
  } else if (['property', 'home'].includes(claimType)) {
    assignment.team = 'Property Claims';
    assignment.adjuster_name = 'Property Team (Auto-assign)';
  } else {
    assignment.team = 'General Claims';
    assignment.adjuster_name = 'General Team (Auto-assign)';
  }

  return assignment;
}

async function saveToClaimsSystem(
  claimData: ClaimData,
  validation: ValidationResult,
  assignment: Assignment
): Promise<boolean> {
  console.log('\n' + '='.repeat(60));
  console.log('SAVING TO CLAIMS MANAGEMENT SYSTEM');
  console.log('='.repeat(60));

  const apiPayload = {
    claim_info: {
      claim_number: claimData.claim_number,
      policy_number: claimData.policy_number,
      claim_type: claimData.claim_type,
      status: !validation.is_valid ? 'PENDING_REVIEW' : 'OPEN',
    },
    claimant: {
      name: claimData.claimant_name,
      contact: claimData.contact_info || {},
    },
    incident: {
      date: claimData.incident_date,
      location: claimData.incident_location,
      description: claimData.description,
    },
    financial: {
      claimed_amount: calculateClaimTotal(claimData),
      line_items: claimData.line_items || [],
    },
    assignment,
    validation,
  };

  console.log('API Payload:');
  console.log(JSON.stringify(apiPayload, null, 2));

  // In production: await axios.post('https://claims-system.example.com/api/claims', apiPayload);

  console.log('\n✓ Claim saved to CMS (simulated)');
  return true;
}

function generateAdjusterSummary(
  claimData: ClaimData,
  validation: ValidationResult,
  priority: string,
  assignment: Assignment
): string {
  const lines: string[] = [];

  lines.push('CLAIM ADJUSTER SUMMARY');
  lines.push('='.repeat(60));
  lines.push(`Claim Number: ${claimData.claim_number}`);
  lines.push(`Policy Number: ${claimData.policy_number}`);
  lines.push(`Priority: ${priority}`);
  lines.push(`Assigned To: ${assignment.adjuster_name} (${assignment.team})`);
  lines.push('');
  lines.push('CLAIMANT INFORMATION');
  lines.push(`  Name: ${claimData.claimant_name}`);

  if (claimData.contact_info) {
    lines.push(`  Phone: ${claimData.contact_info.phone || 'N/A'}`);
    lines.push(`  Email: ${claimData.contact_info.email || 'N/A'}`);
  }

  lines.push('');
  lines.push('INCIDENT DETAILS');
  lines.push(`  Date: ${claimData.incident_date}`);
  lines.push(`  Type: ${claimData.claim_type}`);
  lines.push(`  Location: ${claimData.incident_location || 'Not specified'}`);
  lines.push(`  Description: ${claimData.description || 'Not specified'}`);

  lines.push('');
  lines.push('FINANCIAL SUMMARY');
  const totalAmount = calculateClaimTotal(claimData);
  lines.push(`  Total Claimed: $${totalAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}`);

  if (claimData.line_items) {
    lines.push(`  Line Items: ${claimData.line_items.length}`);
  }

  if (validation.risk_flags.length > 0) {
    lines.push('');
    lines.push('⚠ RISK FLAGS:');
    validation.risk_flags.forEach(flag => lines.push(`  - ${flag}`));
  }

  if (validation.warnings.length > 0) {
    lines.push('');
    lines.push('⚠ WARNINGS:');
    validation.warnings.forEach(warning => lines.push(`  - ${warning}`));
  }

  lines.push('');
  lines.push('RECOMMENDED ACTIONS:');
  if (!validation.is_valid) {
    lines.push('  [ ] Obtain missing information');
  }
  if (validation.risk_flags.length > 0) {
    lines.push('  [ ] Conduct fraud investigation');
  }
  if (totalAmount > 50000) {
    lines.push('  [ ] Request senior review');
  }
  lines.push('  [ ] Contact claimant for details');
  lines.push('  [ ] Review policy coverage');
  lines.push('  [ ] Inspect damaged property (if applicable)');
  lines.push('  [ ] Obtain repair estimates');

  return lines.join('\n');
}

async function main() {
  console.log('='.repeat(60));
  console.log('INSURANCE CLAIMS PROCESSING - TYPESCRIPT EXAMPLE');
  console.log('='.repeat(60));

  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/insurance-claim1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n⚠ Test image not found: ${testImage}`);
    console.error('Using placeholder for demonstration');
    process.exit(1);
  }

  try {
    // Upload and process claim
    const jobId = await uploadClaim(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const claimData = await waitForResult(jobId);
    console.log('✓ Processing completed');

    // Save raw JSON
    const outputFile = 'claim_data.json';
    fs.writeFileSync(outputFile, JSON.stringify(claimData, null, 2));
    console.log(`\n✓ Saved claim data to ${outputFile}`);

    console.log('\n' + '='.repeat(60));
    console.log('EXTRACTED CLAIM DATA');
    console.log('='.repeat(60));
    console.log(`Claim Number: ${claimData.claim_number}`);
    console.log(`Policy Number: ${claimData.policy_number}`);
    console.log(`Claimant: ${claimData.claimant_name}`);
    console.log(`Claim Type: ${claimData.claim_type}`);
    console.log(`Incident Date: ${claimData.incident_date}`);

    const totalAmount = calculateClaimTotal(claimData);
    console.log(`Total Amount: $${totalAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}`);

    // Validate claim
    const validation = validateClaim(claimData);

    console.log('\n' + '='.repeat(60));
    console.log('VALIDATION RESULTS');
    console.log('='.repeat(60));
    console.log(`Valid: ${validation.is_valid ? '✓' : '✗'}`);

    if (validation.errors.length > 0) {
      console.log(`\nErrors (${validation.errors.length}):`);
      validation.errors.forEach(error => console.log(`  ✗ ${error}`));
    }

    if (validation.warnings.length > 0) {
      console.log(`\nWarnings (${validation.warnings.length}):`);
      validation.warnings.forEach(warning => console.log(`  ⚠ ${warning}`));
    }

    if (validation.risk_flags.length > 0) {
      console.log(`\nRisk Flags (${validation.risk_flags.length}):`);
      validation.risk_flags.forEach(flag => console.log(`  ⚠ ${flag}`));
    }

    // Determine priority and assign
    const priority = determineClaimPriority(claimData, validation);
    const assignment = assignAdjuster(claimData, priority);

    console.log('\n' + '='.repeat(60));
    console.log('CLAIM ROUTING');
    console.log('='.repeat(60));
    console.log(`Priority: ${priority}`);
    console.log(`Assigned Team: ${assignment.team}`);
    console.log(`Assigned Adjuster: ${assignment.adjuster_name}`);

    // Generate adjuster summary
    const summary = generateAdjusterSummary(claimData, validation, priority, assignment);
    console.log('\n' + summary);

    // Save to claims system
    await saveToClaimsSystem(claimData, validation, assignment);

    // Save adjuster summary
    const summaryFile = 'adjuster_summary.txt';
    fs.writeFileSync(summaryFile, summary);
    console.log(`\n✓ Saved adjuster summary to ${summaryFile}`);

    console.log('\n✓ Insurance claim processing completed!');

  } catch (error) {
    console.error(`\n✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
