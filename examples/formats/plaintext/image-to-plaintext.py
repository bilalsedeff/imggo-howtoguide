"""
Extract Plain Text from Images
Complete example showing how to convert images to human-readable text narratives
"""

import os
import sys
from pathlib import Path

# Add common utilities to path
sys.path.append(str(Path(__file__).parent.parent / "common"))

from imggo_client import ImgGoClient


def example_medical_prescription_to_text():
    """
    Example 1: Medical Prescription → Plain Text Report
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Medical Prescription → Plain Text")
    print("="*60)

    client = ImgGoClient()

    # Pattern for medical prescriptions (Plain Text output)
    # Create at img-go.com/patterns with:
    # - Instructions: "Extract prescription details in narrative format: patient, medications, dosages, instructions"
    # - Output format: Plain Text
    PATTERN_ID = "pat_prescription_text"

    # Using document image as prescription example
    prescription_path = Path(__file__).parent.parent.parent / "test-images" / "document-classification1.png"

    print(f"\nProcessing: {prescription_path.name}")

    try:
        result = client.process_image(
            image_path=str(prescription_path),
            pattern_id=PATTERN_ID
        )

        # Result is plain text string
        print("\nExtracted Prescription:")
        print("-" * 60)
        print(result)
        print("-" * 60)

        # Save to file
        output_file = "prescription_report.txt"
        with open(output_file, 'w') as f:
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_field_service_report():
    """
    Example 2: Service Photo → Field Service Report
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Service Photo → Field Service Report")
    print("="*60)

    client = ImgGoClient()

    # Pattern for field service reports
    # Instructions: "Create a detailed service report describing equipment condition, issues found, and recommendations"
    # Output: Plain Text
    PATTERN_ID = "pat_service_report_text"

    # Using construction image as service photo
    service_path = Path(__file__).parent.parent.parent / "test-images" / "construction1.jpg"

    print(f"\nProcessing: {service_path.name}")

    try:
        result = client.process_image(
            image_path=str(service_path),
            pattern_id=PATTERN_ID
        )

        print("\nService Report:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        # Save with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"service_report_{timestamp}.txt"

        with open(output_file, 'w') as f:
            # Add header
            f.write("FIELD SERVICE REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_clinical_notes():
    """
    Example 3: Medical Image → Clinical Notes
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Medical Document → Clinical Notes")
    print("="*60)

    client = ImgGoClient()

    # Pattern for clinical notes
    # Instructions: "Extract clinical notes in SOAP format (Subjective, Objective, Assessment, Plan)"
    # Output: Plain Text
    PATTERN_ID = "pat_clinical_notes_text"

    medical_path = Path(__file__).parent.parent.parent / "test-images" / "document-classification2.png"

    print(f"\nProcessing: {medical_path.name}")

    try:
        result = client.process_image(
            image_path=str(medical_path),
            pattern_id=PATTERN_ID
        )

        print("\nClinical Notes:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        # Save to medical records format
        output_file = "clinical_notes.txt"
        with open(output_file, 'w') as f:
            f.write("CLINICAL NOTES\n")
            f.write("CONFIDENTIAL - HIPAA PROTECTED\n")
            f.write("=" * 60 + "\n\n")
            f.write(result)
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("End of Clinical Notes\n")

        print(f"\n✓ Saved to {output_file}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_inspection_narrative():
    """
    Example 4: Inspection Photo → Narrative Report
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Inspection Photo → Narrative Summary")
    print("="*60)

    client = ImgGoClient()

    # Pattern for inspection narratives
    # Instructions: "Create a detailed narrative describing the inspection findings, observations, and compliance status"
    # Output: Plain Text
    PATTERN_ID = "pat_inspection_narrative_text"

    inspection_path = Path(__file__).parent.parent.parent / "test-images" / "construction2.jpg"

    print(f"\nProcessing: {inspection_path.name}")

    try:
        result = client.process_image(
            image_path=str(inspection_path),
            pattern_id=PATTERN_ID
        )

        print("\nInspection Report:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        # Save formatted report
        output_file = "inspection_narrative.txt"
        with open(output_file, 'w') as f:
            f.write("INSPECTION NARRATIVE REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(result)

        print(f"\n✓ Saved to {output_file}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_batch_text_extraction():
    """
    Example 5: Batch Process Multiple Images → Combined Text Report
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Batch Processing → Combined Text Report")
    print("="*60)

    client = ImgGoClient()

    # Pattern for general text extraction
    PATTERN_ID = "pat_general_text"

    test_images_dir = Path(__file__).parent.parent.parent / "test-images"
    document_images = list(test_images_dir.glob("document-classification*.png"))[:3]

    print(f"\nProcessing {len(document_images)} documents...")

    all_reports = []

    for img_path in document_images:
        print(f"\n  Processing: {img_path.name}... ", end='')

        try:
            result = client.process_image(
                image_path=str(img_path),
                pattern_id=PATTERN_ID
            )

            all_reports.append({
                'filename': img_path.name,
                'text': result
            })
            print("✓")

        except Exception as e:
            print(f"✗ ({e})")

    # Create combined report
    if all_reports:
        output_file = "combined_report.txt"

        with open(output_file, 'w') as f:
            f.write("COMBINED DOCUMENT REPORT\n")
            f.write("=" * 60 + "\n\n")

            for i, report in enumerate(all_reports, 1):
                f.write(f"DOCUMENT {i}: {report['filename']}\n")
                f.write("-" * 60 + "\n")
                f.write(report['text'])
                f.write("\n\n")

            f.write("=" * 60 + "\n")
            f.write(f"Total documents processed: {len(all_reports)}\n")

        print(f"\n✓ Combined report saved to {output_file}")
        print(f"  Total documents: {len(all_reports)}")


def example_image_to_summary():
    """
    Example 6: Complex Image → Executive Summary
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Complex Image → Executive Summary")
    print("="*60)

    client = ImgGoClient()

    # Pattern for executive summaries
    # Instructions: "Create an executive summary highlighting key points, metrics, and actionable insights"
    # Output: Plain Text
    PATTERN_ID = "pat_executive_summary_text"

    image_path = Path(__file__).parent.parent.parent / "test-images" / "invoice1.jpg"

    print(f"\nProcessing: {image_path.name}")

    try:
        result = client.process_image(
            image_path=str(image_path),
            pattern_id=PATTERN_ID
        )

        print("\nExecutive Summary:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        # Save with executive formatting
        output_file = "executive_summary.txt"
        with open(output_file, 'w') as f:
            f.write("EXECUTIVE SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(result)
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("Classification: Confidential\n")

        print(f"\n✓ Saved to {output_file}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_text_to_email():
    """
    Example 7: Image → Email-Ready Text
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Image → Email-Ready Text")
    print("="*60)

    client = ImgGoClient()

    # Pattern for email formatting
    # Instructions: "Extract information and format as professional email content"
    # Output: Plain Text
    PATTERN_ID = "pat_email_format_text"

    image_path = Path(__file__).parent.parent.parent / "test-images" / "invoice2.jpg"

    print(f"\nProcessing: {image_path.name}")

    try:
        result = client.process_image(
            image_path=str(image_path),
            pattern_id=PATTERN_ID
        )

        print("\nEmail Content:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        # Save as email draft
        output_file = "email_draft.txt"
        with open(output_file, 'w') as f:
            f.write("To: recipient@company.com\n")
            f.write("Subject: Document Processing Result\n")
            f.write("\n")
            f.write(result)
            f.write("\n\nBest regards,\n")
            f.write("Automated Document Processing System\n")

        print(f"\n✓ Email draft saved to {output_file}")

        # Could integrate with email API
        print("\nNext steps:")
        print("  - Review email_draft.txt")
        print("  - Send via SMTP, SendGrid, or email API")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def main():
    """
    Run all plain text extraction examples
    """
    print("\n" + "="*60)
    print("IMAGE TO PLAIN TEXT CONVERSION EXAMPLES")
    print("Using ImgGo API to extract human-readable text from images")
    print("="*60)

    # Check API key
    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY environment variable not set")
        print("  Set it in .env file or export IMGGO_API_KEY=your_key")
        return

    # Run examples
    try:
        example_medical_prescription_to_text()
        example_field_service_report()
        example_clinical_notes()
        example_inspection_narrative()
        example_batch_text_extraction()
        example_image_to_summary()
        example_text_to_email()

        print("\n" + "="*60)
        print("ALL PLAIN TEXT EXAMPLES COMPLETED")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
