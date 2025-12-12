# REST API MCP Server - Deployment Guide

## Overview

The REST API MCP Server now includes configurable ports for easy Docker deployment and HTTP endpoints for health checks and monitoring.

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REST_API_BASE_URL` | REST API base URL | - | Yes |
| `OPENAPI_SPEC_URL` | OpenAPI/Swagger spec URL or file path | - | Yes |
| `AUTH_TYPE` | Authentication type (bearer, apikey, basic, none) | bearer | No |
| `API_ACCESS_TOKEN` | Bearer token (if AUTH_TYPE=bearer) | - | Conditional |
| `API_KEY_HEADER` | API key header name (if AUTH_TYPE=apikey) | X-API-Key | Conditional |
| `API_KEY_VALUE` | API key value (if AUTH_TYPE=apikey) | - | Conditional |
| `BASIC_AUTH_USERNAME` | Username (if AUTH_TYPE=basic) | - | Conditional |
| `BASIC_AUTH_PASSWORD` | Password (if AUTH_TYPE=basic) | - | Conditional |
| `MCP_SERVER_PORT` | HTTP server port | 8080 | No |
| `MCP_SERVER_HOST` | HTTP server host | 0.0.0.0 | No |
| `ENABLE_HTTP_ENDPOINT` | Enable HTTP health/metrics endpoints | true | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `REQUEST_TIMEOUT` | Request timeout in seconds | 30 | No |
| `SCHEMA_CACHE_TTL` | Schema cache duration in seconds | 3600 | No |

### Setup Configuration

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your values:**
   ```bash
   REST_API_BASE_URL=https://api.yourdomain.com
   OPENAPI_SPEC_URL=https://api.yourdomain.com/openapi.json
   AUTH_TYPE=bearer
   API_ACCESS_TOKEN=your_token_here
   MCP_SERVER_PORT=8080
   ENABLE_HTTP_ENDPOINT=true
   ```

## Deployment Options

### Option 1: Docker Compose (Recommended)

**Build and run:**
```bash
docker-compose up --build
```

**Run in detached mode:**
```bash
docker-compose up -d
```

**Stop the server:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

### Option 2: Docker (Manual)

**Build the image:**
```bash
docker build -t restapi-mcp-server:latest .
```

**Run the container:**
```bash
docker run -d -i \
  --name restapi-mcp-server \
  -p 8080:8080 \
  -e REST_API_BASE_URL="https://api.yourdomain.com" \
  -e OPENAPI_SPEC_URL="https://api.yourdomain.com/openapi.json" \
  -e API_ACCESS_TOKEN="your_token_here" \
  -e MCP_SERVER_PORT=8080 \
  restapi-mcp-server:latest
```

### Option 3: Local Python

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the server:**
```bash
export $(cat .env | xargs)
python -m restapi_mcp_server
```

## HTTP Endpoints

When `ENABLE_HTTP_ENDPOINT=true`, the server exposes:

### Root Endpoint
```bash
curl http://localhost:8080/
```

### Health Check
```bash
curl http://localhost:8080/health
```

### Metrics
```bash
curl http://localhost:8080/metrics
```

### Schema Information
```bash
curl http://localhost:8080/schema
```

### Available Tools
```bash
curl http://localhost:8080/tools
```

### API Endpoints List
```bash
curl http://localhost:8080/api/endpoints
```

## Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: restapi-mcp-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: restapi-mcp-server
  template:
    metadata:
      labels:
        app: restapi-mcp-server
    spec:
      containers:
      - name: server
        image: restapi-mcp-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: REST_API_BASE_URL
          value: "https://api.yourdomain.com"
        - name: OPENAPI_SPEC_URL
          value: "https://api.yourdomain.com/openapi.json"
        - name: API_ACCESS_TOKEN
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: token
        - name: MCP_SERVER_PORT
          value: "8080"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: restapi-mcp-server
spec:
  selector:
    app: restapi-mcp-server
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

## Cloud Deployment

### Google Cloud Run

```bash
gcloud run deploy restapi-mcp-server \
  --image gcr.io/<project-id>/restapi-mcp-server:latest \
  --port 8080 \
  --set-env-vars REST_API_BASE_URL=https://api.yourdomain.com \
  --set-env-vars OPENAPI_SPEC_URL=https://api.yourdomain.com/openapi.json \
  --set-env-vars API_ACCESS_TOKEN=your_token \
  --allow-unauthenticated
```

### AWS ECS

1. Push image to ECR
2. Create task definition with port 8080 exposed
3. Deploy to ECS service

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name restapi-mcp-server \
  --image restapi-mcp-server:latest \
  --ports 8080 \
  --environment-variables \
    REST_API_BASE_URL=https://api.yourdomain.com \
    OPENAPI_SPEC_URL=https://api.yourdomain.com/openapi.json \
    API_ACCESS_TOKEN=your_token
```

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
MCP_SERVER_PORT=9000 docker-compose up
```

### Container Won't Start
```bash
# Check logs
docker logs restapi-mcp-server

# Common issues:
# - Missing REST_API_BASE_URL or OPENAPI_SPEC_URL
# - Invalid OpenAPI spec URL
# - Authentication credentials not set
```

### HTTP Endpoints Not Working
```bash
# Verify ENABLE_HTTP_ENDPOINT is true
docker exec restapi-mcp-server env | grep ENABLE_HTTP_ENDPOINT

# Test connection
curl -v http://localhost:8080/health
```

## Security Best Practices

1. **Never commit `.env` to version control**
2. **Use secrets management** for tokens and credentials
3. **Limit port exposure** in production
4. **Use TLS/SSL** with reverse proxy
5. **Set resource limits** in container orchestration

## Support

For issues or questions, refer to the main README.md or open a GitHub issue.
