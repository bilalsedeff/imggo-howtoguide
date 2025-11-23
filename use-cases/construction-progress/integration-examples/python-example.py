"""
Construction Progress Tracking - Python Example
Extract progress data from construction site photos in YAML format
"""

import os
import sys
import yaml
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def track_construction_progress(image_url: str) -> dict:
    """Extract construction progress from site photo"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("CONSTRUCTION_PATTERN_ID", "pat_construction_yaml")

    print(f"\nProcessing construction image: {image_url}")

    result = client.process_image_url(
        image_url=image_url,
        pattern_id=PATTERN_ID
    )

    # Parse YAML result
    progress_data = yaml.safe_load(result)

    return progress_data


def calculate_overall_completion(progress: dict) -> float:
    """Calculate overall project completion percentage"""
    if 'zones' not in progress or not progress['zones']:
        return 0.0

    total_completion = sum(zone.get('overall_completion', 0) for zone in progress['zones'])
    return total_completion / len(progress['zones'])


def identify_behind_schedule_zones(progress: dict, threshold: float = 70.0) -> list:
    """Identify zones that are behind schedule"""
    behind_schedule = []

    for zone in progress.get('zones', []):
        completion = zone.get('overall_completion', 0)
        if completion < threshold:
            behind_schedule.append({
                'zone_id': zone.get('zone_id'),
                'completion': completion,
                'gap': threshold - completion
            })

    return behind_schedule


def generate_progress_report(progress: dict) -> str:
    """Generate human-readable progress report"""
    report = []
    report.append(f"Project: {progress.get('project_id', 'Unknown')}")
    report.append(f"Date: {progress.get('inspection_date', 'Unknown')}")
    report.append("-" * 60)

    overall = calculate_overall_completion(progress)
    report.append(f"\nOverall Completion: {overall:.1f}%")

    report.append(f"\nZone Progress:")
    for zone in progress.get('zones', []):
        zone_id = zone.get('zone_id', 'Unknown')
        completion = zone.get('overall_completion', 0)
        report.append(f"  {zone_id}: {completion}%")

    behind = identify_behind_schedule_zones(progress)
    if behind:
        report.append(f"\nZones Behind Schedule:")
        for zone in behind:
            report.append(f"  {zone['zone_id']}: {zone['completion']}% ({zone['gap']:.1f}% gap)")

    return "\n".join(report)


def main():
    print("="*60)
    print("CONSTRUCTION PROGRESS TRACKING - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    # Example construction site image URL
    image_url = "https://construction-camera.example.com/site-123/latest.jpg"

    try:
        # Track progress
        progress = track_construction_progress(image_url)

        # Display progress
        print("\n" + "="*60)
        print("CONSTRUCTION PROGRESS")
        print("="*60)
        report = generate_progress_report(progress)
        print(report)

        # Save YAML
        output_file = "construction_progress.yaml"
        with open(output_file, 'w') as f:
            yaml.dump(progress, f, default_flow_style=False, sort_keys=False)
        print(f"\n✓ Saved to {output_file}")

        print("\n✓ Construction progress tracking completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
