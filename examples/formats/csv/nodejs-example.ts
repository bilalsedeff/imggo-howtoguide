/**
 * ImgGo CSV Output - Node.js/TypeScript Example
 * Process images and get CSV results
 */

import axios, { AxiosError } from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

const FormData = require('form-data');

dotenv.config();

const IMGGO_BASE_URL = 'https://img-go.com/api';
const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const INVENTORY_PATTERN_ID = process.env.INVENTORY_PATTERN_ID || 'pat_inventory_csv';

interface JobResponse {
  success: boolean;
  data: {
    job_id: string;
    status: string;
  };
}

interface JobStatusResponse {
  success: boolean;
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'succeeded' | 'failed';
    result?: string;  // CSV string
    manifest?: any;  // CSV or structured data
    error?: string;
  };
}

const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

async function uploadImage(imagePath: string, patternId: string): Promise<string> {
  console.log(`\nUploading image: ${imagePath}`);

  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  const idempotencyKey = `csv-nodejs-${path.basename(imagePath)}-${Date.now()}`;

  try {
    const response = await axios.post<JobResponse>(
      `${IMGGO_BASE_URL}/patterns/${patternId}/ingest`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${IMGGO_API_KEY}`,
          'Idempotency-Key': idempotencyKey,
          ...formData.getHeaders(),
        },
      }
    );

    const jobId = response.data.data.job_id;
    console.log(`✓ Upload successful! Job ID: ${jobId}`);

    return jobId;

  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      console.error('Upload failed:', axiosError.response?.data || axiosError.message);
    }
    throw error;
  }
}

async function waitForResult(
  jobId: string,
  maxAttempts: number = 30,
  waitSeconds: number = 2
): Promise<string> {
  console.log('\nPolling for CSV result...');

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    console.log(`  Attempt ${attempt}/${maxAttempts}...`);

    try {
      const response = await axios.get<JobStatusResponse>(
        `${IMGGO_BASE_URL}/jobs/${jobId}`,
        {
          headers: {
            'Authorization': `Bearer ${IMGGO_API_KEY}`,
          },
        }
      );

      const { status, manifest, result, error } = response.data.data;

      if (status === 'completed' || status === 'succeeded') {
        const data = manifest || result;
        if (!data) {
          throw new Error('Job completed but no result returned');
        }
        console.log('✓ Processing completed!');
        return data;
      }

      if (status === 'failed') {
        throw new Error(`Job failed: ${error || 'Unknown error'}`);
      }

      await sleep(waitSeconds * 1000);

    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;
        console.error('Status check failed:', axiosError.response?.data || axiosError.message);
      }
      throw error;
    }
  }

  throw new Error(`Timeout: Job did not complete within ${maxAttempts * waitSeconds} seconds`);
}

function parseCSV(csvString: string): Array<Record<string, string>> {
  const lines = csvString.trim().split('\n');
  if (lines.length < 2) {
    throw new Error('CSV has no data rows');
  }

  const headers = lines[0].split(',').map(h => h.trim());
  const rows: Array<Record<string, string>> = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim());
    const row: Record<string, string> = {};

    headers.forEach((header, index) => {
      row[header] = values[index] || '';
    });

    rows.push(row);
  }

  return rows;
}

function displayCSV(csvString: string): void {
  console.log('\n========================================');
  console.log('Extracted CSV Data');
  console.log('========================================\n');

  console.log(csvString);

  // Parse and display summary
  try {
    const rows = parseCSV(csvString);
    console.log(`\n========================================`);
    console.log(`Total items: ${rows.length}`);
    console.log('========================================');

    if (rows.length > 0) {
      console.log('\nFirst 5 items:');
      rows.slice(0, 5).forEach((row, index) => {
        console.log(`\n${index + 1}. ${JSON.stringify(row, null, 2)}`);
      });

      if (rows.length > 5) {
        console.log(`\n... and ${rows.length - 5} more items`);
      }
    }
  } catch (error) {
    console.warn('Could not parse CSV for summary');
  }
}

function saveResult(csvString: string, outputFile: string): void {
  fs.writeFileSync(outputFile, csvString, 'utf-8');
  console.log(`\n✓ Saved to ${outputFile}`);
}

async function main(): Promise<void> {
  console.log('========================================');
  console.log('ImgGo CSV Extraction - Node.js Example');
  console.log('========================================');

  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY environment variable not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../test-images/inventory1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n✗ Error: Test image not found: ${testImage}`);
    process.exit(1);
  }

  try {
    const jobId = await uploadImage(testImage, INVENTORY_PATTERN_ID);
    const csvResult = await waitForResult(jobId);

    displayCSV(csvResult);

    const outputFile = 'inventory_result.csv';
    saveResult(csvResult, outputFile);

    console.log('\n✓ CSV extraction completed!');

  } catch (error) {
    console.error('\n✗ Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { uploadImage, waitForResult, parseCSV, displayCSV, saveResult };
