/**
 * Field Service - TypeScript Integration Example
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const FIELD_SERVICE_PATTERN_ID = process.env.FIELD_SERVICE_PATTERN_ID || 'pat_field_service_json';

interface ServiceData {
  work_order_id?: string;
  technician_name: string;
  customer_name: string;
  service_location: string;
  equipment_type: string;
  reported_issue: string;
  diagnosis?: string;
  actions_taken?: string[];
  parts_used?: Array<{ name: string; quantity: number; price: number }>;
  labor_hours?: number;
  completed?: boolean;
}

async function uploadServicePhoto(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) throw new Error('IMGGO_API_KEY not set');

  const formData = new FormData();
  formData.append('file', fs.createReadStream(imagePath));

  const response = await axios.post(
    `${IMGGO_BASE_URL}/patterns/${FIELD_SERVICE_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `field-service-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}

async function waitForResult(jobId: string): Promise<ServiceData> {
  for (let attempt = 1; attempt <= 60; attempt++) {
    const response = await axios.get(
      `${IMGGO_BASE_URL}/jobs/${jobId}`,
      { headers: { 'Authorization': `Bearer ${IMGGO_API_KEY}` } }
    );

    const { status, result, error } = response.data.data;

    if (status === 'completed') {
      if (!result) throw new Error('No result');
      return result;
    }

    if (status === 'failed') throw new Error(`Job failed: ${error}`);

    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error('Timeout');
}

async function main() {
  console.log('FIELD SERVICE - TYPESCRIPT EXAMPLE');

  if (!IMGGO_API_KEY) {
    console.error('✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/field-service1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error('⚠ Test image not found');
    process.exit(1);
  }

  try {
    const jobId = await uploadServicePhoto(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const serviceData = await waitForResult(jobId);
    console.log('✓ Processing completed');

    fs.writeFileSync('service_data.json', JSON.stringify(serviceData, null, 2));
    console.log('✓ Saved service data');

    console.log(`\nWork Order: ${serviceData.work_order_id || 'Generated'}`);
    console.log(`Technician: ${serviceData.technician_name}`);
    console.log(`Customer: ${serviceData.customer_name}`);

    console.log('\n✓ Field service processing completed!');

  } catch (error) {
    console.error(`✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
