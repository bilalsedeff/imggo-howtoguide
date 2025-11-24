"""
Simple Resume Parsing Test
Test the pattern with a sample resume image
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
    print("TESTING RESUME PARSING PATTERN")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\nX Error: IMGGO_API_KEY not set")
        print("Please set your API key in .env file")
        sys.exit(1)

    # Check pattern ID
    pattern_id = os.getenv("RESUME_PATTERN_ID")
    if not pattern_id:
        print("\nX Error: RESUME_PATTERN_ID not set")
        print("Run create-pattern.py first to create a pattern")
        sys.exit(1)

    # Get test image
    test_image = Path(__file__).parent.parent.parent / "test-images" / "resume1.jpg"

    if not test_image.exists():
        print(f"\nX Error: Test image not found: {test_image}")
        sys.exit(1)

    print(f"\nPattern ID: {pattern_id}")
    print(f"Test Image: {test_image.name}")
    print()

    try:
        # Process resume
        client = ImgGoClient()
        print("Processing resume image...")

        result = client.process_image(
            image_path=str(test_image),
            pattern_id=pattern_id
        )

        print("V Processing completed!")
        print()

        # Save to outputs folder
        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        output_file = outputs_dir / "resume1_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f"V Output saved to: {output_file}")
        print()

        # Display first 500 characters
        print("="*60)
        print("EXTRACTED TEXT (first 500 chars)")
        print("="*60)
        print(result[:500])
        if len(result) > 500:
            print(f"\n... ({len(result) - 500} more characters)")
        print()

        print("V Test completed successfully!")

    except Exception as e:
        print(f"\nX Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
