#!/bin/bash

IMGGO_API_KEY="${IMGGO_API_KEY}"
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"

if [ -z "$IMGGO_API_KEY" ]; then
    echo "X Error: IMGGO_API_KEY not set"
    exit 1
fi

echo "============================================================"
echo "CREATING PARKING MANAGEMENT PATTERN"
echo "============================================================"
echo ""

RESPONSE=$(curl -s -X POST "${IMGGO_BASE_URL}/patterns" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Parking Management - XML",
        "instructions": "Extract license plate number, vehicle make, model, color, type (car/truck/SUV), timestamp, and parking spot number if visible. Also detect if multiple vehicles are in frame.",
        "response_format": "xml",
        "xml_root_element": "ParkingEvent"
    }')

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
echo "PARKING_PATTERN_ID=${PATTERN_ID}"
echo ""
echo "$PATTERN_ID" > pattern_id.txt
echo "V Saved to pattern_id.txt"
