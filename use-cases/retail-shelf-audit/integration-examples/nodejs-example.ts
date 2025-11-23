/**
 * Retail Shelf Audit - Node.js/TypeScript Example
 * Process shelf photos and extract product analytics
 */

import axios, { AxiosError } from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Configuration
const IMGGO_BASE_URL = 'https://img-go.com/api';
const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const SHELF_AUDIT_PATTERN_ID = process.env.SHELF_AUDIT_PATTERN_ID || 'pat_shelf_audit';

// TypeScript interfaces
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
    result?: ShelfAnalytics;
    error?: string;
  };
}

interface Product {
  name: string;
  brand: string;
  facing_count: number;
  price_visible: boolean;
  position?: {
    shelf: number;
    column: number;
  };
}

interface BrandShare {
  [brand: string]: number;
}

interface PlanogramCompliance {
  score: number;
  issues: string[];
}

interface ShelfAnalytics {
  total_facings: number;
  unique_skus: number;
  out_of_stock_count: number;
  brand_share: BrandShare;
  products: Product[];
  planogram_compliance?: PlanogramCompliance;
}

/**
 * Sleep helper
 */
const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Process shelf image and get analytics
 */
async function processShelfAudit(imageUrl: string): Promise<ShelfAnalytics> {
  console.log(`\nProcessing shelf image: ${imageUrl}`);

  const idempotencyKey = `shelf-audit-${Date.now()}`;

  try {
    // Step 1: Submit image for processing
    const uploadResponse = await axios.post<JobResponse>(
      `${IMGGO_BASE_URL}/patterns/${SHELF_AUDIT_PATTERN_ID}/ingest`,
      { image_url: imageUrl },
      {
        headers: {
          'Authorization': `Bearer ${IMGGO_API_KEY}`,
          'Content-Type': 'application/json',
          'Idempotency-Key': idempotencyKey,
        },
      }
    );

    const jobId = uploadResponse.data.data.job_id;
    console.log(`✓ Job submitted! Job ID: ${jobId}`);

    // Step 2: Poll for results
    return await waitForResult(jobId);

  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      console.error('Processing failed:', axiosError.response?.data || axiosError.message);
    } else {
      console.error('Processing failed:', error);
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
): Promise<ShelfAnalytics> {
  console.log('\nWaiting for shelf audit results...');

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

      const { status, result, error } = response.data.data;

      if (status === 'completed') {
        if (!result) {
          throw new Error('Job completed but no result returned');
        }
        console.log('✓ Shelf audit completed!');
        return result;
      }

      if (status === 'failed') {
        throw new Error(`Job failed: ${error || 'Unknown error'}`);
      }

      // Still processing
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
 * Display shelf analytics
 */
function displayAnalytics(analytics: ShelfAnalytics): void {
  console.log('\n========================================');
  console.log('SHELF AUDIT ANALYTICS');
  console.log('========================================');

  // Overall metrics
  console.log(`\nTotal Products: ${analytics.total_facings}`);
  console.log(`Unique SKUs: ${analytics.products.length}`);
  console.log(`Out of Stock Items: ${analytics.out_of_stock_count}`);

  // Brand share
  if (analytics.brand_share) {
    console.log('\nBrand Share:');
    Object.entries(analytics.brand_share).forEach(([brand, percentage]) => {
      console.log(`  ${brand}: ${percentage.toFixed(1)}%`);
    });
  }

  // Products detail
  if (analytics.products && analytics.products.length > 0) {
    console.log(`\nProducts Detected (${analytics.products.length} items):`);

    // Show first 5 products
    analytics.products.slice(0, 5).forEach((product, index) => {
      console.log(`\n  ${index + 1}. ${product.name}`);
      console.log(`     Brand: ${product.brand}`);
      console.log(`     Facings: ${product.facing_count}`);
      console.log(`     Price Visible: ${product.price_visible ? 'Yes' : 'No'}`);
    });

    if (analytics.products.length > 5) {
      console.log(`\n  ... and ${analytics.products.length - 5} more products`);
    }
  }

  // Planogram compliance
  if (analytics.planogram_compliance) {
    console.log(`\nPlanogram Compliance: ${analytics.planogram_compliance.score.toFixed(1)}%`);
    if (analytics.planogram_compliance.issues.length > 0) {
      console.log(`  Issues: ${analytics.planogram_compliance.issues.join(', ')}`);
    }
  }
}

/**
 * Save results to file
 */
function saveResult(analytics: ShelfAnalytics, outputFile: string): void {
  fs.writeFileSync(
    outputFile,
    JSON.stringify(analytics, null, 2),
    'utf-8'
  );
  console.log(`\n✓ Results saved to ${outputFile}`);
}

/**
 * Save to database (example using PostgreSQL)
 */
async function saveToDatabase(
  analytics: ShelfAnalytics,
  storeId: string,
  location: string
): Promise<void> {
  // This is a placeholder - replace with your actual database logic
  // Example using pg package:
  /*
  const { Pool } = require('pg');

  const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'retail_analytics',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD,
  });

  await pool.query(`
    INSERT INTO shelf_audits (
      store_id,
      location,
      total_facings,
      unique_skus,
      out_of_stock_count,
      planogram_compliance_score,
      audit_data,
      audit_date
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
  `, [
    storeId,
    location,
    analytics.total_facings,
    analytics.products.length,
    analytics.out_of_stock_count,
    analytics.planogram_compliance?.score || 0,
    JSON.stringify(analytics),
  ]);

  await pool.end();
  */

  console.log(`\n✓ Would save to database: Store ${storeId}, Location ${location}`);
}

/**
 * Main function
 */
async function main(): Promise<void> {
  console.log('========================================');
  console.log('Retail Shelf Audit - Node.js Example');
  console.log('========================================');

  // Check API key
  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY environment variable not set');
    console.error('  Set it in .env file or export IMGGO_API_KEY=your_key');
    process.exit(1);
  }

  // Example shelf image URL
  // In production, this would come from your store cameras or mobile app
  const imageUrl = 'https://example.com/shelf-photos/store-123-aisle-5.jpg';

  try {
    // Process shelf photo
    const analytics = await processShelfAudit(imageUrl);

    // Display results
    displayAnalytics(analytics);

    // Save to file
    const outputFile = 'shelf_audit_result.json';
    saveResult(analytics, outputFile);

    // Optional: Save to database
    // await saveToDatabase(analytics, 'STORE-123', 'Aisle 5');

    console.log('\n✓ Shelf audit completed successfully!');

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
  processShelfAudit,
  displayAnalytics,
  saveResult,
  saveToDatabase,
};
