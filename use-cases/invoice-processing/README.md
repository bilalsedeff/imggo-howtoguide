# Invoice Processing Automation

Automatically extract invoice data from images and sync to accounting systems, ERPs, or databases.

## Business Problem

Finance teams manually process hundreds or thousands of invoices monthly:

- **Time-consuming**: 5-10 minutes per invoice for manual data entry
- **Error-prone**: Human mistakes in amounts, dates, account codes
- **Slow approvals**: Manual routing delays payment cycles
- **No visibility**: Lack of real-time tracking and reporting

**Cost**: At $12.42 per invoice (manual processing), processing 1,000 invoices/month costs $12,420/month or $149,040/year.

## Solution

Automated invoice processing with image-to-structured data extraction:

1. **Receive invoices** via email, upload, or scan
2. **Extract data** automatically (vendor, amounts, line items, dates)
3. **Validate** against business rules
4. **Route** for approval based on amount thresholds
5. **Sync** to accounting system (QuickBooks, Xero, NetSuite, SAP)

**Result**: Processing cost drops to $2.65 per invoice - a **79% reduction**.

## What Gets Extracted

### Standard Invoice Fields

```json
{
  "vendor": {
    "name": "string",
    "address": "string",
    "tax_id": "string",
    "contact_email": "string",
    "contact_phone": "string"
  },
  "invoice_number": "string",
  "po_number": "string",
  "invoice_date": "date",
  "due_date": "date",
  "line_items": [
    {
      "line_number": "number",
      "description": "string",
      "quantity": "number",
      "unit_price": "number",
      "amount": "number",
      "tax_rate": "number",
      "account_code": "string"
    }
  ],
  "subtotal": "number",
  "tax_total": "number",
  "discount": "number",
  "shipping": "number",
  "total_amount": "number",
  "currency": "string",
  "payment_terms": "string",
  "notes": "string"
}
```

## Pattern Setup

### Create Pattern (One-Time)

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Invoice Data Extractor - Production",
    "output_format": "json",
    "instructions": "Extract all invoice details including vendor information (name, address, tax ID, contact details), invoice metadata (number, PO number, dates, payment terms), line items with descriptions, quantities, unit prices, amounts, and tax rates, and totals (subtotal, tax, discount, shipping, grand total). Extract currency code. If any field is not visible, return null for that field.",
    "schema": {
      "vendor": {
        "name": "string",
        "address": "string",
        "tax_id": "string",
        "contact_email": "email",
        "contact_phone": "phone"
      },
      "invoice_number": "string",
      "po_number": "string",
      "invoice_date": "date",
      "due_date": "date",
      "line_items": [
        {
          "line_number": "number",
          "description": "string",
          "quantity": "number",
          "unit_price": "number",
          "amount": "number",
          "tax_rate": "number"
        }
      ],
      "subtotal": "number",
      "tax_total": "number",
      "discount": "number",
      "shipping": "number",
      "total_amount": "number",
      "currency": "string",
      "payment_terms": "string"
    }
  }'
```

## End-to-End Workflows

### Workflow 1: Email → Extract → PostgreSQL

**Stack**: Python + Gmail API + PostgreSQL

**1. Watch for new invoice emails**:

```python
import os
import imaplib
import email
from email.header import decode_header
import requests
import psycopg2
from datetime import datetime

# Configuration
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
IMGGO_API_KEY = os.environ["IMGGO_API_KEY"]
IMGGO_PATTERN_ID = os.environ["IMGGO_PATTERN_ID"]
DB_CONNECTION = os.environ["DATABASE_URL"]

def connect_to_inbox():
    """Connect to Gmail IMAP"""
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(GMAIL_USER, GMAIL_PASSWORD)
    imap.select("INBOX")
    return imap

def get_unread_invoices():
    """Fetch unread emails with 'invoice' in subject"""
    imap = connect_to_inbox()
    status, messages = imap.search(None, '(UNSEEN SUBJECT "invoice")')

    invoice_emails = []
    for num in messages[0].split():
        status, msg_data = imap.fetch(num, "(RFC822)")
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)

        # Extract attachments
        for part in email_message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if filename and filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                invoice_emails.append({
                    'filename': filename,
                    'data': part.get_payload(decode=True)
                })

    return invoice_emails

def upload_and_process_invoice(file_data, filename):
    """Upload to CDN and process via ImgGo"""
    # Upload to your CDN/S3 (simplified example)
    upload_url = f"https://your-cdn.com/invoices/{filename}"

    # Process with ImgGo
    response = requests.post(
        f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
        headers={"Authorization": f"Bearer {IMGGO_API_KEY}"},
        json={"image_url": upload_url}
    )

    job_id = response.json()["data"]["job_id"]
    return job_id

