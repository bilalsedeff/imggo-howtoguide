"""
Medical Prescription Processing - Python Integration Example
Extract prescription data from images and integrate with pharmacy systems
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_prescription(image_path: str) -> str:
    """Process prescription image and extract text data"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("PRESCRIPTION_PATTERN_ID", "pat_prescription_text")

    print(f"\nProcessing prescription: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return result  # Plain text string


def parse_prescription_text(text: str) -> dict:
    """Parse prescription text into structured data"""
    prescription = {
        'patient_name': None,
        'patient_dob': None,
        'prescriber': None,
        'prescriber_license': None,
        'date_written': None,
        'medications': [],
        'pharmacy_notes': None
    }

    # Extract patient name (usually appears after "Patient:" or "Name:")
    patient_match = re.search(r'(?:Patient|Name):\s*([^\n]+)', text, re.IGNORECASE)
    if patient_match:
        prescription['patient_name'] = patient_match.group(1).strip()

    # Extract date of birth
    dob_match = re.search(r'(?:DOB|Date of Birth):\s*([^\n]+)', text, re.IGNORECASE)
    if dob_match:
        prescription['patient_dob'] = dob_match.group(1).strip()

    # Extract prescriber
    prescriber_match = re.search(r'(?:Prescriber|Doctor|Physician):\s*([^\n]+)', text, re.IGNORECASE)
    if prescriber_match:
        prescription['prescriber'] = prescriber_match.group(1).strip()

    # Extract license number
    license_match = re.search(r'(?:License|DEA|NPI):\s*([^\n]+)', text, re.IGNORECASE)
    if license_match:
        prescription['prescriber_license'] = license_match.group(1).strip()

    # Extract prescription date
    date_match = re.search(r'Date:\s*([^\n]+)', text, re.IGNORECASE)
    if date_match:
        prescription['date_written'] = date_match.group(1).strip()

    # Extract medications (simplified - looking for drug names followed by dosage)
    # In production, use medical NLP or drug database
    med_patterns = [
        r'(\w+)\s+(\d+\s*mg)\s+([^\n]+)',
        r'Rx:\s*([^\n]+)',
        r'Medication:\s*([^\n]+)'
    ]

    for pattern in med_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            prescription['medications'].append(match.group(0).strip())

    # Extract pharmacy notes or instructions
    notes_match = re.search(r'(?:Notes|Instructions|Directions):\s*([^\n]+)', text, re.IGNORECASE)
    if notes_match:
        prescription['pharmacy_notes'] = notes_match.group(1).strip()

    return prescription


def validate_prescription(prescription: dict) -> dict:
    """Validate prescription data for pharmacy processing"""
    validation = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }

    # Check required fields
    if not prescription['patient_name']:
        validation['is_valid'] = False
        validation['errors'].append("Missing patient name")

    if not prescription['prescriber']:
        validation['is_valid'] = False
        validation['errors'].append("Missing prescriber information")

    if not prescription['medications']:
        validation['is_valid'] = False
        validation['errors'].append("No medications found")

    # Check prescription date
    if prescription['date_written']:
        try:
            # Try to parse date
            # Note: This is simplified - production should handle various date formats
            date_str = prescription['date_written']
            # Add date validation logic here
        except Exception as e:
            validation['warnings'].append(f"Unable to validate prescription date: {e}")

    # Check prescriber license
    if not prescription['prescriber_license']:
        validation['warnings'].append("Prescriber license number not found - manual verification required")

    return validation


