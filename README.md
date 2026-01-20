# protocol-mcp

[![BioContextAI - Registry](https://img.shields.io/badge/Registry-package?style=flat&label=BioContextAI&labelColor=%23fff&color=%233555a1&link=https%3A%2F%2Fbiocontext.ai%2Fregistry)](https://biocontext.ai/registry)
[![Tests][badge-tests]][tests]
[![Documentation][badge-docs]][documentation]

[badge-tests]: https://img.shields.io/github/actions/workflow/status/biocontext-ai/protocol-mcp/test.yaml?branch=main
[badge-docs]: https://img.shields.io/readthedocs/protocol-mcp

MCP that connects to wetlab protocol resources, including protocols.io

## Getting started

Please refer to the [documentation][],
in particular, the [API documentation][].

You can also find the project on [BioContextAI](https://biocontext.ai), the community-hub for biomedical MCP servers: [protocol-mcp on BioContextAI](https://biocontext.ai/registry/biocontext-ai/protocol-mcp).

## Installation

You need to have Python 3.10 or newer installed on your system.
If you don't have Python installed, we recommend installing [uv][].

There are several alternative options to install protocol-mcp:

### 1. Use `uvx` to run it immediately
After publication to PyPI:
```bash
uvx protocol_mcp
```

Or from a Git repository:

```bash
uvx git+https://github.com/biocontext-ai/protocol-mcp.git@main
```

### 2. Include it in one of various clients that supports the `mcp.json` standard

If your MCP server is published to PyPI, use the following configuration:

```json
{
  "mcpServers": {
    "protocol-mcp": {
      "command": "uvx",
      "args": ["protocol_mcp"]
    }
  }
}
```
In case the MCP server is not yet published to PyPI, use this configuration:

```json
{
  "mcpServers": {
    "protocol-mcp": {
      "command": "uvx",
      "args": ["git+https://github.com/biocontext-ai/protocol-mcp.git@main"]
    }
  }
}
```

For purely local development (e.g., in Cursor or VS Code), use the following configuration:

```json
{
  "mcpServers": {
    "protocol-mcp": {
      "command": "uvx",
      "args": [
        "--refresh",
        "--from",
        "path/to/repository",
        "protocol_mcp"
      ]
    }
  }
}
```

If you want to reuse and existing environment for local development, use the following configuration:

```json
{
  "mcpServers": {
    "protocol-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "path/to/repository", "protocol_mcp"]
    }
  }
}
```

### 3. Install it through `pip`:

```bash
pip install --user protocol_mcp
```

### 4. Install the latest development version:

```bash
pip install git+https://github.com/biocontext-ai/protocol-mcp.git@main
```

## Contact

If you found a bug, please use the [issue tracker][].

## Citation

> t.b.a

[uv]: https://github.com/astral-sh/uv
[issue tracker]: https://github.com/biocontext-ai/protocol-mcp/issues
[tests]: https://github.com/biocontext-ai/protocol-mcp/actions/workflows/test.yaml
[documentation]: https://protocol-mcp.readthedocs.io
[changelog]: https://protocol-mcp.readthedocs.io/en/latest/changelog.html
[api documentation]: https://protocol-mcp.readthedocs.io/en/latest/api.html
[pypi]: https://pypi.org/project/protocol-mcp
