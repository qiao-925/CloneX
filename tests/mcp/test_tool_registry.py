# Goalkeeper tests: verify the 14 CloneX MCP tools are correctly registered
# with non-empty descriptions, valid input schemas, and safe default values
# (dry_run defaults to True on every write/execute path).
#
# If any tool is renamed, removed, or its safety defaults are silently flipped,
# these tests fail fast before the change ever reaches a real MCP client.

from __future__ import annotations

import pytest

pytestmark = pytest.mark.anyio


EXPECTED_TOOLS: set[str] = {
    # A. read-only queries
    "list_repos",
    "read_groups",
    "list_failed",
    "get_auth_status",
    # B. group-file writer
    "write_groups",
    # C. single-repo execution
    "clone_repo",
    "pull_repo",
    "check_repo",
    # C2. arbitrary-list batch
    "clone_repos_batch",
    "pull_repos_batch",
    "check_repos_batch",
    # D. high-level flows
    "clone_group",
    "update_all",
    "retry_failed",
}

# Tools that mutate local disk or remote state and MUST default to dry_run=True.
TOOLS_WITH_DRY_RUN_DEFAULT_TRUE: set[str] = {
    "write_groups",
    "clone_repo",
    "pull_repo",
    "clone_repos_batch",
    "pull_repos_batch",
    "clone_group",
    "update_all",
    "retry_failed",
}


async def test_all_fourteen_tools_are_registered(mcp_client):
    result = await mcp_client.list_tools()
    registered = {tool.name for tool in result.tools}
    missing = EXPECTED_TOOLS - registered
    extra = registered - EXPECTED_TOOLS
    assert not missing, f"missing tools: {missing}"
    assert not extra, f"unexpected tools: {extra}"
    assert len(registered) == 14


async def test_every_tool_has_non_empty_description(mcp_client):
    result = await mcp_client.list_tools()
    for tool in result.tools:
        assert tool.description and tool.description.strip(), (
            f"tool {tool.name} has empty description"
        )


async def test_every_tool_has_valid_input_schema(mcp_client):
    result = await mcp_client.list_tools()
    for tool in result.tools:
        schema = tool.inputSchema
        assert isinstance(schema, dict), f"{tool.name} schema is not a dict"
        assert schema.get("type") == "object", (
            f"{tool.name} schema.type should be 'object', got {schema.get('type')!r}"
        )
        # FastMCP always generates `properties` (possibly empty).
        assert "properties" in schema, f"{tool.name} schema missing `properties`"


async def test_write_and_execute_tools_default_to_dry_run_true(mcp_client):
    """Every mutating tool must default dry_run=true so an agent can't accidentally
    trigger real side effects just by calling the tool without arguments."""
    result = await mcp_client.list_tools()
    by_name = {tool.name: tool for tool in result.tools}

    for tool_name in TOOLS_WITH_DRY_RUN_DEFAULT_TRUE:
        schema = by_name[tool_name].inputSchema
        properties = schema.get("properties", {})
        assert "dry_run" in properties, f"{tool_name} does not expose a `dry_run` parameter"
        dry_run_default = properties["dry_run"].get("default")
        assert dry_run_default is True, (
            f"{tool_name}.dry_run default must be True for safety, got {dry_run_default!r}"
        )


async def test_check_tools_do_not_expose_dry_run(mcp_client):
    """check_repo / check_repos_batch are read-only (git fsck); exposing a dry_run
    flag would be misleading. Guard against drift."""
    result = await mcp_client.list_tools()
    by_name = {tool.name: tool for tool in result.tools}

    for tool_name in ("check_repo", "check_repos_batch"):
        properties = by_name[tool_name].inputSchema.get("properties", {})
        assert "dry_run" not in properties, (
            f"{tool_name} should not expose dry_run (it's read-only)"
        )


async def test_clone_repo_requires_owner_and_repo(mcp_client):
    result = await mcp_client.list_tools()
    schema = next(tool for tool in result.tools if tool.name == "clone_repo").inputSchema
    required = set(schema.get("required", []))
    assert {"owner", "repo"}.issubset(required), (
        f"clone_repo should require owner and repo, got required={required}"
    )


async def test_clone_group_requires_group_name(mcp_client):
    result = await mcp_client.list_tools()
    schema = next(tool for tool in result.tools if tool.name == "clone_group").inputSchema
    required = set(schema.get("required", []))
    assert "group_name" in required, (
        f"clone_group should require group_name, got required={required}"
    )


async def test_batch_tools_require_tasks(mcp_client):
    result = await mcp_client.list_tools()
    by_name = {tool.name: tool for tool in result.tools}
    for tool_name in ("clone_repos_batch", "pull_repos_batch", "check_repos_batch"):
        required = set(by_name[tool_name].inputSchema.get("required", []))
        assert "tasks" in required, f"{tool_name} should require `tasks`"
