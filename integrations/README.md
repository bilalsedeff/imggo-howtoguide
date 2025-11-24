# Integrations

Connect your image processing workflows to databases, automation platforms, and business tools.

## Databases

Store and query extracted data in production databases:

- [PostgreSQL](./databases/postgresql.md) - Relational data storage with powerful querying
- [Google Sheets](./databases/google-sheets.md) - Spreadsheet automation for teams
- MySQL (coming soon)
- MongoDB (coming soon)
- Airtable (coming soon)

## Automation Platforms

Build no-code/low-code workflows with visual automation tools:

### [n8n](./automation/n8n)

Open-source workflow automation with 350+ integrations:
- Self-hosted or cloud
- Visual workflow builder
- Custom JavaScript functions
- [Setup Guide](./automation/n8n/README.md)

### [Zapier](./automation/zapier)

Connect 5,000+ apps without code:
- Quick setup with templates
- Pre-built triggers and actions
- [Setup Guide](./automation/zapier/README.md)

### [Make](./automation/make)

Advanced automation with complex routing:
- Visual scenario builder
- Advanced data transformation
- [Setup Guide](./automation/make/README.md)

### [Power Automate](./automation/power-automate)

Microsoft ecosystem integration:
- Office 365, SharePoint, Teams
- Enterprise connectors
- [Setup Guide](./automation/power-automate/README.md)

## Integration Patterns

### Webhook Integration

Real-time event-driven automation:

```javascript
// Receive extraction results via webhook
app.post('/webhook/imggo-results', (req, res) => {
  const { job_id, status, result } = req.body;

  if (status === 'succeeded') {
    // Process result and save to database
    await database.save(result);
  }

  res.status(200).send('OK');
});
```

### Polling Integration

Check job status periodically:

```python
import time
import requests

def poll_until_complete(job_id, max_attempts=30):
    for attempt in range(max_attempts):
        response = requests.get(f"https://img-go.com/api/jobs/{job_id}")
        data = response.json()["data"]

        if data["status"] == "succeeded":
            return data["manifest"]
        elif data["status"] == "failed":
            raise Exception(data["error"])

        time.sleep(2)
```

### Database Direct Integration

Store results immediately after extraction:

```python
# Extract from image
result = client.process_image(image_path, pattern_id)

# Save to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute(
    "INSERT INTO invoices (vendor, amount, date) VALUES (%s, %s, %s)",
    (result['vendor'], result['total_amount'], result['invoice_date'])
)
conn.commit()
```

## Need Help?

- See [Use Cases](../use-cases) for complete end-to-end examples
- Check [Examples](../examples) for code samples
- Review [API Reference](../docs/api-reference) for technical details
