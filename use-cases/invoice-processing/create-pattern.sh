#!/bin/bash

###############################################################################
# Create ImgGo Pattern for Invoice Processing
# This script creates a pattern specifically for extracting invoice data
###############################################################################

set -e

# Configuration
IMGGO_API_KEY="${IMGGO_API_KEY}"
IMGGO_BASE_URL="https://img-go.com/api"

# Check for API key
if [ -z "$IMGGO_API_KEY" ]; then
    echo "X Error: IMGGO_API_KEY environment variable not set"
    echo "  Set it in .env file or: export IMGGO_API_KEY=your_key"
    exit 1
fi

echo "============================================================"
echo "CREATING INVOICE PROCESSING PATTERN"
echo "============================================================"
echo ""

# Pattern configuration
PATTERN_NAME="Invoice Processing - JSON"
INSTRUCTIONS="Extract all invoice data including vendor name, invoice number, date, due date, line items with descriptions and amounts, subtotal, tax, and total amount. Format as structured JSON."
RESPONSE_FORMAT="image_analysis"

# JSON Schema for invoice
SCHEMA='{
  "type": "object",
  "properties": {
    "invoice_number": {
      "type": "string",
      "description": "Invoice or reference number"
    },
    "vendor": {
      "type": "string",
      "description": "Vendor or company name"
    },
    "invoice_date": {
      "type": "string",
      "description": "Invoice issue date"
    },
    "due_date": {
      "type": "string",
      "description": "Payment due date"
    },
    "subtotal": {
      "type": "number",
      "description": "Subtotal before tax"
    },
    "tax_amount": {
      "type": "number",
      "description": "Tax amount"
    },
    "total_amount": {
      "type": "number",
      "description": "Total amount due"
    },
    "currency": {
      "type": "string",
      "description": "Currency code (USD, EUR, etc.)"
    },
    "line_items": {
      "type": "array",
      "description": "List of invoice line items",
      "items": {
        "type": "object",
        "properties": {
          "description": {"type": "string"},
          "quantity": {"type": "number"},
          "unit_price": {"type": "number"},
          "amount": {"type": "number"}
        },
        "required": ["description", "amount"]
      }
    }
  },
  "required": ["invoice_number", "vendor", "total_amount"]
}'

echo "Configuration:"
echo "  Name: $PATTERN_NAME"
echo "  Format: $RESPONSE_FORMAT"
echo ""

# Create pattern
RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"$PATTERN_NAME\",
        \"instructions\": \"$INSTRUCTIONS\",
        \"response_format\": \"$RESPONSE_FORMAT\",
        \"schema\": $SCHEMA
    }")

# Check if request was successful
if echo "$RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
    PATTERN_ID=$(echo "$RESPONSE" | jq -r '.data.id')

    echo "V Pattern created successfully!"
    echo ""
    echo "Pattern ID: $PATTERN_ID"
    echo ""
    echo "Save this ID to your .env file:"
    echo "INVOICE_PATTERN_ID=$PATTERN_ID"
    echo ""
    echo "Or use it directly in your scripts:"
    echo "PATTERN_ID=\"$PATTERN_ID\""
    echo ""

    # Save to file
    echo "$PATTERN_ID" > pattern_id.txt
    echo "V Pattern ID saved to pattern_id.txt"
    echo ""
    echo "============================================================"

else
    echo "X Error creating pattern"
    echo ""
    echo "Response:"
    echo "$RESPONSE" | jq '.'
    exit 1
fi
