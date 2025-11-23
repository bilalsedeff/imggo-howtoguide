/**
 * Content Moderation - TypeScript Integration Example
 * Detect inappropriate content in images using AI-powered analysis
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const CONTENT_MODERATION_PATTERN_ID = process.env.CONTENT_MODERATION_PATTERN_ID || 'pat_content_moderation_json';

interface JobResponse {
  success: boolean;
  data: { job_id: string; status: string };
}

interface JobResult {
  success: boolean;
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    result?: ModerationResult;
    error?: string;
  };
}

interface ContentFlag {
  detected: boolean;
  confidence: number;
}

interface ModerationResult {
  explicit_content?: ContentFlag;
  violence?: ContentFlag;
  hate_symbols?: ContentFlag;
  profanity?: ContentFlag;
  timestamp?: string;
}

interface RiskAnalysis {
  overall_risk: number;
  risk_level: string;
  flagged_categories: string[];
  action_required: string;
  reasons: string[];
}

async function uploadContentImage(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) throw new Error('IMGGO_API_KEY not set');

  const formData = new FormData();
  formData.append('file', fs.createReadStream(imagePath));

  console.log(`\nUploading image for moderation: ${path.basename(imagePath)}`);

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${CONTENT_MODERATION_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `moderation-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}

async function waitForResult(jobId: string, maxAttempts: number = 60): Promise<ModerationResult> {
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

function calculateRiskScore(moderationResult: ModerationResult): RiskAnalysis {
  const riskAnalysis: RiskAnalysis = {
    overall_risk: 0,
    risk_level: 'SAFE',
    flagged_categories: [],
    action_required: 'APPROVE',
    reasons: [],
  };

  // Check explicit content
  if (moderationResult.explicit_content?.detected) {
    const confidence = moderationResult.explicit_content.confidence;
    riskAnalysis.overall_risk += confidence * 100;
    riskAnalysis.flagged_categories.push('Explicit Content');
    riskAnalysis.reasons.push(`Explicit content detected (${(confidence * 100).toFixed(0)}% confidence)`);
  }

  // Check violence
  if (moderationResult.violence?.detected) {
    const confidence = moderationResult.violence.confidence;
    riskAnalysis.overall_risk += confidence * 80;
    riskAnalysis.flagged_categories.push('Violence');
    riskAnalysis.reasons.push(`Violent content detected (${(confidence * 100).toFixed(0)}% confidence)`);
  }

  // Check hate symbols
  if (moderationResult.hate_symbols?.detected) {
    riskAnalysis.overall_risk += 100;
    riskAnalysis.flagged_categories.push('Hate Symbols');
    riskAnalysis.reasons.push('Hate symbols detected');
  }

  // Check profanity
  if (moderationResult.profanity?.detected) {
    riskAnalysis.overall_risk += 30;
    riskAnalysis.flagged_categories.push('Profanity');
  }

  // Determine risk level
  if (riskAnalysis.overall_risk >= 80) {
    riskAnalysis.risk_level = 'HIGH';
    riskAnalysis.action_required = 'BLOCK';
  } else if (riskAnalysis.overall_risk >= 50) {
    riskAnalysis.risk_level = 'MEDIUM';
    riskAnalysis.action_required = 'REVIEW';
  } else if (riskAnalysis.overall_risk >= 20) {
    riskAnalysis.risk_level = 'LOW';
    riskAnalysis.action_required = 'FLAG';
  } else {
    riskAnalysis.risk_level = 'SAFE';
    riskAnalysis.action_required = 'APPROVE';
  }

  return riskAnalysis;
}

async function saveToModerationSystem(
  moderationResult: ModerationResult,
  riskAnalysis: RiskAnalysis,
  contentId: string
): Promise<boolean> {
  console.log('\n' + '='.repeat(60));
  console.log('SAVING TO MODERATION SYSTEM');
  console.log('='.repeat(60));

  const payload = {
    content_id: contentId,
    timestamp: moderationResult.timestamp,
    risk_score: riskAnalysis.overall_risk,
    risk_level: riskAnalysis.risk_level,
    action: riskAnalysis.action_required,
    flagged_categories: riskAnalysis.flagged_categories,
    moderation_details: moderationResult,
  };

  console.log(`Content ID: ${contentId}`);
  console.log(`Risk Level: ${riskAnalysis.risk_level}`);
  console.log(`Action: ${riskAnalysis.action_required}`);

  // In production: await axios.post('https://moderation-system.example.com/api/moderate', payload);

  console.log('\n✓ Moderation result saved (simulated)');
  return true;
}

function triggerModerationAction(riskAnalysis: RiskAnalysis, contentId: string): string {
  const action = riskAnalysis.action_required;

  console.log('\n' + '='.repeat(60));
  console.log('MODERATION ACTION');
  console.log('='.repeat(60));

  if (action === 'BLOCK') {
    console.log(`✗ CONTENT BLOCKED - Content ID: ${contentId}`);
    console.log('  • Content removed from platform');
    console.log('  • User notified of policy violation');
    console.log('  • Account flagged for review');
    return 'BLOCKED';
  } else if (action === 'REVIEW') {
    console.log(`⚠ FLAGGED FOR REVIEW - Content ID: ${contentId}`);
    console.log('  • Content hidden pending manual review');
    console.log('  • Assigned to moderation queue');
    console.log('  • User notified of pending review');
    return 'PENDING_REVIEW';
  } else if (action === 'FLAG') {
    console.log(`⚠ CONTENT FLAGGED - Content ID: ${contentId}`);
    console.log('  • Content allowed but monitored');
    console.log('  • Added to watchlist');
    return 'FLAGGED';
  } else {
    console.log(`✓ CONTENT APPROVED - Content ID: ${contentId}`);
    console.log('  • Content published');
    return 'APPROVED';
  }
}

async function main() {
  console.log('='.repeat(60));
  console.log('CONTENT MODERATION - TYPESCRIPT EXAMPLE');
  console.log('='.repeat(60));

  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/content-moderation1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n⚠ Test image not found: ${testImage}`);
    process.exit(1);
  }

  try {
    const jobId = await uploadContentImage(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const moderationResult = await waitForResult(jobId);
    console.log('✓ Processing completed');

    // Save raw JSON
    const outputFile = 'moderation_result.json';
    fs.writeFileSync(outputFile, JSON.stringify(moderationResult, null, 2));
    console.log(`\n✓ Saved moderation result to ${outputFile}`);

    // Calculate risk
    const riskAnalysis = calculateRiskScore(moderationResult);

    console.log('\n' + '='.repeat(60));
    console.log('MODERATION ANALYSIS');
    console.log('='.repeat(60));
    console.log(`Risk Level: ${riskAnalysis.risk_level}`);
    console.log(`Risk Score: ${riskAnalysis.overall_risk.toFixed(1)}/100`);
    console.log(`Recommended Action: ${riskAnalysis.action_required}`);

    if (riskAnalysis.flagged_categories.length > 0) {
      console.log(`\nFlagged Categories (${riskAnalysis.flagged_categories.length}):`);
      riskAnalysis.flagged_categories.forEach(category => console.log(`  ✗ ${category}`));
    }

    // Save to moderation system
    const contentId = `IMG-${path.basename(testImage, path.extname(testImage))}`;
    await saveToModerationSystem(moderationResult, riskAnalysis, contentId);

    // Trigger action
    triggerModerationAction(riskAnalysis, contentId);

    console.log('\n✓ Content moderation completed!');

  } catch (error) {
    console.error(`\n✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
