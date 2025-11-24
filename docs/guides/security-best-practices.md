# Security Best Practices

This guide covers security considerations when integrating the ImgGo API into your applications.

## Table of Contents

- [API Key Management](#api-key-management)
- [Data Privacy](#data-privacy)
- [Network Security](#network-security)
- [Input Validation](#input-validation)
- [Output Sanitization](#output-sanitization)
- [Compliance](#compliance)
- [Incident Response](#incident-response)

## API Key Management

### 1. Never Hardcode API Keys

**Bad:**

```python
IMGGO_API_KEY = "imggo_key_abc123xyz456"  # NEVER DO THIS
```

**Good:**

```python
import os
IMGGO_API_KEY = os.getenv('IMGGO_API_KEY')
```

### 2. Use Environment Variables

**Development (.env file):**

```bash
# .env (add to .gitignore!)
IMGGO_API_KEY=imggo_key_abc123xyz456
IMGGO_BASE_URL=https://img-go.com/api
```

**Production (system environment):**

```bash
# Linux/Mac
export IMGGO_API_KEY="imggo_key_abc123xyz456"

# Windows
set IMGGO_API_KEY=imggo_key_abc123xyz456

# Docker
docker run -e IMGGO_API_KEY="imggo_key_abc123xyz456" myapp
```

### 3. Use Secret Management Services

**AWS Secrets Manager:**

```python
import boto3
import json

def get_api_key():
    """Retrieve API key from AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId='imggo/api-key')
    secret = json.loads(response['SecretString'])
    return secret['IMGGO_API_KEY']

IMGGO_API_KEY = get_api_key()
```

**Azure Key Vault:**

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_api_key():
    """Retrieve API key from Azure Key Vault."""
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url="https://myvault.vault.azure.net/",
        credential=credential
    )
    secret = client.get_secret("imggo-api-key")
    return secret.value

IMGGO_API_KEY = get_api_key()
```

**HashiCorp Vault:**

```python
import hvac

def get_api_key():
    """Retrieve API key from HashiCorp Vault."""
    client = hvac.Client(url='http://127.0.0.1:8200')
    client.token = os.getenv('VAULT_TOKEN')

    secret = client.secrets.kv.v2.read_secret_version(
        path='imggo/api-key'
    )
    return secret['data']['data']['key']

IMGGO_API_KEY = get_api_key()
```

### 4. Rotate API Keys Regularly

```python
import datetime

def check_key_age(key_created_date):
    """Alert if API key is older than 90 days."""
    age = (datetime.datetime.now() - key_created_date).days

    if age > 90:
        print(f"Warning: API key is {age} days old. Consider rotating.")
        send_alert("API key rotation needed")
```

### 5. Use Different Keys per Environment

```plaintext
Development:   imggo_key_dev_abc123
Staging:       imggo_key_staging_def456
Production:    imggo_key_prod_ghi789
```

Never use production keys in development/testing.

### 6. Restrict API Key Permissions

If the API supports it:

- Limit keys to specific patterns
- Set rate limits per key
- Restrict IP addresses
- Set expiration dates

## Data Privacy

### 1. Minimize Data Exposure

Only extract data you actually need:

**Bad:**

```python
# Extract everything
pattern = "Extract all information from this document"
```

**Good:**

```python
# Extract only required fields
pattern = "Extract only: invoice_number, date, total_amount"
```

### 2. Handle Sensitive Data

For documents containing PII (Personal Identifiable Information):

```python
def redact_sensitive_data(result):
    """Redact or hash sensitive fields."""
    import hashlib

    if 'ssn' in result:
        # Replace with hash
        result['ssn_hash'] = hashlib.sha256(
            result['ssn'].encode()
        ).hexdigest()
        del result['ssn']

    if 'credit_card' in result:
        # Keep last 4 digits only
        result['credit_card'] = '**** **** **** ' + result['credit_card'][-4:]

    return result

result = process_image(image_path, pattern_id)
result = redact_sensitive_data(result)
```

### 3. Encrypt Data at Rest

Store extraction results encrypted:

```python
from cryptography.fernet import Fernet

def encrypt_result(result, encryption_key):
    """Encrypt result before storage."""
    import json

    cipher = Fernet(encryption_key)
    plaintext = json.dumps(result).encode()
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext

def decrypt_result(ciphertext, encryption_key):
    """Decrypt result after retrieval."""
    import json

    cipher = Fernet(encryption_key)
    plaintext = cipher.decrypt(ciphertext)
    return json.loads(plaintext.decode())

# Usage
encryption_key = Fernet.generate_key()  # Store securely!

# Encrypt before saving
result = process_image(image_path, pattern_id)
encrypted = encrypt_result(result, encryption_key)
save_to_database(encrypted)

# Decrypt when needed
encrypted = load_from_database()
result = decrypt_result(encrypted, encryption_key)
```

### 4. Secure Image Storage

If storing images temporarily:

```python
import os
import tempfile

def process_image_securely(image_data):
    """Process image without persistent storage."""
    # Use temporary file
    with tempfile.NamedTemporaryFile(delete=True, suffix='.jpg') as tmp_file:
        tmp_file.write(image_data)
        tmp_file.flush()

        result = process_image(tmp_file.name, pattern_id)

        # File is automatically deleted when context exits
        return result
```

### 5. Data Retention Policies

```python
import datetime

def cleanup_old_data(max_age_days=30):
    """Delete extraction results older than specified days."""
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)

    # Delete old database records
    db.execute(
        "DELETE FROM extraction_results WHERE created_at < ?",
        (cutoff_date,)
    )

    # Delete old cached files
    for cache_file in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, cache_file)
        file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

        if file_mtime < cutoff_date:
            os.remove(file_path)
            print(f"Deleted old file: {cache_file}")
```

## Network Security

### 1. Always Use HTTPS

**Bad:**

```python
IMGGO_BASE_URL = "http://img-go.com/api"  # INSECURE
```

**Good:**

```python
IMGGO_BASE_URL = "https://img-go.com/api"  # SECURE
```

### 2. Verify SSL Certificates

```python
import requests

# Good: Verify SSL certificates (default)
response = requests.post(url, files=files, verify=True)

# Bad: Disable SSL verification (NEVER do this in production)
response = requests.post(url, files=files, verify=False)
```

### 3. Use Webhooks Securely

Verify webhook signatures:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """Verify webhook signature to ensure authenticity."""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)

@app.route('/webhook/imggo', methods=['POST'])
def handle_webhook():
    # Get signature from header
    signature = request.headers.get('X-ImgGo-Signature')

    # Verify signature
    if not verify_webhook_signature(request.data.decode(), signature, WEBHOOK_SECRET):
        return jsonify({'error': 'Invalid signature'}), 401

    # Process webhook
    data = request.json
    process_result(data)
    return jsonify({'status': 'ok'}), 200
```

### 4. IP Whitelisting

If your infrastructure supports it, whitelist ImgGo API IPs:

```python
ALLOWED_IPS = [
    '192.0.2.1',
    '192.0.2.2',
    # Add ImgGo webhook IP addresses
]

@app.before_request
def check_ip():
    """Restrict access to whitelisted IPs."""
    if request.endpoint == 'handle_webhook':
        if request.remote_addr not in ALLOWED_IPS:
            abort(403)
```

### 5. Rate Limiting

Protect your endpoints from abuse:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/api/process', methods=['POST'])
@limiter.limit("10 per minute")
def process_endpoint():
    """Rate-limited endpoint."""
    pass
```

## Input Validation

### 1. Validate File Types

```python
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file_path):
    """Validate uploaded file."""
    # Check extension
    ext = file_path.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file type: {ext}")

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file_size} bytes")

    # Check file content (magic bytes)
    import imghdr
    image_type = imghdr.what(file_path)
    if image_type not in ['jpeg', 'png']:
        raise ValueError(f"Invalid image format: {image_type}")

    return True

# Usage
try:
    validate_file(uploaded_file_path)
    result = process_image(uploaded_file_path, pattern_id)
except ValueError as e:
    print(f"Validation error: {e}")
```

### 2. Sanitize URLs

```python
from urllib.parse import urlparse

def validate_image_url(url):
    """Validate image URL."""
    # Check URL scheme
    parsed = urlparse(url)
    if parsed.scheme not in ['http', 'https']:
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

    # Block internal/private IPs
    import ipaddress
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback:
            raise ValueError("Private/loopback IPs not allowed")
    except ValueError:
        pass  # Hostname is not an IP

    # Check file extension
    path = parsed.path.lower()
    if not any(path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.pdf']):
        raise ValueError("Invalid file extension in URL")

    return True

# Usage
try:
    validate_image_url(user_provided_url)
    result = process_url(user_provided_url, pattern_id)
except ValueError as e:
    print(f"Invalid URL: {e}")
```

### 3. Validate Pattern IDs

```python
import re

def validate_pattern_id(pattern_id):
    """Validate pattern ID format."""
    # Expected format: pat_[a-z0-9_]+
    if not re.match(r'^pat_[a-z0-9_]+$', pattern_id):
        raise ValueError(f"Invalid pattern ID: {pattern_id}")

    return True
```

## Output Sanitization

### 1. Escape Output for Display

If displaying extraction results in web pages:

```python
import html

def sanitize_for_html(result):
    """Escape HTML characters in result."""
    if isinstance(result, dict):
        return {k: sanitize_for_html(v) for k, v in result.items()}
    elif isinstance(result, list):
        return [sanitize_for_html(item) for item in result]
    elif isinstance(result, str):
        return html.escape(result)
    else:
        return result

# Usage
result = process_image(image_path, pattern_id)
safe_result = sanitize_for_html(result)

# Now safe to display in HTML
return render_template('results.html', result=safe_result)
```

### 2. Validate Extracted Data

```python
def validate_extraction_result(result, schema):
    """Validate extracted data against expected schema."""
    errors = []

    # Check required fields
    for field in schema['required']:
        if field not in result:
            errors.append(f"Missing required field: {field}")

    # Check data types
    for field, expected_type in schema['types'].items():
        if field in result:
            if not isinstance(result[field], expected_type):
                errors.append(
                    f"Field '{field}' has wrong type: "
                    f"expected {expected_type}, got {type(result[field])}"
                )

    if errors:
        raise ValueError(f"Validation errors: {', '.join(errors)}")

    return result

# Usage
schema = {
    'required': ['invoice_number', 'total_amount'],
    'types': {
        'invoice_number': str,
        'total_amount': (int, float),
        'invoice_date': str
    }
}

result = process_image(image_path, pattern_id)
validated_result = validate_extraction_result(result, schema)
```

## Compliance

### 1. GDPR Compliance

For processing EU citizen data:

```python
def process_with_gdpr_compliance(image_path, pattern_id, user_id):
    """Process image with GDPR compliance."""
    # Log processing activity
    log_processing_activity(user_id, image_path, pattern_id)

    # Process image
    result = process_image(image_path, pattern_id)

    # Anonymize if needed
    result = anonymize_personal_data(result)

    # Set retention period
    set_data_retention(result, days=30)

    return result

def handle_gdpr_deletion_request(user_id):
    """Handle GDPR right to deletion."""
    # Delete all user data
    db.execute("DELETE FROM extraction_results WHERE user_id = ?", (user_id,))
    db.execute("DELETE FROM processing_logs WHERE user_id = ?", (user_id,))

    # Delete cached files
    user_cache_dir = os.path.join(CACHE_DIR, user_id)
    if os.path.exists(user_cache_dir):
        shutil.rmtree(user_cache_dir)

    print(f"Deleted all data for user: {user_id}")
```

### 2. HIPAA Compliance

For healthcare data:

```python
def process_medical_document(image_path, pattern_id):
    """Process medical document with HIPAA compliance."""
    # Ensure encrypted transmission
    if not IMGGO_BASE_URL.startswith('https://'):
        raise ValueError("HTTPS required for HIPAA compliance")

    # Process with audit logging
    with audit_context(action='process_medical_document', image=image_path):
        result = process_image(image_path, pattern_id)

    # Encrypt result
    encrypted_result = encrypt_result(result, encryption_key)

    # Store with access controls
    save_with_access_control(encrypted_result, allowed_roles=['doctor', 'admin'])

    return result

def audit_context(action, **kwargs):
    """Context manager for audit logging."""
    import contextlib

    @contextlib.contextmanager
    def _audit():
        start_time = time.time()
        try:
            yield
            status = 'success'
        except Exception as e:
            status = 'failure'
            raise
        finally:
            log_audit_event(
                action=action,
                status=status,
                duration=time.time() - start_time,
                **kwargs
            )

    return _audit()
```

### 3. PCI DSS Compliance

For payment card data:

```python
def process_receipt_with_pci_compliance(image_path, pattern_id):
    """Process receipt while maintaining PCI DSS compliance."""
    # Process image
    result = process_image(image_path, pattern_id)

    # Mask credit card numbers
    if 'credit_card' in result:
        result['credit_card'] = mask_credit_card(result['credit_card'])

    # Don't store CVV
    if 'cvv' in result:
        del result['cvv']

    return result

def mask_credit_card(card_number):
    """Mask all but last 4 digits of credit card."""
    if len(card_number) < 4:
        return '*' * len(card_number)

    return '*' * (len(card_number) - 4) + card_number[-4:]
```

## Incident Response

### 1. Monitor for Security Events

```python
import logging

security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)

def detect_anomalies(user_id, request_count, time_window):
    """Detect suspicious activity."""
    rate = request_count / time_window

    if rate > 100:  # More than 100 requests per second
        security_logger.warning(
            f"Suspicious activity detected for user {user_id}: "
            f"{rate:.1f} requests/second"
        )
        send_security_alert(f"Possible abuse from user {user_id}")
```

### 2. Implement Circuit Breaker

```python
class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""

    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func):
        """Execute function with circuit breaker protection."""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func()
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failures = 0
            return result

        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()

            if self.failures >= self.failure_threshold:
                self.state = 'OPEN'
                print("Circuit breaker OPEN")

            raise

# Usage
breaker = CircuitBreaker()

for image in images:
    try:
        result = breaker.call(lambda: process_image(image, pattern_id))
    except Exception as e:
        print(f"Request failed: {e}")
```

### 3. Incident Response Plan

**When API key is compromised:**

1. **Immediate Actions:**
   - Revoke compromised key
   - Generate new key
   - Update all systems with new key
   - Review access logs

2. **Investigation:**
   - Identify how key was compromised
   - Check for unauthorized usage
   - Assess data exposure

3. **Prevention:**
   - Implement key rotation
   - Add monitoring alerts
   - Review security practices

```python
def handle_key_compromise():
    """Handle compromised API key."""
    # Step 1: Revoke old key (manual step - contact ImgGo support)
    print("1. Revoking old API key...")

    # Step 2: Update to new key
    print("2. Updating to new API key...")
    new_key = input("Enter new API key: ")
    update_environment_variable('IMGGO_API_KEY', new_key)

    # Step 3: Review logs
    print("3. Reviewing access logs...")
    suspicious_requests = review_access_logs(start_date='2024-01-01')

    if suspicious_requests:
        print(f"Found {len(suspicious_requests)} suspicious requests")
        send_security_report(suspicious_requests)

    # Step 4: Notify stakeholders
    print("4. Notifying stakeholders...")
    send_notification("API key has been rotated due to security incident")
```

## Security Checklist

- [ ] API keys stored in environment variables or secret manager
- [ ] Never commit API keys to version control
- [ ] Use HTTPS for all API requests
- [ ] Validate all file uploads (type, size, content)
- [ ] Sanitize URLs before processing
- [ ] Encrypt sensitive data at rest
- [ ] Implement data retention policies
- [ ] Verify webhook signatures
- [ ] Rate limit all endpoints
- [ ] Log security events
- [ ] Have incident response plan
- [ ] Regular security audits
- [ ] Compliance requirements met (GDPR, HIPAA, PCI DSS)

## Next Steps

- [Pattern Design Best Practices](./pattern-design-best-practices.md)
- [Performance Optimization](./performance-optimization.md)
- [Production Deployment](./production-deployment.md)

## Need Help?

- [API Reference](../api-reference/)
- [Getting Started Guide](../getting-started/)
- Security Concerns: <security@img-go.com>
- GitHub Issues
