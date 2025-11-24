"""
URL Processing Example

Process images from public URLs (S3, CDN, cloud storage, etc.)
instead of uploading files directly.

Usage:
    python url-processing.py https://example.com/image.jpg PATTERN_ID
"""

import os
import sys
import time
import requests

# Configuration
IMGGO_API_KEY = os.getenv("IMGGO_API_KEY")
IMGGO_BASE_URL = os.getenv("IMGGO_BASE_URL", "https://img-go.com/api")


def process_image_url(image_url: str, pattern_id: str) -> dict:
    """
    Process an image from a URL.

    Args:
        image_url: Public URL to the image
        pattern_id: Pattern ID to use for extraction

    Returns:
        dict: Extracted data from the image
    """
    if not IMGGO_API_KEY:
        raise ValueError("IMGGO_API_KEY environment variable not set")

    print(f"Processing URL: {image_url}")

    # Step 1: Submit URL for processing
    response = requests.post(
        f"{IMGGO_BASE_URL}/patterns/{pattern_id}/ingest",
        headers={
            "Authorization": f"Bearer {IMGGO_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "image_url": image_url
        }
    )

    response.raise_for_status()
    data = response.json()

    job_id = data["data"]["job_id"]
    print(f"Job created: {job_id}")

    # Step 2: Poll for results
    print("Waiting for processing...")
    result = poll_job(job_id)

    print("Processing completed!")
    return result


def poll_job(job_id: str, max_attempts: int = 60, interval: int = 2) -> dict:
    """Poll a job until it completes"""
    for attempt in range(max_attempts):
        response = requests.get(
            f"{IMGGO_BASE_URL}/jobs/{job_id}",
            headers={
                "Authorization": f"Bearer {IMGGO_API_KEY}"
            }
        )

        response.raise_for_status()
        data = response.json()["data"]

        status = data["status"]
        print(f"  Attempt {attempt + 1}/{max_attempts}: {status}")

        if status == "succeeded":
            return data.get("manifest") or data.get("result")

        elif status == "failed":
            error = data.get("error", "Unknown error")
            raise Exception(f"Job failed: {error}")

        time.sleep(interval)

    raise Exception(f"Job timeout after {max_attempts * interval} seconds")


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python url-processing.py <image_url> <pattern_id>")
        print("\nExample:")
        print("  python url-processing.py https://cdn.example.com/invoice.jpg pat_abc123")
        sys.exit(1)

    image_url = sys.argv[1]
    pattern_id = sys.argv[2]

    # Validate URL
    if not image_url.startswith(('http://', 'https://')):
        print("Error: Image URL must start with http:// or https://")
        sys.exit(1)

    try:
        result = process_image_url(image_url, pattern_id)

        print("\n" + "="*60)
        print("EXTRACTED DATA")
        print("="*60)
        print(result)
        print()

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
