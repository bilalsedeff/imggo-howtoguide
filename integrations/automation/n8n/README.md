# n8n Integration Guide

Build powerful no-code/low-code image processing workflows with n8n and ImgGo.

## What is n8n?

n8n is an open-source workflow automation platform that lets you connect different apps and services without writing code. It offers:

- **Visual workflow builder**: Drag-and-drop interface
- **800+ integrations**: Connect to databases, APIs, cloud services
- **Self-hosted or cloud**: Full control over your data
- **Free and open-source**: No vendor lock-in

## Why Use n8n with ImgGo?

Perfect for teams that need:

- **No-code automation**: Build workflows without programming
- **Visual debugging**: See data flow between steps
- **Rapid prototyping**: Test ideas quickly
- **Complex logic**: Conditional branching, loops, data transformation
- **Cost-effective**: Open-source, self-hostable

## Common Workflows

1. **Email → Extract → Database**: Process invoice attachments automatically
2. **Folder Watch → Process → Google Sheets**: Monitor folder for new images
3. **Webhook → Extract → Multiple Destinations**: Fan out results to multiple systems
4. **Scheduled Batch Processing**: Process images from S3/Dropbox on schedule
5. **Form Submission → Process → CRM**: Upload forms trigger data extraction

## Quick Start

### 1. Install n8n

**Option A: Docker** (recommended):

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Option B: npm**:

```bash
npm install n8n -g
n8n start
```

Access n8n at `http://localhost:5678`

### 2. Set Up Credentials

1. Click **Credentials** in left sidebar
2. Click **Add Credential**
3. Search for **HTTP Header Auth**
4. Configure:
   - **Name**: `ImgGo API`
   - **Header Name**: `Authorization`
   - **Header Value**: `Bearer YOUR_API_KEY`
5. Click **Save**

## Workflow Examples

### Workflow 1: Invoice Email → PostgreSQL

Process invoice attachments from Gmail and store in PostgreSQL.

**Nodes**:

1. **Gmail Trigger** - Watch for new emails with attachments
2. **Filter** - Only emails with "invoice" in subject
3. **HTTP Request** - Upload image to ImgGo
4. **Wait** - Pause for processing
5. **HTTP Request** - Get job result
6. **PostgreSQL** - Insert extracted data

**Visual Flow**:

```
[Gmail Trigger] → [Filter] → [HTTP: Upload] → [Wait] → [HTTP: Get Result] → [PostgreSQL]
```

**Step-by-Step Setup**:

#### Node 1: Gmail Trigger

```
Trigger: Gmail
Trigger On: Message Received
Label Names: invoices
```

#### Node 2: Filter

```
Conditions:
  - attachments.length > 0
  - subject contains "invoice"
```

#### Node 3: HTTP Request - Upload Image

```
Method: POST
URL: https://img-go.com/api/patterns/YOUR_PATTERN_ID/ingest
Authentication: ImgGo API (credential created earlier)
Body:
{
  "image_url": "{{ $node['Gmail Trigger'].json['attachments'][0]['url'] }}"
}

Options:
  Response Format: JSON
```

#### Node 4: Wait

```
Resume: After Time Interval
Wait Amount: 30
Time Unit: seconds
```

#### Node 5: HTTP Request - Get Result

```
Method: GET
URL: https://img-go.com/api/jobs/{{ $node['HTTP Request'].json['data']['job_id'] }}
Authentication: ImgGo API
Response Format: JSON
```

#### Node 6: PostgreSQL

```
Operation: Insert
Table: invoices
Columns:
  - vendor_name: {{ $node['HTTP Request1'].json['data']['result']['vendor_name'] }}
  - invoice_number: {{ $node['HTTP Request1'].json['data']['result']['invoice_number'] }}
  - invoice_date: {{ $node['HTTP Request1'].json['data']['result']['invoice_date'] }}
  - total_amount: {{ $node['HTTP Request1'].json['data']['result']['total_amount'] }}
```

### Workflow 2: Dropbox Watch → Process → Google Sheets

Monitor Dropbox folder for new shelf photos, extract product data, append to Google Sheets.

**Nodes**:

1. **Dropbox Trigger** - Watch folder for new files
2. **HTTP Request** - Process with ImgGo
3. **Code** - Poll for completion
4. **Google Sheets** - Append product data

**Visual Flow**:

```
[Dropbox Trigger] → [HTTP: Process] → [Code: Poll] → [Google Sheets: Append]
```

