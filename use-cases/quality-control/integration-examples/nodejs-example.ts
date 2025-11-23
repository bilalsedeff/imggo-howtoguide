/**
 * Quality Control - TypeScript Integration Example
 * Extract defect data from inspection images in CSV format
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const QUALITY_CONTROL_PATTERN_ID = process.env.QUALITY_CONTROL_PATTERN_ID || 'pat_quality_control_csv';

interface JobResponse {
  success: boolean;
  data: { job_id: string; status: string };
}

interface JobResult {
  success: boolean;
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    result?: string;
    error?: string;
  };
}

interface Defect {
  defect_type: string;
  severity: string;
  location: string;
  description?: string;
}

interface QualityMetrics {
  total_defects: number;
  critical_defects: number;
  major_defects: number;
  minor_defects: number;
  defect_density: number;
  pass_fail_status: string;
}

async function uploadInspectionImage(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) throw new Error('IMGGO_API_KEY not set');

  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  console.log(`\nUploading inspection image: ${path.basename(imagePath)}`);

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${QUALITY_CONTROL_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `qc-${Date.now()}`,
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
      { headers: { 'Authorization': `Bearer ${IMGGO_API_KEY}` } }
    );

    const { status, manifest, result, error } = response.data.data;

    if (status === 'completed' || status === 'succeeded') {
      const data = manifest || result;
      if (!data) throw new Error('No result in completed job');
      return data;
    }

    if (status === 'failed') {
      throw new Error(`Job failed: ${error || 'Unknown error'}`);
    }

    console.log(`Attempt ${attempt}/${maxAttempts}: Status = ${status}`);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error('Timeout waiting for job completion');
}

function parseDefectCSV(csvString: string): Defect[] {
  const lines = csvString.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim());

  const defects: Defect[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim());
    const defect: any = {};

    headers.forEach((header, index) => {
      defect[header] = values[index] || '';
    });

    defects.push(defect as Defect);
  }

  return defects;
}

function calculateQualityMetrics(defects: Defect[]): QualityMetrics {
  const metrics: QualityMetrics = {
    total_defects: defects.length,
    critical_defects: 0,
    major_defects: 0,
    minor_defects: 0,
    defect_density: 0,
    pass_fail_status: 'PASS',
  };

  for (const defect of defects) {
    const severity = defect.severity.toLowerCase();

    if (severity === 'critical') {
      metrics.critical_defects++;
    } else if (severity === 'major') {
      metrics.major_defects++;
    } else if (severity === 'minor') {
      metrics.minor_defects++;
    }
  }

  // Determine pass/fail
  if (metrics.critical_defects > 0) {
    metrics.pass_fail_status = 'FAIL - Critical defects found';
  } else if (metrics.major_defects > 3) {
    metrics.pass_fail_status = 'FAIL - Too many major defects';
  } else if (metrics.total_defects > 10) {
    metrics.pass_fail_status = 'REVIEW - High defect count';
  }

  return metrics;
}

async function saveToMESSystem(defects: Defect[], metrics: QualityMetrics, batchId: string): Promise<boolean> {
  console.log('\n' + '='.repeat(60));
  console.log('SAVING TO MES SYSTEM');
  console.log('='.repeat(60));

  const payload = {
    batch_id: batchId,
    inspection_date: new Date().toISOString(),
    total_defects: metrics.total_defects,
    critical_defects: metrics.critical_defects,
    major_defects: metrics.major_defects,
    minor_defects: metrics.minor_defects,
    status: metrics.pass_fail_status,
    defect_details: defects,
  };

  console.log(`MES Payload: ${payload.status}`);
  console.log(`Batch ID: ${batchId}`);
  console.log(`Total Defects: ${metrics.total_defects}`);

  // In production: await axios.post('https://mes-system.example.com/api/inspections', payload);

  console.log('\n✓ Inspection saved to MES (simulated)');
  return true;
}

function generateInspectionReport(defects: Defect[], metrics: QualityMetrics): string {
  const lines: string[] = [];

  lines.push('QUALITY INSPECTION REPORT');
  lines.push('='.repeat(60));
  lines.push(`Inspection Date: ${new Date().toLocaleString()}`);
  lines.push(`Status: ${metrics.pass_fail_status}`);
  lines.push('');
  lines.push('SUMMARY');
  lines.push(`  Total Defects: ${metrics.total_defects}`);
  lines.push(`  Critical: ${metrics.critical_defects}`);
  lines.push(`  Major: ${metrics.major_defects}`);
  lines.push(`  Minor: ${metrics.minor_defects}`);
  lines.push('');
  lines.push('DEFECT DETAILS');

  defects.forEach((defect, index) => {
    lines.push(`\n${index + 1}. ${defect.defect_type}`);
    lines.push(`   Severity: ${defect.severity}`);
    lines.push(`   Location: ${defect.location}`);
  });

  lines.push('');
  lines.push('RECOMMENDED ACTIONS:');

  if (metrics.critical_defects > 0) {
    lines.push('  ✗ REJECT BATCH - Critical defects require rework');
  } else if (metrics.major_defects > 0) {
    lines.push('  ⚠ REVIEW - Major defects may require correction');
  } else {
    lines.push('  ✓ APPROVE - Quality standards met');
  }

  return lines.join('\n');
}

async function main() {
  console.log('='.repeat(60));
  console.log('QUALITY CONTROL - TYPESCRIPT EXAMPLE');
  console.log('='.repeat(60));

  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/quality-control1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n⚠ Test image not found: ${testImage}`);
    process.exit(1);
  }

  try {
    const jobId = await uploadInspectionImage(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const csvResult = await waitForResult(jobId);
    console.log('✓ Processing completed');

    // Save raw CSV
    const outputFile = 'inspection_defects.csv';
    fs.writeFileSync(outputFile, csvResult);
    console.log(`\n✓ Saved CSV to ${outputFile}`);

    // Parse CSV
    const defects = parseDefectCSV(csvResult);

    console.log('\n' + '='.repeat(60));
    console.log('DETECTED DEFECTS');
    console.log('='.repeat(60));
    defects.slice(0, 5).forEach((defect, index) => {
      console.log(`${index + 1}. ${defect.defect_type} - ${defect.severity}`);
    });

    // Calculate metrics
    const metrics = calculateQualityMetrics(defects);

    console.log('\n' + '='.repeat(60));
    console.log('QUALITY METRICS');
    console.log('='.repeat(60));
    console.log(`Total Defects: ${metrics.total_defects}`);
    console.log(`Critical: ${metrics.critical_defects}`);
    console.log(`Major: ${metrics.major_defects}`);
    console.log(`Minor: ${metrics.minor_defects}`);
    console.log(`Status: ${metrics.pass_fail_status}`);

    // Generate report
    const report = generateInspectionReport(defects, metrics);
    console.log('\n' + report);

    // Save to MES
    const batchId = `BATCH-${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}`;
    await saveToMESSystem(defects, metrics, batchId);

    // Save report
    const reportFile = 'inspection_report.txt';
    fs.writeFileSync(reportFile, report);
    console.log(`\n✓ Saved inspection report to ${reportFile}`);

    console.log('\n✓ Quality control inspection completed!');

  } catch (error) {
    console.error(`\n✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
