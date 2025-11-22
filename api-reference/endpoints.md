# API Endpoints Reference

Complete reference for all ImgGo API endpoints, request/response formats, and usage examples.

## Base URL

```
https://img-go.com/api
```

All endpoints use HTTPS. HTTP requests are automatically redirected.

## Authentication

All requests require a Bearer token in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

See [Authentication Guide](../getting-started/authentication.md) for details.

## Endpoints Overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/patterns` | GET | List all patterns |
| `/patterns` | POST | Create new pattern |
| `/patterns/{id}` | GET | Get pattern details |
| `/patterns/{id}` | PATCH | Update pattern |
| `/patterns/{id}` | DELETE | Delete pattern |
| `/patterns/{id}/ingest` | POST | Process image with pattern |
| `/jobs/{id}` | GET | Get job status and results |
| `/jobs` | GET | List recent jobs |
| `/webhooks` | GET | List webhooks |
| `/webhooks` | POST | Create webhook |
| `/webhooks/{id}` | DELETE | Delete webhook |

---

## Patterns

### List All Patterns

Retrieve all patterns for your account.

**Endpoint**: `GET /patterns`

**Parameters**:
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 20, max: 100)
- `status` (optional): Filter by status (`active`, `draft`, `archived`)

**Request**:
```bash
curl -X GET "https://img-go.com/api/patterns?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "pattern_id": "pat_2gYc3kZ8mN",
        "name": "Invoice Data Extractor",
        "output_format": "json",
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T14:22:00Z",
        "request_count": 1247
      },
      {
        "pattern_id": "pat_9xKp1mW4vQ",
        "name": "Receipt Parser",
        "output_format": "json",
        "status": "active",
        "created_at": "2024-01-18T09:15:00Z",
        "updated_at": "2024-01-18T09:15:00Z",
        "request_count": 342
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 3,
      "total_count": 47
    }
  }
}
```

### Create Pattern

Create a new pattern for image data extraction.

**Endpoint**: `POST /patterns`

**Request Body**:
```json
{
  "name": "Invoice Data Extractor",
  "output_format": "json",
  "instructions": "Extract vendor name, invoice number, date, line items, and total amount",
  "schema": {
    "vendor_name": "string",
    "invoice_number": "string",
    "invoice_date": "date",
    "line_items": [
      {
        "description": "string",
        "amount": "number"
      }
    ],
    "total_amount": "number"
  },
  "webhook_url": "https://your-app.com/webhooks/imggo",
  "metadata": {
    "environment": "production",
    "version": "1.0"
  }
}
```

**Request**:
```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Invoice Data Extractor",
    "output_format": "json",
    "instructions": "Extract vendor name, invoice number, date, and total amount",
    "schema": {
      "vendor_name": "string",
      "invoice_number": "string",
      "invoice_date": "date",
      "total_amount": "number"
    }
  }'
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "pattern_id": "pat_2gYc3kZ8mN",
    "name": "Invoice Data Extractor",
    "output_format": "json",
    "status": "active",
    "endpoint": "https://img-go.com/api/patterns/pat_2gYc3kZ8mN/ingest",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Get Pattern Details

Retrieve details for a specific pattern.

**Endpoint**: `GET /patterns/{pattern_id}`

**Request**:
```bash
curl -X GET https://img-go.com/api/patterns/pat_2gYc3kZ8mN \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "pattern_id": "pat_2gYc3kZ8mN",
    "name": "Invoice Data Extractor",
    "output_format": "json",
    "instructions": "Extract vendor name, invoice number, date, and total amount",
    "schema": {
      "vendor_name": "string",
      "invoice_number": "string",
      "invoice_date": "date",
      "total_amount": "number"
    },
    "status": "active",
    "webhook_url": "https://your-app.com/webhooks/imggo",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:22:00Z",
    "statistics": {
      "total_requests": 1247,
      "success_rate": 98.3,
      "avg_processing_time_ms": 4200
    }
  }
}
```

### Update Pattern

Update an existing pattern's instructions or schema.

**Endpoint**: `PATCH /patterns/{pattern_id}`

**Request Body**:
```json
{
  "instructions": "Updated instructions",
  "schema": {...},
  "webhook_url": "https://new-webhook.com/hook"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "pattern_id": "pat_2gYc3kZ8mN",
    "updated_at": "2024-01-21T16:45:00Z"
  }
}
```

### Delete Pattern

Delete a pattern. Warning: This breaks all integrations using this pattern.

**Endpoint**: `DELETE /patterns/{pattern_id}`

**Request**:
```bash
curl -X DELETE https://img-go.com/api/patterns/pat_2gYc3kZ8mN \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Pattern deleted successfully"
}
```

---

## Image Processing

### Process Image (Ingest)

Submit an image for processing with a specific pattern.

**Endpoint**: `POST /patterns/{pattern_id}/ingest`

**Request Methods**:

#### Method 1: Image URL

```bash
curl -X POST https://img-go.com/api/patterns/pat_2gYc3kZ8mN/ingest \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-request-id-123" \
  -d '{
    "image_url": "https://example.com/invoice.jpg"
  }'
```

#### Method 2: Base64 Encoded Image

```bash
curl -X POST https://img-go.com/api/patterns/pat_2gYc3kZ8mN/ingest \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgA..."
  }'
