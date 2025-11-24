"""
Reusable ImgGo API Client for Python
Production-ready client with error handling, retry logic, and webhooks
"""

import os
import time
import requests
from typing import Optional, Dict, Any, Callable
from pathlib import Path


class ImgGoClient:
    """
    Production-ready ImgGo API client

    Usage:
        client = ImgGoClient(api_key="your_key")
        result = client.process_image("path/to/image.jpg", pattern_id="pat_xxx")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://img-go.com/api",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize ImgGo client

        Args:
            api_key: ImgGo API key (or set IMGGO_API_KEY env var)
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        self.api_key = api_key or os.getenv("IMGGO_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set IMGGO_API_KEY or pass api_key parameter")

        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries

    def process_image(
        self,
        image_path: str,
        pattern_id: str,
        idempotency_key: Optional[str] = None,
        poll: bool = True,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an image file with ImgGo

        Args:
            image_path: Path to image file
            pattern_id: ImgGo pattern ID
            idempotency_key: Optional idempotency key for retry safety
            poll: Whether to poll for results (True) or return job_id immediately (False)
            webhook_url: Optional webhook URL for async notification

        Returns:
            Processed result data (if poll=True) or job info (if poll=False)
        """
        # Generate idempotency key if not provided
        if not idempotency_key:
            idempotency_key = f"{Path(image_path).stem}-{int(time.time())}"

        # Upload image
        import mimetypes
        filename = Path(image_path).name
        mime_type, _ = mimetypes.guess_type(image_path)

        with open(image_path, 'rb') as f:
            files = {'image': (filename, f, mime_type or 'image/jpeg')}
            data = {}

            if webhook_url:
                data['webhook_url'] = webhook_url

            response = self._make_request(
                'POST',
                f"/patterns/{pattern_id}/ingest",
                files=files,
                data=data if data else None,
                headers={"Idempotency-Key": idempotency_key}
            )

        job_id = response["data"]["job_id"]

        # Return immediately if not polling
        if not poll:
            return response["data"]

        # Poll for results
        return self.wait_for_job(job_id)

    def process_image_url(
        self,
        image_url: str,
        pattern_id: str,
        idempotency_key: Optional[str] = None,
        poll: bool = True,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an image from URL with ImgGo

        Args:
            image_url: Public URL to image
            pattern_id: ImgGo pattern ID
            idempotency_key: Optional idempotency key
            poll: Whether to poll for results
            webhook_url: Optional webhook URL

        Returns:
            Processed result data (if poll=True) or job info (if poll=False)
        """
        if not idempotency_key:
            idempotency_key = f"url-{hash(image_url)}-{int(time.time())}"

        payload = {"image_url": image_url}

        if webhook_url:
            payload['webhook_url'] = webhook_url

        response = self._make_request(
            'POST',
            f"/patterns/{pattern_id}/ingest",
            json=payload,
            headers={"Idempotency-Key": idempotency_key}
        )

        job_id = response["data"]["job_id"]

        if not poll:
            return response["data"]

        return self.wait_for_job(job_id)

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of a processing job

        Args:
            job_id: Job ID from ingestion request

        Returns:
            Job status data
        """
        response = self._make_request('GET', f"/jobs/{job_id}")
        return response["data"]

    def wait_for_job(
        self,
        job_id: str,
        max_attempts: int = 60,
        wait_seconds: int = 2,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Poll job until completion

        Args:
            job_id: Job ID to poll
            max_attempts: Maximum polling attempts
            wait_seconds: Seconds between polls
            progress_callback: Optional callback for progress updates

        Returns:
            Completed job result

        Raises:
            TimeoutError: If job doesn't complete in time
            RuntimeError: If job fails
        """
        for attempt in range(max_attempts):
            job_status = self.get_job_status(job_id)
            status = job_status["status"]

            if progress_callback:
                progress_callback(status, attempt + 1)

            if status in ("completed", "succeeded"):
                # API returns result in "manifest" field for succeeded jobs
                return job_status.get("manifest") or job_status.get("result")

            elif status == "failed":
                error = job_status.get("error", "Unknown error")
                raise RuntimeError(f"Job {job_id} failed: {error}")

            time.sleep(wait_seconds)

        raise TimeoutError(
            f"Job {job_id} did not complete within {max_attempts * wait_seconds} seconds"
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            JSON response data

        Raises:
            requests.HTTPError: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"

        # Add authorization header
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f"Bearer {self.api_key}"

        # Merge headers
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers

        # Add timeout
        kwargs.setdefault('timeout', self.timeout)

        # Retry logic
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()

            except requests.RequestException as e:
                last_exception = e

                # Don't retry client errors (4xx except 429)
                if hasattr(e, 'response') and e.response is not None:
                    if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                        raise

                # Exponential backoff for retries
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) * 0.5
                    time.sleep(wait_time)

        # All retries failed
        raise last_exception


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = ImgGoClient()

    # Example 1: Process image file
    print("Processing image file...")
    result = client.process_image(
        image_path="../../../test-images/invoice1.jpg",
        pattern_id="pat_invoice_example"
    )
    print("Result:", result)

    # Example 2: Process image from URL (no polling)
    print("\nProcessing image from URL...")
    job_info = client.process_image_url(
        image_url="https://example.com/image.jpg",
        pattern_id="pat_example",
        poll=False  # Return job ID immediately
    )
    print("Job ID:", job_info['job_id'])

    # Later, check status
    status = client.get_job_status(job_info['job_id'])
    print("Status:", status['status'])
