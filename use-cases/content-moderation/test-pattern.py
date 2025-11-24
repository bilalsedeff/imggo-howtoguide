"""
Simple Content Moderation Test
Test the pattern with a sample image
"""

import os
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "examples" / "common"))
from imggo_client import ImgGoClient

def main():
    print("="*60)
    print("TESTING CONTENT MODERATION PATTERN")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\nX Error: IMGGO_API_KEY not set")
        sys.exit(1)

    # Check pattern ID - from env var or pattern_id.txt
    pattern_id = os.getenv("CONTENT_MODERATION_PATTERN_ID")
    if not pattern_id:
        pattern_file = Path(__file__).parent / "pattern_id.txt"
        if pattern_file.exists():
            pattern_id = pattern_file.read_text().strip()
    if not pattern_id:
        print("\nX Error: CONTENT_MODERATION_PATTERN_ID not set")
        print("Run create-pattern.py first to create a pattern")
        sys.exit(1)

    # Use resume image for content moderation
    test_image = Path(__file__).parent.parent.parent / "examples" / "test-images" / "resume1.png"
    if not test_image.exists():
        print(f"\nX Error: Test image not found: {test_image}")
        sys.exit(1)

    print(f"\nPattern ID: {pattern_id}")
    print(f"Test Image: {test_image.name}\n")

    try:
        client = ImgGoClient()
        print("Processing image for content moderation...")

        result = client.process_image(
            image_path=str(test_image),
            pattern_id=pattern_id
        )

        print("V Processing completed!\n")

        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        # JSON format output
        output_file = outputs_dir / "moderation_output.json"
        try:
            mod_data = result if isinstance(result, dict) else json.loads(result)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(mod_data, f, indent=2)

            print(f"V Output saved to: {output_file}\n")
            print("="*60)
            print("MODERATION RESULTS")
            print("="*60)
            print(json.dumps(mod_data, indent=2))

        except json.JSONDecodeError:
            # Not JSON, save as text
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result if isinstance(result, str) else str(result))
            print(f"V Output saved to: {output_file}\n")
            print("="*60)
            print("EXTRACTED DATA")
            print("="*60)
            print(result)

        print("\nV Test completed successfully!")

    except Exception as e:
        print(f"\nX Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