```

#### Method 3: Multipart Form Upload

```bash
curl -X POST https://img-go.com/api/patterns/pat_2gYc3kZ8mN/ingest \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@/path/to/invoice.jpg"
```

**Request Parameters**:
- `image_url` (string): Public URL to image (supports JPG, PNG, PDF, WEBP)
- `image_base64` (string): Base64-encoded image data
- `file` (file): Multipart file upload
- `metadata` (object, optional): Custom metadata to attach to job
- `priority` (string, optional): `normal` or `high` (high priority costs 2x)

**Response** (202 Accepted):
```json
{
  "success": true,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued",
    "message": "Job queued for background processing",
    "approach": "queued",
    "estimated_completion_time": "2024-01-21T10:32:30Z"
  }
}
```

**Response** (200 OK - Synchronous, for simple patterns):
```json
{
  "success": true,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "result": {
      "vendor_name": "Acme Corporation",
      "invoice_number": "INV-2024-001",
      "invoice_date": "2024-01-15",
      "total_amount": 1942.92
    },
    "confidence": 0.97,
    "processing_time_ms": 3420
  }
}
```

---

## Jobs

### Get Job Status

Retrieve the status and result of a processing job.

**Endpoint**: `GET /jobs/{job_id}`

**Request**:
```bash
curl -X GET https://img-go.com/api/jobs/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response** (Job Queued):
```json
{
  "success": true,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "pattern_id": "pat_2gYc3kZ8mN",
    "status": "queued",
    "created_at": "2024-01-21T10:30:00Z"
  }
}
```

**Response** (Job Processing):
```json
{
  "success": true,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "pattern_id": "pat_2gYc3kZ8mN",
    "status": "processing",
    "progress": 65,
    "created_at": "2024-01-21T10:30:00Z",
    "started_at": "2024-01-21T10:30:15Z"
  }
}
```

**Response** (Job Completed):
```json
{
  "success": true,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "pattern_id": "pat_2gYc3kZ8mN",
    "status": "completed",
    "result": {
      "vendor_name": "Acme Corporation",
      "invoice_number": "INV-2024-001",
      "invoice_date": "2024-01-15",
      "total_amount": 1942.92
    },
    "confidence": 0.97,
    "processing_time_ms": 3420,
    "created_at": "2024-01-21T10:30:00Z",
    "completed_at": "2024-01-21T10:30:18Z"
  }
}
```

**Response** (Job Failed):
```json
{
  "success": false,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "pattern_id": "pat_2gYc3kZ8mN",
    "status": "failed",
    "error": {
      "code": "invalid_image",
      "message": "Image URL is not accessible or format is unsupported"
    },
    "created_at": "2024-01-21T10:30:00Z",
    "failed_at": "2024-01-21T10:30:05Z"
  }
}
```

### List Jobs

List recent processing jobs.

**Endpoint**: `GET /jobs`

**Parameters**:
- `page` (optional): Page number
- `limit` (optional): Results per page (max: 100)
- `status` (optional): Filter by status (`queued`, `processing`, `completed`, `failed`)
- `pattern_id` (optional): Filter by pattern

**Request**:
```bash
curl -X GET "https://img-go.com/api/jobs?status=completed&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "pattern_id": "pat_2gYc3kZ8mN",
        "status": "completed",
        "created_at": "2024-01-21T10:30:00Z",
        "completed_at": "2024-01-21T10:30:18Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_count": 89
    }
  }
}
```

---

## Webhooks

### List Webhooks

Retrieve all configured webhooks.

**Endpoint**: `GET /webhooks`

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "webhooks": [
      {
        "webhook_id": "wh_abc123",
        "url": "https://your-app.com/webhooks/imggo",
        "events": ["job.completed", "job.failed"],
        "active": true,
        "created_at": "2024-01-15T10:00:00Z"
      }
    ]
  }
}
```

### Create Webhook

Configure a webhook endpoint to receive real-time job notifications.

**Endpoint**: `POST /webhooks`

**Request Body**:
```json
{
  "url": "https://your-app.com/webhooks/imggo",
  "events": ["job.completed", "job.failed"],
  "secret": "your_webhook_secret_for_signature_verification"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "webhook_id": "wh_abc123",
    "url": "https://your-app.com/webhooks/imggo",
    "events": ["job.completed", "job.failed"],
    "secret": "your_webhook_secret_for_signature_verification",
    "active": true
  }
}
```

### Delete Webhook

Remove a webhook configuration.

**Endpoint**: `DELETE /webhooks/{webhook_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Webhook deleted successfully"
}
```

---

## Response Headers

All API responses include standard headers:

```
Content-Type: application/json
X-Request-ID: req_abc123xyz
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1640995200
```

## Idempotency

Use the `Idempotency-Key` header to safely retry requests:

```bash
-H "Idempotency-Key: unique-request-id-123"
```

If the same key is sent within 24 hours, the original response is returned without reprocessing.

## Next Steps

- Review [Error Handling](./error-handling.md) for error codes and solutions
- Learn about [Rate Limits](./rate-limits.md) and quotas
- Set up [Webhooks](./webhooks.md) for production workflows
