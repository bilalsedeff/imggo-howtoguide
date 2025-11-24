#!/bin/bash

# Simple Resume Parsing Test
# Test the pattern with a sample resume image

IMGGO_API_KEY="${IMGGO_API_KEY}"
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"
RESUME_PATTERN_ID="${RESUME_PATTERN_ID}"

echo "============================================================"
echo "TESTING RESUME PARSING PATTERN"
echo "============================================================"

if [ -z "$IMGGO_API_KEY" ]; then
    echo ""
    echo "X Error: IMGGO_API_KEY not set"
    echo "Please set your API key in .env file"
    exit 1
fi

if [ -z "$RESUME_PATTERN_ID" ]; then
    echo ""
    echo "X Error: RESUME_PATTERN_ID not set"
    echo "Run create-pattern.sh first to create a pattern"
    exit 1
fi

TEST_IMAGE="../../test-images/resume1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo ""
    echo "X Error: Test image not found: $TEST_IMAGE"
    exit 1
fi

echo ""
echo "Pattern ID: ${RESUME_PATTERN_ID}"
echo "Test Image: resume1.jpg"
echo ""

# Upload and process image
echo "Processing resume image..."

INGEST_RESPONSE=$(curl -s -X POST "${IMGGO_BASE_URL}/patterns/${RESUME_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -F "image=@${TEST_IMAGE}")

JOB_ID=$(echo "$INGEST_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo "X Error: Failed to create job"
    echo "$INGEST_RESPONSE"
    exit 1
fi

echo "V Job created: ${JOB_ID}"

# Poll for completion
MAX_ATTEMPTS=60
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    sleep 2

    JOB_RESPONSE=$(curl -s -X GET "${IMGGO_BASE_URL}/jobs/${JOB_ID}" \
        -H "Authorization: Bearer ${IMGGO_API_KEY}")

    STATUS=$(echo "$JOB_RESPONSE" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ "$STATUS" = "succeeded" ] || [ "$STATUS" = "completed" ]; then
        echo "V Processing completed!"
        echo ""

        # Extract result
        RESULT=$(echo "$JOB_RESPONSE" | sed -n 's/.*"manifest":"\([^"]*\)".*/\1/p')
        if [ -z "$RESULT" ]; then
            RESULT=$(echo "$JOB_RESPONSE" | sed -n 's/.*"result":"\([^"]*\)".*/\1/p')
        fi

        # Save to outputs folder
        mkdir -p outputs
        echo "$RESULT" | sed 's/\\n/\n/g' | sed 's/\\"/"/g' > outputs/resume1_output.txt

        echo "V Output saved to: outputs/resume1_output.txt"
        echo ""

        # Display first part
        echo "============================================================"
        echo "EXTRACTED TEXT (first 500 chars)"
        echo "============================================================"
        echo "$RESULT" | sed 's/\\n/\n/g' | head -c 500
        echo ""
        echo "..."
        echo ""

        echo "V Test completed successfully!"
        exit 0

    elif [ "$STATUS" = "failed" ]; then
        echo "X Error: Job failed"
        echo "$JOB_RESPONSE"
        exit 1
    fi

    echo "Attempt ${ATTEMPT}/${MAX_ATTEMPTS}: Status = ${STATUS}"
    ATTEMPT=$((ATTEMPT + 1))
done

echo "X Error: Timeout waiting for job completion"
exit 1