def save_to_pharmacy_system(prescription: dict) -> bool:
    """Save prescription to pharmacy management system"""
    # In production, integrate with your pharmacy system API
    # Examples: PioneerRx, QS/1, Liberty, etc.

    print("\n" + "="*60)
    print("SAVING TO PHARMACY SYSTEM")
    print("="*60)

    # Placeholder for API integration
    api_payload = {
        'patient': {
            'name': prescription['patient_name'],
            'dob': prescription['patient_dob']
        },
        'prescriber': {
            'name': prescription['prescriber'],
            'license': prescription['prescriber_license']
        },
        'prescription_date': prescription['date_written'],
        'medications': prescription['medications'],
        'notes': prescription['pharmacy_notes']
    }

    print(f"API Payload prepared:")
    for key, value in api_payload.items():
        print(f"  {key}: {value}")

    # Simulate API call
    # response = requests.post('https://pharmacy-system.example.com/api/prescriptions', json=api_payload)

    print("\n✓ Prescription saved to pharmacy system (simulated)")
    return True


def generate_fill_instructions(prescription: dict) -> str:
    """Generate pharmacist fill instructions"""
    instructions = []

    instructions.append("PHARMACIST FILL INSTRUCTIONS")
    instructions.append("=" * 60)
    instructions.append(f"Patient: {prescription['patient_name']}")
    instructions.append(f"DOB: {prescription['patient_dob']}")
    instructions.append("")
    instructions.append(f"Prescriber: {prescription['prescriber']}")
    instructions.append(f"License: {prescription['prescriber_license']}")
    instructions.append(f"Date: {prescription['date_written']}")
    instructions.append("")
    instructions.append("MEDICATIONS TO FILL:")

    for i, med in enumerate(prescription['medications'], 1):
        instructions.append(f"  {i}. {med}")

    if prescription['pharmacy_notes']:
        instructions.append("")
        instructions.append(f"Notes: {prescription['pharmacy_notes']}")

    instructions.append("")
    instructions.append("VERIFICATION CHECKLIST:")
    instructions.append("  [ ] Patient ID verified")
    instructions.append("  [ ] Insurance checked")
    instructions.append("  [ ] Drug interactions reviewed")
    instructions.append("  [ ] Prescriber credentials confirmed")
    instructions.append("  [ ] Patient counseling completed")

    return "\n".join(instructions)


def main():
    print("="*60)
    print("MEDICAL PRESCRIPTION PROCESSING - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "medical-prescription1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        print("Using placeholder for demonstration")
        # In production, handle missing file appropriately
        sys.exit(1)

    try:
        # Process prescription image
        prescription_text = process_prescription(str(test_image))

        # Save raw text
        output_file = "prescription_raw.txt"
        with open(output_file, 'w') as f:
            f.write(prescription_text)
        print(f"\n✓ Saved raw text to {output_file}")

        # Parse prescription
        prescription = parse_prescription_text(prescription_text)

        print("\n" + "="*60)
        print("EXTRACTED PRESCRIPTION DATA")
        print("="*60)
        print(f"Patient: {prescription['patient_name']}")
        print(f"DOB: {prescription['patient_dob']}")
        print(f"Prescriber: {prescription['prescriber']}")
        print(f"License: {prescription['prescriber_license']}")
        print(f"Date: {prescription['date_written']}")
        print(f"\nMedications ({len(prescription['medications'])}):")
        for med in prescription['medications']:
            print(f"  - {med}")

        # Validate prescription
        validation = validate_prescription(prescription)

        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)
        print(f"Valid: {'✓' if validation['is_valid'] else '✗'}")

        if validation['errors']:
            print(f"\nErrors ({len(validation['errors'])}):")
            for error in validation['errors']:
                print(f"  ✗ {error}")

        if validation['warnings']:
            print(f"\nWarnings ({len(validation['warnings'])}):")
            for warning in validation['warnings']:
                print(f"  ⚠ {warning}")

        # Generate fill instructions
        if validation['is_valid']:
            fill_instructions = generate_fill_instructions(prescription)
            print("\n" + fill_instructions)

            # Save to pharmacy system
            save_to_pharmacy_system(prescription)

            # Save fill instructions
            instructions_file = "fill_instructions.txt"
            with open(instructions_file, 'w') as f:
                f.write(fill_instructions)
            print(f"\n✓ Saved fill instructions to {instructions_file}")

        else:
            print("\n⚠ Prescription requires manual review before processing")

        print("\n✓ Prescription processing completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
