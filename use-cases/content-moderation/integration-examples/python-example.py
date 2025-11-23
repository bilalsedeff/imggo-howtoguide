"""
Content Moderation - Python Integration Example
Detect inappropriate content in images using AI-powered analysis
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_content_image(image_path: str) -> dict:
    """Process image for content moderation"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("CONTENT_MODERATION_PATTERN_ID", "pat_content_moderation_json")

    print(f"\nProcessing image for moderation: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return json.loads(result) if isinstance(result, str) else result


def calculate_risk_score(moderation_result: dict) -> dict:
    """Calculate overall risk score and categorize content"""
    risk_analysis = {
        'overall_risk': 0,
        'risk_level': 'SAFE',
        'flagged_categories': [],
        'action_required': 'APPROVE',
        'reasons': []
    }

    # Check for explicit content
    if moderation_result.get('explicit_content', {}).get('detected', False):
        confidence = moderation_result['explicit_content'].get('confidence', 0)
        risk_analysis['overall_risk'] += confidence * 100
        risk_analysis['flagged_categories'].append('Explicit Content')
        risk_analysis['reasons'].append(f"Explicit content detected ({confidence:.0%} confidence)")

    # Check for violence
    if moderation_result.get('violence', {}).get('detected', False):
        confidence = moderation_result['violence'].get('confidence', 0)
        risk_analysis['overall_risk'] += confidence * 80
        risk_analysis['flagged_categories'].append('Violence')
        risk_analysis['reasons'].append(f"Violent content detected ({confidence:.0%} confidence)")

    # Check for hate symbols
    if moderation_result.get('hate_symbols', {}).get('detected', False):
        risk_analysis['overall_risk'] += 100
        risk_analysis['flagged_categories'].append('Hate Symbols')
        risk_analysis['reasons'].append("Hate symbols detected")

    # Check for profanity in text
    if moderation_result.get('profanity', {}).get('detected', False):
        risk_analysis['overall_risk'] += 30
        risk_analysis['flagged_categories'].append('Profanity')

    # Determine risk level
    if risk_analysis['overall_risk'] >= 80:
        risk_analysis['risk_level'] = 'HIGH'
        risk_analysis['action_required'] = 'BLOCK'
    elif risk_analysis['overall_risk'] >= 50:
        risk_analysis['risk_level'] = 'MEDIUM'
        risk_analysis['action_required'] = 'REVIEW'
    elif risk_analysis['overall_risk'] >= 20:
        risk_analysis['risk_level'] = 'LOW'
        risk_analysis['action_required'] = 'FLAG'
    else:
        risk_analysis['risk_level'] = 'SAFE'
        risk_analysis['action_required'] = 'APPROVE'

    return risk_analysis


def save_to_moderation_system(moderation_result: dict, risk_analysis: dict, content_id: str) -> bool:
    """Save moderation results to content management system"""
    print("\n" + "="*60)
    print("SAVING TO MODERATION SYSTEM")
    print("="*60)

    # In production: integrate with moderation platforms (AWS Rekognition, Google Cloud Vision, custom CMS)
    payload = {
        'content_id': content_id,
        'timestamp': moderation_result.get('timestamp'),
        'risk_score': risk_analysis['overall_risk'],
        'risk_level': risk_analysis['risk_level'],
        'action': risk_analysis['action_required'],
        'flagged_categories': risk_analysis['flagged_categories'],
        'moderation_details': moderation_result
    }

    print(f"Content ID: {content_id}")
    print(f"Risk Level: {risk_analysis['risk_level']}")
    print(f"Action: {risk_analysis['action_required']}")

    # Simulate API call
    # response = requests.post('https://moderation-system.example.com/api/moderate', json=payload)

    print("\n✓ Moderation result saved (simulated)")
    return True


def trigger_moderation_action(risk_analysis: dict, content_id: str) -> str:
    """Execute moderation action based on risk level"""
    action = risk_analysis['action_required']

    print("\n" + "="*60)
    print("MODERATION ACTION")
    print("="*60)

    if action == 'BLOCK':
        print(f"✗ CONTENT BLOCKED - Content ID: {content_id}")
        print("  • Content removed from platform")
        print("  • User notified of policy violation")
        print("  • Account flagged for review")
        # In production: Call content removal API, notify user, log incident
        return "BLOCKED"

    elif action == 'REVIEW':
        print(f"⚠ FLAGGED FOR REVIEW - Content ID: {content_id}")
        print("  • Content hidden pending manual review")
        print("  • Assigned to moderation queue")
        print("  • User notified of pending review")
        # In production: Add to review queue, notify moderators
        return "PENDING_REVIEW"

    elif action == 'FLAG':
        print(f"⚠ CONTENT FLAGGED - Content ID: {content_id}")
        print("  • Content allowed but monitored")
        print("  • Added to watchlist")
        # In production: Add to monitoring system
        return "FLAGGED"

    else:  # APPROVE
        print(f"✓ CONTENT APPROVED - Content ID: {content_id}")
        print("  • Content published")
        # In production: Publish content
        return "APPROVED"


def generate_moderation_report(moderation_result: dict, risk_analysis: dict) -> str:
    """Generate moderation report"""
    lines = []

    lines.append("CONTENT MODERATION REPORT")
    lines.append("=" * 60)
    lines.append(f"Risk Level: {risk_analysis['risk_level']}")
    lines.append(f"Risk Score: {risk_analysis['overall_risk']:.1f}/100")
    lines.append(f"Action: {risk_analysis['action_required']}")
    lines.append("")

    if risk_analysis['flagged_categories']:
        lines.append("FLAGGED CATEGORIES:")
        for category in risk_analysis['flagged_categories']:
            lines.append(f"  ✗ {category}")
        lines.append("")

    if risk_analysis['reasons']:
        lines.append("REASONS:")
        for reason in risk_analysis['reasons']:
            lines.append(f"  • {reason}")
        lines.append("")

    lines.append("DETAILED ANALYSIS:")
    for key, value in moderation_result.items():
        if isinstance(value, dict) and 'detected' in value:
            status = "✗ DETECTED" if value['detected'] else "✓ CLEAN"
            conf = value.get('confidence', 0)
            lines.append(f"  {key}: {status} ({conf:.0%} confidence)")

    return "\n".join(lines)


def main():
    print("="*60)
    print("CONTENT MODERATION - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "content-moderation1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        sys.exit(1)

    try:
        # Process image for moderation
        moderation_result = process_content_image(str(test_image))

        # Save raw JSON
        output_file = "moderation_result.json"
        with open(output_file, 'w') as f:
            json.dump(moderation_result, f, indent=2)
        print(f"\n✓ Saved moderation result to {output_file}")

        # Calculate risk
        risk_analysis = calculate_risk_score(moderation_result)

        print("\n" + "="*60)
        print("MODERATION ANALYSIS")
        print("="*60)
        print(f"Risk Level: {risk_analysis['risk_level']}")
        print(f"Risk Score: {risk_analysis['overall_risk']:.1f}/100")
        print(f"Recommended Action: {risk_analysis['action_required']}")

        if risk_analysis['flagged_categories']:
            print(f"\nFlagged Categories ({len(risk_analysis['flagged_categories'])}):")
            for category in risk_analysis['flagged_categories']:
                print(f"  ✗ {category}")

        # Generate report
        report = generate_moderation_report(moderation_result, risk_analysis)
        print("\n" + report)

        # Save to moderation system
        content_id = f"IMG-{Path(test_image).stem}"
        save_to_moderation_system(moderation_result, risk_analysis, content_id)

        # Trigger action
        action_result = trigger_moderation_action(risk_analysis, content_id)

        # Save report
        report_file = "moderation_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n✓ Saved moderation report to {report_file}")

        print("\n✓ Content moderation completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
