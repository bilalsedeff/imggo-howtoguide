"""
Simple Invoice Processing Example with ImgGo
Extracts structured data from invoice images
"""

import os
import requests
import time
from pathlib import Path

# Configuration
IMGGO_API_KEY = os.getenv("IMGGO_API_KEY", "your_api_key_here")
IMGGO_BASE_URL = "https://img-go.com/api"

# Pattern ID - read from env var or pattern_id.txt
def get_pattern_id():
    pattern_id = os.getenv("INVOICE_PATTERN_ID")
    if pattern_id:
        return pattern_id
    # Try reading from pattern_id.txt
    pattern_file = Path(__file__).parent / "pattern_id.txt"
    if pattern_file.exists():
        return pattern_file.read_text().strip()
    return None

INVOICE_PATTERN_ID = get_pattern_id()


def process_invoice(image_path):
    """
    Process an invoice image and extract structured data

    Args:
        image_path: Path to invoice image file

    Returns:
        dict: Extracted invoice data
    """
    print(f"Processing invoice: {image_path}")

    # Step 1: Upload image directly to ImgGo
    import mimetypes
    filename = Path(image_path).name
    mime_type, _ = mimetypes.guess_type(image_path)

    with open(image_path, 'rb') as f:
        files = {'image': (filename, f, mime_type or 'image/jpeg')}

        response = requests.post(
            f"{IMGGO_BASE_URL}/patterns/{INVOICE_PATTERN_ID}/ingest",
            headers={
                "Authorization": f"Bearer {IMGGO_API_KEY}",
                "Idempotency-Key": f"invoice-{Path(image_path).stem}-{int(time.time())}"
            },
            files=files
        )

    response.raise_for_status()
    job_data = response.json()

    job_id = job_data["data"]["job_id"]
    print(f"Job submitted: {job_id}")

    # Step 2: Poll for results
    result = poll_for_result(job_id)

    return result


def poll_for_result(job_id, max_attempts=30, wait_seconds=2):
    """
    Poll ImgGo API until job completes

    Args:
        job_id: Job ID from ingestion request
        max_attempts: Maximum number of polling attempts
        wait_seconds: Seconds to wait between attempts

    Returns:
        dict: Processed result data
    """
    for attempt in range(max_attempts):
        response = requests.get(
            f"{IMGGO_BASE_URL}/jobs/{job_id}",
            headers={"Authorization": f"Bearer {IMGGO_API_KEY}"}
        )

        response.raise_for_status()
        job_status = response.json()

        status = job_status["data"]["status"]

        if status in ("completed", "succeeded"):
            print(f"V Processing complete!")
            # API returns result in "manifest" field for succeeded jobs
            return job_status["data"].get("manifest") or job_status["data"].get("result")
        elif status == "failed":
            error = job_status["data"].get("error", "Unknown error")
            raise Exception(f"Job failed: {error}")

        print(f"Status: {status}, waiting... ({attempt + 1}/{max_attempts})")
        time.sleep(wait_seconds)

    raise Exception(f"Job timeout after {max_attempts * wait_seconds} seconds")


def main():
    """
    Example usage: Process a sample invoice
    """
    # Get path to test invoice
    test_invoice = Path(__file__).parent.parent.parent / "examples" / "test-images" / "invoice1.jpg"

    if not test_invoice.exists():
        print(f"Error: Test invoice not found at {test_invoice}")
        print("Please ensure test-images/invoice1.jpg exists")
        return

    try:
        # Process the invoice
        invoice_data = process_invoice(str(test_invoice))

        # Display results
        print("\n" + "="*50)
        print("EXTRACTED INVOICE DATA")
        print("="*50)

        # If result is JSON string, parse it
        import json
        if isinstance(invoice_data, str):
            invoice_data = json.loads(invoice_data)

        print(json.dumps(invoice_data, indent=2))

        # Save to file
        output_file = Path("invoice_output.json")
        with open(output_file, 'w') as f:
            json.dump(invoice_data, f, indent=2)

        print(f"\nV Results saved to {output_file}")

    except Exception as e:
        print(f"\nX Error processing invoice: {e}")
        raise


if __name__ == "__main__":
    main()
