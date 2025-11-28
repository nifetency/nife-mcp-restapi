# Quick Start Guide - REST API MCP Server

## 🚀 Get Started in 5 Minutes

### Step 1: Clone or Download
```bash
# Navigate to the RESTAPI folder
cd "C:\Users\Varun S\Desktop\MCP Schema\RESTAPI"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your API details
# Required:
# - REST_API_BASE_URL
# - OPENAPI_SPEC_URL
# Optional:
# - AUTH_TYPE
# - API_ACCESS_TOKEN (for bearer auth)
```

### Step 4: Run the Server
```bash
python -m restapi_mcp_server
```

## 📋 Example Configurations

### Public API (No Auth)
```env
REST_API_BASE_URL=https://api.github.com
OPENAPI_SPEC_URL=https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json
AUTH_TYPE=none
```

### API with Bearer Token
```env
REST_API_BASE_URL=https://api.example.com
OPENAPI_SPEC_URL=https://api.example.com/openapi.json
AUTH_TYPE=bearer
API_ACCESS_TOKEN=your_bearer_token_here
```

### API with API Key
```env
REST_API_BASE_URL=https://api.example.com
OPENAPI_SPEC_URL=https://api.example.com/swagger.json
AUTH_TYPE=apikey
API_KEY_HEADER=X-API-Key
API_KEY_VALUE=your_api_key_here
```

### API with Basic Auth
```env
REST_API_BASE_URL=https://api.example.com
OPENAPI_SPEC_URL=https://api.example.com/openapi.yaml
AUTH_TYPE=basic
BASIC_AUTH_USERNAME=your_username
BASIC_AUTH_PASSWORD=your_password
```

## 🐳 Docker Quick Start

### Using Docker Compose (Recommended)
```bash
# 1. Configure .env file
cp .env.example .env
# Edit .env with your settings

# 2. Build and run
docker-compose up -d

# 3. View logs
docker-compose logs -f

# 4. Stop
docker-compose down
```

### Using Docker Directly
```bash
# Build
docker build -t restapi-mcp-server .

# Run with environment variables
docker run -it --rm \
  -e REST_API_BASE_URL=https://api.example.com \
  -e OPENAPI_SPEC_URL=https://api.example.com/openapi.json \
  -e API_ACCESS_TOKEN=your_token \
  restapi-mcp-server
```

## 🔌 Claude Desktop Integration

### Step 1: Find Claude Config
**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Add Server Configuration

**Local Python:**
```json
{
  "mcpServers": {
    "restapi": {
      "command": "python",
      "args": ["-m", "restapi_mcp_server"],
      "env": {
        "REST_API_BASE_URL": "https://api.example.com",
        "OPENAPI_SPEC_URL": "https://api.example.com/openapi.json",
        "AUTH_TYPE": "bearer",
        "API_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

**Docker:**
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

### Step 3: Restart Claude Desktop

## 📝 Testing Your Setup

Once the server is running with Claude, try these commands:

### 1. Check Health
```
Check the health of the REST API server
```

### 2. List Endpoints
```
Show me all available API endpoints
```

### 3. Get Endpoint Info
```
What parameters does the GET /users endpoint accept?
```

### 4. Execute Request
```
Get all users from the API
```

### 5. Create Resource
```
Create a new user with name "John Doe" and email "john@example.com"
```

## 🔍 Troubleshooting

### Server Won't Start
```bash
# Check Python version (need 3.11+)
python --version

# Verify dependencies
pip install -r requirements.txt

# Check environment variables
python -c "import os; print(os.getenv('REST_API_BASE_URL'))"
```

### Schema Loading Fails
- Verify OPENAPI_SPEC_URL is accessible
- Check OpenAPI spec format (JSON or YAML)
- Ensure spec is valid OpenAPI 3.x or Swagger 2.0
- Test URL in browser or with curl

### Authentication Errors
- Verify AUTH_TYPE is correct
- Check token/key/credentials are valid
- Try with AUTH_TYPE=none first
- Check API documentation for auth requirements

### Tools Not Generated
- Check server logs for errors
- Verify OpenAPI spec contains paths
- Ensure spec is properly formatted
- Try reloading the schema

### Docker Issues
```bash
# Check container status
docker ps -a

# View logs
docker logs <container_id>

# Rebuild image
docker-compose build --no-cache
```

## 📚 Next Steps

1. **Explore Generated Tools**: Use `list_available_endpoints` to see all tools
2. **Read API Docs**: Check your OpenAPI spec for endpoint details
3. **Test Endpoints**: Start with simple GET requests
4. **Build Workflows**: Chain multiple API calls together
5. **Monitor Usage**: Check logs for request/response details

## 🆘 Getting Help

- Check logs in stderr for detailed error messages
- Verify OpenAPI spec is valid using online validators
- Test API directly using curl or Postman first
- Review the README.md for full documentation
- Check COMPARISON.md to understand differences from GraphQL

## 💡 Tips

1. **Start Simple**: Test with a public API first (like GitHub)
2. **Verify Spec**: Validate your OpenAPI spec before loading
3. **Use Logging**: Set LOG_LEVEL=DEBUG for detailed information
4. **Test Auth**: Try without auth first, then add authentication
5. **Cache Smart**: Use SCHEMA_CACHE_TTL to balance freshness vs performance

---

**Ready to build? Start with the examples above! 🚀**
