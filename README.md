# CloneX

> GitHub 多仓库批量维护工具 —— **桌面 GUI + MCP Server 双入口**

CloneX 提供仓库同步、分类管理、批量克隆/更新、失败重试能力。同一套业务核心同时面向**开发者**（PyQt6 GUI）与 **AI Agent**（MCP 协议）暴露，减少重复命令操作、提升多仓库日常维护效率。

## 核心功能

- **仓库同步与分类管理**：同步 GitHub 仓库列表，支持按语言自动分类、增量归档到 `未分类` 及手动维护。
- **批量执行与一致性校验**：按分组并行克隆并执行 `git fsck` 校验，支持已克隆仓库批量更新（`git pull --ff-only`）。
- **失败追踪与重试闭环**：自动记录失败任务清单，支持一键重试与执行结果回溯。
- **MCP Agent 接入**：将全部能力暴露为 **14 个 MCP 工具**，分为 A（查询）/ B（分组写入）/ C（单仓执行）/ C2（批量执行）/ D（高层流程）五组；mutating 工具默认 `dry_run=true`，错误统一以 `{ok, error, message}` 返回。

## Quick Start

### GUI

打包：

```bash
uv sync --group build
uv run pyinstaller --noconfirm --clean --onefile --windowed --name CloneX --paths src gui.py
```

启动：

- **Windows**：`.\dist\CloneX.exe`
- **Linux / macOS**：`chmod +x ./dist/CloneX && ./dist/CloneX`

### MCP Server

开发模式（仓库源码直跑）：

```bash
uv run --extra mcp python -m gh_repos_sync.mcp
```

客户端接入示例（Claude Desktop / Cursor / Windsurf）见 `docs/mcp_config_dev.json` 与 `docs/mcp_config_uvx.json`，完整使用与调试指南见 `docs/MCP-GUIDE.md`。

### 测试

```bash
uv run --group test pytest                         # ~50 cases in-memory 单测（~1 秒）
uv run --group test python scripts/mcp_smoke.py    # 真 keyring 凭据 + 真 GitHub API smoke
```

交互式调试（MCP Inspector）：

```bash
npx @modelcontextprotocol/inspector uv run --extra mcp python -m gh_repos_sync.mcp
```

## 文档

| 文档 | 用途 |
|------|------|
| `AGENTS.md` | Agent 协作规则（分层约束、重打包规则） |
| `docs/MCP-GUIDE.md` | MCP Server 使用、测试与调试三层策略 |
| `docs/BUILD.md` | 打包细节 |
| `docs/GIST-CONFIG-GUIDE.md` | Gist 云同步配置 |

## 项目结构

```text
.
├─ gui.py                           # GUI 启动入口
├─ AGENTS.md                        # Agent 协作规则
├─ docs/                            # 文档、MCP 客户端配置示例
├─ scripts/
│  ├─ inspect_ui.py                 # AT-SPI UI 自检脚本
│  ├─ monitor_github.py             # GitHub Actions 监控
│  ├─ mcp_smoke.py                  # MCP 端到端 smoke 测试
│  ├─ rebuild-run.ps1               # 一键重打包并运行（Windows）
│  └─ watch-rebuild-run.ps1         # 监听文件变化后重打包运行
├─ tests/
│  └─ mcp/                          # MCP 工具 in-memory 单测（~50 cases）
└─ src/
   └─ gh_repos_sync/
      ├─ ui/                        # 界面与交互层（GUI 入口）
      │  ├─ main_window.py          # 主窗口与主流程入口
      │  ├─ workers.py              # 后台任务线程
      │  ├─ auto_sync_dialog.py     # Gist 自动同步设置对话框
      │  ├─ gist_manager_dialog.py  # Gist 管理对话框
      │  ├─ theme.py                # 主题样式
      │  └─ chrome.py               # 窗口外观
      ├─ mcp/                       # MCP Server（Agent 入口）
      │  ├─ server.py               # 注册工具并启动 stdio
      │  ├─ app.py                  # FastMCP 单例
      │  ├─ context.py              # token / 路径共享助手
      │  ├─ errors.py               # 统一错误码与响应封装
      │  └─ tools/                  # A 查询 / B 分组写入 / C 单仓 / C2 批量 / D 流程
      ├─ application/               # 用例编排层
      │  ├─ local_generation.py     # 按语言规则分类流程
      │  └─ execution.py            # 克隆/更新执行流程
      ├─ core/                      # 核心能力层
      │  ├─ repo_config.py          # 分组文件读写与 Gist 同步
      │  ├─ clone.py                # 单仓库克隆
      │  ├─ pull.py                 # 单仓库更新
      │  ├─ parallel.py             # 并行任务调度
      │  ├─ check.py                # 仓库完整性校验
      │  ├─ failed_repos.py         # 失败仓库记录
      │  └─ process_control.py      # 执行过程控制
      ├─ domain/                    # 领域规则层
      │  ├─ models.py               # 领域模型
      │  └─ repo_groups.py          # 分组解析与渲染
      └─ infra/                     # 基础设施层
         ├─ auth.py                 # GitHub OAuth 授权
         ├─ github_api.py           # GitHub API 封装
         ├─ gist_config.py          # Gist 配置管理
         ├─ auto_gist_sync.py       # 自动 Gist 同步
         ├─ logger.py               # 日志
         └─ paths.py                # 运行路径
```

依赖方向：`ui / mcp → application → core / domain → infra`

## 依赖

- **Python** `>=3.10`
- **GUI**：`PyQt6`、`PyQt6-WebEngine`、`qt-material`
- **GitHub / 存储**：`pygithub`、`requests`、`keyring`、`chardet`
- **MCP**（可选，`uv sync --extra mcp`）：`mcp>=1.0`
- **打包**（`uv sync --group build`）：`pyinstaller`
- **测试**（`uv sync --group test`）：`pytest`、`anyio`、`mcp`
