/**
 * Error Handling Example
 *
 * Production-ready error handling with:
 * - Automatic retry with exponential backoff
 * - Rate limit handling (429)
 * - Timeout management
 * - Idempotency keys
 * - Custom exceptions
 * - Result validation
 *
 * Usage:
 *   npx ts-node error-handling.ts path/to/image.jpg PATTERN_ID
 */

import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import FormData from 'form-data';
import fs from 'fs';

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';

// Custom exceptions
class ImgGoAPIError extends Error {
  constructor(message: string, public statusCode?: number, public response?: any) {
    super(message);
    this.name = 'ImgGoAPIError';
  }
}

class RateLimitError extends ImgGoAPIError {
  constructor(message: string, public retryAfter: number) {
    super(message, 429);
    this.name = 'RateLimitError';
  }
}

class ValidationError extends ImgGoAPIError {
  constructor(message: string) {
    super(message, 400);
    this.name = 'ValidationError';
  }
}

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

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function uploadImageWithRetry(
  imagePath: string,
  patternId: string,
  maxRetries: number = 3
): Promise<string> {
  if (!IMGGO_API_KEY) {
    throw new ValidationError('IMGGO_API_KEY environment variable not set');
  }

  if (!fs.existsSync(imagePath)) {
    throw new ValidationError(`Image file not found: ${imagePath}`);
  }

  // Generate idempotency key to prevent duplicate uploads
  const idempotencyKey = `upload-${imagePath}-${patternId}-${Date.now()}`;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      console.log(`Upload attempt ${attempt + 1}/${maxRetries}...`);

      const formData = new FormData();
      formData.append('image', fs.createReadStream(imagePath));

      const config: AxiosRequestConfig = {
        headers: {
          'Authorization': `Bearer ${IMGGO_API_KEY}`,
          'Idempotency-Key': idempotencyKey,
          ...formData.getHeaders(),
        },
        timeout: 30000, // 30 second timeout
      };

      const response = await axios.post<JobResponse>(
        `${IMGGO_BASE_URL}/patterns/${patternId}/ingest`,
        formData,
        config
      );

      const jobId = response.data.data.job_id;
      console.log(`Job created: ${jobId}`);
      return jobId;

    } catch (error) {
      const axiosError = error as AxiosError;

      // Handle rate limiting (429)
      if (axiosError.response?.status === 429) {
        const retryAfter = parseInt(axiosError.response.headers['retry-after'] || '60');
        console.log(`Rate limited. Waiting ${retryAfter} seconds...`);

        if (attempt < maxRetries - 1) {
          await sleep(retryAfter * 1000);
          continue;
        }
        throw new RateLimitError(`Rate limit exceeded after ${maxRetries} attempts`, retryAfter);
      }

      // Handle 4xx client errors (don't retry)
      if (axiosError.response?.status && axiosError.response.status >= 400 && axiosError.response.status < 500) {
        const errorMessage = (axiosError.response.data as any)?.error || axiosError.message;
        throw new ValidationError(`Client error (${axiosError.response.status}): ${errorMessage}`);
      }

      // Handle 5xx server errors (retry with exponential backoff)
      if (axiosError.response?.status && axiosError.response.status >= 500) {
        console.error(`Server error (${axiosError.response.status}). Retrying...`);

        if (attempt < maxRetries - 1) {
          const waitTime = Math.pow(2, attempt) * 1000; // Exponential backoff
          console.log(`Waiting ${waitTime / 1000} seconds before retry...`);
          await sleep(waitTime);
          continue;
        }
        throw new ImgGoAPIError(
          `Server error after ${maxRetries} attempts`,
          axiosError.response.status,
          axiosError.response.data
        );
      }

      // Handle connection errors (retry with backoff)
      if (axiosError.code === 'ECONNABORTED' || axiosError.code === 'ETIMEDOUT') {
        console.error('Connection timeout. Retrying...');

        if (attempt < maxRetries - 1) {
          const waitTime = Math.pow(2, attempt) * 1000;
          await sleep(waitTime);
          continue;
        }
        throw new ImgGoAPIError(`Connection timeout after ${maxRetries} attempts`);
      }

      // Unknown error
      if (attempt === maxRetries - 1) {
        throw new ImgGoAPIError(`Upload failed: ${axiosError.message}`);
      }

      // Retry for unknown errors
      const waitTime = Math.pow(2, attempt) * 1000;
      console.log(`Unknown error. Waiting ${waitTime / 1000} seconds before retry...`);
      await sleep(waitTime);
    }
  }

  throw new ImgGoAPIError('Upload failed after all retries');
}

async function pollJobWithRetry(
  jobId: string,
  maxAttempts: number = 60,
  pollInterval: number = 2000
): Promise<any> {
  console.log('Waiting for processing...');

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const response = await axios.get<JobResult>(
        `${IMGGO_BASE_URL}/jobs/${jobId}`,
        {
          headers: { 'Authorization': `Bearer ${IMGGO_API_KEY}` },
          timeout: 10000, // 10 second timeout
        }
      );

      const { status, manifest, result, error } = response.data.data;
      console.log(`  Attempt ${attempt + 1}/${maxAttempts}: ${status}`);

      if (status === 'succeeded') {
        const extractedData = manifest || result;

        // Validate result
        if (!extractedData) {
          throw new ValidationError('Job succeeded but no data returned');
        }

        return extractedData;
      }

      if (status === 'failed') {
        throw new ImgGoAPIError(`Job failed: ${error}`);
      }

      await sleep(pollInterval);

    } catch (error) {
      const axiosError = error as AxiosError;

      // Re-throw custom errors
      if (error instanceof ImgGoAPIError) {
        throw error;
      }

      // Handle timeout during polling (retry without counting against maxAttempts)
      if (axiosError.code === 'ECONNABORTED' || axiosError.code === 'ETIMEDOUT') {
        console.log('  Polling timeout, retrying...');
        await sleep(pollInterval);
        continue;
      }

      // For other errors during polling, log and retry
      console.error(`  Polling error: ${axiosError.message}`);
      await sleep(pollInterval);
    }
  }

  throw new ImgGoAPIError(`Job timeout after ${maxAttempts * pollInterval / 1000} seconds`);
}

async function processImageWithRetry(imagePath: string, patternId: string): Promise<any> {
  const jobId = await uploadImageWithRetry(imagePath, patternId);
  return await pollJobWithRetry(jobId);
}

async function main() {
  const [imagePath, patternId] = process.argv.slice(2);

  if (!imagePath || !patternId) {
    console.log('Usage: npx ts-node error-handling.ts <image_path> <pattern_id>');
    process.exit(1);
  }

  try {
    const result = await processImageWithRetry(imagePath, patternId);
    console.log('\n' + '='.repeat(60));
    console.log('EXTRACTED DATA');
    console.log('='.repeat(60));
    console.log(JSON.stringify(result, null, 2));
  } catch (error: any) {
    console.error(`\nError: ${error.message}`);

    if (error instanceof RateLimitError) {
      console.error(`Please wait ${error.retryAfter} seconds before retrying.`);
    }

    if (error.statusCode) {
      console.error(`Status Code: ${error.statusCode}`);
    }

    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { processImageWithRetry, uploadImageWithRetry, pollJobWithRetry };
