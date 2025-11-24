"""
Async Batch Processing

Process multiple images concurrently using asyncio.
Great for high-volume workflows.

Usage:
    python async-batch.py PATTERN_ID image1.jpg image2.jpg image3.jpg
"""

import os
import sys
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Any


# Configuration
IMGGO_API_KEY = os.getenv("IMGGO_API_KEY")
IMGGO_BASE_URL = os.getenv("IMGGO_BASE_URL", "https://img-go.com/api")


async def upload_image_async(
    session: aiohttp.ClientSession,
    image_path: str,
    pattern_id: str
) -> Dict[str, Any]:
    """
    Upload a single image asynchronously.

    Args:
        session: aiohttp session
        image_path: Path to image file
        pattern_id: Pattern ID to use

    Returns:
        dict: Result with job_id, image_path, and status
    """
    try:
        print(f"Uploading: {Path(image_path).name}")

        # Read file
        with open(image_path, 'rb') as f:
            file_data = f.read()

        # Guess MIME type
        import mimetypes
        mime_type, _ = mimetypes.guess_type(image_path)

        # Create form data
        data = aiohttp.FormData()
        data.add_field('image',
                      file_data,
                      filename=Path(image_path).name,
                      content_type=mime_type or 'image/jpeg')

        # Upload
        async with session.post(
            f"{IMGGO_BASE_URL}/patterns/{pattern_id}/ingest",
            data=data
        ) as response:
            response.raise_for_status()
            result = await response.json()

            job_id = result["data"]["job_id"]
            print(f"  Created job: {job_id}")

            return {
                "job_id": job_id,
                "image_path": image_path,
                "status": "uploaded"
            }

    except Exception as e:
        print(f"  Error uploading {image_path}: {e}")
        return {
            "job_id": None,
            "image_path": image_path,
            "status": "error",
            "error": str(e)
        }


async def poll_job_async(
    session: aiohttp.ClientSession,
    job_id: str,
    image_path: str,
    max_attempts: int = 60
) -> Dict[str, Any]:
    """
    Poll a job asynchronously until completion.

    Args:
        session: aiohttp session
        job_id: Job ID to poll
        image_path: Original image path (for tracking)
        max_attempts: Maximum polling attempts

    Returns:
        dict: Result with extracted data
    """
    try:
        for attempt in range(max_attempts):
            async with session.get(
                f"{IMGGO_BASE_URL}/jobs/{job_id}"
            ) as response:
                response.raise_for_status()
                data = await response.json()

                status = data["data"]["status"]

                if status == "succeeded":
                    result = data["data"].get("manifest") or data["data"].get("result")
                    print(f"  Completed: {Path(image_path).name}")

                    return {
                        "job_id": job_id,
                        "image_path": image_path,
                        "status": "completed",
                        "result": result
                    }

                elif status == "failed":
                    error = data["data"].get("error", "Unknown error")
                    print(f"  Failed: {Path(image_path).name} - {error}")

                    return {
                        "job_id": job_id,
                        "image_path": image_path,
                        "status": "failed",
                        "error": error
                    }

                # Still processing
                await asyncio.sleep(2)

        # Timeout
        print(f"  Timeout: {Path(image_path).name}")
        return {
            "job_id": job_id,
            "image_path": image_path,
            "status": "timeout"
        }

    except Exception as e:
        print(f"  Error polling {job_id}: {e}")
        return {
            "job_id": job_id,
            "image_path": image_path,
            "status": "error",
            "error": str(e)
        }


async def process_batch(
    image_paths: List[str],
    pattern_id: str
) -> List[Dict[str, Any]]:
    """
    Process multiple images concurrently.

    Args:
        image_paths: List of paths to image files
        pattern_id: Pattern ID to use

    Returns:
        list: Results for each image
    """
    if not IMGGO_API_KEY:
        raise ValueError("IMGGO_API_KEY environment variable not set")

    # Create session with auth header
    headers = {
        "Authorization": f"Bearer {IMGGO_API_KEY}"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        # Phase 1: Upload all images concurrently
        print(f"\nUploading {len(image_paths)} images...")
        upload_tasks = [
            upload_image_async(session, image_path, pattern_id)
            for image_path in image_paths
        ]
        upload_results = await asyncio.gather(*upload_tasks)

        # Filter out failed uploads
        successful_uploads = [
            r for r in upload_results
            if r["status"] == "uploaded" and r["job_id"]
        ]

        if not successful_uploads:
            print("\nNo successful uploads!")
            return upload_results

        # Phase 2: Poll all jobs concurrently
        print(f"\nProcessing {len(successful_uploads)} jobs...")
        poll_tasks = [
            poll_job_async(session, r["job_id"], r["image_path"])
            for r in successful_uploads
        ]
        final_results = await asyncio.gather(*poll_tasks)

        return final_results


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python async-batch.py <pattern_id> <image1> <image2> ...")
        print("\nExample:")
        print("  python async-batch.py pat_abc123 invoice1.jpg invoice2.jpg invoice3.jpg")
        sys.exit(1)

    pattern_id = sys.argv[1]
    image_paths = sys.argv[2:]

    # Validate files exist
    missing_files = [p for p in image_paths if not os.path.exists(p)]
    if missing_files:
        print(f"Error: Files not found: {', '.join(missing_files)}")
        sys.exit(1)

    print(f"Processing {len(image_paths)} images with pattern {pattern_id}")

    try:
        # Run async batch processing
        results = asyncio.run(process_batch(image_paths, pattern_id))

        # Display summary
        print("\n" + "="*60)
        print("BATCH PROCESSING SUMMARY")
        print("="*60)

        completed = [r for r in results if r["status"] == "completed"]
        failed = [r for r in results if r["status"] == "failed"]
        errors = [r for r in results if r["status"] == "error"]
        timeouts = [r for r in results if r["status"] == "timeout"]

        print(f"Total: {len(results)}")
        print(f"Completed: {len(completed)}")
        print(f"Failed: {len(failed)}")
        print(f"Errors: {len(errors)}")
        print(f"Timeouts: {len(timeouts)}")

        # Display failed/error details
        if failed or errors or timeouts:
            print("\nIssues:")
            for r in failed + errors + timeouts:
                error_msg = r.get("error", "Unknown")
                print(f"  - {Path(r['image_path']).name}: {r['status']} - {error_msg}")

        print("\nResults saved to: batch_results.json")

        # Save results to file
        import json
        with open("batch_results.json", "w") as f:
            json.dump(results, f, indent=2)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
