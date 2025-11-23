/**
 * VIN Extraction - TypeScript Integration Example
 * Extract vehicle identification data from images in XML format
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import { parseStringPromise } from 'xml2js';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const VIN_PATTERN_ID = process.env.VIN_PATTERN_ID || 'pat_vin_xml';

interface JobResponse {
  success: boolean;
  data: { job_id: string; status: string };
}

interface JobResult {
  success: boolean;
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    result?: string;
    error?: string;
  };
}

interface VINData {
  vin_number: string | null;
  make: string | null;
  model: string | null;
  year: string | null;
  color: string | null;
  license_plate: string | null;
  odometer: string | null;
}

interface DecodedVIN {
  valid: boolean;
  wmi?: string;
  vds?: string;
  vis?: string;
  country?: string;
  manufacturer?: string;
  model_year?: string;
  plant_code?: string;
  error?: string;
}

async function uploadVINImage(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) throw new Error('IMGGO_API_KEY not set');

  const formData = new FormData();
  formData.append('file', fs.createReadStream(imagePath));

  console.log(`\nUploading VIN image: ${path.basename(imagePath)}`);

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${VIN_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `vin-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}

async function waitForResult(jobId: string, maxAttempts: number = 60): Promise<string> {
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

async function parseVINXML(xmlString: string): Promise<VINData> {
  const parsed = await parseStringPromise(xmlString);
  const vehicle = parsed.Vehicle || {};

  return {
    vin_number: vehicle.VINNumber?.[0] || null,
    make: vehicle.Make?.[0] || null,
    model: vehicle.Model?.[0] || null,
    year: vehicle.Year?.[0] || null,
    color: vehicle.Color?.[0] || null,
    license_plate: vehicle.LicensePlate?.[0] || null,
    odometer: vehicle.Odometer?.[0] || null,
  };
}

function decodeVIN(vin: string): DecodedVIN {
  if (!vin || vin.length !== 17) {
    return { valid: false, error: 'Invalid VIN length' };
  }

  const countryMap: Record<string, string> = {
    '1': 'United States', '2': 'Canada', '3': 'Mexico',
    'J': 'Japan', 'K': 'South Korea', 'L': 'China',
    'S': 'United Kingdom', 'V': 'Spain', 'W': 'Germany',
    'Z': 'Italy'
  };

  const manufacturerMap: Record<string, string> = {
    '1FA': 'Ford', '1G1': 'Chevrolet', '1HG': 'Honda',
    '1N4': 'Nissan', '5YJ': 'Tesla', 'JHM': 'Honda',
    'JTD': 'Toyota', 'WBA': 'BMW', 'WDB': 'Mercedes-Benz'
  };

  const yearMap: Record<string, string> = {
    'A': '2010', 'B': '2011', 'C': '2012', 'D': '2013',
    'E': '2014', 'F': '2015', 'G': '2016', 'H': '2017',
    'J': '2018', 'K': '2019', 'L': '2020', 'M': '2021',
    'N': '2022', 'P': '2023', 'R': '2024', 'S': '2025'
  };

  const wmi = vin.substring(0, 3);

  return {
    valid: true,
    wmi,
    vds: vin.substring(3, 9),
    vis: vin.substring(9, 17),
    country: countryMap[vin[0]] || 'Unknown',
    manufacturer: manufacturerMap[wmi] || 'Unknown',
    model_year: yearMap[vin[9]] || 'Unknown',
    plant_code: vin[10],
  };
}

async function saveToFleetSystem(vinData: VINData, decoded: DecodedVIN): Promise<boolean> {
  console.log('\n' + '='.repeat(60));
  console.log('SAVING TO FLEET MANAGEMENT SYSTEM');
  console.log('='.repeat(60));

  const payload = {
    vehicle: {
      vin: vinData.vin_number,
      make: vinData.make || decoded.manufacturer,
      model: vinData.model,
      year: vinData.year || decoded.model_year,
      color: vinData.color,
      license_plate: vinData.license_plate,
      odometer: vinData.odometer,
      country_of_origin: decoded.country,
    },
  };

  console.log('Fleet System Payload:');
  console.log(JSON.stringify(payload, null, 2));

  // In production: await axios.post('https://fleet-api.example.com/vehicles', payload);

  console.log('\n✓ Vehicle saved to fleet system (simulated)');
  return true;
}

async function main() {
  console.log('='.repeat(60));
  console.log('VIN EXTRACTION - TYPESCRIPT EXAMPLE');
  console.log('='.repeat(60));

  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/vin1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n⚠ Test image not found: ${testImage}`);
    process.exit(1);
  }

  try {
    const jobId = await uploadVINImage(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const xmlResult = await waitForResult(jobId);
    console.log('✓ Processing completed');

    // Save raw XML
    const outputFile = 'vin_data.xml';
    fs.writeFileSync(outputFile, xmlResult);
    console.log(`\n✓ Saved XML to ${outputFile}`);

    // Parse XML
    const vinData = await parseVINXML(xmlResult);

    console.log('\n' + '='.repeat(60));
    console.log('EXTRACTED VIN DATA');
    console.log('='.repeat(60));
    Object.entries(vinData).forEach(([key, value]) => {
      console.log(`${key}: ${value}`);
    });

    // Decode VIN
    if (vinData.vin_number) {
      const decoded = decodeVIN(vinData.vin_number);

      console.log('\n' + '='.repeat(60));
      console.log('DECODED VIN INFORMATION');
      console.log('='.repeat(60));
      Object.entries(decoded).forEach(([key, value]) => {
        console.log(`${key}: ${value}`);
      });

      await saveToFleetSystem(vinData, decoded);
    }

    console.log('\n✓ VIN extraction completed!');

  } catch (error) {
    console.error(`\n✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
