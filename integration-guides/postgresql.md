# PostgreSQL Integration Guide

Store extracted image data in PostgreSQL for powerful querying, analytics, and reporting.

## Why PostgreSQL?

- **ACID compliance**: Reliable transactions for financial data
- **JSON support**: Store complex nested structures
- **Full-text search**: Search extracted text fields
- **Scalability**: Handle millions of records
- **Rich ecosystem**: Works with BI tools, ORMs, frameworks

## Quick Start

### 1. Install PostgreSQL

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS**:

```bash
brew install postgresql
brew services start postgresql
```

**Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE imggo_data;

# Connect to new database
\c imggo_data

# Create user
CREATE USER imggo_app WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE imggo_data TO imggo_app;
```

## Schema Design

### Invoice Processing

```sql
-- Invoices table
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL,
    vendor_tax_id VARCHAR(50),
    vendor_address TEXT,
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
    image_url VARCHAR(500),
    raw_json JSONB,  -- Store full extracted data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Line items table
CREATE TABLE invoice_line_items (
    line_item_id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    line_number INTEGER,
    description TEXT NOT NULL,
    quantity DECIMAL(10,2),
    unit_price DECIMAL(15,2),
    amount DECIMAL(15,2) NOT NULL,
    tax_rate DECIMAL(5,2),
    account_code VARCHAR(50)
);

-- Indexes for performance
CREATE INDEX idx_invoices_vendor ON invoices(vendor_name);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_line_items_invoice ON invoice_line_items(invoice_id);

-- Full-text search index
CREATE INDEX idx_invoices_search ON invoices USING gin(to_tsvector('english', vendor_name || ' ' || COALESCE(po_number, '')));
```

### Retail Shelf Audit

```sql
-- Shelf audits table
CREATE TABLE shelf_audits (
    audit_id SERIAL PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL,
    aisle VARCHAR(100),
    category VARCHAR(100),
    audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_facings INTEGER,
    brand_facings INTEGER,
    brand_share_percent DECIMAL(5,2),
    out_of_stock_count INTEGER,
    compliance_percent DECIMAL(5,2),
    image_url VARCHAR(500),
    raw_json JSONB
);

-- Products detected table
CREATE TABLE shelf_products (
    product_id SERIAL PRIMARY KEY,
    audit_id INTEGER REFERENCES shelf_audits(audit_id) ON DELETE CASCADE,
    product_name VARCHAR(255),
    brand VARCHAR(100),
    sku VARCHAR(50),
    facing_count INTEGER,
    shelf_position VARCHAR(50),
    price_visible BOOLEAN,
    price DECIMAL(10,2),
    in_stock BOOLEAN
);

-- Indexes
CREATE INDEX idx_audits_store ON shelf_audits(store_id);
CREATE INDEX idx_audits_date ON shelf_audits(audit_date);
CREATE INDEX idx_products_brand ON shelf_products(brand);
CREATE INDEX idx_products_sku ON shelf_products(sku);
```

### Insurance Claims

```sql
-- Claims table
CREATE TABLE insurance_claims (
    claim_id VARCHAR(50) PRIMARY KEY,
    policy_number VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vehicle_make VARCHAR(100),
    vehicle_model VARCHAR(100),
    vehicle_year INTEGER,
    vin VARCHAR(17),
    total_estimated_cost DECIMAL(12,2),
    is_repairable BOOLEAN,
    decision_type VARCHAR(50),
    decision_reason TEXT,
    payout_amount DECIMAL(12,2),
    fraud_risk_score INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    raw_json JSONB
);

-- Damage details table
CREATE TABLE claim_damage_details (
    damage_id SERIAL PRIMARY KEY,
    claim_id VARCHAR(50) REFERENCES insurance_claims(claim_id),
    location VARCHAR(100),
    damage_type VARCHAR(100),
    severity VARCHAR(50),
    estimated_cost DECIMAL(10,2)
);

