from mcp.server import MCPServer

mcp = MCPServer("Demo")

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"