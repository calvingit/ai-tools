#!/usr/bin/env python3
"""
更新 Skills 脚本

该脚本用于维护和更新项目中的 Skills。它从 README.md 文件中读取 "开源 Skills" 列表，
自动检查远程仓库的最新提交，下载并更新本地的 Skills 目录。

主要功能：
1. 解析 README.md 获取 Skills 列表。
2. 检查 GitHub 仓库的最新 commit hash。
3. 下载并缓存仓库快照 (tar.gz)。
4. 提取 Skill 源码并安装到 skills/ 目录。
5. 更新 scripts/skills-list.json 记录版本信息。
"""

import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

# 项目根目录路径
ROOT_DIR = Path(__file__).resolve().parent.parent
# README 文件路径，作为 Skills 列表的数据源
README_PATH = ROOT_DIR / "README.md"
# 输出的 Skills 版本记录文件
OUTPUT_PATH = ROOT_DIR / "scripts" / "skills-list.json"
# 缓存下载的仓库文件
CACHE_DIR = ROOT_DIR / ".cache"
# 最终 Skills 安装的目标目录
TARGET_SKILLS_DIR = ROOT_DIR / "skills"


def to_repo_url(url: str) -> str:
    """
    标准化 GitHub 仓库 URL。

    Args:
        url: 原始 URL (例如 https://github.com/owner/repo.git)

    Returns:
        标准化后的 URL (https://github.com/owner/repo)
    """
    match = re.match(r"^https?://github\.com/([^/]+)/([^/]+)", url.strip())
    if not match:
        return url.strip().rstrip("/")
    owner, repo = match.group(1), match.group(2)
    repo = repo.removesuffix(".git")
    return f"https://github.com/{owner}/{repo}"


def extract_owner_repo(repo_url: str) -> tuple[str, str]:
    """
    从 GitHub URL 中提取 Owner 和 Repo 名称。

    Raises:
        ValueError: 如果 URL 格式不正确。
    """
    cleaned = repo_url.strip().removesuffix("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    if not cleaned.startswith("https://github.com/"):
        raise ValueError(f"不支持的仓库地址: {repo_url}")
    parts = cleaned.split("/")
    if len(parts) < 5:
        raise ValueError(f"仓库地址不完整: {repo_url}")
    return parts[3], parts[4]


def get_latest_commit(repo_url: str) -> str:
    """
    获取远程仓库的最新 Commit Hash (HEAD)。
    使用 git ls-remote 避免下载整个仓库历史。
    """
    repo_git_url = repo_url.rstrip("/") + ".git"
    result = subprocess.run(
        ["git", "ls-remote", repo_git_url, "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    # 输出格式通常为: <hash>\tHEAD
    line = result.stdout.strip().splitlines()[0]
    commit = line.split()[0].strip()
    if not commit:
        raise RuntimeError(f"获取提交失败: {repo_url}")
    return commit


def ensure_repo_cached(repo_url: str, commit: str) -> Path:
    """
    确保指定版本的仓库已被下载并缓存。

    如果缓存不存在，会从 GitHub 下载 tar.gz 归档并解压。

    Args:
        repo_url: 仓库 URL
        commit: 提交 Hash

    Returns:
        缓存的仓库根目录路径
    """
    owner, repo_name = extract_owner_repo(repo_url)
    cache_repo_dir = CACHE_DIR / f"{repo_name}-{commit}"

    # 如果已有缓存，直接返回
    if cache_repo_dir.exists():
        return cache_repo_dir

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tarball_url = f"https://codeload.github.com/{owner}/{repo_name}/tar.gz/{commit}"

    # 使用临时目录进行下载和解压，确保原子性
    with tempfile.TemporaryDirectory(prefix=f"{repo_name}-{commit[:7]}-", dir=CACHE_DIR) as tmp:
        tmp_dir = Path(tmp)
        archive_path = tmp_dir / "repo.tar.gz"

        # 下载 tarball
        with urllib.request.urlopen(tarball_url) as resp:
            archive_path.write_bytes(resp.read())

        extract_dir = tmp_dir / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)

        # 解压
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)

        # 找到解压后的根目录（GitHub tarball 通常包含一层目录）
        extracted_roots = [p for p in extract_dir.iterdir() if p.is_dir()]
        if not extracted_roots:
            raise RuntimeError(f"解压后未找到目录: {repo_url}@{commit}")

        # 移动到最终缓存位置
        shutil.move(str(extracted_roots[0]), str(cache_repo_dir))

    return cache_repo_dir


def find_skill_source_dir(repo_dir: Path, skill_name: str) -> Path | None:
    """
    在仓库中查找 Skill 的源文件目录。

    查找策略：
    1. 查找 repo/skills/{skill_name} 目录。
    2. 如果不存在，查找 repo/SKILL.md（单 Skill 仓库模式）。
       如果是单 Skill 仓库，会创建一个临时目录包含该 SKILL.md。
    """
    # 策略 1: 标准 skills 目录结构
    for skills_dir in repo_dir.rglob("skills"):
        if not skills_dir.is_dir():
            continue
        candidate = skills_dir / skill_name
        if candidate.is_dir():
            return candidate

    # 策略 2: 根目录 SKILL.md (单 Skill 仓库)
    root_skill_md = repo_dir / "SKILL.md"
    if root_skill_md.is_file():
        temp_skill_dir = CACHE_DIR / f"__skill_temp_{skill_name}"
        if temp_skill_dir.exists():
            shutil.rmtree(temp_skill_dir)
        temp_skill_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root_skill_md, temp_skill_dir / "SKILL.md")
        return temp_skill_dir

    return None


