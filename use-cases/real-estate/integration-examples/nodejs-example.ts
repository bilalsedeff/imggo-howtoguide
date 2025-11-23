/**
 * Real Estate Listing Automation - TypeScript Integration Example
 * Extract property data from photos and integrate with MLS systems
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const REAL_ESTATE_PATTERN_ID = process.env.REAL_ESTATE_PATTERN_ID || 'pat_real_estate_json';

interface JobResponse {
  success: boolean;
  data: {
    job_id: string;
    status: string;
  };
}

interface JobResult {
  success: boolean;
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    result?: PropertyData;
    error?: string;
  };
}

interface PropertyData {
  listing_id?: string;
  address: string;
  city?: string;
  state?: string;
  zip_code?: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  square_feet: number;
  lot_size?: number;
  year_built?: number;
  property_type?: string;
  property_subtype?: string;
  description?: string;
  features?: string[];
  photos?: string[];
}

interface EnrichedPropertyData extends PropertyData {
  price_per_sqft?: number;
  category?: string;
  estimated_monthly_payment?: number;
}

interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
}

interface MLSListing {
  ListingID?: string;
  StandardStatus: string;
  ListPrice: number;
  UnparsedAddress: string;
  City?: string;
  StateOrProvince?: string;
  PostalCode?: string;
  PropertyType?: string;
  PropertySubType?: string;
  BedroomsTotal: number;
  BathroomsTotalInteger: number;
  LivingArea: number;
  LotSizeSquareFeet?: number;
  YearBuilt?: number;
  PublicRemarks?: string;
  Media: Array<{
    MediaURL: string;
    Order: number;
    MediaCategory: string;
  }>;
  Features?: string[];
}

async function uploadPropertyPhoto(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) {
    throw new Error('IMGGO_API_KEY not set');
  }

  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  console.log(`\nUploading property photo: ${path.basename(imagePath)}`);

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${REAL_ESTATE_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `real-estate-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}

async function waitForResult(jobId: string, maxAttempts: number = 60): Promise<PropertyData> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const response = await axios.get<JobResult>(
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
        throw new Error('No result in completed job');
      }
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

function enrichPropertyData(propertyData: PropertyData): EnrichedPropertyData {
  const enriched: EnrichedPropertyData = { ...propertyData };

  // Calculate price per square foot
  if (propertyData.price && propertyData.square_feet && propertyData.square_feet > 0) {
    enriched.price_per_sqft = Math.round((propertyData.price / propertyData.square_feet) * 100) / 100;
  }

  // Determine property category
  if (propertyData.property_type) {
    const propType = propertyData.property_type.toLowerCase();
    if (propType.includes('condo') || propType.includes('apartment')) {
      enriched.category = 'Multi-Family';
    } else if (propType.includes('commercial')) {
      enriched.category = 'Commercial';
    } else if (propType.includes('land') || propType.includes('lot')) {
      enriched.category = 'Land';
    } else {
      enriched.category = 'Single-Family';
    }
  }

  // Calculate estimated monthly payment
  if (propertyData.price) {
    const loanAmount = propertyData.price * 0.8; // 20% down
    const monthlyRate = 0.07 / 12; // 7% annual interest
    const numPayments = 30 * 12; // 30-year mortgage
    const monthlyPayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
      (Math.pow(1 + monthlyRate, numPayments) - 1);
    enriched.estimated_monthly_payment = Math.round(monthlyPayment * 100) / 100;
  }

  return enriched;
}

function validateListing(propertyData: PropertyData): ValidationResult {
  const validation: ValidationResult = {
    is_valid: true,
    errors: [],
    warnings: [],
  };

  // Required fields
  const requiredFields: (keyof PropertyData)[] = [
    'address',
    'price',
    'bedrooms',
    'bathrooms',
    'square_feet'
  ];

  for (const field of requiredFields) {
    if (!propertyData[field]) {
      validation.is_valid = false;
      validation.errors.push(`Missing required field: ${field}`);
    }
  }

  // Data validation
  if (propertyData.price !== undefined) {
    if (propertyData.price <= 0) {
      validation.errors.push('Price must be greater than zero');
      validation.is_valid = false;
    } else if (propertyData.price < 10000) {
      validation.warnings.push(`Unusually low price: $${propertyData.price.toLocaleString()}`);
    }
  }

  if (propertyData.square_feet !== undefined) {
    if (propertyData.square_feet <= 0) {
      validation.errors.push('Square feet must be greater than zero');
      validation.is_valid = false;
    } else if (propertyData.square_feet < 200) {
      validation.warnings.push(`Unusually small property: ${propertyData.square_feet} sqft`);
    }
  }

  // Check for photos
  if (propertyData.photos) {
    const photoCount = propertyData.photos.length;
    if (photoCount === 0) {
      validation.warnings.push('No property photos - listings with photos get 95% more views');
    } else if (photoCount < 5) {
      validation.warnings.push(`Only ${photoCount} photos - consider adding more`);
    }
  }

  return validation;
}

function generateMLSListing(propertyData: PropertyData): MLSListing {
  const mlsListing: MLSListing = {
    ListingID: propertyData.listing_id,
    StandardStatus: 'Active',
    ListPrice: propertyData.price,
    UnparsedAddress: propertyData.address,
    City: propertyData.city,
    StateOrProvince: propertyData.state,
    PostalCode: propertyData.zip_code,
    PropertyType: propertyData.property_type,
    PropertySubType: propertyData.property_subtype,
    BedroomsTotal: propertyData.bedrooms,
    BathroomsTotalInteger: propertyData.bathrooms,
    LivingArea: propertyData.square_feet,
    LotSizeSquareFeet: propertyData.lot_size,
    YearBuilt: propertyData.year_built,
    PublicRemarks: propertyData.description,
    Media: [],
  };

  // Add photos
  if (propertyData.photos) {
    mlsListing.Media = propertyData.photos.map((photoUrl, index) => ({
      MediaURL: photoUrl,
      Order: index + 1,
      MediaCategory: 'Photo',
    }));
  }

  // Add features
  if (propertyData.features) {
    mlsListing.Features = propertyData.features;
  }

  return mlsListing;
}

async function saveToMLSSystem(mlsListing: MLSListing): Promise<boolean> {
  console.log('\n' + '='.repeat(60));
  console.log('SAVING TO MLS SYSTEM');
  console.log('='.repeat(60));

  console.log('MLS Listing Data:');
  console.log(JSON.stringify(mlsListing, null, 2));

  // In production: await axios.post('https://mls-api.example.com/listings', mlsListing);

  console.log('\n✓ Listing saved to MLS (simulated)');
  return true;
}

async function syncToPortals(propertyData: PropertyData): Promise<string[]> {
  console.log('\n' + '='.repeat(60));
  console.log('SYNCING TO REAL ESTATE PORTALS');
  console.log('='.repeat(60));

  const portals = ['Zillow', 'Realtor.com', 'Trulia', 'Redfin'];
  const syncedPortals: string[] = [];

  for (const portal of portals) {
    console.log(`  Syncing to ${portal}...`);
    // Simulate sync
    syncedPortals.push(portal);
    console.log(`    ✓ ${portal} sync completed`);
  }

  return syncedPortals;
}

function generateListingDescription(propertyData: PropertyData): string {
  const descriptionParts: string[] = [];

  const address = propertyData.address || 'this beautiful property';
  const bedrooms = propertyData.bedrooms;
  const bathrooms = propertyData.bathrooms;
  const sqft = propertyData.square_feet;
  const price = propertyData.price;

  // Opening
  descriptionParts.push(`Welcome to ${address}, offered at $${price.toLocaleString()}.`);

  // Details
  if (bedrooms && bathrooms && sqft) {
    descriptionParts.push(
      `This stunning ${bedrooms} bedroom, ${bathrooms} bathroom home features ` +
      `${sqft.toLocaleString()} square feet of beautifully designed living space.`
    );
  }

  // Features
  if (propertyData.features && propertyData.features.length > 0) {
    const featureStr = propertyData.features.slice(0, 5).join(', ');
    descriptionParts.push(`Enjoy premium amenities including ${featureStr}.`);
  }

  // Location
  if (propertyData.city) {
    descriptionParts.push(
      `Conveniently located in ${propertyData.city}, close to shopping, dining, and entertainment.`
    );
  }

  // Call to action
  descriptionParts.push('Schedule your showing today!');

  return descriptionParts.join(' ');
}

async function main() {
  console.log('='.repeat(60));
  console.log('REAL ESTATE LISTING AUTOMATION - TYPESCRIPT EXAMPLE');
  console.log('='.repeat(60));

  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/real-estate1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n⚠ Test image not found: ${testImage}`);
    console.error('Using placeholder for demonstration');
    process.exit(1);
  }

  try {
    // Upload and process property photo
    const jobId = await uploadPropertyPhoto(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const propertyData = await waitForResult(jobId);
    console.log('✓ Processing completed');

    // Save raw JSON
    const outputFile = 'property_data.json';
    fs.writeFileSync(outputFile, JSON.stringify(propertyData, null, 2));
    console.log(`\n✓ Saved property data to ${outputFile}`);

    // Enrich data
    const enrichedData = enrichPropertyData(propertyData);

    console.log('\n' + '='.repeat(60));
    console.log('PROPERTY DETAILS');
    console.log('='.repeat(60));
    console.log(`Address: ${enrichedData.address}`);
    console.log(`City: ${enrichedData.city}, ${enrichedData.state} ${enrichedData.zip_code}`);
    console.log(`Price: $${enrichedData.price.toLocaleString()}`);
    console.log(`Bedrooms: ${enrichedData.bedrooms}`);
    console.log(`Bathrooms: ${enrichedData.bathrooms}`);
    console.log(`Square Feet: ${enrichedData.square_feet.toLocaleString()}`);

    if (enrichedData.price_per_sqft) {
      console.log(`Price/SqFt: $${enrichedData.price_per_sqft}`);
    }

    if (enrichedData.estimated_monthly_payment) {
      console.log(`Est. Monthly Payment: $${enrichedData.estimated_monthly_payment.toLocaleString()}`);
    }

    // Validate listing
    const validation = validateListing(enrichedData);

    console.log('\n' + '='.repeat(60));
    console.log('VALIDATION RESULTS');
    console.log('='.repeat(60));
    console.log(`Valid: ${validation.is_valid ? '✓' : '✗'}`);

    if (validation.errors.length > 0) {
      console.log(`\nErrors (${validation.errors.length}):`);
      validation.errors.forEach(error => console.log(`  ✗ ${error}`));
    }

    if (validation.warnings.length > 0) {
      console.log(`\nWarnings (${validation.warnings.length}):`);
      validation.warnings.forEach(warning => console.log(`  ⚠ ${warning}`));
    }

    if (validation.is_valid) {
      // Generate listing description
      const description = generateListingDescription(enrichedData);

      console.log('\n' + '='.repeat(60));
      console.log('GENERATED LISTING DESCRIPTION');
      console.log('='.repeat(60));
      console.log(description);

      // Generate MLS listing
      enrichedData.description = description;
      const mlsListing = generateMLSListing(enrichedData);

      // Save to MLS
      await saveToMLSSystem(mlsListing);

      // Sync to portals
      const syncedPortals = await syncToPortals(enrichedData);

      console.log('\n' + '='.repeat(60));
      console.log('SYNDICATION COMPLETE');
      console.log('='.repeat(60));
      console.log(`Listing published to ${syncedPortals.length} portals:`);
      syncedPortals.forEach(portal => console.log(`  ✓ ${portal}`));

      // Save MLS listing
      const mlsFile = 'mls_listing.json';
      fs.writeFileSync(mlsFile, JSON.stringify(mlsListing, null, 2));
      console.log(`\n✓ Saved MLS listing to ${mlsFile}`);
    } else {
      console.log('\n⚠ Listing requires corrections before publishing');
    }

    console.log('\n✓ Real estate listing automation completed!');

  } catch (error) {
    console.error(`\n✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