def poll_job_result(job_id, max_attempts=30):
    """Poll for job completion"""
    import time

    for attempt in range(max_attempts):
        response = requests.get(
            f"https://img-go.com/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {IMGGO_API_KEY}"}
        )

        data = response.json()["data"]

        if data["status"] == "completed":
            return data["result"]
        elif data["status"] == "failed":
            raise Exception(f"Job failed: {data.get('error')}")

        time.sleep(2)

    raise Exception("Job timeout")

def store_in_database(invoice_data):
    """Store extracted data in PostgreSQL"""
    conn = psycopg2.connect(DB_CONNECTION)
    cur = conn.cursor()

    # Insert invoice header
    cur.execute("""
        INSERT INTO invoices (
            vendor_name, vendor_tax_id, invoice_number, po_number,
            invoice_date, due_date, subtotal, tax_total,
            discount, shipping, total_amount, currency, payment_terms,
            created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING invoice_id
    """, (
        invoice_data["vendor"]["name"],
        invoice_data["vendor"]["tax_id"],
        invoice_data["invoice_number"],
        invoice_data["po_number"],
        invoice_data["invoice_date"],
        invoice_data["due_date"],
        invoice_data["subtotal"],
        invoice_data["tax_total"],
        invoice_data["discount"],
        invoice_data["shipping"],
        invoice_data["total_amount"],
        invoice_data["currency"],
        invoice_data["payment_terms"],
        datetime.now()
    ))

    invoice_id = cur.fetchone()[0]

    # Insert line items
    for item in invoice_data["line_items"]:
        cur.execute("""
            INSERT INTO invoice_line_items (
                invoice_id, line_number, description, quantity,
                unit_price, amount, tax_rate
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            invoice_id,
            item["line_number"],
            item["description"],
            item["quantity"],
            item["unit_price"],
            item["amount"],
            item["tax_rate"]
        ))

    conn.commit()
    cur.close()
    conn.close()

    return invoice_id

# Main execution
if __name__ == "__main__":
    invoices = get_unread_invoices()

    for invoice in invoices:
        job_id = upload_and_process_invoice(invoice['data'], invoice['filename'])
        result = poll_job_result(job_id)
        invoice_id = store_in_database(result)
        print(f"Processed invoice {invoice_id}: {result['invoice_number']}")
```

**Database Schema**:

```sql
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL,
    vendor_tax_id VARCHAR(50),
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    po_number VARCHAR(100),
    invoice_date DATE NOT NULL,
    due_date DATE,
    subtotal DECIMAL(15,2),
    tax_total DECIMAL(15,2),
    discount DECIMAL(15,2),
    shipping DECIMAL(15,2),
    total_amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_terms VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoice_line_items (
    line_item_id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(invoice_id),
    line_number INTEGER,
    description TEXT NOT NULL,
    quantity DECIMAL(10,2),
    unit_price DECIMAL(15,2),
    amount DECIMAL(15,2) NOT NULL,
    tax_rate DECIMAL(5,2)
);

CREATE INDEX idx_invoices_vendor ON invoices(vendor_name);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_status ON invoices(status);
```

### Workflow 2: S3 Upload → Lambda → QuickBooks

**Stack**: AWS S3 + Lambda + QuickBooks API

See [integration-examples/aws-lambda-quickbooks.py](./integration-examples/aws-lambda-quickbooks.py)

### Workflow 3: n8n Automation Workflow

**Stack**: n8n (no-code platform)

See [integration-examples/n8n-workflow.json](./integration-examples/n8n-workflow.json)

## Validation Rules

Implement business logic validation:

```python
def validate_invoice(data):
    """Validate extracted invoice data"""
    errors = []

    # Check required fields
    required_fields = ['vendor', 'invoice_number', 'total_amount', 'invoice_date']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")

    # Validate total matches sum of line items
    if data.get('line_items'):
        calculated_subtotal = sum(item['amount'] for item in data['line_items'])
        if abs(calculated_subtotal - data.get('subtotal', 0)) > 0.01:
            errors.append(f"Subtotal mismatch: {calculated_subtotal} vs {data['subtotal']}")

    # Validate total = subtotal + tax - discount + shipping
    expected_total = (
        data.get('subtotal', 0) +
        data.get('tax_total', 0) -
        data.get('discount', 0) +
        data.get('shipping', 0)
    )

    if abs(expected_total - data.get('total_amount', 0)) > 0.01:
        errors.append(f"Total mismatch: expected {expected_total}, got {data['total_amount']}")

    # Check for duplicate invoice number
    if invoice_exists_in_db(data['invoice_number']):
        errors.append(f"Duplicate invoice number: {data['invoice_number']}")

    return errors

def invoice_exists_in_db(invoice_number):
    """Check if invoice already exists"""
    conn = psycopg2.connect(DB_CONNECTION)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM invoices WHERE invoice_number = %s", (invoice_number,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count > 0
```

## Approval Workflow

Route invoices based on amount thresholds:

```python
def route_for_approval(invoice_data):
    """Route invoice based on approval rules"""
    amount = invoice_data['total_amount']

    if amount < 1000:
        return {'approval_required': False, 'approver': None}
    elif amount < 5000:
        return {'approval_required': True, 'approver': 'manager@company.com'}
    elif amount < 25000:
        return {'approval_required': True, 'approver': 'director@company.com'}
    else:
        return {'approval_required': True, 'approver': 'cfo@company.com'}

def send_approval_notification(invoice_id, approver_email):
    """Send approval request email"""
    import smtplib
    from email.mime.text import MIMEText

    approval_link = f"https://your-app.com/approvals/{invoice_id}"

    msg = MIMEText(f"New invoice requires your approval: {approval_link}")
    msg['Subject'] = f"Invoice Approval Required: Invoice #{invoice_id}"
    msg['From'] = "noreply@company.com"
    msg['To'] = approver_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
```

## Integration Examples

All integration examples are available in the `integration-examples/` directory:

- [n8n Workflow](./integration-examples/n8n-workflow.json) - Visual no-code automation
- [Python Script](./integration-examples/python-complete.py) - Production-ready Python
- [Node.js Script](./integration-examples/nodejs-complete.js) - Express.js webhook server
- [AWS Lambda](./integration-examples/aws-lambda-quickbooks.py) - Serverless processing
- [Zapier Setup](./integration-examples/zapier-setup.md) - Step-by-step Zapier guide

## Performance Metrics

Based on 10,000+ invoices processed:

| Metric | Value |
|--------|-------|
| Accuracy | 98.7% field-level accuracy |
| Processing Time | 15-30 seconds per invoice |
| Cost Reduction | 79% vs manual processing |
| Error Rate | 1.3% requiring manual review |
| ROI Timeline | 3-6 months for mid-size companies |

## Common Edge Cases

### Multiple Pages

For multi-page invoices, concatenate pages or process individually:

```python
# Option 1: Combine images before processing
combined_image_url = merge_pdf_pages(page_urls)

# Option 2: Process each page separately and merge results
results = []
for page_url in page_urls:
    result = process_image(page_url)
    results.append(result)

merged_result = merge_invoice_results(results)
```

### Handwritten Invoices

Pattern handles handwritten text with reduced accuracy:

```json
{
  "instructions": "Extract invoice data. For handwritten fields, use best-effort OCR. If confidence is low, flag field for manual review."
}
```

### Non-English Invoices

Specify language in instructions:

```json
{
  "instructions": "Extract invoice data from Spanish-language invoices. Return field names in English but preserve original text values."
}
```

## Troubleshooting

### Issue: Incorrect Line Item Extraction

**Solution**: Improve instructions specificity:

```
Extract ALL line items from the invoice table, including:
- Line number (if present)
- Item description or service name
- Quantity (if not present, assume 1)
- Unit price
- Total amount for that line
Skip header rows and summary rows.
```

### Issue: Date Format Inconsistencies

**Solution**: Normalize dates in post-processing:

```python
from dateutil import parser

def normalize_date(date_string):
    """Parse various date formats to ISO format"""
    try:
        dt = parser.parse(date_string)
        return dt.strftime('%Y-%m-%d')
    except:
        return None
```

### Issue: Duplicate Processing

**Solution**: Use idempotency keys:

```python
import hashlib

def generate_idempotency_key(invoice_file):
    """Generate unique key based on file content"""
    file_hash = hashlib.sha256(invoice_file).hexdigest()
    return f"invoice-{file_hash[:16]}"

# Use in API call
response = requests.post(
    endpoint,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Idempotency-Key": generate_idempotency_key(file_data)
    },
    json={"image_url": url}
)
```

## Next Steps

- Set up [Webhooks](../../api-reference/webhooks.md) for real-time processing
- Integrate with [QuickBooks](../../integration-guides/quickbooks.md)
- Explore [n8n automation](../../automation-platforms/n8n)
- Review [error handling](../../api-reference/error-handling.md) best practices

---

**Related Use Cases**:

- [Receipt Management](../expense-management)
- [Document Classification](../document-classification)
