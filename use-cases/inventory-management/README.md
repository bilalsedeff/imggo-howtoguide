# Automated Inventory Management and Cycle Counting

## Overview

Automate inventory counting and stock monitoring by extracting product data from warehouse shelf photos and converting them into **CSV spreadsheets** for easy import into inventory management systems. Eliminate manual counting errors and update stock levels in real-time.

**Output Format**: CSV (universal format for spreadsheets and ERP systems)
**Upload Method**: URL Processing (from warehouse cameras, mobile photos in cloud storage)
**Industry**: Retail, Warehousing, Manufacturing, Distribution, E-commerce

---

## The Problem

Warehouse and retail operations face these inventory challenges:

- **Labor-Intensive Counting**: Manual cycle counts take 40+ hours per month in medium warehouses
- **Counting Errors**: Human error rate of 3-5% leads to stockouts and overstocking
- **Delayed Updates**: Inventory systems lag actual stock by days or weeks
- **Shrinkage**: 30% of shrinkage goes undetected between annual physical counts
- **Order Fulfillment**: Out-of-stock items delay 15-20% of customer orders
- **Capital Waste**: $1.1 trillion in excess inventory held globally due to inaccurate counts

Traditional cycle counting requires staff with clipboards or barcode scanners walking aisles for hours, disrupting operations and still missing discrepancies.

---

## The Solution

ImgGo extracts product counts, SKUs, and location data from shelf photos and outputs **CSV files** that directly import into inventory management systems:

**Workflow**:

```plaintext
Warehouse Photo (URL) → ImgGo API → CSV Output → ERP/WMS Import
```

**What Gets Extracted**:

- Product SKUs and descriptions
- Quantities on shelf
- Location (aisle, bin, shelf)
- Product conditions
- Expiration dates (if visible)
- Pricing discrepancies
- Empty/low stock alerts

---

## Why CSV Output?

CSV is the universal format for inventory data:

- **Universal Compatibility**: Every ERP, WMS, and spreadsheet tool accepts CSV imports
- **Bulk Updates**: Import thousands of SKUs in seconds
- **Audit Trail**: CSV files serve as snapshot records for compliance
- **Easy Validation**: Review in Excel/Google Sheets before importing to ERP
- **Legacy Systems**: Works with decades-old inventory systems that don't support APIs
- **No Transformation**: Direct mapping to inventory system fields

**Example Output (inventory_count_2025-01-22.csv)**:

```csv
Location,SKU,Product_Description,Quantity_Counted,Unit_Price,Total_Value,Condition,Expiration_Date,Last_Updated,Count_Confidence
A-12-3,SKU-100234,Premium Coffee Beans 1lb,47,12.99,610.53,Good,,2025-01-22T14:30:00Z,0.98
A-12-3,SKU-100235,Organic Tea Bags 50ct,23,8.49,195.27,Good,2025-12-31,2025-01-22T14:30:00Z,0.95
A-12-4,SKU-100236,Gourmet Cookies 12oz,0,5.99,0.00,Out of Stock,,2025-01-22T14:30:00Z,1.00
A-12-4,SKU-100237,Dark Chocolate Bar 3.5oz,156,3.49,544.44,Good,2025-08-15,2025-01-22T14:30:00Z,0.97
A-12-5,SKU-100238,Mixed Nuts 16oz,34,9.99,339.66,Good,2025-06-30,2025-01-22T14:30:00Z,0.96
A-12-5,SKU-100239,Dried Fruit Mix 12oz,12,7.49,89.88,Damaged,2025-05-20,2025-01-22T14:30:00Z,0.92
A-12-6,SKU-100240,Protein Bars Box of 12,89,24.99,2224.11,Good,2025-10-10,2025-01-22T14:30:00Z,0.98
```

---

## Implementation Guide

### Step 1: Create Inventory Counting Pattern

Define the CSV schema for inventory extraction:

```bash
POST https://img-go.com/api/patterns
Authorization: Bearer YOUR_API_KEY

{
  "name": "Warehouse Inventory Counter",
  "output_format": "csv",
  "csv_headers": [
    "Location",
    "SKU",
    "Product_Description",
    "Quantity_Counted",
    "Unit_Price",
    "Total_Value",
    "Condition",
    "Expiration_Date",
    "Last_Updated",
    "Count_Confidence"
  ],
  "schema": {
    "items": [
      {
        "Location": "string",
        "SKU": "string",
        "Product_Description": "string",
        "Quantity_Counted": "number",
        "Unit_Price": "number",
        "Total_Value": "number",
        "Condition": "enum[Good,Damaged,Expired,Out of Stock]",
        "Expiration_Date": "date",
        "Last_Updated": "datetime",
        "Count_Confidence": "number"
      }
    ]
  }
}
```

