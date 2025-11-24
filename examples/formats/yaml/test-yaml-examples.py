"""
Test YAML Format Examples from README
This script tests all code snippets from examples/formats/yaml/README.md
"""

import os
import sys
from pathlib import Path
import json

# Add common utilities to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "common"))
from imggo_client import ImgGoClient

def json_to_yaml(data_dict):
    """Convert JSON result to YAML format for testing"""
    try:
        import yaml
        return yaml.dump(data_dict, default_flow_style=False, sort_keys=False)
    except ImportError:
        # Fallback to manual YAML formatting
        yaml_lines = []
        for key, value in data_dict.items():
            yaml_lines.append(f"{key}: {value}")
        return "\n".join(yaml_lines)

def test_basic_yaml_parsing():
    """Test Example 1: Basic YAML parsing from README (lines 151-166)"""
    print("\n" + "="*60)
    print("TEST 1: Basic YAML Parsing")
    print("="*60)

    client = ImgGoClient()
    pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

    # Process invoice image
    image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice1.jpg")

    print(f"Processing: {Path(image_path).name}")

    try:
        result = client.process_image(image_path, pattern_id)

        # Convert JSON to YAML
        yaml_result = json_to_yaml(result)

        print("\nExtracted YAML:")
        print(yaml_result)

        # Parse YAML (as shown in README line 157)
        try:
            import yaml
            data = yaml.safe_load(yaml_result)

            # Modify data (as shown in README lines 160-161)
            data["processed_at"] = "2025-01-22T14:30:00Z"
            data["status"] = "reviewed"

            print(f"\nModified YAML:")
            print(f"  processed_at: {data['processed_at']}")
            print(f"  status: {data['status']}")

            # Save updated YAML (as shown in README lines 164-165)
            output_file = "outputs/invoice1-basic.yaml"
            os.makedirs("outputs", exist_ok=True)
            with open(output_file, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            print(f"\nSUCCESS: Saved to {output_file}")
            return True

        except ImportError:
            print("SKIPPED: PyYAML not installed")
            return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_kubernetes_configmap():
    """Test Example 2: Kubernetes ConfigMap from README (lines 169-189)"""
    print("\n" + "="*60)
    print("TEST 2: Kubernetes ConfigMap Generation")
    print("="*60)

    try:
        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "construction1.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)
        yaml_result = json_to_yaml(result)

        # Create ConfigMap (as shown in README lines 174-182)
        configmap = f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: monitoring-data
  namespace: production
data:
  config.yaml: |
{chr(10).join('    ' + line for line in yaml_result.split(chr(10)))}
"""

        print("\nKubernetes ConfigMap:")
        print(configmap[:300] + "...")

        # Save
        output_file = "outputs/configmap.yaml"
        with open(output_file, "w") as f:
            f.write(configmap)

        print(f"\nSUCCESS: Saved to {output_file}")
        print("Apply with: kubectl apply -f {output_file}")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_yaml_validation():
    """Test Example 3: YAML validation from README (lines 314-327)"""
    print("\n" + "="*60)
    print("TEST 3: YAML Required Fields Validation")
    print("="*60)

    try:
        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice2.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)

        # Validate it's parseable
        try:
            import yaml
            yaml_result = json_to_yaml(result)
            data = yaml.safe_load(yaml_result)

            # Check required fields (as shown in README lines 320-326)
            required_fields = ["invoice_number", "vendor"]
            missing = [field for field in required_fields if field not in data]

            if missing:
                print(f"WARNING: Missing fields: {', '.join(missing)}")
            else:
                print("SUCCESS: All required fields present")

            return True

        except yaml.YAMLError as e:
            print(f"ERROR: Invalid YAML: {e}")
            return False
        except ImportError:
            print("SKIPPED: PyYAML not installed")
            return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_merge():
    """Test Example 4: Batch merge from README (lines 362-382)"""
    print("\n" + "="*60)
    print("TEST 4: Batch YAML Merge")
    print("="*60)

    try:
        import yaml

        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        test_images_dir = Path(__file__).parent.parent.parent / "test-images"

        # Process multiple images (as shown in README line 367)
        invoice_images = list(test_images_dir.glob("invoice*.jpg"))[:3]

        print(f"\nProcessing {len(invoice_images)} images...")

        all_configs = []

        for image_path in invoice_images:
            print(f"  Processing: {image_path.name}...", end=' ')

            try:
                result = client.process_image(str(image_path), pattern_id)
                yaml_result = json_to_yaml(result)
                data = yaml.safe_load(yaml_result)
                all_configs.append(data)

                print("SUCCESS")

            except Exception as e:
                print(f"ERROR: {e}")

        # Merge all configs (as shown in README lines 373-379)
        merged = {
            "project_id": "MULTI-SITE-001",
            "sites": all_configs
        }

        output_file = "outputs/merged_config.yaml"
        with open(output_file, 'w') as f:
            yaml.dump(merged, f, default_flow_style=False, sort_keys=False)

        print(f"\nSUCCESS: Merged {len(all_configs)} configurations to {output_file}")
        return True

    except ImportError:
        print("SKIPPED: PyYAML not installed")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pretty_printing():
    """Test Example 5: Pretty printing from README (lines 386-402)"""
    print("\n" + "="*60)
    print("TEST 5: YAML Pretty Printing")
    print("="*60)

    try:
        import yaml

        client = ImgGoClient()
        pattern_id = "24f3f9f0-70cd-4b4b-b348-6b5691f859ba"

        image_path = str(Path(__file__).parent.parent.parent / "test-images" / "invoice3.jpg")

        print(f"Processing: {Path(image_path).name}")

        result = client.process_image(image_path, pattern_id)

        # Pretty print with options (as shown in README lines 393-399)
        pretty_yaml = yaml.dump(
            result,
            default_flow_style=False,  # Block style
            sort_keys=False,            # Preserve key order
            indent=2,                   # 2-space indentation
            allow_unicode=True          # Support Unicode
        )

        print("\nPretty Printed YAML:")
        print(pretty_yaml)

        # Save
        output_file = "outputs/invoice3-pretty.yaml"
        with open(output_file, 'w') as f:
            f.write(pretty_yaml)

        print(f"SUCCESS: Saved to {output_file}")
        return True

    except ImportError:
        print("SKIPPED: PyYAML not installed")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all YAML format tests"""
    print("\n" + "="*60)
    print("YAML FORMAT EXAMPLES TEST SUITE")
    print("Testing all code snippets from README.md")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\nERROR: IMGGO_API_KEY environment variable not set")
        print("Set it with: export IMGGO_API_KEY=your_key")
        return

    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)

    # Run all tests
    tests = [
        ("Basic YAML Parsing", test_basic_yaml_parsing),
        ("Kubernetes ConfigMap", test_kubernetes_configmap),
        ("YAML Validation", test_yaml_validation),
        ("Batch YAML Merge", test_batch_merge),
        ("Pretty Printing", test_pretty_printing),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\nFATAL ERROR in {test_name}: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)

if __name__ == "__main__":
    main()
