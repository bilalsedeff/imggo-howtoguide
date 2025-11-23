"""
Insurance Claims Processing - Python Integration Example
Extract claims data from images and integrate with claims management systems
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_insurance_claim(image_path: str) -> dict:
    """Process insurance claim document and extract structured data"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("INSURANCE_CLAIMS_PATTERN_ID", "pat_insurance_claim_json")

    print(f"\nProcessing insurance claim: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return json.loads(result) if isinstance(result, str) else result


def calculate_claim_total(claim_data: dict) -> float:
    """Calculate total claim amount"""
    line_items = claim_data.get('line_items', [])

    total = 0.0
    for item in line_items:
        amount = item.get('amount', 0)
        quantity = item.get('quantity', 1)
        total += float(amount) * int(quantity)

    return total


def validate_claim(claim_data: dict) -> dict:
    """Validate insurance claim for processing"""
    validation = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'risk_flags': []
    }

    # Required fields check
    required_fields = ['claim_number', 'claimant_name', 'incident_date', 'claim_type']

    for field in required_fields:
        if not claim_data.get(field):
            validation['is_valid'] = False
            validation['errors'].append(f"Missing required field: {field}")

    # Policy validation
    if 'policy_number' in claim_data:
        policy_number = claim_data['policy_number']
        # In production, validate against policy database
        if not policy_number or len(str(policy_number)) < 5:
            validation['errors'].append("Invalid policy number")
            validation['is_valid'] = False
    else:
        validation['errors'].append("Missing policy number")
        validation['is_valid'] = False

    # Incident date validation
    if 'incident_date' in claim_data:
        try:
            incident_date = datetime.strptime(claim_data['incident_date'], '%Y-%m-%d')
            days_since_incident = (datetime.now() - incident_date).days

            if days_since_incident < 0:
                validation['errors'].append("Incident date cannot be in the future")
                validation['is_valid'] = False
            elif days_since_incident > 365:
                validation['warnings'].append(f"Claim filed {days_since_incident} days after incident - requires review")
        except ValueError:
            validation['errors'].append("Invalid incident date format")
            validation['is_valid'] = False

    # Claim amount validation
    total_amount = calculate_claim_total(claim_data)

    if total_amount == 0:
        validation['errors'].append("Claim amount is zero")
        validation['is_valid'] = False
    elif total_amount > 50000:
        validation['risk_flags'].append(f"High value claim: ${total_amount:,.2f} - requires senior adjuster review")

    # Check for duplicate claims (simplified)
    claim_number = claim_data.get('claim_number')
    if claim_number:
        # In production, check against claims database
        # if is_duplicate_claim(claim_number):
        #     validation['risk_flags'].append("Possible duplicate claim")
        pass

    # Fraud detection indicators
    if 'description' in claim_data:
        description = claim_data['description'].lower()
        fraud_keywords = ['fire', 'total loss', 'stolen', 'vandalism']

        matched_keywords = [kw for kw in fraud_keywords if kw in description]
        if matched_keywords:
            validation['risk_flags'].append(f"Requires fraud review - Keywords: {', '.join(matched_keywords)}")

    return validation


def determine_claim_priority(claim_data: dict, validation: dict) -> str:
    """Determine claim processing priority"""
    total_amount = calculate_claim_total(claim_data)
    claim_type = claim_data.get('claim_type', '').lower()

    # High priority cases
    if any('fraud' in flag.lower() for flag in validation.get('risk_flags', [])):
        return 'HIGH - Fraud Review Required'

    if total_amount > 100000:
        return 'HIGH - Large Claim'

    if claim_type in ['injury', 'medical', 'death']:
        return 'HIGH - Medical/Injury Claim'

    # Medium priority
    if total_amount > 10000:
        return 'MEDIUM'

    if validation.get('warnings'):
        return 'MEDIUM'

    # Low priority
    return 'LOW - Standard Processing'


def assign_adjuster(claim_data: dict, priority: str) -> dict:
    """Assign claim to appropriate adjuster"""
    claim_type = claim_data.get('claim_type', '').lower()

    # In production, integrate with adjuster assignment system
    assignment = {
        'adjuster_id': None,
        'adjuster_name': None,
        'team': None
    }

    if 'HIGH' in priority:
        assignment['team'] = 'Senior Adjusters'
        assignment['adjuster_name'] = 'Senior Team (Auto-assign)'
    elif claim_type in ['auto', 'vehicle']:
        assignment['team'] = 'Auto Claims'
        assignment['adjuster_name'] = 'Auto Team (Auto-assign)'
    elif claim_type in ['property', 'home']:
        assignment['team'] = 'Property Claims'
        assignment['adjuster_name'] = 'Property Team (Auto-assign)'
    else:
        assignment['team'] = 'General Claims'
        assignment['adjuster_name'] = 'General Team (Auto-assign)'

    return assignment


