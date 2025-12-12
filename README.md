# REST API MCP Server

A dynamic Model Context Protocol (MCP) server that automatically discovers and generates tools from any REST API using OpenAPI/Swagger specifications. Zero hardcoding required!

## 🚀 Features

- **Automatic Tool Generation**: Parses OpenAPI/Swagger specs and generates MCP tools dynamically
- **Zero Configuration**: Just provide your REST API base URL and OpenAPI spec
- **Schema-Driven**: Always up-to-date with your API
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Configurable Ports**: Define custom ports for HTTP endpoints
- **HTTP Health Endpoints**: Built-in health checks, metrics, and monitoring
- **Production Ready**: Kubernetes, AWS ECS, Google Cloud Run compatible
- **Multiple Auth Methods**: Support for Bearer tokens, API keys, Basic auth
- **Type-Safe**: Validates requests against the OpenAPI schema
- **Self-Documenting**: Built-in API exploration tools

## 📋 Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- A REST API with OpenAPI/Swagger specification
- API access token (if your API requires authentication)

## 🛠️ Installation

### Option 1: Local Installation

```bash
# Clone or download this folder
cd restapi-mcp-server

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your REST API details

# Run the server
python -m restapi_mcp_server
```

### Option 2: Docker (Recommended for Deployment)

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your REST API details

# Quick start (Linux/Mac)
./quickstart.sh

# Quick start (Windows)
quickstart.bat

# Or manually with Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t restapi-mcp-server .
docker run -it -p 8080:8080 --env-file .env restapi-mcp-server

# Or build and run manually
docker build -t restapi-mcp-server .
docker run -it --env-file .env restapi-mcp-server
```

### Option 3: Docker with Environment Variables

```bash
docker run -it \
  -e REST_API_BASE_URL=https://api.example.com \
  -e OPENAPI_SPEC_URL=https://api.example.com/openapi.json \
  -e API_ACCESS_TOKEN=your_token_here \
  restapi-mcp-server:latest
```

## 🔧 Configuration

Create a `.env` file in the project root:

```env
# REST API Base URL (REQUIRED)
REST_API_BASE_URL=https://api.example.com

# OpenAPI Spec URL (REQUIRED)
# Can be a URL or local file path
OPENAPI_SPEC_URL=https://api.example.com/openapi.json

# Authentication Type (optional)
# Options: bearer, apikey, basic, none
AUTH_TYPE=bearer

# API Access Token (required for bearer auth)
API_ACCESS_TOKEN=your_access_token_here

# API Key Header Name (required for apikey auth)
API_KEY_HEADER=X-API-Key
API_KEY_VALUE=your_api_key_here

# Basic Auth (required for basic auth)
BASIC_AUTH_USERNAME=username
BASIC_AUTH_PASSWORD=password

# Logging Level (optional)
LOG_LEVEL=INFO

# Request Timeout (optional, in seconds)
REQUEST_TIMEOUT=30

# Schema Cache TTL (optional, in seconds)
SCHEMA_CACHE_TTL=3600
```

## 🌐 HTTP Endpoints

When `ENABLE_HTTP_ENDPOINT=true` (default), the server provides REST endpoints:

- **GET /** - Server info and available endpoints
- **GET /health** - Health check (use for monitoring)
- **GET /metrics** - Server metrics and statistics
- **GET /schema** - OpenAPI schema information
- **GET /tools** - List of available MCP tools
- **GET /api/endpoints** - List of available REST API endpoints

Example:
```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/endpoints
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📖 Usage

### With Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "restapi": {
      "command": "python",
      "args": ["-m", "restapi_mcp_server"],
      "env": {
        "REST_API_BASE_URL": "https://api.example.com",
        "OPENAPI_SPEC_URL": "https://api.example.com/openapi.json",
        "API_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

Or using Docker:

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

### Available Tools

The server automatically generates the following types of tools:

1. **Endpoint Tools**: `<method>_<endpoint>` - Execute any API endpoint
   - Examples: `get_users`, `post_users`, `get_users_by_id`, `delete_users_by_id`
2. **Utility Tools**:
   - `list_available_endpoints` - List all API endpoints
   - `get_endpoint_info` - Get detailed endpoint information
   - `get_schema_info` - Get OpenAPI schema information
   - `execute_custom_request` - Make custom API requests
   - `health_check` - Check server health

### Example Queries

```
# List available endpoints
"Show me all available API endpoints"

# Execute a GET request
"Get all users from the API"

# Execute a POST request
"Create a new user with name 'John Doe' and email 'john@example.com'"

# Execute with path parameters
"Get user with ID 123"

# Execute with query parameters
"Get users with limit 10 and status active"

# Get endpoint information
"What parameters does the POST /users endpoint accept?"
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Claude Desktop / CLI               │
└───────────────────┬─────────────────────────────┘
                    │ MCP Protocol (stdio)
┌───────────────────▼─────────────────────────────┐
│           REST API MCP Server                   │
│  ┌─────────────────────────────────────────┐   │
│  │      Schema Manager                     │   │
│  │  • Parses OpenAPI/Swagger specs         │   │
│  │  • Caches endpoints and schemas         │   │
│  │  • Generates tool definitions           │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │      REST Client                        │   │
│  │  • Executes HTTP requests               │   │
│  │  • Handles authentication               │   │
│  │  • Error handling and retries           │   │
│  └─────────────────────────────────────────┘   │
└───────────────────┬─────────────────────────────┘
                    │ HTTPS
┌───────────────────▼─────────────────────────────┐
│           Your REST API                         │
└─────────────────────────────────────────────────┘
```

## 📝 OpenAPI Specification Support

The server supports both OpenAPI 3.x and Swagger 2.x specifications:

- **OpenAPI 3.0+**: Full support for all features
- **Swagger 2.0**: Full backward compatibility

Specification can be provided as:
- URL to JSON file
- URL to YAML file
- Local file path

## 🔐 Authentication Methods

### Bearer Token
```env
AUTH_TYPE=bearer
API_ACCESS_TOKEN=your_bearer_token
```

### API Key
```env
AUTH_TYPE=apikey
API_KEY_HEADER=X-API-Key
API_KEY_VALUE=your_api_key
```

### Basic Auth
```env
AUTH_TYPE=basic
BASIC_AUTH_USERNAME=username
BASIC_AUTH_PASSWORD=password
```

### No Auth
```env
AUTH_TYPE=none
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io/)
- Inspired by the need for dynamic, schema-driven API integration

## 🔍 Troubleshooting

### Schema Not Loading
- Check OpenAPI spec URL and format
- Verify base URL is correct
- Check network connectivity

### Docker Container Exits Immediately
- Verify environment variables are set correctly
- Check logs with `docker logs <container_id>`

### Tool Calls Failing
- Check API authentication and permissions
- Verify endpoint paths and parameters
- Check API rate limits

### No Tools Generated
- Verify OpenAPI spec is valid
- Check spec contains paths
- Review server logs

## 📧 Support

- Open an issue on GitHub
- Check documentation

---
