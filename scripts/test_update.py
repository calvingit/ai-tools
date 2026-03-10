import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import update


class UpdateScriptTests(unittest.TestCase):
    def test_output_path_points_to_root_lock_file(self) -> None:
        self.assertEqual(update.OUTPUT_PATH.name, ".skills-lock.json")
        self.assertEqual(update.OUTPUT_PATH.parent, update.ROOT_DIR)

    def test_build_cache_dir_name_from_tree_url(self) -> None:
        name = update.build_cache_dir_name(
            "https://github.com/antfu/skills/tree/main/skills/pnpm"
        )
        self.assertEqual(name, "antfu-skills")

    def test_to_shanghai_time(self) -> None:
        converted = update.to_shanghai_time("2026-01-15T00:00:00+00:00")
        self.assertEqual(converted, "2026-01-15 08:00:00")

    def test_get_last_commit_for_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_dir = Path(tmp)
            self._run(["git", "init"], cwd=repo_dir)
            self._run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir)
            self._run(["git", "config", "user.name", "tester"], cwd=repo_dir)

            (repo_dir / "skills" / "alpha").mkdir(parents=True)
            (repo_dir / "skills" / "alpha" / "SKILL.md").write_text("v1", encoding="utf-8")
            self._run(["git", "add", "."], cwd=repo_dir)
            self._run(["git", "commit", "-m", "first"], cwd=repo_dir)
            first_commit = self._run(["git", "rev-parse", "HEAD"], cwd=repo_dir)

            (repo_dir / "other").mkdir(parents=True)
            (repo_dir / "other" / "README.md").write_text("x", encoding="utf-8")
            self._run(["git", "add", "."], cwd=repo_dir)
            self._run(["git", "commit", "-m", "second"], cwd=repo_dir)

            commit_id, last_update = update.get_last_commit_for_path(
                repo_dir,
                "skills/alpha",
            )

            self.assertEqual(commit_id, first_commit)
            self.assertRegex(last_update, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_copy_root_skill_with_optional_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            source_repo = base_dir / "source"
            source_repo.mkdir(parents=True, exist_ok=True)
            (source_repo / "SKILL.md").write_text("# root skill", encoding="utf-8")
            (source_repo / "scripts").mkdir()
            (source_repo / "scripts" / "run.py").write_text("print('ok')", encoding="utf-8")
            (source_repo / "references").mkdir()
            (source_repo / "references" / "guide.md").write_text("guide", encoding="utf-8")
            (source_repo / "assets").mkdir()
            (source_repo / "assets" / "template.txt").write_text("tpl", encoding="utf-8")

            target_root = base_dir / "skills"
            with mock.patch.object(update, "TARGET_SKILLS_DIR", target_root):
                update.copy_skill_to_target(
                    skill_name="humanizer-zh",
                    category="Writing",
                    source_dir=source_repo / "SKILL.md",
                    repo_root=source_repo,
                )

            installed = target_root / "Writing" / "humanizer-zh"
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertTrue((installed / "scripts" / "run.py").is_file())
            self.assertTrue((installed / "references" / "guide.md").is_file())
            self.assertTrue((installed / "assets" / "template.txt").is_file())

    def test_install_skills_skips_copy_when_repo_commit_unchanged(self) -> None:
        skills = {
            "skill-a": {
                "repo": "https://github.com/acme/repo",
                "path": "skills/skill-a",
                "category": "Tool",
                "commit": "",
                "lastUpdate": "",
                "lastCommitId": "",
            }
        }
        existing = {
            "skill-a": {
                "repo": "https://github.com/acme/repo",
                "path": "skills/skill-a",
                "category": "Tool",
                "commit": "same-commit",
                "lastUpdate": "2026-01-01 00:00:00",
                "lastCommitId": "old-last-commit",
            }
        }

        with (
            mock.patch.object(update, "ensure_repo_cached", return_value=Path("/tmp/repo")),
            mock.patch.object(update, "get_repo_head_commit", return_value="same-commit"),
            mock.patch.object(update, "copy_skill_to_target") as copy_mock,
            mock.patch.object(update, "get_last_commit_for_path") as last_commit_mock,
            mock.patch.object(update, "find_skill_source_dir") as source_mock,
        ):
            update.install_skills(skills, existing)

        copy_mock.assert_not_called()
        last_commit_mock.assert_not_called()
        source_mock.assert_not_called()
        self.assertEqual(skills["skill-a"]["commit"], "same-commit")
        self.assertEqual(skills["skill-a"]["lastUpdate"], "2026-01-01 00:00:00")
        self.assertEqual(skills["skill-a"]["lastCommitId"], "old-last-commit")

    def test_install_skills_syncs_when_repo_commit_changed(self) -> None:
        skills = {
            "skill-a": {
                "repo": "https://github.com/acme/repo",
                "path": "skills/skill-a",
                "category": "Tool",
                "commit": "",
                "lastUpdate": "",
                "lastCommitId": "",
            }
        }
        existing = {
            "skill-a": {
                "repo": "https://github.com/acme/repo",
                "path": "skills/skill-a",
                "category": "Tool",
                "commit": "old-commit",
                "lastUpdate": "2026-01-01 00:00:00",
                "lastCommitId": "old-last-commit",
            }
        }

        with (
            mock.patch.object(update, "ensure_repo_cached", return_value=Path("/tmp/repo")),
            mock.patch.object(update, "get_repo_head_commit", return_value="new-commit"),
            mock.patch.object(update, "find_skill_source_dir", return_value=Path("/tmp/repo/skills/skill-a")) as source_mock,
            mock.patch.object(update, "copy_skill_to_target") as copy_mock,
            mock.patch.object(update, "get_last_commit_for_path", return_value=("path-commit", "2026-02-02 02:02:02")) as last_commit_mock,
        ):
            update.install_skills(skills, existing)

        source_mock.assert_called_once()
        copy_mock.assert_called_once()
        last_commit_mock.assert_called_once()
        self.assertEqual(skills["skill-a"]["commit"], "new-commit")
        self.assertEqual(skills["skill-a"]["lastUpdate"], "2026-02-02 02:02:02")
        self.assertEqual(skills["skill-a"]["lastCommitId"], "path-commit")

    def test_ensure_repo_cached_reclones_when_pull_ff_only_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            cache_dir = base / ".cache"
            repo_dir = cache_dir / "github-awesome-copilot"
            (repo_dir / ".git").mkdir(parents=True)
            (repo_dir / "README.md").write_text("cached", encoding="utf-8")

            with (
                mock.patch.object(update, "CACHE_DIR", cache_dir),
                mock.patch.object(
                    update,
                    "run_command",
                    side_effect=["", RuntimeError("fatal: Not possible to fast-forward, aborting.")],
                ) as run_cmd_mock,
                mock.patch.object(update, "clone_repo_to_cache", return_value=repo_dir) as clone_mock,
                mock.patch.object(update.shutil, "rmtree") as rmtree_mock,
            ):
                result = update.ensure_repo_cached("https://github.com/github/awesome-copilot")

        self.assertEqual(result, repo_dir)
        self.assertEqual(run_cmd_mock.call_count, 2)
        rmtree_mock.assert_called_once_with(repo_dir)
        clone_mock.assert_called_once_with(
            "https://github.com/github/awesome-copilot", repo_dir
        )

    def _run(self, cmd: list[str], cwd: Path) -> str:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()


if __name__ == "__main__":
    unittest.main()
