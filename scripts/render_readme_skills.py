#!/usr/bin/env python3

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT_DIR / "index.json"
README_PATH = ROOT_DIR / "README.md"
START_MARKER = "SKILLS_LIST_START"
END_MARKER = "SKILLS_LIST_END"


def load_index(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"未找到技能索引文件: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_skills_block(index_data: dict) -> list[str]:
    categories = index_data.get("categories", [])
    if not isinstance(categories, list):
        raise ValueError("技能索引格式错误: categories 应为数组")
    lines: list[str] = [
        ">（以下内容由 scripts/render_readme_skills.py 生成，请勿手改）",
        "",
    ]
    for category in categories:
        if not isinstance(category, dict):
            raise ValueError("技能索引格式错误: category 应为对象")
        name = str(category.get("name", "")).strip()
        items = category.get("items", [])
        if not name or not isinstance(items, list):
            raise ValueError("技能索引格式错误: category.name 或 items 无效")
        lines.append(f"#### {name}")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("技能索引格式错误: item 应为对象")
            skill_id = str(item.get("id", "")).strip()
            url = str(item.get("url", "")).strip()
            desc = str(item.get("desc", "")).strip()
            if not skill_id or not url:
                raise ValueError("技能索引格式错误: item.id 或 item.url 为空")
            if desc:
                lines.append(f"- [{skill_id}]({url})：{desc}")
            else:
                lines.append(f"- [{skill_id}]({url})")
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    return lines


def find_marker_line(lines: list[str], marker: str) -> tuple[int, str]:
    for idx, line in enumerate(lines):
        if marker in line:
            return idx, line
    raise ValueError("README 未包含技能列表标记")


def replace_block(readme_text: str, block_lines: list[str]) -> str:
    lines = readme_text.splitlines()
    start_idx, start_line = find_marker_line(lines, START_MARKER)
    end_idx, end_line = find_marker_line(lines, END_MARKER)
    if start_idx >= end_idx:
        raise ValueError("README 技能列表标记顺序错误")
    new_lines = (
        lines[:start_idx]
        + [start_line]
        + block_lines
        + [end_line]
        + lines[end_idx + 1 :]
    )
    return "\n".join(new_lines).rstrip() + "\n"


def main() -> None:
    index_data = load_index(INDEX_PATH)
    block_lines = build_skills_block(index_data)
    readme_text = README_PATH.read_text(encoding="utf-8")
    updated = replace_block(readme_text, block_lines)
    README_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
