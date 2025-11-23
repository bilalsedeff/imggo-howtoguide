"""
Food Safety - Python Integration Example
Extract food safety inspection data from restaurant photos (CSV format)
"""

import os
import sys
import csv
import io
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))
from imggo_client import ImgGoClient


def process_inspection_photo(image_path: str) -> str:
    """Process food safety inspection photo"""
    client = ImgGoClient()
    PATTERN_ID = os.getenv("FOOD_SAFETY_PATTERN_ID", "pat_food_safety_csv")
    
    print(f"\nProcessing inspection photo: {Path(image_path).name}")
    return client.process_image(image_path=image_path, pattern_id=PATTERN_ID)


def parse_inspection_csv(csv_string: str) -> list:
    """Parse CSV inspection data"""
    reader = csv.DictReader(io.StringIO(csv_string))
    return list(reader)


def calculate_compliance_score(violations: list) -> dict:
    """Calculate compliance score"""
    score = {
        'total_violations': len(violations),
        'critical_violations': 0,
        'major_violations': 0,
        'minor_violations': 0,
        'compliance_score': 100,
        'status': 'PASS'
    }
    
    for violation in violations:
        severity = violation.get('severity', '').lower()
        if severity == 'critical':
            score['critical_violations'] += 1
            score['compliance_score'] -= 20
        elif severity == 'major':
            score['major_violations'] += 1
            score['compliance_score'] -= 10
        elif severity == 'minor':
            score['minor_violations'] += 1
            score['compliance_score'] -= 5
    
    if score['critical_violations'] > 0:
        score['status'] = 'FAIL'
    elif score['compliance_score'] < 70:
        score['status'] = 'CONDITIONAL_PASS'
    
    return score


def main():
    print("="*60)
    print("FOOD SAFETY - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "food-safety1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        sys.exit(1)

    try:
        csv_result = process_inspection_photo(str(test_image))
        
        with open("inspection_violations.csv", 'w') as f:
            f.write(csv_result)
        print(f"\n✓ Saved CSV to inspection_violations.csv")

        violations = parse_inspection_csv(csv_result)
        score = calculate_compliance_score(violations)

        print("\n" + "="*60)
        print("INSPECTION RESULTS")
        print("="*60)
        print(f"Total Violations: {score['total_violations']}")
        print(f"Critical: {score['critical_violations']}")
        print(f"Major: {score['major_violations']}")
        print(f"Minor: {score['minor_violations']}")
        print(f"Compliance Score: {score['compliance_score']}/100")
        print(f"Status: {score['status']}")

        print("\n✓ Food safety inspection completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
