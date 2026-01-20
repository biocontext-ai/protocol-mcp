# Agent Instructions

## Package Management

Always use `uv` for package management, not pip:

```bash
# Install dependencies
uv sync

# Install with test dependencies
uv sync --extra test

# Run tests
uv run pytest

# Run the server
uv run protocol_mcp
```
