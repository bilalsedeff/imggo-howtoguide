# Quick Start Guide

Get up and running with image-to-structured data automation in under 10 minutes.

## Prerequisites

- Basic understanding of REST APIs
- A valid API key from your image processing service provider
- Sample images for testing

## Step 1: Sign Up and Get Your API Key

1. Create an account at [img-go.com/auth/signup](https://img-go.com/auth/signup)
2. Navigate to Settings > API Keys
3. Click "Generate New Key"
4. Copy and securely store your API key

**Security Note**: Treat your API key like a password. Never commit it to version control or expose it in client-side code.

## Step 2: Test Your API Connection

Verify your API key works with a simple test request:

```bash
curl -X GET https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Expected response:
```json
{
  "success": true,
  "data": {
    "patterns": []
  }
}
```

## Step 3: Create Your First Pattern

A pattern defines what data you want to extract from images. You can create patterns via:

1. **Pattern Studio UI** (recommended for beginners)
2. **API** (for programmatic creation)

### Using Pattern Studio

1. Log in to [img-go.com/dashboard](https://img-go.com/dashboard)
2. Navigate to **Patterns** > **New Pattern**
3. Fill in the pattern details:
   - **Name**: "Invoice Data Extractor"
   - **Output Format**: JSON
   - **Instructions**: "Extract vendor name, invoice number, date, line items with descriptions and amounts, and total amount"

4. Click **Generate Template** to let AI suggest a schema
5. Review the generated schema:

```json
{
  "vendor_name": "string",
  "invoice_number": "string",
  "invoice_date": "date",
  "line_items": [
    {
      "description": "string",
      "quantity": "number",
      "unit_price": "number",
      "amount": "number"
    }
  ],
  "subtotal": "number",
  "tax": "number",
  "total_amount": "number"
}
```

6. Click **Publish** to activate your pattern

### Using API (Alternative)

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Invoice Data Extractor",
    "output_format": "json",
    "instructions": "Extract vendor name, invoice number, date, line items, and total amount",
    "schema": {
      "vendor_name": "string",
      "invoice_number": "string",
      "invoice_date": "date",
      "line_items": "array",
      "total_amount": "number"
    }
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "pattern_id": "pat_abc123xyz",
    "name": "Invoice Data Extractor",
    "endpoint": "https://img-go.com/api/patterns/pat_abc123xyz/ingest"
  }
}
```

## Step 4: Process Your First Image

Now send an image to your pattern's endpoint:

```bash
curl -X POST https://img-go.com/api/patterns/pat_abc123xyz/ingest \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-request-id-123" \
  -d '{
    "image_url": "https://example.com/invoice.jpg"
  }'
```

**Response (202 Accepted)**:
```json
{
  "success": true,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued",
    "message": "Job queued for background processing",
    "approach": "queued"
  }
}
```

## Step 5: Retrieve Results

### Option 1: Polling (Quick Testing)

Poll the job status endpoint:

```bash
curl -X GET https://img-go.com/api/jobs/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response (Job Completed)**:
```json
{
  "success": true,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "result": {
      "vendor_name": "Acme Corporation",
      "invoice_number": "INV-2024-001",
      "invoice_date": "2024-01-15",
      "line_items": [
        {
          "description": "Professional Services",
          "quantity": 10,
          "unit_price": 150.00,
          "amount": 1500.00
        },
        {
          "description": "Software License",
          "quantity": 1,
          "unit_price": 299.00,
          "amount": 299.00
        }
      ],
      "subtotal": 1799.00,
      "tax": 143.92,
      "total_amount": 1942.92
    }
  }
}
```

### Option 2: Webhooks (Production Recommended)

Configure a webhook endpoint to receive results automatically:

1. **Set up webhook endpoint** in your pattern settings
2. **Process image** (same as above)
3. **Receive webhook** automatically when processing completes:

```json
POST https://your-domain.com/webhooks/imggo
Content-Type: application/json

{
  "event": "job.completed",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "pattern_id": "pat_abc123xyz",
  "status": "completed",
  "result": {
    "vendor_name": "Acme Corporation",
    "invoice_number": "INV-2024-001",
    ...
  }
}
```

## Step 6: Scale Your Workflow

### Batch Processing

Process multiple images in parallel:

```python
import requests
import concurrent.futures

API_KEY = "your_api_key"
PATTERN_ID = "pat_abc123xyz"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

image_urls = [
    "https://example.com/invoice1.jpg",
    "https://example.com/invoice2.jpg",
    "https://example.com/invoice3.jpg"
]

def process_image(image_url):
    response = requests.post(
        f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
        headers=HEADERS,
        json={"image_url": image_url}
    )
    return response.json()

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(process_image, image_urls))

print(f"Processed {len(results)} images")
```

### Store Results in Database

Example PostgreSQL integration:

```python
import psycopg2
import requests

# Get job result
response = requests.get(
    f"https://img-go.com/api/jobs/{job_id}",
    headers={"Authorization": f"Bearer {API_KEY}"}
)
result = response.json()["data"]["result"]

# Store in database
conn = psycopg2.connect("dbname=mydb user=postgres")
cur = conn.cursor()

cur.execute("""
    INSERT INTO invoices (vendor, invoice_num, date, amount)
    VALUES (%s, %s, %s, %s)
""", (
    result["vendor_name"],
    result["invoice_number"],
    result["invoice_date"],
    result["total_amount"]
))

conn.commit()
cur.close()
conn.close()
```

## Common Issues

### 401 Unauthorized
- Verify your API key is correct
- Check that the key hasn't expired
- Ensure the `Authorization` header format is correct

### 422 Invalid Schema
- Verify your pattern schema matches the instructions
- Check that required fields are present
- Ensure data types are correct (string, number, date, array)

### 429 Rate Limit Exceeded
- You've exceeded your plan's request quota
- Implement request throttling or upgrade your plan
- Check rate limit headers in responses

### Job Stuck in "queued" Status
- High volume periods may cause delays
- Typical processing time: 10-30 seconds
- If stuck >5 minutes, contact support

## Next Steps

- Explore [20+ Use Cases](../use-cases) for specific industry solutions
- Learn about [Authentication](./authentication.md) best practices
- Set up [Webhooks](../api-reference/webhooks.md) for production workflows
- Integrate with [n8n](../automation-platforms/n8n) for visual workflow building
- Connect to [databases](../integration-guides) for data persistence

## Support

- API Reference: [img-go.com/docs](https://img-go.com/docs)
- Dashboard: [img-go.com/dashboard](https://img-go.com/dashboard)
- Community: [img-go.com/community](https://img-go.com/community)

---

**Next**: [Authentication Best Practices](./authentication.md)