**Detailed Configuration**:

#### Node 1: Dropbox Trigger

```
Trigger: Dropbox
Trigger On: File Created
Folder: /ShelfAudits
```

#### Node 2: HTTP Request

```
Method: POST
URL: https://img-go.com/api/patterns/YOUR_SHELF_PATTERN_ID/ingest
Authentication: ImgGo API
Body:
{
  "image_url": "{{ $node['Dropbox'].json['link'] }}"
}
```

#### Node 3: Code Node - Poll for Completion

```javascript
// Poll job status until completed
const jobId = $node['HTTP Request'].json['data']['job_id'];
const apiKey = 'YOUR_API_KEY';

let status = 'queued';
let result = null;
let attempts = 0;
const maxAttempts = 30;

while (status !== 'completed' && attempts < maxAttempts) {
  const response = await $http.get({
    url: `https://img-go.com/api/jobs/${jobId}`,
    headers: {
      'Authorization': `Bearer ${apiKey}`
    }
  });

  status = response.data.status;

  if (status === 'completed') {
    result = response.data.result;
    break;
  } else if (status === 'failed') {
    throw new Error('Job failed: ' + response.data.error);
  }

  await new Promise(resolve => setTimeout(resolve, 2000));
  attempts++;
}

return { json: result };
```

#### Node 4: Google Sheets

```
Operation: Append
Document: Shelf Audit Report
Sheet: Audits
Columns:
  - Store ID: {{ $node['Dropbox'].json['path_display'].split('/')[2] }}
  - Audit Date: {{ $now }}
  - Total Products: {{ $node['Code'].json['analytics']['total_facings'] }}
  - Brand Share: {{ $node['Code'].json['analytics']['your_brand_share_percent'] }}%
  - Out of Stock: {{ $node['Code'].json['analytics']['out_of_stock_count'] }}
```

### Workflow 3: Webhook → Process → Fan-Out

Receive webhook, process image, send results to multiple destinations.

**Nodes**:

1. **Webhook** - Receive image submission
2. **HTTP Request** - Process with ImgGo
3. **Wait** - Allow processing time
4. **HTTP Request** - Get results
5. **Split In Batches** - Prepare for fan-out
6. **PostgreSQL** - Store in database
7. **Slack** - Send notification
8. **HTTP Request** - Send to external webhook
9. **Google Sheets** - Append to sheet

**Visual Flow**:

```
[Webhook] → [HTTP: Process] → [Wait] → [HTTP: Get] → [Split] → [PostgreSQL]
                                                             → [Slack]
                                                             → [HTTP: External]
                                                             → [Google Sheets]
```

## Advanced Patterns

### Error Handling

Add error handling to gracefully handle failures:

```
1. Wrap risky nodes in Error Trigger
2. Add error notification
3. Retry logic for transient errors
```

**Example Error Handler**:

```javascript
// Error Trigger Node
const error = $input.first().json;

// Send to Slack
await $http.post({
  url: process.env.SLACK_WEBHOOK_URL,
  json: {
    text: `WARNING: Workflow Error: ${error.message}`,
    attachments: [{
      fields: [
        { title: 'Node', value: error.node },
        { title: 'Error', value: error.error }
      ]
    }]
  }
});

// Log to database
await $http.post({
  url: 'YOUR_ERROR_LOGGING_ENDPOINT',
  json: {
    workflow: 'invoice_processing',
    error: error,
    timestamp: new Date().toISOString()
  }
});

return [];
```

### Conditional Routing

Route based on extracted data:

```javascript
// IF Node
const totalAmount = $node['HTTP Request1'].json['data']['result']['total_amount'];

// Route to different paths based on amount
if (totalAmount > 10000) {
  return [
    { json: { route: 'high_value', data: $input.first().json } }
  ];
} else if (totalAmount > 1000) {
  return [
    { json: { route: 'medium_value', data: $input.first().json } }
  ];
} else {
  return [
    { json: { route: 'auto_approve', data: $input.first().json } }
  ];
}
```

### Batch Processing

Process multiple images efficiently:

```javascript
// Function Node - Batch Upload
const images = $input.all();
const apiKey = process.env.IMGGO_API_KEY;
const patternId = process.env.IMGGO_PATTERN_ID;

const jobIds = [];

