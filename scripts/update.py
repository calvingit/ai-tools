#!/usr/bin/env python3

import json
import logging
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT_DIR / "index.json"
OUTPUT_PATH = ROOT_DIR / "scripts" / "skills-list.json"
CACHE_DIR = ROOT_DIR / ".cache"
TARGET_SKILLS_DIR = ROOT_DIR / "skills"
LOGGER = logging.getLogger("skills-updater")
RETRY_TIMES = 3
RETRY_WAIT_SECONDS = 2
TIMEZONE_SHANGHAI = ZoneInfo("Asia/Shanghai")


def parse_github_url(url: str) -> dict[str, str]:
    cleaned_url = url.strip().rstrip("/")
    match = re.match(
        r"^https?://github\.com/([^/]+)/([^/]+)(?:/tree/[^/]+(?:/(.*))?)?$",
        cleaned_url,
    )
    if not match:
        raise ValueError(f"不支持的 GitHub URL: {url}")
    owner = match.group(1).strip()
    repo = match.group(2).removesuffix(".git").strip()
    raw_path = (match.group(3) or "").strip().strip("/")
    path = raw_path if raw_path else "./"
    return {
        "owner": owner,
        "repo": repo,
        "repo_url": f"https://github.com/{owner}/{repo}",
        "path": path,
    }


def build_cache_dir_name(repo_url: str) -> str:
    parsed = parse_github_url(repo_url)
    return f"{parsed['owner']}-{parsed['repo']}".replace("/", "-")


def run_command(cmd: list[str], cwd: Path | None = None) -> str:
    last_error: Exception | None = None
    for attempt in range(1, RETRY_TIMES + 1):
        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            last_error = exc
            if attempt >= RETRY_TIMES:
                break
            LOGGER.warning(
                "命令失败，%s 秒后重试 (%s/%s): %s",
                RETRY_WAIT_SECONDS,
                attempt,
                RETRY_TIMES,
                " ".join(cmd),
            )
            time.sleep(RETRY_WAIT_SECONDS)
    if isinstance(last_error, subprocess.CalledProcessError):
        stderr = (last_error.stderr or "").strip()
        raise RuntimeError(f"命令执行失败: {' '.join(cmd)}\n{stderr}") from last_error
    raise RuntimeError(f"命令执行失败: {' '.join(cmd)}") from last_error


def ensure_repo_cached(repo_url: str) -> Path:
    cache_repo_dir = CACHE_DIR / build_cache_dir_name(repo_url)
    cache_repo_dir.parent.mkdir(parents=True, exist_ok=True)

    if cache_repo_dir.exists() and any(cache_repo_dir.iterdir()):
        if (cache_repo_dir / ".git").is_dir():
            LOGGER.info("检测到缓存仓库，执行拉取: %s", cache_repo_dir.name)
            run_command(["git", "-C", str(cache_repo_dir), "fetch", "--all", "--prune"])
            run_command(["git", "-C", str(cache_repo_dir), "pull", "--ff-only"])
        else:
            LOGGER.info("检测到非空缓存目录，跳过下载: %s", cache_repo_dir.name)
        return cache_repo_dir

    if cache_repo_dir.exists() and not any(cache_repo_dir.iterdir()):
        cache_repo_dir.rmdir()

    with tempfile.TemporaryDirectory(
        prefix=f"{cache_repo_dir.name}-tmp-",
        dir=CACHE_DIR,
    ) as tmp:
        tmp_dir = Path(tmp) / cache_repo_dir.name
        clone_url = repo_url.rstrip("/") + ".git"
        LOGGER.info("克隆仓库到缓存: %s", clone_url)
        run_command(["git", "clone", "--depth", "1", clone_url, str(tmp_dir)])
        if cache_repo_dir.exists():
            shutil.rmtree(cache_repo_dir)
        shutil.move(str(tmp_dir), str(cache_repo_dir))
    return cache_repo_dir


def get_repo_head_commit(repo_dir: Path) -> str:
    return run_command(["git", "-C", str(repo_dir), "rev-parse", "HEAD"])


def to_shanghai_time(date_text: str) -> str:
    dt = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
    return dt.astimezone(TIMEZONE_SHANGHAI).strftime("%Y-%m-%d %H:%M:%S")


