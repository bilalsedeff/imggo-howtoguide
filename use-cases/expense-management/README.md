# Expense Management & Receipt Processing

Automate expense report creation with receipt image-to-CSV conversion for accounting systems and spreadsheet analysis.

## Business Problem

Companies struggle with manual expense reporting:

- **Time-consuming**: Employees spend 20+ minutes per expense report
- **Error-prone**: 19% of expense reports contain errors
- **Delayed reimbursement**: 2-3 weeks average processing time
- **Poor visibility**: Finance teams lack real-time spending insights
- **Compliance issues**: Missing receipts and inadequate documentation
- **High costs**: $58 average cost to process one expense report manually

**Lost productivity**: Employees hate expense reports - 54% call it the worst part of business travel.

## Solution: Image to CSV Automation

Automated receipt processing with CSV output for easy import:

1. **Capture**: Employee photographs receipt with mobile app
2. **Upload**: Auto-sync to expense management system
3. **Extract**: Convert image to CSV with all transaction details
4. **Categorize**: AI suggests expense categories
5. **Export**: Download CSV for import into accounting software
6. **Approve**: Manager reviews and approves in dashboard
7. **Reimburse**: Integrate with payroll for automatic payment

**Result**: 80% time savings, 95% accuracy, instant reimbursement.

## CSV Output Format

### Single Receipt CSV

```csv
Date,Merchant,Category,Amount,Currency,Payment Method,Receipt Number,Tax,Notes
2025-01-20,Starbucks,Meals & Entertainment,15.47,USD,Corporate Card,****1234,1.23,Client meeting - coffee
```

### Batch Receipts CSV Export

Perfect for monthly expense reports:

```csv
Employee,Date,Merchant,Category,Amount,Currency,Payment Method,Receipt Number,Tax,Project Code,Notes
John Smith,2025-01-15,Uber,Transportation,32.50,USD,Personal,UBER-123,0.00,PROJ-001,Airport transfer
John Smith,2025-01-15,Hilton Hotel,Lodging,245.00,USD,Corporate Card,****1234,19.60,PROJ-001,Conference accommodation
John Smith,2025-01-16,The Capital Grille,Meals & Entertainment,127.80,USD,Corporate Card,****1234,10.22,PROJ-001,Client dinner
John Smith,2025-01-16,FedEx Office,Office Supplies,18.99,USD,Personal,FDX-456,1.52,PROJ-001,Printing materials
John Smith,2025-01-17,Delta Airlines,Transportation,450.00,USD,Corporate Card,****1234,0.00,PROJ-001,Return flight
```

### JSON Output (Alternative)

For API integrations:

```json
{
  "receipt_date": "2025-01-20",
  "merchant_name": "Starbucks",
  "merchant_address": "123 Main St, Seattle, WA",
  "receipt_number": "1234-5678",
  "items": [
    {
      "description": "Grande Latte",
      "quantity": 2,
      "unit_price": 5.45,
      "amount": 10.90
    },
    {
      "description": "Croissant",
      "quantity": 2,
      "unit_price": 2.25,
      "amount": 4.50
    }
  ],
  "subtotal": 15.40,
  "tax": 1.23,
  "tip": 0.00,
  "total": 16.63,
  "payment_method": "Visa ****1234",
  "category_suggested": "Meals & Entertainment"
}
```

## Pattern Setup

### CSV Output Pattern

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Receipt to CSV",
    "output_format": "csv",
    "instructions": "Extract receipt details as CSV row. Include date, merchant name, total amount, tax, payment method (last 4 digits if card), and list individual line items if visible. Suggest expense category based on merchant type.",
    "csv_headers": ["Date", "Merchant", "Category", "Amount", "Currency", "Tax", "Payment Method", "Receipt Number", "Items", "Notes"]
  }'
```

### JSON Output Pattern

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Receipt Data Extractor",
    "output_format": "json",
    "instructions": "Extract all receipt details including merchant, date, line items, subtotal, tax, tip, total, and payment method.",
    "schema": {
      "receipt_date": "date",
      "merchant_name": "string",
      "merchant_address": "string",
      "items": [
        {
          "description": "string",
          "quantity": "number",
          "amount": "number"
        }
      ],
      "subtotal": "number",
      "tax": "number",
      "tip": "number",
      "total": "number",
      "payment_method": "string"
    }
  }'
```

