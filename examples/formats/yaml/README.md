# YAML Output Examples

Complete working examples for converting images to YAML using ImgGo API.

## What is YAML Output?

YAML (YAML Ain't Markup Language) is perfect for:
- Configuration files
- DevOps and CI/CD (GitHub Actions, GitLab CI)
- Kubernetes manifests
- Ansible playbooks
- Docker Compose
- Human-readable configs

## Examples Included

### 1. Construction Progress to YAML
Extract construction site progress as configuration data.

**Use case**: Project monitoring, progress tracking

**Output example**:
```yaml
project_id: PRJ-2025-001
inspection_date: 2025-01-22
zones:
  - zone_id: A-North
    work_packages:
      - foundation
      - framing
    overall_completion: 75
  - zone_id: B-South
    work_packages:
      - electrical
      - plumbing
    overall_completion: 60
```

### 2. Quality Control Reports
Generate QC inspection reports in YAML.

**Use case**: Manufacturing quality control

**Output example**:
```yaml
inspection_id: QC-2025-001
product_sku: WID-001
inspector: John Doe
defects:
  - type: surface_scratch
    severity: minor
    location: top_panel
status: conditional_pass
```

### 3. YAML to Kubernetes ConfigMap
Convert image data to Kubernetes configurations.

**Use case**: GitOps, infrastructure as code

**Output example**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: construction-progress
  namespace: monitoring
data:
  progress.yaml: |
    project_id: PRJ-2025-001
    zones: [...]
```

### 4. Batch Merge YAML Configs
Combine multiple YAML outputs into unified config.

**Use case**: Multi-site monitoring, aggregated reporting

### 5. YAML Validation
Validate YAML structure and required fields.

**Use case**: Configuration validation, CI/CD pipelines

## Running the Examples

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export IMGGO_API_KEY="your_api_key_here"
```

### Run All Examples

```bash
python image-to-yaml.py
```

### Process Single Image

```python
from imggo_client import ImgGoClient
import yaml

client = ImgGoClient()
yaml_result = client.process_image(
    image_path="construction.jpg",
    pattern_id="pat_construction_yaml"
)

# yaml_result is a YAML string
print(yaml_result)

# Parse YAML
data = yaml.safe_load(yaml_result)
print(f"Project: {data['project_id']}")
print(f"Zones: {len(data['zones'])}")
```

## Pattern Setup

Create YAML patterns at [img-go.com/patterns](https://img-go.com/patterns):

1. Click "New Pattern"
2. Select **YAML** as output format
3. Define structure in instructions
4. Publish and copy Pattern ID

**Example instructions**:
```
Extract construction progress in YAML format with this structure:

project_id: Project identifier
inspection_date: ISO date
zones: Array of zone objects
  - zone_id: Zone identifier
    work_packages: List of work types
    overall_completion: Percentage (0-100)
    issues: Optional list of concerns

Use clear indentation and proper YAML syntax.
```

## Integration Examples

### Load and Modify YAML

```python
import yaml

yaml_result = client.process_image("data.jpg", "pat_yaml")

# Parse YAML
data = yaml.safe_load(yaml_result)

# Modify data
data["processed_at"] = "2025-01-22T14:30:00Z"
data["status"] = "reviewed"

# Save updated YAML
with open("updated_config.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

### Kubernetes ConfigMap

```python
yaml_result = client.process_image("monitoring.jpg", "pat_monitoring")

# Create ConfigMap
configmap = f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: monitoring-data
  namespace: production
data:
  config.yaml: |
{chr(10).join('    ' + line for line in yaml_result.split(chr(10)))}
"""

# Apply to cluster
with open("configmap.yaml", "w") as f:
    f.write(configmap)

# kubectl apply -f configmap.yaml
```

### GitHub Actions Workflow

```python
yaml_result = client.process_image("deployment.jpg", "pat_deployment")

# Create workflow file
workflow = f"""name: Auto Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        env:
{chr(10).join('          ' + line for line in yaml_result.split(chr(10)))}
"""

with open(".github/workflows/deploy.yaml", "w") as f:
    f.write(workflow)
```

### Ansible Inventory

```python
import yaml

yaml_result = client.process_image("servers.jpg", "pat_inventory")
data = yaml.safe_load(yaml_result)

# Create Ansible inventory
inventory = {
    "all": {
        "children": {
            "webservers": {
                "hosts": data.get("webservers", [])
            },
            "databases": {
                "hosts": data.get("databases", [])
            }
        }
    }
}

with open("inventory.yaml", "w") as f:
    yaml.dump(inventory, f)

# ansible-playbook -i inventory.yaml playbook.yaml
```

### Docker Compose

```python
yaml_result = client.process_image("services.jpg", "pat_services")

# Wrap in docker-compose structure
compose = f"""version: '3.8'

services:
{chr(10).join('  ' + line for line in yaml_result.split(chr(10)))}
"""

with open("docker-compose.yaml", "w") as f:
    f.write(compose)

# docker-compose up -d
```

## Common Use Cases

- **Construction Progress**: Site monitoring configs
- **Infrastructure as Code**: Kubernetes, Terraform
- **CI/CD Pipelines**: GitHub Actions, GitLab CI
- **Configuration Management**: Ansible, Salt
- **API Configs**: OpenAPI specifications
- **Monitoring**: Prometheus, Grafana configs
- **Deployment**: Docker Compose, Helm values
- **Project Management**: Work breakdown structures
- **Quality Control**: Inspection configurations
- **Environment Settings**: Application configs

## YAML Validation

### Schema Validation

```python
import yaml
from cerberus import Validator

yaml_result = client.process_image("data.jpg", "pat_yaml")
data = yaml.safe_load(yaml_result)

# Define schema
schema = {
    "project_id": {"type": "string", "required": True},
    "zones": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "zone_id": {"type": "string", "required": True},
                "overall_completion": {"type": "integer", "min": 0, "max": 100}
            }
        }
    }
}

# Validate
validator = Validator(schema)
if validator.validate(data):
    print("✓ YAML is valid")
else:
    print("✗ Validation errors:")
    print(validator.errors)
```

### Required Fields Check

```python
import yaml

yaml_result = client.process_image("config.jpg", "pat_config")
data = yaml.safe_load(yaml_result)

required_fields = ["project_id", "zones"]
missing = [field for field in required_fields if field not in data]

if missing:
    raise ValueError(f"Missing required fields: {', '.join(missing)}")

print("✓ All required fields present")
```

## Error Handling

```python
import yaml

try:
    yaml_result = client.process_image("data.jpg", "pat_yaml")

    # Validate YAML syntax
    try:
        data = yaml.safe_load(yaml_result)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")

    # Check data structure
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")

except Exception as e:
    print(f"Error processing YAML: {e}")
```

## Best Practices

1. **Use safe_load**: Avoid yaml.load() for security
2. **Maintain indentation**: 2 spaces is standard
3. **Quote when needed**: Strings with special characters
4. **Validate structure**: Check required fields
5. **Version control**: Store YAML configs in Git
6. **Comments**: Use # for documentation in YAML

## Batch Merge

```python
import yaml

all_configs = []

for image_path in glob.glob("sites/*.jpg"):
    yaml_result = client.process_image(image_path, "pat_site_config")
    data = yaml.safe_load(yaml_result)
    all_configs.append(data)

# Merge all zones
merged = {
    "project_id": "MULTI-SITE-001",
    "sites": all_configs
}

with open("merged_config.yaml", "w") as f:
    yaml.dump(merged, f, default_flow_style=False, sort_keys=False)

print(f"✓ Merged {len(all_configs)} site configurations")
```

## Pretty Printing

```python
import yaml

yaml_result = client.process_image("data.jpg", "pat_yaml")
data = yaml.safe_load(yaml_result)

# Pretty print with options
pretty_yaml = yaml.dump(
    data,
    default_flow_style=False,  # Block style, not inline
    sort_keys=False,            # Preserve key order
    indent=2,                   # 2-space indentation
    allow_unicode=True          # Support Unicode characters
)

print(pretty_yaml)
```

## Git Integration

```python
import yaml
import subprocess

yaml_result = client.process_image("config.jpg", "pat_config")

# Save to repo
config_path = "config/production.yaml"
with open(config_path, "w") as f:
    f.write(yaml_result)

# Git commit
subprocess.run(["git", "add", config_path])
subprocess.run([
    "git", "commit", "-m",
    "Update production config from image scan"
])
subprocess.run(["git", "push", "origin", "main"])

print("✓ Config committed and pushed to Git")
```

## Support

- [ImgGo API Documentation](https://img-go.com/docs)
- [YAML Format Guide](https://img-go.com/docs/output-formats/yaml)
- [YAML Specification](https://yaml.org/spec/)
- Email: support@img-go.com
