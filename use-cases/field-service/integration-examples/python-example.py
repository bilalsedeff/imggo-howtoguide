"""
Field Service - Python Integration Example
Extract service report data from technician photos
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_service_photo(image_path: str) -> dict:
    """Process field service photo and extract report data"""
    client = ImgGoClient()
    PATTERN_ID = os.getenv("FIELD_SERVICE_PATTERN_ID", "pat_field_service_json")

    print(f"\nProcessing service photo: {Path(image_path).name}")
    result = client.process_image(image_path=image_path, pattern_id=PATTERN_ID)
    return json.loads(result) if isinstance(result, str) else result


def generate_work_order(service_data: dict) -> dict:
    """Generate work order from service data"""
    work_order = {
        'work_order_id': service_data.get('work_order_id') or f"WO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'technician': service_data.get('technician_name'),
        'customer': service_data.get('customer_name'),
        'location': service_data.get('service_location'),
        'equipment': service_data.get('equipment_type'),
        'issue': service_data.get('reported_issue'),
        'diagnosis': service_data.get('diagnosis'),
        'actions_taken': service_data.get('actions_taken', []),
        'parts_used': service_data.get('parts_used', []),
        'labor_hours': service_data.get('labor_hours', 0),
        'status': 'COMPLETED' if service_data.get('completed') else 'IN_PROGRESS',
        'timestamp': datetime.now().isoformat()
    }
    return work_order


def calculate_service_cost(work_order: dict) -> dict:
    """Calculate total service cost"""
    costs = {
        'labor_cost': 0,
        'parts_cost': 0,
        'total_cost': 0
    }

    # Labor cost ($75/hour standard rate)
    labor_hours = float(work_order.get('labor_hours', 0))
    costs['labor_cost'] = labor_hours * 75.0

    # Parts cost
    parts = work_order.get('parts_used', [])
    for part in parts:
        if isinstance(part, dict):
            costs['parts_cost'] += float(part.get('price', 0)) * int(part.get('quantity', 1))

    costs['total_cost'] = costs['labor_cost'] + costs['parts_cost']
    return costs


def save_to_field_service_system(work_order: dict, costs: dict) -> bool:
    """Save to field service management system"""
    print("\n" + "="*60)
    print("SAVING TO FIELD SERVICE SYSTEM")
    print("="*60)

    payload = {
        'work_order': work_order,
        'costs': costs,
        'created_at': datetime.now().isoformat()
    }

    print(f"Work Order: {work_order['work_order_id']}")
    print(f"Technician: {work_order['technician']}")
    print(f"Status: {work_order['status']}")
    print(f"Total Cost: ${costs['total_cost']:.2f}")

    # In production: integrate with ServiceTitan, FieldEdge, etc.
    # response = requests.post('https://fsm-system.example.com/api/work-orders', json=payload)

    print("\n✓ Work order saved (simulated)")
    return True


def main():
    print("="*60)
    print("FIELD SERVICE - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "field-service1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        print("Using placeholder for demonstration")
        sys.exit(1)

    try:
        # Process service photo
        service_data = process_service_photo(str(test_image))

        # Save raw JSON
        with open("service_data.json", 'w') as f:
            json.dump(service_data, f, indent=2)
        print(f"\n✓ Saved service data to service_data.json")

        # Generate work order
        work_order = generate_work_order(service_data)

        print("\n" + "="*60)
        print("WORK ORDER DETAILS")
        print("="*60)
        print(f"Work Order ID: {work_order['work_order_id']}")
        print(f"Technician: {work_order['technician']}")
        print(f"Customer: {work_order['customer']}")
        print(f"Equipment: {work_order['equipment']}")
        print(f"Status: {work_order['status']}")

        # Calculate costs
        costs = calculate_service_cost(work_order)
        print(f"\nLabor Hours: {work_order['labor_hours']}")
        print(f"Labor Cost: ${costs['labor_cost']:.2f}")
        print(f"Parts Cost: ${costs['parts_cost']:.2f}")
        print(f"Total Cost: ${costs['total_cost']:.2f}")

        # Save to FSM system
        save_to_field_service_system(work_order, costs)

        print("\n✓ Field service report processing completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
