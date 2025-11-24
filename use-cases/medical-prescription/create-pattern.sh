#!/bin/bash

# Create ImgGo Pattern for Medical Prescription Processing
# Extract prescription data from medical prescription images

IMGGO_API_KEY="${IMGGO_API_KEY}"
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"

if [ -z "$IMGGO_API_KEY" ]; then
    echo "X Error: IMGGO_API_KEY not set"
    exit 1
fi

echo "============================================================"
echo "CREATING PRESCRIPTION PROCESSING PATTERN"
echo "============================================================"
echo ""

PATTERN_NAME="Medical Prescription - Plain Text"
INSTRUCTIONS="Extract all text from the medical prescription including: patient name, doctor name, clinic/hospital name, prescription date, medication names, dosages, frequency, duration, special instructions, and refill information. Format as readable plain text."

RESPONSE=$(curl -s -X POST "${IMGGO_BASE_URL}/patterns" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"${PATTERN_NAME}\",
        \"instructions\": \"${INSTRUCTIONS}\",
        \"response_format\": \"text\"
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
echo "PRESCRIPTION_PATTERN_ID=${PATTERN_ID}"
echo ""

# Save to file
echo "$PATTERN_ID" > pattern_id.txt
echo "V Saved to pattern_id.txt"
