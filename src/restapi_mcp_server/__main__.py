#!/usr/bin/env python3
"""
Main entry point for REST API MCP Server
Supports configuration via CLI args, environment variables, or .env file
Priority: CLI args > Environment variables > .env file > defaults
"""
import asyncio
import argparse
import os
import sys
from dotenv import load_dotenv


def parse_args():
    parser = argparse.ArgumentParser(
        description="REST API MCP Server - Dynamic MCP server for any REST API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration priority (highest to lowest):
  1. CLI arguments (--base-url, --spec-url, --token, etc.)
  2. Environment variables (REST_API_BASE_URL, OPENAPI_SPEC_URL, API_ACCESS_TOKEN, etc.)
  3. .env file in current working directory
  4. Built-in defaults

Examples:
  # Run with CLI args
  restapi-mcp-server --base-url https://api.example.com --spec-url https://api.example.com/openapi.json --token mytoken

  # Run in HTTP mode (Docker/server deployments)
  restapi-mcp-server --base-url https://api.example.com --spec-url https://api.example.com/openapi.json --mode http --port 8080

  # Run with env vars
  REST_API_BASE_URL=https://api.example.com OPENAPI_SPEC_URL=https://api.example.com/openapi.json restapi-mcp-server

  # Claude Desktop config (no CLI args needed — env block handles it)
  See: https://github.com/nifetency/nife-mcp-restapi#claude-desktop
        """
    )

    parser.add_argument(
        "--base-url",
        metavar="URL",
        help="REST API base URL (overrides REST_API_BASE_URL env var)"
    )
    parser.add_argument(
        "--spec-url",
        metavar="URL",
        help="OpenAPI/Swagger spec URL or file path (overrides OPENAPI_SPEC_URL env var)"
    )
    parser.add_argument(
        "--token",
        metavar="TOKEN",
        help="API access token for bearer authentication (overrides API_ACCESS_TOKEN env var)"
    )
    parser.add_argument(
        "--auth-type",
        choices=["bearer", "apikey", "basic", "none"],
        default=None,
        help="Authentication type (overrides AUTH_TYPE env var)"
    )
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default=None,
        help="Server mode: 'stdio' for MCP clients (default), 'http' for Docker/server deployments (overrides MCP_MODE env var)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        metavar="PORT",
        help="HTTP server port, only used when --mode=http (default: 8080, overrides MCP_SERVER_PORT env var)"
    )
    parser.add_argument(
        "--host",
        default=None,
        metavar="HOST",
        help="HTTP server host, only used when --mode=http (default: 0.0.0.0, overrides MCP_SERVER_HOST env var)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        metavar="LEVEL",
        help="Logging level (default: INFO, overrides LOG_LEVEL env var)"
    )
    parser.add_argument(
        "--env-file",
        default=None,
        metavar="PATH",
        help="Path to a custom .env file (default: looks for .env in current directory)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    return parser.parse_args()


async def main():
    args = parse_args()

    # Load .env file first (lowest priority — CLI args and real env vars override it)
    if args.env_file:
        if not os.path.exists(args.env_file):
            print(f"[ERROR] --env-file not found: {args.env_file}", file=sys.stderr)
            sys.exit(1)
        load_dotenv(dotenv_path=args.env_file, override=False)
    else:
        load_dotenv(override=False)  # loads .env from cwd if present, won't override real env vars

    # Apply CLI args into environment (they take highest priority)
    if args.base_url:
        os.environ["REST_API_BASE_URL"] = args.base_url

    if args.spec_url:
        os.environ["OPENAPI_SPEC_URL"] = args.spec_url

    if args.token:
        os.environ["API_ACCESS_TOKEN"] = args.token

    if args.auth_type:
        os.environ["AUTH_TYPE"] = args.auth_type

    if args.mode:
        os.environ["MCP_MODE"] = args.mode

    if args.port is not None:
        os.environ["MCP_SERVER_PORT"] = str(args.port)

    if args.host:
        os.environ["MCP_SERVER_HOST"] = args.host

    if args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level

    # Validate required config
    if not os.environ.get("REST_API_BASE_URL"):
        print(
            "[ERROR] REST API base URL not configured.\n"
            "\n"
            "Set it using one of these methods:\n"
            "  1. CLI arg:    restapi-mcp-server --base-url https://api.example.com\n"
            "  2. Env var:    export REST_API_BASE_URL=https://api.example.com\n"
            "  3. .env file:  echo 'REST_API_BASE_URL=https://api.example.com' > .env\n"
            "  4. Claude Desktop config: add REST_API_BASE_URL to the 'env' block\n",
            file=sys.stderr
        )
        sys.exit(1)

    if not os.environ.get("OPENAPI_SPEC_URL"):
        print(
            "[ERROR] OpenAPI spec URL not configured.\n"
            "\n"
            "Set it using one of these methods:\n"
            "  1. CLI arg:    restapi-mcp-server --spec-url https://api.example.com/openapi.json\n"
            "  2. Env var:    export OPENAPI_SPEC_URL=https://api.example.com/openapi.json\n"
            "  3. .env file:  echo 'OPENAPI_SPEC_URL=https://api.example.com/openapi.json' > .env\n"
            "  4. Claude Desktop config: add OPENAPI_SPEC_URL to the 'env' block\n",
            file=sys.stderr
        )
        sys.exit(1)

    # Now import and run the server (imports after env setup so config is ready)
    from restapi_mcp_server.server import RestApiMCPServer
    server = RestApiMCPServer()
    await server.run()


def main_sync():
    """Synchronous entry point for the CLI script registered in pyproject.toml"""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
