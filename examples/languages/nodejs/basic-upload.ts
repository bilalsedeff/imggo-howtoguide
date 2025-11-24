/**
 * Basic Image Upload Example
 *
 * This example shows how to upload an image directly to ImgGo API
 * and get the extracted data back.
 *
 * Usage:
 *   npx ts-node basic-upload.ts path/to/image.jpg PATTERN_ID
 */

import axios from 'axios';
const FormData = require('form-data');
import * as fs from 'fs';

// Configuration
const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';

interface JobResponse {
  data: {
    job_id: string;
    status: string;
  };
}

interface JobResult {
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'succeeded' | 'failed';
    manifest?: any;
    result?: any;
    error?: string;
  };
}

/**
 * Upload an image and process it with a pattern
 */
async function uploadImage(
  imagePath: string,
  patternId: string
): Promise<any> {
  if (!IMGGO_API_KEY) {
    throw new Error('IMGGO_API_KEY environment variable not set');
  }

  console.log(`Uploading: ${imagePath}`);

  // Step 1: Upload and start processing
  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${patternId}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        ...formData.getHeaders(),
      },
    }
  );

  const jobId = response.data.data.job_id;
  console.log(`Job created: ${jobId}`);

  // Step 2: Poll for results
  console.log('Waiting for processing...');
  const result = await pollJob(jobId);

  console.log('Processing completed!');
  return result;
}

/**
 * Poll a job until it completes
 */
async function pollJob(
  jobId: string,
  maxAttempts: number = 60,
  interval: number = 2000
): Promise<any> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const response = await axios.get<JobResult>(
      `${IMGGO_BASE_URL}/jobs/${jobId}`,
      {
        headers: {
          'Authorization': `Bearer ${IMGGO_API_KEY}`,
        },
      }
    );

    const data = response.data.data;
    const status = data.status;

    console.log(`  Attempt ${attempt + 1}/${maxAttempts}: ${status}`);

    if (status === 'succeeded') {
      // Extract the result
      return data.manifest || data.result;
    }

    if (status === 'failed') {
      throw new Error(`Job failed: ${data.error || 'Unknown error'}`);
    }

    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, interval));
  }

  throw new Error(`Job timeout after ${maxAttempts * interval / 1000} seconds`);
}

/**
 * Main entry point
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.log('Usage: npx ts-node basic-upload.ts <image_path> <pattern_id>');
    console.log('\nExample:');
    console.log('  npx ts-node basic-upload.ts invoice.jpg pat_abc123');
    process.exit(1);
  }

  const [imagePath, patternId] = args;

  if (!fs.existsSync(imagePath)) {
    console.error(`Error: Image file not found: ${imagePath}`);
    process.exit(1);
  }

  try {
    const result = await uploadImage(imagePath, patternId);

    console.log('\n' + '='.repeat(60));
    console.log('EXTRACTED DATA');
    console.log('='.repeat(60));
    console.log(JSON.stringify(result, null, 2));
    console.log();

  } catch (error) {
    if (error instanceof Error) {
      console.error(`\nError: ${error.message}`);
    } else {
      console.error(`\nError: ${error}`);
    }
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

export { uploadImage, pollJob };
