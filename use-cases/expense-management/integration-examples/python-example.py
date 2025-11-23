"""
Expense Management - Python Example
Process receipt images and extract expense data
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add common client to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_receipt(image_path: str) -> dict:
    """Process receipt and extract expense data"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("RECEIPT_PATTERN_ID", "pat_receipt_expense")

    print(f"\nProcessing receipt: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return result


def categorize_expense(expense: dict) -> str:
    """Automatically categorize expense based on merchant and items"""
    merchant = expense.get('merchant', '').lower()
    category = expense.get('category', '')

    # Auto-categorization rules
    if category:
        return category

    if any(word in merchant for word in ['hotel', 'marriott', 'hilton', 'airbnb']):
        return 'Lodging'
    elif any(word in merchant for word in ['uber', 'lyft', 'taxi', 'rental']):
        return 'Transportation'
    elif any(word in merchant for word in ['restaurant', 'cafe', 'starbucks']):
        return 'Meals'
    elif any(word in merchant for word in ['office', 'depot', 'staples']):
        return 'Office Supplies'
    else:
        return 'Other'


def save_to_expensify(expense: dict) -> None:
    """Submit expense to Expensify via API"""
    import requests

    EXPENSIFY_API_KEY = os.getenv("EXPENSIFY_API_KEY")

    if not EXPENSIFY_API_KEY:
        print("⚠ Expensify API key not set, skipping integration")
        return

    # Expensify API endpoint
    url = "https://integrations.expensify.com/Integration-Server/ExpensifyIntegrations"

    payload = {
        "type": "create",
        "credentials": {
            "partnerUserID": os.getenv("EXPENSIFY_USER_ID"),
            "partnerUserSecret": EXPENSIFY_API_KEY
        },
        "transaction": {
            "merchant": expense.get('merchant'),
            "amount": expense.get('total_amount'),
            "currency": expense.get('currency', 'USD'),
            "created": expense.get('date'),
            "category": categorize_expense(expense),
            "comment": f"Auto-imported via ImgGo"
        }
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"✓ Expense submitted to Expensify")
    else:
        print(f"✗ Failed to submit to Expensify: {response.text}")


def main():
    print("="*60)
    print("EXPENSE MANAGEMENT - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    # Test with receipt image
    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "receipt1.jpg"

    if not test_image.exists():
        print(f"\n✗ Test image not found: {test_image}")
        sys.exit(1)

    try:
        # Process receipt
        expense = process_receipt(str(test_image))

        # Display results
        print("\n" + "="*60)
        print("EXPENSE DATA")
        print("="*60)
        print(json.dumps(expense, indent=2))

        # Categorize
        category = categorize_expense(expense)
        print(f"\nAuto-categorized as: {category}")

        # Save results
        output_file = "expense_result.json"
        with open(output_file, 'w') as f:
            json.dump(expense, f, indent=2)
        print(f"\n✓ Saved to {output_file}")

        # Optional: Submit to Expensify
        # save_to_expensify(expense)

        print("\n✓ Expense processing completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
