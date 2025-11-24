<div align="center">
  <img src="examples/public/white/logo.svg" alt="ImgGo Logo" width="200"/>
</div>

# Image-to-Structured Data Automation Guide

A comprehensive guide for automating image processing workflows and extracting structured data from visual content at scale.

## Overview

Modern businesses process thousands of images daily—invoices, receipts, product photos, damage assessments, medical records, and more. Manually extracting data from these images is time-consuming, error-prone, and doesn't scale.

This repository provides practical, end-to-end solutions for automating image data extraction workflows across 20+ real-world use cases. Learn how to transform images into structured data (JSON, YAML, XML, CSV, or plain text) and integrate them into your existing systems.

## What You'll Find Here

- **20+ Real-World Use Cases**: Invoice processing, retail audits, construction tracking, medical records, insurance claims, and more
- **Complete Integration Guides**: n8n, Zapier, Make, Power Automate, and direct API implementations
- **Database Connectors**: PostgreSQL, Google Sheets, and more
- **Production-Ready Code**: Python, Node.js, cURL examples with error handling and best practices
- **End-to-End Workflows**: From image upload to structured data storage

## Repository Structure

```
├── docs/                    # Documentation
│   ├── getting-started/     # Quick start, authentication, first pattern
│   ├── api-reference/       # API endpoints, webhooks, error handling
│   └── guides/              # Best practices and advanced topics
├── examples/                # Code examples
│   ├── languages/           # Python, Node.js, cURL, Postman
│   ├── formats/             # JSON, CSV, XML, YAML, Plain Text
│   ├── common/              # Shared utilities and helpers
│   └── test-images/         # Sample images for testing
├── integrations/            # Platform integrations
│   ├── automation/          # n8n, Zapier, Make, Power Automate
│   └── databases/           # PostgreSQL, Google Sheets
└── use-cases/               # 20 industry-specific use cases
```

## Quick Start

1. **Choose Your Use Case**: Browse the [use-cases/](./use-cases) directory
2. **Read the Docs**: Start with [Getting Started](./docs/getting-started/quick-start.md)
3. **Follow the Guide**: Each use case includes step-by-step instructions
4. **Deploy & Scale**: Production-ready examples with webhooks and automation

## Use Cases

### Finance & Accounting

- [Invoice Processing](./use-cases/invoice-processing) - Extract invoice data and sync to ERP/accounting systems
- [Expense Management](./use-cases/expense-management) - Automate expense report processing
- [Document Classification](./use-cases/document-classification) - Categorize and route financial documents

### Retail & E-commerce

- [Retail Shelf Audit](./use-cases/retail-shelf-audit) - Monitor stock levels, planogram compliance, and shelf share
- [Product Catalog](./use-cases/product-catalog) - Extract product info from images for listings
- [Inventory Management](./use-cases/inventory-management) - Visual inventory counting and tracking

### Healthcare

- [Medical Prescription](./use-cases/medical-prescription) - Digitize handwritten prescriptions
- [Medical Records](./use-cases/medical-records) - Extract patient data from forms and reports
- [KYC Verification](./use-cases/kyc-verification) - Automated identity verification for onboarding

### Insurance & Field Service

- [Insurance Claims](./use-cases/insurance-claims) - Automated claim processing from damage photos
- [Field Service](./use-cases/field-service) - Technician photo documentation and reporting

### Construction & Real Estate

- [Construction Progress](./use-cases/construction-progress) - Monitor project milestones from site photos
- [Real Estate](./use-cases/real-estate) - Generate property listings from photos

### Automotive

- [VIN Extraction](./use-cases/vin-extraction) - Automated vehicle identification number capture
- [Parking Management](./use-cases/parking-management) - License plate recognition and occupancy tracking

### Compliance & Security

- [GDPR Anonymization](./use-cases/gdpr-anonymization) - Automated face and PII blurring
- [Content Moderation](./use-cases/content-moderation) - Visual content screening and compliance
- [Food Safety](./use-cases/food-safety) - Restaurant inspection report automation

### Operations

- [Quality Control](./use-cases/quality-control) - Manufacturing defect detection
- [Resume Parsing](./use-cases/resume-parsing) - Automated candidate data extraction

[View all 20 use cases →](./use-cases/)

## Integrations

### Automation Platforms

Build no-code/low-code workflows with visual automation tools:

- [n8n](./integrations/automation/n8n) - Open-source workflow automation with 350+ integrations
- [Zapier](./integrations/automation/zapier) - Quick integration with 5,000+ apps
- [Make](./integrations/automation/make) - Advanced automation with complex routing
- [Power Automate](./integrations/automation/power-automate) - Microsoft ecosystem integration

### Databases

Connect to production databases and storage systems:

- [PostgreSQL](./integrations/databases/postgresql.md) - Relational data storage
- [Google Sheets](./integrations/databases/google-sheets.md) - Spreadsheet automation

[View all integrations →](./integrations/)

## Code Examples

### By Programming Language

- [Python](./examples/languages/python/) - Production-ready scripts with error handling
- [Node.js](./examples/languages/nodejs/) - Async/await patterns and best practices
- [cURL](./examples/languages/curl/) - Quick testing and debugging
- [Postman](./examples/languages/postman/) - Interactive API exploration

### By Output Format