### Step 2: Process Warehouse Photos from URLs

Most warehouses use fixed cameras or upload mobile photos to cloud storage:

```python
import requests
import pandas as pd
from datetime import datetime
import time

IMGGO_API_KEY = "your_api_key"
IMGGO_PATTERN_ID = "pat_inventory_counter_xyz"

def count_inventory_from_photo(image_url, location_code):
    """
    Process warehouse shelf photo from URL and return CSV data
    """
    # Submit to ImgGo
    response = requests.post(
        f"https://img-go.com/api/patterns/{IMGGO_PATTERN_ID}/ingest",
        headers={
            "Authorization": f"Bearer {IMGGO_API_KEY}",
            "Idempotency-Key": f"{location_code}-{datetime.now().isoformat()}"
        },
        json={
            "image_url": image_url,
            "context": {
                "location": location_code,
                "count_date": datetime.now().isoformat()
            }
        }
    )

    job_id = response.json()["data"]["job_id"]

    # Poll for results
    for _ in range(30):
        result = requests.get(
            f"https://img-go.com/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {IMGGO_API_KEY}"}
        ).json()

        if result["data"]["status"] == "completed":
            # Result is already in CSV format
            csv_output = result["data"]["result"]
            return csv_output
        elif result["data"]["status"] == "failed":
            raise Exception(f"Processing failed: {result['data'].get('error')}")

        time.sleep(2)

    raise Exception("Processing timeout")


# Example: Process from warehouse camera
camera_url = "https://s3.amazonaws.com/warehouse-cams/aisle-a/section-12/latest.jpg"
csv_data = count_inventory_from_photo(camera_url, "A-12")

# Save CSV file
with open(f"inventory_count_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv", "w") as f:
    f.write(csv_data)

# Load into pandas for analysis
df = pd.read_csv(f"inventory_count_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv")

# Identify out-of-stock items
out_of_stock = df[df['Quantity_Counted'] == 0]
print(f"Out of stock items: {len(out_of_stock)}")

# Identify low-stock items (< 10 units)
low_stock = df[(df['Quantity_Counted'] > 0) & (df['Quantity_Counted'] < 10)]
print(f"Low stock items: {len(low_stock)}")

# Calculate total inventory value
total_value = df['Total_Value'].sum()
print(f"Total inventory value: ${total_value:,.2f}")
```

### Step 3: Automated Cycle Counting

Schedule automated counts for different warehouse zones:

```python
import schedule
import pandas as pd
from io import StringIO

# Warehouse camera configuration
WAREHOUSE_CAMERAS = {
    "A-12": "https://s3.amazonaws.com/warehouse-cams/aisle-a/section-12/latest.jpg",
    "A-13": "https://s3.amazonaws.com/warehouse-cams/aisle-a/section-13/latest.jpg",
    "A-14": "https://s3.amazonaws.com/warehouse-cams/aisle-a/section-14/latest.jpg",
    "B-01": "https://s3.amazonaws.com/warehouse-cams/aisle-b/section-01/latest.jpg",
    "B-02": "https://s3.amazonaws.com/warehouse-cams/aisle-b/section-02/latest.jpg",
    # ... more locations
}

def perform_cycle_count(zone_ids):
    """
    Perform cycle count for specified zones
    """
    all_counts = []

    for zone_id in zone_ids:
        camera_url = WAREHOUSE_CAMERAS.get(zone_id)
        if not camera_url:
            print(f"Warning: No camera configured for {zone_id}")
            continue

        try:
            csv_data = count_inventory_from_photo(camera_url, zone_id)
            df = pd.read_csv(StringIO(csv_data))
            all_counts.append(df)

            print(f"Counted {len(df)} SKUs in {zone_id}")

        except Exception as e:
            print(f"Error counting {zone_id}: {e}")

    # Consolidate all counts
    if all_counts:
        consolidated = pd.concat(all_counts, ignore_index=True)

        # Save master CSV
        filename = f"cycle_count_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        consolidated.to_csv(filename, index=False)

        # Generate variance report
        variances = check_variances(consolidated)

        # Send alerts for critical variances
        if variances:
            send_variance_alerts(variances)

        return consolidated


def check_variances(count_df):
    """
    Compare counted quantities vs system quantities
    """
    # Fetch system quantities from ERP
    system_inventory = fetch_system_inventory(count_df['SKU'].tolist())

    # Merge and calculate variances
    merged = count_df.merge(
        system_inventory,
        on='SKU',
        suffixes=('_counted', '_system')
    )

    merged['Variance'] = merged['Quantity_Counted_counted'] - merged['Quantity_system']
    merged['Variance_Pct'] = (merged['Variance'] / merged['Quantity_system']) * 100

    # Flag significant variances (>10% or >$500)
    significant = merged[
        (abs(merged['Variance_Pct']) > 10) |
        (abs(merged['Variance'] * merged['Unit_Price']) > 500)
    ]

    return significant


# Schedule cycle counts
# Zone A: Daily at 6 PM
schedule.every().day.at("18:00").do(
    lambda: perform_cycle_count(["A-12", "A-13", "A-14"])
)

# Zone B: Every Monday, Wednesday, Friday at 7 PM
schedule.every().monday.at("19:00").do(
    lambda: perform_cycle_count(["B-01", "B-02"])
)
schedule.every().wednesday.at("19:00").do(
    lambda: perform_cycle_count(["B-01", "B-02"])
)
schedule.every().friday.at("19:00").do(
    lambda: perform_cycle_count(["B-01", "B-02"])
)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Step 4: Import to ERP System

Upload CSV counts directly to ERP (example: SAP Business One):

```python
import csv
import pymssql  # SAP Business One uses SQL Server

