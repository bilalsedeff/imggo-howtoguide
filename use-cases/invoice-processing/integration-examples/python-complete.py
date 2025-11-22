"""
Complete Invoice Processing Workflow - Python
Handles: Email → CDN Upload → ImgGo Processing → PostgreSQL → Validation
"""

import os
import imaplib
import email
from email.header import decode_header
import requests
import psycopg2
from psycopg2.extras import Json
import time
from datetime import datetime
import hashlib
import smtplib
from email.mime.text import MIMEText

# Configuration
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
IMGGO_API_KEY = os.environ["IMGGO_API_KEY"]
IMGGO_PATTERN_ID = os.environ["IMGGO_PATTERN_ID"]
DB_CONNECTION = os.environ["DATABASE_URL"]
CDN_UPLOAD_ENDPOINT = os.environ.get("CDN_UPLOAD_ENDPOINT", "")


class InvoiceProcessor:
    """Production-ready invoice processing pipeline"""

    def __init__(self):
        self.processed_count = 0
        self.error_count = 0

    def run(self):
        """Main processing loop"""
        print("Starting invoice processing...")

        # Connect to Gmail
        invoices = self.fetch_invoice_emails()
        print(f"Found {len(invoices)} new invoices")

        # Process each invoice
        for invoice in invoices:
            try:
                self.process_invoice(invoice)
                self.processed_count += 1
            except Exception as e:
                print(f"Error processing invoice: {e}")
                self.error_count += 1
                self.log_error(invoice, str(e))

        print(f"\nProcessing complete!")
        print(f"Processed: {self.processed_count}")
        print(f"Errors: {self.error_count}")

    def fetch_invoice_emails(self):
        """Fetch unread emails with invoice attachments"""
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(GMAIL_USER, GMAIL_PASSWORD)
        imap.select("INBOX")

        # Search for unread emails with "invoice" in subject
        status, messages = imap.search(None, '(UNSEEN SUBJECT "invoice")')

        invoice_emails = []

        for num in messages[0].split():
            status, msg_data = imap.fetch(num, "(RFC822)")
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)

            # Extract subject and sender
            subject = decode_header(email_message["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            sender = email_message.get("From")

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
                        'data': part.get_payload(decode=True),
                        'subject': subject,
                        'sender': sender,
                        'email_id': num.decode()
                    })

        imap.close()
        imap.logout()

        return invoice_emails

    def process_invoice(self, invoice_email):
        """Complete invoice processing workflow"""

        print(f"\nProcessing: {invoice_email['filename']}")

        # 1. Upload to CDN
        image_url = self.upload_to_cdn(
            invoice_email['data'],
            invoice_email['filename']
        )

        # 2. Process with ImgGo
        job_id = self.submit_to_imggo(image_url)

        # 3. Poll for results
        result = self.poll_job_result(job_id)

        # 4. Validate data
        validation = self.validate_invoice(result)

        if not validation['is_valid']:
            print(f"Validation failed: {validation['errors']}")
            self.flag_for_review(result, validation['errors'])
            return

        # 5. Check for duplicates
        if self.is_duplicate(result['invoice_number']):
            print(f"Duplicate invoice: {result['invoice_number']}")
            return

        # 6. Store in database
        invoice_id = self.store_in_database(result, image_url)

        # 7. Route for approval if needed
        approval = self.route_for_approval(result)

        if approval['approval_required']:
            self.send_approval_request(invoice_id, approval['approver'])

        print(f"✓ Stored invoice {invoice_id}: {result['invoice_number']}")

    def upload_to_cdn(self, file_data, filename):
        """Upload file to CDN and return public URL"""

        if not CDN_UPLOAD_ENDPOINT:
            # Fallback: save locally and use local path
            local_path = f"/tmp/invoices/{filename}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(file_data)
            return f"file://{local_path}"

        # Upload to CDN (example with S3-compatible storage)
        files = {'file': (filename, file_data)}
        response = requests.post(
            CDN_UPLOAD_ENDPOINT,
            files=files,
            headers={'Authorization': f"Bearer {os.environ.get('CDN_API_KEY')}"}
        )

        response.raise_for_status()
        return response.json()['url']

    def submit_to_imggo(self, image_url):
        """Submit image to ImgGo for processing"""

        # Generate idempotency key
        idempotency_key = hashlib.sha256(image_url.encode()).hexdigest()[:16]

        response = requests.post(
            f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
            headers={
                "Authorization": f"Bearer {IMGGO_API_KEY}",
                "Idempotency-Key": idempotency_key
            },
            json={"image_url": image_url}
        )

        response.raise_for_status()
        return response.json()["data"]["job_id"]

    def poll_job_result(self, job_id, max_attempts=30):
        """Poll for job completion"""

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

    def validate_invoice(self, data):
        """Validate extracted invoice data"""
        errors = []

        # Required fields
        required_fields = ['vendor', 'invoice_number', 'total_amount', 'invoice_date']
        for field in required_fields:
            if field == 'vendor':
                if not data.get('vendor', {}).get('name'):
                    errors.append(f"Missing vendor name")
            elif not data.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate total matches line items
        if data.get('line_items'):
            calculated_subtotal = sum(
                float(item.get('amount', 0))
                for item in data['line_items']
            )

            if abs(calculated_subtotal - float(data.get('subtotal', 0))) > 0.01:
                errors.append(
                    f"Subtotal mismatch: {calculated_subtotal} vs {data['subtotal']}"
                )

        # Validate total calculation
        expected_total = (
            float(data.get('subtotal', 0)) +
            float(data.get('tax_total', 0)) -
            float(data.get('discount', 0)) +
            float(data.get('shipping', 0))
        )

        if abs(expected_total - float(data.get('total_amount', 0))) > 0.01:
            errors.append(
                f"Total mismatch: expected {expected_total}, got {data['total_amount']}"
            )

        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

    def is_duplicate(self, invoice_number):
        """Check if invoice already exists"""
        conn = psycopg2.connect(DB_CONNECTION)
        cur = conn.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM invoices WHERE invoice_number = %s",
            (invoice_number,)
        )

        count = cur.fetchone()[0]
        cur.close()
        conn.close()

        return count > 0

    def store_in_database(self, invoice_data, image_url):
        """Store invoice in PostgreSQL"""
        conn = psycopg2.connect(DB_CONNECTION)
        cur = conn.cursor()

        try:
            # Insert invoice header
            cur.execute("""
                INSERT INTO invoices (
                    vendor_name, vendor_tax_id, invoice_number, po_number,
                    invoice_date, due_date, subtotal, tax_total,
                    discount, shipping, total_amount, currency,
                    payment_terms, image_url, raw_json, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING invoice_id
            """, (
                invoice_data.get('vendor', {}).get('name'),
                invoice_data.get('vendor', {}).get('tax_id'),
                invoice_data['invoice_number'],
                invoice_data.get('po_number'),
                invoice_data['invoice_date'],
                invoice_data.get('due_date'),
                invoice_data.get('subtotal'),
                invoice_data.get('tax_total'),
                invoice_data.get('discount'),
                invoice_data.get('shipping'),
                invoice_data['total_amount'],
                invoice_data.get('currency', 'USD'),
                invoice_data.get('payment_terms'),
                image_url,
                Json(invoice_data),
                datetime.now()
            ))

            invoice_id = cur.fetchone()[0]

            # Insert line items
            for idx, item in enumerate(invoice_data.get('line_items', [])):
                cur.execute("""
                    INSERT INTO invoice_line_items (
                        invoice_id, line_number, description,
                        quantity, unit_price, amount, tax_rate
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    invoice_id,
                    idx + 1,
                    item.get('description'),
                    item.get('quantity'),
                    item.get('unit_price'),
                    item.get('amount'),
                    item.get('tax_rate')
                ))

            conn.commit()
            return invoice_id

        except Exception as e:
            conn.rollback()
            raise

        finally:
            cur.close()
            conn.close()

    def route_for_approval(self, invoice_data):
        """Determine if approval is needed and who should approve"""
        amount = float(invoice_data['total_amount'])

        if amount < 1000:
            return {'approval_required': False, 'approver': None}
        elif amount < 5000:
            return {'approval_required': True, 'approver': 'manager@company.com'}
        elif amount < 25000:
            return {'approval_required': True, 'approver': 'director@company.com'}
        else:
            return {'approval_required': True, 'approver': 'cfo@company.com'}

    def send_approval_request(self, invoice_id, approver_email):
        """Send approval request email"""
        approval_link = f"https://your-app.com/approvals/{invoice_id}"

        msg = MIMEText(f"""
        New invoice requires your approval:

        Invoice ID: {invoice_id}

        Please review and approve/reject:
        {approval_link}
        """)

        msg['Subject'] = f"Invoice Approval Required: #{invoice_id}"
        msg['From'] = "noreply@company.com"
        msg['To'] = approver_email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)

    def flag_for_review(self, invoice_data, errors):
        """Flag invoice for manual review"""
        conn = psycopg2.connect(DB_CONNECTION)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO invoice_review_queue (
                invoice_number, vendor_name, errors, raw_data, created_at
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            invoice_data.get('invoice_number', 'UNKNOWN'),
            invoice_data.get('vendor', {}).get('name', 'UNKNOWN'),
            Json(errors),
            Json(invoice_data),
            datetime.now()
        ))

        conn.commit()
        cur.close()
        conn.close()

    def log_error(self, invoice_email, error_message):
        """Log processing errors"""
        with open('invoice_processing_errors.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {invoice_email.get('filename', 'UNKNOWN')}: {error_message}\n")


if __name__ == "__main__":
    processor = InvoiceProcessor()
    processor.run()
