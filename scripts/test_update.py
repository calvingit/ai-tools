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
