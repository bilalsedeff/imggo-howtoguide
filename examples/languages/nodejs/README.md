# Node.js/TypeScript Examples

Production-ready Node.js and TypeScript code examples for the ImgGo API.

## Installation

```bash
cd examples/languages/nodejs
npm install
```

## Setup

Set your API key as an environment variable:

```bash
export IMGGO_API_KEY="your_api_key_here"
```

Or create a `.env` file:

```plaintext
IMGGO_API_KEY=your_api_key_here
IMGGO_BASE_URL=https://img-go.com/api
```

## Examples

### 1. Basic Upload (`basic-upload.ts`)

Upload an image file directly and get results.

**When to use:**

- Simple, one-off image processing
- Backend services with local files
- Getting started

**Usage:**

```bash
npx ts-node basic-upload.ts path/to/image.jpg PATTERN_ID
```

**Example:**

```bash
npx ts-node basic-upload.ts ../../test-images/invoice1.jpg pat_invoice_abc123
```

**Features:**

- Direct file upload using multipart/form-data
- Synchronous polling
- Simple error handling
- TypeScript type safety

---

### 2. URL Processing (`url-processing.ts`)

Process images from public URLs (S3, CDN, cloud storage).

**When to use:**

- Cloud-based workflows
- Images already hosted elsewhere
- Email attachment processing
- S3/CloudFront integration
- Serverless functions (Lambda, Cloud Functions)

**Usage:**

```bash
npx ts-node url-processing.ts <image_url> PATTERN_ID
```

**Example:**

```bash
npx ts-node url-processing.ts https://my-cdn.com/invoices/inv001.jpg pat_invoice_abc123
```

**Features:**

- Process remote images
- No file downloads required
- Ideal for serverless architectures
- Lower bandwidth usage

---

### 3. Error Handling (`error-handling.ts`)

Production-ready example with comprehensive error handling.

**When to use:**

- Production deployments
- High-reliability requirements
- Network-unstable environments
- Enterprise applications

**Usage:**

```bash
npx ts-node error-handling.ts path/to/image.jpg PATTERN_ID
```

**Features:**

- Automatic retry with exponential backoff
- Rate limit handling (429 status codes)
- Timeout management
- Idempotency keys to prevent duplicates
- Custom TypeScript exception classes
- Result validation
- Request timeout configuration

**Error Handling:**

- `429 Rate Limit` → Waits for `Retry-After` header duration
- `5xx Server Errors` → Retries with exponential backoff (1s, 2s, 4s, ...)
- `4xx Client Errors` → Fails immediately (don't retry invalid requests)
- `Connection Errors` → Retries with backoff
- `Timeouts` → Retries with backoff

**Custom Exceptions:**

- `ImgGoAPIError` - Base exception class
- `RateLimitError` - Rate limit exceeded
- `ValidationError` - Invalid request or result

---

### 4. Async Batch Processing (`async-batch.ts`)

Process multiple images concurrently using Promise.all().

**When to use:**

- Batch processing workflows
- High-volume processing (100s-1000s of images)
- Time-sensitive processing
- API endpoint with multiple images

**Usage:**

```bash
npx ts-node async-batch.ts PATTERN_ID image1.jpg image2.jpg image3.jpg ...
```

**Example:**

```bash
npx ts-node async-batch.ts pat_invoice_abc123 invoice*.jpg
```

**Features:**

- Concurrent uploads (10 at a time by default)
- Concurrent polling
- Batch progress tracking
- Results saved to JSON file
- Summary statistics
- Graceful error handling per image

**Performance:**

- Process 100 images in parallel
- 10-20x faster than sequential processing
- Configurable concurrency limit

---

## Code Patterns

### Pattern 1: Simple Upload

```typescript
import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';

async function uploadImage(imagePath: string, patternId: string): Promise<string> {
  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  const response = await axios.post(
    `https://img-go.com/api/patterns/${patternId}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}
```

### Pattern 2: Polling with Timeout

```typescript
async function pollJob(jobId: string, maxAttempts: number = 60): Promise<any> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const response = await axios.get(
      `https://img-go.com/api/jobs/${jobId}`,
      { headers: { 'Authorization': `Bearer ${API_KEY}` } }
    );

    const { status, manifest, result } = response.data.data;

    if (status === 'succeeded') {
      return manifest || result;
    }

    if (status === 'failed') {
      throw new Error(response.data.data.error);
    }

    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error('Job timeout');
}
```

### Pattern 3: URL Processing

```typescript
async function processUrl(imageUrl: string, patternId: string): Promise<string> {
  const response = await axios.post(
    `https://img-go.com/api/patterns/${patternId}/ingest`,
    { image_url: imageUrl },
    {
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
    }
  );

  return response.data.data.job_id;
}
```

### Pattern 4: Error Handling with Retry

```typescript
async function uploadWithRetry(
  imagePath: string,
  patternId: string,
  maxRetries: number = 3
): Promise<string> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await uploadImage(imagePath, patternId);
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;

      const waitTime = Math.pow(2, attempt) * 1000; // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }

  throw new Error('Upload failed after retries');
}
```

### Pattern 5: Batch Processing

```typescript
async function processBatch(imagePaths: string[], patternId: string): Promise<any[]> {
  // Phase 1: Upload all concurrently
  const uploadPromises = imagePaths.map(path => uploadImage(path, patternId));
  const jobIds = await Promise.all(uploadPromises);

  // Phase 2: Poll all concurrently
  const pollPromises = jobIds.map(jobId => pollJob(jobId));
  return await Promise.all(pollPromises);
}
```

## Best Practices

### 1. Always Use Idempotency Keys

```typescript
const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Idempotency-Key': `unique-request-id-${imageHash}`,
};
```

Prevents duplicate processing if request is retried.

### 2. Set Timeouts

```typescript
const response = await axios.post(url, data, { timeout: 30000 }); // 30 seconds
```

Prevents hanging connections.

### 3. Validate Results

```typescript
const result = data.manifest;
if (!result || !result.required_field) {
  throw new Error('Invalid result');
}
```

### 4. Use TypeScript Interfaces

```typescript
interface JobResponse {
  data: {
    job_id: string;
  };
}

