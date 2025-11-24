# Make (Integromat) Integration Guide

Build powerful visual automation workflows with Make and ImgGo for image processing.

## What is Make?

Make (formerly Integromat) is a visual platform for building complex automation workflows. It excels at:

- **Visual workflow builder**: Drag-and-drop interface with detailed data mapping
- **Advanced logic**: Complex branching, error handling, and data transformation
- **1000+ app integrations**: Connect to databases, APIs, and cloud services
- **Real-time processing**: Immediate execution with webhooks
- **Affordable pricing**: Generous free tier and competitive paid plans

## Why Make + ImgGo?

Perfect for teams that need:

- **Visual data mapping**: See exactly how data flows between modules
- **Complex workflows**: Multi-step processing with conditional logic
- **Error handling**: Built-in retry logic and error routes
- **Real-time processing**: Webhook-driven immediate execution
- **Cost-effective automation**: Free tier supports 1,000 operations/month

## Quick Start

### 1. Create Make Account

Sign up at [make.com](https://www.make.com) - free tier includes 1,000 operations/month.

### 2. Import Blueprint

1. Click **Scenarios** → **Create a new scenario**
2. Click the **three dots** (⋮) → **Import Blueprint**
3. Select one of the JSON files from this directory
4. Map your connections (Gmail, ImgGo, Database)

### 3. Configure ImgGo Connection

#### HTTP Module Setup for ImgGo

Make doesn't have a native ImgGo integration, so use the **HTTP** module:

**Module**: HTTP > Make a request

**URL**: `https://img-go.com/api/patterns/{{PATTERN_ID}}/ingest`

**Method**: POST

**Headers**:
```
Authorization: Bearer {{IMGGO_API_KEY}}
Idempotency-Key: {{unique_id}}
Content-Type: application/json
```

**Body**:
```json
{
  "image_url": "{{image_url}}"
}
```

## Available Blueprints

### 1. Invoice to Database
**File**: [invoice-to-database.json](./invoice-to-database.json)

**Flow**: Gmail → ImgGo → PostgreSQL → Email Notification

**Use case**: Automatic invoice processing and database storage

**Modules**:
1. Gmail: Watch Emails (trigger)
2. HTTP: Upload to ImgGo
3. Tools: Sleep (30 seconds)
4. HTTP: Get ImgGo result
5. Tools: Set Variables (parse result)
6. PostgreSQL: Insert Row
7. Gmail: Send Email (confirmation)

### 2. Document Router
**Flow**: Webhook → ImgGo → Router → Multiple Destinations

**Use case**: Classify documents and route to appropriate systems

**Features**:
- Automatic document classification
- Conditional routing based on document type
- Error handling with fallback to manual review

### 3. Batch Processor
**Flow**: Schedule → Cloud Storage → ImgGo → Aggregator → Report

**Use case**: Daily batch processing of images from cloud storage

**Features**:
- Scheduled execution (daily, hourly, etc.)
- Parallel processing of multiple images
- Aggregate results into single report
- Email summary with statistics

## Workflow Examples

### Example 1: Email Attachment Processing

**Scenario**: Process invoice attachments from Gmail

```
[Gmail: Watch Emails]
    ↓ (has attachment)
[Filter: Only emails with "invoice" in subject]
    ↓
[HTTP: Upload to ImgGo]
    ↓
[Tools: Sleep 30s]
    ↓
[HTTP: Get Result]
    ↓
[Tools: Set Variables]
    ↓
[PostgreSQL: Insert Invoice]
    ↓
[Gmail: Send Confirmation]
```

**Key Mappings**:

**ImgGo Upload**:
- image_url: `{{1.attachments[].url}}`
- Idempotency-Key: `{{1.id}}-{{now}}`

**Parse Result**:
```javascript
{{parseJSON(4.data.result).invoice_number}}
{{parseJSON(4.data.result).vendor.name}}
{{parseJSON(4.data.result).total_amount}}
```

### Example 2: Webhook-Driven Processing

**Scenario**: Real-time document processing via webhook

```
[Webhooks: Custom Webhook]
    ↓
[HTTP: Process with ImgGo]
    ↓
[Router]
    ├─ [High Confidence] → Auto-process
    ├─ [Low Confidence] → Manual Review
    └─ [Error] → Error Notification
[Webhooks: Response]
```

**Webhook Configuration**:

**Trigger**: Webhooks > Custom webhook

**Response**:
```json
{
  "success": true,
  "document_type": "{{classification.document_type}}",
  "confidence": "{{classification.confidence}}",
  "status": "{{if(classification.confidence > 0.85, "processed", "review_required")}}"
}
```

### Example 3: Cloud Storage Monitoring

**Scenario**: Monitor Dropbox folder for new images

```
[Dropbox: Watch Files]
    ↓
[Filter: Only image files]
    ↓
[HTTP: Process with ImgGo]
    ↓
[Iterator: Process each result]
    ↓
[Google Sheets: Add Row]
    ↓
[Dropbox: Move File] (to processed folder)
```

## Data Mapping Examples

### Accessing ImgGo Results

**Parse JSON Response**:
```javascript
// After HTTP: Get Result module

// Access invoice number
{{parseJSON(4.data.result).invoice_number}}

// Access nested vendor name
{{parseJSON(4.data.result).vendor.name}}

// Access array (line items)
{{parseJSON(4.data.result).line_items[]}}

// Calculate total from line items
{{sum(parseJSON(4.data.result).line_items[].amount)}}
```

### Conditional Logic

**Router with Filters**:

**Route 1 - High Confidence** (auto-process):
```
Condition: confidence >= 0.85
{{parseJSON(3.data.result).confidence}} >= 0.85
```

**Route 2 - Medium Confidence** (review):
```
Condition: 0.70 <= confidence < 0.85
{{parseJSON(3.data.result).confidence}} >= 0.70
AND
{{parseJSON(3.data.result).confidence}} < 0.85
```

**Route 3 - Low Confidence** (reject):
```
Condition: confidence < 0.70
{{parseJSON(3.data.result).confidence}} < 0.70
```

### Error Handling

**Add Error Handler**:

1. Right-click any module
2. Select **Add error handler**
3. Choose **Resume** or **Rollback**

**Example Error Handler**:
```
[HTTP: Process with ImgGo]
    ↓ (on error)
[Slack: Send Message]
    "WARNING: Image processing failed: {{error.message}}"
    ↓
[Tools: Resume]
```

## Advanced Features

### Polling with Repeat Module

Instead of fixed sleep time, poll until complete:

```
[HTTP: Upload to ImgGo]
    ↓
[Tools: Set Variable] (job_id)
    ↓
[Repeater]
    ↓
[HTTP: Check Job Status]
    ↓
[Filter: Status = completed]
    ↓
[Break] (exit repeater)
```

**Repeater Settings**:
- Max iterations: 30
- Delay between iterations: 2 seconds

### Batch Processing with Aggregator

Process multiple images and combine results:

```
[Dropbox: Search Files]
    ↓
[Iterator]
    ↓
[HTTP: Process Each Image]
    ↓
[Aggregator]
    ↓
[Tools: Create CSV]
    ↓
[Email: Send Report]
```

**Aggregator Configuration**:
- Source Module: HTTP Process
- Aggregate into: Array
- Group by: project_id

### Data Store Integration

Save processing history in Make's data store:

```
[HTTP: Get ImgGo Result]
    ↓
[Data Store: Add Record]
    Key: {{job_id}}
    Data: {{result}}
    Timestamp: {{now}}
```

## Integration Examples

### PostgreSQL Database

**Module**: PostgreSQL > Insert a row

**Connection**: Configure PostgreSQL credentials

**Mapping**:
```
Table: invoices
Columns:
  - invoice_number: {{5.invoice_number}}
  - vendor_name: {{5.vendor_name}}
  - total_amount: {{5.total_amount}}
  - processed_at: {{now}}
```

### Google Sheets

**Module**: Google Sheets > Add a row

**Mapping**:
```
Spreadsheet: Shelf Audit Results
Sheet: Audits
Values:
  - Store ID: {{1.store_id}}
  - Audit Date: {{formatDate(now; "YYYY-MM-DD")}}
  - Total Products: {{parseJSON(3.data.result).total_facings}}
  - Brand Share: {{parseJSON(3.data.result).brand_share.your_brand}}%
```

### Salesforce

**Module**: Salesforce > Create a record

**Mapping**:
```
Object: Lead
Fields:
  - FirstName: {{parseJSON(3.data.result).first_name}}
  - LastName: {{parseJSON(3.data.result).last_name}}
  - Email: {{parseJSON(3.data.result).email}}
  - LeadSource: "Business Card Scan"
```

## Best Practices

### 1. Use Data Stores for State

Store job IDs and results for debugging:

```javascript
// Data Store: Add Record
{
  "job_id": "{{job_id}}",
  "status": "{{status}}",
  "result": "{{result}}",
  "timestamp": "{{now}}"
}
```

### 2. Implement Retry Logic

Use error handlers with Resume:

```
[Module]
  ↓ (on error)
[Tools: Sleep] (exponential backoff)
  ↓
[Tools: Resume]
```

### 3. Validate Data Before Processing

Use filters to ensure data quality:

```
[Filter]
Condition: image_url is not empty
AND file_size > 0
AND file_extension in (jpg, png, pdf)
```

### 4. Monitor Operations Usage

Make charges by operations. Optimize:
- Use filters early to skip unnecessary processing
- Batch requests when possible
- Use webhooks instead of polling

## Troubleshooting

### Issue: "Timeout waiting for result"

**Solution**: Increase sleep time or use repeater with polling

### Issue: "Invalid JSON response"

**Solution**: Check ImgGo API response format, ensure pattern is published

### Issue: "Module failed to parse response"

**Solution**: Use `{{parseJSON()}}` function explicitly

### Issue: "Operations limit exceeded"

**Solution**: Upgrade plan or optimize workflow to use fewer operations

## Resources

- [Make Documentation](https://www.make.com/en/help)
- [Make Academy](https://www.make.com/en/academy)
- [Make Community](https://community.make.com)
- [ImgGo API Docs](https://img-go.com/docs)

## Example Blueprints

All blueprint JSON files are ready to import:

1. Download JSON file
2. Import into Make
3. Configure connections
4. Map data fields
5. Activate scenario

Start automating with Make + ImgGo today!
