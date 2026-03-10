import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import install


class InstallScriptTests(unittest.TestCase):
    def test_normalize_agents_supports_comma_values(self) -> None:
        agents = install.normalize_agents(["claude-code, codex, trae"])
        self.assertEqual(agents, ["claude-code", "codex", "trae"])

    def test_normalize_agents_supports_mixed_flags(self) -> None:
        agents = install.normalize_agents(["claude-code,codex", "trae"])
        self.assertEqual(agents, ["claude-code", "codex", "trae"])

    def test_load_categories_from_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.json").write_text(
                json.dumps(
                    {
                        "categories": [
                            {"name": "Tool", "items": []},
                            {"name": "Web", "items": []},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(install.load_categories(root), ["Tool", "Web"])

    def test_list_units_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            category_dir = root / "skills" / "Web"
            (category_dir / "nuxt").mkdir(parents=True)
            (category_dir / "nuxt" / "SKILL.md").write_text("# nuxt", encoding="utf-8")
            (category_dir / "next-skills" / "next-best-practices").mkdir(parents=True)

            units = install.list_units(root, "Web")
            self.assertEqual(list(units.keys()), ["next-skills", "nuxt"])
            self.assertEqual(units["nuxt"], "skill")
            self.assertEqual(units["next-skills"], "bundle")

    def test_build_plan_for_category_with_units(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.json").write_text(
                json.dumps({"categories": [{"name": "Tool", "items": []}]}),
                encoding="utf-8",
            )
            tool_dir = root / "skills" / "Tool"
            (tool_dir / "chrome-devtools").mkdir(parents=True)
            (tool_dir / "chrome-devtools" / "SKILL.md").write_text("# x", encoding="utf-8")

            plan = install.build_install_plan(
                root=root,
                categories=["Tool"],
                category="Tool",
                units=["chrome-devtools"],
                global_install=True,
                agents=["codex", "claude-code"],
            )

            self.assertEqual(len(plan), 1)
            cmd = plan[0]["cmd"]
            self.assertEqual(cmd[:4], ["npx", "skills", "add", str(tool_dir / "chrome-devtools")])
            self.assertIn("-g", cmd)
            self.assertEqual(cmd.count("-a"), 2)
            self.assertEqual(cmd[-1], "-y")

    def test_build_plan_for_all_categories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.json").write_text(
                json.dumps(
                    {"categories": [{"name": "Tool", "items": []}, {"name": "Web", "items": []}]}
                ),
                encoding="utf-8",
            )
            (root / "skills" / "Tool" / "chrome-devtools").mkdir(parents=True)
            (root / "skills" / "Web" / "nuxt").mkdir(parents=True)

            plan = install.build_install_plan(
                root=root,
                categories=["Tool", "Web"],
                category="all",
                units=[],
                global_install=False,
                agents=[],
            )
            self.assertEqual(len(plan), 2)
            self.assertEqual(plan[0]["category"], "Tool")
            self.assertEqual(plan[1]["category"], "Web")

    def test_all_cannot_mix_with_units(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.json").write_text(
                json.dumps({"categories": [{"name": "Tool", "items": []}]}),
                encoding="utf-8",
            )
            (root / "skills" / "Tool").mkdir(parents=True)

            with self.assertRaises(ValueError):
                install.build_install_plan(
                    root=root,
                    categories=["Tool"],
                    category="all",
                    units=["chrome-devtools"],
                    global_install=False,
                    agents=[],
                )


if __name__ == "__main__":
    unittest.main()
