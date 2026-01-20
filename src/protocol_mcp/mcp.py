from fastmcp import FastMCP

mcp: FastMCP = FastMCP(
    name="protocol-mcp",
    instructions="MCP that connects to wetlab protocol resources, including protocols.io",
    on_duplicate_tools="error",
)