interface JobResult {
  data: {
    status: string;
    manifest?: any;
    result?: any;
    error?: string;
  };
}
```

Provides type safety and autocomplete.

### 5. Handle Streams Properly

```typescript
const stream = fs.createReadStream(imagePath);
formData.append('image', stream);

// Stream is automatically closed after upload
```

### 6. Log Everything in Production

```typescript
console.log(`Processing ${imagePath} with pattern ${patternId}`);
console.log(`Job created: ${jobId}`);
console.error(`Job failed: ${error}`);
```

## Common Issues

### Issue: `Cannot find module 'axios'`

**Solution:**

```bash
npm install
```

### Issue: `Error: IMGGO_API_KEY environment variable not set`

**Solution:**

```bash
export IMGGO_API_KEY="your_key_here"
```

Or create a `.env` file and load it:

```typescript
import dotenv from 'dotenv';
dotenv.config();
```

### Issue: `ENOENT: no such file or directory`

**Solution:** Use absolute paths or check current working directory:

```typescript
import path from 'path';
const absolutePath = path.resolve(__dirname, imagePath);
```

### Issue: `SyntaxError: Cannot use import statement outside a module`

**Cause:** Mixing ES modules with CommonJS

**Solution:** Use `ts-node` to run TypeScript files directly:

```bash
npx ts-node script.ts
```

Or compile first:

```bash
npx tsc
node dist/script.js
```

### Issue: `Error: socket hang up` or `ETIMEDOUT`

**Cause:** Network issues or API slowness

**Solution:** Use the error-handling example with retry logic, or increase timeout:

```typescript
axios.post(url, data, { timeout: 60000 }) // 60 seconds
```

## Deployment Patterns

### AWS Lambda

```typescript
import { Handler } from 'aws-lambda';

export const handler: Handler = async (event) => {
  const { imageUrl, patternId } = event;
  const result = await processImageUrl(imageUrl, patternId);
  return { statusCode: 200, body: JSON.stringify(result) };
};
```

### Express.js API

```typescript
import express from 'express';
import multer from 'multer';

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/process', upload.single('image'), async (req, res) => {
  const result = await uploadImage(req.file.path, req.body.pattern_id);
  res.json(result);
});

app.listen(3000);
```

### NestJS Service

```typescript
import { Injectable } from '@nestjs/common';

@Injectable()
export class ImgGoService {
  async processImage(imagePath: string, patternId: string): Promise<any> {
    const jobId = await this.uploadImage(imagePath, patternId);
    return await this.pollJob(jobId);
  }
}
```

## Next Steps

- See [Use Cases](../../../use-cases/) for complete end-to-end examples
- See [Formats](../../formats/) for output format examples
- See [Integrations](../../../integrations/) for database/automation setup

## Need Help?

- [API Reference](../../../docs/api-reference/)
- [Getting Started Guide](../../../docs/getting-started/)
- GitHub Issues