## Batch Processing to CSV

### Python Script: Folder to CSV

```python
import os
import requests
import csv
from datetime import datetime
import glob

API_KEY = os.environ["IMGGO_API_KEY"]
PATTERN_ID = os.environ["IMGGO_PATTERN_ID"]

def process_receipts_to_csv(input_folder, output_csv):
    """Process all receipt images in folder and generate CSV"""

    # Get all image files
    image_files = glob.glob(os.path.join(input_folder, "*.{jpg,jpeg,png}"), recursive=False)
    image_files.extend(glob.glob(os.path.join(input_folder, "*.JPG")))
    image_files.extend(glob.glob(os.path.join(input_folder, "*.PNG")))

    results = []

    for image_path in image_files:
        print(f"Processing {os.path.basename(image_path)}...")

        try:
            # Upload image
            result = process_receipt_image(image_path)
            results.append(result)

        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            continue

    # Write to CSV
    write_to_csv(results, output_csv)

    print(f"\nProcessed {len(results)} receipts → {output_csv}")

def process_receipt_image(image_path):
    """Process single receipt image"""

    # Upload to CDN first (or use direct upload)
    image_url = upload_to_cdn(image_path)

    # Process with ImgGo
    response = requests.post(
        f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"image_url": image_url}
    )

    job_id = response.json()["data"]["job_id"]

    # Poll for results
    result = poll_job_result(job_id)

    # Enhance with auto-categorization
    result['category'] = categorize_expense(result['merchant_name'])
    result['employee'] = os.environ.get("EMPLOYEE_NAME", "Unknown")
    result['project_code'] = extract_project_from_filename(image_path)

    return result

def categorize_expense(merchant_name):
    """Auto-categorize based on merchant"""
    merchant_lower = merchant_name.lower()

    categories = {
        'Meals & Entertainment': ['restaurant', 'starbucks', 'cafe', 'pizza', 'bar', 'grill'],
        'Transportation': ['uber', 'lyft', 'taxi', 'airline', 'delta', 'united', 'parking'],
        'Lodging': ['hotel', 'hilton', 'marriott', 'airbnb', 'inn'],
        'Office Supplies': ['staples', 'office depot', 'fedex', 'ups'],
        'Fuel': ['shell', 'chevron', 'exxon', 'mobil', 'gas'],
        'Communications': ['verizon', 'at&t', 't-mobile', 'sprint']
    }

    for category, keywords in categories.items():
        if any(keyword in merchant_lower for keyword in keywords):
            return category

    return 'Other'

def extract_project_from_filename(filepath):
    """Extract project code from filename (e.g., PROJ001_receipt.jpg)"""
    filename = os.path.basename(filepath)

    if filename.startswith('PROJ'):
        return filename.split('_')[0]

    return ''

def write_to_csv(results, output_path):
    """Write results to CSV file"""

    if not results:
        print("No results to write")
        return

    # Define CSV columns
    fieldnames = [
        'Employee',
        'Date',
        'Merchant',
        'Category',
        'Amount',
        'Currency',
        'Tax',
        'Payment Method',
        'Receipt Number',
        'Project Code',
        'Notes'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({
                'Employee': result.get('employee', ''),
                'Date': result.get('receipt_date', ''),
                'Merchant': result.get('merchant_name', ''),
                'Category': result.get('category', ''),
                'Amount': result.get('total', 0),
                'Currency': result.get('currency', 'USD'),
                'Tax': result.get('tax', 0),
                'Payment Method': result.get('payment_method', ''),
                'Receipt Number': result.get('receipt_number', ''),
                'Project Code': result.get('project_code', ''),
                'Notes': ''
            })

def poll_job_result(job_id):
    """Poll for job completion"""
    import time

    for attempt in range(30):
        response = requests.get(
            f"https://img-go.com/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )

        data = response.json()["data"]

        if data["status"] == "completed":
            return data["result"]
        elif data["status"] == "failed":
            raise Exception(f"Job failed: {data.get('error')}")

        time.sleep(2)

    raise Exception("Timeout waiting for results")

# Usage
if __name__ == "__main__":
    process_receipts_to_csv(
        input_folder="./receipts/january",
        output_csv="./exports/january_expenses.csv"
    )
```

### Node.js: Email Attachments to CSV

