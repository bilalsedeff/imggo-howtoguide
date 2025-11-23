import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const FOOD_SAFETY_PATTERN_ID = process.env.FOOD_SAFETY_PATTERN_ID || 'pat_food_safety_csv';

async function uploadInspectionPhoto(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) throw new Error('IMGGO_API_KEY not set');

  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  const response = await axios.post(
    `${IMGGO_BASE_URL}/patterns/${FOOD_SAFETY_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `food-safety-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}

async function waitForResult(jobId: string): Promise<string> {
  for (let attempt = 1; attempt <= 60; attempt++) {
    const response = await axios.get(
      `${IMGGO_BASE_URL}/jobs/${jobId}`,
      { headers: { 'Authorization': `Bearer ${IMGGO_API_KEY}` } }
    );

    const { status, result, error } = response.data.data;

    if (status === 'completed') return result;
    if (status === 'failed') throw new Error(`Job failed: ${error}`);

    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error('Timeout');
}

async function main() {
  console.log('FOOD SAFETY - TYPESCRIPT EXAMPLE');

  if (!IMGGO_API_KEY) {
    console.error('✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/food-safety1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error('⚠ Test image not found');
    process.exit(1);
  }

  try {
    const jobId = await uploadInspectionPhoto(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const csvResult = await waitForResult(jobId);
    console.log('✓ Processing completed');

    fs.writeFileSync('inspection_violations.csv', csvResult);
    console.log('✓ Saved CSV');

    console.log('\n✓ Food safety inspection completed!');

  } catch (error) {
    console.error(`✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
