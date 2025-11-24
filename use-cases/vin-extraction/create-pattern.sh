#!/bin/bash

# Create ImgGo Pattern for VIN Extraction
# Extract Vehicle Identification Numbers from images

IMGGO_API_KEY="${IMGGO_API_KEY}"
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"

if [ -z "$IMGGO_API_KEY" ]; then
    echo "X Error: IMGGO_API_KEY not set"
    exit 1
fi

echo "============================================================"
echo "CREATING VIN EXTRACTION PATTERN"
echo "============================================================"
echo ""

PATTERN_NAME="VIN Extraction - JSON"
INSTRUCTIONS="Extract the Vehicle Identification Number (VIN) from the image. VIN is a 17-character alphanumeric code. Also extract vehicle make, model, and year if visible."

SCHEMA='{
  "type": "object",
  "properties": {
    "vin": {
      "type": "string",
      "description": "17-character VIN code"
    },
    "make": {
      "type": "string",
      "description": "Vehicle manufacturer"
    },
    "model": {
      "type": "string",
      "description": "Vehicle model"
    },
    "year": {
      "type": "number",
      "description": "Model year"
    }
  },
  "required": ["vin"]
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
echo "VIN_PATTERN_ID=${PATTERN_ID}"
echo ""

# Save to file
echo "$PATTERN_ID" > pattern_id.txt
echo "V Saved to pattern_id.txt"
