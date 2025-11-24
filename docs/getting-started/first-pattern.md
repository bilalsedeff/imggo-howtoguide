# Create Your First Pattern

Learn how to create patterns that extract structured data from images with precision and consistency.

## What is a Pattern?

A **pattern** is a template that defines:

1. **What data to extract** from images (instructions)
2. **How to structure the output** (schema)
3. **What format to use** (JSON, YAML, XML, CSV, or text)

Once created, each pattern gets a unique API endpoint that you can call repeatedly with different images.

## Pattern Components

### 1. Name
A descriptive identifier for your pattern.

**Examples**:
- "Invoice Data Extractor"
- "Retail Shelf Audit"
- "Medical Prescription Parser"

### 2. Output Format

Choose from five formats:

| Format | Best For | Example |
|--------|----------|---------|
| JSON | APIs, databases, modern apps | `{"vendor": "Acme"}` |
| YAML | Configuration files, human-readable | `vendor: Acme` |
| XML | Legacy systems, SOAP APIs | `<vendor>Acme</vendor>` |
| CSV | Spreadsheets, batch imports | `vendor,amount\nAcme,1500` |
| TEXT | Simple key-value pairs | `Vendor: Acme` |

### 3. Instructions

Natural language description of what data to extract.

**Good Instructions**:
```
Extract the vendor name, invoice number, invoice date,
all line items including description and amount,
subtotal, tax, and total amount from the invoice.
```

**Poor Instructions**:
```
Get all data from the invoice.
```

Be specific about:
- Exact field names
- Data types (dates, numbers, text)
- Nested structures (line items, addresses)
- Edge cases (missing fields, multiple values)

### 4. Schema

Defines the structure and data types of extracted data.

**Basic Schema**:
```json
{
  "vendor_name": "string",
  "invoice_number": "string",
  "total_amount": "number"
}
```

**Complex Schema with Nested Arrays**:
```json
{
  "vendor": {
    "name": "string",
    "address": "string",
    "tax_id": "string"
  },
  "invoice_number": "string",
  "invoice_date": "date",
  "line_items": [
    {
      "description": "string",
      "quantity": "number",
      "unit_price": "number",
      "amount": "number"
    }
  ],
  "totals": {
    "subtotal": "number",
    "tax": "number",
    "total": "number"
  }
}
```

## Creating Patterns: Two Methods

### Method 1: Pattern Studio (UI)

**Best for**: Beginners, visual workflow, quick prototyping

