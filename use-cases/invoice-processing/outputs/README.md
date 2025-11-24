# Example Outputs

This folder contains example outputs from processing invoice images.

## Files

When you run the integration examples, output files will be saved here:

- `invoice1_output.json` - Extracted data from invoice1.jpg
- `invoice2_output.json` - Extracted data from invoice2.jpg
- etc.

## Format

All outputs are in JSON format with the following structure:

```json
{
  "invoice_number": "INV-10012",
  "vendor": "Your Company",
  "invoice_date": "26/3/2021",
  "due_date": "...",
  "total_amount": 1699.48,
  "currency": "USD",
  "line_items": [...]
}
```

## Usage

Run any of the integration examples to generate outputs:

```bash
# Python
python python-example.py

# Node.js/TypeScript
npm install && npx ts-node nodejs-example.ts

# curl
bash curl-example.sh
```

Outputs will be automatically saved to this directory.
