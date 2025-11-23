"""
Extract YAML Configuration from Images
Complete example showing how to convert images to YAML format
"""

import os
import sys
from pathlib import Path

# Add common utilities to path
sys.path.append(str(Path(__file__).parent.parent / "common"))

from imggo_client import ImgGoClient


def example_construction_progress_to_yaml():
    """
    Example 1: Construction Site Photo → YAML Progress Config
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Construction Photo → YAML Progress Report")
    print("="*60)

    client = ImgGoClient()

    # Pattern for construction progress (YAML output)
    # Create at img-go.com/patterns with:
    # - Instructions: "Extract construction progress, zones, work packages, completion percentages"
    # - Output format: YAML
    PATTERN_ID = "pat_construction_yaml"

    construction_path = Path(__file__).parent.parent.parent / "test-images" / "construction1.jpg"

    print(f"\nProcessing: {construction_path.name}")

    try:
        result = client.process_image(
            image_path=str(construction_path),
            pattern_id=PATTERN_ID
        )

        # Result is YAML string
        print("\nExtracted YAML:")
        print(result)

        # Save to file
        output_file = "construction_progress.yaml"
        with open(output_file, 'w') as f:
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

        # Parse YAML
        try:
            import yaml

            data = yaml.safe_load(result)

            # Display key metrics
            if isinstance(data, dict):
                if 'zones' in data:
                    print(f"\nProgress Summary:")
                    for zone in data.get('zones', []):
                        zone_id = zone.get('zone_id', 'Unknown')
                        completion = zone.get('overall_completion', 0)
                        print(f"  {zone_id}: {completion}% complete")

        except ImportError:
            print("\n⚠ PyYAML not installed. Install with: pip install pyyaml")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_quality_control_to_yaml():
    """
    Example 2: Quality Control Inspection → YAML Report
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: QC Photo → YAML Defect Report")
    print("="*60)

    client = ImgGoClient()

    # Pattern for quality control
    # Instructions: "Identify defects, measurements, pass/fail status in YAML format"
    # Output: YAML
    PATTERN_ID = "pat_qc_yaml"

    # Using document as QC example
    qc_path = Path(__file__).parent.parent.parent / "test-images" / "document-classification3.png"

    print(f"\nProcessing: {qc_path.name}")

    try:
        result = client.process_image(
            image_path=str(qc_path),
            pattern_id=PATTERN_ID
        )

        print("\nQC Report YAML:")
        print(result)

        # Save to file
        output_file = "qc_inspection.yaml"
        with open(output_file, 'w') as f:
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_yaml_to_kubernetes_config():
    """
    Example 3: Convert YAML to Kubernetes ConfigMap
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Image Data → Kubernetes ConfigMap")
    print("="*60)

    client = ImgGoClient()
    PATTERN_ID = "pat_construction_yaml"

    construction_path = Path(__file__).parent.parent.parent / "test-images" / "construction2.jpg"

    print(f"\nProcessing: {construction_path.name}")

    try:
        result = client.process_image(
            image_path=str(construction_path),
            pattern_id=PATTERN_ID
        )

        # Create Kubernetes ConfigMap
        configmap = f'''apiVersion: v1
kind: ConfigMap
metadata:
  name: construction-progress
  namespace: monitoring
data:
  progress.yaml: |
{result}'''

        # Indent the YAML content
        indented_result = '\n'.join('    ' + line for line in result.split('\n'))

        configmap = f'''apiVersion: v1
kind: ConfigMap
metadata:
  name: construction-progress
  namespace: monitoring
data:
  progress.yaml: |
{indented_result}'''

        print("\nKubernetes ConfigMap:")
        print(configmap)

        # Save
        output_file = "construction-configmap.yaml"
        with open(output_file, 'w') as f:
            f.write(configmap)

        print(f"\n✓ Saved to {output_file}")
        print("\nApply with: kubectl apply -f construction-configmap.yaml")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_yaml_merge_and_transform():
    """
    Example 4: Batch process and merge YAML configs
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Multiple Photos → Merged YAML Config")
    print("="*60)

    client = ImgGoClient()
    PATTERN_ID = "pat_construction_yaml"

    test_images_dir = Path(__file__).parent.parent.parent / "test-images"
    construction_images = list(test_images_dir.glob("construction*.jpg"))[:3]

    print(f"\nProcessing {len(construction_images)} construction photos...")

    all_data = []

    for img_path in construction_images:
        print(f"\n  Processing: {img_path.name}... ", end='')

        try:
            result = client.process_image(
                image_path=str(img_path),
                pattern_id=PATTERN_ID
            )

            # Parse YAML
            try:
                import yaml
                data = yaml.safe_load(result)
                all_data.append(data)
                print("✓")

            except ImportError:
                print("⚠ (PyYAML not installed)")
                all_data.append({"raw": result})

        except Exception as e:
            print(f"✗ ({e})")

    # Merge configs
    if all_data:
        try:
            import yaml

            merged_config = {
                "project_id": "PRJ-2025-001",
                "monitoring_timestamp": "2025-01-22T14:30:00Z",
                "zones": []
            }

            # Extract zones from all reports
            for data in all_data:
                if isinstance(data, dict) and 'zones' in data:
                    merged_config['zones'].extend(data['zones'])

            # Save merged config
            output_file = "merged_construction_progress.yaml"

            with open(output_file, 'w') as f:
                yaml.dump(merged_config, f, default_flow_style=False, sort_keys=False)

            print(f"\n✓ Merged {len(all_data)} configs to {output_file}")

            # Display summary
            total_zones = len(merged_config.get('zones', []))
            print(f"  Total zones tracked: {total_zones}")

        except ImportError:
            print("\n⚠ PyYAML not installed. Cannot merge configs")


def example_yaml_validation():
    """
    Example 5: Validate YAML structure
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: YAML Validation and Schema Check")
    print("="*60)

    yaml_file = "construction_progress.yaml"

    if not Path(yaml_file).exists():
        print(f"\n✗ {yaml_file} not found. Run example 1 first.")
        return

    try:
        import yaml

        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        print(f"Loading: {yaml_file}")

        # Validate structure
        print("\nValidating structure...")

        required_fields = ['project_id', 'zones']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            print(f"✗ Missing required fields: {', '.join(missing_fields)}")
        else:
            print("✓ All required fields present")

        # Validate zones
        if 'zones' in data and isinstance(data['zones'], list):
            print(f"✓ Found {len(data['zones'])} zones")

            for i, zone in enumerate(data['zones']):
                if 'zone_id' not in zone:
                    print(f"  ✗ Zone {i}: missing zone_id")
                elif 'overall_completion' not in zone:
                    print(f"  ✗ Zone {zone['zone_id']}: missing completion")
                else:
                    print(f"  ✓ Zone {zone['zone_id']}: {zone['overall_completion']}% complete")

    except ImportError:
        print("\n⚠ PyYAML not installed. Install with: pip install pyyaml")
    except yaml.YAMLError as e:
        print(f"\n✗ YAML parsing error: {e}")


def main():
    """
    Run all YAML extraction examples
    """
    print("\n" + "="*60)
    print("IMAGE TO YAML CONVERSION EXAMPLES")
    print("Using ImgGo API to extract YAML configs from images")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY environment variable not set")
        print("  Set it in .env file or export IMGGO_API_KEY=your_key")
        return

    # Run examples
    try:
        example_construction_progress_to_yaml()
        example_quality_control_to_yaml()
        example_yaml_to_kubernetes_config()
        example_yaml_merge_and_transform()
        example_yaml_validation()

        print("\n" + "="*60)
        print("ALL YAML EXAMPLES COMPLETED")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
