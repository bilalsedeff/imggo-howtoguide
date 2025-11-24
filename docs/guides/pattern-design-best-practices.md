# Pattern Design Best Practices

This guide covers best practices for designing effective extraction patterns in ImgGo.

## Table of Contents

- [Understanding Patterns](#understanding-patterns)
- [Design Principles](#design-principles)
- [Common Patterns](#common-patterns)
- [Testing and Iteration](#testing-and-iteration)
- [Performance Optimization](#performance-optimization)
- [Common Mistakes](#common-mistakes)

## Understanding Patterns

A **pattern** in ImgGo defines what data to extract from images and how to structure it. Think of it as a template that tells the API:

- What fields to extract (e.g., invoice number, date, total amount)
- Expected data types (string, number, date, boolean)
- Output format (JSON, CSV, XML, YAML, plain text)
- Validation rules

## Design Principles

### 1. Be Specific and Clear

**Bad:**

```plaintext
Extract information from this document
```

**Good:**

```plaintext
Extract the following fields from this invoice:
- Invoice Number (string)
- Invoice Date (date in YYYY-MM-DD format)
- Vendor Name (string)
- Total Amount (number with 2 decimal places)
- Line Items (array of objects with: description, quantity, unit_price, total)
```

### 2. Provide Examples

Include example values in your pattern definition:

```plaintext
Invoice Number: INV-2024-001
Invoice Date: 2024-01-15
Vendor Name: Acme Corp
Total Amount: 1250.50
```

This helps the AI understand the expected format.

### 3. Specify Data Types Explicitly

```plaintext
- invoice_number: string
- invoice_date: date (ISO 8601)
- total_amount: number (float, 2 decimals)
- is_paid: boolean
- line_items: array
```

### 4. Handle Edge Cases

Consider and document how to handle:

- Missing fields
- Multiple occurrences (e.g., two dates on the same invoice)
- Ambiguous data
- Different formats

**Example:**

```plaintext
If the invoice date is not found, return null.
If multiple dates are present, use the date labeled "Invoice Date" or the earliest date.
```

### 5. Use Consistent Naming

Follow a naming convention:

**Snake case (recommended):**

```plaintext
invoice_number
vendor_name
total_amount
```

**Camel case:**

```plaintext
invoiceNumber
vendorName
totalAmount
```

Pick one and stick to it across all patterns.

## Common Patterns

### Document Classification

**Use Case:** Determine document type before extraction

**Pattern Example:**

```plaintext
Classify this document into one of the following categories:
- invoice
- receipt
- purchase_order
- packing_slip
- other

Return the classification as: { "document_type": "category_name" }
```

### Structured Data Extraction

**Use Case:** Extract specific fields with known structure

**Pattern Example:**

```plaintext
Extract the following fields from this invoice:

{
  "invoice_number": "string",
  "invoice_date": "YYYY-MM-DD",
  "due_date": "YYYY-MM-DD",
  "vendor": {
    "name": "string",
    "address": "string",
    "tax_id": "string"
  },
  "customer": {
    "name": "string",
    "address": "string"
  },
  "line_items": [
    {
      "description": "string",
      "quantity": "number",
      "unit_price": "number",
      "total": "number"
    }
  ],
  "subtotal": "number",
  "tax": "number",
  "total": "number"
}
```

### Table Extraction

**Use Case:** Extract data from tables

**Pattern Example:**

```plaintext
Extract all rows from the inventory table with these columns:
- SKU (string)
- Product Name (string)
- Quantity (integer)
- Unit Price (number with 2 decimals)
- Location (string)

Return as an array of objects.
```

### Key-Value Pairs

**Use Case:** Extract labeled data

**Pattern Example:**

```plaintext
Extract all key-value pairs from this form where:
- Key is the label text (e.g., "Full Name:", "Date of Birth:")
- Value is the filled-in information

Return as: { "key": "value", ... }
```

### OCR with Validation

**Use Case:** Extract text with specific validation rules

**Pattern Example:**

```plaintext
Extract the VIN (Vehicle Identification Number) from this image.

Validation rules:
- Must be exactly 17 characters
- Only alphanumeric characters (no I, O, Q)
- Return null if validation fails

Return as: { "vin": "string or null" }
```

## Testing and Iteration

### 1. Start with Sample Images

Test your pattern with 5-10 representative sample images:

```bash
# Test with samples
python test-pattern.py sample1.jpg pat_invoice_123
python test-pattern.py sample2.jpg pat_invoice_123
python test-pattern.py sample3.jpg pat_invoice_123
```

### 2. Validate Output

Check that the output:

- Contains all expected fields
- Has correct data types
- Handles edge cases
- Is structured consistently

### 3. Iterate Based on Results

If results are incorrect:

1. **Missing fields?** → Add more specific instructions
2. **Wrong data type?** → Clarify the expected type
3. **Incorrect values?** → Provide examples
4. **Inconsistent structure?** → Use explicit schema

### 4. Test Edge Cases

Test with challenging images:

- Low quality/blurry images
- Rotated or skewed images
- Images with watermarks
- Multi-page documents
- Handwritten text
- Forms with empty fields

### 5. Measure Accuracy

Track extraction accuracy:

```python
correct_extractions = 0
total_samples = 100

for image in test_images:
    result = extract(image, pattern_id)
    if validate_result(result, expected):
        correct_extractions += 1

accuracy = (correct_extractions / total_samples) * 100
print(f"Accuracy: {accuracy}%")
```

Aim for >95% accuracy on your test set.

## Performance Optimization

### 1. Request Only What You Need

**Slow:**

```plaintext
Extract everything from this document
```

**Fast:**

```plaintext
Extract only: invoice_number, invoice_date, total_amount
```

### 2. Use Appropriate Output Formats

Choose the right format for your use case:

- **JSON**: Best for structured data, APIs, databases
- **CSV**: Best for tabular data, spreadsheets, bulk exports
- **Plain Text**: Best for simple, human-readable summaries

### 3. Batch Processing

Process multiple images concurrently:

```python
# See: examples/languages/python/async-batch.py
results = await process_batch(image_paths, pattern_id)
```

Can be 10-20x faster than sequential processing.

### 4. Cache Results

Store extraction results to avoid reprocessing:

```python
import hashlib

def get_cached_result(image_path, pattern_id):
    # Generate cache key
    with open(image_path, 'rb') as f:
        image_hash = hashlib.md5(f.read()).hexdigest()
    cache_key = f"{image_hash}-{pattern_id}"

    # Check cache
    if cache_key in cache:
        return cache[cache_key]

    # Process and cache
    result = process_image(image_path, pattern_id)
    cache[cache_key] = result
    return result
```

### 5. Optimize Image Size

Resize large images before upload:

```python
from PIL import Image

def optimize_image(image_path, max_size=2048):
    img = Image.open(image_path)
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    img.save(image_path, optimize=True, quality=85)
```

Smaller images = faster upload and processing.

## Common Mistakes

### Mistake 1: Vague Instructions

**Bad:**

```plaintext
Get the date
```

**Problem:** Which date? Format?

**Good:**

```plaintext
Extract the invoice date in YYYY-MM-DD format
```

### Mistake 2: No Data Type Specification

**Bad:**

```plaintext
Extract: amount
```

**Problem:** Could return "$1,250.50" (string) instead of 1250.50 (number)

**Good:**

```plaintext
Extract: amount (number, no currency symbols or commas)
```

### Mistake 3: Ignoring Edge Cases

**Bad:**

```plaintext
Extract all line items
```

**Problem:** What if there are no line items?

**Good:**

```plaintext
Extract all line items. If no line items are found, return an empty array.
```

### Mistake 4: Over-Complicating Patterns

**Bad:**

```plaintext
Extract invoice data and also classify the document type and summarize the content
and calculate the tax percentage and validate the address format and...
```

**Problem:** Too many tasks in one pattern reduces accuracy

**Good:**

```plaintext
Create separate patterns for:
1. Document classification
2. Invoice data extraction
3. Address validation
```

### Mistake 5: Not Providing Examples

**Bad:**

```plaintext
Extract SKU
```

**Problem:** What does a SKU look like?

**Good:**

```plaintext
Extract SKU (example: SKU-12345 or PROD-ABC-001)
```

### Mistake 6: Inconsistent Field Names

**Bad:**

```plaintext
Pattern 1: invoice_number
Pattern 2: invoiceNumber
Pattern 3: InvoiceNum
```

**Problem:** Hard to integrate and maintain

**Good:**

```plaintext
Use snake_case consistently:
- invoice_number
- invoice_date
- total_amount
```

## Pattern Templates

### Invoice Extraction

```plaintext
Extract the following fields from this invoice:

{
  "invoice_number": "string (e.g., INV-2024-001)",
  "invoice_date": "string in YYYY-MM-DD format",
  "due_date": "string in YYYY-MM-DD format or null",
  "vendor_name": "string",
  "vendor_address": "string",
  "customer_name": "string",
  "line_items": [
    {
      "description": "string",
      "quantity": "number (integer)",
      "unit_price": "number (2 decimals)",
      "line_total": "number (2 decimals)"
    }
  ],
  "subtotal": "number (2 decimals)",
  "tax_amount": "number (2 decimals)",
  "total_amount": "number (2 decimals)"
}

Return null for any field that is not found.
```

### Resume/CV Extraction

```plaintext
Extract the following information from this resume:

{
  "name": "string",
  "email": "string (email format)",
  "phone": "string",
  "location": "string (city, state or city, country)",
  "summary": "string (2-3 sentences)",
  "work_experience": [
    {
      "company": "string",
      "title": "string",
      "start_date": "string (YYYY-MM)",
      "end_date": "string (YYYY-MM) or 'Present'",
      "responsibilities": ["string"]
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "field": "string",
      "graduation_date": "string (YYYY)"
    }
  ],
  "skills": ["string"]
}
```

### Form Data Extraction

```plaintext
Extract all filled form fields with their labels and values.

Return as:
{
  "field_name": "value",
  ...
}

Where field_name is the label text (lowercase, spaces replaced with underscores).

For checkboxes:
- checked = true
- unchecked = false

For empty fields, return null.
```

## Next Steps

- [Performance Optimization](./performance-optimization.md)
- [Security Best Practices](./security-best-practices.md)
- [Production Deployment](./production-deployment.md)
- [Use Cases](../../use-cases/) for pattern examples

## Need Help?

- [Getting Started Guide](../getting-started/)
- [API Reference](../api-reference/)
- GitHub Issues
