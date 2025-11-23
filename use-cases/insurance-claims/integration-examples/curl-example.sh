#!/bin/bash

###############################################################################
# Insurance Claims Processing - curl Example
# Extract insurance claim data from images using ImgGo API
###############################################################################

set -e  # Exit on error

# Configuration
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"
INSURANCE_CLAIMS_PATTERN_ID="${INSURANCE_CLAIMS_PATTERN_ID:-pat_insurance_claim_json}"

# Check for API key
if [ -z "$IMGGO_API_KEY" ]; then
    echo "Error: IMGGO_API_KEY environment variable not set"
    exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    echo "Install with: sudo apt-get install jq (Ubuntu/Debian) or brew install jq (macOS)"
    exit 1
fi

# Test image path
TEST_IMAGE="../../../test-images/insurance-claim1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "Warning: Test image not found: $TEST_IMAGE"
    echo "Using placeholder for demonstration"
    exit 1
fi

echo "============================================================"
echo "INSURANCE CLAIMS PROCESSING - CURL EXAMPLE"
echo "============================================================"

# Generate idempotency key
IDEMPOTENCY_KEY="claim-$(date +%s)"

echo ""
echo "Step 1: Uploading insurance claim image..."

# Upload claim
UPLOAD_RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns/${INSURANCE_CLAIMS_PATTERN_ID}/ingest" \
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
CLAIM_DATA=$(echo "$JOB_RESPONSE" | jq '.data.result')

# Save raw JSON
OUTPUT_FILE="claim_data.json"
echo "$CLAIM_DATA" | jq . > "$OUTPUT_FILE"
echo ""
echo "✓ Saved claim data to $OUTPUT_FILE"

echo ""
echo "============================================================"
echo "EXTRACTED CLAIM DATA"
echo "============================================================"

# Parse claim data
CLAIM_NUMBER=$(echo "$CLAIM_DATA" | jq -r '.claim_number')
POLICY_NUMBER=$(echo "$CLAIM_DATA" | jq -r '.policy_number')
CLAIMANT_NAME=$(echo "$CLAIM_DATA" | jq -r '.claimant_name')
CLAIM_TYPE=$(echo "$CLAIM_DATA" | jq -r '.claim_type')
INCIDENT_DATE=$(echo "$CLAIM_DATA" | jq -r '.incident_date')
DESCRIPTION=$(echo "$CLAIM_DATA" | jq -r '.description // "Not specified"')

echo "Claim Number: $CLAIM_NUMBER"
echo "Policy Number: $POLICY_NUMBER"
echo "Claimant: $CLAIMANT_NAME"
echo "Claim Type: $CLAIM_TYPE"
echo "Incident Date: $INCIDENT_DATE"
echo "Description: $DESCRIPTION"

# Calculate total amount
TOTAL_AMOUNT=$(echo "$CLAIM_DATA" | jq '[.line_items[]? | (.amount * (.quantity // 1))] | add // 0')
echo "Total Amount: \$$TOTAL_AMOUNT"

echo ""
echo "============================================================"
echo "VALIDATION"
echo "============================================================"

# Simple validation
ERRORS=0
WARNINGS=0
RISK_FLAGS=0

if [ -z "$CLAIM_NUMBER" ] || [ "$CLAIM_NUMBER" = "null" ]; then
    echo "✗ Missing claim number"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "$POLICY_NUMBER" ] || [ "$POLICY_NUMBER" = "null" ]; then
    echo "✗ Missing policy number"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "$CLAIMANT_NAME" ] || [ "$CLAIMANT_NAME" = "null" ]; then
    echo "✗ Missing claimant name"
    ERRORS=$((ERRORS + 1))
fi

# Check amount
if (( $(echo "$TOTAL_AMOUNT > 50000" | bc -l) )); then
    echo "⚠ High value claim: \$$TOTAL_AMOUNT - requires senior adjuster review"
    RISK_FLAGS=$((RISK_FLAGS + 1))
fi

