"""
Simple VIN Extraction Test
Test the pattern with a sample VIN image
"""

import os
import sys
import json
from pathlib import Path

# Add imggo_client to path
sys.path.append(str(Path(__file__).parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def main():
    print("="*60)
    print("TESTING VIN EXTRACTION PATTERN")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\nX Error: IMGGO_API_KEY not set")
        print("Please set your API key in .env file")
        sys.exit(1)

    # Check pattern ID
    pattern_id = os.getenv("VIN_PATTERN_ID")
    if not pattern_id:
        print("\nX Error: VIN_PATTERN_ID not set")
        print("Run create-pattern.py first to create a pattern")
        sys.exit(1)

    # Get test image
    test_image = Path(__file__).parent.parent.parent / "test-images" / "vin1.jpg"

    if not test_image.exists():
        print(f"\nX Error: Test image not found: {test_image}")
        sys.exit(1)

    print(f"\nPattern ID: {pattern_id}")
    print(f"Test Image: {test_image.name}")
    print()

    try:
        # Process VIN image
        client = ImgGoClient()
        print("Processing VIN image...")

        result = client.process_image(
            image_path=str(test_image),
            pattern_id=pattern_id
        )

        print("V Processing completed!")
        print()

        # Save to outputs folder
        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        # Try to parse as JSON
        try:
            vin_data = json.loads(result)
            output_file = outputs_dir / "vin1_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(vin_data, f, indent=2)

            print(f"V Output saved to: {output_file}")
            print()

            # Display extracted VIN data
            print("="*60)
            print("EXTRACTED VIN DATA")
            print("="*60)
            print(json.dumps(vin_data, indent=2))
            print()

        except json.JSONDecodeError:
            # Not JSON, save as text
            output_file = outputs_dir / "vin1_output.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)

            print(f"V Output saved to: {output_file}")
            print()
            print("="*60)
            print("EXTRACTED TEXT")
            print("="*60)
            print(result)
            print()

        print("V Test completed successfully!")

    except Exception as e:
        print(f"\nX Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
