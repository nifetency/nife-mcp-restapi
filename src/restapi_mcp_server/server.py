#!/usr/bin/env python3
"""
Intelligent REST API MCP Server - Schema-Driven Implementation
Auto-generates tools from OpenAPI/Swagger specs - Zero hardcoded endpoints!
"""
import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Import schema manager and REST client
from restapi_mcp_server.schema_manager import SchemaManager
from restapi_mcp_server.rest_client import RestClient

class RestApiMCPServer:
    """
    Intelligent MCP Server with automatic tool generation
    
    Features:
    - Auto-discovers all endpoints from OpenAPI/Swagger specs
    - Generates MCP tools dynamically
    - Zero hardcoded endpoints
    - Always up-to-date with API
    - Self-documenting
    - Optional HTTP endpoint for health checks and metrics
    """
    
    def __init__(self):
        self.schema_manager = SchemaManager()
        self.tools: Dict[str, Dict] = {}
        self.ready = False
        self.port = int(os.environ.get('MCP_SERVER_PORT', 8080))
        self.host = os.environ.get('MCP_SERVER_HOST', '0.0.0.0')
        self.enable_http = os.environ.get('ENABLE_HTTP_ENDPOINT', 'true').lower() == 'true'
        self.app = None
        self.runner = None
        
    async def initialize(self) -> bool:
        """Initialize server by loading schema and generating tools"""
        logger.info("="*60)
        logger.info("Intelligent REST API MCP Server - Initializing")
        logger.info(f"Server Configuration:")
        logger.info(f"  - HTTP Endpoint: {'Enabled' if self.enable_http else 'Disabled'}")
        if self.enable_http:
            logger.info(f"  - Host: {self.host}")
            logger.info(f"  - Port: {self.port}")
        logger.info("="*60)
        
        # Get configuration
        base_url = os.environ.get('REST_API_BASE_URL')
        spec_url = os.environ.get('OPENAPI_SPEC_URL')
        auth_type = os.environ.get('AUTH_TYPE', 'bearer')
        
        if not base_url:
            logger.error("✗ REST_API_BASE_URL not configured")
            return False
        
        if not spec_url:
            logger.error("✗ OPENAPI_SPEC_URL not configured")
            return False
        
        # Configure authentication
        auth_config = self._get_auth_config(auth_type)
        
        # Set configuration
        self.schema_manager.base_url = base_url
        self.schema_manager.auth_config = auth_config
        
        # Load schema
        logger.info(f"Loading OpenAPI spec from: {spec_url}")
        success = self.schema_manager.load_schema(spec_url)
        
        if not success:
            logger.error("✗ Failed to load OpenAPI schema")
            return False
        
        # Generate tools
        logger.info("Generating MCP tools from schema...")
        self._generate_tools()
        
        self.ready = True
        logger.info("="*60)
        logger.info(f"✓ Server ready with {len(self.tools)} tools!")
        logger.info("="*60)
        
        return True
    
    def _get_auth_config(self, auth_type: str) -> Dict[str, Any]:
        """Get authentication configuration"""
        auth_type = auth_type.lower()
        
        if auth_type == 'bearer':
            token = os.environ.get('API_ACCESS_TOKEN')
            if token:
                logger.info("✓ Bearer token authentication configured")
                return {'type': 'bearer', 'token': token}
            else:
                logger.warning("⚠️  Bearer auth selected but no token provided")
                return {'type': 'none'}
        
        elif auth_type == 'apikey':
            header = os.environ.get('API_KEY_HEADER', 'X-API-Key')
            value = os.environ.get('API_KEY_VALUE')
            if value:
                logger.info(f"✓ API key authentication configured (header: {header})")
                return {'type': 'apikey', 'header': header, 'value': value}
            else:
                logger.warning("⚠️  API key auth selected but no key provided")
                return {'type': 'none'}
        
        elif auth_type == 'basic':
            username = os.environ.get('BASIC_AUTH_USERNAME')
            password = os.environ.get('BASIC_AUTH_PASSWORD')
            if username and password:
                logger.info("✓ Basic authentication configured")
                return {'type': 'basic', 'username': username, 'password': password}
            else:
                logger.warning("⚠️  Basic auth selected but credentials not complete")
                return {'type': 'none'}
        
        else:
            logger.info("ℹ No authentication configured")
            return {'type': 'none'}
    
    def _generate_tools(self):
        """Generate MCP tools dynamically from schema"""
        self.tools = {}
        
        # Generate endpoint tools
        endpoints = self.schema_manager.get_all_endpoints()
        for endpoint in endpoints:
            tool_name = self._create_tool_name(endpoint['method'], endpoint['path'])
            
            # Build parameter schema
            properties = {}
            required = []
            
            # Path parameters
            for param in endpoint.get('path_params', []):
                properties[param['name']] = {
                    'type': self._convert_type(param.get('type', 'string')),
                    'description': param.get('description', f"Path parameter: {param['name']}")
                }
                if param.get('required', True):
                    required.append(param['name'])
            
            # Query parameters
            for param in endpoint.get('query_params', []):
                properties[param['name']] = {
                    'type': self._convert_type(param.get('type', 'string')),
                    'description': param.get('description', f"Query parameter: {param['name']}")
                }
                if param.get('required', False):
                    required.append(param['name'])
            
            # Request body
            if endpoint.get('request_body'):
                properties['body'] = {
                    'type': 'object',
                    'description': 'Request body data'
                }
                if endpoint['request_body'].get('required', False):
                    required.append('body')
            
            self.tools[tool_name] = {
                "name": tool_name,
                "description": f"{endpoint['method'].upper()} {endpoint['path']} - {endpoint.get('description', 'No description')}",
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        
        # Add utility tools
        self._add_utility_tools()
        
        logger.info(f"Generated {len([t for t in self.tools if not t.startswith('list_') and not t.startswith('get_') and not t.startswith('execute_') and not t.startswith('health_')])} endpoint tools")
        logger.info(f"Added {len([t for t in self.tools if t.startswith('list_') or t.startswith('get_') or t.startswith('execute_') or t.startswith('health_')])} utility tools")
    
    def _create_tool_name(self, method: str, path: str) -> str:
        """Create a tool name from HTTP method and path"""
        # Convert path to snake_case and remove special characters
        path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
        
        # Add method prefix
        tool_name = f"{method.lower()}_"
        
        # Add path parts
        if path_parts:
            tool_name += '_'.join(path_parts)
        else:
            tool_name += 'root'
        
        # Handle path parameters - add "by" prefix
        if '{' in path:
            # Extract parameter names
            params = [p.strip('{}') for p in path.split('/') if p.startswith('{')]
            if params:
                tool_name += '_by_' + '_'.join(params)
        
        return tool_name.replace('-', '_').replace('.', '_')
    
    def _convert_type(self, openapi_type: str) -> str:
        """Convert OpenAPI type to JSON Schema type"""
        type_mapping = {
            'integer': 'number',
            'number': 'number',
            'string': 'string',
            'boolean': 'boolean',
            'array': 'array',
            'object': 'object'
        }
        return type_mapping.get(openapi_type.lower(), 'string')
    
    def _add_utility_tools(self):
        """Add utility tools for API exploration"""
        
        self.tools["list_available_endpoints"] = {
            "name": "list_available_endpoints",
            "description": "List all available REST API endpoints that can be called",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "Filter by HTTP method (GET, POST, PUT, DELETE, etc.)",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
                    },
                    "search": {
                        "type": "string",
                        "description": "Search term to filter endpoints by path"
                    }
                },
                "required": []
            }
        }
        
        self.tools["get_endpoint_info"] = {
            "name": "get_endpoint_info",
            "description": "Get detailed information about a specific API endpoint",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, etc.)"
                    },
                    "path": {
                        "type": "string",
                        "description": "Endpoint path"
                    }
                },
                "required": ["method", "path"]
            }
        }
        
        self.tools["get_schema_info"] = {
            "name": "get_schema_info",
            "description": "Get information about the OpenAPI schema",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "schema_name": {
                        "type": "string",
                        "description": "Optional: Get details about a specific schema/model"
                    }
                },
                "required": []
            }
        }
        
        self.tools["execute_custom_request"] = {
            "name": "execute_custom_request",
            "description": "Execute a custom HTTP request with full control",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE, etc.)",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
                    },
                    "path": {
                        "type": "string",
                        "description": "API endpoint path"
                    },
                    "query_params": {
                        "type": "object",
                        "description": "Query parameters"
                    },
                    "body": {
                        "type": "object",
                        "description": "Request body (for POST, PUT, PATCH)"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Additional headers"
                    }
                },
                "required": ["method", "path"]
            }
        }
        
        self.tools["health_check"] = {
            "name": "health_check",
            "description": "Check server health and schema status",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    
    async def handle_tool_call(self, tool_name: str, arguments: dict) -> dict:
        """Route tool calls to appropriate handlers"""
        
        if not self.ready:
            return {"error": "Server not ready. Schema not loaded."}
        
        try:
            # Utility tools
            if tool_name == "list_available_endpoints":
                return self._handle_list_endpoints(arguments)
            
            elif tool_name == "get_endpoint_info":
                return self._handle_endpoint_info(arguments)
            
            elif tool_name == "get_schema_info":
                return self._handle_schema_info(arguments)
            
            elif tool_name == "execute_custom_request":
                return await self._handle_custom_request(arguments)
            
            elif tool_name == "health_check":
                return self._handle_health_check(arguments)
            
            # Endpoint tools
            else:
                return await self._handle_endpoint_call(tool_name, arguments)
                
        except Exception as e:
            logger.error(f"Error in handle_tool_call: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def _handle_endpoint_call(self, tool_name: str, args: dict) -> dict:
        """Handle dynamic endpoint tool calls"""
        try:
            # Find the endpoint info from tool name
            endpoint_info = self._find_endpoint_from_tool(tool_name)
            
            if not endpoint_info:
                return {"error": f"Endpoint not found for tool: {tool_name}"}
            
            method = endpoint_info['method']
            path = endpoint_info['path']
            
            # Build path with parameters
            final_path = path
            path_params = {}
            for param in endpoint_info.get('path_params', []):
                param_name = param['name']
                if param_name in args:
                    path_params[param_name] = args[param_name]
                    final_path = final_path.replace(f"{{{param_name}}}", str(args[param_name]))
            
            # Extract query parameters
            query_params = {}
            for param in endpoint_info.get('query_params', []):
                param_name = param['name']
                if param_name in args:
                    query_params[param_name] = args[param_name]
            
            # Extract body
            body = args.get('body')
            
            logger.info(f"Executing {method.upper()} {final_path}")
            
            # Execute request
            client = RestClient(
                self.schema_manager.base_url,
                self.schema_manager.auth_config
            )
            result = client.execute_request(
                method=method,
                path=final_path,
                query_params=query_params,
                body=body
            )
            
            return {
                "success": True,
                "data": result,
                "metadata": {
                    "method": method.upper(),
                    "path": final_path,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in endpoint call: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _find_endpoint_from_tool(self, tool_name: str) -> Optional[Dict]:
        """Find endpoint info from tool name"""
        # Extract method from tool name
        method_prefix = tool_name.split('_')[0]
        
        # Search through endpoints
        for endpoint in self.schema_manager.get_all_endpoints():
            if self._create_tool_name(endpoint['method'], endpoint['path']) == tool_name:
                return endpoint
        
        return None
    
    def _handle_list_endpoints(self, args: dict) -> dict:
        """List available endpoints"""
        method_filter = args.get('method', '').upper()
        search = args.get('search', '').lower()
        
        endpoints = self.schema_manager.get_all_endpoints()
        
        # Apply filters
        if method_filter:
            endpoints = [e for e in endpoints if e['method'].upper() == method_filter]
        
        if search:
            endpoints = [e for e in endpoints if search in e['path'].lower()]
        
        return {
            "endpoints": [
                {
                    "method": e['method'].upper(),
                    "path": e['path'],
                    "description": e.get('description', 'No description'),
                    "tool_name": self._create_tool_name(e['method'], e['path'])
                }
                for e in endpoints
            ],
            "total_count": len(endpoints),
            "filters": {
                "method": method_filter if method_filter else None,
                "search": search if search else None
            }
        }
    
    def _handle_endpoint_info(self, args: dict) -> dict:
        """Get endpoint information"""
        method = args.get('method', '').lower()
        path = args.get('path', '')
        
        if not method or not path:
            return {"error": "Both method and path are required"}
        
        endpoint_info = self.schema_manager.get_endpoint_info(method, path)
        
        if not endpoint_info:
            return {"error": f"Endpoint {method.upper()} {path} not found"}
        
        return {
            "method": endpoint_info['method'].upper(),
            "path": endpoint_info['path'],
            "description": endpoint_info.get('description', 'No description'),
            "path_parameters": endpoint_info.get('path_params', []),
            "query_parameters": endpoint_info.get('query_params', []),
            "request_body": endpoint_info.get('request_body'),
            "responses": endpoint_info.get('responses', {}),
            "tool_name": self._create_tool_name(endpoint_info['method'], endpoint_info['path'])
        }
    
    def _handle_schema_info(self, args: dict) -> dict:
        """Get schema information"""
        schema_name = args.get('schema_name')
        
        if schema_name:
            schema_def = self.schema_manager.get_schema_definition(schema_name)
            if not schema_def:
                return {"error": f"Schema '{schema_name}' not found"}
            return {"schema": schema_def}
        
        return {
            "api_info": self.schema_manager.get_api_info(),
            "endpoints_count": len(self.schema_manager.get_all_endpoints()),
            "schemas_count": len(self.schema_manager.get_all_schemas())
        }
    
    async def _handle_custom_request(self, args: dict) -> dict:
        """Execute custom HTTP request"""
        try:
            method = args.get('method', '').upper()
            path = args.get('path', '')
            query_params = args.get('query_params', {})
            body = args.get('body')
            headers = args.get('headers', {})
            
            if not method or not path:
                return {"error": "Both method and path are required"}
            
            logger.info(f"Executing custom request: {method} {path}")
            
            client = RestClient(
                self.schema_manager.base_url,
                self.schema_manager.auth_config
            )
            result = client.execute_request(
                method=method.lower(),
                path=path,
                query_params=query_params,
                body=body,
                headers=headers
            )
            
            return {
                "success": True,
                "data": result,
                "metadata": {
                    "method": method,
                    "path": path,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in custom request: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _handle_health_check(self, args: dict) -> dict:
        """Health check"""
        return {
            "status": "healthy" if self.ready else "not_ready",
            "server": "restapi-mcp-server",
            "version": "1.0.0",
            "schema_loaded": self.schema_manager.schema_loaded,
            "tools_count": len(self.tools),
            "endpoints_count": len(self.schema_manager.get_all_endpoints()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def handle_request(self, request: dict) -> Optional[dict]:
        """Handle MCP JSON-RPC requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                # Initialize if not already done
                if not self.ready:
                    await self.initialize()
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "restapi-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "notifications/initialized":
                logger.info("✓ Client initialized successfully")
                return None
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": tool["name"],
                                "description": tool["description"],
                                "inputSchema": tool["inputSchema"]
                            }
                            for tool in self.tools.values()
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})
                
                result = await self.handle_tool_call(tool_name, tool_arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                raise Exception(f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def setup_http_server(self):
        """Setup optional HTTP server for health checks and metrics"""
        if not self.enable_http:
            return
        
        self.app = web.Application()
        
        # Health check endpoint
        async def health_handler(request):
            health_data = self._handle_health_check({})
            return web.json_response(health_data)
        
        # Metrics endpoint
        async def metrics_handler(request):
            metrics = {
                "server": "restapi-mcp-server",
                "version": "1.0.0",
                "uptime_seconds": asyncio.get_event_loop().time() - getattr(self, '_start_time', 0),
                "schema_loaded": self.schema_manager.schema_loaded,
                "tools_count": len(self.tools),
                "endpoints_count": len(self.schema_manager.get_all_endpoints()),
                "ready": self.ready,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            return web.json_response(metrics)
        
        # Schema info endpoint
        async def schema_handler(request):
            schema_info = self._handle_schema_info({})
            return web.json_response(schema_info)
        
        # Tools list endpoint
        async def tools_handler(request):
            tools_list = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "type": "endpoint" if not tool["name"].startswith(('list_', 'get_', 'execute_', 'health_')) else "utility"
                }
                for tool in self.tools.values()
            ]
            return web.json_response({
                "tools": tools_list,
                "total_count": len(tools_list)
            })
        
        # Endpoints list
        async def endpoints_handler(request):
            endpoints = self.schema_manager.get_all_endpoints()
            return web.json_response({
                "endpoints": [
                    {
                        "method": e['method'].upper(),
                        "path": e['path'],
                        "description": e.get('description', 'No description')
                    }
                    for e in endpoints
                ],
                "total_count": len(endpoints)
            })
        
        # Root endpoint
        async def root_handler(request):
            return web.json_response({
                "server": "restapi-mcp-server",
                "version": "1.0.0",
                "status": "running",
                "mode": "stdio",
                "endpoints": {
                    "health": "/health",
                    "metrics": "/metrics",
                    "schema": "/schema",
                    "tools": "/tools",
                    "api_endpoints": "/api/endpoints"
                }
            })
        
        # Register routes
        self.app.router.add_get('/', root_handler)
        self.app.router.add_get('/health', health_handler)
        self.app.router.add_get('/metrics', metrics_handler)
        self.app.router.add_get('/schema', schema_handler)
        self.app.router.add_get('/tools', tools_handler)
        self.app.router.add_get('/api/endpoints', endpoints_handler)
        
        # Start HTTP server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()
        
        logger.info("="*60)
        logger.info(f"✓ HTTP Server started on http://{self.host}:{self.port}")
        logger.info(f"  - Health: http://{self.host}:{self.port}/health")
        logger.info(f"  - Metrics: http://{self.host}:{self.port}/metrics")
        logger.info(f"  - Schema: http://{self.host}:{self.port}/schema")
        logger.info(f"  - Tools: http://{self.host}:{self.port}/tools")
        logger.info(f"  - Endpoints: http://{self.host}:{self.port}/api/endpoints")
        logger.info("="*60)
    
    async def run(self):
        """Main MCP server loop"""
        logger.info("Starting REST API MCP Server...")
        
        # Initialize schema immediately on startup
        logger.info("Initializing server and loading schema...")
        await self.initialize()
        
        # Setup HTTP server if enabled
        if self.enable_http:
            await self.setup_http_server()
        
        logger.info("Waiting for MCP client connection via stdin/stdout")
        self._start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Read JSON-RPC request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    logger.info("No more input, exiting")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse and handle request
                request = json.loads(line)
                response = await self.handle_request(request)
                
                # Send response to stdout
                if response is not None:
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
            except KeyboardInterrupt:
                logger.info("Server stopped by user")
                break
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                break
        
        # Cleanup HTTP server
        if self.runner:
            await self.runner.cleanup()
            logger.info("HTTP server stopped")
        
        logger.info("REST API MCP Server stopped")



async def start_http_server(server: RestApiMCPServer):
    """Start aiohttp HTTP server if enabled"""
    if not server.enable_http:
        logger.info("HTTP endpoint disabled")
        return

    app = web.Application()

    # Health endpoint
    async def health(request):
        return web.json_response({"status": "ok", "server": "restapi-mcp-server"})

    app.router.add_get("/health", health)

    server.app = app
    server.runner = web.AppRunner(app)
    await server.runner.setup()
    site = web.TCPSite(server.runner, host=server.host, port=server.port)

    logger.info(f"Starting HTTP server on http://{server.host}:{server.port}")
    await site.start()


async def start_mcp_listener(server: RestApiMCPServer):
    """
    Read JSON-RPC messages from stdin.
    If MCP client disconnects → exit MCP loop but KEEP HTTP running.
    """
    logger.info("MCP listener started — waiting for client...")

    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_running_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        try:
            line = await reader.readline()
            if not line:
                logger.info("MCP client disconnected — continuing HTTP server")
                break

            line = line.decode().strip()
            if not line:
                continue

            request = json.loads(line)
            response = await server.handle_request(request)

            if response:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

        except Exception as e:
            logger.error(f"MCP listener error: {e}", exc_info=True)
            break


async def main():
    server = RestApiMCPServer()
    await server.initialize()

    # Start HTTP server (forever)
    asyncio.create_task(start_http_server(server))

    # Start MCP listener (optional)
    asyncio.create_task(start_mcp_listener(server))

    # Keep container alive
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())

