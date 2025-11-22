# Retail Shelf Audit Automation

Automate in-store shelf monitoring with computer vision: track stock levels, planogram compliance, shelf share, and competitor pricing in real-time.

## Business Problem

Retail brands spend millions on field teams manually auditing shelves:

- **Labor-intensive**: 20-50 minutes per store audit
- **Subjective**: Inconsistent reporting between auditors
- **Delayed insights**: Days or weeks between audit and action
- **Limited coverage**: Can't audit all stores frequently
- **Lost revenue**: Out-of-stocks cost retailers $1 trillion annually

**Traditional approach**: Field reps visit stores, take photos, manually count products, fill forms.

## Solution

Automated shelf audit with image recognition:

1. **Capture**: Rep takes shelf photo with mobile app
2. **Upload**: Photo automatically uploads via API
3. **Extract**: AI identifies products, pricing, placement
4. **Analyze**: System calculates share of shelf, compliance, gaps
5. **Alert**: Real-time notifications for out-of-stocks or compliance issues
6. **Report**: Dashboard shows trends across stores/regions

**Result**: 80% time reduction, real-time insights, 100% consistency.

## What Gets Extracted

### Shelf Audit Schema

```json
{
  "store_id": "string",
  "aisle": "string",
  "category": "string",
  "audit_timestamp": "datetime",
  "products": [
    {
      "product_name": "string",
      "brand": "string",
      "sku": "string",
      "facing_count": "number",
      "shelf_position": "string",
      "price_tag_visible": "boolean",
      "price": "number",
      "in_stock": "boolean",
      "planogram_compliant": "boolean",
      "product_condition": "string"
    }
  ],
  "analytics": {
    "total_facings": "number",
    "your_brand_facings": "number",
    "your_brand_share_percent": "number",
    "competitor_brands": ["string"],
    "out_of_stock_count": "number",
    "planogram_compliance_percent": "number"
  }
}
```

## Pattern Setup

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Retail Shelf Audit - Beverage Category",
    "output_format": "json",
    "instructions": "Identify all products visible on the retail shelf from left to right, top to bottom. For each product extract: product name, brand, number of facings (how many units are visible), shelf position (shelf number and position like Top-Left, Middle-Center), whether price tag is visible, the price if visible, stock status (in-stock or out-of-stock). Calculate total facings, our brand share percentage, and list all competitor brands present. Identify any planogram violations.",
    "schema": {
      "products": [
        {
          "product_name": "string",
          "brand": "string",
          "sku": "string",
          "facing_count": "number",
          "shelf_position": "string",
          "price_tag_visible": "boolean",
          "price": "number",
          "in_stock": "boolean"
        }
      ],
      "analytics": {
        "total_facings": "number",
        "your_brand_facings": "number",
        "your_brand_share_percent": "number",
        "out_of_stock_count": "number"
      }
    }
  }'
```

## End-to-End Workflow: Mobile App → API → Power BI

### Architecture

```
Mobile App (React Native) → ImgGo API → PostgreSQL → Power BI Dashboard
                             ↓
                     Real-time Alerts (Twilio SMS)
```

### Mobile App Integration

**React Native component for shelf capture**:

```javascript
// ShelfAuditScreen.js
import React, { useState } from 'react';
import { Camera } from 'expo-camera';
import * as FileSystem from 'expo-file-system';
import axios from 'axios';

const ShelfAuditScreen = () => {
  const [processing, setProcessing] = useState(false);

  const captureAndProcess = async (camera) => {
    setProcessing(true);

    // Capture photo
    const photo = await camera.takePictureAsync({
      quality: 0.8,
      base64: false
    });

    // Upload to your CDN
    const uploadUrl = await uploadToCDN(photo.uri);

    // Process with ImgGo
    const result = await processShelf(uploadUrl, {
      store_id: globalState.currentStore,
      aisle: globalState.currentAisle,
      category: globalState.currentCategory
    });

    // Save to database
    await saveAuditResult(result);

    // Show results
    navigation.navigate('AuditResults', { data: result });

    setProcessing(false);
  };

  const processShelf = async (imageUrl, metadata) => {
    try {
      // Submit job
      const submitResponse = await axios.post(
        `https://img-go.com/api/patterns/${PATTERN_ID}/ingest`,
        {
          image_url: imageUrl,
          metadata: metadata
        },
        {
          headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Idempotency-Key': `audit-${Date.now()}`
          }
        }
      );

      const jobId = submitResponse.data.data.job_id;

      // Poll for result
      return await pollJobResult(jobId);
    } catch (error) {
      console.error('Processing error:', error);
      throw error;
    }
  };

  const pollJobResult = async (jobId) => {
    let attempts = 0;
    const maxAttempts = 30;

    while (attempts < maxAttempts) {
      const response = await axios.get(
        `https://img-go.com/api/jobs/${jobId}`,
        {
          headers: { 'Authorization': `Bearer ${API_KEY}` }
        }
      );

      const status = response.data.data.status;

      if (status === 'completed') {
        return response.data.data.result;
      } else if (status === 'failed') {
        throw new Error('Processing failed');
      }

      await new Promise(resolve => setTimeout(resolve, 2000));
      attempts++;
    }

    throw new Error('Polling timeout');
  };

  return (
    <View style={styles.container}>
      <Camera ref={ref => setCamera(ref)} style={styles.camera}>
        <Button
          title={processing ? "Processing..." : "Capture Shelf"}
          onPress={() => captureAndProcess(camera)}
          disabled={processing}
        />
      </Camera>
    </View>
  );
};
```

### Backend Processing & Alerts

```python
import os
import requests
import psycopg2
from twilio.rest import Client

