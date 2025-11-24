"""
Error Handling and Retry Logic

Production-ready example with proper error handling,
exponential backoff, and retry logic.

Usage:
    python error-handling.py path/to/image.jpg PATTERN_ID
"""

import os
import sys
import time
import requests
from typing import Optional, Dict, Any


# Configuration
IMGGO_API_KEY = os.getenv("IMGGO_API_KEY")
IMGGO_BASE_URL = os.getenv("IMGGO_BASE_URL", "https://img-go.com/api")


class ImgGoError(Exception):
    """Base exception for ImgGo API errors"""
    pass


class RateLimitError(ImgGoError):
    """Raised when rate limit is exceeded"""
    pass


class JobFailedError(ImgGoError):
    """Raised when job processing fails"""
    pass


def upload_with_retry(
    image_path: str,
    pattern_id: str,
    max_retries: int = 3
) -> dict:
    """
    Upload an image with automatic retry on failure.

    Args:
        image_path: Path to the image file
        pattern_id: Pattern ID to use
        max_retries: Maximum number of retry attempts

    Returns:
        dict: Extracted data

    Raises:
        ImgGoError: If all retries fail
    """
    if not IMGGO_API_KEY:
        raise ValueError("IMGGO_API_KEY environment variable not set")

    for attempt in range(max_retries):
        try:
            print(f"Upload attempt {attempt + 1}/{max_retries}")

            # Upload image
            import mimetypes
            mime_type, _ = mimetypes.guess_type(image_path)

            with open(image_path, 'rb') as f:
                response = requests.post(
                    f"{IMGGO_BASE_URL}/patterns/{pattern_id}/ingest",
                    headers={
                        "Authorization": f"Bearer {IMGGO_API_KEY}",
                        "Idempotency-Key": f"upload-{image_path}-{pattern_id}"
                    },
                    files={"image": (os.path.basename(image_path), f, mime_type or 'image/jpeg')},
                    timeout=30
                )

            # Handle different HTTP status codes
            if response.status_code == 429:
                # Rate limit - wait and retry
                retry_after = int(response.headers.get("Retry-After", 60))
                print(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue

            elif response.status_code >= 500:
                # Server error - retry with exponential backoff
                wait_time = 2 ** attempt
                print(f"Server error. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            elif response.status_code >= 400:
                # Client error - don't retry
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                raise ImgGoError(f"Client error: {error_msg}")

            # Success
            response.raise_for_status()
            data = response.json()
            job_id = data["data"]["job_id"]

            print(f"Job created: {job_id}")

            # Poll for results
            result = poll_with_retry(job_id)
            return result

        except requests.exceptions.Timeout:
            print(f"Request timeout. Retrying...")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise ImgGoError("Max retries exceeded due to timeouts")

        except requests.exceptions.ConnectionError:
            print(f"Connection error. Retrying...")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise ImgGoError("Max retries exceeded due to connection errors")

    raise ImgGoError("Max retries exceeded")


def poll_with_retry(job_id: str, max_attempts: int = 60) -> dict:
    """
    Poll a job with error handling.

    Args:
        job_id: Job ID to poll
        max_attempts: Maximum polling attempts

    Returns:
        dict: Extracted data

    Raises:
        JobFailedError: If job processing fails
    """
    for attempt in range(max_attempts):
        try:
            response = requests.get(
                f"{IMGGO_BASE_URL}/jobs/{job_id}",
                headers={
                    "Authorization": f"Bearer {IMGGO_API_KEY}"
                },
                timeout=10
            )

            if response.status_code == 404:
                # Job not found - might be temporary, retry
                print(f"  Job not found yet, retrying...")
                time.sleep(2)
                continue

            response.raise_for_status()
            data = response.json()["data"]

            status = data["status"]
            print(f"  Status: {status} ({attempt + 1}/{max_attempts})")

            if status == "succeeded":
                result = data.get("manifest") or data.get("result")

                # Validate result
                if not result:
                    raise JobFailedError("Job succeeded but no result returned")

                return result

            elif status == "failed":
                error = data.get("error", "Unknown error")
                raise JobFailedError(f"Job failed: {error}")

            # Still processing, wait
            time.sleep(2)

        except requests.exceptions.Timeout:
            print(f"  Poll timeout, retrying...")
            time.sleep(1)

        except requests.exceptions.ConnectionError:
            print(f"  Connection error, retrying...")
            time.sleep(2)

    raise ImgGoError(f"Job timeout after {max_attempts} attempts")


def validate_result(result: Any) -> bool:
    """
    Validate extracted data.

    Args:
        result: The extracted data to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not result:
        return False

    # Add custom validation logic here
    # For example, check required fields exist

    return True


def main():
    """Main entry point with comprehensive error handling"""
    if len(sys.argv) < 3:
        print("Usage: python error-handling.py <image_path> <pattern_id>")
        sys.exit(1)

    image_path = sys.argv[1]
    pattern_id = sys.argv[2]

    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)

    try:
        result = upload_with_retry(image_path, pattern_id)

        # Validate result
        if not validate_result(result):
            print("Warning: Result validation failed")

        print("\n" + "="*60)
        print("EXTRACTED DATA")
        print("="*60)
        print(result)
        print("\nSuccess!")

    except ImgGoError as e:
        print(f"\nAPI Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
