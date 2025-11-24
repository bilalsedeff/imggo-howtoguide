# Examples

General-purpose code examples for using the ImgGo API across all output formats and programming languages.

## Directory Structure

```
examples/
├── languages/       # Code examples by programming language
│   ├── python/      # Python implementation examples
│   ├── nodejs/      # Node.js/TypeScript examples
│   ├── curl/        # Command-line curl examples
│   └── postman/     # Postman collection
├── formats/         # Examples by output format
│   ├── json/        # JSON output format
│   ├── csv/         # CSV output format
│   ├── xml/         # XML output format
│   ├── yaml/        # YAML output format
│   └── plaintext/   # Plain text output
├── common/          # Shared utilities and helpers
├── test-images/     # Sample images for testing
└── README.md
```

## Quick Start

### Prerequisites

All examples require an ImgGo API key. Get yours at [img-go.com/auth/signup](https://img-go.com/auth/signup).

Set your API key as an environment variable:

```bash
export IMGGO_API_KEY="your_api_key_here"
```

Or create a `.env` file:

```
IMGGO_API_KEY=your_api_key_here
```

## By Programming Language

### Python Examples

Located in [`languages/python/`](./languages/python/)

```bash
cd examples/languages/python
pip install -r requirements.txt
python basic-example.py
```

**Use when:**
- Building backend services
- Data processing pipelines
- Automation scripts
- Integration with Django/Flask apps

### Node.js Examples

Located in [`languages/nodejs/`](./languages/nodejs/)

```bash
cd examples/languages/nodejs
npm install
npm start
```

**Use when:**
- Building web APIs
- Real-time applications
- Frontend/backend integration
- Serverless functions

### cURL Examples

Located in [`languages/curl/`](./languages/curl/)

```bash
cd examples/languages/curl
chmod +x basic-example.sh
./basic-example.sh
```

**Use when:**
- Quick API testing
- Command-line automation
- Shell scripts
- CI/CD pipelines

### Postman Collection

Located in [`languages/postman/`](./languages/postman/)

Import the collection into Postman for interactive API exploration.

**Use when:**
- API exploration and testing
- Debugging API calls
- Team collaboration
- Documentation generation

## By Output Format

### JSON Output

Located in [`formats/json/`](./formats/json/)

**Best for:** Modern web apps, APIs, NoSQL databases, JavaScript frameworks

**Example use cases:**
- Structured data extraction (invoices, forms, receipts)
- Product catalogs
- API responses
- Document classification

### CSV Output

Located in [`formats/csv/`](./formats/csv/)

**Best for:** Spreadsheets, data analysis, bulk imports, reporting

**Example use cases:**
- Inventory counts
- Inspection reports
- Bulk data exports
- Excel/Google Sheets integration

### XML Output

Located in [`formats/xml/`](./formats/xml/)

**Best for:** Legacy systems, SOAP services, industry standards (HL7, EDI)

**Example use cases:**
- Parking management systems
- Healthcare data (HL7 format)
- Financial EDI transactions
- Enterprise integrations

### YAML Output

Located in [`formats/yaml/`](./formats/yaml/)

**Best for:** Configuration files, DevOps, Kubernetes, Infrastructure-as-Code

**Example use cases:**
- Construction progress configurations
- Deployment specifications
- Application configs
- CI/CD pipelines

### Plain Text Output

Located in [`formats/plaintext/`](./formats/plaintext/)

**Best for:** Human-readable reports, narrative summaries, documentation

**Example use cases:**
- Medical prescription notes
- Field service reports
- Inspection narratives
- Document summaries

## Common Utilities

The [`common/`](./common/) directory contains shared utilities used across examples:

- `imggo_client.py` - Reusable Python client with error handling
- `imggo_client.ts` - Reusable TypeScript client
- `helpers.py` - Common helper functions
- `test_helpers.sh` - Bash testing utilities

These utilities are imported by use-case examples to avoid code duplication.

## Test Images

The [`test-images/`](./test-images/) directory contains sample images for testing:

- `invoice1-5.jpg` - Sample invoices
- `resume1-5.jpg` - Sample resumes/CVs
- `inventory1-5.jpg` - Retail shelf images
- `parking1-5.jpg` - Parking lot images
- `vin1-5.jpg` - VIN number images
- `prescription1-5.jpg` - Medical prescriptions

## Use Case-Specific Examples

For complete end-to-end production solutions, see the [`use-cases/`](../use-cases/) directory:

- [Invoice Processing](../use-cases/invoice-processing) - Full accounting integration
- [Resume Parsing](../use-cases/resume-parsing) - ATS integration with scoring
- [Retail Shelf Audit](../use-cases/retail-shelf-audit) - Database analytics
- [VIN Extraction](../use-cases/vin-extraction) - Fleet management
- [And 16 more...](../use-cases/)

## Integration Examples

For database and automation platform integrations, see the [`integrations/`](../integrations/) directory:

- [PostgreSQL Integration](../integrations/databases/postgresql.md)
- [Google Sheets Integration](../integrations/databases/google-sheets.md)
- [n8n Workflows](../integrations/automation/n8n/)
- [Zapier Setup](../integrations/automation/zapier/)

## Support

- [Getting Started Guide](../docs/getting-started/)
- [API Reference](../docs/api-reference/)
- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- GitHub Issues: Report problems or request examples
- Email: support@img-go.com
