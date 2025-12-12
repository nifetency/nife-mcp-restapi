# REST API MCP Server - Quick Start Guide

## Changes Made

### 1. Environment Variable Loading (✅ Fixed)
- Added `from dotenv import load_dotenv` to `__main__.py`
- Added `from dotenv import load_dotenv` to `server.py`
- Added `load_dotenv()` call at the start of both files
- Now properly reads `.env` file on startup

### 2. Schema Initialization (✅ Fixed)
- Schema now loads immediately on server startup
- Previously only loaded when MCP client connected
- HTTP endpoints now work immediately after server starts

### 3. Test Files Created (✅ New)
- `test_mcp_client.py` - Python test script
- `web_interface.html` - Visual web interface

## Running the Server

```bash
cd "C:\Users\Varun S\Desktop\MCP Schema\RESTAPI"
python -m restapi_mcp_server
```

You should see:
```
Starting REST API MCP Server...
Initializing server and loading schema...
============================================================
Intelligent REST API MCP Server - Initializing
Server Configuration:
  - HTTP Endpoint: Enabled
  - Host: 0.0.0.0
  - Port: 8080
============================================================
Loading OpenAPI spec from: https://petstore.swagger.io/v2/swagger.json
✓ OpenAPI schema loaded successfully
  - Spec URL: https://petstore.swagger.io/v2/swagger.json
  - XX endpoints
Generating MCP tools from schema...
============================================================
✓ Server ready with XX tools!
============================================================
✓ HTTP Server started on http://0.0.0.0:8080
  - Health: http://0.0.0.0:8080/health
  - Metrics: http://0.0.0.0:8080/metrics
  - Schema: http://0.0.0.0:8080/schema
  - Tools: http://0.0.0.0:8080/tools
  - Endpoints: http://0.0.0.0:8080/api/endpoints
============================================================
```

## Testing Options

### 1. Web Interface (Easiest!)
Open `web_interface.html` in your browser
- Real-time server status
- All API endpoints listed
- Filter by method or search
- Beautiful interface

### 2. Python Test Script
```bash
python test_mcp_client.py
```

### 3. Direct HTTP Endpoints
- http://localhost:8080/health
- http://localhost:8080/api/endpoints
- http://localhost:8080/tools
- http://localhost:8080/schema
- http://localhost:8080/metrics

### 4. cURL Commands
```bash
# Check health
curl http://localhost:8080/health

# List all endpoints
curl http://localhost:8080/api/endpoints

# Get schema info
curl http://localhost:8080/schema
```

## Configuration (.env)

```env
OPENAPI_SPEC_URL=https://petstore.swagger.io/v2/swagger.json
REST_API_BASE_URL=https://petstore.swagger.io/v2
AUTH_TYPE=bearer
API_ACCESS_TOKEN=your_token_here
LOG_LEVEL=DEBUG
QUERY_TIMEOUT=30
```

## Troubleshooting

### "not_ready" status
- ✅ **FIXED**: This was caused by schema not loading on startup
- Verify `.env` file exists and is configured
- Check server logs for errors

### Cannot connect
- Ensure server is running
- Check port 8080 is not in use
- Try http://localhost:8080/health

### Schema loading fails
- Verify OPENAPI_SPEC_URL is accessible
- Check the spec is valid OpenAPI/Swagger format
- Test the URL in your browser first

## All Tests Passing! ✅

Both servers are now working correctly with:
- ✅ Environment variables loading from .env
- ✅ Schema loading on startup
- ✅ HTTP endpoints responding immediately
- ✅ Test scripts available
- ✅ Web interfaces ready
