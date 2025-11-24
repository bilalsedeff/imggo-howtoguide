"""
ImgGo Webhook Example
Demonstrates how to register a webhook and handle webhook events

Based on ImgGo API documentation:
- POST /webhooks - Register a webhook
- Events: job.succeeded, job.failed
"""

import os
import json
import hmac
import hashlib
import requests
from flask import Flask, request, jsonify

# Configuration
IMGGO_API_KEY = os.getenv("IMGGO_API_KEY", "your_api_key_here")
IMGGO_BASE_URL = "https://img-go.com/api"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_webhook_secret_here")

app = Flask(__name__)


def create_webhook(url: str, events: list[str]) -> dict:
    """
    Register a new webhook with ImgGo API

    Args:
        url: The URL to receive webhook events
        events: List of events to subscribe to (job.succeeded, job.failed)

    Returns:
        dict: Webhook registration response
    """
    payload = {
        "url": url,
        "events": events,
        "secret": WEBHOOK_SECRET  # Used to verify webhook signatures
    }

    response = requests.post(
        f"{IMGGO_BASE_URL}/webhooks",
        headers={
            "Authorization": f"Bearer {IMGGO_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    response.raise_for_status()
    return response.json()


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify the webhook signature to ensure it's from ImgGo

    Args:
        payload: Raw request body
        signature: X-ImgGo-Signature header value

    Returns:
        bool: True if signature is valid
    """
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected}", signature)


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """
    Handle incoming webhook events from ImgGo

    Events:
    - job.succeeded: Job completed successfully
    - job.failed: Job failed
    """
    # Verify signature
    signature = request.headers.get("X-ImgGo-Signature", "")
    if WEBHOOK_SECRET != "your_webhook_secret_here":
        if not verify_webhook_signature(request.data, signature):
            return jsonify({"error": "Invalid signature"}), 401

    # Parse event
    event = request.json
    event_type = event.get("event")
    job_id = event.get("data", {}).get("job_id")

    print(f"Received webhook: {event_type} for job {job_id}")

    if event_type == "job.succeeded":
        # Handle successful job
        result = event.get("data", {}).get("result")
        print(f"Job {job_id} succeeded!")
        print(f"Result: {json.dumps(result, indent=2)}")

        # TODO: Process the result (save to database, trigger next step, etc.)

    elif event_type == "job.failed":
        # Handle failed job
        error = event.get("data", {}).get("error")
        print(f"Job {job_id} failed: {error}")

        # TODO: Handle failure (retry, notify admin, etc.)

    return jsonify({"status": "received"}), 200


def main():
    """
    Example: Register a webhook and start the server
    """
    print("="*60)
    print("IMGGO WEBHOOK EXAMPLE")
    print("="*60)

    # Check API key
    if IMGGO_API_KEY == "your_api_key_here":
        print("\nNote: Set IMGGO_API_KEY environment variable")
        print("      to register webhooks with the API")
    else:
        # Example: Register webhook (uncomment to use)
        # webhook_url = "https://your-server.com/webhook"
        # result = create_webhook(
        #     url=webhook_url,
        #     events=["job.succeeded", "job.failed"]
        # )
        # print(f"Webhook registered: {result}")
        pass

    print("\nStarting webhook server on http://localhost:5000")
    print("Webhook endpoint: http://localhost:5000/webhook")
    print("\nTo test locally, use ngrok or similar to expose this server")
    print("  ngrok http 5000")
    print("\nThen register the ngrok URL as your webhook endpoint")
    print()

    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
