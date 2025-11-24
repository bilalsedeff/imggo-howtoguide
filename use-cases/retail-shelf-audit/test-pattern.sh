#!/bin/bash

# Retail Shelf Audit - curl Example
# Process shelf photos and extract product analytics using bash/curl

set -e

# Configuration
IMGGO_BASE_URL="https://img-go.com/api"
IMGGO_API_KEY="${IMGGO_API_KEY}"
SHELF_AUDIT_PATTERN_ID="${SHELF_AUDIT_PATTERN_ID:-pat_shelf_audit}"

# Check requirements
if [ -z "$IMGGO_API_KEY" ]; then
    echo "Error: IMGGO_API_KEY environment variable not set"
    echo "Usage: export IMGGO_API_KEY=your_api_key"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    echo "Install: sudo apt-get install jq  (Ubuntu/Debian)"
    echo "        brew install jq           (macOS)"
    exit 1
fi

echo "========================================"
echo "Retail Shelf Audit - curl Example"
echo "========================================"

# Example shelf image URL
# In production, this would come from your store cameras or mobile app
IMAGE_URL="https://example.com/shelf-photos/store-123-aisle-5.jpg"

echo -e "\nProcessing shelf image: $IMAGE_URL"

# Generate idempotency key
IDEMPOTENCY_KEY="shelf-audit-$(date +%s)"

# Step 1: Submit image for processing
echo -e "\nStep 1: Submitting image for processing..."

UPLOAD_RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns/${SHELF_AUDIT_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Content-Type: application/json" \
    -H "Idempotency-Key: ${IDEMPOTENCY_KEY}" \
    -d "{\"image_url\": \"${IMAGE_URL}\"}")

echo "Upload response:"
echo "$UPLOAD_RESPONSE" | jq '.'

# Extract job ID
JOB_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.data.job_id')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
    echo "Error: Failed to get job ID"
    echo "Response: $UPLOAD_RESPONSE"
    exit 1
fi

echo -e "\nJob ID: $JOB_ID"

# Step 2: Poll for result
echo -e "\nStep 2: Waiting for shelf audit results..."

MAX_ATTEMPTS=30
WAIT_SECONDS=2
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "  Attempt $ATTEMPT/$MAX_ATTEMPTS..."

    JOB_RESPONSE=$(curl -s -X GET \
        "${IMGGO_BASE_URL}/jobs/${JOB_ID}" \
        -H "Authorization: Bearer ${IMGGO_API_KEY}")

    STATUS=$(echo "$JOB_RESPONSE" | jq -r '.data.status')

    if [ "$STATUS" = "completed" ]; then
        echo -e "\n✓ Shelf audit completed!"

        # Extract result
        RESULT=$(echo "$JOB_RESPONSE" | jq '.data.result')

        echo -e "\nShelf Audit Analytics:"
        echo "======================================"
        echo "$RESULT" | jq '.'

        # Save to file
        OUTPUT_FILE="shelf_audit_result.json"
        echo "$RESULT" | jq '.' > "$OUTPUT_FILE"
        echo -e "\n✓ Saved to $OUTPUT_FILE"

        # Display key metrics
        echo -e "\nKey Metrics:"
        echo "----------------------------------------"
        echo "  Total Products: $(echo "$RESULT" | jq -r '.total_facings // 0')"
        echo "  Unique SKUs: $(echo "$RESULT" | jq '.products | length // 0')"
        echo "  Out of Stock: $(echo "$RESULT" | jq -r '.out_of_stock_count // 0')"

        # Brand share
        echo -e "\n  Brand Share:"
        echo "$RESULT" | jq -r '.brand_share // {} | to_entries[] | "    \(.key): \(.value)%"'

        # Planogram compliance
        COMPLIANCE=$(echo "$RESULT" | jq -r '.planogram_compliance.score // 0')
        echo -e "\n  Planogram Compliance: ${COMPLIANCE}%"

        # Top products
        echo -e "\n  Top Products:"
        echo "$RESULT" | jq -r '.products[0:3][] | "    - \(.name // "Unknown") (\(.brand // "N/A")) - \(.facing_count // 0) facings"'

        exit 0

    elif [ "$STATUS" = "failed" ]; then
        echo -e "\n✗ Shelf audit failed"
        ERROR=$(echo "$JOB_RESPONSE" | jq -r '.data.error // "Unknown error"')
        echo "Error: $ERROR"
        exit 1

    else
        # Still processing
        sleep $WAIT_SECONDS
        ATTEMPT=$((ATTEMPT + 1))
    fi
done

echo -e "\n✗ Timeout: Shelf audit did not complete within $((MAX_ATTEMPTS * WAIT_SECONDS)) seconds"
exit 1
