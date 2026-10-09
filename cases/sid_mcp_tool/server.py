"""MCP server exposing one variant's get_customer tool over stdio.

Usage: CRM_TENANT=acme python cases/sid_mcp_tool/server.py fixed
The tenant comes from the server's own configuration, never from the model.
"""
import importlib.util
import os
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

variant = sys.argv[1] if len(sys.argv) > 1 else "fixed"
spec = importlib.util.spec_from_file_location(
    "tool", Path(__file__).parent / variant / "tool.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

mcp = MCPServer("crm")


@mcp.tool()
def get_customer(customer_id: str) -> dict:
    """Look up a customer record for the support agent."""
    return tool.get_customer(customer_id, os.environ.get("CRM_TENANT", ""))


if __name__ == "__main__":
    mcp.run()
