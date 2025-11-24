"""
Extract Structured JSON from Images
Complete example showing how to convert any image to structured JSON data
"""

import os
import sys
from pathlib import Path

# Add common utilities to path
sys.path.append(str(Path(__file__).parent.parent / "common"))

from imggo_client import ImgGoClient
import json


def example_invoice_to_json():
    """
    Example 1: Extract invoice data as JSON
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Invoice Image -> JSON")
    print("="*60)

    client = ImgGoClient()

    # Pattern for invoice extraction (JSON output)
    # Create this pattern at img-go.com/patterns with:
    # - Instructions: "Extract vendor name, invoice number, date, line items, and total amount"
    # - Output format: JSON
    PATTERN_ID = "pat_invoice_json"

    invoice_path = Path(__file__).parent.parent.parent / "test-images" / "invoice1.jpg"

    print(f"\nProcessing: {invoice_path.name}")

    try:
        result = client.process_image(
            image_path=str(invoice_path),
            pattern_id=PATTERN_ID
        )

        print("\nExtracted JSON:")
        print(json.dumps(result, indent=2))

        # Save to file
        output_file = "invoice_output.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\nV Saved to {output_file}")

    except Exception as e:
        print(f"\nX Error: {e}")


def example_document_classification_to_json():
    """
    Example 2: Classify documents and extract metadata as JSON
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Document Classification -> JSON")
    print("="*60)

    client = ImgGoClient()

    # Pattern for document classification
    # Instructions: "Classify document type (invoice, receipt, contract, etc.) and extract key metadata"
    PATTERN_ID = "pat_doc_classify_json"

    doc_path = Path(__file__).parent.parent.parent / "test-images" / "document-classification1.png"

    print(f"\nProcessing: {doc_path.name}")

    try:
        result = client.process_image(
            image_path=str(doc_path),
            pattern_id=PATTERN_ID
        )

        print("\nClassification Result:")
        print(json.dumps(result, indent=2))

        # Example: Route based on document type
        if isinstance(result, str):
            result = json.loads(result)

        doc_type = result.get('document_type', 'unknown')
        print(f"\n-> Document Type: {doc_type}")

        if doc_type == 'invoice':
            print("  Routing to: Accounts Payable")
        elif doc_type == 'contract':
            print("  Routing to: Legal Department")
        elif doc_type == 'receipt':
            print("  Routing to: Expense Management")

    except Exception as e:
        print(f"\nX Error: {e}")


def example_product_catalog_to_json():
    """
    Example 3: Extract product details from images as JSON
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Product Image -> JSON Catalog Entry")
    print("="*60)

    client = ImgGoClient()

    # Pattern for product extraction
    # Instructions: "Extract product name, brand, price, description, and visible features"
    PATTERN_ID = "pat_product_json"

    # Using URL processing for products
    product_url = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"

    print(f"\nProcessing URL: {product_url}")

    try:
        result = client.process_image_url(
            image_url=product_url,
            pattern_id=PATTERN_ID
        )

        print("\nProduct Data:")
        print(json.dumps(result, indent=2))

        # Save as product catalog entry
        output_file = "product_catalog_entry.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\nV Saved to {output_file}")

    except Exception as e:
        print(f"\nX Error: {e}")


def example_batch_processing():
    """
    Example 4: Batch process multiple images to JSON
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Processing -> Multiple JSON Files")
    print("="*60)

    client = ImgGoClient()
    PATTERN_ID = "pat_invoice_json"

    test_images_dir = Path(__file__).parent.parent.parent / "test-images"
    invoice_images = list(test_images_dir.glob("invoice*.jpg"))[:3]  # First 3 invoices

    print(f"\nProcessing {len(invoice_images)} invoices...")

    results = []

    for img_path in invoice_images:
        print(f"\n  Processing: {img_path.name}... ", end='')

        try:
            result = client.process_image(
                image_path=str(img_path),
                pattern_id=PATTERN_ID
            )

            results.append({
                "filename": img_path.name,
                "data": result,
                "status": "success"
            })

            print("V")

        except Exception as e:
            results.append({
                "filename": img_path.name,
                "error": str(e),
                "status": "failed"
            })
            print(f"X ({e})")

    # Save batch results
    batch_output = "batch_results.json"
    with open(batch_output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nV Batch results saved to {batch_output}")

    # Summary
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"\nSummary: {successful}/{len(results)} processed successfully")


def main():
    """
    Run all JSON extraction examples
    """
    print("\n" + "="*60)
    print("IMAGE TO JSON CONVERSION EXAMPLES")
    print("Using ImgGo API to extract structured JSON from images")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\nX Error: IMGGO_API_KEY environment variable not set")
        print("  Set it in .env file or export IMGGO_API_KEY=your_key")
        return

    # Run examples
    try:
        example_invoice_to_json()
        example_document_classification_to_json()
        example_product_catalog_to_json()
        example_batch_processing()

        print("\n" + "="*60)
        print("ALL EXAMPLES COMPLETED")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nX Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