API_KEY = os.environ["IMGGO_API_KEY"]
DB_URL = os.environ["DATABASE_URL"]
TWILIO_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_FROM = os.environ["TWILIO_PHONE_NUMBER"]

def save_audit_to_database(audit_data, metadata):
    """Store shelf audit in PostgreSQL"""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # Insert audit record
    cur.execute("""
        INSERT INTO shelf_audits (
            store_id, aisle, category, audit_date,
            total_facings, brand_facings, brand_share_percent,
            out_of_stock_count, compliance_percent
        ) VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)
        RETURNING audit_id
    """, (
        metadata['store_id'],
        metadata['aisle'],
        metadata['category'],
        audit_data['analytics']['total_facings'],
        audit_data['analytics']['your_brand_facings'],
        audit_data['analytics']['your_brand_share_percent'],
        audit_data['analytics']['out_of_stock_count'],
        audit_data['analytics'].get('planogram_compliance_percent', 0)
    ))

    audit_id = cur.fetchone()[0]

    # Insert product details
    for product in audit_data['products']:
        cur.execute("""
            INSERT INTO shelf_products (
                audit_id, product_name, brand, sku, facing_count,
                shelf_position, price_visible, price, in_stock
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            audit_id,
            product['product_name'],
            product['brand'],
            product.get('sku'),
            product['facing_count'],
            product['shelf_position'],
            product['price_tag_visible'],
            product.get('price'),
            product['in_stock']
        ))

    conn.commit()
    cur.close()
    conn.close()

    # Check for alerts
    check_and_send_alerts(audit_id, audit_data, metadata)

    return audit_id

def check_and_send_alerts(audit_id, audit_data, metadata):
    """Send alerts for critical issues"""
    analytics = audit_data['analytics']

    alerts = []

    # Low shelf share alert
    if analytics['your_brand_share_percent'] < 30:
        alerts.append(f"LOW SHELF SHARE: Only {analytics['your_brand_share_percent']:.1f}% at {metadata['store_id']}")

    # Out of stock alert
    if analytics['out_of_stock_count'] > 0:
        alerts.append(f"OUT OF STOCK: {analytics['out_of_stock_count']} products at {metadata['store_id']}")

    # Planogram compliance alert
    if analytics.get('planogram_compliance_percent', 100) < 80:
        alerts.append(f"COMPLIANCE ISSUE: {analytics['planogram_compliance_percent']:.1f}% compliance at {metadata['store_id']}")

    # Send alerts via SMS
    if alerts:
        send_sms_alerts(alerts, metadata['store_id'])

def send_sms_alerts(alerts, store_id):
    """Send SMS alerts via Twilio"""
    client = Client(TWILIO_SID, TWILIO_TOKEN)

    message_body = f"Store {store_id} Alerts:\n" + "\n".join(alerts)

    # Get store manager phone from database
    manager_phone = get_store_manager_phone(store_id)

    message = client.messages.create(
        body=message_body,
        from_=TWILIO_FROM,
        to=manager_phone
    )

    print(f"Alert sent: {message.sid}")
```

### Database Schema

```sql
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
    image_url VARCHAR(500)
);

CREATE TABLE shelf_products (
    product_id SERIAL PRIMARY KEY,
    audit_id INTEGER REFERENCES shelf_audits(audit_id),
    product_name VARCHAR(255),
    brand VARCHAR(100),
    sku VARCHAR(50),
    facing_count INTEGER,
    shelf_position VARCHAR(50),
    price_visible BOOLEAN,
    price DECIMAL(10,2),
    in_stock BOOLEAN
);

CREATE INDEX idx_audits_store ON shelf_audits(store_id);
CREATE INDEX idx_audits_date ON shelf_audits(audit_date);
CREATE INDEX idx_products_brand ON shelf_products(brand);
```

## Analytics & Reporting

### Power BI Integration

**DAX Measures for dashboard**:

```dax
// Average Shelf Share by Region
Avg Shelf Share =
AVERAGE(shelf_audits[brand_share_percent])

// Out of Stock Trend
OOS Trend =
CALCULATE(
    SUM(shelf_audits[out_of_stock_count]),
    DATESINPERIOD(shelf_audits[audit_date], MAX(shelf_audits[audit_date]), -30, DAY)
)

// Compliance Score
Compliance Score =
AVERAGEX(
    shelf_audits,
    shelf_audits[compliance_percent]
)

// Store Ranking by Shelf Share
Store Rank =
RANKX(
    ALL(shelf_audits[store_id]),
    [Avg Shelf Share],
    ,
    DESC,
    DENSE
)
```

## Use Cases by Industry

### CPG Brands (Coca-Cola, Unilever, P&G)

- **Objective**: Maximize shelf share, ensure planogram compliance
- **Frequency**: Weekly audits across 10,000+ retail locations
- **KPIs**: Shelf share %, distribution %, out-of-stock rate

### Retail Chains (Walmart, Target, Kroger)

- **Objective**: Inventory accuracy, reduce out-of-stocks
- **Frequency**: Daily automated checks via store staff
- **KPIs**: Stock availability, inventory turnover, shrinkage

### Field Marketing Agencies

- **Objective**: Execute merchandising programs for multiple brands
- **Frequency**: Daily store visits
- **KPIs**: Compliance rate, execution speed, coverage

## Performance Metrics

| Metric | Before Automation | After Automation |
|--------|-------------------|------------------|
| Audit Time | 30 min/store | 3 min/store |
| Accuracy | 75-85% | 98%+ |
| Coverage | 20% of stores weekly | 100% of stores weekly |
| Time to Insight | 3-7 days | Real-time |
| Cost per Audit | $25 | $3 |

## Advanced Features

### Competitor Price Monitoring

Extract competitor prices for price intelligence:

```json
{
  "products": [
    {
      "product_name": "Coca-Cola 2L",
      "brand": "Coca-Cola",
      "price": 2.99
    },
    {
      "product_name": "Pepsi 2L",
      "brand": "Pepsi",
      "price": 2.79
    }
  ]
}
```

### Planogram Comparison

Compare actual shelf vs ideal planogram:

```python
def compare_to_planogram(audit_data, planogram):
    """Compare actual shelf to planogram"""
    actual_positions = {p['sku']: p['shelf_position'] for p in audit_data['products']}
    expected_positions = {p['sku']: p['position'] for p in planogram['products']}

    violations = []

    for sku, expected_pos in expected_positions.items():
        actual_pos = actual_positions.get(sku)

        if not actual_pos:
            violations.append(f"SKU {sku} missing from shelf")
        elif actual_pos != expected_pos:
            violations.append(f"SKU {sku} in wrong position: {actual_pos} (expected {expected_pos})")

    compliance_rate = (1 - len(violations) / len(expected_positions)) * 100

    return {
        'compliance_rate': compliance_rate,
        'violations': violations
    }
```

## Integration Examples

- [n8n Workflow](./integration-examples/n8n-workflow.json) - Mobile upload → processing → database
- [Python Mobile Backend](./integration-examples/python-mobile-backend.py) - Flask API for mobile apps
- [Power BI Integration](./integration-examples/powerbi-connector.py) - Real-time dashboard data

## Troubleshooting

### Issue: Products Not Detected

**Causes**:
- Poor lighting or image quality
- Products too far from camera
- Obscured labels

**Solutions**:
- Use good lighting (avoid glare)
- Capture from 3-5 feet distance
- Take multiple angles if needed
- Improve pattern instructions

### Issue: Incorrect Facing Counts

**Solution**: Add specific counting instructions:

```
Count the number of visible product facings (individual units visible from the front). If products are stacked, count only the front-facing row. For multi-packs, count each multi-pack as one facing.
```

## Next Steps

- Explore [Inventory Management](../inventory-management) for warehouse applications
- Set up [Real-time Webhooks](../../api-reference/webhooks.md)
- Build [Mobile Apps](../../examples/react-native)

---

**ROI Calculator**: A store with 1,000 weekly audits saves $22,000/month with automation.
