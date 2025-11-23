# JSON Output Examples

Complete working examples for converting images to JSON using ImgGo API.

## What is JSON Output?

JSON (JavaScript Object Notation) is the most popular output format for:
- Modern web applications and APIs
- NoSQL databases (MongoDB, DynamoDB)
- RESTful services
- JavaScript/TypeScript applications

## Examples Included

### 1. Invoice to JSON
Extract structured invoice data including vendor, line items, totals.

**Use case**: Accounting automation, AP processing

**Output example**:
```json
{
  "invoice_number": "INV-2025-001",
  "vendor": {
    "name": "Acme Corp",
    "address": "123 Main St"
  },
  "total_amount": 1250.00,
  "line_items": [...]
}
```

### 2. Document Classification
Automatically classify documents and extract metadata.

**Use case**: Document routing, intelligent filing

**Output example**:
```json
{
  "document_type": "invoice",
  "confidence": 0.95,
  "metadata": {
    "priority": "high"
  }
}
```

### 3. Product Catalog
Extract product information from images for e-commerce.

**Use case**: Catalog automation, marketplace integration

**Output example**:
```json
{
  "products": [
    {
      "name": "Widget Pro",
      "price": 49.99,
      "sku": "WID-001"
    }
  ]
}
```

### 4. Batch Processing
Process multiple images and aggregate results.

**Use case**: Bulk data extraction, reporting

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
python image-to-json.py
```

### Run Specific Example

```python
from imggo_client import ImgGoClient

client = ImgGoClient()
result = client.process_image(
    image_path="path/to/image.jpg",
    pattern_id="pat_your_pattern"
)

# result is already parsed JSON dict
print(result["invoice_number"])
```

## Pattern Setup

Create JSON patterns at [img-go.com/patterns](https://img-go.com/patterns):

1. Click "New Pattern"
2. Select **JSON** as output format
3. Write extraction instructions
4. Publish and copy Pattern ID

**Example instructions**:
```
Extract invoice data including:
- Invoice number
- Vendor name and address
- Invoice date and due date
- Line items with descriptions, quantities, prices
- Subtotal, tax, and total amount
```

## Integration Examples

### Save to MongoDB

```python
from pymongo import MongoClient

client_imggo = ImgGoClient()
client_mongo = MongoClient("mongodb://localhost:27017/")

result = client_imggo.process_image("invoice.jpg", "pat_invoice")

# Insert directly into MongoDB
db = client_mongo["accounting"]
db.invoices.insert_one(result)
```

### POST to REST API

```python
import requests

result = client.process_image("document.jpg", "pat_doc")

# Send to your API
requests.post(
    "https://api.yourapp.com/documents",
    json=result,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### Save to JSON File

```python
import json

result = client.process_image("data.jpg", "pat_data")

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)
```

## Common Use Cases

- **Invoice Processing**: Extract vendor, amounts, line items
- **Receipt Scanning**: Parse merchant, date, items, total
- **Form Data Extraction**: Digitize paper forms
- **Product Information**: Extract name, price, SKU
- **ID Card Parsing**: Extract name, DOB, ID number
- **Business Card OCR**: Extract contact information
- **Document Metadata**: Extract document type, date, parties
- **Medical Records**: Extract patient info, diagnosis codes
- **Real Estate**: Extract property details, measurements

## Error Handling

```python
try:
    result = client.process_image(
        image_path="invoice.jpg",
        pattern_id="pat_invoice"
    )

    # Validate required fields
    if not result.get("invoice_number"):
        raise ValueError("Missing invoice number")

except Exception as e:
    print(f"Error processing image: {e}")
    # Send to manual review queue
```

## Best Practices

1. **Validate output**: Always check for required fields
2. **Handle missing data**: Use `.get()` with defaults
3. **Type checking**: Verify data types match expectations
4. **Idempotency**: Use idempotency keys for retries
5. **Error logging**: Log failures for debugging

## Support

- [ImgGo API Documentation](https://img-go.com/docs)
- [JSON Format Guide](https://img-go.com/docs/output-formats/json)
- Email: support@img-go.com
