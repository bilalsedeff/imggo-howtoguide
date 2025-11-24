"""
Simple Food Safety Test
Test the pattern with a sample food handling area image
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "examples" / "common"))
from imggo_client import ImgGoClient

def main():
    print("="*60)
    print("TESTING FOOD SAFETY PATTERN")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\nX Error: IMGGO_API_KEY not set")
        sys.exit(1)

    # Check pattern ID - from env var or pattern_id.txt
    pattern_id = os.getenv("FOOD_SAFETY_PATTERN_ID")
    if not pattern_id:
        pattern_file = Path(__file__).parent / "pattern_id.txt"
        if pattern_file.exists():
            pattern_id = pattern_file.read_text().strip()
    if not pattern_id:
        print("\nX Error: FOOD_SAFETY_PATTERN_ID not set")
        print("Run create-pattern.py first to create a pattern")
        sys.exit(1)

    # Use inventory image as food handling area
    test_image = Path(__file__).parent.parent.parent / "examples" / "test-images" / "inventory1.jpg"
    if not test_image.exists():
        print(f"\nX Error: Test image not found: {test_image}")
        sys.exit(1)

    print(f"\nPattern ID: {pattern_id}")
    print(f"Test Image: {test_image.name}\n")

    try:
        client = ImgGoClient()
        print("Processing food safety image...")

        result = client.process_image(
            image_path=str(test_image),
            pattern_id=pattern_id
        )

        print("V Processing completed!\n")

        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        # YAML format output
        output_file = outputs_dir / "food_safety_output.yaml"
        # Result could be dict with _raw field or string
        if isinstance(result, dict):
            yaml_content = result.get('_raw', str(result))
        else:
            yaml_content = result
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        print(f"V Output saved to: {output_file}\n")
        print("="*60)
        print("EXTRACTED YAML DATA")
        print("="*60)
        print(yaml_content[:500] if len(yaml_content) > 500 else yaml_content)
        if len(yaml_content) > 500:
            print(f"\n... ({len(yaml_content) - 500} more characters)")
        print("\nV Test completed successfully!")

    except Exception as e:
        print(f"\nX Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
