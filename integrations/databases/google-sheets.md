# Google Sheets Integration Guide

Send extracted image data directly to Google Sheets for easy viewing, collaboration, and analysis—no database required.

## Why Google Sheets?

- **No technical setup**: No servers or databases needed
- **Collaboration**: Share with team in real-time
- **Familiar interface**: Everyone knows spreadsheets
- **Built-in charts**: Visualize data instantly
- **Mobile access**: View and edit from anywhere
- **Free**: No cost for small teams

## Use Cases

- **Receipt tracking**: Team expense reports
- **Shelf audits**: Store visit data collection
- **Invoice logging**: Small business accounting
- **Quality inspections**: Manufacturing checks
- **Field reports**: Service technician documentation

## Quick Start

### 1. Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Click "Blank" to create new sheet
3. Name it (e.g., "Invoice Data")
4. Create headers:

```plaintext
| Invoice Number | Vendor | Date | Amount | Status | Processed At |
```

### 2. Get Sheet ID

From your Google Sheet URL:

```plaintext
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                     ↑                                        ↑
                                     Sheet ID starts here          ends here
```

Copy the Sheet ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

### 3. Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable "Google Sheets API"
4. Create credentials:
   - Click "Create Credentials" > "Service Account"
   - Download JSON key file
5. Share your Google Sheet with the service account email (found in JSON):

   ```plaintext
   my-service-account@project-id.iam.gserviceaccount.com
   ```

   Give "Editor" permission

## Python Integration

### Using gspread

**Install**:

```bash
pip install gspread oauth2client
```

**Example**:

```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime

# Setup Google Sheets connection
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json',
    scope
)

gc = gspread.authorize(credentials)

# Open spreadsheet
SHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
sheet = gc.open_by_key(SHEET_ID).sheet1

def append_invoice_to_sheet(invoice_data):
    """Append invoice data to Google Sheet"""
    row = [
        invoice_data['invoice_number'],
        invoice_data['vendor']['name'],
        invoice_data['invoice_date'],
        float(invoice_data['total_amount']),
        'Pending',
        datetime.now().isoformat()
    ]

    sheet.append_row(row)
    print(f"Added invoice {invoice_data['invoice_number']} to sheet")

def append_line_items(invoice_data):
    """Append detailed line items"""
    for item in invoice_data.get('line_items', []):
        row = [
            invoice_data['invoice_number'],
            item['description'],
            float(item.get('quantity', 1)),
            float(item.get('unit_price', 0)),
            float(item['amount'])
        ]
        sheet.append_row(row)

# Complete workflow
def process_and_append(image_url):
    """Process invoice image and append to Google Sheets"""

    # Process with ImgGo
    response = requests.post(
        f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"image_url": image_url}
    )

    job_id = response.json()["data"]["job_id"]

    # Poll for results
    result = poll_job_result(job_id)

    # Append to Google Sheets
    append_invoice_to_sheet(result)

    return result
```

### Batch Updates

```python
def batch_append_invoices(invoices):
    """Efficiently append multiple rows"""
    rows = []

    for invoice in invoices:
        row = [
            invoice['invoice_number'],
            invoice['vendor']['name'],
            invoice['invoice_date'],
            float(invoice['total_amount']),
            'Pending',
            datetime.now().isoformat()
        ]
        rows.append(row)

    # Batch append (much faster than individual appends)
    sheet.append_rows(rows)

    print(f"Added {len(rows)} invoices to sheet")
```

### Update Existing Rows

```python
def update_invoice_status(invoice_number, new_status):
    """Find and update invoice status"""

    # Find the row
    cell = sheet.find(invoice_number)

    if cell:
        # Update status column (column 5)
        sheet.update_cell(cell.row, 5, new_status)
        print(f"Updated {invoice_number} status to {new_status}")
    else:
        print(f"Invoice {invoice_number} not found")
```

### Read from Sheet

```python
def get_pending_invoices():
    """Get all invoices with 'Pending' status"""

    # Get all values
    all_values = sheet.get_all_records()

    # Filter pending
    pending = [
        row for row in all_values
        if row['Status'] == 'Pending'
    ]

    return pending
```

## Node.js Integration

### Using google-spreadsheet

**Install**:

```bash
npm install google-spreadsheet
```

**Example**:

