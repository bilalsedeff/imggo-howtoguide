"""
GDPR Anonymization - Python Integration Example
"""
import os, sys, json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))
from imggo_client import ImgGoClient

def main():
    print("GDPR ANONYMIZATION - PYTHON EXAMPLE")
    if not os.getenv("IMGGO_API_KEY"):
        print("✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)
    
    client = ImgGoClient()
    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "gdpr1.jpg"
    
    if not test_image.exists():
        print(f"⚠ Test image not found: {test_image}")
        sys.exit(1)
    
    try:
        result = client.process_image(str(test_image), os.getenv("GDPR_PATTERN_ID", "pat_gdpr_json"))
        data = json.loads(result) if isinstance(result, str) else result
        
        print(f"\n✓ Detected {len(data.get('faces', []))} faces")
        print(f"✓ Detected {len(data.get('license_plates', []))} license plates")
        print("\n✓ GDPR anonymization completed!")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
