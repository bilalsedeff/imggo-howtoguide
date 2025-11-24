/**
 * Async Batch Processing Example
 *
 * Process multiple images concurrently using Promise.all() for high-performance batch workflows.
 *
 * Usage:
 *   npx ts-node async-batch.ts PATTERN_ID image1.jpg image2.jpg image3.jpg ...
 *
 * Example:
 *   npx ts-node async-batch.ts pat_abc123 invoice*.jpg
 */

import axios, { AxiosError } from 'axios';
const FormData = require('form-data');
import * as fs from 'fs';
import * as path from 'path';

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const MAX_CONCURRENT = 10; // Maximum concurrent uploads

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

interface UploadResult {
  imagePath: string;
  jobId?: string;
  error?: string;
}

interface ProcessResult {
  imagePath: string;
  success: boolean;
  data?: any;
  error?: string;
}

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function uploadImage(imagePath: string, patternId: string): Promise<UploadResult> {
  try {
    if (!fs.existsSync(imagePath)) {
      return { imagePath, error: 'File not found' };
    }

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
        timeout: 30000,
      }
    );

    const jobId = response.data.data.job_id;
    console.log(`[UPLOAD] ${path.basename(imagePath)} -> ${jobId}`);
    return { imagePath, jobId };

  } catch (error) {
    const axiosError = error as AxiosError;
    const errorMessage = (axiosError.response?.data as any)?.error || axiosError.message;
    console.error(`[UPLOAD FAILED] ${path.basename(imagePath)}: ${errorMessage}`);
    return { imagePath, error: errorMessage };
  }
}

async function pollJob(
  jobId: string,
  imagePath: string,
  maxAttempts: number = 60
): Promise<ProcessResult> {
  try {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const response = await axios.get<JobResult>(
        `${IMGGO_BASE_URL}/jobs/${jobId}`,
        {
          headers: { 'Authorization': `Bearer ${IMGGO_API_KEY}` },
          timeout: 10000,
        }
      );

      const { status, manifest, result, error } = response.data.data;

      if (status === 'succeeded') {
        console.log(`[SUCCESS] ${path.basename(imagePath)}`);
        return {
          imagePath,
          success: true,
          data: manifest || result,
        };
      }

      if (status === 'failed') {
        console.error(`[FAILED] ${path.basename(imagePath)}: ${error}`);
        return {
          imagePath,
          success: false,
          error: error || 'Job failed',
        };
      }

      // Still processing
      if (attempt % 10 === 0) {
        console.log(`[POLLING] ${path.basename(imagePath)}: ${status} (${attempt + 1}/${maxAttempts})`);
      }

      await sleep(2000);
    }

    console.error(`[TIMEOUT] ${path.basename(imagePath)}`);
    return {
      imagePath,
      success: false,
      error: 'Job timeout',
    };

  } catch (error) {
    const axiosError = error as AxiosError;
    const errorMessage = axiosError.message;
    console.error(`[POLLING ERROR] ${path.basename(imagePath)}: ${errorMessage}`);
    return {
      imagePath,
      success: false,
      error: errorMessage,
    };
  }
}

async function processBatch(
  imagePaths: string[],
  patternId: string
): Promise<ProcessResult[]> {
  if (!IMGGO_API_KEY) {
    throw new Error('IMGGO_API_KEY environment variable not set');
  }

  console.log(`\nProcessing ${imagePaths.length} images with pattern ${patternId}...\n`);

  // Phase 1: Upload all images concurrently (in chunks)
  console.log('=== PHASE 1: UPLOADING ===\n');
  const uploadResults: UploadResult[] = [];

  for (let i = 0; i < imagePaths.length; i += MAX_CONCURRENT) {
    const chunk = imagePaths.slice(i, i + MAX_CONCURRENT);
    const chunkResults = await Promise.all(
      chunk.map(imagePath => uploadImage(imagePath, patternId))
    );
    uploadResults.push(...chunkResults);
  }

  // Separate successful uploads from failures
  const successfulUploads = uploadResults.filter(r => r.jobId);
  const failedUploads = uploadResults.filter(r => r.error);

  console.log(`\nUploaded: ${successfulUploads.length} succeeded, ${failedUploads.length} failed\n`);

  // Phase 2: Poll all jobs concurrently
  console.log('=== PHASE 2: PROCESSING ===\n');

  const pollPromises = successfulUploads.map(upload =>
    pollJob(upload.jobId!, upload.imagePath)
  );

  const processResults = await Promise.all(pollPromises);

  // Add failed uploads to results
  const allResults = [
    ...processResults,
    ...failedUploads.map(upload => ({
      imagePath: upload.imagePath,
      success: false,
      error: upload.error,
    })),
  ];

  return allResults;
}

async function main() {
  const [patternId, ...imagePaths] = process.argv.slice(2);

  if (!patternId || imagePaths.length === 0) {
    console.log('Usage: npx ts-node async-batch.ts <pattern_id> <image1> <image2> ...');
    console.log('\nExample:');
    console.log('  npx ts-node async-batch.ts pat_abc123 invoice1.jpg invoice2.jpg invoice3.jpg');
    process.exit(1);
  }

  try {
    const startTime = Date.now();
    const results = await processBatch(imagePaths, patternId);
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);

    // Save results to JSON file
    const outputFile = `batch-results-${Date.now()}.json`;
    fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));

    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('BATCH PROCESSING SUMMARY');
    console.log('='.repeat(60));

    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);

    console.log(`Total Images: ${results.length}`);
    console.log(`Succeeded: ${successful.length}`);
    console.log(`Failed: ${failed.length}`);
    console.log(`Duration: ${duration}s`);
    console.log(`Output File: ${outputFile}`);

    if (failed.length > 0) {
      console.log('\nFailed Images:');
      failed.forEach(result => {
        console.log(`  - ${path.basename(result.imagePath)}: ${result.error}`);
      });
    }

    console.log('\n' + '='.repeat(60));

  } catch (error: any) {
    console.error(`\nError: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { processBatch };
