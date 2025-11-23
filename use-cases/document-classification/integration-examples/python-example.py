"""
Document Classification - Python Example
Automatically classify and route documents
"""

import os
import sys
import json
from pathlib import Path

# Add common client to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def classify_document(image_path: str) -> dict:
    """
    Classify a document image

    Args:
        image_path: Path to document image

    Returns:
        Classification result with document type and confidence
    """
    client = ImgGoClient()

    # Pattern for document classification
    # Create at img-go.com/patterns with:
    # - Instructions: "Classify document type: invoice, receipt, contract, form, letter, ID card, or other"
    # - Output format: JSON
    PATTERN_ID = os.getenv("DOC_CLASSIFICATION_PATTERN_ID", "pat_doc_classification")

    print(f"\nClassifying document: {Path(image_path).name}")

    try:
        result = client.process_image(
            image_path=image_path,
            pattern_id=PATTERN_ID
        )

        return result

    except Exception as e:
        print(f"Error classifying document: {e}")
        raise


def route_document(classification: dict, original_path: str) -> str:
    """
    Route document based on classification

    Args:
        classification: Classification result
        original_path: Original file path

    Returns:
        Destination path for the document
    """
    doc_type = classification.get('document_type', 'unknown').lower()
    confidence = classification.get('confidence', 0)

    # Define routing rules
    routing_map = {
        'invoice': 'invoices/pending',
        'receipt': 'receipts/pending',
        'contract': 'contracts/pending',
        'form': 'forms/pending',
        'letter': 'correspondence/pending',
        'id_card': 'identity/pending',
        'other': 'uncategorized'
    }

    # Low confidence items go to manual review
    if confidence < 0.85:
        destination = 'manual_review'
    else:
        destination = routing_map.get(doc_type, 'uncategorized')

    return destination


def move_document(source_path: str, destination_folder: str) -> str:
    """
    Move document to classified folder

    Args:
        source_path: Source file path
        destination_folder: Destination folder name

    Returns:
        New file path
    """
    import shutil

    # Create destination directory if it doesn't exist
    base_dir = Path(source_path).parent.parent / "classified"
    dest_dir = base_dir / destination_folder
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Move file
    filename = Path(source_path).name
    dest_path = dest_dir / filename
    shutil.move(source_path, dest_path)

    print(f"✓ Moved to: {dest_path}")

    return str(dest_path)


def trigger_downstream_workflow(classification: dict, file_path: str) -> None:
    """
    Trigger downstream workflows based on document type

    Args:
        classification: Classification result
        file_path: Path to classified document
    """
    doc_type = classification.get('document_type', 'unknown').lower()

    if doc_type == 'invoice':
        print("\n→ Triggering invoice processing workflow...")
        # Call invoice processing API
        # process_invoice(file_path)

    elif doc_type == 'receipt':
        print("\n→ Triggering expense management workflow...")
        # Call expense processing API
        # process_expense(file_path)

    elif doc_type == 'contract':
        print("\n→ Sending to legal review...")
        # Send notification to legal team
        # notify_legal_team(file_path)

    elif doc_type == 'id_card':
        print("\n→ Triggering KYC verification...")
        # Call KYC verification workflow
        # verify_identity(file_path)


def save_classification_log(classification: dict, file_path: str) -> None:
    """
    Log classification result to database

    This is a placeholder - replace with your actual database logic
    """
    import psycopg2
    from datetime import datetime

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "document_management"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO classification_log (
            file_path,
            document_type,
            confidence,
            classification_data,
            classified_at
        ) VALUES (%s, %s, %s, %s, %s)
    """, (
        file_path,
        classification.get('document_type'),
        classification.get('confidence'),
        json.dumps(classification),
        datetime.now()
    ))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✓ Classification logged to database")


def main():
    """Run document classification example"""

    print("="*60)
    print("DOCUMENT CLASSIFICATION - PYTHON EXAMPLE")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY environment variable not set")
        print("  Set it in .env file or export IMGGO_API_KEY=your_key")
        sys.exit(1)

    # Example document to classify
    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "document-classification1.png"

    if not test_image.exists():
        print(f"\n✗ Error: Test image not found: {test_image}")
        print("  Please ensure test images are available in test-images folder")
        sys.exit(1)

    try:
        # Step 1: Classify document
        classification = classify_document(str(test_image))

        # Display results
        print("\n" + "="*60)
        print("CLASSIFICATION RESULT")
        print("="*60)
        print(json.dumps(classification, indent=2))

        doc_type = classification.get('document_type', 'unknown')
        confidence = classification.get('confidence', 0)

        print(f"\nDocument Type: {doc_type}")
        print(f"Confidence: {confidence:.2%}")

        if confidence < 0.85:
            print("⚠ Low confidence - routing to manual review")
        else:
            print("✓ High confidence - routing automatically")

        # Step 2: Route document
        destination = route_document(classification, str(test_image))
        print(f"\nRouting to: {destination}")

        # Step 3: Save results
        output_file = "classification_result.json"
        with open(output_file, 'w') as f:
            json.dump(classification, f, indent=2)
        print(f"\n✓ Results saved to {output_file}")

        # Step 4: Optional - Move file and trigger workflows
        # new_path = move_document(str(test_image), destination)
        # trigger_downstream_workflow(classification, new_path)
        # save_classification_log(classification, new_path)

        print("\n✓ Document classification completed successfully!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