def copy_skill_to_target(skill_name: str, source_dir: Path) -> None:
    """
    将 Skill 安装到目标目录。
    会完全替换目标目录中的同名 Skill。
    """
    destination = TARGET_SKILLS_DIR / skill_name
    if destination.exists():
        shutil.rmtree(destination)
    TARGET_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, destination)


def extract_skills(content: str) -> dict[str, dict[str, str]]:
    """
    从 README.md 内容中解析 Skill 列表。

    查找 "### 开源 Skills" 章节下的列表项。
    格式: - [SkillName](RepoURL)
    """
    section_match = re.search(
        r"###\s*开源 Skills\s*(.*?)(?:\n###\s+|\Z)",
        content,
        flags=re.S,
    )
    skills: dict[str, dict[str, str]] = {}
    if not section_match:
        return skills

    section_text = section_match.group(1)
    for name, url in re.findall(
        r"-\s*\[([^\]]+)\]\((https?://[^)]+)\)",
        section_text,
    ):
        skills[name.strip()] = {
            "repo": to_repo_url(url),
            "commit": "", # 初始 commit 为空，后续合并或获取
        }
    return skills


def load_existing_skills(path: Path) -> dict[str, dict[str, str]]:
    """读取已保存的 skills-list.json，用于获取上次更新的 commit hash。"""
    if not path.exists():
        return {}
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(existing, dict):
        return {}

    normalized: dict[str, dict[str, str]] = {}
    for name, item in existing.items():
        if not isinstance(name, str) or not isinstance(item, dict):
            continue
        repo = str(item.get("repo", "")).strip()
        commit = str(item.get("commit", "")).strip()
        normalized[name.strip()] = {"repo": repo, "commit": commit}
    return normalized


def merge_skills(
    extracted: dict[str, dict[str, str]],
    existing: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    """
    合并提取的 Skills 和现有的 Skills。

    如果 Repo URL 未变，则保留现有的 Commit Hash (避免不必要的更新检测)。
    如果 Repo URL 变了，或者现有记录为空，则 Commit 置空 (将触发更新)。
    """
    merged: dict[str, dict[str, str]] = {}
    for name, new_item in extracted.items():
        new_repo = str(new_item.get("repo", "")).strip()
        new_commit = str(new_item.get("commit", "")).strip()

        old_item = existing.get(name, {})
        old_repo = str(old_item.get("repo", "")).strip() if isinstance(old_item, dict) else ""
        old_commit = str(old_item.get("commit", "")).strip() if isinstance(old_item, dict) else ""

        # 逻辑：保留旧的 commit，除非 repo 地址变了
        if old_repo and old_repo != new_repo:
            merged_commit = ""
        elif new_commit and (old_commit == "" or old_commit != new_commit):
            merged_commit = new_commit
        else:
            merged_commit = old_commit

        merged[name] = {
            "repo": new_repo,
            "commit": merged_commit,
        }
    return merged


def install_skills(skills: dict[str, dict[str, str]]) -> None:
    """
    批量安装/更新 Skills。

    1. 获取每个仓库的最新 Commit。
    2. 下载并缓存仓库。
    3. 提取 Skill 并复制到目标目录。
    """
    repo_latest_commit: dict[str, str] = {}
    repo_cached_dir: dict[str, Path] = {}

    # 阶段 1: 准备仓库数据 (去重处理)
    for info in skills.values():
        repo = info["repo"]
        if repo in repo_latest_commit:
            continue
        # 获取远程最新 commit
        commit = get_latest_commit(repo)
        repo_latest_commit[repo] = commit
        # 确保仓库已下载缓存
        repo_cached_dir[repo] = ensure_repo_cached(repo, commit)

    # 阶段 2: 安装每个 Skill
    for skill_name, info in skills.items():
        repo = info["repo"]
        latest_commit = repo_latest_commit[repo]

        # 更新 info 中的 commit 信息，以便后续保存
        info["commit"] = latest_commit

        source_dir = find_skill_source_dir(repo_cached_dir[repo], skill_name)
        if source_dir is None:
            raise RuntimeError(f"未找到 skill 目录或 SKILL.md: {skill_name} ({repo})")

        copy_skill_to_target(skill_name, source_dir)


def main() -> None:
    content = README_PATH.read_text(encoding="utf-8")

    # 1. 提取 README 中的配置
    extracted_skills = extract_skills(content)

    # 2. 加载旧配置
    existing_skills = load_existing_skills(OUTPUT_PATH)

    # 3. 合并配置
    skills = merge_skills(extracted_skills, existing_skills)

    # 4. 执行安装
    install_skills(skills)

    # 5. 保存新的状态
    OUTPUT_PATH.write_text(
        json.dumps(skills, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Skills 列表与安装已完成: {OUTPUT_PATH} -> {TARGET_SKILLS_DIR}")


if __name__ == "__main__":
    main()
