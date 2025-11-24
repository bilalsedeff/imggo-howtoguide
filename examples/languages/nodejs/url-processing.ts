/**
 * URL Processing Example
 *
 * Process images from public URLs (S3, CDN, cloud storage, etc.)
 *
 * Usage:
 *   npx ts-node url-processing.ts https://example.com/image.jpg PATTERN_ID
 */

import axios from 'axios';

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';

interface JobResponse {
  data: {
    job_id: string;
  };
}

interface JobResult {
  data: {
    status: string;
    manifest?: any;
    result?: any;
    error?: string;
  };
}

async function processImageUrl(imageUrl: string, patternId: string): Promise<any> {
  if (!IMGGO_API_KEY) {
    throw new Error('IMGGO_API_KEY environment variable not set');
  }

  console.log(`Processing URL: ${imageUrl}`);

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${patternId}/ingest`,
    { image_url: imageUrl },
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Content-Type': 'application/json',
      },
    }
  );

  const jobId = response.data.data.job_id;
  console.log(`Job created: ${jobId}`);

  console.log('Waiting for processing...');
  return await pollJob(jobId);
}

async function pollJob(jobId: string, maxAttempts: number = 60): Promise<any> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const response = await axios.get<JobResult>(
      `${IMGGO_BASE_URL}/jobs/${jobId}`,
      { headers: { 'Authorization': `Bearer ${IMGGO_API_KEY}` } }
    );

    const { status, manifest, result, error } = response.data.data;
    console.log(`  Attempt ${attempt + 1}/${maxAttempts}: ${status}`);

    if (status === 'succeeded') {
      return manifest || result;
    }

    if (status === 'failed') {
      throw new Error(`Job failed: ${error}`);
    }

    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error('Job timeout');
}

async function main() {
  const [imageUrl, patternId] = process.argv.slice(2);

  if (!imageUrl || !patternId) {
    console.log('Usage: npx ts-node url-processing.ts <image_url> <pattern_id>');
    process.exit(1);
  }

  if (!imageUrl.startsWith('http://') && !imageUrl.startsWith('https://')) {
    console.error('Error: Image URL must start with http:// or https://');
    process.exit(1);
  }

  try {
    const result = await processImageUrl(imageUrl, patternId);
    console.log('\n' + '='.repeat(60));
    console.log('EXTRACTED DATA');
    console.log('='.repeat(60));
    console.log(JSON.stringify(result, null, 2));
  } catch (error: any) {
    console.error(`\nError: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { processImageUrl };
