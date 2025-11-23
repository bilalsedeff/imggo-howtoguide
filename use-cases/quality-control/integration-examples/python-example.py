"""
Quality Control - Python Integration Example
Extract defect data from inspection images in CSV format
"""

import os
import sys
import csv
import io
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_inspection_image(image_path: str) -> str:
    """Process inspection image and extract defect data as CSV"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("QUALITY_CONTROL_PATTERN_ID", "pat_quality_control_csv")

    print(f"\nProcessing inspection image: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return result  # CSV string


def parse_defect_csv(csv_string: str) -> list:
    """Parse CSV defect data"""
    reader = csv.DictReader(io.StringIO(csv_string))
    return list(reader)


def calculate_quality_metrics(defects: list) -> dict:
    """Calculate quality control metrics"""
    metrics = {
        'total_defects': len(defects),
        'critical_defects': 0,
        'major_defects': 0,
        'minor_defects': 0,
        'defect_density': 0,
        'pass_fail_status': 'PASS'
    }

    for defect in defects:
        severity = defect.get('severity', '').lower()

        if severity == 'critical':
            metrics['critical_defects'] += 1
        elif severity == 'major':
            metrics['major_defects'] += 1
        elif severity == 'minor':
            metrics['minor_defects'] += 1

    # Determine pass/fail
    if metrics['critical_defects'] > 0:
        metrics['pass_fail_status'] = 'FAIL - Critical defects found'
    elif metrics['major_defects'] > 3:
        metrics['pass_fail_status'] = 'FAIL - Too many major defects'
    elif metrics['total_defects'] > 10:
        metrics['pass_fail_status'] = 'REVIEW - High defect count'

    return metrics


def save_to_mes_system(defects: list, metrics: dict, batch_id: str) -> bool:
    """Save inspection results to Manufacturing Execution System"""
    print("\n" + "="*60)
    print("SAVING TO MES SYSTEM")
    print("="*60)

    # In production, integrate with MES (SAP ME, Siemens Opcenter, etc.)
    payload = {
        'batch_id': batch_id,
        'inspection_date': datetime.now().isoformat(),
        'total_defects': metrics['total_defects'],
        'critical_defects': metrics['critical_defects'],
        'major_defects': metrics['major_defects'],
        'minor_defects': metrics['minor_defects'],
        'status': metrics['pass_fail_status'],
        'defect_details': defects
    }

    print(f"MES Payload: {payload['status']}")
    print(f"Batch ID: {batch_id}")
    print(f"Total Defects: {metrics['total_defects']}")

    # Simulate API call
    # response = requests.post('https://mes-system.example.com/api/inspections', json=payload)

    print("\n✓ Inspection saved to MES (simulated)")
    return True


def generate_inspection_report(defects: list, metrics: dict) -> str:
    """Generate quality inspection report"""
    lines = []

    lines.append("QUALITY INSPECTION REPORT")
    lines.append("=" * 60)
    lines.append(f"Inspection Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Status: {metrics['pass_fail_status']}")
    lines.append("")
    lines.append("SUMMARY")
    lines.append(f"  Total Defects: {metrics['total_defects']}")
    lines.append(f"  Critical: {metrics['critical_defects']}")
    lines.append(f"  Major: {metrics['major_defects']}")
    lines.append(f"  Minor: {metrics['minor_defects']}")
    lines.append("")
    lines.append("DEFECT DETAILS")

    for i, defect in enumerate(defects, 1):
        lines.append(f"\n{i}. {defect.get('defect_type', 'Unknown')}")
        lines.append(f"   Severity: {defect.get('severity', 'N/A')}")
        lines.append(f"   Location: {defect.get('location', 'N/A')}")

    lines.append("")
    lines.append("RECOMMENDED ACTIONS:")

    if metrics['critical_defects'] > 0:
        lines.append("  ✗ REJECT BATCH - Critical defects require rework")
    elif metrics['major_defects'] > 0:
        lines.append("  ⚠ REVIEW - Major defects may require correction")
    else:
        lines.append("  ✓ APPROVE - Quality standards met")

    return "\n".join(lines)


def main():
    print("="*60)
    print("QUALITY CONTROL - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "quality-control1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        sys.exit(1)

    try:
        # Process inspection image
        csv_result = process_inspection_image(str(test_image))

        # Save raw CSV
        output_file = "inspection_defects.csv"
        with open(output_file, 'w') as f:
            f.write(csv_result)
        print(f"\n✓ Saved CSV to {output_file}")

        # Parse CSV
        defects = parse_defect_csv(csv_result)

        print("\n" + "="*60)
        print("DETECTED DEFECTS")
        print("="*60)
        for i, defect in enumerate(defects[:5], 1):
            print(f"{i}. {defect.get('defect_type')} - {defect.get('severity')}")

        # Calculate metrics
        metrics = calculate_quality_metrics(defects)

        print("\n" + "="*60)
        print("QUALITY METRICS")
        print("="*60)
        print(f"Total Defects: {metrics['total_defects']}")
        print(f"Critical: {metrics['critical_defects']}")
        print(f"Major: {metrics['major_defects']}")
        print(f"Minor: {metrics['minor_defects']}")
        print(f"Status: {metrics['pass_fail_status']}")

        # Generate report
        report = generate_inspection_report(defects, metrics)
        print("\n" + report)

        # Save to MES
        batch_id = f"BATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        save_to_mes_system(defects, metrics, batch_id)

        # Save report
        report_file = "inspection_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n✓ Saved inspection report to {report_file}")

        print("\n✓ Quality control inspection completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