-- Photos table
CREATE TABLE claim_photos (
    photo_id SERIAL PRIMARY KEY,
    claim_id VARCHAR(50) REFERENCES insurance_claims(claim_id),
    photo_url VARCHAR(500),
    photo_angle VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_claims_policy ON insurance_claims(policy_number);
CREATE INDEX idx_claims_status ON insurance_claims(status);
CREATE INDEX idx_claims_date ON insurance_claims(assessment_date);
```

## Python Integration

### Using psycopg2

**Install**:

```bash
pip install psycopg2-binary
```

**Example**:

```python
import os
import psycopg2
from psycopg2.extras import Json
import requests

# Database connection
DB_URL = os.environ["DATABASE_URL"]
API_KEY = os.environ["IMGGO_API_KEY"]
PATTERN_ID = os.environ["IMGGO_PATTERN_ID"]

def store_invoice(invoice_data):
    """Store extracted invoice data in PostgreSQL"""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    try:
        # Insert invoice header
        cur.execute("""
            INSERT INTO invoices (
                vendor_name, vendor_tax_id, vendor_address,
                invoice_number, po_number, invoice_date, due_date,
                subtotal, tax_total, discount, shipping, total_amount,
                currency, payment_terms, raw_json
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING invoice_id
        """, (
            invoice_data['vendor']['name'],
            invoice_data['vendor'].get('tax_id'),
            invoice_data['vendor'].get('address'),
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
            Json(invoice_data)  # Store full JSON
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
                item['description'],
                item.get('quantity'),
                item.get('unit_price'),
                item['amount'],
                item.get('tax_rate')
            ))

        conn.commit()
        return invoice_id

    except Exception as e:
        conn.rollback()
        print(f"Error storing invoice: {e}")
        raise

    finally:
        cur.close()
        conn.close()

# Process and store
def process_and_store(image_url):
    """Complete workflow: process image and store in database"""

    # Process with ImgGo
    response = requests.post(
        f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"image_url": image_url}
    )

    job_id = response.json()["data"]["job_id"]

    # Poll for results
    result = poll_job_result(job_id)

    # Store in PostgreSQL
    invoice_id = store_invoice(result)

    print(f"Stored invoice {invoice_id}: {result['invoice_number']}")

    return invoice_id
```

### Using SQLAlchemy ORM

**Install**:

```bash
pip install sqlalchemy
```

**Models**:

```python
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, Text, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

Base = declarative_base()

class Invoice(Base):
    __tablename__ = 'invoices'

    invoice_id = Column(Integer, primary_key=True)
    vendor_name = Column(String(255), nullable=False)
    vendor_tax_id = Column(String(50))
    invoice_number = Column(String(100), unique=True, nullable=False)
    po_number = Column(String(100))
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date)
    subtotal = Column(Numeric(15, 2))
    tax_total = Column(Numeric(15, 2))
    total_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default='USD')
    status = Column(String(50), default='pending')
    raw_json = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    line_items = relationship('InvoiceLineItem', back_populates='invoice', cascade='all, delete-orphan')

class InvoiceLineItem(Base):
    __tablename__ = 'invoice_line_items'

    line_item_id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.invoice_id'), nullable=False)
    line_number = Column(Integer)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(10, 2))
    unit_price = Column(Numeric(15, 2))
    amount = Column(Numeric(15, 2), nullable=False)

    invoice = relationship('Invoice', back_populates='line_items')

# Create engine and session
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)

# Usage
def store_invoice_orm(invoice_data):
    """Store invoice using SQLAlchemy ORM"""
    session = Session()

    try:
        # Create invoice object
        invoice = Invoice(
            vendor_name=invoice_data['vendor']['name'],
            vendor_tax_id=invoice_data['vendor'].get('tax_id'),
            invoice_number=invoice_data['invoice_number'],
            po_number=invoice_data.get('po_number'),
            invoice_date=invoice_data['invoice_date'],
            due_date=invoice_data.get('due_date'),
            subtotal=invoice_data.get('subtotal'),
            tax_total=invoice_data.get('tax_total'),
            total_amount=invoice_data['total_amount'],
            currency=invoice_data.get('currency', 'USD'),
            raw_json=invoice_data
        )

        # Add line items
        for idx, item in enumerate(invoice_data.get('line_items', [])):
            line_item = InvoiceLineItem(
                line_number=idx + 1,
                description=item['description'],
                quantity=item.get('quantity'),
                unit_price=item.get('unit_price'),
                amount=item['amount']
            )
            invoice.line_items.append(line_item)

        # Save to database
        session.add(invoice)
        session.commit()

        return invoice.invoice_id

    except Exception as e:
        session.rollback()
        raise

    finally:
        session.close()
```

## Node.js Integration

### Using pg (node-postgres)

**Install**:

```bash
npm install pg
```

**Example**:

```javascript
const { Pool } = require('pg');
const axios = require('axios');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

