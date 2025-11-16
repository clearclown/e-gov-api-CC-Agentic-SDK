"""MCP Server for Japanese Legal Information Tools

This MCP server provides tools for searching and analyzing Japanese laws and court precedents.
Uses Claude Agent SDK with TOON format for optimal token efficiency.

Usage:
    python -m app.mcp.legal_server
"""

import asyncio
import logging
from typing import Optional

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    Server = None

from app.mcp.legal_tools import (
    search_law,
    search_case,
    analyze_law_case_relationship,
    get_law_detail,
    get_case_detail,
    ask_legal_question,
    LEGAL_TOOLS,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalMCPServer:
    """MCP Server for Japanese Legal Information

    Provides 6 tools for legal search and analysis:
    - search_law: Search Japanese laws
    - search_case: Search court precedents
    - analyze_law_case_relationship: Analyze law-case relationships
    - get_law_detail: Get detailed law information
    - get_case_detail: Get detailed case information
    - ask_legal_question: Natural language legal Q&A
    """

    def __init__(self):
        """Initialize the MCP server"""
        if not SDK_AVAILABLE:
            raise ImportError(
                "MCP SDK not available. Install with: uv pip install mcp"
            )

        self.name = "legal_tools"
        self._name = "legal_tools"  # Alias for compatibility
        self.description = "日本の法令・判例検索および分析ツール - Japanese legal information search and analysis tools"
        self.version = "1.0.0"

        # Create server instance
        self.server = Server(self.name)

        # Register tool handlers
        self._register_handlers()

        logger.info(f"Legal MCP Server initialized: {self.name} v{self.version}")
        logger.info(f"Registered {len(LEGAL_TOOLS)} tools")

    def _register_handlers(self):
        """Register all tool handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools"""
            tools = []
            for tool_def in LEGAL_TOOLS:
                tools.append(Tool(
                    name=tool_def["name"],
                    description=tool_def["description"],
                    inputSchema=tool_def["input_schema"]
                ))
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Call a tool by name"""
            logger.info(f"Calling tool: {name} with args: {arguments}")

            # Map tool names to functions
            tool_map = {
                "search_law": search_law,
                "search_case": search_case,
                "analyze_law_case_relationship": analyze_law_case_relationship,
                "get_law_detail": get_law_detail,
                "get_case_detail": get_case_detail,
                "ask_legal_question": ask_legal_question,
            }

            if name not in tool_map:
                raise ValueError(f"Unknown tool: {name}")

            # Execute tool
            try:
                result = await tool_map[name](arguments)

                # Convert result to TextContent format
                if "content" in result:
                    return [
                        TextContent(
                            type="text",
                            text=item.get("text", str(item))
                        )
                        for item in result["content"]
                    ]
                else:
                    # Fallback for different result formats
                    return [TextContent(type="text", text=str(result))]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def run(self):
        """Run the MCP server"""
        logger.info(f"Starting {self.name} MCP server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# Create global server instance
if SDK_AVAILABLE:
    try:
        server = LegalMCPServer()
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        server = None
else:
    logger.warning("MCP SDK not available - server not initialized")
    server = None


async def main():
    """Main entry point"""
    if server is None:
        print("Error: Server not initialized. Install dependencies with:")
        print("  uv pip install mcp")
        return 1

    try:
        await server.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