```javascript
// email-receipts-to-csv.js
const { google } = require('googleapis');
const axios = require('axios');
const fs = require('fs');
const csvWriter = require('csv-writer').createObjectCsvWriter;

const API_KEY = process.env.IMGGO_API_KEY;
const PATTERN_ID = process.env.IMGGO_PATTERN_ID;

async function processEmailReceipts() {
  // Connect to Gmail
  const gmail = google.gmail({ version: 'v1', auth: getGmailAuth() });

  // Search for emails with receipts
  const res = await gmail.users.messages.list({
    userId: 'me',
    q: 'subject:receipt OR subject:invoice has:attachment'
  });

  const messages = res.data.messages || [];

  const results = [];

  for (const message of messages) {
    const msg = await gmail.users.messages.get({
      userId: 'me',
      id: message.id
    });

    // Process attachments
    for (const part of msg.data.payload.parts || []) {
      if (part.filename && isImageAttachment(part)) {
        const attachment = await getAttachment(gmail, message.id, part.body.attachmentId);

        // Process receipt
        const result = await processReceiptImage(attachment);
        results.push(result);
      }
    }
  }

  // Write to CSV
  await writeCSV(results, 'email_receipts.csv');

  console.log(`Processed ${results.length} receipts`);
}

async function processReceiptImage(imageBuffer) {
  // Upload to CDN first
  const imageUrl = await uploadToCDN(imageBuffer);

  // Process with ImgGo
  const response = await axios.post(
    `https://img-go.com/api/patterns/${PATTERN_ID}/ingest`,
    { image_url: imageUrl },
    {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    }
  );

  const jobId = response.data.data.job_id;

  // Poll for results
  return await pollJobResult(jobId);
}

async function writeCSV(results, filename) {
  const writer = csvWriter({
    path: filename,
    header: [
      { id: 'date', title: 'Date' },
      { id: 'merchant', title: 'Merchant' },
      { id: 'category', title: 'Category' },
      { id: 'amount', title: 'Amount' },
      { id: 'currency', title: 'Currency' },
      { id: 'tax', title: 'Tax' },
      { id: 'payment_method', title: 'Payment Method' }
    ]
  });

  const records = results.map(r => ({
    date: r.receipt_date,
    merchant: r.merchant_name,
    category: categorizeExpense(r.merchant_name),
    amount: r.total,
    currency: r.currency || 'USD',
    tax: r.tax || 0,
    payment_method: r.payment_method
  }));

  await writer.writeRecords(records);
}

processEmailReceipts();
```

## Integration with Accounting Software

### QuickBooks Integration

```python
from intuitlib.client import AuthClient
from quickbooks import QuickBooks

def sync_to_quickbooks(csv_file):
    """Import expenses from CSV to QuickBooks"""

    # Authenticate with QuickBooks
    auth_client = AuthClient(
        client_id=os.environ["QB_CLIENT_ID"],
        client_secret=os.environ["QB_CLIENT_SECRET"],
        redirect_uri=os.environ["QB_REDIRECT_URI"]
    )

    qb_client = QuickBooks(
        auth_client=auth_client,
        refresh_token=os.environ["QB_REFRESH_TOKEN"],
        company_id=os.environ["QB_COMPANY_ID"]
    )

    # Read CSV
    import pandas as pd
    df = pd.read_csv(csv_file)

    # Create expense for each row
    for _, row in df.iterrows():
        expense = {
            "TxnDate": row['Date'],
            "PaymentType": "Cash",
            "AccountRef": {
                "value": get_expense_account_id(row['Category'])
            },
            "Line": [{
                "Amount": row['Amount'],
                "DetailType": "AccountBasedExpenseLineDetail",
                "Description": f"{row['Merchant']} - {row['Notes']}",
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {
                        "value": get_expense_account_id(row['Category'])
                    }
                }
            }]
        }

        # Create in QuickBooks
        qb_client.create_expense(expense)

    print(f"Synced {len(df)} expenses to QuickBooks")
