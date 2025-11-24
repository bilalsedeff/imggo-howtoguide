# Plain Text Output Examples

Complete working examples for converting images to human-readable text using ImgGo API.

## What is Plain Text Output?

Plain Text output is ideal for:
- Human-readable reports
- Narrative summaries
- Email content
- Document descriptions
- Medical notes (SOAP format)
- Service reports
- Executive summaries

## Examples Included

### 1. Medical Prescription to Text
Extract prescription information as readable narrative.

**Use case**: Clinical documentation, patient records

**Output example**:
```
PRESCRIPTION

Patient: John Doe
Date: January 22, 2025

Medications:
- Lisinopril 10mg, once daily, for blood pressure control
- Metformin 500mg, twice daily with meals, for diabetes management

Instructions: Take medications as prescribed. Follow up in 30 days.

Dr. Jane Smith, MD
License #12345
```

### 2. Field Service Report
Convert service photos to detailed reports.

**Use case**: Field technician documentation

**Output example**:
```
FIELD SERVICE REPORT

Equipment: HVAC Unit #A-123
Location: Building 5, Roof Access
Technician: Mike Johnson

Findings:
The HVAC unit shows signs of normal wear. Air filters are dirty
and require replacement. Refrigerant levels are adequate.
Electrical connections are secure.

Actions Taken:
- Replaced air filters
- Cleaned condenser coils
- Tested all safety switches

Recommendations:
Schedule next maintenance in 90 days. Monitor for unusual noises.
```

### 3. Clinical Notes (SOAP Format)
Extract medical documentation in structured narrative format.

**Use case**: Healthcare documentation, EHR integration

**Output example**:
```
CLINICAL NOTES

Subjective:
Patient reports persistent headache for 3 days.

Objective:
BP 120/80, HR 72, Temp 98.6°F. No focal neurological deficits.

Assessment:
Tension headache, likely stress-related.

Plan:
OTC pain relief as needed. Follow up if symptoms worsen.
```

### 4. Inspection Narrative
Generate detailed inspection reports.

**Use case**: Property inspections, quality control

**Output example**:
```
INSPECTION NARRATIVE

The property inspection conducted on January 22, 2025 revealed
the following conditions:

The foundation appears structurally sound with no visible cracks
or settling. The roof is in good condition with approximately 10
years of useful life remaining. Minor water staining was observed
in the northwest corner of the basement, indicating possible
drainage issues that should be monitored.

Overall Assessment: Property is in good condition with routine
maintenance recommended.
```

### 5. Batch Text Extraction
Process multiple documents into combined reports.

**Use case**: Document summarization, reporting

### 6. Image to Executive Summary
Generate high-level summaries from complex images.

**Use case**: Business reporting, presentations

### 7. Email-Ready Text
Format extracted data as email content.

**Use case**: Automated notifications, reporting

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
python image-to-plaintext.py
```

### Process Single Image

```python
from imggo_client import ImgGoClient

client = ImgGoClient()
text_result = client.process_image(
    image_path="report.jpg",
    pattern_id="pat_report_text"
)

# text_result is a plain text string
print(text_result)

# Save to file
with open("report.txt", "w") as f:
    f.write(text_result)
```

## Pattern Setup

Create Plain Text patterns at [img-go.com/patterns](https://img-go.com/patterns):

1. Click "New Pattern"
2. Select **Plain Text** as output format
3. Define narrative structure in instructions
4. Publish and copy Pattern ID

**Example instructions**:
```
Create a field service report with this structure:

FIELD SERVICE REPORT

Equipment: [Equipment type and ID]
Location: [Physical location]
Technician: [Technician name]

Findings:
[Detailed narrative of observations, issues, and equipment condition]

Actions Taken:
[List of maintenance or repair actions performed]

Recommendations:
[Next steps and future recommendations]

Write in professional, clear language suitable for customer review.
```

## Integration Examples

### Send via Email (SMTP)

```python
import smtplib
from email.mime.text import MIMEText

text_result = client.process_image("service.jpg", "pat_service_report")

# Create email
msg = MIMEText(text_result)
msg["Subject"] = "Service Report - Equipment A-123"
msg["From"] = "reports@company.com"
msg["To"] = "customer@example.com"

# Send
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login("your_email", "your_password")
    server.send_message(msg)

print("✓ Report sent via email")
```

### Send via SendGrid

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

text_result = client.process_image("report.jpg", "pat_report")

message = Mail(
    from_email="reports@company.com",
    to_emails="customer@example.com",
    subject="Automated Report",
    plain_text_content=text_result
)

sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
response = sg.send(message)

print(f"✓ Email sent: {response.status_code}")
```

### Save to Google Docs

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

text_result = client.process_image("notes.jpg", "pat_notes")

creds = service_account.Credentials.from_service_account_file("creds.json")
service = build("docs", "v1", credentials=creds)

# Create new document
doc = service.documents().create(body={"title": "Extracted Notes"}).execute()
doc_id = doc["documentId"]

# Insert text
requests = [{
    "insertText": {
        "location": {"index": 1},
        "text": text_result
    }
}]

service.documents().batchUpdate(
    documentId=doc_id,
    body={"requests": requests}
).execute()

