#!/bin/bash

# Create ImgGo Pattern for Retail Shelf Audit
# Extract product analytics from retail shelf images

IMGGO_API_KEY="${IMGGO_API_KEY}"
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"

if [ -z "$IMGGO_API_KEY" ]; then
    echo "X Error: IMGGO_API_KEY not set"
    exit 1
fi

echo "============================================================"
echo "CREATING RETAIL SHELF AUDIT PATTERN"
echo "============================================================"
echo ""

PATTERN_NAME="Retail Shelf Audit - JSON"
INSTRUCTIONS="Analyze the retail shelf image and extract: all visible products with brand names, product count per brand (facings), shelf position, out-of-stock gaps, planogram compliance, price tags if visible, and promotional items. Calculate total facings, unique SKUs, and brand share percentages."

SCHEMA='{
  "type": "object",
  "properties": {
    "products": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "brand": {"type": "string"},
          "product_name": {"type": "string"},
          "facings": {"type": "number"},
          "shelf_level": {"type": "string"},
          "position": {"type": "string"},
          "price": {"type": "string"}
        }
      }
    },
    "total_facings": {"type": "number"},
    "unique_skus": {"type": "number"},
    "out_of_stock_count": {"type": "number"},
    "brand_share": {
      "type": "object",
      "additionalProperties": {"type": "number"}
    }
  },
  "required": ["products", "total_facings"]
}'

RESPONSE=$(curl -s -X POST "${IMGGO_BASE_URL}/patterns" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"${PATTERN_NAME}\",
        \"instructions\": \"${INSTRUCTIONS}\",
        \"response_format\": \"image_analysis\",
        \"schema\": ${SCHEMA}
    }")

# Extract pattern ID from response
PATTERN_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$PATTERN_ID" ]; then
    echo "X Error creating pattern"
    echo "$RESPONSE"
    exit 1
fi

echo "V Pattern created successfully!"
echo ""
echo "Pattern ID: ${PATTERN_ID}"
echo ""
echo "Add to .env:"
echo "SHELF_AUDIT_PATTERN_ID=${PATTERN_ID}"
echo ""

# Save to file
echo "$PATTERN_ID" > pattern_id.txt
echo "V Saved to pattern_id.txt"