SAP_DB_CONFIG = {
    'server': 'sap-server.local',
    'database': 'SBO_Company',
    'user': 'sa',
    'password': os.environ['SAP_DB_PASSWORD']
}

def import_counts_to_sap(csv_file):
    """
    Import cycle count CSV to SAP Business One
    """
    conn = pymssql.connect(**SAP_DB_CONFIG)
    cursor = conn.cursor()

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            sku = row['SKU']
            location = row['Location']
            quantity_counted = int(row['Quantity_Counted'])

            # Get current system quantity
            cursor.execute("""
                SELECT OnHand, Committed, AvgPrice
                FROM OITW
                WHERE ItemCode = %s AND WhsCode = %s
            """, (sku, location))

            current = cursor.fetchone()

            if not current:
                print(f"Warning: SKU {sku} not found in system")
                continue

            system_qty = current[0]
            variance = quantity_counted - system_qty

            # Update inventory if variance exists
            if variance != 0:
                # Create inventory adjustment transaction
                cursor.execute("""
                    INSERT INTO OIGN (DocDate, DocDueDate, Comments, U_CountDate)
                    VALUES (GETDATE(), GETDATE(), %s, %s)
                """, (f"Cycle count adjustment - Camera count", row['Last_Updated']))

                doc_entry = cursor.lastrowid

                # Add line item
                cursor.execute("""
                    INSERT INTO IGN1 (DocEntry, ItemCode, Quantity, Price, WhsCode)
                    VALUES (%s, %s, %s, %s, %s)
                """, (doc_entry, sku, variance, current[2], location))

                print(f"Adjusted {sku}: {variance:+d} units (was {system_qty}, now {quantity_counted})")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Import complete from {csv_file}")


# Import latest cycle count
import_counts_to_sap("cycle_count_2025-01-22_18-00.csv")
```

---

## Integration Examples

### NetSuite Integration

```python
import requests
import csv

NETSUITE_ACCOUNT_ID = "your_account_id"
NETSUITE_TOKEN = os.environ['NETSUITE_TOKEN']

