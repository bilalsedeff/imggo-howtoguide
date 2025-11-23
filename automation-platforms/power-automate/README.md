# Power Automate Integration Guide

Build enterprise-grade automation workflows with Microsoft Power Automate and ImgGo for image processing.

## What is Power Automate?

Power Automate (formerly Microsoft Flow) is Microsoft's cloud-based automation platform, tightly integrated with Microsoft 365 and Azure. It's ideal for:

- **Microsoft 365 Integration**: Seamlessly works with Outlook, Teams, SharePoint, OneDrive
- **Enterprise Features**: Advanced security, compliance, and governance
- **Azure Services**: Easy integration with Azure Functions, Logic Apps, Cognitive Services
- **Desktop Automation**: RPA capabilities with Power Automate Desktop
- **Dataverse**: Built-in database for storing workflow data

## Why Power Automate + ImgGo?

Perfect for enterprises using Microsoft stack:

- **Native Office 365 integration**: Process emails, SharePoint files, Teams attachments
- **Enterprise security**: Azure AD authentication, DLP policies, compliance features
- **Governance**: Centralized management, audit logs, environment controls
- **Scalability**: Handle enterprise-level automation volumes
- **Approvals**: Built-in approval workflows for document processing

## Quick Start

### 1. Access Power Automate

