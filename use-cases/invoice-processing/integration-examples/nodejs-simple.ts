/**
 * Simple Invoice Processing Example with ImgGo (Node.js/TypeScript)
 * Extracts structured data from invoice images
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';

// Configuration
const IMGGO_API_KEY = process.env.IMGGO_API_KEY || 'your_api_key_here';
const IMGGO_BASE_URL = 'https://img-go.com/api';

// Pattern ID for invoice processing
const INVOICE_PATTERN_ID = process.env.INVOICE_PATTERN_ID || 'pat_invoice_example';

// Types
interface JobResponse {
  success: boolean;
  data: {
    job_id: string;
    status: string;
    message?: string;
  };
}

interface JobStatusResponse {
  success: boolean;
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    result?: any;
    error?: string;
  };
}

/**
 * Process an invoice image and extract structured data
 */
async function processInvoice(imagePath: string): Promise<any> {
  console.log(`Processing invoice: ${imagePath}`);

  // Step 1: Upload image directly to ImgGo
  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  const uploadResponse = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${INVOICE_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `invoice-${path.basename(imagePath, path.extname(imagePath))}-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  const jobId = uploadResponse.data.data.job_id;
  console.log(`Job submitted: ${jobId}`);

  // Step 2: Poll for results
  const result = await pollForResult(jobId);

  return result;
}

/**
 * Poll ImgGo API until job completes
 */
async function pollForResult(
  jobId: string,
  maxAttempts: number = 30,
  waitSeconds: number = 2
): Promise<any> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const response = await axios.get<JobStatusResponse>(
      `${IMGGO_BASE_URL}/jobs/${jobId}`,
      {
        headers: {
          'Authorization': `Bearer ${IMGGO_API_KEY}`,
        },
      }
    );

    const { status, manifest, result } = response.data.data;

    if (status === 'completed' || status === 'succeeded') {
      console.log('✓ Processing complete!');
      return manifest || result;
    } else if (status === 'failed') {
      const error = response.data.data.error || 'Unknown error';
      throw new Error(`Job failed: ${error}`);
    }

    console.log(`Status: ${status}, waiting... (${attempt + 1}/${maxAttempts})`);
    await new Promise(resolve => setTimeout(resolve, waitSeconds * 1000));
  }

  throw new Error(`Job timeout after ${maxAttempts * waitSeconds} seconds`);
}

/**
 * Main execution
 */
async function main() {
  // Get path to test invoice
  const testInvoice = path.join(__dirname, '..', '..', '..', 'test-images', 'invoice1.jpg');

  if (!fs.existsSync(testInvoice)) {
    console.error(`Error: Test invoice not found at ${testInvoice}`);
    console.error('Please ensure test-images/invoice1.jpg exists');
    process.exit(1);
  }

  try {
    // Process the invoice
    const invoiceData = await processInvoice(testInvoice);

    // Display results
    console.log('\n' + '='.repeat(50));
    console.log('EXTRACTED INVOICE DATA');
    console.log('='.repeat(50));

    // Parse if result is string
    let parsedData = invoiceData;
    if (typeof invoiceData === 'string') {
      parsedData = JSON.parse(invoiceData);
    }

    console.log(JSON.stringify(parsedData, null, 2));

    // Save to file
    const outputFile = 'invoice_output.json';
    fs.writeFileSync(outputFile, JSON.stringify(parsedData, null, 2));

    console.log(`\n✓ Results saved to ${outputFile}`);

  } catch (error) {
    console.error(`\n✗ Error processing invoice:`, error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export { processInvoice, pollForResult };