def save_to_claims_system(claim_data: dict, validation: dict, assignment: dict) -> bool:
    """Save claim to insurance claims management system"""
    print("\n" + "="*60)
    print("SAVING TO CLAIMS MANAGEMENT SYSTEM")
    print("="*60)

    # In production, integrate with your CMS (Guidewire, Duck Creek, etc.)
    api_payload = {
        'claim_info': {
            'claim_number': claim_data.get('claim_number'),
            'policy_number': claim_data.get('policy_number'),
            'claim_type': claim_data.get('claim_type'),
            'status': 'PENDING_REVIEW' if not validation['is_valid'] else 'OPEN'
        },
        'claimant': {
            'name': claim_data.get('claimant_name'),
            'contact': claim_data.get('contact_info', {})
        },
        'incident': {
            'date': claim_data.get('incident_date'),
            'location': claim_data.get('incident_location'),
            'description': claim_data.get('description')
        },
        'financial': {
            'claimed_amount': calculate_claim_total(claim_data),
            'line_items': claim_data.get('line_items', [])
        },
        'assignment': assignment,
        'validation': validation
    }

    print(f"API Payload:")
    print(json.dumps(api_payload, indent=2))

    # Simulate API call
    # response = requests.post('https://claims-system.example.com/api/claims', json=api_payload)

    print("\n✓ Claim saved to CMS (simulated)")
    return True


def generate_adjuster_summary(claim_data: dict, validation: dict, priority: str, assignment: dict) -> str:
    """Generate summary for adjuster"""
    lines = []

    lines.append("CLAIM ADJUSTER SUMMARY")
    lines.append("=" * 60)
    lines.append(f"Claim Number: {claim_data.get('claim_number')}")
    lines.append(f"Policy Number: {claim_data.get('policy_number')}")
    lines.append(f"Priority: {priority}")
    lines.append(f"Assigned To: {assignment['adjuster_name']} ({assignment['team']})")
    lines.append("")
    lines.append("CLAIMANT INFORMATION")
    lines.append(f"  Name: {claim_data.get('claimant_name')}")

    if 'contact_info' in claim_data:
        contact = claim_data['contact_info']
        if isinstance(contact, dict):
            lines.append(f"  Phone: {contact.get('phone', 'N/A')}")
            lines.append(f"  Email: {contact.get('email', 'N/A')}")

    lines.append("")
    lines.append("INCIDENT DETAILS")
    lines.append(f"  Date: {claim_data.get('incident_date')}")
    lines.append(f"  Type: {claim_data.get('claim_type')}")
    lines.append(f"  Location: {claim_data.get('incident_location', 'Not specified')}")
    lines.append(f"  Description: {claim_data.get('description', 'Not specified')}")

    lines.append("")
    lines.append("FINANCIAL SUMMARY")
    total_amount = calculate_claim_total(claim_data)
    lines.append(f"  Total Claimed: ${total_amount:,.2f}")

    if claim_data.get('line_items'):
        lines.append(f"  Line Items: {len(claim_data['line_items'])}")

    if validation.get('risk_flags'):
        lines.append("")
        lines.append("⚠ RISK FLAGS:")
        for flag in validation['risk_flags']:
            lines.append(f"  - {flag}")

    if validation.get('warnings'):
        lines.append("")
        lines.append("⚠ WARNINGS:")
        for warning in validation['warnings']:
            lines.append(f"  - {warning}")

    lines.append("")
    lines.append("RECOMMENDED ACTIONS:")
    if not validation['is_valid']:
        lines.append("  [ ] Obtain missing information")
    if validation.get('risk_flags'):
        lines.append("  [ ] Conduct fraud investigation")
    if total_amount > 50000:
        lines.append("  [ ] Request senior review")
    lines.append("  [ ] Contact claimant for details")
    lines.append("  [ ] Review policy coverage")
    lines.append("  [ ] Inspect damaged property (if applicable)")
    lines.append("  [ ] Obtain repair estimates")

    return "\n".join(lines)


def main():
    print("="*60)
    print("INSURANCE CLAIMS PROCESSING - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "insurance-claim1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        print("Using placeholder for demonstration")
        # In production, handle missing file
        sys.exit(1)

    try:
        # Process claim
        claim_data = process_insurance_claim(str(test_image))

        # Save raw JSON
        output_file = "claim_data.json"
        with open(output_file, 'w') as f:
            json.dump(claim_data, f, indent=2)
        print(f"\n✓ Saved claim data to {output_file}")

        print("\n" + "="*60)
        print("EXTRACTED CLAIM DATA")
        print("="*60)
        print(f"Claim Number: {claim_data.get('claim_number')}")
        print(f"Policy Number: {claim_data.get('policy_number')}")
        print(f"Claimant: {claim_data.get('claimant_name')}")
        print(f"Claim Type: {claim_data.get('claim_type')}")
        print(f"Incident Date: {claim_data.get('incident_date')}")

        total_amount = calculate_claim_total(claim_data)
        print(f"Total Amount: ${total_amount:,.2f}")

        # Validate claim
        validation = validate_claim(claim_data)

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

        if validation['risk_flags']:
            print(f"\nRisk Flags ({len(validation['risk_flags'])}):")
            for flag in validation['risk_flags']:
                print(f"  ⚠ {flag}")

        # Determine priority and assign
        priority = determine_claim_priority(claim_data, validation)
        assignment = assign_adjuster(claim_data, priority)

        print("\n" + "="*60)
        print("CLAIM ROUTING")
        print("="*60)
        print(f"Priority: {priority}")
        print(f"Assigned Team: {assignment['team']}")
        print(f"Assigned Adjuster: {assignment['adjuster_name']}")

        # Generate adjuster summary
        summary = generate_adjuster_summary(claim_data, validation, priority, assignment)
        print("\n" + summary)

        # Save to claims system
        save_to_claims_system(claim_data, validation, assignment)

        # Save adjuster summary
        summary_file = "adjuster_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        print(f"\n✓ Saved adjuster summary to {summary_file}")

        print("\n✓ Insurance claim processing completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
