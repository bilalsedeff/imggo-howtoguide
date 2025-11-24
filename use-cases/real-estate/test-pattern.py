"""
Simple Real Estate Test
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "examples" / "common"))
from imggo_client import ImgGoClient

def main():
    print("="*60)
    print("TESTING REAL ESTATE PATTERN")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\nX Error: IMGGO_API_KEY not set")
        sys.exit(1)

    pattern_id = os.getenv("REAL_ESTATE_PATTERN_ID")
    if not pattern_id:
        print("\nX Error: REAL_ESTATE_PATTERN_ID not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent / "test-images" / "resume1.jpg"
    if not test_image.exists():
        print(f"\nX Error: Test image not found: {test_image}")
        sys.exit(1)

    print(f"\nPattern ID: {pattern_id}")
    print(f"Test Image: {test_image.name}\n")

    try:
        client = ImgGoClient()
        print("Processing image...")

        result = client.process_image(
            image_path=str(test_image),
            pattern_id=pattern_id
        )

        print("V Processing completed!\n")

        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        output_file = outputs_dir / "real_estate_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f"V Output saved to: {output_file}\n")
        print("="*60)
        print("EXTRACTED DATA (first 500 chars)")
        print("="*60)
        print(result[:500])
        if len(result) > 500:
            print(f"\n... ({len(result) - 500} more characters)")
        print("\nV Test completed successfully!")

    except Exception as e:
        print(f"\nX Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
