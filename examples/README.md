# ImgGo API Examples

This directory contains general-purpose code examples for using ImgGo API across all output formats and use cases.

## Directory Structure

```
examples/
├── json/           # JSON output format examples
├── csv/            # CSV output format examples
├── xml/            # XML output format examples
├── yaml/           # YAML output format examples
├── plaintext/      # Plain text output format examples
└── common/         # Shared utilities and helpers
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

### Running Examples

#### Python Examples

```bash
cd examples/json
pip install -r requirements.txt
python image-to-json.py
```

#### Node.js Examples

```bash
cd examples/json
npm install
npm start
```

#### curl Examples

```bash
cd examples/json
chmod +x curl-example.sh
./curl-example.sh
```

## Output Format Examples

### JSON Output
Best for: APIs, modern web apps, NoSQL databases

Example: Extract structured product data, invoice fields, form data

### CSV Output
Best for: Spreadsheets, data analysis, bulk imports

Example: Inventory counts, inspection reports, bulk data export

### XML Output
Best for: Legacy systems, SOAP services, industry standards

Example: Parking systems, healthcare HL7, financial EDI

### YAML Output
Best for: Configuration files, DevOps, Kubernetes

Example: Construction progress configs, deployment specs

### Plain Text Output
Best for: Human-readable reports, narrative summaries

Example: Medical notes, service reports, inspection narratives

## Common Utilities

The `common/` directory contains shared utilities:

- `imggo_client.py` - Reusable Python client
- `imggo_client.ts` - Reusable TypeScript client
- `helpers.py` - Common helper functions
- `test_helpers.sh` - Bash testing utilities

## Use Case-Specific Examples

For complete end-to-end solutions, see the `use-cases/` directory:

- [Invoice Processing](../use-cases/invoice-processing)
- [Document Classification](../use-cases/document-classification)
- [Parking Management](../use-cases/parking-management)
- [And 17 more...](../use-cases/)

## Support

- API Documentation: [https://img-go.com/docs](https://img-go.com/docs)
- GitHub Issues: Report problems or request examples
- Email: support@img-go.com