def get_last_commit_for_path(repo_dir: Path, skill_path: str) -> tuple[str, str]:
    path_arg = "." if skill_path == "./" else skill_path.lstrip("./")
    output = run_command(
        [
            "git",
            "-C",
            str(repo_dir),
            "log",
            "-1",
            "--format=%H|%cI",
            "--",
            path_arg,
        ]
    )
    if not output:
        output = run_command(
            ["git", "-C", str(repo_dir), "log", "-1", "--format=%H|%cI"]
        )
    commit_id, commit_date = output.split("|", 1)
    return commit_id.strip(), to_shanghai_time(commit_date.strip())


def find_skill_source_dir(
    repo_dir: Path, skill_name: str, skill_path: str
) -> Path | None:
    if skill_path != "./":
        exact_path = repo_dir / skill_path.lstrip("./")
        if exact_path.is_dir():
            return exact_path
        if exact_path.is_file() and exact_path.name == "SKILL.md":
            return exact_path

    root_skills_dir = repo_dir / "skills"
    skills_dirs: list[Path] = []
    if root_skills_dir.is_dir():
        skills_dirs.append(root_skills_dir)

    nested_skills_dirs = [
        path
        for path in repo_dir.rglob("skills")
        if path.is_dir() and path != root_skills_dir
    ]
    nested_skills_dirs.sort(key=lambda p: (len(p.relative_to(repo_dir).parts), str(p)))
    skills_dirs.extend(nested_skills_dirs)

    for skills_dir in skills_dirs:
        candidate = skills_dir / skill_name
        if candidate.is_dir():
            return candidate

    if skills_dirs:
        return skills_dirs[0]

    root_skill_md = repo_dir / "SKILL.md"
    if root_skill_md.is_file():
        return root_skill_md

    return None


def copy_skill_to_target(skill_name: str, source_dir: Path, repo_root: Path) -> None:
    if source_dir.is_file() and source_dir.name == "SKILL.md":
        destination = TARGET_SKILLS_DIR / skill_name
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_dir, destination / "SKILL.md")
        for optional_dir_name in ("scripts", "references", "assets"):
            optional_dir = source_dir.parent / optional_dir_name
            if optional_dir.is_dir():
                shutil.copytree(optional_dir, destination / optional_dir_name)
        return

    is_skills_dir = source_dir.name == "skills"

    if is_skills_dir:
        destination = ROOT_DIR / skill_name
    else:
        destination = TARGET_SKILLS_DIR / skill_name

    if destination.exists():
        shutil.rmtree(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)

    ignore = shutil.ignore_patterns(
        ".DS_Store",
        "__pycache__",
        "*.pyc",
    )

    shutil.copytree(source_dir, destination, ignore=ignore)


def cleanup_cache_dirs(valid_cache_dir_names: set[str]) -> None:
    if not CACHE_DIR.exists():
        return
    for entry in CACHE_DIR.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("__skill_temp_") or "-tmp-" in entry.name:
            shutil.rmtree(entry)
            continue
        if entry.name not in valid_cache_dir_names:
            LOGGER.info("清理旧缓存目录: %s", entry.name)
            shutil.rmtree(entry)


