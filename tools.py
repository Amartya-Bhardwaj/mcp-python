# tools.py
from fastmcp import FastMCP
from main1 import summarize_youtube_fn

mcp = FastMCP("Demo 🚀")

@mcp.tool
def summarize_youtube(query: str) -> str:
    """MCP tool wrapper — calls the plain function."""
    # Use default max_results inside MCP
    return summarize_youtube_fn(query, max_results=3)

@mcp.tool
def greet_tool(name: str):
    return f"Hello {name}! 👋"
