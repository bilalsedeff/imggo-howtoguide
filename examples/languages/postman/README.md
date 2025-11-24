# Postman Collection

Interactive API exploration and testing using Postman.

## Overview

This Postman collection provides pre-configured requests for all ImgGo API endpoints with:
- Automatic variable management
- Request examples
- Response validation
- Test scripts
- Documentation

## Installation

### Option 1: Import File

1. Download [`ImgGo-API.postman_collection.json`](./ImgGo-API.postman_collection.json)
2. Open Postman
3. Click **Import** button (top left)
4. Select the downloaded JSON file
5. Click **Import**

### Option 2: Import URL (if hosted)

```
https://raw.githubusercontent.com/your-org/imggo-guide/main/examples/languages/postman/ImgGo-API.postman_collection.json
```

## Setup

After importing the collection:

### 1. Set Your API Key

1. Click on the **ImgGo API** collection
2. Go to the **Variables** tab
3. Set `IMGGO_API_KEY` to your API key
4. Click **Save**

![Set API Key](https://via.placeholder.com/800x200?text=Set+API+Key+in+Variables+Tab)

### 2. Set Your Pattern ID

1. In the **Variables** tab
2. Set `pattern_id` to your pattern ID (e.g., `pat_abc123`)
3. Click **Save**

### 3. Optional: Change Base URL

The default base URL is `https://img-go.com/api`. To change it:

1. In the **Variables** tab
2. Modify `IMGGO_BASE_URL`
3. Click **Save**

## Collection Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `IMGGO_API_KEY` | Your API key (required) | `imggo_key_abc123...` |
| `IMGGO_BASE_URL` | API base URL | `https://img-go.com/api` |
| `pattern_id` | Pattern ID for extraction | `pat_invoice_abc123` |
| `job_id` | Auto-set after upload | `job_xyz789` |
| `idempotency_key` | Auto-generated | `request-1234567890-abc` |

## Available Requests

### 1. Upload Image (File)

**Purpose:** Upload a local image file for processing.

**Steps:**
1. Click on **1. Upload Image (File)**
2. Go to **Body** tab
3. Click **Select File** next to the `image` field
4. Choose your image file
5. Click **Send**
6. The `job_id` is automatically saved to collection variables

**Response:**
```json
{
  "data": {
    "job_id": "job_abc123xyz"
  }
}
```

---

### 2. Upload Image (URL)

**Purpose:** Process an image from a public URL.

**Steps:**
1. Click on **2. Upload Image (URL)**
2. Go to **Body** tab
3. Update the `image_url` field with your image URL
4. Click **Send**
5. The `job_id` is automatically saved

**Request Body:**
```json
{
  "image_url": "https://example.com/invoice.jpg"
}
```

---

### 3. Get Job Status

**Purpose:** Check processing status and get results.

**Steps:**
1. After uploading an image, click on **3. Get Job Status**
2. Click **Send**
3. Check the **Console** (bottom panel) for status messages
4. Re-run until status is `succeeded` or `failed`

**Status Values:**
- `pending` - Job is queued
- `processing` - Job is being processed
- `succeeded` - Completed successfully
- `failed` - Processing failed

**Response (Succeeded):**
```json
{
  "data": {
    "status": "succeeded",
    "manifest": {
      "field1": "value1",
      "field2": "value2"
    }
  }
}
```

---

### 4. Upload with Idempotency Key

**Purpose:** Upload with duplicate prevention.

**Steps:**
1. Click on **4. Upload with Idempotency Key**
2. Select an image file
3. Click **Send**
4. The idempotency key is auto-generated in Pre-request Script

**Use Case:**
- Production environments
- Retry logic
- Preventing duplicate jobs

**How it works:**
- If you retry with the same key, you get the same `job_id`
- No duplicate processing occurs

---

### 5. List Patterns (if supported)

**Purpose:** List all available patterns (if endpoint exists).

**Note:** This endpoint may not be available in all API versions.

---

## Automated Testing

Each request includes test scripts that:

1. **Validate response status codes**
2. **Check for required fields**
3. **Extract and save variables**
4. **Log useful information to console**

### View Test Results

After sending a request:

1. Click on the **Test Results** tab (bottom panel)
2. See passed/failed assertions
3. Check the **Console** for logged data

### Example Test Script

```javascript
// Save job_id to collection variable
const response = pm.response.json();
pm.collectionVariables.set('job_id', response.data.job_id);

// Assertions
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});

pm.test('Response has job_id', function () {
    pm.expect(response.data).to.have.property('job_id');
});
```

## Complete Workflow Example

### Step 1: Upload Image
1. Open **1. Upload Image (File)**
2. Select an image file
3. Click **Send**
4. Note the `job_id` in the response

### Step 2: Poll for Results
1. Open **3. Get Job Status**
2. Click **Send** (the `job_id` is auto-set)
3. Check status in response
4. If status is `processing`, wait 2-3 seconds and click **Send** again
5. Repeat until status is `succeeded`

### Step 3: Extract Data
1. When status is `succeeded`, look for the `manifest` or `result` field
2. This contains your extracted structured data

## Advanced Usage

### Environment Variables

For managing multiple environments (dev, staging, production):

1. Create a new **Environment** in Postman
2. Add variables: `IMGGO_API_KEY`, `IMGGO_BASE_URL`, `pattern_id`
3. Switch between environments using the dropdown (top right)

**Example Environments:**

**Development:**
```
IMGGO_API_KEY: dev_key_123
IMGGO_BASE_URL: https://dev-api.img-go.com/api
pattern_id: pat_dev_abc
```

**Production:**
```
IMGGO_API_KEY: prod_key_xyz
IMGGO_BASE_URL: https://img-go.com/api
pattern_id: pat_prod_xyz
```

### Collection Runner

Process multiple images automatically:

1. Click **...** on the collection
2. Select **Run collection**
3. Select requests to run
4. Set iterations (number of times to run)
5. Click **Run ImgGo API**

### Newman (CLI Runner)

Run collection from command line:

```bash
# Install Newman
npm install -g newman

# Run collection
newman run ImgGo-API.postman_collection.json \
  --env-var "IMGGO_API_KEY=your_key_here" \
  --env-var "pattern_id=pat_abc123"
```

**Use cases:**
- CI/CD pipeline integration
- Automated testing
- Scheduled jobs

### Pre-request Scripts

Automatically run code before each request:

**Collection-level Pre-request Script:**
```javascript
// Add timestamp to all requests
pm.collectionVariables.set('timestamp', Date.now());

// Log request details
console.log('Making request to:', pm.request.url);
```

**Request-level Pre-request Script:**
```javascript
// Generate unique idempotency key
const key = 'request-' + Date.now() + '-' + Math.random();
pm.collectionVariables.set('idempotency_key', key);
```

## Troubleshooting

### Issue: "Could not get any response"

**Possible Causes:**
- Invalid API key
- Incorrect base URL
- Network/firewall issues

**Solution:**
1. Check `IMGGO_API_KEY` is set correctly
2. Verify `IMGGO_BASE_URL` is correct
3. Try in a browser: `https://img-go.com/api/health` (if available)

### Issue: "401 Unauthorized"

**Cause:** Invalid or missing API key

**Solution:**
1. Go to collection **Variables** tab
2. Verify `IMGGO_API_KEY` is set
3. Check the key is valid (no extra spaces)
4. Ensure Authorization is set to **Bearer Token** (should be inherited from collection)

### Issue: "404 Not Found"

**Cause:** Invalid pattern_id or endpoint URL

**Solution:**
1. Verify `pattern_id` is correct
2. Check the endpoint path in the request
3. Verify `IMGGO_BASE_URL` doesn't have a trailing slash

### Issue: Job status stays "processing" forever

**Cause:** API processing issue or very large image

**Solution:**
1. Wait longer (large images take more time)
2. Check if the pattern_id is correct
3. Try with a smaller test image
4. Check API status page (if available)

### Issue: Variables not updating

**Solution:**
1. Make sure you're modifying **Collection Variables** (not Environment Variables)
2. Click **Save** after changing variables
3. Check the **Console** to see if test scripts are running

## Tips and Best Practices

### 1. Use Console for Debugging

Open Console (View → Show Postman Console) to see:
- Request/response details
- Test script logs
- Variable values

### 2. Save Responses as Examples

After getting a successful response:
1. Click **Save Response**
2. Click **Save as Example**
3. Helps document API behavior

### 3. Organize with Folders

For large collections:
1. Right-click collection → **Add Folder**
2. Group related requests (e.g., "Upload", "Jobs", "Patterns")

### 4. Share with Team

1. Click **Share** on the collection
2. Generate a link or export JSON
3. Team members can import and collaborate

### 5. Document as You Go

1. Add descriptions to requests
2. Add comments in test scripts
3. Save example responses

## Integration with CI/CD

### GitHub Actions

```yaml
name: API Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Newman
        run: npm install -g newman
      - name: Run API Tests
        run: |
          newman run examples/languages/postman/ImgGo-API.postman_collection.json \
            --env-var "IMGGO_API_KEY=${{ secrets.IMGGO_API_KEY }}" \
            --env-var "pattern_id=pat_test_123"
```

### GitLab CI

```yaml
api_tests:
  script:
    - npm install -g newman
    - newman run examples/languages/postman/ImgGo-API.postman_collection.json
        --env-var "IMGGO_API_KEY=$IMGGO_API_KEY"
```

## Next Steps

- See [Use Cases](../../../use-cases/) for complete integration examples
- See [Python Examples](../python/) for programmatic access
- See [Node.js Examples](../nodejs/) for backend integration
- See [API Reference](../../../docs/api-reference/) for detailed documentation

## Need Help?

- [Getting Started Guide](../../../docs/getting-started/)
- [API Reference](../../../docs/api-reference/)
- Postman Documentation: https://learning.postman.com/
- GitHub Issues