1. Log in to [img-go.com/dashboard](https://img-go.com/dashboard)
2. Click **Patterns** > **New Pattern**
3. Fill in the form:

   **Name**: `Invoice Data Extractor`

   **Output Format**: `JSON`

   **Instructions**:
   ```
   Extract vendor name, invoice number, invoice date,
   line items with descriptions and amounts, and total amount.
   ```

4. Click **Generate Template** - AI will suggest a schema
5. Review and customize the schema
6. Click **Test Pattern** to upload a sample image
7. Review extracted results
8. Adjust instructions/schema if needed
9. Click **Publish**

**Result**: You'll receive a `pattern_id` and endpoint URL.

### Method 2: API (Programmatic)

**Best for**: Automation, CI/CD, pattern versioning

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Invoice Data Extractor",
    "output_format": "json",
    "instructions": "Extract vendor name, invoice number, invoice date, line items, and total amount",
    "schema": {
      "vendor_name": "string",
      "invoice_number": "string",
      "invoice_date": "date",
      "line_items": [
        {
          "description": "string",
          "amount": "number"
        }
      ],
      "total_amount": "number"
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "pattern_id": "pat_2gYc3kZ8mN",
    "name": "Invoice Data Extractor",
    "status": "active",
    "endpoint": "https://img-go.com/api/patterns/pat_2gYc3kZ8mN/ingest",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

## Data Types Reference

| Type | Description | Example Value | Validation |
|------|-------------|---------------|------------|
| `string` | Text data | `"Acme Corp"` | UTF-8 string |
| `number` | Integer or float | `1234.56` | Numeric validation |
| `date` | Date/datetime | `"2024-01-15"` | ISO 8601 format |
| `boolean` | True/false | `true` | Boolean value |
| `array` | List of items | `[{...}, {...}]` | Array of objects |
| `object` | Nested structure | `{"key": "value"}` | JSON object |
| `email` | Email address | `"user@example.com"` | RFC 5322 validation |
| `url` | Web URL | `"https://example.com"` | URL validation |
| `phone` | Phone number | `"+1-555-0123"` | E.164 format |

## Best Practices for Instructions

### Be Specific

**Bad**:
```
Extract all product information
```

**Good**:
```
Extract product name, SKU, brand, price,
and whether the product is in stock (yes/no)
```

### Handle Missing Data

**Example**:
```
Extract invoice date. If not present, return null.
Extract line items. If none found, return an empty array.
```

### Specify Formats

**Example**:
```
Extract date in YYYY-MM-DD format.
Extract phone numbers in E.164 format (e.g., +1-555-0123).
Extract currency amounts as decimal numbers without symbols.
```

### Define Edge Cases

**Example**:
```
If multiple addresses are present, extract the billing address.
If total amount is not visible, calculate it from line items.
For handwritten text, use best-effort recognition.
```

## Testing Your Pattern

### Upload Test Image

**Via UI**:
1. Navigate to your pattern in the dashboard
2. Click **Test**
3. Upload a sample image
4. Review extracted results
5. Iterate on instructions/schema if needed

**Via API**:
```bash
curl -X POST https://img-go.com/api/patterns/pat_abc/ingest \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/test-invoice.jpg",
    "idempotency_key": "test-run-1"
  }'
```

### Review Results

Check for:
- **Accuracy**: Are all fields correctly extracted?
- **Completeness**: Are any fields missing?
- **Format**: Do dates, numbers, and other types match expectations?
- **Edge Cases**: Test with varied image quality, layouts, handwriting

## Pattern Versioning

Create multiple versions for A/B testing or gradual rollouts:

```bash
curl -X POST https://img-go.com/api/patterns/pat_abc/versions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "instructions": "Updated instructions with better accuracy",
    "schema": {...}
  }'
```

**Response**:
```json
{
  "pattern_id": "pat_abc",
  "version": "v2",
  "endpoint": "https://img-go.com/api/patterns/pat_abc/ingest?version=v2"
}
```

## Common Patterns by Use Case

### Invoice Extraction

```json
{
  "vendor_name": "string",
  "invoice_number": "string",
  "invoice_date": "date",
  "due_date": "date",
  "line_items": [
    {
      "description": "string",
      "quantity": "number",
      "unit_price": "number",
      "amount": "number"
    }
  ],
  "subtotal": "number",
  "tax": "number",
  "total_amount": "number"
}
```

### Product Shelf Audit

```json
{
  "products": [
    {
      "product_name": "string",
      "brand": "string",
      "sku": "string",
      "price_visible": "boolean",
      "in_stock": "boolean",
      "shelf_position": "string"
    }
  ],
  "total_products": "number",
  "out_of_stock_count": "number"
}
```

### ID Verification (KYC)

```json
{
  "document_type": "string",
  "full_name": "string",
  "date_of_birth": "date",
  "document_number": "string",
  "expiration_date": "date",
  "issuing_country": "string",
  "address": "string"
}
```

### Receipt Processing

```json
{
  "merchant_name": "string",
  "date": "date",
  "time": "string",
  "items": [
    {
      "name": "string",
      "quantity": "number",
      "price": "number"
    }
  ],
  "subtotal": "number",
  "tax": "number",
  "total": "number",
  "payment_method": "string"
}
```

## Managing Patterns

### List All Patterns

```bash
curl -X GET https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Update Pattern

```bash
curl -X PATCH https://img-go.com/api/patterns/pat_abc \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "instructions": "Updated instructions",
    "schema": {...}
  }'
```

### Delete Pattern

```bash
curl -X DELETE https://img-go.com/api/patterns/pat_abc \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Warning**: Deleting a pattern breaks all integrations using it. Consider archiving instead.

## Next Steps

Now that you've created your first pattern:

1. **Process Images at Scale**: Explore [Use Cases](../use-cases) for production workflows
2. **Set Up Webhooks**: Learn about [asynchronous processing](../api-reference/webhooks.md)
3. **Integrate with Tools**: Connect to [n8n](../automation-platforms/n8n), [Zapier](../automation-platforms/zapier), or databases
4. **Monitor Performance**: Track accuracy and processing times in the dashboard

---

**Previous**: [Authentication](./authentication.md) | **Next**: [Use Cases Overview](../use-cases)