```javascript
const { GoogleSpreadsheet } = require('google-spreadsheet');
const creds = require('./credentials.json');

const SHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms';

async function appendInvoiceToSheet(invoiceData) {
  // Initialize sheet
  const doc = new GoogleSpreadsheet(SHEET_ID);

  // Authenticate
  await doc.useServiceAccountAuth(creds);

  // Load document
  await doc.loadInfo();

  // Get first sheet
  const sheet = doc.sheetsByIndex[0];

  // Append row
  await sheet.addRow({
    'Invoice Number': invoiceData.invoice_number,
    'Vendor': invoiceData.vendor.name,
    'Date': invoiceData.invoice_date,
    'Amount': invoiceData.total_amount,
    'Status': 'Pending',
    'Processed At': new Date().toISOString()
  });

  console.log(`Added invoice ${invoiceData.invoice_number}`);
}

// Complete workflow
async function processAndAppend(imageUrl) {
  const axios = require('axios');

  // Process with ImgGo
  const response = await axios.post(
    `https://img-go.com/api/patterns/${process.env.PATTERN_ID}/ingest`,
    { image_url: imageUrl },
    {
      headers: {
        'Authorization': `Bearer ${process.env.API_KEY}`
      }
    }
  );

  const jobId = response.data.data.job_id;

  // Poll for results
  const result = await pollJobResult(jobId);

  // Append to Google Sheets
  await appendInvoiceToSheet(result);

  return result;
}
```

## Google Apps Script Integration

Use Apps Script directly in Google Sheets for zero-setup automation.

### Script Editor

1. In Google Sheet, go to **Extensions** > **Apps Script**
2. Paste code below:

```javascript
function processInvoiceImage(imageUrl) {
  const API_KEY = 'YOUR_API_KEY';
  const PATTERN_ID = 'YOUR_PATTERN_ID';

  // Submit for processing
  const response = UrlFetchApp.fetch(
    `https://img-go.com/api/patterns/${PATTERN_ID}/ingest`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify({
        image_url: imageUrl
      })
    }
  );

  const jobId = JSON.parse(response.getContentText()).data.job_id;

  // Poll for results
  let status = 'queued';
  let result = null;

  for (let i = 0; i < 30; i++) {
    Utilities.sleep(2000); // Wait 2 seconds

    const resultResponse = UrlFetchApp.fetch(
      `https://img-go.com/api/jobs/${jobId}`,
      {
        headers: {
          'Authorization': `Bearer ${API_KEY}`
        }
      }
    );

    const data = JSON.parse(resultResponse.getContentText()).data;
    status = data.status;

    if (status === 'completed') {
      result = data.result;
      break;
    } else if (status === 'failed') {
      throw new Error('Processing failed');
    }
  }

  // Append to sheet
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  sheet.appendRow([
    result.invoice_number,
    result.vendor.name,
    result.invoice_date,
    result.total_amount,
    'Pending',
    new Date()
  ]);

  return result;
}

// Custom menu
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Invoice Processing')
    .addItem('Process Image URL', 'processImageFromPrompt')
    .addToUi();
}

function processImageFromPrompt() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt('Enter image URL:');

  if (response.getSelectedButton() === ui.Button.OK) {
    const imageUrl = response.getResponseText();
    processInvoiceImage(imageUrl);
    ui.alert('Invoice processed and added to sheet!');
  }
}
```

3. Save and run `onOpen()` once to authorize
4. Refresh Google Sheet
5. Use **Invoice Processing** menu

## n8n Integration

Easiest way to connect ImgGo to Google Sheets without code.

**Workflow**:

```
[Trigger: Gmail/Webhook/Folder Watch]
    ↓
[HTTP Request: Process with ImgGo]
    ↓
[Wait or Webhook]
    ↓
[HTTP Request: Get Result]
    ↓
[Google Sheets: Append Row]
```

**Google Sheets Node Configuration**:

```
Operation: Append
Spreadsheet: Select your sheet
Sheet Name: Sheet1

Columns:
  - Invoice Number: {{ $node['HTTP Request'].json.data.result.invoice_number }}
  - Vendor: {{ $node['HTTP Request'].json.data.result.vendor.name }}
  - Date: {{ $node['HTTP Request'].json.data.result.invoice_date }}
  - Amount: {{ $node['HTTP Request'].json.data.result.total_amount }}
  - Status: Pending
  - Processed At: {{ $now }}
```

## Advanced Features

### Data Validation

Add dropdown for status column:

```python
from gspread_formatting import *

# Set data validation for Status column
validation_rule = DataValidationRule(
    BooleanCondition('ONE_OF_LIST', ['Pending', 'Approved', 'Paid', 'Rejected']),
    showCustomUi=True
)