- Go to [make.powerautomate.com](https://make.powerautomate.com)
- Sign in with your Microsoft 365 account
- Free tier available, premium features require license

### 2. Import Flow

1. Click **My flows** → **Import** → **Import Package (Legacy)**
2. Upload one of the JSON files from this directory
3. Configure connections (Outlook, SharePoint, etc.)
4. Update environment variables

### 3. Configure ImgGo Connection

Power Automate doesn't have a native ImgGo connector, so use **HTTP** action:

**Action**: HTTP

**Method**: POST

**URI**: `https://img-go.com/api/patterns/@{variables('IMGGO_PATTERN_ID')}/ingest`

**Headers**:
```
Authorization: Bearer @{variables('IMGGO_API_KEY')}
Idempotency-Key: @{triggerOutputs()?['id']}-@{utcNow()}
Content-Type: application/json
```

**Body**:
```json
{
  "image_url": "@{triggerOutputs()?['attachments'][0]['contentBytes']}"
}
```

## Available Flows

### 1. Invoice to SharePoint
**File**: [invoice-to-sharepoint.json](./invoice-to-sharepoint.json)

**Trigger**: When a new email arrives (Office 365 Outlook)

**Actions**:
1. Extract invoice data with ImgGo
2. Save PDF to SharePoint document library
3. Create item in SharePoint list with metadata
4. Send approval request email

**Use Case**: Automated invoice processing for AP teams

**SharePoint Setup**:

Create a list named "Invoices" with these columns:
- Title (Text) - Invoice Number
- VendorName (Text)
- InvoiceDate (Date)
- DueDate (Date)
- TotalAmount (Number)
- Status (Choice: Pending Review, Approved, Rejected)
- FileLink (Hyperlink)

### 2. Document Approval Workflow
**Flow**: Email → ImgGo → SharePoint → Teams Approval

**Features**:
- Automatic document classification
- Route to appropriate approver based on document type
- Teams notification with approval buttons
- Update SharePoint based on approval decision

### 3. Expense Report Automation
**Flow**: Outlook → ImgGo → Excel Online → Email

**Features**:
- Process receipt attachments
- Extract expense data
- Update Excel workbook
- Send monthly summary

## Workflow Examples

### Example 1: Email Attachment Processing

```
[When email arrives] (Office 365 Outlook)
    ↓
[Condition] Has attachment
    ↓
[HTTP] Upload to ImgGo
    ↓
[Delay] 30 seconds
    ↓
[HTTP] Get result
    ↓
[Parse JSON] Extract invoice data
    ↓
[Create file] Save to SharePoint
    ↓
[Create item] Add to SharePoint list
    ↓
[Start approval] Send approval request
```

### Example 2: SharePoint Trigger

```
[When file created] (SharePoint)
    ↓
[Get file content] Read file
    ↓
[HTTP] Process with ImgGo
    ↓
[Apply to each] Process results
    ↓
[Update file properties] Add metadata
    ↓
[Send email] Notify team
```

### Example 3: Teams Integration

```
[When message posted] (Teams)
    ↓
[Get file attachments] Extract files
    ↓
[HTTP] Process with ImgGo
    ↓
[Reply to message] Post results in Teams
```

## Data Operations

### Parse JSON Action

After getting ImgGo result, use **Parse JSON** to work with the data:

**Schema for Invoice**:
```json
{
  "type": "object",
  "properties": {
    "invoice_number": { "type": "string" },
    "vendor": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "address": { "type": "string" }
      }
    },
    "invoice_date": { "type": "string" },
    "due_date": { "type": "string" },
    "total_amount": { "type": "number" },
    "line_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "description": { "type": "string" },
          "amount": { "type": "number" }
        }
      }
    }
  }
}
```

### Expressions

**Get first attachment**:
```
@triggerOutputs()?['attachments'][0]
```

**Format date**:
```
@formatDateTime(body('Parse_JSON')?['invoice_date'], 'yyyy-MM-dd')
```

**Calculate total**:
```
@body('Parse_JSON')?['total_amount']
```

**Check if field exists**:
```
@if(empty(body('Parse_JSON')?['vendor']), 'Unknown', body('Parse_JSON')?['vendor']?['name'])
```

## Conditional Logic

### Condition Action

**Check confidence score**:
```
Condition: @body('Parse_JSON')?['confidence']
Operator: is greater than
Value: 0.85
```

**If true**: Auto-approve
**If false**: Route to manual review

### Switch Action

**Route by document type**:

**Expression**: `@body('Parse_JSON')?['document_type']`

**Cases**:
- **invoice**: Create in accounting system
- **receipt**: Add to expense report
- **contract**: Send to legal team
- **Default**: Flag for manual review

## Approval Workflows

### Start and Wait for Approval

**Action**: Start and wait for an approval

**Approval type**: Approve/Reject - First to respond

**Title**: `Invoice Approval: @{body('Parse_JSON')?['invoice_number']}`

**Assigned to**: approver@company.com

**Details**:
```
Invoice Number: @{body('Parse_JSON')?['invoice_number']}
Vendor: @{body('Parse_JSON')?['vendor']?['name']}
Amount: $@{body('Parse_JSON')?['total_amount']}
Due Date: @{body('Parse_JSON')?['due_date']}

View invoice: @{outputs('Create_file')?['WebUrl']}
```

### Handle Approval Response

```
[Condition] Outcome equals Approve
    ↓ (Yes)
[Update item] Set status to Approved
[Send email] Notify AP team
    ↓ (No)
[Update item] Set status to Rejected
[Send email] Notify submitter
```

## SharePoint Integration

### Create File

**Action**: Create file (SharePoint)

**Site Address**: `https://yourtenant.sharepoint.com/sites/YourSite`

**Folder Path**: `/Invoices`

**File Name**: `@{body('Parse_JSON')?['invoice_number']}.pdf`

**File Content**: `@{triggerOutputs()?['attachments'][0]['contentBytes']}`

### Create List Item

**Action**: Create item (SharePoint)

**Site Address**: `https://yourtenant.sharepoint.com/sites/YourSite`

**List Name**: `Invoices`

**Fields**:
- Title: `@{body('Parse_JSON')?['invoice_number']}`
- VendorName: `@{body('Parse_JSON')?['vendor']?['name']}`
- InvoiceDate: `@{body('Parse_JSON')?['invoice_date']}`
- TotalAmount: `@{body('Parse_JSON')?['total_amount']}`
- Status: `Pending Review`

### Update File Properties

Add metadata to uploaded files:

**Action**: Update file properties (SharePoint)

**File Identifier**: `@{outputs('Create_file')?['ItemId']}`

**Custom Properties**:
- InvoiceNumber: `@{body('Parse_JSON')?['invoice_number']}`
- Vendor: `@{body('Parse_JSON')?['vendor']?['name']}`
- Amount: `@{body('Parse_JSON')?['total_amount']}`

## Teams Integration

### Post Message

**Action**: Post message in a chat or channel (Teams)

**Team**: Your Team Name

**Channel**: General

**Message**:
```
**New Invoice Processed**

Invoice Number: @{body('Parse_JSON')?['invoice_number']}
Vendor: @{body('Parse_JSON')?['vendor']?['name']}
Amount: $@{body('Parse_JSON')?['total_amount']}

[View in SharePoint](@{outputs('Create_file')?['WebUrl']})
```

### Adaptive Card

Post rich cards with actions:

**Card JSON**:
```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.2",
  "body": [
    {
      "type": "TextBlock",
      "text": "New Invoice: @{body('Parse_JSON')?['invoice_number']}",
      "weight": "Bolder",
      "size": "Large"
    },
    {
      "type": "FactSet",
      "facts": [
        { "title": "Vendor", "value": "@{body('Parse_JSON')?['vendor']?['name']}" },
        { "title": "Amount", "value": "$@{body('Parse_JSON')?['total_amount']}" },
        { "title": "Due Date", "value": "@{body('Parse_JSON')?['due_date']}" }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View Invoice",
      "url": "@{outputs('Create_file')?['WebUrl']}"
    }
  ]
}
```

## Error Handling

### Configure Run After

Set actions to run on failure:

1. Click **...** on any action
2. Select **Configure run after**
3. Check **has failed** or **has timed out**
4. Add error notification action

### Try-Catch Pattern

```
[Scope] Main Processing
  └─ [HTTP] Process with ImgGo
  └─ [Parse JSON] Extract data
  └─ [Create item] Save to SharePoint

[Scope] Error Handler (Configure to run after Main Processing has failed)
  └─ [Compose] Format error message
  └─ [Send email] Notify admin
  └─ [Terminate] End flow with failure status
```

## Performance Optimization

### Parallel Processing

Use **Parallel Branch** to process multiple actions simultaneously:

```
[HTTP: Get Result]
    ├─ [Branch 1] Save to SharePoint
    ├─ [Branch 2] Send email notification
    └─ [Branch 3] Post to Teams
```

### Batch Processing

Use **Apply to each** with concurrency control:

**Settings** → **Concurrency Control** → **On** → Degree: 10

## Security Best Practices

### Secure Inputs/Outputs

Prevent sensitive data from appearing in run history:

1. Click **...** on HTTP action
2. Select **Settings**
3. Enable **Secure Inputs** and **Secure Outputs**

### Use Azure Key Vault

Store API keys in Key Vault:

**Action**: Get secret (Azure Key Vault)

**Name of secret**: `IMGGO-API-KEY`

Then use: `@body('Get_secret')?['value']` in HTTP action

### Data Loss Prevention

Configure DLP policies to prevent sensitive data leakage:

1. Go to **Power Platform Admin Center**
2. Create DLP policy
3. Classify connectors (Business/Non-Business/Blocked)

## Monitoring & Analytics

### Flow Analytics

View metrics in Power Automate portal:
- Run history
- Success/failure rates
- Average duration
- Most active flows

### Application Insights

Connect to Azure Application Insights for advanced monitoring:
- Custom telemetry
- Performance metrics
- Error tracking
- Usage analytics

## Common Patterns

### Email Polling

**Trigger**: When a new email arrives (V3)

**Folder**: Inbox

**Subject Filter**: `invoice`

**Has Attachments**: Yes

**Include Attachments**: Yes

### Schedule-Based

**Trigger**: Recurrence

**Frequency**: Day

**Interval**: 1

**Time zone**: UTC

**At these hours**: 2 (runs at 2 AM daily)

### Webhook Response

**Trigger**: When an HTTP request is received

**Request Body JSON Schema**: Define expected payload

**Response**: Return processing result

## Troubleshooting

### Issue: "The file name you specified could not be found"

**Solution**: Check SharePoint permissions and file path

### Issue: "Invalid JSON in request body"

**Solution**: Validate JSON structure, use Parse JSON action

### Issue: "Flow timeout"

**Solution**: Increase timeout in settings or use asynchronous pattern

### Issue: "Attachment too large"

**Solution**: Use OneDrive/SharePoint instead of email attachments

## Resources

- [Power Automate Documentation](https://learn.microsoft.com/en-us/power-automate/)
- [Power Automate Community](https://powerusers.microsoft.com/t5/Power-Automate-Community/ct-p/MPACommunity)
- [Power Platform Admin Center](https://admin.powerplatform.microsoft.com/)
- [ImgGo API Docs](https://img-go.com/docs)

## Example Flows

All flow JSON files are ready to import:

1. Download JSON file
2. Import into Power Automate
3. Configure connections
4. Update variables
5. Test and activate

Start automating with Power Automate + ImgGo today!