def sync_to_netsuite(csv_file):
    """
    Upload inventory counts to NetSuite via REST API
    """
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Create inventory adjustment
            adjustment = {
                "recordType": "inventoryadjustment",
                "fields": {
                    "subsidiary": "1",
                    "account": "115",  # Inventory adjustment account
                    "trandate": row['Last_Updated'],
                    "memo": f"Automated count - {row['Location']}"
                },
                "sublists": {
                    "inventory": {
                        "items": [{
                            "item": row['SKU'],
                            "location": row['Location'],
                            "adjustqtyby": row['Quantity_Counted']  # NetSuite calculates variance
                        }]
                    }
                }
            }

            response = requests.post(
                f"https://{NETSUITE_ACCOUNT_ID}.suitetalk.api.netsuite.com/services/rest/record/v1/inventoryadjustment",
                headers={
                    "Authorization": f"Bearer {NETSUITE_TOKEN}",
                    "Content-Type": "application/json"
                },
                json=adjustment
            )

            if response.status_code == 200:
                print(f"Created NetSuite adjustment: {row['SKU']}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
```

### Shopify Integration

Sync warehouse counts to Shopify inventory levels:

```python
import shopify
import csv

SHOPIFY_SHOP_URL = "your-store.myshopify.com"
SHOPIFY_API_KEY = os.environ['SHOPIFY_API_KEY']
SHOPIFY_PASSWORD = os.environ['SHOPIFY_PASSWORD']

shopify.ShopifyResource.set_site(f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOPIFY_SHOP_URL}/admin")

def update_shopify_inventory(csv_file):
    """
    Update Shopify inventory levels from CSV counts
    """
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            sku = row['SKU']
            quantity = int(row['Quantity_Counted'])
            location_name = row['Location']

            # Find product by SKU
            products = shopify.Product.find(fields="id,variants", limit=1, sku=sku)

            if not products:
                print(f"SKU {sku} not found in Shopify")
                continue

            variant = products[0].variants[0]

            # Get location ID
            locations = shopify.Location.find()
            location = next((loc for loc in locations if loc.name == location_name), locations[0])

            # Update inventory level
            inventory_level = shopify.InventoryLevel.set(
                location_id=location.id,
                inventory_item_id=variant.inventory_item_id,
                available=quantity
            )

            print(f"Updated Shopify: {sku} = {quantity} at {location_name}")
```

### Google Sheets Integration

Export CSV to Google Sheets for review:

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import csv

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = 'your_spreadsheet_id'

def export_to_google_sheets(csv_file, sheet_name='Inventory Count'):
    """
    Upload CSV data to Google Sheets
    """
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # Read CSV
    with open(csv_file, 'r') as f:
        csv_data = list(csv.reader(f))

    # Clear existing data
    service.spreadsheets().values().clear(
        spreadsheetId=SHEET_ID,
        range=f"{sheet_name}!A:Z"
    ).execute()

    # Upload new data
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"{sheet_name}!A1",
        valueInputOption='RAW',
        body={'values': csv_data}
    ).execute()

    # Format header row
    service.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={
            'requests': [{
                'repeatCell': {
                    'range': {
                        'sheetId': get_sheet_id(service, SHEET_ID, sheet_name),
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            }]
        }
    ).execute()

    print(f"Uploaded to Google Sheets: {sheet_name}")
```

---

## Performance Metrics

### Counting Accuracy

- **SKU Recognition**: 96.8% accuracy with clear product labels
- **Quantity Counting**: ±1 unit accuracy for quantities up to 50
- **Location Detection**: 98.2% accuracy with visible location labels
- **Expiration Date Recognition**: 94.5% accuracy

### Time Savings

| Task | Manual Process | With ImgGo | Savings |
|------|----------------|------------|---------|
| Count 100 SKUs | 45 minutes | 3 minutes | 93% |
| Weekly cycle count (500 SKUs) | 6 hours | 20 minutes | 94% |
| Monthly full count (5,000 SKUs) | 3 days | 4 hours | 94% |
| Variance resolution | 2 hours | 15 minutes | 88% |

### Financial Impact

**Medium warehouse** (10,000 SKUs, $2M inventory value):

- **Labor Savings**: $48,000/year (eliminate 2,000 counting hours at $24/hour)
- **Reduced Shrinkage**: $60,000/year (from 3% to 1% through frequent counts)
- **Fewer Stockouts**: $120,000/year (improved order fulfillment rate)
- **Excess Inventory Reduction**: $200,000 (one-time, from better accuracy)
- **Total Annual Benefit**: $228,000
- **ImgGo Cost**: $12,000/year
- **ROI**: 1,800%

---

## Advanced Features

### Barcode/QR Code Integration

```python
from pyzbar import pyzbar
import cv2

def extract_barcodes_from_image(image_url):
    """
    Extract barcodes before sending to ImgGo for counting
    """
    # Download image
    img_data = requests.get(image_url).content

    # Decode barcodes
    img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
    barcodes = pyzbar.decode(img)

    skus = [barcode.data.decode('utf-8') for barcode in barcodes]

    return skus


# Use barcodes as validation for ImgGo SKU extraction
barcodes_found = extract_barcodes_from_image(camera_url)
csv_data = count_inventory_from_photo(camera_url, "A-12")

df = pd.read_csv(StringIO(csv_data))
imggo_skus = df['SKU'].tolist()

# Cross-validate
missing = set(barcodes_found) - set(imggo_skus)
if missing:
    print(f"Warning: Barcodes found but not extracted: {missing}")
```

### Mobile App Integration

```javascript
// React Native warehouse counting app
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
import axios from 'axios';

const CountInventoryScreen = () => {
  const takePhoto = async (locationCode) => {
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });

    if (!result.cancelled) {
      // Upload to S3
      const s3Url = await uploadToS3(result.uri, `${locationCode}/${Date.now()}.jpg`);

      // Process with ImgGo
      const csvData = await countInventory(s3Url, locationCode);

      // Display results
      displayCountResults(csvData);
    }
  };

  const uploadToS3 = async (fileUri, key) => {
    const response = await FileSystem.readAsStringAsync(fileUri, {
      encoding: FileSystem.EncodingType.Base64,
    });

    const s3Response = await axios.put(
      `https://warehouse-photos.s3.amazonaws.com/${key}`,
      Buffer.from(response, 'base64'),
      {
        headers: { 'Content-Type': 'image/jpeg' },
      }
    );

    return `https://warehouse-photos.s3.amazonaws.com/${key}`;
  };

  // ... rest of component
};
```

### Predictive Reordering

```python
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_reorder_points(historical_counts_csv):
    """
    Analyze historical counts to predict optimal reorder points
    """
    # Load historical counts
    df = pd.read_csv(historical_counts_csv, parse_dates=['Last_Updated'])

    # Group by SKU and calculate trends
    for sku in df['SKU'].unique():
        sku_data = df[df['SKU'] == sku].sort_values('Last_Updated')

        # Calculate daily usage rate
        sku_data['Days'] = (sku_data['Last_Updated'] - sku_data['Last_Updated'].min()).dt.days

        X = sku_data['Days'].values.reshape(-1, 1)
        y = sku_data['Quantity_Counted'].values

        model = LinearRegression()
        model.fit(X, y)

        # Slope = daily usage rate
        daily_usage = -model.coef_[0]

        # Predict stockout date
        current_qty = sku_data.iloc[-1]['Quantity_Counted']
        days_until_stockout = current_qty / daily_usage if daily_usage > 0 else float('inf')

        if days_until_stockout < 14:  # Less than 2 weeks
            print(f"REORDER ALERT: {sku} will stock out in {days_until_stockout:.1f} days")

            # Calculate reorder quantity (30 days supply)
            reorder_qty = daily_usage * 30

            create_purchase_requisition(sku, reorder_qty)
