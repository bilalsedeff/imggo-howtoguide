#!/bin/bash

###############################################################################
# Real Estate Listing Automation - curl Example
# Extract property data from photos using ImgGo API
###############################################################################

set -e  # Exit on error

# Configuration
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"
REAL_ESTATE_PATTERN_ID="${REAL_ESTATE_PATTERN_ID:-pat_real_estate_json}"

# Check for API key
if [ -z "$IMGGO_API_KEY" ]; then
    echo "Error: IMGGO_API_KEY environment variable not set"
    exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    exit 1
fi

# Test image path
TEST_IMAGE="../../../test-images/real-estate1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "Warning: Test image not found: $TEST_IMAGE"
    exit 1
fi

echo "============================================================"
echo "REAL ESTATE LISTING AUTOMATION - CURL EXAMPLE"
echo "============================================================"

# Generate idempotency key
IDEMPOTENCY_KEY="real-estate-$(date +%s)"

echo ""
echo "Step 1: Uploading property photo..."

# Upload property photo
UPLOAD_RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns/${REAL_ESTATE_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Idempotency-Key: ${IDEMPOTENCY_KEY}" \
    -F "file=@${TEST_IMAGE}")

# Extract job ID
JOB_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.data.job_id')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
    echo "Error: Failed to get job ID"
    echo "Response: $UPLOAD_RESPONSE"
    exit 1
fi

echo "✓ Job created: $JOB_ID"

# Poll for result
MAX_ATTEMPTS=60
ATTEMPT=1

echo ""
echo "Step 2: Waiting for processing to complete..."

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    JOB_RESPONSE=$(curl -s -X GET \
        "${IMGGO_BASE_URL}/jobs/${JOB_ID}" \
        -H "Authorization: Bearer ${IMGGO_API_KEY}")

    STATUS=$(echo "$JOB_RESPONSE" | jq -r '.data.status')

    if [ "$STATUS" = "completed" ]; then
        echo "✓ Processing completed"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "Error: Job failed"
        echo "$JOB_RESPONSE" | jq .
        exit 1
    fi

    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS: Status = $STATUS"
    ATTEMPT=$((ATTEMPT + 1))
    sleep 2
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo "Error: Timeout waiting for job completion"
    exit 1
fi

# Extract result
PROPERTY_DATA=$(echo "$JOB_RESPONSE" | jq '.data.result')

# Save raw JSON
OUTPUT_FILE="property_data.json"
echo "$PROPERTY_DATA" | jq . > "$OUTPUT_FILE"
echo ""
echo "✓ Saved property data to $OUTPUT_FILE"

echo ""
echo "============================================================"
echo "PROPERTY DETAILS"
echo "============================================================"

# Parse property data
ADDRESS=$(echo "$PROPERTY_DATA" | jq -r '.address')
CITY=$(echo "$PROPERTY_DATA" | jq -r '.city // "N/A"')
STATE=$(echo "$PROPERTY_DATA" | jq -r '.state // "N/A"')
ZIP_CODE=$(echo "$PROPERTY_DATA" | jq -r '.zip_code // "N/A"')
PRICE=$(echo "$PROPERTY_DATA" | jq -r '.price')
BEDROOMS=$(echo "$PROPERTY_DATA" | jq -r '.bedrooms')
BATHROOMS=$(echo "$PROPERTY_DATA" | jq -r '.bathrooms')
SQFT=$(echo "$PROPERTY_DATA" | jq -r '.square_feet')

echo "Address: $ADDRESS"
echo "City: $CITY, $STATE $ZIP_CODE"
echo "Price: \$$PRICE"
echo "Bedrooms: $BEDROOMS"
echo "Bathrooms: $BATHROOMS"
echo "Square Feet: $SQFT"

# Calculate price per sqft
if [ "$SQFT" != "null" ] && [ "$SQFT" != "0" ]; then
    PRICE_PER_SQFT=$(echo "scale=2; $PRICE / $SQFT" | bc)
    echo "Price/SqFt: \$$PRICE_PER_SQFT"
fi

# Calculate estimated monthly payment
if [ "$PRICE" != "null" ]; then
    LOAN_AMOUNT=$(echo "scale=2; $PRICE * 0.8" | bc)  # 20% down
    # Simplified monthly payment calculation (7% interest, 30 years)
    MONTHLY_PAYMENT=$(echo "scale=2; $LOAN_AMOUNT * 0.00665 / (1 - (1.00665)^-360)" | bc)
    echo "Est. Monthly Payment: \$$MONTHLY_PAYMENT"
fi

echo ""
echo "============================================================"
echo "VALIDATION"
echo "============================================================"

# Simple validation
ERRORS=0

if [ -z "$ADDRESS" ] || [ "$ADDRESS" = "null" ]; then
    echo "✗ Missing address"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "$PRICE" ] || [ "$PRICE" = "null" ] || [ "$PRICE" = "0" ]; then
    echo "✗ Missing or invalid price"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "$BEDROOMS" ] || [ "$BEDROOMS" = "null" ]; then
    echo "✗ Missing bedrooms"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "$BATHROOMS" ] || [ "$BATHROOMS" = "null" ]; then
    echo "✗ Missing bathrooms"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "$SQFT" ] || [ "$SQFT" = "null" ] || [ "$SQFT" = "0" ]; then
    echo "✗ Missing or invalid square feet"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -eq 0 ]; then
    echo "✓ Validation passed"