- [JSON](./examples/formats/json/) - Modern web apps, APIs, NoSQL databases
- [CSV](./examples/formats/csv/) - Spreadsheets, data analysis, bulk imports
- [XML](./examples/formats/xml/) - Legacy systems, SOAP services, industry standards
- [YAML](./examples/formats/yaml/) - Configuration files, DevOps, Kubernetes
- [Plain Text](./examples/formats/plaintext/) - Human-readable reports and summaries

[View all examples →](./examples/)

## Getting Started

### Prerequisites

- Basic understanding of REST APIs
- API key from your image processing provider
- Target system credentials (database, webhook endpoint, etc.)

### Your First Workflow

1. Read the [Quick Start Guide](./docs/getting-started/quick-start.md)
2. Learn about [Authentication](./docs/getting-started/authentication.md)
3. Create your [First Pattern](./docs/getting-started/first-pattern.md)
4. Choose a [Use Case](./use-cases) that matches your needs
5. Deploy and scale

## Documentation

Complete technical documentation:

- [API Endpoints](./docs/api-reference/endpoints.md) - Complete API reference
- [Webhooks](./docs/api-reference/webhooks.md) - Real-time event notifications
- [Error Handling](./docs/api-reference/error-handling.md) - Common errors and solutions
- [Rate Limits](./docs/api-reference/rate-limits.md) - Understanding quotas and throttling

[View all documentation →](./docs/)

## Output Format Examples

### Image to JSON

Perfect for APIs, modern apps, and NoSQL databases. Most popular format for web applications.

```json
{
  "vendor_name": "Acme Corp",
  "invoice_number": "INV-2024-001",
  "total_amount": 1942.92,
  "line_items": [...]
}
```

**Use cases**: [Invoice Processing](./use-cases/invoice-processing), [Retail Shelf Audit](./use-cases/retail-shelf-audit), [Insurance Claims](./use-cases/insurance-claims)

### Image to CSV

Ideal for spreadsheets, data analysis, and bulk imports.

```csv
Product,Brand,Price,In Stock
Coca-Cola 2L,Coca-Cola,2.99,Yes
Pepsi 2L,Pepsi,2.79,Yes
```

**Use cases**: [Inventory Management](./use-cases/inventory-management), [Expense Management](./use-cases/expense-management)

### Image to Plain Text

Extract human-readable narratives from images.

```text
Prescription for John Doe
Medication: Amoxicillin 500mg
Dosage: Take one capsule three times daily with food
Duration: 10 days
```

**Use cases**: [Medical Prescription](./use-cases/medical-prescription), [Quality Control](./use-cases/quality-control), [Field Service](./use-cases/field-service)

### Image to XML

Legacy system integration and enterprise applications.

```xml
<invoice>
  <vendor>Acme Corp</vendor>
  <number>INV-2024-001</number>
  <amount>1942.92</amount>
</invoice>
```

**Use cases**: [Parking Management](./use-cases/parking-management), [Medical Records](./use-cases/medical-records)

### Image to YAML

Configuration files and human-readable structured data.

```yaml
vendor_name: Acme Corp
invoice_number: INV-2024-001
total_amount: 1942.92
```

**Use cases**: [Construction Progress](./use-cases/construction-progress), [Inventory Management](./use-cases/inventory-management)

## Architecture Pattern

All use cases follow this proven architecture:

```plaintext
Image Source → API Processing → Structured Output → Storage/Action
     ↓              ↓                  ↓                  ↓
 (Upload)    (Pattern Match)      (JSON/CSV)      (Database/Webhook)
```

1. **Image Ingestion**: Upload via URL, base64, or multipart form-data
2. **Pattern Processing**: AI-powered extraction based on your schema
3. **Structured Output**: Consistent JSON, YAML, XML, CSV, or text format
4. **Integration**: Store in databases, trigger webhooks, or feed downstream systems

## Example: Invoice Processing Pipeline

A complete invoice processing workflow in 3 steps:

### 1. Create Pattern (one-time setup)

```json
{
  "name": "Invoice Data Extractor",
  "output_format": "json",
  "instructions": "Extract vendor, invoice number, date, line items, and total amount",
  "schema": {
    "vendor_name": "string",
    "invoice_number": "string",
    "date": "date",
    "line_items": "array",
    "total_amount": "number"
  }
}
```

### 2. Process Image

```bash
curl -X POST https://img-go.com/api/patterns/{pattern_id}/ingest \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://your-cdn.com/invoice.jpg"}'
```

### 3. Store Results

```python
# Automatically inserted into PostgreSQL
INSERT INTO invoices (vendor, invoice_num, date, amount)
VALUES (result['vendor_name'], result['invoice_number'],
        result['date'], result['total_amount']);
```

**[See complete implementation →](./use-cases/invoice-processing)**

## Best Practices

- **Idempotency**: Use unique request IDs to prevent duplicate processing
- **Webhooks**: Implement async processing for high-volume workflows
- **Error Handling**: Implement retry logic with exponential backoff
- **Rate Limiting**: Respect quota limits and implement request queuing
- **Security**: Never commit API keys; use environment variables
- **Validation**: Always validate structured output before storage
- **Monitoring**: Track success rates, latency, and error patterns

## Contributing

This is a living document. Use cases, examples, and integrations are continuously updated based on real-world implementations.

## Support

- Review the [Documentation](./docs/) for detailed guides
- Check [Integrations](./integrations/) for specific platform instructions
- Explore [Use Cases](./use-cases/) for complete examples

## License

MIT License - See [LICENSE](./LICENSE) file for details

---

**Note**: This guide uses img-go.com API endpoints in examples. You can adapt these patterns to any image processing API that supports structured output formats.
