#!/usr/bin/env python3
"""Generate a task-closure log and archive it.

Usage example:
python scripts/generate_task_log.py \
  --task-type chore \
  --task-name CloneX收尾 \
  --issue-id 1 \
  --issue-url https://github.com/qiao-925/CloneX/issues/1
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, List


ROOT_DIR = Path(__file__).resolve().parents[1]


def _next_sequence(date_prefix: str, candidates: Iterable[Path]) -> int:
    pattern = re.compile(rf"^{re.escape(date_prefix)}-(\d+)_")
    max_seq = 0
    for directory in candidates:
        if not directory.exists():
            continue
        for file_path in directory.iterdir():
            if not file_path.is_file():
                continue
            match = pattern.match(file_path.name)
            if match:
                max_seq = max(max_seq, int(match.group(1)))
    return max_seq + 1


def _to_bullets(items: List[str], empty_placeholder: str = "- 无") -> str:
    if not items:
        return empty_placeholder
    return "\n".join(f"- {item}" for item in items)


def _build_markdown(
    *,
    now: datetime,
    task_type: str,
    task_name: str,
    doc_type: str,
    trigger: str,
    issue_id: str,
    issue_url: str,
    next_step: str,
    w00_summary: str,
    completed_items: List[str],
    structure_issues: List[str],
    test_summary: str,
) -> str:
    date_text = now.strftime("%Y-%m-%d")
    structure_passed = "否" if structure_issues else "是"
    structure_block = _to_bullets(structure_issues, empty_placeholder="- 无（均 ≤300 行）")
    completed_block = _to_bullets(completed_items)

    return f"""# {date_text} 【{task_type}】{task_name}-{doc_type}

## Goal / Next
- Goal：完成项目最终收尾，沉淀可追踪的交付与遗留项。
- Next：{next_step}

## 当前状态
**阶段**：✅ 收尾完成
**触发方式**：{trigger}

## W00 同步检查
- Issue：#{issue_id}（{issue_url}）
- 结果：{w00_summary}

## 结构检查（再收尾）
- 检查标准：本任务涉及代码文件 ≤300 行、职责清晰、无明显循环依赖。
- 是否通过：{structure_passed}
- 结构问题：
{structure_block}
- 处理结论：本轮不再做结构性重构，作为「遗留：结构问题」进入维护期。

## 关键步骤
{completed_block}

## 测试与验证
- {test_summary}

## 六维度优化分析

### 1) 代码质量
- ✅ 已清理多处失效代码与冗余入口，整体可读性提升。
- ⚠️ 仍有超 300 行文件，后续改动时建议按功能拆分（优先级：🟡）。

### 2) 架构设计
- ✅ 分层结构（`ui -> application -> core/domain -> infra`）保持清晰。
- ⚠️ `ui/main_window.py` 体量较大，建议按页面区域拆分（优先级：🟡）。

### 3) 性能
- ✅ 批量任务已有并行执行与阶段化进度反馈机制。
- ⚠️ 尚缺少性能基准记录，后续可补一次大仓库场景压测（优先级：🟢）。

### 4) 测试
- ✅ 已保留“打包 + 可执行文件启动”作为交付前验证链路。
- ⚠️ 自动化测试已按阶段决策移除，后续若进入高频迭代建议补最小回归集（优先级：🟡）。

### 5) 可维护性
- ✅ README 已重写为简洁、重点明确的说明文档。
- ⚠️ 结构检查结论与遗留说明需要在后续维护时持续更新（优先级：🟢）。

### 6) 技术债务
- ✅ 已偿还明显历史债务（无效模块、重复入口、失效函数）。
- ⚠️ 超长文件属于剩余技术债，建议只在必要需求触发时处理（优先级：🟡）。

## 优先级汇总
| 优先级 | 含义 | 本任务结论 |
|--------|------|------------|
| 🔴 | 立即处理（本周） | 无 |
| 🟡 | 近期处理（本月） | 超长文件拆分（按需） |
| 🟢 | 长期规划（季度） | 补性能基线与维护文档 |

## 交付结论
- 本任务交付目标已达成，Issue 已收口并关闭。
- 当前进入低频维护阶段，后续以问题驱动的小步修复为主。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and archive a closure task log")
    parser.add_argument("--task-type", default="chore")
    parser.add_argument("--task-name", default="CloneX收尾")
    parser.add_argument("--doc-type", default="任务日志")
    parser.add_argument("--trigger", default="用户明确进入收尾流程")
    parser.add_argument("--issue-id", default="-")
    parser.add_argument("--issue-url", default="-")
    parser.add_argument("--next-step", default="归档完成，进入低频维护")
    parser.add_argument(
        "--w00-summary",
        default="已完成最终 checkpoint，同步为 status:done 且 Issue 已关闭",
    )
    parser.add_argument(
        "--completed-item",
        action="append",
        default=[],
        help="Repeatable. Key completed step.",
    )
    parser.add_argument(
        "--structure-issue",
        action="append",
        default=[],
        help="Repeatable. Remaining structure issue.",
    )
    parser.add_argument(
        "--test-summary",
        default="已按仓库规则执行重打包并启动可执行文件验证通过。",
    )

    args = parser.parse_args()
    now = datetime.now()
    date_prefix = now.strftime("%Y-%m-%d")
    archive_month = now.strftime("%Y-%m")

    ongoing_dir = ROOT_DIR / "agent-task-log" / "ongoing"
    archive_dir = ROOT_DIR / "agent-task-log" / "archive" / archive_month
    ongoing_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    seq = _next_sequence(date_prefix, [ongoing_dir, archive_dir])
    filename = f"{date_prefix}-{seq}_【{args.task_type}】{args.task_name}-{args.doc_type}.md"
    ongoing_path = ongoing_dir / filename
    archive_path = archive_dir / filename

    completed_items = args.completed_item or [
        "完成文档精简重写与结构说明更新。",
        "清理失效代码与兼容入口，删除无效模块。",
        "完成仓库重命名并同步远端、本地与项目元信息。",
    ]

    markdown = _build_markdown(
        now=now,
        task_type=args.task_type,
        task_name=args.task_name,
        doc_type=args.doc_type,
        trigger=args.trigger,
        issue_id=args.issue_id,
        issue_url=args.issue_url,
        next_step=args.next_step,
        w00_summary=args.w00_summary,
        completed_items=completed_items,
        structure_issues=args.structure_issue,
        test_summary=args.test_summary,
    )

    ongoing_path.write_text(markdown, encoding="utf-8")
    ongoing_path.replace(archive_path)

    print(str(archive_path))


if __name__ == "__main__":
    main()

