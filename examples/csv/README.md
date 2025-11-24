# CSV Output Examples

Complete working examples for converting images to CSV using ImgGo API.

## What is CSV Output?

CSV (Comma-Separated Values) is ideal for:

- Spreadsheet imports (Excel, Google Sheets)
- Database bulk imports
- Data analysis tools (pandas, R)
- Legacy system integration
- Batch data processing

## Examples Included

### 1. Inventory to CSV

Extract inventory counts from warehouse photos.

**Use case**: Cycle counting, stock management

**Output example**:

```csv
sku,product_name,quantity,location,condition
SKU-001,Widget Pro,150,A-12-3,Good
SKU-002,Gadget Plus,75,B-05-1,Good
```

### 2. Inspection Reports to CSV

Convert inspection checklists to tabular data.

**Use case**: Quality control, compliance reporting

**Output example**:

```csv
inspection_id,item,status,notes,inspector
INS-001,Fire Extinguisher,Pass,Fully charged,John Doe
INS-001,Exit Sign,Fail,Light not working,John Doe
```

### 3. Expense Receipts Batch

Process multiple receipts into expense report.

**Use case**: Expense management, accounting

**Output example**:

```csv
date,merchant,category,amount,payment_method
2025-01-15,Office Depot,Supplies,45.99,Corporate Card
2025-01-16,Starbucks,Meals,12.50,Cash
```

### 4. CSV to Database Import

Direct import of CSV results into SQLite/PostgreSQL.

**Use case**: Data warehousing, reporting

## Running the Examples

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export IMGGO_API_KEY="your_api_key_here"
```

### Run All Examples

```bash
python image-to-csv.py
```

### Process Single Image

```python
from imggo_client import ImgGoClient

client = ImgGoClient()
csv_result = client.process_image(
    image_path="inventory.jpg",
    pattern_id="pat_inventory_csv"
)

# csv_result is a CSV string
print(csv_result)

# Save to file
with open("inventory.csv", "w") as f:
    f.write(csv_result)
```

## Pattern Setup

Create CSV patterns at [img-go.com/patterns](https://img-go.com/patterns):

1. Click "New Pattern"
2. Select **CSV** as output format
3. Define column names in instructions
4. Publish and copy Pattern ID

**Example instructions**:

```plaintext
Extract inventory data with these columns:
- sku: Stock keeping unit
- product_name: Product description
- quantity: Count of items
- location: Warehouse location code
- condition: Item condition (Good/Damaged/Missing)

Include header row.
```

## Integration Examples

### Import to Pandas

```python
import pandas as pd
import io

csv_result = client.process_image("data.jpg", "pat_csv")

# Read CSV string into DataFrame
df = pd.read_csv(io.StringIO(csv_result))

print(df.describe())
print(df.groupby("category").sum())
```

### Import to PostgreSQL

```python
import psycopg2
import io

csv_result = client.process_image("inventory.jpg", "pat_inventory")

conn = psycopg2.connect("dbname=warehouse user=postgres")
cur = conn.cursor()

# Use COPY for fast bulk import
cur.copy_expert(
    "COPY inventory(sku, product_name, quantity, location, condition) FROM STDIN WITH CSV HEADER",
    io.StringIO(csv_result)
)

conn.commit()
```

### Import to Google Sheets

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

csv_result = client.process_image("data.jpg", "pat_data")

# Parse CSV
import csv
import io
reader = csv.reader(io.StringIO(csv_result))
rows = list(reader)

# Update Google Sheet
creds = service_account.Credentials.from_service_account_file("creds.json")
service = build("sheets", "v4", credentials=creds)

service.spreadsheets().values().update(
    spreadsheetId="your_sheet_id",
    range="Sheet1!A1",
    valueInputOption="RAW",
    body={"values": rows}
).execute()
```

### Import to SQLite

```python
import sqlite3
import csv
import io

csv_result = client.process_image("expenses.jpg", "pat_expenses")

conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        date TEXT,
        merchant TEXT,
        category TEXT,
        amount REAL,
        payment_method TEXT
    )
""")

# Import CSV
reader = csv.DictReader(io.StringIO(csv_result))
for row in reader:
    cursor.execute(
        "INSERT INTO expenses VALUES (?, ?, ?, ?, ?)",
        (row["date"], row["merchant"], row["category"],
         float(row["amount"]), row["payment_method"])
    )

conn.commit()
```

## Common Use Cases

- **Inventory Counts**: Warehouse cycle counting
- **Inspection Reports**: Quality control checklists
- **Expense Reports**: Receipt batch processing
- **Attendance Sheets**: Time tracking from photos
- **Survey Results**: Paper form digitization
- **Lab Results**: Medical test data extraction
- **Product Catalogs**: Bulk product data extraction
- **Shipping Manifests**: Logistics documentation
- **Asset Tracking**: Equipment audit results
- **Sales Reports**: POS data extraction

## CSV Format Options

### Custom Delimiter

```python
# Request semicolon-delimited output
# In pattern instructions, specify:
# "Use semicolon (;) as delimiter instead of comma"
```

### Include Headers

```python
# Specify in pattern instructions:
# "Include header row with column names"
```

### Quote Fields

```python
# Specify in pattern instructions:
# "Quote all text fields to handle commas in values"
```

## Error Handling

```python
import csv
import io

try:
    csv_result = client.process_image("data.jpg", "pat_data")

    # Validate CSV structure
    reader = csv.reader(io.StringIO(csv_result))
    rows = list(reader)

    if len(rows) < 2:
        raise ValueError("CSV has no data rows")

    # Check column count
    header = rows[0]
    for i, row in enumerate(rows[1:], start=2):
        if len(row) != len(header):
            print(f"Warning: Row {i} has {len(row)} columns, expected {len(header)}")

except Exception as e:
    print(f"Error processing CSV: {e}")
```

## Best Practices

1. **Always specify headers**: Include column names in instructions
2. **Handle commas**: Quote fields that may contain commas
3. **Validate structure**: Check row count and column consistency
4. **Data types**: Specify expected types (numbers, dates) in instructions
5. **Missing values**: Define how to handle empty cells

## Batch Processing

```python
import glob
import pandas as pd

all_data = []

for image_path in glob.glob("images/*.jpg"):
    csv_result = client.process_image(image_path, "pat_inventory")
    df = pd.read_csv(io.StringIO(csv_result))
    all_data.append(df)

# Combine all results
combined_df = pd.concat(all_data, ignore_index=True)
combined_df.to_csv("combined_inventory.csv", index=False)

print(f"Processed {len(all_data)} images")
print(f"Total rows: {len(combined_df)}")
```

## Support

- [ImgGo API Documentation](https://img-go.com/docs)
- [CSV Format Guide](https://img-go.com/docs/output-formats/csv)
- Email: <support@img-go.com>
