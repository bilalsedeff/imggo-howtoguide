/**
 * Create ImgGo Pattern for Content Moderation
 * Node.js/TypeScript version
 * Detect inappropriate content in images
 */

import axios from 'axios';
import * as fs from 'fs';
import * as dotenv from 'dotenv';

dotenv.config();

const API_KEY = process.env.IMGGO_API_KEY;
const BASE_URL = 'https://img-go.com/api';

interface PatternResponse {
  success: boolean;
  data: {
    id: string;
    name: string;
    format: string;
    endpoint_url: string;
  };
}

async function createModerationPattern(): Promise<string | null> {
  if (!API_KEY) {
    console.error('X Error: IMGGO_API_KEY not set');
    return null;
  }

  // Based on ImgGo API: format must be json, yaml, xml, csv, or text
  // All properties must be in required array
  const payload = {
    name: 'Content Moderation - JSON (Node.js)',
    instructions: 'Analyze image for inappropriate content. Detect: violence, adult content, hate symbols, weapons, drugs, self-harm. Return safety assessment and flagged categories.',
    format: 'json',
    json_schema: {
      type: 'object',
      properties: {
        is_safe: { type: 'boolean' },
        risk_level: { type: 'string' },
        flagged_categories: { type: 'string' },
        confidence: { type: 'number' }
      },
      required: ['is_safe', 'risk_level', 'flagged_categories', 'confidence'],
      additionalProperties: false
    }
  };

  console.log('='.repeat(60));
  console.log('CREATING CONTENT MODERATION PATTERN (Node.js)');
  console.log('='.repeat(60));
  console.log();

  try {
    const response = await axios.post<PatternResponse>(
      `${BASE_URL}/patterns`,
      payload,
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    console.log(`Response Status: ${response.status}`);

    const patternId = response.data.data.id;

    console.log('V Pattern created successfully!');
    console.log();
    console.log(`Pattern ID: ${patternId}`);
    console.log();
    console.log('Add to .env:');
    console.log(`CONTENT_MODERATION_PATTERN_ID=${patternId}`);
    console.log();

    // Save pattern ID to file
    fs.writeFileSync('pattern_id.txt', patternId);
    console.log('V Saved to pattern_id.txt');

    return patternId;

  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(`X Error: ${error.message}`);
      if (error.response) {
        console.error(`Response: ${JSON.stringify(error.response.data)}`);
      }
    } else {
      console.error(`X Error: ${error}`);
    }
    return null;
  }
}

// Run if called directly
createModerationPattern();

export { createModerationPattern };
