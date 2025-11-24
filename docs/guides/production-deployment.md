# Production Deployment

This guide covers deploying ImgGo API integrations to production environments.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Architectures](#deployment-architectures)
- [Platform-Specific Guides](#platform-specific-guides)
- [Configuration Management](#configuration-management)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling Strategies](#scaling-strategies)
- [Disaster Recovery](#disaster-recovery)
- [Maintenance](#maintenance)

## Pre-Deployment Checklist

### Code Quality

- [ ] All code reviewed and tested
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Load testing completed
- [ ] Security audit completed
- [ ] Dependencies up to date
- [ ] No hardcoded secrets
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Documentation complete

### Infrastructure

- [ ] Production environment provisioned
- [ ] SSL certificates configured
- [ ] DNS configured
- [ ] Firewall rules set
- [ ] Load balancer configured (if needed)
- [ ] Database backups configured
- [ ] Monitoring tools set up
- [ ] Alerting rules configured
- [ ] Disaster recovery plan documented

### Configuration

- [ ] Environment variables set
- [ ] API keys rotated for production
- [ ] Rate limits configured
- [ ] Timeouts set appropriately
- [ ] Connection pooling enabled
- [ ] Caching configured
- [ ] Retry logic implemented

## Deployment Architectures

### Architecture 1: Simple Web Service

**Use Case:** Small-scale, single-region deployment

```mermaid
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│  Web Server │─────▶│  ImgGo API   │
│  (Flask/    │      │              │
│   Express)  │      └──────────────┘
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │
└─────────────┘
```

**Components:**

- Single web server (Docker container)
- PostgreSQL database
- Direct API calls to ImgGo

**Pros:**

- Simple to deploy and maintain
- Low cost
- Easy to debug

**Cons:**

- Single point of failure
- Limited scalability
- No geographic distribution

---

### Architecture 2: Queue-Based Processing

**Use Case:** High-volume, batch processing

```mermaid
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│  Web Server │─────▶│  Message     │
│             │      │  Queue       │
└─────────────┘      │  (RabbitMQ/  │
                     │   Redis)     │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐      ┌──────────────┐
                     │   Worker     │─────▶│  ImgGo API   │
                     │   Pool       │      │              │
                     └──────┬───────┘      └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Database    │
                     └──────────────┘
```

**Components:**

- Web server (accepts uploads)
- Message queue (RabbitMQ, Redis, SQS)
- Worker pool (processes jobs)
- Database (stores results)

**Pros:**

- Scalable (add more workers)
- Resilient (retry failed jobs)
- Decoupled components

**Cons:**

- More complex
- Additional infrastructure
- Eventual consistency

---

### Architecture 3: Serverless

**Use Case:** Variable load, pay-per-use

```mermaid
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│  API        │─────▶│  Lambda/     │
│  Gateway    │      │  Cloud Fn    │
│             │      └──────┬───────┘
└─────────────┘             │
                            ▼
                     ┌──────────────┐
                     │  ImgGo API   │
                     │              │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  DynamoDB/   │
                     │  Firestore   │
                     └──────────────┘
```

**Components:**

- API Gateway
- Serverless functions (Lambda, Cloud Functions)
- NoSQL database (DynamoDB, Firestore)
- Object storage (S3, Cloud Storage)

**Pros:**

- Auto-scaling
- Pay only for usage
- No server management
- High availability

**Cons:**

- Cold start latency
- Vendor lock-in
- Complex debugging

---

### Architecture 4: Microservices

**Use Case:** Large-scale, multi-team

```mermaid
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│  Load       │─────▶│  Upload      │
│  Balancer   │      │  Service     │
└─────────────┘      └──────┬───────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐    ┌──────────────┐
│  Processing  │────▶│  ImgGo API   │    │  Webhook     │
│  Service     │     │              │    │  Service     │
└──────┬───────┘     └──────────────┘    └──────┬───────┘
       │                                         │
       ▼                                         ▼
┌──────────────┐                         ┌──────────────┐
│  Storage     │                         │  Notification│
│  Service     │                         │  Service     │
└──────────────┘                         └──────────────┘
```

**Components:**

- Multiple specialized services
- Service mesh (Istio, Linkerd)
- Container orchestration (Kubernetes)
- Distributed tracing

**Pros:**

- Highly scalable
- Independent deployment
- Technology diversity
- Fault isolation

**Cons:**

- Complex to deploy
- Distributed system challenges
- High operational overhead

## Platform-Specific Guides

### AWS Deployment

#### AWS Lambda + API Gateway

```python
# lambda_function.py
import os
import json
import requests

IMGGO_API_KEY = os.environ['IMGGO_API_KEY']
IMGGO_BASE_URL = os.environ['IMGGO_BASE_URL']

def lambda_handler(event, context):
    """AWS Lambda handler for image processing."""
    try:
        # Get image URL from event
        body = json.loads(event['body'])
        image_url = body['image_url']
        pattern_id = body['pattern_id']

        # Process image
        response = requests.post(
            f"{IMGGO_BASE_URL}/patterns/{pattern_id}/ingest",
            headers={'Authorization': f'Bearer {IMGGO_API_KEY}'},
            json={'image_url': image_url},
            timeout=30
        )

        job_id = response.json()['data']['job_id']

        # Return job_id to client
        return {
            'statusCode': 200,
            'body': json.dumps({'job_id': job_id})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**Deployment:**

```bash
# Package dependencies
pip install requests -t package/
cp lambda_function.py package/

# Create deployment package
cd package
zip -r ../lambda.zip .

# Deploy with AWS CLI
aws lambda create-function \
  --function-name imggo-processor \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda.zip \
  --environment Variables="{IMGGO_API_KEY=$IMGGO_API_KEY,IMGGO_BASE_URL=https://img-go.com/api}"
```

#### AWS ECS (Docker)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - IMGGO_API_KEY=${IMGGO_API_KEY}
      - IMGGO_BASE_URL=${IMGGO_BASE_URL}
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Deploy to ECS:**

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker build -t imggo-app .
docker tag imggo-app:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/imggo-app:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/imggo-app:latest

# Create ECS task and service (via AWS Console or CLI)
```

---

### Azure Deployment

#### Azure Functions

```python
# __init__.py
import logging
import os
import json
import requests
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function handler."""
    logging.info('Processing image request')

    try:
        req_body = req.get_json()
        image_url = req_body['image_url']
        pattern_id = req_body['pattern_id']

        # Get API key from environment
        api_key = os.environ['IMGGO_API_KEY']

        # Process image
        response = requests.post(
            f"https://img-go.com/api/patterns/{pattern_id}/ingest",
            headers={'Authorization': f'Bearer {api_key}'},
            json={'image_url': image_url}
        )

        return func.HttpResponse(
            response.text,
            status_code=response.status_code
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500
        )
```

**Deploy:**

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Initialize project
func init imggo-processor --python

# Create function
func new --name ProcessImage --template "HTTP trigger"

# Deploy
func azure functionapp publish imggo-processor-app
```

---

### Google Cloud Deployment

#### Cloud Functions

```python
# main.py
import os
import requests
from flask import jsonify

def process_image(request):
    """Google Cloud Function handler."""
    request_json = request.get_json()

    if not request_json or 'image_url' not in request_json:
        return jsonify({'error': 'Missing image_url'}), 400

    image_url = request_json['image_url']
    pattern_id = request_json['pattern_id']
    api_key = os.environ['IMGGO_API_KEY']

    # Process image
    response = requests.post(
        f"https://img-go.com/api/patterns/{pattern_id}/ingest",
        headers={'Authorization': f'Bearer {api_key}'},
        json={'image_url': image_url}
    )

    return jsonify(response.json()), response.status_code
```

**Deploy:**

```bash
gcloud functions deploy process-image \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars IMGGO_API_KEY=$IMGGO_API_KEY
```

---

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: imggo-processor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: imggo-processor
  template:
    metadata:
      labels:
        app: imggo-processor
    spec:
      containers:
      - name: processor
        image: your-registry/imggo-processor:latest
        ports:
        - containerPort: 8000
        env:
        - name: IMGGO_API_KEY
          valueFrom:
            secretKeyRef:
              name: imggo-secrets
              key: api-key
        - name: IMGGO_BASE_URL
          value: "https://img-go.com/api"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: imggo-processor-service
spec:
  selector:
    app: imggo-processor
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy:**

```bash
# Create secret
kubectl create secret generic imggo-secrets --from-literal=api-key=$IMGGO_API_KEY

# Deploy
kubectl apply -f deployment.yaml

# Check status
kubectl get pods
kubectl get service imggo-processor-service
```

## Configuration Management

### Environment Variables

```bash
# .env.production
IMGGO_API_KEY=imggo_prod_key_xyz
IMGGO_BASE_URL=https://img-go.com/api
DATABASE_URL=postgresql://user:pass@db.example.com:5432/imggo
REDIS_URL=redis://redis.example.com:6379
LOG_LEVEL=INFO
WORKERS=4
MAX_CONCURRENT=10
```

### Configuration File

```python
# config.py
import os

class Config:
    """Base configuration."""
    IMGGO_API_KEY = os.getenv('IMGGO_API_KEY')
    IMGGO_BASE_URL = os.getenv('IMGGO_BASE_URL', 'https://img-go.com/api')
    DATABASE_URL = os.getenv('DATABASE_URL')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    MAX_CONCURRENT = 5

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    MAX_CONCURRENT = 20

# Select config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

def get_config():
    env = os.getenv('ENVIRONMENT', 'development')
    return config[env]()
```

## Monitoring and Logging

### Application Logging

```python
import logging
import sys

def setup_logging():
    """Configure production logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/var/log/imggo/app.log')
        ]
    )

    # Set specific log levels
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Usage
logger.info(f"Processing image: {image_path}")
logger.error(f"Failed to process: {error}", exc_info=True)
```

### Structured Logging (JSON)

```python
import logging
import json
import sys

class JsonFormatter(logging.Formatter):
    """Format logs as JSON."""

    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Health Check Endpoint

```python
@app.route('/health')
def health_check():
    """Health check endpoint for load balancers."""
    try:
        # Check database connection
        db.execute('SELECT 1')

        # Check ImgGo API connectivity (optional)
        # response = requests.get(f"{IMGGO_BASE_URL}/health", timeout=5)
        # if response.status_code != 200:
        #     raise Exception("ImgGo API unhealthy")

        return jsonify({'status': 'healthy'}), 200

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
request_count = Counter('imggo_requests_total', 'Total requests')
request_duration = Histogram('imggo_request_duration_seconds', 'Request duration')
errors_count = Counter('imggo_errors_total', 'Total errors')

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

# Track metrics
@request_duration.time()
def process_image_tracked(image_path, pattern_id):
    request_count.inc()
    try:
        return process_image(image_path, pattern_id)
    except Exception as e:
        errors_count.inc()
        raise
```

## Scaling Strategies

### Vertical Scaling

Increase resources of existing instances:

```bash
# AWS EC2
aws ec2 modify-instance-attribute --instance-id i-1234567890abcdef0 --instance-type m5.2xlarge

# Kubernetes
kubectl set resources deployment imggo-processor --limits=cpu=2,memory=2Gi
```

### Horizontal Scaling

Add more instances:

```bash
# AWS Auto Scaling
aws autoscaling set-desired-capacity --auto-scaling-group-name imggo-asg --desired-capacity 5

# Kubernetes Horizontal Pod Autoscaler
kubectl autoscale deployment imggo-processor --min=3 --max=10 --cpu-percent=70
```

### Database Scaling

```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

## Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Backup database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
aws s3 cp backup_$(date +%Y%m%d).sql s3://imggo-backups/

# Backup configuration
tar -czf config_$(date +%Y%m%d).tar.gz /etc/imggo/
aws s3 cp config_$(date +%Y%m%d).tar.gz s3://imggo-backups/

# Cleanup old backups (keep last 30 days)
find . -name "backup_*.sql" -mtime +30 -delete
```

### Restore Procedure

```bash
#!/bin/bash
# restore.sh

# Download latest backup
aws s3 cp s3://imggo-backups/backup_20240115.sql .

# Restore database
psql $DATABASE_URL < backup_20240115.sql

# Restore configuration
aws s3 cp s3://imggo-backups/config_20240115.tar.gz .
tar -xzf config_20240115.tar.gz -C /
```

## Maintenance

### Zero-Downtime Deployment

```bash
# Blue-Green Deployment
# 1. Deploy new version (green)
kubectl apply -f deployment-v2.yaml

# 2. Wait for new pods to be ready
kubectl wait --for=condition=ready pod -l version=v2

# 3. Switch traffic
kubectl patch service imggo-processor -p '{"spec":{"selector":{"version":"v2"}}}'

# 4. Remove old version (blue)
kubectl delete deployment imggo-processor-v1
```

### Rolling Updates

```yaml
# deployment.yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

### Canary Deployment

```yaml
# 90% traffic to stable, 10% to canary
apiVersion: v1
kind: Service
metadata:
  name: imggo-processor
spec:
  selector:
    app: imggo-processor
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: imggo-stable
spec:
  replicas: 9
  template:
    metadata:
      labels:
        app: imggo-processor
        version: stable
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: imggo-canary
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: imggo-processor
        version: canary
```

## Production Checklist

### Pre-Launch

- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Monitoring and alerting configured
- [ ] Backup and restore tested
- [ ] Disaster recovery plan documented
- [ ] Runbooks created
- [ ] On-call rotation scheduled

### Post-Launch

- [ ] Monitor metrics daily
- [ ] Review logs for errors
- [ ] Track API usage and costs
- [ ] Gather user feedback
- [ ] Plan capacity for growth
- [ ] Regular security updates
- [ ] Performance optimization

## Next Steps

- [Pattern Design Best Practices](./pattern-design-best-practices.md)
- [Performance Optimization](./performance-optimization.md)
- [Security Best Practices](./security-best-practices.md)
- [Use Cases](../../use-cases/) for production examples

## Need Help?

- [API Reference](../api-reference/)
- [Getting Started Guide](../getting-started/)
- Support: <support@img-go.com>
- GitHub Issues