print(f"✓ Saved to Google Docs: {doc_id}")
```

### Post to Slack

```python
import requests

text_result = client.process_image("update.jpg", "pat_update")

# Post to Slack
slack_webhook = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

requests.post(slack_webhook, json={
    "text": "Daily Report",
    "blocks": [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"```{text_result}```"
        }
    }]
})

print("✓ Posted to Slack")
```

### Save to Notion

```python
import requests

text_result = client.process_image("notes.jpg", "pat_notes")

# Create Notion page
notion_api = "https://api.notion.com/v1/pages"
headers = {
    "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

data = {
    "parent": {"database_id": "your_database_id"},
    "properties": {
        "Title": {"title": [{"text": {"content": "Extracted Notes"}}]}
    },
    "children": [{
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text_result}}]
        }
    }]
}

response = requests.post(notion_api, headers=headers, json=data)
print(f"✓ Saved to Notion: {response.json()['id']}")
```

## Common Use Cases

- **Medical Documentation**: Prescriptions, clinical notes, discharge summaries
- **Field Service**: Technician reports, maintenance logs
- **Inspection Reports**: Property inspections, safety audits
- **Executive Summaries**: High-level business reports
- **Email Automation**: Automated notifications from images
- **Customer Communication**: Service updates, status reports
- **Legal Documents**: Case notes, evidence descriptions
- **Research Notes**: Lab observations, field notes
- **Quality Control**: Defect descriptions, compliance notes
- **Construction**: Daily logs, progress narratives

## Formatting Options

### Add Headers and Footers

```python
from datetime import datetime

text_result = client.process_image("report.jpg", "pat_report")

# Add formatting
formatted = f"""
{'='*60}
AUTOMATED REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

{text_result}

{'='*60}
End of Report
"""

with open("formatted_report.txt", "w") as f:
    f.write(formatted)
```

### Convert to Markdown

```python
text_result = client.process_image("notes.jpg", "pat_notes")

# Convert sections to markdown
lines = text_result.split("\n")
markdown = []

for line in lines:
    if line.isupper() and len(line) < 50:  # Likely a header
        markdown.append(f"## {line.title()}\n")
    elif line.startswith("- "):  # List item
        markdown.append(line)
    else:
        markdown.append(line)

with open("notes.md", "w") as f:
    f.write("\n".join(markdown))
```

### Word Count and Summary

```python
text_result = client.process_image("document.jpg", "pat_document")

# Analyze text
words = len(text_result.split())
lines = len(text_result.split("\n"))
chars = len(text_result)

print(f"Word count: {words}")
print(f"Lines: {lines}")
print(f"Characters: {chars}")

# Extract first paragraph as summary
summary = text_result.split("\n\n")[0]
print(f"\nSummary:\n{summary}")
```

## Error Handling

```python
try:
    text_result = client.process_image("document.jpg", "pat_text")

    # Validate text content
    if len(text_result.strip()) < 10:
        raise ValueError("Extracted text is too short")

    # Check for expected keywords
    required_words = ["patient", "prescription"]
    if not any(word in text_result.lower() for word in required_words):
        print("⚠ Warning: Expected keywords not found")

    # Save result
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(text_result)

except Exception as e:
    print(f"Error processing text: {e}")
```

## Best Practices

1. **Define clear structure**: Specify headings, sections in instructions
2. **Professional tone**: Request appropriate language style
3. **Consistent formatting**: Use standard formats (SOAP, etc.)
4. **UTF-8 encoding**: Handle special characters properly
5. **Validation**: Check for minimum length, required keywords

## Text Processing

### Remove Extra Whitespace

```python
import re

text_result = client.process_image("messy.jpg", "pat_text")

# Clean up whitespace
cleaned = re.sub(r'\n\n+', '\n\n', text_result)  # Max 2 newlines
cleaned = re.sub(r' +', ' ', cleaned)             # Single spaces
cleaned = cleaned.strip()                         # Trim edges

print(cleaned)
```

### Extract Sections

```python
import re

text_result = client.process_image("report.jpg", "pat_report")

# Extract sections by headers
sections = {}
current_section = "intro"
sections[current_section] = []

for line in text_result.split("\n"):
    if line.isupper() and line.strip():
        current_section = line.strip()
        sections[current_section] = []
    else:
        sections[current_section].append(line)

# Access specific section
findings = "\n".join(sections.get("FINDINGS", []))
print(findings)
```

## Batch Processing

```python
import glob

all_reports = []

for image_path in glob.glob("images/*.jpg"):
    text_result = client.process_image(image_path, "pat_report")

    all_reports.append({
        "filename": image_path,
        "text": text_result
    })

# Create combined document
with open("combined_reports.txt", "w") as f:
    for i, report in enumerate(all_reports, 1):
        f.write(f"\n{'='*60}\n")
        f.write(f"REPORT {i}: {report['filename']}\n")
        f.write(f"{'='*60}\n\n")
        f.write(report['text'])
        f.write("\n\n")

print(f"✓ Combined {len(all_reports)} reports")
```

## Support

- [ImgGo API Documentation](https://img-go.com/docs)
- [Plain Text Format Guide](https://img-go.com/docs/output-formats/plaintext)
- Email: support@img-go.com