```

### Expensify Integration

```javascript
async function syncToExpensify(csvFilePath) {
  const expenses = await readCSV(csvFilePath);

  for (const expense of expenses) {
    await axios.post('https://integrations.expensify.com/Integration-Server/ExpensifyIntegrations', {
      type: 'create',
      credentials: {
        partnerUserID: process.env.EXPENSIFY_USER_ID,
        partnerUserSecret: process.env.EXPENSIFY_SECRET
      },
      inputSettings: {
        type: 'expenses',
        employeeEmail: expense.employee_email,
        merchant: expense.merchant,
        created: expense.date,
        amount: expense.amount * 100, // Cents
        currency: expense.currency,
        category: expense.category
      }
    });
  }
}
```

## Mobile App Integration

### React Native Expense Tracker

```javascript
// ExpenseCapture.js
import React, { useState } from 'react';
import { Camera } from 'expo-camera';
import * as FileSystem from 'expo-file-system';

const ExpenseCapture = () => {
  const [expenses, setExpenses] = useState([]);

  const captureReceipt = async () => {
    const photo = await camera.takePictureAsync();

    // Process receipt
    const formData = new FormData();
    formData.append('file', {
      uri: photo.uri,
      type: 'image/jpeg',
      name: 'receipt.jpg'
    });

    const response = await fetch(
      `https://img-go.com/api/patterns/${PATTERN_ID}/ingest`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_KEY}`
        },
        body: formData
      }
    );

    const jobId = await response.json().data.job_id;

    const result = await pollJobResult(jobId);

    // Add to local state
    setExpenses([...expenses, result]);

    // Save to device
    await saveToLocalStorage(result);

    // Show preview
    navigation.navigate('ExpensePreview', { expense: result });
  };

  const exportToCSV = async () => {
    // Convert expenses to CSV
    const csv = convertToCSV(expenses);

    // Share or upload
    await shareCSV(csv);
  };

  return (
    <View>
      <Camera ref={ref => camera = ref} />
      <Button title="Capture Receipt" onPress={captureReceipt} />
      <Button title="Export CSV" onPress={exportToCSV} />
    </View>
  );
};
```

## Real-World Use Cases

### Business Travel Expense Report

```csv
Trip,Date,Merchant,Category,Amount,Reimbursable,Project
NYC Conference,2025-01-15,Delta Airlines,Transportation,450.00,Yes,CONF-2025
NYC Conference,2025-01-15,Uber,Transportation,32.50,Yes,CONF-2025
NYC Conference,2025-01-15,Hilton Midtown,Lodging,245.00,Yes,CONF-2025
NYC Conference,2025-01-16,Starbucks,Meals,12.50,Yes,CONF-2025
NYC Conference,2025-01-16,Ruth's Chris,Client Dinner,287.00,Yes,CONF-2025
NYC Conference,2025-01-17,Uber,Transportation,28.00,Yes,CONF-2025
```

### Monthly Department Expenses

```csv
Department,Employee,Date,Category,Amount,Vendor,Invoice Number
Marketing,John Smith,2025-01-10,Advertising,1200.00,Google Ads,INV-12345
Marketing,Sarah Johnson,2025-01-12,Events,850.00,Eventbrite,EVT-567
Sales,Mike Brown,2025-01-15,Client Entertainment,320.00,The Capital Grille,TGI-890
IT,Alice Wong,2025-01-18,Software,99.00,Adobe,SUB-234
```

## Performance Metrics

| Metric | Manual Entry | Automated CSV |
|--------|-------------|---------------|
| Time per Receipt | 3-5 minutes | 10-20 seconds |
| Monthly Report Time | 2-3 hours | 5 minutes |
| Data Accuracy | 81% | 96% |
| Reimbursement Cycle | 14-21 days | 1-3 days |
| Processing Cost | $58/report | $5/report |

## Integration Examples

Complete code examples in `integration-examples/`:

- [Python Batch CSV Export](./integration-examples/python-batch-to-csv.py)
- [Node.js Email to CSV](./integration-examples/nodejs-email-to-csv.js)
- [React Native App](./integration-examples/react-native-expense-app.js)
- [QuickBooks Sync](./integration-examples/quickbooks-integration.py)

## Next Steps

- Explore [Invoice Processing](../invoice-processing) for vendor bills
- Review [Google Sheets Integration](../../integration-guides/google-sheets.md)
- Set up [Batch Processing](../../examples/batch-processing)

---

**SEO Keywords**: receipt to CSV, expense management automation, image to CSV conversion, receipt OCR to spreadsheet, batch receipt processing

**Sources**:
- [Expense Report Statistics](https://www.certify.com/)
- [OCR for Business](https://www.klippa.com/)
