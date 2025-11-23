"""
KYC Verification - Python Example
Extract identity information from ID cards for compliance
"""

import os
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def extract_id_info(image_path: str) -> dict:
    """Extract information from ID card"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("KYC_PATTERN_ID", "pat_kyc_verification")

    print(f"\nProcessing ID card: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return result


def verify_identity(id_info: dict) -> dict:
    """Perform compliance checks on extracted ID data"""

    # Basic validation
    required_fields = ['full_name', 'date_of_birth', 'id_number']
    missing_fields = [f for f in required_fields if f not in id_info or not id_info[f]]

    if missing_fields:
        return {
            'status': 'failed',
            'reason': f"Missing required fields: {', '.join(missing_fields)}"
        }

    # Age verification (must be 18+)
    from datetime import datetime
    try:
        dob = datetime.strptime(id_info['date_of_birth'], '%Y-%m-%d')
        age = (datetime.now() - dob).days // 365

        if age < 18:
            return {
                'status': 'failed',
                'reason': 'Applicant must be 18 years or older'
            }
    except:
        return {
            'status': 'failed',
            'reason': 'Invalid date of birth format'
        }

    # Document expiry check
    if 'expiry_date' in id_info:
        try:
            expiry = datetime.strptime(id_info['expiry_date'], '%Y-%m-%d')
            if expiry < datetime.now():
                return {
                    'status': 'failed',
                    'reason': 'ID document has expired'
                }
        except:
            pass

    return {
        'status': 'passed',
        'age': age
    }


def main():
    print("="*60)
    print("KYC VERIFICATION - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "id-card1.jpg"

    if not test_image.exists():
        print(f"\n✗ Test image not found: {test_image}")
        sys.exit(1)

    try:
        # Extract ID information
        id_info = extract_id_info(str(test_image))

        print("\n" + "="*60)
        print("EXTRACTED ID INFORMATION")
        print("="*60)
        print(json.dumps(id_info, indent=2))

        # Verify identity
        verification = verify_identity(id_info)

        print("\n" + "="*60)
        print("VERIFICATION RESULT")
        print("="*60)
        print(f"Status: {verification['status'].upper()}")

        if verification['status'] == 'passed':
            print(f"✓ Verification passed")
            if 'age' in verification:
                print(f"  Age: {verification['age']} years")
        else:
            print(f"✗ Verification failed: {verification['reason']}")

        # Save results
        output_file = "kyc_verification_result.json"
        with open(output_file, 'w') as f:
            json.dump({
                'id_info': id_info,
                'verification': verification
            }, f, indent=2)
        print(f"\n✓ Results saved to {output_file}")

        print("\n✓ KYC verification completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
