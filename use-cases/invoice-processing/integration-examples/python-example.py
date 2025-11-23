"""
Invoice Processing - Python Integration Example
"""
import os, sys, json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))
from imggo_client import ImgGoClient

def main():
    print("INVOICE PROCESSING - PYTHON EXAMPLE")
    if not os.getenv("IMGGO_API_KEY"):
        print("✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)
    
    client = ImgGoClient()
    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "invoice1.jpg"
    
    if not test_image.exists():
        print(f"⚠ Test image not found: {test_image}")
        sys.exit(1)
    
    try:
        result = client.process_image(str(test_image), os.getenv("INVOICE_PATTERN_ID", "pat_invoice_json"))
        invoice = json.loads(result) if isinstance(result, str) else result
        
        print(f"\nInvoice: {invoice.get('invoice_number')}")
        print(f"Vendor: {invoice.get('vendor')}")
        print(f"Total: ${invoice.get('total_amount', 0)}")
        print("\n✓ Invoice processing completed!")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