set_data_validation_for_cell_range(sheet, 'E2:E1000', validation_rule)
```

### Conditional Formatting

Highlight high-value invoices:

```python
from gspread_formatting import *

# Format rules
rules = get_conditional_format_rules(sheet)

# Highlight amounts > $10,000 in red
rule = ConditionalFormatRule(
    ranges=[GridRange.from_a1_range('D2:D1000', sheet)],
    booleanRule=BooleanRule(
        condition=BooleanCondition('NUMBER_GREATER', ['10000']),
        format=CellFormat(backgroundColor=Color(1, 0.8, 0.8))
    )
)

rules.append(rule)
rules.save()
```

### Charts and Pivot Tables

```python
def create_monthly_chart():
    """Create chart showing monthly invoice totals"""

    # This requires Google Sheets API v4
    from googleapiclient.discovery import build

    service = build('sheets', 'v4', credentials=credentials)

    requests = [{
        'addChart': {
            'chart': {
                'spec': {
                    'title': 'Monthly Invoice Totals',
                    'basicChart': {
                        'chartType': 'COLUMN',
                        'domains': [{
                            'domain': {
                                'sourceRange': {
                                    'sources': [{'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 100, 'startColumnIndex': 2, 'endColumnIndex': 3}]
                                }
                            }
                        }],
                        'series': [{
                            'series': {
                                'sourceRange': {
                                    'sources': [{'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 100, 'startColumnIndex': 3, 'endColumnIndex': 4}]
                                }
                            }
                        }]
                    }
                }
            }
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={'requests': requests}
    ).execute()
```

### Formulas

Add calculated columns:

```python
# Add formula to calculate days until due
sheet.update_cell(1, 7, 'Days Until Due')
sheet.update_cell(2, 7, '=C2-TODAY()')  # Assuming due date is in column C

# Copy formula down
sheet.update_cell(3, 7, '=C3-TODAY()')
# ... or use fill down
```

## Real-Time Collaboration

### Share with Team

```python
def share_sheet_with_team(email_addresses):
    """Share sheet with team members"""
    for email in email_addresses:
        sheet.share(email, perm_type='user', role='writer')
        print(f"Shared with {email}")
```

### Notifications

```python
def send_notification_on_new_invoice(invoice_data):
    """Send email notification when new invoice added"""
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(f"""
    New invoice added to tracking sheet:

    Vendor: {invoice_data['vendor']['name']}
    Invoice #: {invoice_data['invoice_number']}
    Amount: ${invoice_data['total_amount']}

    View sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}
    """)

    msg['Subject'] = f"New Invoice: {invoice_data['invoice_number']}"
    msg['From'] = 'invoices@company.com'
    msg['To'] = 'accounting@company.com'

    # Send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
```

## Performance Tips

### Batch Operations

```python
# ❌ Slow: Individual appends
for invoice in invoices:
    sheet.append_row([...])  # 100 API calls for 100 invoices

# ✅ Fast: Batch append
rows = [[...] for invoice in invoices]
sheet.append_rows(rows)  # 1 API call
```

### Caching

```python
import functools
import time

@functools.lru_cache(maxsize=1)
def get_sheet_with_cache():
    """Cache sheet object for 5 minutes"""
    return gc.open_by_key(SHEET_ID).sheet1

# Use cached version
sheet = get_sheet_with_cache()
```

### Rate Limits

Google Sheets API limits:

- **100 requests per 100 seconds per user**
- **500 requests per 100 seconds per project**

```python
import time

def rate_limited_append(rows, delay=1):
    """Append with rate limiting"""
    for i in range(0, len(rows), 10):
        batch = rows[i:i+10]
        sheet.append_rows(batch)
        time.sleep(delay)
```

## Troubleshooting

### Error: "Insufficient Permission"

**Solution**: Share sheet with service account email.

### Error: "Quota Exceeded"

**Solution**: Implement rate limiting or upgrade to paid plan.

### Slow Performance

**Solutions**:

- Use batch operations
- Cache sheet connections
- Reduce unnecessary reads

## Next Steps

- Connect to [PostgreSQL](./postgresql.md) for large datasets
- Integrate with [Airtable](./airtable.md) for advanced features
- Set up [Webhooks](../api-reference/webhooks.md) for real-time updates

---

**Perfect for**: Small teams, quick prototypes, non-technical users, collaborative workflows.
