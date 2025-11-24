"""
Simple Construction Progress Test
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "examples" / "common"))
from imggo_client import ImgGoClient

def main():
    print("="*60)
    print("TESTING CONSTRUCTION PROGRESS PATTERN")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\nX Error: IMGGO_API_KEY not set")
        sys.exit(1)

    pattern_id = os.getenv("CONSTRUCTION_PATTERN_ID")
    if not pattern_id:
        pattern_file = Path(__file__).parent / "pattern_id.txt"
        if pattern_file.exists():
            pattern_id = pattern_file.read_text().strip()
    if not pattern_id:
        print("\nX Error: CONSTRUCTION_PATTERN_ID not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent / "examples" / "test-images" / "construction1.jpg"
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

        output_file = outputs_dir / "construction_output.yaml"
        # Result could be dict with _raw field or string
        if isinstance(result, dict):
            content = result.get('_raw', str(result))
        else:
            content = result
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"V Output saved to: {output_file}\n")
        print("="*60)
        print("EXTRACTED DATA (first 500 chars)")
        print("="*60)
        print(content[:500])
        if len(content) > 500:
            print(f"\n... ({len(content) - 500} more characters)")
        print("\nV Test completed successfully!")

    except Exception as e:
        print(f"\nX Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
