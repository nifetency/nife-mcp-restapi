# REST API MCP Server

![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![MCP](https://img.shields.io/badge/MCP-compatible-purple)

A dynamic Model Context Protocol (MCP) server that automatically discovers and generates tools from any REST API using OpenAPI/Swagger specifications. Point it at any OpenAPI spec and it instantly exposes every endpoint as an MCP tool — zero manual configuration.

---

## Documentation

For full documentation, guides, and examples, visit:

https://nife.io/mcp_opensource

---


## Installation

```bash
pip install nife-restapi-mcp-server
```

---

## Configuration

There are **four ways** to configure the server. They are applied in priority order — higher entries win:

| Priority | Method | Best for |
|----------|--------|----------|
| 1 | CLI arguments | One-off runs, testing |
| 2 | Environment variables | Docker, CI/CD, shell scripts |
| 3 | `.env` file | Local development |
| 4 | Defaults | Nothing required by default |

### Method 1 — CLI Arguments

```bash
restapi-mcp-server --base-url https://api.example.com --spec-url https://api.example.com/openapi.json --token mytoken
```

All available flags:

```
--base-url URL       REST API base URL (required if not set via env)
--spec-url URL       OpenAPI/Swagger spec URL or local file path (required if not set via env)
--token TOKEN        API access token for bearer authentication
--auth-type TYPE     Authentication type: bearer, apikey, basic, none (default: bearer)
--mode stdio|http    Server mode (default: stdio)
--port PORT          HTTP port, only used in http mode (default: 8080)
--host HOST          HTTP host, only used in http mode (default: 0.0.0.0)
--log-level LEVEL    Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
--env-file PATH      Path to a custom .env file
--version            Show version and exit
```

### Method 2 — Environment Variables

```bash
export REST_API_BASE_URL=https://api.example.com
export OPENAPI_SPEC_URL=https://api.example.com/openapi.json
export API_ACCESS_TOKEN=your_token_here
export MCP_MODE=stdio

restapi-mcp-server
```

### Method 3 — `.env` File

Create a `.env` file in your working directory:

```env
REST_API_BASE_URL=https://api.example.com
OPENAPI_SPEC_URL=https://api.example.com/openapi.json
API_ACCESS_TOKEN=your_token_here
AUTH_TYPE=bearer
MCP_MODE=stdio
LOG_LEVEL=INFO
```

Then just run:

```bash
restapi-mcp-server
```

### Method 4 — Claude Desktop Config (most common for MCP use)

No `.env` file needed. Pass everything via the `env` block in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "restapi": {
      "command": "restapi-mcp-server",
      "env": {
        "REST_API_BASE_URL": "https://api.example.com",
        "OPENAPI_SPEC_URL": "https://api.example.com/openapi.json",
        "API_ACCESS_TOKEN": "your_token_here",
        "MCP_MODE": "stdio",
        "ENABLE_HTTP_ENDPOINT": "false"
      }
    }
  }
}
```

Claude Desktop injects the `env` block values directly into the process — this is the standard MCP pattern.

---

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REST_API_BASE_URL` | Yes | — | REST API base URL |
| `OPENAPI_SPEC_URL` | Yes | — | OpenAPI/Swagger spec URL or local file path |
| `AUTH_TYPE` | No | `bearer` | Auth method: `bearer`, `apikey`, `basic`, `none` |
| `API_ACCESS_TOKEN` | No | — | Bearer token for auth |
| `API_KEY_HEADER` | No | `X-API-Key` | Header name for API key auth |
| `API_KEY_VALUE` | No | — | API key value |
| `BASIC_AUTH_USERNAME` | No | — | Username for basic auth |
| `BASIC_AUTH_PASSWORD` | No | — | Password for basic auth |
| `MCP_MODE` | No | `stdio` | `stdio` or `http` |
| `ENABLE_HTTP_ENDPOINT` | No | `true` | Enable HTTP health/metrics endpoints |
| `MCP_SERVER_PORT` | No | `8080` | HTTP server port |
| `MCP_SERVER_HOST` | No | `0.0.0.0` | HTTP server host |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `REQUEST_TIMEOUT` | No | `30` | Request timeout in seconds |
| `SCHEMA_CACHE_TTL` | No | `3600` | Schema cache TTL in seconds |

