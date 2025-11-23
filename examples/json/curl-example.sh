#!/bin/bash

# ImgGo JSON Output - curl Example
# Process images and get JSON results using pure bash and curl

set -e

# Configuration
IMGGO_BASE_URL="https://img-go.com/api"
IMGGO_API_KEY="${IMGGO_API_KEY}"
INVOICE_PATTERN_ID="${INVOICE_PATTERN_ID:-pat_invoice_json}"

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
echo "ImgGo JSON Extraction - curl Example"
echo "========================================"

# Find test image
TEST_IMAGE="../../test-images/invoice1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "Error: Test image not found: $TEST_IMAGE"
    exit 1
fi

echo -e "\nProcessing: $TEST_IMAGE"

# Generate idempotency key
IDEMPOTENCY_KEY="curl-example-$(date +%s)"

# Step 1: Upload image to ImgGo
echo -e "\nStep 1: Uploading image..."

UPLOAD_RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns/${INVOICE_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Idempotency-Key: ${IDEMPOTENCY_KEY}" \
    -F "file=@${TEST_IMAGE}")

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
echo -e "\nStep 2: Polling for result..."

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
        echo -e "\n✓ Processing completed!"

        # Extract result
        RESULT=$(echo "$JOB_RESPONSE" | jq '.data.result')

        echo -e "\nExtracted Invoice Data (JSON):"
        echo "======================================"
        echo "$RESULT" | jq '.'

        # Save to file
        OUTPUT_FILE="invoice_result.json"
        echo "$RESULT" | jq '.' > "$OUTPUT_FILE"
        echo -e "\n✓ Saved to $OUTPUT_FILE"

        # Display key fields
        echo -e "\nKey Fields:"
        echo "  Invoice Number: $(echo "$RESULT" | jq -r '.invoice_number // "N/A"')"
        echo "  Vendor: $(echo "$RESULT" | jq -r '.vendor.name // .vendor // "N/A"')"
        echo "  Total Amount: \$$(echo "$RESULT" | jq -r '.total_amount // "N/A"')"
        echo "  Invoice Date: $(echo "$RESULT" | jq -r '.invoice_date // "N/A"')"
        echo "  Due Date: $(echo "$RESULT" | jq -r '.due_date // "N/A"')"

        # Count line items
        LINE_ITEMS=$(echo "$RESULT" | jq '.line_items | length // 0')
        echo "  Line Items: $LINE_ITEMS"

        exit 0

    elif [ "$STATUS" = "failed" ]; then
        echo -e "\n✗ Processing failed"
        ERROR=$(echo "$JOB_RESPONSE" | jq -r '.data.error // "Unknown error"')
        echo "Error: $ERROR"
        exit 1

    else
        # Still processing
        sleep $WAIT_SECONDS
        ATTEMPT=$((ATTEMPT + 1))
    fi
done

echo -e "\n✗ Timeout: Job did not complete within $((MAX_ATTEMPTS * WAIT_SECONDS)) seconds"
exit 1
