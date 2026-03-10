#!/usr/bin/env python3
"""Skills 安装脚本：封装 npx skills add。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "index.json"
SKILLS_ROOT = ROOT / "skills"


def load_categories(root: Path) -> list[str]:
    index_path = root / "index.json"
    if not index_path.is_file():
        raise ValueError(f"未找到 index.json: {index_path}")

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    categories = payload.get("categories", [])
    if not isinstance(categories, list):
        raise ValueError("index.json 格式错误: categories 必须是数组")

    names: list[str] = []
    for item in categories:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            names.append(name.strip())

    if not names:
        raise ValueError("index.json 中未找到可用分类")
    return names


def category_path(root: Path, category: str) -> Path:
    return root / "skills" / category


def list_units(root: Path, category: str) -> dict[str, str]:
    cat_dir = category_path(root, category)
    if not cat_dir.is_dir():
        raise ValueError(f"分类目录不存在: {cat_dir}")

    units: dict[str, str] = {}
    for child in sorted(cat_dir.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        unit_type = "skill" if (child / "SKILL.md").is_file() else "bundle"
        units[child.name] = unit_type

    if not units:
        raise ValueError(f"分类 {category} 下未找到可安装单元")
    return units


def build_install_command(source: Path, global_install: bool, agents: list[str]) -> list[str]:
    cmd: list[str] = ["npx", "skills", "add", str(source)]
    if global_install:
        cmd.append("-g")
    for agent in agents:
        cmd.extend(["-a", agent])
    cmd.append("-y")
    return cmd


def build_install_plan(
    *,
    root: Path,
    categories: list[str],
    category: str,
    units: list[str],
    global_install: bool,
    agents: list[str],
) -> list[dict[str, object]]:
    if category == "all" and units:
        raise ValueError("--category all 不能与 --unit 同时使用")

    if category != "all" and category not in categories:
        raise ValueError(
            f"无效分类: {category}。可选分类: {', '.join(categories)}"
        )

    plan: list[dict[str, object]] = []

    if category == "all":
        targets = categories
    else:
        targets = [category]

    for cat in targets:
        cat_dir = category_path(root, cat)
        if not cat_dir.is_dir():
            raise ValueError(f"分类目录不存在: {cat_dir}")

        if category != "all" and units:
            available = list_units(root, cat)
            missing = [u for u in units if u not in available]
            if missing:
                raise ValueError(
                    f"分类 {cat} 不存在单元: {', '.join(missing)}。"
                    f"可选单元: {', '.join(available.keys())}"
                )
            for unit in units:
                source = cat_dir / unit
                plan.append(
                    {
                        "category": cat,
                        "unit": unit,
                        "unit_type": available[unit],
                        "source": source,
                        "cmd": build_install_command(source, global_install, agents),
                    }
                )
        else:
            plan.append(
                {
                    "category": cat,
                    "unit": None,
                    "unit_type": None,
                    "source": cat_dir,
                    "cmd": build_install_command(cat_dir, global_install, agents),
                }
            )

    return plan


def ensure_npx_available() -> None:
    try:
        subprocess.run(
            ["npx", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError("未检测到可用的 npx，请先安装 Node.js/npm") from exc


def execute_plan(plan: list[dict[str, object]]) -> None:
    for step in plan:
        cat = str(step["category"])
        unit = step["unit"]
        unit_type = step["unit_type"]
        cmd = step["cmd"]

        if unit is None:
            print(f"[INFO] 安装分类: {cat}")
        else:
            print(f"[INFO] 安装单元: {cat}/{unit} ({unit_type})")
        print(f"[CMD] {' '.join(str(x) for x in cmd)}")

        subprocess.run(cmd, check=True)


def ask_choice(prompt: str, options: list[str]) -> str:
    while True:
        print(f"\n{prompt}")
        for idx, option in enumerate(options, start=1):
            print(f"  {idx}. {option}")

        selected = input("请输入编号: ").strip()
        if not selected.isdigit():
            print("输入无效，请输入数字编号。")
            continue
        pos = int(selected)
        if 1 <= pos <= len(options):
            return options[pos - 1]
        print("输入越界，请重新选择。")


def ask_units(category: str, units: dict[str, str]) -> list[str]:
    ordered = list(units.keys())
    print(f"\n分类 {category} 的可选单元:")
    for idx, unit in enumerate(ordered, start=1):
        print(f"  {idx}. {unit} ({units[unit]})")

    while True:
        raw = input("请输入要安装的编号（支持逗号分隔，如 1,3）: ").strip()
        if not raw:
            print("至少选择一个单元。")
            continue

        selected: list[str] = []
        seen: set[str] = set()
        valid = True
        for token in raw.split(","):
            token = token.strip()
            if not token.isdigit():
                valid = False
                break
            pos = int(token)
            if not (1 <= pos <= len(ordered)):
                valid = False
                break
            name = ordered[pos - 1]
            if name not in seen:
                selected.append(name)
                seen.add(name)

        if valid and selected:
            return selected
        print("选择格式错误，请重新输入。")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="安装本仓库 Skills 到 Agent（封装 npx skills add）",
    )
    parser.add_argument("legacy", nargs="*", help="兼容旧参数: <category>|all")
    parser.add_argument("--category", help="分类名或 all")
    parser.add_argument(
        "--unit",
        action="append",
        default=[],
        help="分类下单个安装单元（可重复）",
    )
    parser.add_argument("-g", "--global", dest="global_install", action="store_true")
    parser.add_argument("-a", "--agent", action="append", default=[])
    return parser.parse_args(argv)


def normalize_inputs(args: argparse.Namespace) -> tuple[str | None, list[str]]:
    category = args.category
    units = list(args.unit)

    if args.legacy:
        if category is not None:
            raise ValueError("不能同时使用位置参数和 --category")
        if len(args.legacy) > 1:
            raise ValueError("位置参数最多只能提供一个分类")
        category = args.legacy[0]

    return category, units


def normalize_agents(raw_agents: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw in raw_agents:
        for item in raw.split(","):
            agent = item.strip()
            if agent:
                normalized.append(agent)
    return normalized


def interactive_select(categories: list[str]) -> tuple[str, list[str]]:
    category = ask_choice("请选择要安装的分类", ["all", *categories])
    if category == "all":
        return category, []

    mode = ask_choice("请选择安装方式", ["install-all-units", "install-selected-units"])
    if mode == "install-all-units":
        return category, []

    units = list_units(ROOT, category)
    return category, ask_units(category, units)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    categories = load_categories(ROOT)

    category, units = normalize_inputs(args)
    agents = normalize_agents(list(args.agent))
    if category is None:
        category, units = interactive_select(categories)

    ensure_npx_available()
    plan = build_install_plan(
        root=ROOT,
        categories=categories,
        category=category,
        units=units,
        global_install=args.global_install,
        agents=agents,
    )
    execute_plan(plan)
    print("[INFO] 安装完成")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
