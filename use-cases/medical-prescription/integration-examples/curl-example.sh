#!/bin/bash

###############################################################################
# Medical Prescription Processing - curl Example
# Extract prescription data from images using ImgGo API
###############################################################################

set -e  # Exit on error

# Configuration
IMGGO_BASE_URL="${IMGGO_BASE_URL:-https://img-go.com/api}"
PRESCRIPTION_PATTERN_ID="${PRESCRIPTION_PATTERN_ID:-pat_prescription_text}"

# Check for API key
if [ -z "$IMGGO_API_KEY" ]; then
    echo "Error: IMGGO_API_KEY environment variable not set"
    exit 1
fi

# Test image path
TEST_IMAGE="../../../test-images/medical-prescription1.jpg"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "Warning: Test image not found: $TEST_IMAGE"
    echo "Using placeholder for demonstration"
    exit 1
fi

echo "============================================================"
echo "MEDICAL PRESCRIPTION PROCESSING - CURL EXAMPLE"
echo "============================================================"

# Generate idempotency key
IDEMPOTENCY_KEY="prescription-$(date +%s)"

echo ""
echo "Step 1: Uploading prescription image..."

# Upload prescription
UPLOAD_RESPONSE=$(curl -s -X POST \
    "${IMGGO_BASE_URL}/patterns/${PRESCRIPTION_PATTERN_ID}/ingest" \
    -H "Authorization: Bearer ${IMGGO_API_KEY}" \
    -H "Idempotency-Key: ${IDEMPOTENCY_KEY}" \
    -F "file=@${TEST_IMAGE}")

# Extract job ID
JOB_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$JOB_ID" ]; then
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

    STATUS=$(echo "$JOB_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

    if [ "$STATUS" = "completed" ]; then
        echo "✓ Processing completed"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "Error: Job failed"
        echo "$JOB_RESPONSE"
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
PRESCRIPTION_TEXT=$(echo "$JOB_RESPONSE" | grep -o '"result":"[^"]*"' | cut -d'"' -f4 | sed 's/\\n/\n/g')

# Save raw text
OUTPUT_FILE="prescription_raw.txt"
echo "$PRESCRIPTION_TEXT" > "$OUTPUT_FILE"
echo ""
echo "✓ Saved raw text to $OUTPUT_FILE"

echo ""
echo "============================================================"
echo "EXTRACTED PRESCRIPTION DATA"
echo "============================================================"

# Parse prescription (simplified bash parsing)
PATIENT_NAME=$(echo "$PRESCRIPTION_TEXT" | grep -i "Patient:" | sed 's/Patient://i' | xargs)
PATIENT_DOB=$(echo "$PRESCRIPTION_TEXT" | grep -i "DOB:" | sed 's/DOB://i' | xargs)
PRESCRIBER=$(echo "$PRESCRIPTION_TEXT" | grep -i "Prescriber:" | sed 's/Prescriber://i' | xargs)
LICENSE=$(echo "$PRESCRIPTION_TEXT" | grep -i "License:" | sed 's/License://i' | xargs)
DATE=$(echo "$PRESCRIPTION_TEXT" | grep -i "Date:" | head -1 | sed 's/Date://i' | xargs)

echo "Patient: $PATIENT_NAME"
echo "DOB: $PATIENT_DOB"
echo "Prescriber: $PRESCRIBER"
echo "License: $LICENSE"
echo "Date: $DATE"

echo ""
echo "Medications:"
echo "$PRESCRIPTION_TEXT" | grep -i "^Rx:" || echo "  (Parse medications from text)"

echo ""
echo "============================================================"
echo "VALIDATION"
echo "============================================================"

# Simple validation
ERRORS=0

if [ -z "$PATIENT_NAME" ]; then
    echo "✗ Missing patient name"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "$PRESCRIBER" ]; then
    echo "✗ Missing prescriber information"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -eq 0 ]; then
    echo "✓ Basic validation passed"

    echo ""
    echo "============================================================"
    echo "PHARMACIST FILL INSTRUCTIONS"
    echo "============================================================"
    echo "Patient: $PATIENT_NAME"
    echo "DOB: $PATIENT_DOB"
    echo ""
    echo "Prescriber: $PRESCRIBER"
    echo "License: $LICENSE"
    echo "Date: $DATE"
    echo ""
    echo "VERIFICATION CHECKLIST:"
    echo "  [ ] Patient ID verified"
    echo "  [ ] Insurance checked"
    echo "  [ ] Drug interactions reviewed"
    echo "  [ ] Prescriber credentials confirmed"
    echo "  [ ] Patient counseling completed"

    # Save fill instructions
    INSTRUCTIONS_FILE="fill_instructions.txt"
    cat > "$INSTRUCTIONS_FILE" <<EOF
PHARMACIST FILL INSTRUCTIONS
============================================================
Patient: $PATIENT_NAME
DOB: $PATIENT_DOB

Prescriber: $PRESCRIBER
License: $LICENSE
Date: $DATE

VERIFICATION CHECKLIST:
  [ ] Patient ID verified
  [ ] Insurance checked
  [ ] Drug interactions reviewed
  [ ] Prescriber credentials confirmed
  [ ] Patient counseling completed
EOF

    echo ""
    echo "✓ Saved fill instructions to $INSTRUCTIONS_FILE"
else
    echo "⚠ Prescription requires manual review ($ERRORS errors)"
fi

echo ""
echo "✓ Prescription processing completed!"
