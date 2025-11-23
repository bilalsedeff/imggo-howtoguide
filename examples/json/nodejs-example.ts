/**
 * ImgGo JSON Output - Node.js/TypeScript Example
 * Process images and get JSON results using TypeScript
 */

import axios, { AxiosError } from 'axios';
import FormData from 'form-data';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Configuration
const IMGGO_BASE_URL = 'https://img-go.com/api';
const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const INVOICE_PATTERN_ID = process.env.INVOICE_PATTERN_ID || 'pat_invoice_json';

// TypeScript interfaces for type safety
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
    status: 'queued' | 'processing' | 'completed' | 'failed';
    result?: InvoiceData;
    error?: string;
  };
}

interface InvoiceData {
  invoice_number: string;
  vendor: {
    name: string;
    address?: string;
  } | string;
  invoice_date: string;
  due_date: string;
  subtotal?: number;
  tax_amount?: number;
  total_amount: number;
  currency?: string;
  line_items?: LineItem[];
}

interface LineItem {
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
}

/**
 * Sleep helper function
 */
const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Upload image to ImgGo for processing
 */
async function uploadImage(imagePath: string, patternId: string): Promise<string> {
  console.log(`\nUploading image: ${imagePath}`);

  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  const idempotencyKey = `nodejs-${path.basename(imagePath)}-${Date.now()}`;

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
    } else {
      console.error('Upload failed:', error);
    }
    throw error;
  }
}

/**
 * Poll job status until completion
 */
async function waitForResult(
  jobId: string,
  maxAttempts: number = 30,
  waitSeconds: number = 2
): Promise<InvoiceData> {
  console.log('\nPolling for result...');

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

      // Still processing, wait and retry
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

/**
 * Display invoice data
 */
function displayInvoiceData(invoice: InvoiceData): void {
  console.log('\n========================================');
  console.log('Extracted Invoice Data (JSON)');
  console.log('========================================\n');

  console.log(JSON.stringify(invoice, null, 2));

  console.log('\n========================================');
  console.log('Key Fields:');
  console.log('========================================');

  const vendorName = typeof invoice.vendor === 'string'
    ? invoice.vendor
    : invoice.vendor.name;

  console.log(`  Invoice Number: ${invoice.invoice_number}`);
  console.log(`  Vendor: ${vendorName}`);
  console.log(`  Total Amount: $${invoice.total_amount.toFixed(2)}`);
  console.log(`  Invoice Date: ${invoice.invoice_date}`);
  console.log(`  Due Date: ${invoice.due_date}`);

  if (invoice.line_items) {
    console.log(`  Line Items: ${invoice.line_items.length}`);

    if (invoice.line_items.length > 0) {
      console.log('\n  Line Items Detail:');
      invoice.line_items.forEach((item, index) => {
        console.log(`    ${index + 1}. ${item.description}`);
        console.log(`       Qty: ${item.quantity} × $${item.unit_price} = $${item.amount}`);
      });
    }
  }
}

/**
 * Save result to file
 */
function saveResult(invoice: InvoiceData, outputFile: string): void {
  fs.writeFileSync(
    outputFile,
    JSON.stringify(invoice, null, 2),
    'utf-8'
  );
  console.log(`\n✓ Saved to ${outputFile}`);
}

/**
 * Main function
 */
async function main(): Promise<void> {
  console.log('========================================');
  console.log('ImgGo JSON Extraction - Node.js Example');
  console.log('========================================');

  // Check API key
  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY environment variable not set');
    console.error('  Set it in .env file or export IMGGO_API_KEY=your_key');
    process.exit(1);
  }

  // Check test image
  const testImage = path.join(__dirname, '../../test-images/invoice1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n✗ Error: Test image not found: ${testImage}`);
    process.exit(1);
  }

  try {
    // Step 1: Upload image
    const jobId = await uploadImage(testImage, INVOICE_PATTERN_ID);

    // Step 2: Wait for result
    const invoice = await waitForResult(jobId);

    // Step 3: Display result
    displayInvoiceData(invoice);

    // Step 4: Save to file
    const outputFile = 'invoice_result.json';
    saveResult(invoice, outputFile);

    console.log('\n✓ Processing complete!');

  } catch (error) {
    console.error('\n✗ Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

// Export for use as module
export {
  uploadImage,
  waitForResult,
  displayInvoiceData,
  saveResult,
};