```

---

## Best Practices

### Photo Quality

- **Lighting**: Ensure uniform lighting across shelf (avoid shadows and glare)
- **Angle**: Capture shelves straight-on (not at steep angles)
- **Resolution**: Minimum 1920x1080 for reliable counting
- **Focus**: Products and labels must be in focus
- **Coverage**: Capture entire shelf section in one photo

### Counting Procedures

- **Timing**: Perform counts during off-peak hours to avoid movement
- **Consistency**: Use same camera angles and positions for comparable results
- **Validation**: Spot-check 10% of counts manually for accuracy verification
- **Frequency**: High-value/fast-moving items weekly, others monthly

### Data Management

- **Archive**: Retain CSV count files for 7 years for audit compliance
- **Version Control**: Use timestamps in filenames for easy tracking
- **Backup**: Store CSV files in multiple locations (local + cloud)
- **Reconciliation**: Compare automated counts to ERP weekly, investigate >5% variances

### Integration

- **Batch Imports**: Import counts during ERP off-hours to avoid performance issues
- **Error Handling**: Log failed imports, retry with exponential backoff
- **Validation**: Validate CSV schema before importing to prevent data corruption
- **Rollback**: Maintain ability to rollback incorrect imports

---

## Troubleshooting

### Issue: Inaccurate Counts for Stacked Products

**Solution**: Take multiple photos from different angles, use 3D camera setups, or manually verify stacked items

### Issue: Low Confidence Scores

**Solution**: Improve lighting, increase camera resolution, clean product labels, retrain pattern with more examples

### Issue: CSV Import Fails in ERP

**Solution**: Validate CSV schema matches ERP requirements, check for special characters in SKUs, ensure date formats match

### Issue: Slow Processing for Large Warehouses

**Solution**: Process zones in parallel, use multiple API instances, implement caching for repeat SKUs

---

## Related Use Cases

- [Retail Shelf Audit](../retail-shelf-audit) - Planogram compliance and shelf monitoring
- [Quality Control](../quality-control) - Manufacturing defect detection
- [Construction Progress](../construction-progress) - Material tracking on job sites

---

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- CSV Output Guide: [https://img-go.com/docs/output-formats#csv](https://img-go.com/docs/output-formats#csv)
- Inventory Best Practices: [https://img-go.com/docs/inventory-counting](https://img-go.com/docs/inventory-counting)
- Integration Help: <support@img-go.com>
