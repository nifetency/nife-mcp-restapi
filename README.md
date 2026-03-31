# REST API MCP Server

A dynamic Model Context Protocol (MCP) server that automatically discovers and generates tools from any REST API using OpenAPI/Swagger specifications. This server eliminates manual integration by dynamically adapting to API schemas.

---

## Overview

The REST API MCP Server enables seamless integration between Large Language Models and REST APIs by parsing OpenAPI/Swagger specifications and exposing endpoints as MCP tools. The system is schema-driven, ensuring it remains synchronized with API changes without requiring code modifications.

---

## Key Features

### Automatic Tool Generation
- Parses OpenAPI/Swagger specifications
- Dynamically generates MCP tools for all endpoints
- No manual configuration required

### Schema-Driven Architecture
- Always aligned with API changes
- Supports OpenAPI 3.x and Swagger 2.x
- Enables type-safe request validation

### Production Ready
- Docker and Docker Compose support
- Kubernetes compatible
- Deployable on AWS ECS and Google Cloud Run
- Built-in health checks and monitoring endpoints

### Flexible Authentication
- Bearer token authentication
- API key support
- Basic authentication
- No-auth mode for public APIs

### Developer Experience
- Self-documenting API exploration
- Built-in schema inspection tools
- Strong logging and error handling
- Configurable request timeout and caching

---

## Prerequisites

- Python 3.11+
- Docker (optional)
- REST API with OpenAPI/Swagger specification
- API access credentials (if required)

---

## Installation

### Local Installation

```bash
git clone https://github.com/nifetency/nife-mcp-restapi
cd restapi-mcp-server

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API details

python -m restapi_mcp_server
```

---

### Docker Deployment

```bash
cp .env.example .env
# Edit .env

docker build -t restapi-mcp-server .
docker run -it -p 8080:8080 --env-file .env restapi-mcp-server
```

---

### Docker with Direct Environment Variables

```bash
docker run -it \
  -e REST_API_BASE_URL=https://api.example.com \
  -e MCP_MODE=http 
  -e OPENAPI_SPEC_URL=https://api.example.com/openapi.json \
  -e API_ACCESS_TOKEN=your_token_here \
  restapi-mcp-server:latest
```

---

## Configuration

Create a `.env` file in the project root:

```env
REST_API_BASE_URL=https://api.example.com
OPENAPI_SPEC_URL=https://api.example.com/openapi.json

AUTH_TYPE=bearer
API_ACCESS_TOKEN=your_access_token_here

API_KEY_HEADER=X-API-Key
API_KEY_VALUE=your_api_key_here

BASIC_AUTH_USERNAME=username
BASIC_AUTH_PASSWORD=password

LOG_LEVEL=INFO
REQUEST_TIMEOUT=30
SCHEMA_CACHE_TTL=3600
MCP_MODE=http

```

---

## HTTP Endpoints

When HTTP mode is enabled, the server exposes the following endpoints:

- GET / – Server information
- GET /health – Health check
- GET /metrics – Metrics and statistics
- GET /schema – OpenAPI schema details
- GET /tools – Available MCP tools
- GET /api/endpoints – List of API endpoints

Example:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/endpoints
```

---

## Integration

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "graphql": {
      "command": "python",
      "args": ["-m", "restapi_mcp_server"],
      "cwd": "<PATH_TO_REPO_ROOT>",
      "env": {
        "MCP_MODE": "stdio",
        "REST_API_BASE_URL": "https://api.example.com",
        "OPENAPI_SPEC_URL": "https://api.example.com/openapi.json",
        "API_ACCESS_TOKEN": "",
        "ENABLE_HTTP_ENDPOINT": "false"
        "PYTHONPATH": ""
      }
    }
  }
}
```

---

### Docker-Based Integration

```json
{
  "mcpServers": {
    "restapi": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "REST_API_BASE_URL=https://api.example.com",
        "-e", "OPENAPI_SPEC_URL=https://api.example.com/openapi.json",
        "-e", "API_ACCESS_TOKEN=your_token",
        "restapi-mcp-server:latest"
      ]
    }
  }
}
```

---

## Available Tools

The server dynamically generates the following tool types:

### Endpoint Tools
Format: <method>_<endpoint>

Examples:
- get_users
- post_users
- get_users_by_id
- delete_users_by_id

### Utility Tools
- list_available_endpoints
- get_endpoint_info
- get_schema_info
- execute_custom_request
- health_check

---

## Example Usage

```
Show all available API endpoints
Get all users from the API
Create a new user with name "John Doe" and email "john@example.com"
Get user with ID 123
Get users with limit 10 and status active
What parameters does the POST /users endpoint accept?
```

---

## Architecture

```
Client (MCP)
   │
   ▼
REST API MCP Server
   ├── Schema Manager
   │     • Parses OpenAPI specifications
   │     • Caches schemas
   │     • Generates tool definitions
   │
   └── REST Client
         • Executes HTTP requests
         • Handles authentication
         • Manages errors and retries
   │
   ▼
REST API
```

---

## OpenAPI Specification Support

- OpenAPI 3.x (full support)
- Swagger 2.0 (backward compatible)

Supported formats:
- Remote JSON URL
- Remote YAML URL
- Local file path

---

## Authentication Methods

### Bearer Token

```env
AUTH_TYPE=bearer
API_ACCESS_TOKEN=your_token
```

### API Key

```env
AUTH_TYPE=apikey
API_KEY_HEADER=X-API-Key
API_KEY_VALUE=your_key
```

### Basic Authentication

```env
AUTH_TYPE=basic
BASIC_AUTH_USERNAME=username
BASIC_AUTH_PASSWORD=password
```

### No Authentication

```env
AUTH_TYPE=none
```

---

## Troubleshooting

### Schema Not Loading
- Verify OpenAPI spec URL
- Check API availability
- Ensure correct format (JSON/YAML)

### Docker Container Exits Immediately
- Verify environment variables
- Check container logs

```bash
docker logs <container_id>
```

### Tool Execution Fails
- Verify authentication credentials
- Check endpoint parameters
- Confirm API permissions

### No Tools Generated
- Validate OpenAPI specification
- Ensure paths are defined
- Check server logs

---

## Contributing

Contributions are welcome. Please submit a pull request or open an issue for discussion.

---

## License

This project is licensed under the MIT License.

---

## Support

For issues and questions:
- Open an issue in the repository
- Review documentation and logs