---

## Operating Modes

### MCP Mode (`stdio`) — for Claude Desktop, Cursor, MCP clients

```bash
restapi-mcp-server --base-url https://api.example.com --spec-url https://api.example.com/openapi.json --mode stdio
```

Communicates via stdin/stdout. No HTTP server is started. This is the default.

### HTTP Mode — for Docker, Kubernetes, server deployments

```bash
restapi-mcp-server --base-url https://api.example.com --spec-url https://api.example.com/openapi.json --mode http --port 8080
```

Starts an HTTP server with health and metrics endpoints:
- `GET /` — server info
- `GET /health` — health check
- `GET /metrics` — server metrics
- `GET /schema` — OpenAPI schema summary
- `GET /tools` — all generated tools
- `GET /api/endpoints` — all API endpoints

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

## Docker

```bash
docker build -t restapi-mcp-server .

docker run -p 8080:8080 \
  -e REST_API_BASE_URL=https://api.example.com \
  -e OPENAPI_SPEC_URL=https://api.example.com/openapi.json \
  -e API_ACCESS_TOKEN=your_token \
  -e MCP_MODE=http \
  restapi-mcp-server
```

Or with Docker Compose:

```bash
cp .env.example .env   # fill in your values
docker-compose up
```

---

## Available Tools

The server dynamically generates the following tool types:

### Endpoint Tools
Named by HTTP method and path: `<method>_<path_parts>`

Examples:
- `get_users`
- `post_users`
- `get_users_by_id`
- `delete_users_by_id`
- `put_users_by_id`

### Utility Tools
- `list_available_endpoints` — list all endpoints (filterable by method or path)
- `get_endpoint_info` — detailed info about a specific endpoint
- `get_schema_info` — OpenAPI schema summary or specific model details
- `execute_custom_request` — run any HTTP request with full control
- `health_check` — server health and schema status

---

## OpenAPI Specification Support

- OpenAPI 3.x (full support)
- Swagger 2.0 (backward compatible)

Supported spec sources:
- Remote JSON URL
- Remote YAML URL
- Local JSON file
- Local YAML file

---

## Key Features

- **Zero config endpoints** — auto-parses any OpenAPI/Swagger spec and generates MCP tools
- **Dual mode** — stdio for MCP clients, HTTP for server deployments
- **Flexible config** — CLI args, env vars, .env file, or Claude Desktop env block
- **Multiple auth methods** — Bearer, API key, Basic, or none
- **Production ready** — Docker, Kubernetes, AWS ECS, Google Cloud Run compatible
- **Self-documenting** — `list_available_endpoints`, `get_endpoint_info`, `get_schema_info` tools built in
- **Documentation** — https://nife.io/mcp_opensource
---

## Troubleshooting

**`[ERROR] REST API base URL not configured`**

Set `REST_API_BASE_URL` via any method above. The most common fix:
```bash
restapi-mcp-server --base-url https://your-api.com
```

**`[ERROR] OpenAPI spec URL not configured`**

Set `OPENAPI_SPEC_URL` via any method above:
```bash
restapi-mcp-server --spec-url https://your-api.com/openapi.json
```

**Port already in use**

Change the port:
```bash
restapi-mcp-server --mode http --port 9090
```

**Docker container exits immediately**

Make sure you're using HTTP mode:
```bash
docker run -e MCP_MODE=http -e REST_API_BASE_URL=... -e OPENAPI_SPEC_URL=... restapi-mcp-server
```

**Schema not loading**

- Verify the spec URL is reachable
- Check the format is valid JSON or YAML
- Ensure the spec is OpenAPI 3.x or Swagger 2.0

---

## License

MIT
