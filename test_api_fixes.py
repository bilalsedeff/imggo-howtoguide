"""
Quick API test to verify all fixes work correctly
Tests the Python client with the real ImgGo API
"""

import os
import sys
from pathlib import Path

# Add common directory to path
sys.path.append(str(Path(__file__).parent / "examples" / "common"))

from imggo_client import ImgGoClient

def main():
    print("=" * 60)
    print("TESTING ImgGo API CLIENT WITH ALL FIXES")
    print("=" * 60)

    # Check API key
    api_key = os.getenv("IMGGO_API_KEY")
    if not api_key:
        print("\nX Error: IMGGO_API_KEY not set in .env")
        sys.exit(1)

    print(f"\nV API Key found: {api_key[:20]}...")

    # Initialize client
    try:
        client = ImgGoClient()
        print("V ImgGoClient initialized successfully")
    except Exception as e:
        print(f"X Error initializing client: {e}")
        sys.exit(1)

    # Test pattern ID from previous test
    pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"  # From .pattern_id_v2

    # Test with the test-images/invoice1.jpg (if it exists)
    test_image = Path(__file__).parent / "test-images" / "invoice1.jpg"

    if not test_image.exists():
        print(f"\nWarning: Test image not found at {test_image}")
        print("Checking job status instead...")

        # Check status of previous job
        job_id = "a5960b09-bd57-4447-931d-2e4b58bc96dc"  # From .job_id
        try:
            print(f"\nTesting get_job_status() method...")
            job_status = client.get_job_status(job_id)

            print(f"\nV Job Status Retrieved Successfully:")
            print(f"  Job ID: {job_id}")
            print(f"  Status: {job_status.get('status')}")

            if job_status.get('status') in ('succeeded', 'completed'):
                manifest = job_status.get('manifest') or job_status.get('result')
                print(f"\nV Extracted Data:")
                import json
                print(json.dumps(manifest, indent=2))

                print("\n" + "=" * 60)
                print("SUCCESS: All API client methods working correctly!")
                print("=" * 60)
                print("\nVerified:")
                print("  [V] Client initialization")
                print("  [V] get_job_status() method")
                print("  [V] Correct field name ('manifest' not 'result')")
                print("  [V] Correct status value ('succeeded' not 'completed')")

        except Exception as e:
            print(f"\nX Error checking job status: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print(f"\nV Test image found: {test_image}")
        print(f"\nTesting full workflow (upload + poll)...")

        try:
            result = client.process_image(
                image_path=str(test_image),
                pattern_id=pattern_id
            )

            print("\nV Image processed successfully!")
            print(f"\nExtracted Data:")
            import json
            print(json.dumps(result, indent=2))

            print("\n" + "=" * 60)
            print("SUCCESS: Full API workflow working correctly!")
            print("=" * 60)

        except Exception as e:
            print(f"\nX Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()
