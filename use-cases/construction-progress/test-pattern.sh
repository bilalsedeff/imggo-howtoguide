#!/bin/bash
# Construction Progress Test - Shell Script Example
# Demonstrates ImgGo API usage with curl for YAML format

set -e

echo "============================================================"
echo "TESTING CONSTRUCTION PROGRESS PATTERN (Shell/curl)"
echo "============================================================"

# Check for API key
if [ -z "$IMGGO_API_KEY" ]; then
    echo ""
    echo "X Error: IMGGO_API_KEY not set"
    echo "Please set your API key: export IMGGO_API_KEY=your_key_here"
    exit 1
fi

# Get pattern ID from file or environment
PATTERN_ID="${CONSTRUCTION_PATTERN_ID:-$(cat pattern_id.txt 2>/dev/null || echo '')}"
if [ -z "$PATTERN_ID" ]; then
    echo ""
    echo "X Error: CONSTRUCTION_PATTERN_ID not set"
    echo "Run create-pattern.py first to create a pattern"
    exit 1
fi

# Test image path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_IMAGE="$SCRIPT_DIR/../../examples/test-images/construction1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo ""
    echo "X Error: Test image not found: $TEST_IMAGE"
    exit 1
fi

echo ""
echo "Pattern ID: $PATTERN_ID"
echo "Test Image: construction1.jpg"
echo ""

# Submit image to ImgGo
echo "Submitting construction image..."
RESPONSE=$(curl -s -X POST "https://img-go.com/api/patterns/$PATTERN_ID/ingest" \
    -H "Authorization: Bearer $IMGGO_API_KEY" \
    -H "Idempotency-Key: construction-shell-test-$(date +%s)" \
    -F "image=@$TEST_IMAGE")

JOB_ID=$(echo "$RESPONSE" | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
    echo "X Error: Failed to submit image"
    echo "$RESPONSE"
    exit 1
fi

echo "Job submitted: $JOB_ID"
echo "Polling for results..."

# Poll for results
for i in {1..30}; do
    RESULT=$(curl -s "https://img-go.com/api/jobs/$JOB_ID" \
        -H "Authorization: Bearer $IMGGO_API_KEY")

    STATUS=$(echo "$RESULT" | grep -o '"status":"[^"]*' | cut -d'"' -f4)

    if [ "$STATUS" = "succeeded" ] || [ "$STATUS" = "completed" ]; then
        echo "V Processing complete!"
        echo ""

        # Save result
        mkdir -p outputs
        echo "$RESULT" > outputs/construction_shell_output.yaml

        echo "V Output saved to: outputs/construction_shell_output.yaml"
        echo ""
        echo "============================================================"
        echo "RESULT (YAML FORMAT)"
        echo "============================================================"
        echo "$RESULT" | head -c 500
        echo ""
        echo ""
        echo "V Test completed successfully!"
        exit 0
    elif [ "$STATUS" = "failed" ]; then
        echo "X Job failed"
        echo "$RESULT"
        exit 1
    fi

    echo "Status: $STATUS, waiting... ($i/30)"
    sleep 2
done

echo "X Timeout waiting for result"
exit 1
