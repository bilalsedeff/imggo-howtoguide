#!/bin/bash

###############################################################################
# Invoice Processing with ImgGo - curl Example
# This script demonstrates how to use ImgGo API with pure curl commands
###############################################################################

set -e  # Exit on error

# Configuration
IMGGO_API_KEY="${IMGGO_API_KEY:-your_api_key_here}"
IMGGO_BASE_URL="https://img-go.com/api"
INVOICE_PATTERN_ID="${INVOICE_PATTERN_ID:-pat_invoice_example}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "ImgGo Invoice Processing - curl Example"
echo "=================================================="

# Find test image
TEST_IMAGE="../../../test-images/invoice1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo -e "${RED}✗ Error: Test image not found at $TEST_IMAGE${NC}"
    echo "Please ensure test-images/invoice1.jpg exists"
    exit 1
fi

echo -e "${GREEN}✓${NC} Using test image: $TEST_IMAGE"

# Step 1: Upload image and create job
echo ""
echo "Step 1: Uploading invoice to ImgGo..."
echo "---------------------------------------"

IDEMPOTENCY_KEY="invoice-curl-$(date +%s)"

UPLOAD_RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns/${INVOICE_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Idempotency-Key: ${IDEMPOTENCY_KEY}" \
    -F "file=@${TEST_IMAGE}")

echo "Response:"
echo "$UPLOAD_RESPONSE" | jq '.'

# Extract job ID
JOB_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.data.job_id')

if [ "$JOB_ID" == "null" ] || [ -z "$JOB_ID" ]; then
    echo -e "${RED}✗ Error: Failed to get job ID${NC}"
    echo "Response: $UPLOAD_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓${NC} Job created: $JOB_ID"

# Step 2: Poll for results
echo ""
echo "Step 2: Polling for results..."
echo "---------------------------------------"

MAX_ATTEMPTS=30
WAIT_SECONDS=2

for ((i=1; i<=MAX_ATTEMPTS; i++)); do
    STATUS_RESPONSE=$(curl -s -X GET \
        "${IMGGO_BASE_URL}/jobs/${JOB_ID}" \
        -H "Authorization: Bearer ${IMGGO_API_KEY}")

    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.data.status')

    if [ "$STATUS" == "completed" ]; then
        echo -e "${GREEN}✓ Processing complete!${NC}"
        echo ""
        echo "=================================================="
        echo "EXTRACTED INVOICE DATA"
        echo "=================================================="

        # Extract and display result
        echo "$STATUS_RESPONSE" | jq '.data.result'

        # Save to file
        echo "$STATUS_RESPONSE" | jq '.data.result' > invoice_output.json
        echo ""
        echo -e "${GREEN}✓${NC} Results saved to invoice_output.json"

        exit 0

    elif [ "$STATUS" == "failed" ]; then
        echo -e "${RED}✗ Job failed${NC}"
        echo "$STATUS_RESPONSE" | jq '.data.error'
        exit 1

    else
        echo -e "${YELLOW}Status: $STATUS${NC}, waiting... ($i/$MAX_ATTEMPTS)"
        sleep $WAIT_SECONDS
    fi
done

echo -e "${RED}✗ Timeout: Job did not complete within $((MAX_ATTEMPTS * WAIT_SECONDS)) seconds${NC}"
exit 1
