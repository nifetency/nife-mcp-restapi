# Claude Desktop Setup

After installing the package via pip:

```bash
pip install restapi-mcp-server
```

Add the following to your `claude_desktop_config.json`:

## Option 1 — Using the installed CLI command (recommended)

```json
{
  "mcpServers": {
    "restapi": {
      "command": "restapi-mcp-server",
      "env": {
        "REST_API_BASE_URL": "",
        "OPENAPI_SPEC_URL": "https://api.example.com/openapi.json",
        "API_ACCESS_TOKEN": "your_token_here",
        "MCP_MODE": "stdio",
        "ENABLE_HTTP_ENDPOINT": "false"
      }
    }
  }
}
```

## Option 2 — Using python -m (from source / development)

```json
{
  "mcpServers": {
    "restapi": {
      "command": "python",
      "args": ["-m", "restapi_mcp_server"],
      "cwd": "<PATH_TO_REPO_ROOT>",
      "env": {
        "REST_API_BASE_URL": "https://api.example.com",
        "OPENAPI_SPEC_URL": "https://api.example.com/openapi.json",
        "API_ACCESS_TOKEN": "your_token_here",
        "MCP_MODE": "stdio",
        "ENABLE_HTTP_ENDPOINT": "false",
        "PYTHONPATH": "<PATH_TO_REPO_ROOT>/src"
      }
    }
  }
}
```

## Finding your config file

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
