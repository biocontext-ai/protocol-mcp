from importlib.metadata import version

from protocol_mcp.main import run_app
from protocol_mcp.mcp import mcp

__version__ = version("protocol_mcp")

__all__ = ["mcp", "run_app", "__version__"]


if __name__ == "__main__":
    run_app()