fi

if [ $ERRORS -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "GENERATED LISTING DESCRIPTION"
    echo "============================================================"

    # Generate simple description
    cat <<EOF
Welcome to $ADDRESS, offered at \$$PRICE.

This stunning $BEDROOMS bedroom, $BATHROOMS bathroom home features
$SQFT square feet of beautifully designed living space.

Conveniently located in $CITY, close to shopping, dining, and entertainment.

Schedule your showing today!
EOF

    echo ""
    echo "============================================================"
    echo "MLS LISTING DATA"
    echo "============================================================"

    # Generate MLS listing
    MLS_LISTING=$(jq -n \
        --arg address "$ADDRESS" \
        --arg city "$CITY" \
        --arg state "$STATE" \
        --arg zip "$ZIP_CODE" \
        --arg price "$PRICE" \
        --arg bedrooms "$BEDROOMS" \
        --arg bathrooms "$BATHROOMS" \
        --arg sqft "$SQFT" \
        '{
            StandardStatus: "Active",
            ListPrice: ($price | tonumber),
            UnparsedAddress: $address,
            City: $city,
            StateOrProvince: $state,
            PostalCode: $zip,
            BedroomsTotal: ($bedrooms | tonumber),
            BathroomsTotalInteger: ($bathrooms | tonumber),
            LivingArea: ($sqft | tonumber),
            Media: []
        }')

    echo "$MLS_LISTING" | jq .

    # Save MLS listing
    MLS_FILE="mls_listing.json"
    echo "$MLS_LISTING" | jq . > "$MLS_FILE"
    echo ""
    echo "✓ Saved MLS listing to $MLS_FILE"

    echo ""
    echo "============================================================"
    echo "SYNCING TO REAL ESTATE PORTALS"
    echo "============================================================"

    # Simulate portal sync
    for PORTAL in "Zillow" "Realtor.com" "Trulia" "Redfin"; do
        echo "  Syncing to $PORTAL..."
        # In production: curl -X POST "https://${PORTAL}-api.example.com/listings" -d "$MLS_LISTING"
        echo "    ✓ $PORTAL sync completed"
    done

    echo ""
    echo "============================================================"
    echo "SYNDICATION COMPLETE"
    echo "============================================================"
    echo "Listing published to 4 portals:"
    echo "  ✓ Zillow"
    echo "  ✓ Realtor.com"
    echo "  ✓ Trulia"
    echo "  ✓ Redfin"

else
    echo ""
    echo "⚠ Listing requires corrections before publishing ($ERRORS errors)"
fi

echo ""
echo "✓ Real estate listing automation completed!"