if [ $ERRORS -eq 0 ]; then
    echo "✓ Basic validation passed"
fi

echo ""
echo "============================================================"
echo "CLAIM ROUTING"
echo "============================================================"

# Determine priority
if [ $RISK_FLAGS -gt 0 ]; then
    PRIORITY="HIGH"
elif (( $(echo "$TOTAL_AMOUNT > 10000" | bc -l) )); then
    PRIORITY="MEDIUM"
else
    PRIORITY="LOW - Standard Processing"
fi

echo "Priority: $PRIORITY"

# Assign adjuster based on claim type
case "$CLAIM_TYPE" in
    *auto*|*vehicle*)
        TEAM="Auto Claims"
        ;;
    *property*|*home*)
        TEAM="Property Claims"
        ;;
    *)
        TEAM="General Claims"
        ;;
esac

echo "Assigned Team: $TEAM"

if [ "$PRIORITY" = "HIGH" ]; then
    echo "Assigned Adjuster: Senior Team (Auto-assign)"
else
    echo "Assigned Adjuster: ${TEAM} (Auto-assign)"
fi

echo ""
echo "============================================================"
echo "CLAIM ADJUSTER SUMMARY"
echo "============================================================"

# Generate adjuster summary
SUMMARY_FILE="adjuster_summary.txt"
cat > "$SUMMARY_FILE" <<EOF
CLAIM ADJUSTER SUMMARY
============================================================
Claim Number: $CLAIM_NUMBER
Policy Number: $POLICY_NUMBER
Priority: $PRIORITY
Assigned Team: $TEAM

CLAIMANT INFORMATION
  Name: $CLAIMANT_NAME

INCIDENT DETAILS
  Date: $INCIDENT_DATE
  Type: $CLAIM_TYPE
  Description: $DESCRIPTION

FINANCIAL SUMMARY
  Total Claimed: \$$TOTAL_AMOUNT

RECOMMENDED ACTIONS:
  [ ] Contact claimant for details
  [ ] Review policy coverage
  [ ] Inspect damaged property (if applicable)
  [ ] Obtain repair estimates
EOF

if [ $ERRORS -gt 0 ]; then
    echo "  [ ] Obtain missing information" >> "$SUMMARY_FILE"
fi

if [ $RISK_FLAGS -gt 0 ]; then
    echo "  [ ] Request senior review" >> "$SUMMARY_FILE"
fi

cat "$SUMMARY_FILE"

echo ""
echo "✓ Saved adjuster summary to $SUMMARY_FILE"

echo ""
echo "============================================================"
echo "SAVING TO CLAIMS MANAGEMENT SYSTEM"
echo "============================================================"

# Prepare API payload
API_PAYLOAD=$(jq -n \
    --arg claim_number "$CLAIM_NUMBER" \
    --arg policy_number "$POLICY_NUMBER" \
    --arg claim_type "$CLAIM_TYPE" \
    --arg claimant_name "$CLAIMANT_NAME" \
    --arg incident_date "$INCIDENT_DATE" \
    --arg description "$DESCRIPTION" \
    --arg total_amount "$TOTAL_AMOUNT" \
    --arg team "$TEAM" \
    --arg priority "$PRIORITY" \
    '{
        claim_info: {
            claim_number: $claim_number,
            policy_number: $policy_number,
            claim_type: $claim_type,
            status: "OPEN"
        },
        claimant: {
            name: $claimant_name
        },
        incident: {
            date: $incident_date,
            description: $description
        },
        financial: {
            claimed_amount: ($total_amount | tonumber)
        },
        assignment: {
            team: $team,
            priority: $priority
        }
    }')

echo "API Payload:"
echo "$API_PAYLOAD" | jq .

# In production, send to claims system:
# curl -X POST "https://claims-system.example.com/api/claims" \
#     -H "Content-Type: application/json" \
#     -d "$API_PAYLOAD"

echo ""
echo "✓ Claim saved to CMS (simulated)"
echo ""
echo "✓ Insurance claim processing completed!"
