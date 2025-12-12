# Changes Summary - REST API MCP Server Port Configuration

## Overview

Added configurable port support and HTTP health endpoints to make the REST API MCP Server production-ready for Docker deployment.

## What's New

### 1. **Configurable Ports**
- Port configurable via `MCP_SERVER_PORT` environment variable (default: 8080)
- Host configurable via `MCP_SERVER_HOST` environment variable (default: 0.0.0.0)
- HTTP endpoints can be enabled/disabled via `ENABLE_HTTP_ENDPOINT` (default: true)

### 2. **HTTP Health Endpoints**
New REST endpoints for monitoring and debugging:

| Endpoint | Description |
|----------|-------------|
| `GET /` | Server information and available endpoints |
| `GET /health` | Health check endpoint for load balancers |
| `GET /metrics` | Server metrics (uptime, tool count, etc.) |
| `GET /schema` | OpenAPI schema information |
| `GET /tools` | List of available MCP tools |
| `GET /api/endpoints` | List of all available REST API endpoints |

### 3. **Enhanced Docker Support**
- Dockerfile updated with `EXPOSE 8080`
- docker-compose.yml updated with port mapping
- Environment variables properly configured
- Health checks configured in Docker

### 4. **New Files**

#### Documentation
- `DEPLOYMENT.md` - Complete deployment guide
- `CHANGES.md` - This file - detailed change summary

#### Scripts
- `quickstart.sh` - Quick start script for Linux/Mac
- `quickstart.bat` - Quick start script for Windows

### 5. **Updated Files**

#### Code Changes
- `src/restapi_mcp_server/server.py`:
  - Added aiohttp web server for HTTP endpoints
  - Added `setup_http_server()` method
  - Port and host configuration in `__init__`
  - Graceful shutdown of HTTP server
  - New handler methods for all HTTP endpoints
  - Additional /api/endpoints route for listing REST API endpoints

#### Configuration
- `requirements.txt`:
  - Added `aiohttp>=3.9.0` dependency

- `.env.example`:
  - Added `MCP_SERVER_PORT=8080`
  - Added `MCP_SERVER_HOST=0.0.0.0`
  - Added `ENABLE_HTTP_ENDPOINT=true`

- `Dockerfile`:
  - Added port environment variables
  - Added `EXPOSE 8080`

- `docker-compose.yml`:
  - Added port mapping `8080:8080`
  - Added port environment variables

- `README.md`:
  - Added HTTP endpoints section
  - Updated feature list
  - Added deployment instructions
  - Added references to new documentation

## Quick Start

### For New Users

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your credentials:**
   ```env
   REST_API_BASE_URL=https://api.yourdomain.com
   OPENAPI_SPEC_URL=https://api.yourdomain.com/openapi.json
   AUTH_TYPE=bearer
   API_ACCESS_TOKEN=your_token_here
   MCP_SERVER_PORT=8080
   ```

3. **Run quick start:**
   ```bash
   # Linux/Mac
   chmod +x quickstart.sh
   ./quickstart.sh

   # Windows
   quickstart.bat
   ```

4. **Test the server:**
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/api/endpoints
   ```

### For Existing Users

If you're already using this server:

1. **Update your code:**
   ```bash
   git pull
   pip install -r requirements.txt  # Install aiohttp
   ```

2. **Update your .env file** (optional, uses defaults if not set):
   ```env
   MCP_SERVER_PORT=8080
   MCP_SERVER_HOST=0.0.0.0
   ENABLE_HTTP_ENDPOINT=true
   ```

3. **Update Docker setup:**
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

## Configuration Examples

### Default Configuration (Recommended)
```env
REST_API_BASE_URL=https://api.yourdomain.com
OPENAPI_SPEC_URL=https://api.yourdomain.com/openapi.json
AUTH_TYPE=bearer
API_ACCESS_TOKEN=your_token
MCP_SERVER_PORT=8080
ENABLE_HTTP_ENDPOINT=true
```

### Custom Port
```env
REST_API_BASE_URL=https://api.yourdomain.com
OPENAPI_SPEC_URL=https://api.yourdomain.com/openapi.json
API_ACCESS_TOKEN=your_token
MCP_SERVER_PORT=9000
ENABLE_HTTP_ENDPOINT=true
```

### Disable HTTP Endpoints (stdio only)
```env
REST_API_BASE_URL=https://api.yourdomain.com
OPENAPI_SPEC_URL=https://api.yourdomain.com/openapi.json
API_ACCESS_TOKEN=your_token
ENABLE_HTTP_ENDPOINT=false
```

## Deployment Examples

### Docker Compose
```bash
docker-compose up -d
```

### Docker with Custom Port
```bash
docker run -d -p 9000:9000 \
  -e REST_API_BASE_URL=https://api.example.com \
  -e OPENAPI_SPEC_URL=https://api.example.com/openapi.json \
  -e API_ACCESS_TOKEN=token \
  -e MCP_SERVER_PORT=9000 \
  restapi-mcp-server:latest
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: restapi-mcp-server
spec:
  template:
    spec:
      containers:
      - name: server
        image: restapi-mcp-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: MCP_SERVER_PORT
          value: "8080"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
```

## Migration Guide

### From Previous Version

No breaking changes! The server is backward compatible:
- If `MCP_SERVER_PORT` is not set, defaults to 8080
- If `ENABLE_HTTP_ENDPOINT` is not set, defaults to true
- Existing stdio communication continues to work unchanged

### Updating Docker Deployments

1. Pull latest changes
2. Rebuild Docker image: `docker-compose build`
3. Restart services: `docker-compose up -d`

### Updating Kubernetes Deployments

1. Build and push new image
2. Update deployment: `kubectl apply -f deployment.yaml`
3. Verify health: `kubectl get pods`

## Testing

### Test HTTP Endpoints
```bash
# Health check
curl http://localhost:8080/health

# Metrics
curl http://localhost:8080/metrics

# Schema info
curl http://localhost:8080/schema

# Tools list
curl http://localhost:8080/tools

# API endpoints
curl http://localhost:8080/api/endpoints
```

### Test with Different Ports
```bash
# Start on port 9000
MCP_SERVER_PORT=9000 docker-compose up -d

# Test
curl http://localhost:9000/health
```

## Monitoring

### Health Check Integration

**Docker Compose:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Kubernetes:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
```

## Benefits

1. **Production Ready**: Deployable to production environments
2. **Health Monitoring**: Easy integration with monitoring systems
3. **Flexible Deployment**: Works with any container orchestration
4. **Better Debugging**: HTTP endpoints for troubleshooting
5. **Port Flexibility**: Can run multiple instances on different ports
6. **Cloud Compatible**: Works with all major cloud providers

## Key Differences from GraphQL Server

While both servers share the same port configuration features, the REST API server includes:

- Additional `/api/endpoints` route for listing REST API endpoints
- Support for multiple authentication methods (Bearer, API Key, Basic)
- OpenAPI/Swagger spec parsing instead of GraphQL introspection
- Different tool naming convention based on HTTP methods and paths

## Documentation

- **DEPLOYMENT.md** - Complete deployment guide
- **README.md** - Updated with new features
- **.env.example** - Updated with new variables

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Submit pull requests
- Check the main README.md for more information

## Next Steps

- Consider adding Prometheus metrics format support
- Add OpenTelemetry integration for distributed tracing
- Create Helm charts for Kubernetes deployment
- Add support for custom health check endpoints

## License

Same as the main project - MIT License