async function storeInvoice(invoiceData) {
  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    // Insert invoice
    const invoiceResult = await client.query(`
      INSERT INTO invoices (
        vendor_name, invoice_number, invoice_date,
        total_amount, currency, raw_json
      ) VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING invoice_id
    `, [
      invoiceData.vendor.name,
      invoiceData.invoice_number,
      invoiceData.invoice_date,
      invoiceData.total_amount,
      invoiceData.currency || 'USD',
      JSON.stringify(invoiceData)
    ]);

    const invoiceId = invoiceResult.rows[0].invoice_id;

    // Insert line items
    for (const [index, item] of (invoiceData.line_items || []).entries()) {
      await client.query(`
        INSERT INTO invoice_line_items (
          invoice_id, line_number, description, amount
        ) VALUES ($1, $2, $3, $4)
      `, [invoiceId, index + 1, item.description, item.amount]);
    }

    await client.query('COMMIT');

    return invoiceId;

  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

// Usage
async function processAndStore(imageUrl) {
  // Process with ImgGo
  const response = await axios.post(
    `https://img-go.com/api/patterns/${process.env.IMGGO_PATTERN_ID}/ingest`,
    { image_url: imageUrl },
    {
      headers: {
        'Authorization': `Bearer ${process.env.IMGGO_API_KEY}`
      }
    }
  );

  const jobId = response.data.data.job_id;

  // Poll for results
  const result = await pollJobResult(jobId);

  // Store in PostgreSQL
  const invoiceId = await storeInvoice(result);

  console.log(`Stored invoice ${invoiceId}`);

  return invoiceId;
}
```

## Advanced Queries

### JSON Queries

```sql
-- Query nested JSON data
SELECT
    invoice_number,
    raw_json->>'vendor_name' AS vendor,
    raw_json->'line_items'->0->>'description' AS first_item,
    (raw_json->'line_items'->0->>'amount')::DECIMAL AS first_item_amount
FROM invoices
WHERE raw_json->>'currency' = 'USD';

-- Array length
SELECT
    invoice_number,
    jsonb_array_length(raw_json->'line_items') AS item_count
FROM invoices
WHERE jsonb_array_length(raw_json->'line_items') > 5;
```

### Analytics Queries

```sql
-- Top vendors by total amount
SELECT
    vendor_name,
    COUNT(*) AS invoice_count,
    SUM(total_amount) AS total_spent
FROM invoices
WHERE invoice_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY vendor_name
ORDER BY total_spent DESC
LIMIT 10;

-- Monthly invoice trends
SELECT
    DATE_TRUNC('month', invoice_date) AS month,
    COUNT(*) AS invoice_count,
    SUM(total_amount) AS total_amount,
    AVG(total_amount) AS avg_amount
FROM invoices
WHERE invoice_date >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY DATE_TRUNC('month', invoice_date)
ORDER BY month;

-- Shelf audit trends
SELECT
    store_id,
    AVG(brand_share_percent) AS avg_brand_share,
    AVG(out_of_stock_count) AS avg_oos
FROM shelf_audits
WHERE audit_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY store_id
ORDER BY avg_brand_share DESC;
```

## Performance Optimization

### Connection Pooling

```python
from psycopg2 import pool

# Create connection pool
connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    dsn=DATABASE_URL
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)

# Usage
conn = get_connection()
try:
    # Use connection
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices")
finally:
    release_connection(conn)
```

### Batch Inserts

```python
from psycopg2.extras import execute_values

def batch_insert_invoices(invoices):
    """Efficiently insert multiple invoices"""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # Prepare data
    invoice_data = [
        (
            inv['vendor_name'],
            inv['invoice_number'],
            inv['total_amount'],
            Json(inv)
        )
        for inv in invoices
    ]

    # Batch insert
    execute_values(
        cur,
        """
        INSERT INTO invoices (vendor_name, invoice_number, total_amount, raw_json)
        VALUES %s
        """,
        invoice_data
    )

    conn.commit()
    cur.close()
    conn.close()
```

## Backup & Maintenance

```bash
# Backup database
pg_dump -U imggo_app imggo_data > backup.sql

# Restore database
psql -U imggo_app imggo_data < backup.sql

# Vacuum (reclaim space)
VACUUM ANALYZE invoices;

# Reindex
REINDEX TABLE invoices;
```

## Next Steps

- Set up [MongoDB](./mongodb.md) for flexible schema
- Integrate with [Google Sheets](./google-sheets.md) for business users
- Connect to [Salesforce](./salesforce.md) for CRM workflows
