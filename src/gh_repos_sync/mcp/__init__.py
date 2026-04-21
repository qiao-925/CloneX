# MCP adapter layer for CloneX.
#
# Exposes CloneX capabilities (list/classify/clone/pull/check) to any
# MCP-compatible agent (Claude Desktop, Cursor, Windsurf, ...).
# Runs as an independent process via `python -m gh_repos_sync.mcp` and reuses
# the same keyring / config files the GUI uses.

__all__ = []
