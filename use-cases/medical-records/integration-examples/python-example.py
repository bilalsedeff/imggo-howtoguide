"""
Medical Records - Python Integration Example
"""
import os, sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))
from imggo_client import ImgGoClient

def main():
    print("MEDICAL RECORDS - PYTHON EXAMPLE")
    if not os.getenv("IMGGO_API_KEY"):
        print("✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)
    
    client = ImgGoClient()
    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "medical-records1.jpg"
    
    if not test_image.exists():
        print(f"⚠ Test image not found: {test_image}")
        sys.exit(1)
    
    try:
        result = client.process_image(str(test_image), os.getenv("MEDICAL_RECORDS_PATTERN_ID", "pat_medical_text"))
        
        with open("medical_record.txt", "w") as f:
            f.write(result)
        print(f"\n✓ Saved medical record to medical_record.txt")
        print("✓ Medical records processing completed!")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
