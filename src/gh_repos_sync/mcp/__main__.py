# Entry point: `python -m gh_repos_sync.mcp` starts the MCP server over stdio.

from .server import main


if __name__ == "__main__":
    main()
