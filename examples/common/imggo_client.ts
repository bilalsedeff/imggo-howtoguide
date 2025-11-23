/**
 * Reusable ImgGo API Client for TypeScript/Node.js
 * Production-ready client with error handling, retry logic, and webhooks
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';

interface ImgGoConfig {
  apiKey?: string;
  baseUrl?: string;
  timeout?: number;
  maxRetries?: number;
}

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
    manifest?: any;
    result?: any;
    error?: string;
  };
}

export class ImgGoClient {
  private apiKey: string;
  private baseUrl: string;
  private timeout: number;
  private maxRetries: number;
  private axiosInstance: AxiosInstance;

  constructor(config: ImgGoConfig = {}) {
    this.apiKey = config.apiKey || process.env.IMGGO_API_KEY || '';

    if (!this.apiKey) {
      throw new Error('API key required. Set IMGGO_API_KEY env var or pass apiKey parameter');
    }

    this.baseUrl = (config.baseUrl || 'https://img-go.com/api').replace(/\/$/, '');
    this.timeout = config.timeout || 30000;
    this.maxRetries = config.maxRetries || 3;

    this.axiosInstance = axios.create({
      baseURL: this.baseUrl,
      timeout: this.timeout,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
      },
    });
  }

  /**
   * Process an image file with ImgGo
   */
  async processImage(
    imagePath: string,
    patternId: string,
    options: {
      idempotencyKey?: string;
      poll?: boolean;
      webhookUrl?: string;
    } = {}
  ): Promise<any> {
    const { idempotencyKey, poll = true, webhookUrl } = options;

    // Generate idempotency key if not provided
    const key = idempotencyKey || `${path.basename(imagePath, path.extname(imagePath))}-${Date.now()}`;

    // Upload image
    const formData = new FormData();
    formData.append('image', fs.createReadStream(imagePath));  // CRITICAL: Use 'image' not 'file'

    if (webhookUrl) {
      formData.append('webhook_url', webhookUrl);
    }

    const response = await this.makeRequest<JobResponse>('POST', `/patterns/${patternId}/ingest`, {
      data: formData,
      headers: {
        'Idempotency-Key': key,
        ...formData.getHeaders(),
      },
    });

    const jobId = response.data.job_id;

    // Return immediately if not polling
    if (!poll) {
      return response.data;
    }

    // Poll for results
    return this.waitForJob(jobId);
  }

  /**
   * Process an image from URL with ImgGo
   */
  async processImageUrl(
    imageUrl: string,
    patternId: string,
    options: {
      idempotencyKey?: string;
      poll?: boolean;
      webhookUrl?: string;
    } = {}
  ): Promise<any> {
    const { idempotencyKey, poll = true, webhookUrl } = options;

    const key = idempotencyKey || `url-${this.hashString(imageUrl)}-${Date.now()}`;

    const payload: any = { image_url: imageUrl };
    if (webhookUrl) {
      payload.webhook_url = webhookUrl;
    }

    const response = await this.makeRequest<JobResponse>('POST', `/patterns/${patternId}/ingest`, {
      data: payload,
      headers: {
        'Idempotency-Key': key,
      },
    });

    const jobId = response.data.job_id;

    if (!poll) {
      return response.data;
    }

    return this.waitForJob(jobId);
  }

  /**
   * Get status of a processing job
   */
  async getJobStatus(jobId: string): Promise<any> {
    const response = await this.makeRequest<JobStatusResponse>('GET', `/jobs/${jobId}`);
    return response.data;
  }

  /**
   * Poll job until completion
   */
  async waitForJob(
    jobId: string,
    options: {
      maxAttempts?: number;
      waitSeconds?: number;
      progressCallback?: (status: string, attempt: number) => void;
    } = {}
  ): Promise<any> {
    const { maxAttempts = 60, waitSeconds = 2, progressCallback } = options;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      const jobStatus = await this.getJobStatus(jobId);
      const status = jobStatus.status;

      if (progressCallback) {
        progressCallback(status, attempt);
      }

      // CRITICAL: API returns "succeeded" not "completed"
      if (status === 'completed' || status === 'succeeded') {
        // CRITICAL: API returns result in "manifest" field, not "result"
        return jobStatus.manifest || jobStatus.result;
      }

      if (status === 'failed') {
        const error = jobStatus.error || 'Unknown error';
        throw new Error(`Job ${jobId} failed: ${error}`);
      }

      await this.sleep(waitSeconds * 1000);
    }

    throw new Error(`Job ${jobId} did not complete within ${maxAttempts * waitSeconds} seconds`);
  }

  /**
   * Make HTTP request with retry logic
   */
  private async makeRequest<T>(
    method: string,
    endpoint: string,
    config: any = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const response = await this.axiosInstance.request({
          method,
          url: endpoint,
          ...config,
        });

        return response.data;

      } catch (error) {
        lastError = error as Error;
        const axiosError = error as AxiosError;

        // Don't retry client errors (4xx except 429)
        if (axiosError.response) {
          const status = axiosError.response.status;
          if (status >= 400 && status < 500 && status !== 429) {
            throw error;
          }
        }

        // Exponential backoff for retries
        if (attempt < this.maxRetries - 1) {
          const waitTime = Math.pow(2, attempt) * 500;
          await this.sleep(waitTime);
        }
      }
    }

    throw lastError;
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Simple string hash for idempotency keys
   */
  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash);
  }
}

// Example usage
async function main() {
  // Initialize client
  const client = new ImgGoClient();

  // Example 1: Process image file
  console.log('Processing image file...');
  const result = await client.processImage(
    '../../../test-images/invoice1.jpg',
    'pat_invoice_example'
  );
  console.log('Result:', result);

  // Example 2: Process image from URL (no polling)
  console.log('\nProcessing image from URL...');
  const jobInfo = await client.processImageUrl(
    'https://example.com/image.jpg',
    'pat_example',
    { poll: false }
  );
  console.log('Job ID:', jobInfo.job_id);

  // Later, check status
  const status = await client.getJobStatus(jobInfo.job_id);
  console.log('Status:', status.status);
}

// Only run if this file is executed directly
if (require.main === module) {
  main().catch(console.error);
}
