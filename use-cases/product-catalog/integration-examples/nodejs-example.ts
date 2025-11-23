/**
 * Product Catalog - TypeScript Integration Example
 * Extract product information and sync with e-commerce platforms
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const PRODUCT_CATALOG_PATTERN_ID = process.env.PRODUCT_CATALOG_PATTERN_ID || 'pat_product_catalog_json';

interface JobResponse {
  success: boolean;
  data: { job_id: string; status: string };
}

interface JobResult {
  success: boolean;
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    result?: Product;
    error?: string;
  };
}

interface Product {
  name: string;
  brand?: string;
  sku?: string;
  price: number;
  compare_at_price?: number;
  sale_price?: number;
  description?: string;
  short_description?: string;
  category?: string;
  tags?: string[];
  stock_quantity?: number;
  image_url?: string;
  weight?: number;
  weight_unit?: string;
  gtin?: string;
}

interface EnrichedProduct extends Product {
  discount_percentage?: number;
  inventory_status?: string;
}

async function uploadProductImage(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) throw new Error('IMGGO_API_KEY not set');

  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  console.log(`\nUploading product image: ${path.basename(imagePath)}`);

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${PRODUCT_CATALOG_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `product-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}

async function waitForResult(jobId: string, maxAttempts: number = 60): Promise<Product> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const response = await axios.get<JobResult>(
      `${IMGGO_BASE_URL}/jobs/${jobId}`,
      { headers: { 'Authorization': `Bearer ${IMGGO_API_KEY}` } }
    );

    const { status, result, error } = response.data.data;

    if (status === 'completed') {
      if (!result) throw new Error('No result in completed job');
      return result;
    }

    if (status === 'failed') {
      throw new Error(`Job failed: ${error || 'Unknown error'}`);
    }

    console.log(`Attempt ${attempt}/${maxAttempts}: Status = ${status}`);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error('Timeout waiting for job completion');
}

function enrichProductData(product: Product): EnrichedProduct {
  const enriched: EnrichedProduct = { ...product };

  // Generate SKU if missing
  if (!enriched.sku) {
    const brand = (enriched.brand || 'UNK').substring(0, 3).toUpperCase();
    const name = (enriched.name || 'PRODUCT').substring(0, 3).toUpperCase();
    enriched.sku = `${brand}${name}${Date.now()}`;
  }

  // Calculate discounts
  if (enriched.price && enriched.compare_at_price && enriched.compare_at_price > enriched.price) {
    const discount = ((enriched.compare_at_price - enriched.price) / enriched.compare_at_price) * 100;
    enriched.discount_percentage = Math.round(discount * 10) / 10;
  }

  // Set inventory status
  const stock = enriched.stock_quantity || 0;
  if (stock === 0) {
    enriched.inventory_status = 'OUT_OF_STOCK';
  } else if (stock < 10) {
    enriched.inventory_status = 'LOW_STOCK';
  } else {
    enriched.inventory_status = 'IN_STOCK';
  }

  return enriched;
}

async function syncToShopify(product: EnrichedProduct): Promise<object> {
  console.log('\n' + '='.repeat(60));
  console.log('SYNCING TO SHOPIFY');
  console.log('='.repeat(60));

  const shopifyProduct = {
    product: {
      title: product.name,
      body_html: product.description || '',
      vendor: product.brand,
      product_type: product.category,
      tags: product.tags || [],
      variants: [{
        price: product.price,
        compare_at_price: product.compare_at_price,
        sku: product.sku,
        inventory_quantity: product.stock_quantity || 0,
        weight: product.weight,
        weight_unit: product.weight_unit || 'kg',
      }],
      images: product.image_url ? [{ src: product.image_url }] : [],
    },
  };

  console.log(`Product: ${product.name}`);
  console.log(`SKU: ${product.sku}`);
  console.log(`Price: $${product.price}`);

  // In production: await axios.post('https://your-store.myshopify.com/admin/api/2024-01/products.json', ...)

  console.log('\n✓ Product synced to Shopify (simulated)');
  return shopifyProduct;
}

async function syncToWooCommerce(product: EnrichedProduct): Promise<object> {
  console.log('\n' + '='.repeat(60));
  console.log('SYNCING TO WOOCOMMERCE');
  console.log('='.repeat(60));

  const wooProduct = {
    name: product.name,
    type: 'simple',
    regular_price: String(product.price || 0),
    sale_price: String(product.sale_price || ''),
    description: product.description || '',
    short_description: product.short_description || '',
    sku: product.sku,
    manage_stock: true,
    stock_quantity: product.stock_quantity || 0,
    categories: product.category ? [{ name: product.category }] : [],
    tags: (product.tags || []).map(tag => ({ name: tag })),
    images: product.image_url ? [{ src: product.image_url }] : [],
  };

  console.log(`Product: ${product.name}`);
  console.log(`Regular Price: $${product.price}`);

  // In production: await axios.post('https://your-site.com/wp-json/wc/v3/products', ...)

  console.log('\n✓ Product synced to WooCommerce (simulated)');
  return wooProduct;
}

async function main() {
  console.log('='.repeat(60));
  console.log('PRODUCT CATALOG - TYPESCRIPT EXAMPLE');
  console.log('='.repeat(60));

  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/product1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n⚠ Test image not found: ${testImage}`);
    process.exit(1);
  }

  try {
    const jobId = await uploadProductImage(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const product = await waitForResult(jobId);
    console.log('✓ Processing completed');

    // Save raw JSON
    const outputFile = 'product_data.json';
    fs.writeFileSync(outputFile, JSON.stringify(product, null, 2));
    console.log(`\n✓ Saved product data to ${outputFile}`);

    // Enrich data
    const enrichedProduct = enrichProductData(product);

    console.log('\n' + '='.repeat(60));
    console.log('PRODUCT DETAILS');
    console.log('='.repeat(60));
    console.log(`Name: ${enrichedProduct.name}`);
    console.log(`Brand: ${enrichedProduct.brand}`);
    console.log(`SKU: ${enrichedProduct.sku}`);
    console.log(`Price: $${enrichedProduct.price}`);
    console.log(`Stock: ${enrichedProduct.stock_quantity} (${enrichedProduct.inventory_status})`);

    if (enrichedProduct.discount_percentage) {
      console.log(`Discount: ${enrichedProduct.discount_percentage}%`);
    }

    // Sync to platforms
    await syncToShopify(enrichedProduct);
    await syncToWooCommerce(enrichedProduct);

    console.log('\n✓ Product catalog sync completed!');

  } catch (error) {
    console.error(`\n✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