def load_index_skills(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"未找到技能索引文件: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    categories = raw.get("categories", [])
    if not isinstance(categories, list):
        raise ValueError("技能索引格式错误: categories 应为数组")

    skills: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    for category in categories:
        if not isinstance(category, dict):
            errors.append("技能索引格式错误: category 应为对象")
            continue
        items = category.get("items", [])
        if not isinstance(items, list):
            errors.append("技能索引格式错误: category.items 应为数组")
            continue
        for item in items:
            if not isinstance(item, dict):
                errors.append("技能索引格式错误: item 应为对象")
                continue
            name = str(item.get("id", "")).strip()
            url = str(item.get("url", "")).strip()
            if not name or not url:
                errors.append("技能索引格式错误: item.id 或 item.url 为空")
                continue
            if name in skills:
                errors.append(f"技能索引格式错误: 重复的技能 id {name}")
                continue
            try:
                parsed = parse_github_url(url)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            skills[name] = {
                "repo": parsed["repo_url"],
                "path": parsed["path"],
                "commit": "",
                "lastUpdate": "",
                "lastCommitId": "",
            }

    if errors:
        raise ValueError("\n".join(errors))
    return skills


def load_existing_skills(path: Path) -> dict[str, dict[str, str]]:
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
        skill_path = str(item.get("path", "")).strip() or "./"
        last_update = str(item.get("lastUpdate", "")).strip()
        last_commit_id = str(item.get("lastCommitId", "")).strip()
        normalized[name.strip()] = {
            "repo": repo,
            "path": skill_path,
            "commit": commit,
            "lastUpdate": last_update,
            "lastCommitId": last_commit_id,
        }
    return normalized


def merge_skills(
    extracted: dict[str, dict[str, str]],
    existing: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for name, new_item in extracted.items():
        new_repo = str(new_item.get("repo", "")).strip()
        new_path = str(new_item.get("path", "")).strip() or "./"
        new_commit = str(new_item.get("commit", "")).strip()

        old_item = existing.get(name, {})
        old_repo = str(old_item.get("repo", "")).strip() if isinstance(old_item, dict) else ""
        old_path = (
            str(old_item.get("path", "")).strip()
            if isinstance(old_item, dict)
            else "./"
        )
        old_commit = str(old_item.get("commit", "")).strip() if isinstance(old_item, dict) else ""
        old_last_update = (
            str(old_item.get("lastUpdate", "")).strip()
            if isinstance(old_item, dict)
            else ""
        )
        old_last_commit_id = (
            str(old_item.get("lastCommitId", "")).strip()
            if isinstance(old_item, dict)
            else ""
        )

        if old_repo and old_repo != new_repo:
            merged_commit = ""
            merged_last_update = ""
            merged_last_commit_id = ""
        elif new_commit and (old_commit == "" or old_commit != new_commit):
            merged_commit = new_commit
            merged_last_update = old_last_update
            merged_last_commit_id = old_last_commit_id
        else:
            merged_commit = old_commit
            merged_last_update = old_last_update
            merged_last_commit_id = old_last_commit_id

        merged[name] = {
            "repo": new_repo,
            "path": new_path or old_path or "./",
            "commit": merged_commit,
            "lastUpdate": merged_last_update,
            "lastCommitId": merged_last_commit_id,
        }
    return merged


def install_skills(skills: dict[str, dict[str, str]]) -> None:
    repo_latest_commit: dict[str, str] = {}
    repo_cached_dir: dict[str, Path] = {}

    for info in skills.values():
        repo = info["repo"]
        if repo in repo_latest_commit:
            continue
        repo_cached_dir[repo] = ensure_repo_cached(repo)
        repo_latest_commit[repo] = get_repo_head_commit(repo_cached_dir[repo])

    for skill_name, info in skills.items():
        repo = info["repo"]
        latest_commit = repo_latest_commit[repo]
        skill_path = str(info.get("path", "")).strip() or "./"

        info["commit"] = latest_commit

        source_dir = find_skill_source_dir(
            repo_cached_dir[repo], skill_name, skill_path
        )
        if source_dir is None:
            raise RuntimeError(f"未找到 skill 目录或 SKILL.md: {skill_name} ({repo})")

        copy_skill_to_target(skill_name, source_dir, repo_cached_dir[repo])
        last_commit_id, last_update = get_last_commit_for_path(
            repo_cached_dir[repo], skill_path
        )
        info["lastCommitId"] = last_commit_id
        info["lastUpdate"] = last_update


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    try:
        extracted_skills = load_index_skills(INDEX_PATH)
        existing_skills = load_existing_skills(OUTPUT_PATH)
        skills = merge_skills(extracted_skills, existing_skills)
        valid_cache_names = {
            build_cache_dir_name(info["repo"]) for info in skills.values()
        }
        cleanup_cache_dirs(valid_cache_names)
        install_skills(skills)
        OUTPUT_PATH.write_text(
            json.dumps(skills, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        LOGGER.info("Skills 列表与安装已完成: %s -> %s", OUTPUT_PATH, TARGET_SKILLS_DIR)
    except Exception as exc:
        LOGGER.error("更新失败: %s", exc)
        raise


if __name__ == "__main__":
    main()
