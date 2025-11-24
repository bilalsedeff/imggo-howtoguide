/**
 * Quality Control Test - TypeScript/Node.js Example
 * Demonstrates ImgGo API usage with TypeScript
 */

import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const BASE_URL = 'img-go.com';

interface JobResponse {
    success: boolean;
    data: {
        job_id?: string;
        status?: string;
        manifest?: Record<string, unknown>;
        result?: Record<string, unknown>;
    };
}

function getPatternId(): string | null {
    const envId = process.env.QUALITY_CONTROL_PATTERN_ID;
    if (envId) return envId;

    const patternFile = path.join(__dirname, 'pattern_id.txt');
    if (fs.existsSync(patternFile)) {
        return fs.readFileSync(patternFile, 'utf-8').trim();
    }
    return null;
}

async function submitImage(patternId: string, imagePath: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const imageData = fs.readFileSync(imagePath);
        const boundary = '----FormBoundary' + Math.random().toString(36).substring(2);

        const body = Buffer.concat([
            Buffer.from(`--${boundary}\r\n`),
            Buffer.from(`Content-Disposition: form-data; name="image"; filename="${path.basename(imagePath)}"\r\n`),
            Buffer.from('Content-Type: image/jpeg\r\n\r\n'),
            imageData,
            Buffer.from(`\r\n--${boundary}--\r\n`)
        ]);

        const options: https.RequestOptions = {
            hostname: BASE_URL,
            path: `/api/patterns/${patternId}/ingest`,
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${IMGGO_API_KEY}`,
                'Content-Type': `multipart/form-data; boundary=${boundary}`,
                'Content-Length': body.length,
                'Idempotency-Key': `qc-ts-${Date.now()}`
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const response: JobResponse = JSON.parse(data);
                    if (response.data?.job_id) {
                        resolve(response.data.job_id);
                    } else {
                        reject(new Error(`No job_id in response: ${data}`));
                    }
                } catch (e) {
                    reject(new Error(`Failed to parse response: ${data}`));
                }
            });
        });

        req.on('error', reject);
        req.write(body);
        req.end();
    });
}

async function pollForResult(jobId: string, maxAttempts = 30): Promise<Record<string, unknown>> {
    for (let i = 0; i < maxAttempts; i++) {
        const result = await new Promise<JobResponse>((resolve, reject) => {
            const options: https.RequestOptions = {
                hostname: BASE_URL,
                path: `/api/jobs/${jobId}`,
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${IMGGO_API_KEY}`
                }
            };

            const req = https.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        reject(new Error(`Failed to parse response: ${data}`));
                    }
                });
            });

            req.on('error', reject);
            req.end();
        });

        const status = result.data?.status;
        if (status === 'succeeded' || status === 'completed') {
            return result.data?.manifest || result.data?.result || result.data;
        } else if (status === 'failed') {
            throw new Error('Job failed');
        }

        console.log(`Status: ${status}, waiting... (${i + 1}/${maxAttempts})`);
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
    throw new Error('Timeout waiting for result');
}

async function main(): Promise<void> {
    console.log('='.repeat(60));
    console.log('TESTING QUALITY CONTROL PATTERN (TypeScript)');
    console.log('='.repeat(60));

    if (!IMGGO_API_KEY) {
        console.log('\nX Error: IMGGO_API_KEY not set');
        process.exit(1);
    }

    const patternId = getPatternId();
    if (!patternId) {
        console.log('\nX Error: QUALITY_CONTROL_PATTERN_ID not set');
        console.log('Run create-pattern.py first to create a pattern');
        process.exit(1);
    }

    const testImage = path.join(__dirname, '../../examples/test-images/inventory1.jpg');
    if (!fs.existsSync(testImage)) {
        console.log(`\nX Error: Test image not found: ${testImage}`);
        process.exit(1);
    }

    console.log(`\nPattern ID: ${patternId}`);
    console.log(`Test Image: inventory1.jpg\n`);

    try {
        console.log('Processing quality inspection image...');
        const jobId = await submitImage(patternId, testImage);
        console.log(`Job submitted: ${jobId}`);

        const result = await pollForResult(jobId);
        console.log('V Processing completed!\n');

        // Save output
        const outputDir = path.join(__dirname, 'outputs');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir);
        }

        const outputFile = path.join(outputDir, 'quality_control_ts_output.json');
        fs.writeFileSync(outputFile, JSON.stringify(result, null, 2));

        console.log(`V Output saved to: ${outputFile}\n`);
        console.log('='.repeat(60));
        console.log('QC INSPECTION RESULTS');
        console.log('='.repeat(60));
        console.log(JSON.stringify(result, null, 2));
        console.log('\nV Test completed successfully!');

    } catch (error) {
        console.log(`\nX Error: ${error}`);
        process.exit(1);
    }
}

main();
