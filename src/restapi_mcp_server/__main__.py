#!/usr/bin/env python3
"""
Main entry point for REST API MCP Server
"""
import asyncio
from restapi_mcp_server.server import RestApiMCPServer

async def main():
    server = RestApiMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