for (const item of images) {
  const response = await $http.post({
    url: `https://img-go.com/api/patterns/${patternId}/ingest`,
    headers: {
      'Authorization': `Bearer ${apiKey}`
    },
    json: {
      image_url: item.json.image_url
    }
  });

  jobIds.push({
    job_id: response.data.job_id,
    image_url: item.json.image_url
  });

  // Rate limiting
  await new Promise(resolve => setTimeout(resolve, 100));
}

return jobIds.map(item => ({ json: item }));
```

## Pre-Built Workflow Templates

Download ready-to-use workflow templates from the `workflows/` directory:

1. [Invoice Processing](./workflows/invoice-processing.json)
2. [Shelf Audit](./workflows/shelf-audit.json)
3. [Receipt Management](./workflows/receipt-management.json)
4. [ID Verification](./workflows/id-verification.json)
5. [Damage Assessment](./workflows/damage-assessment.json)

### Importing Templates

1. Download JSON file
2. In n8n, click **Workflows** > **Import from File**
3. Select downloaded JSON
4. Update credentials and pattern IDs
5. Activate workflow

## Integration with Other Tools

### Zapier Migration

Convert Zapier workflows to n8n:

| Zapier | n8n Equivalent |
|--------|----------------|
| Trigger | Trigger Node |
| Action | Action Node |
| Filter | IF Node |
| Formatter | Code Node |
| Delay | Wait Node |

### Power Automate Comparison

| Power Automate | n8n |
|----------------|-----|
| Flows | Workflows |
| Connectors | Nodes |
| Conditions | IF Node |
| Variables | Expressions |
| Error Handling | Error Trigger |

## Performance Optimization

### 1. Use Webhooks Instead of Polling

```javascript
// Instead of polling in n8n
while (status !== 'completed') {
  await sleep(2000);
  checkStatus();
}

// Use webhook trigger
// Configure webhook in ImgGo pattern settings
// Point to n8n webhook URL
```

### 2. Parallel Processing

```javascript
// Process multiple images in parallel
const images = $input.all();
const promises = images.map(item =>
  processImage(item.json.image_url)
);

const results = await Promise.all(promises);
return results.map(r => ({ json: r }));
```

### 3. Caching

```javascript
// Cache frequently accessed data
const cacheKey = `result_${imageHash}`;

// Check cache
const cached = await $redis.get(cacheKey);
if (cached) {
  return { json: JSON.parse(cached) };
}

// Process and cache
const result = await processImage(imageUrl);
await $redis.setex(cacheKey, 86400, JSON.stringify(result));

return { json: result };
```

## Monitoring & Debugging

### Enable Execution Logging

```
Settings > General:
  [x] Save execution progress
  [x] Save manual executions
  [x] Save error executions
```

### View Execution Data

1. Click **Executions** in sidebar
2. Select execution to inspect
3. View data at each node
4. Check for errors

### Set Up Alerts

```javascript
// Monitor workflow health
if ($workflow.lastRun.status === 'error') {
  await $http.post({
    url: process.env.SLACK_WEBHOOK,
    json: {
      text: `Workflow ${$workflow.name} failed`
    }
  });
}
```

## Troubleshooting

### Issue: Timeout Waiting for Results

**Solution**: Use webhook trigger instead of Wait node.

### Issue: Rate Limit Errors

**Solution**: Add rate limiting between requests:

```javascript
for (const item of items) {
  await processImage(item);
  await new Promise(resolve => setTimeout(resolve, 100)); // 100ms delay
}
```

### Issue: Large Result Data

**Solution**: Store results in database, pass only ID:

```javascript
// Instead of passing large JSON
return { json: fullResult };  // Can exceed n8n limits

// Store and pass reference
const resultId = await saveToDatabase(fullResult);
return { json: { result_id: resultId } };
```

## Resources

- [n8n Documentation](https://docs.n8n.io)
- [n8n Community Forum](https://community.n8n.io)
- [Workflow Templates](./workflows)
- [Video Tutorials](https://www.youtube.com/c/n8n-io)

## Next Steps

- Try [Workflow Templates](./workflows)
- Explore [Database Integrations](../../integration-guides)
- Review [Error Handling](../../api-reference/error-handling.md) patterns

---

**Sources**:

- [n8n Official Documentation](https://docs.n8n.io/)
- [Mastering AI Image Automation with n8n](https://n8n-automation.com/2024/09/25/top-10-ai-image-automations/)
- [n8n Workflow Templates](https://n8n.io/workflows/)
