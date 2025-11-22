# Automation Platform Integrations

ImgGo integrates seamlessly with popular automation platforms, enabling no-code/low-code image processing workflows.

## Supported Platforms

### n8n (Self-Hosted Automation)
Open-source workflow automation with powerful image processing capabilities.

- [Invoice Processing](./n8n/README.md#invoice-processing)
- [Document Classification](./n8n/README.md#document-classification)
- [Batch Processing](./n8n/README.md#batch-processing)

**Example**: Email → ImgGo → PostgreSQL
```
See: n8n/invoice-to-postgresql.json
```

### Zapier (Cloud Automation)
Popular cloud automation platform with 5,000+ app integrations.

- [Invoice to QuickBooks](./zapier/invoice-to-quickbooks.json)
- [Receipt to Expense Tracker](./zapier/receipt-to-expensify.json)
- [Document to Google Sheets](./zapier/document-to-sheets.json)

**Example**: Gmail → ImgGo → QuickBooks
```
See: zapier/invoice-to-quickbooks.json
```

### Make (Integromat)
Visual automation platform with advanced data transformation.

- [Multi-Document Processing](./make/multi-document-processor.json)
- [Image to Airtable](./make/image-to-airtable.json)

### Power Automate (Microsoft)
Enterprise automation integrated with Microsoft 365.

- [SharePoint to ImgGo](./power-automate/sharepoint-processor.json)
- [Teams Notification](./power-automate/teams-notification.json)

## Quick Start

### 1. Get ImgGo API Key

Sign up at [img-go.com/auth/signup](https://img-go.com/auth/signup) and get your API key from Settings → API Keys.

### 2. Create a Pattern

Define what you want to extract from images using Pattern Studio:

1. Go to [img-go.com/patterns](https://img-go.com/patterns)
2. Click "New Pattern"
3. Choose output format (JSON, CSV, XML, YAML, or Plain Text)
4. Write instructions (e.g., "Extract invoice vendor, number, and total")
5. Publish and copy your Pattern ID

### 3. Import Workflow

#### n8n
```bash
# Import workflow JSON
n8n import:workflow --input=n8n/invoice-to-postgresql.json

# Set credentials
n8n credentials:create --type=httpHeaderAuth --data='{"name":"ImgGo API","value":"Bearer YOUR_API_KEY"}'
```

#### Zapier
1. Click "Create Zap"
2. Import from template or use webhook
3. Add environment variables for API key and pattern ID

#### Make
1. Create new scenario
2. Import blueprint JSON
3. Configure ImgGo HTTP module with API key

## Common Workflow Patterns

### Pattern 1: Email Attachment Processing

**Trigger**: New email with attachment
**Process**: Extract data from attachment with ImgGo
**Action**: Save to database/CRM/accounting software

**Platforms**: n8n, Zapier, Make, Power Automate

**Example Use Cases**:
- Invoice processing (Email → QuickBooks)
- Resume parsing (Email → ATS)
- Form submission (Email → Database)

### Pattern 2: Cloud Storage Monitoring

**Trigger**: New file in Dropbox/Google Drive/S3
**Process**: Process with ImgGo
**Action**: Move to organized folder, update inventory

**Platforms**: n8n, Make, Power Automate

**Example Use Cases**:
- Product catalog automation (S3 → Shopify)
- Document classification (Dropbox → SharePoint)
- Construction photos (Google Drive → Procore)

### Pattern 3: Scheduled Batch Processing

**Trigger**: Scheduled (daily, hourly, etc.)
**Process**: Process all images in queue with ImgGo
**Action**: Generate reports, send summaries

**Platforms**: n8n, Make, Power Automate

**Example Use Cases**:
- Daily inventory counts (Warehouse cameras → ERP)
- Parking occupancy reports (Cameras → Dashboard)
- Quality control batches (Factory cameras → MES)

### Pattern 4: Webhook-Driven Processing

**Trigger**: Webhook from external system
**Process**: ImgGo extraction
**Action**: Return structured data immediately

**Platforms**: n8n, Make

**Example Use Cases**:
- Real-time content moderation (Upload → Safety check)
- Instant KYC verification (ID upload → Compliance check)
- Live damage assessment (Photo → Claim system)

## API Integration in Workflows

### n8n HTTP Request Node

```json
{
  "method": "POST",
  "url": "https://img-go.com/api/patterns/{{$env.PATTERN_ID}}/ingest",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Idempotency-Key",
        "value": "={{$node[\"Trigger\"].json[\"id\"]}}"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "image_url",
        "value": "={{$node[\"Trigger\"].json[\"attachment_url\"]}}"
      }
    ]
  }
}
```

### Zapier Webhooks by Zapier

**Action**: POST Request

```
URL: https://img-go.com/api/patterns/{{env.PATTERN_ID}}/ingest
Headers:
  Authorization: Bearer {{env.IMGGO_API_KEY}}
  Idempotency-Key: {{trigger.id}}
Body:
  {
    "image_url": "{{trigger.attachment_url}}"
  }
```

### Make HTTP Module

**Method**: POST
**URL**: `https://img-go.com/api/patterns/{{1.PATTERN_ID}}/ingest`

**Headers**:
```
Authorization: Bearer {{1.IMGGO_API_KEY}}
Idempotency-Key: {{1.trigger_id}}
```

**Body**:
```json
{
  "image_url": "{{1.image_url}}"
}
```

## Error Handling Best Practices

### 1. Idempotency Keys

Always use idempotency keys to prevent duplicate processing:

```javascript
// n8n Code Node
const idempotencyKey = `${$node["Trigger"].json["id"]}-${Date.now()}`;
return [{json: {idempotency_key: idempotencyKey}}];
```

### 2. Retry Logic

Configure retries for transient failures:

**n8n**: Use "Retry On Fail" node setting (3 retries with 2s backoff)
**Zapier**: Automatic retries enabled by default
**Make**: Configure error handler with retry module

### 3. Validation

Validate extracted data before downstream actions:

```javascript
// Zapier Code Step
const invoice = JSON.parse(inputData.result);

if (!invoice.vendor || !invoice.total_amount) {
  throw new Error('Missing required fields');
}

output = {validated: true, ...invoice};
```

### 4. Fallback to Manual Review

Route low-confidence results to human review:

```javascript
// n8n Switch Node
const confidence = $json.metadata.confidence;

if (confidence < 0.85) {
  return [0]; // Route to manual review queue
} else {
  return [1]; // Auto-process
}
```

## Performance Optimization

### Async Processing with Webhooks

For high-volume workflows, use webhooks instead of polling:

**Step 1**: Submit job with webhook URL
```json
{
  "image_url": "https://...",
  "webhook_url": "https://your-workflow.n8n.cloud/webhook/imggo-result"
}
```

**Step 2**: Configure webhook endpoint to receive results

**Benefits**:
- No polling overhead
- Faster processing
- Better scalability

### Batch Processing

Process multiple images in parallel:

**n8n**: Use "Split In Batches" node with 10 concurrent executions
**Make**: Configure parallel processing in router settings
**Zapier**: Use Looping by Zapier for batch operations

## Cost Optimization

### 1. Conditional Processing

Only process images that meet criteria:

```javascript
// Skip if image already processed
if ($json.metadata.processed === true) {
  return null; // Skip
}
```

### 2. Cache Results

Store results to avoid reprocessing identical images:

```sql
-- PostgreSQL example
INSERT INTO processed_images (image_hash, result_data, processed_at)
VALUES (md5(image_url), result, NOW())
ON CONFLICT (image_hash) DO NOTHING;
```

### 3. Scheduled Off-Peak Processing

Process non-urgent images during off-peak hours for lower resource costs.

## Security Best Practices

### 1. Store API Keys Securely

**n8n**: Use credentials feature, never hardcode
**Zapier**: Store in environment variables
**Make**: Use connections, not inline keys

### 2. Validate Webhooks

Verify webhook signatures to prevent unauthorized access:

```javascript
// n8n Webhook Validation
const signature = $node["Webhook"].json["headers"]["x-imggo-signature"];
const expected = crypto.createHmac('sha256', process.env.WEBHOOK_SECRET)
  .update(JSON.stringify($node["Webhook"].json["body"]))
  .digest('hex');

if (signature !== expected) {
  throw new Error('Invalid webhook signature');
}
```

### 3. Use HTTPS Only

Always use HTTPS for webhook URLs and API calls.

## Support

- Platform-specific questions: Check each platform's documentation
- ImgGo API issues: support@img-go.com
- Workflow examples: Browse `automation-platforms/` directory
- Community workflows: [ImgGo Community](https://community.img-go.com)
