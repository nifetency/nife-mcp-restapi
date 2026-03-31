"""
REST API MCP Server - Dynamic tool generation from OpenAPI/Swagger specs
"""

__version__ = "1.0.0"
__author__ = "Varun S"
__description__ = "Dynamic MCP server for REST APIs"

from restapi_mcp_server.server import RestApiMCPServer
from restapi_mcp_server.schema_manager import SchemaManager
from restapi_mcp_server.rest_client import RestClient

__all__ = ["RestApiMCPServer", "SchemaManager", "RestClient"]
