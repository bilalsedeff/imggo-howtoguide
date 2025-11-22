"""
Invoice Processing with URL Method
Process invoices from publicly accessible URLs (e.g., S3, Cloud Storage)
"""

import os
import requests
import time
import json

# Configuration
IMGGO_API_KEY = os.getenv("IMGGO_API_KEY", "your_api_key_here")
IMGGO_BASE_URL = "https://img-go.com/api"
INVOICE_PATTERN_ID = os.getenv("INVOICE_PATTERN_ID", "pat_invoice_example")


def process_invoice_from_url(image_url):
    """
    Process an invoice from a publicly accessible URL

    Args:
        image_url: Public URL to invoice image (S3, Dropbox, etc.)

    Returns:
        dict: Extracted invoice data
    """
    print(f"Processing invoice from URL: {image_url}")

    # Step 1: Submit URL to ImgGo (no file upload needed!)
    response = requests.post(
        f"{IMGGO_BASE_URL}/patterns/{INVOICE_PATTERN_ID}/ingest",
        headers={
            "Authorization": f"Bearer {IMGGO_API_KEY}",
            "Content-Type": "application/json",
            "Idempotency-Key": f"invoice-url-{hash(image_url)}-{int(time.time())}"
        },
        json={
            "image_url": image_url
        }
    )

    response.raise_for_status()
    job_data = response.json()

    job_id = job_data["data"]["job_id"]
    print(f"Job submitted: {job_id}")

    # Step 2: Poll for results
    result = poll_for_result(job_id)

    return result


def poll_for_result(job_id, max_attempts=30, wait_seconds=2):
    """Poll ImgGo API until job completes"""
    for attempt in range(max_attempts):
        response = requests.get(
            f"{IMGGO_BASE_URL}/jobs/{job_id}",
            headers={"Authorization": f"Bearer {IMGGO_API_KEY}"}
        )

        response.raise_for_status()
        job_status = response.json()

        status = job_status["data"]["status"]

        if status == "completed":
            print(f"✓ Processing complete!")
            return job_status["data"]["result"]
        elif status == "failed":
            error = job_status["data"].get("error", "Unknown error")
            raise Exception(f"Job failed: {error}")

        print(f"Status: {status}, waiting... ({attempt + 1}/{max_attempts})")
        time.sleep(wait_seconds)

    raise Exception(f"Job timeout after {max_attempts * wait_seconds} seconds")


def main():
    """
    Example: Process invoice from public URL
    """
    # Example invoice URLs (you can use your own S3, Dropbox, etc.)
    example_invoices = [
        # Sample invoice URLs (replace with your actual URLs)
        "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/pdf.traineddata",
        # Add your S3/Cloud Storage URLs here
    ]

    # For demonstration, using a sample URL
    test_url = "https://raw.githubusercontent.com/sampledocs/invoice-samples/main/invoice-001.jpg"

    print("\n" + "="*60)
    print("INVOICE URL PROCESSING EXAMPLE")
    print("="*60)
    print(f"\nProcessing invoice from: {test_url}\n")

    try:
        # Process the invoice
        invoice_data = process_invoice_from_url(test_url)

        # Display results
        print("\n" + "="*60)
        print("EXTRACTED INVOICE DATA")
        print("="*60)

        # Parse if result is JSON string
        if isinstance(invoice_data, str):
            invoice_data = json.loads(invoice_data)

        print(json.dumps(invoice_data, indent=2))

        # Save to file
        with open('invoice_url_output.json', 'w') as f:
            json.dump(invoice_data, f, indent=2)

        print(f"\n✓ Results saved to invoice_url_output.json")

    except Exception as e:
        print(f"\n✗ Error processing invoice: {e}")
        raise


if __name__ == "__main__":
    main()
