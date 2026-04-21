## 分层与依赖约束

  - 默认依赖方向遵循：`ui / mcp -> application -> core / domain -> infra`
  - `mcp` 应优先复用 `application` / `core` / `domain` / `infra`，不应复制一套业务实现
  - `ui` 负责交互与状态展示，不应长期承载复杂业务主流程
  - 多步骤业务动作优先沉淀到 `application/`
  - 外部系统接入优先收敛到 `infra/`
  - 分组语义、解析规则、渲染规则优先放在 `domain/`
  - 若一次改动改变了分层结构或依赖方向，应在 `README.md` 的"项目结构"一节同步说明

## 自动重打包与运行规则

  - 对仓库进行任何代码改动后（`src/`、`gui.py`、`main.py`、`*.spec`），必须自动执行：

```bash
uv sync --group build
uv run pyinstaller --noconfirm --clean --onefile --windowed --name CloneX --paths src gui.py
```

  - 根据当前操作系统决定执行

**Windows**

```powershell
.\dist\CloneX.exe
```

**Linux / macOS**

```bash
chmod +x ./dist/CloneX && ./dist/CloneX
```

  - 若只修改文档（如 `README.md`、`AGENTS.md`）可跳过
  - 若自动重打包失败，需返回错误原因并停止继续操作
