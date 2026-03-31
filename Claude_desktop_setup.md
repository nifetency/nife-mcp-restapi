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