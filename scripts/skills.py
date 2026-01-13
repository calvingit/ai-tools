#!/usr/bin/env python3
"""Skill installation/uninstallation script for Claude Code."""

import argparse
import json
import os
import sys
from pathlib import Path

# Default paths
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
CLAUDE_SKILLS_DIR = Path.home() / ".claude" / "skills"


def get_skill_dirs():
    """Get all skill directories."""
    if not SKILLS_DIR.exists():
        print(f"Error: Skills directory not found: {SKILLS_DIR}")
        sys.exit(1)

    return [d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]


def install_skill(skill_path: Path, force: bool = False) -> bool:
    """Install a single skill by creating a symlink."""
    skill_name = skill_path.name
    target_path = CLAUDE_SKILLS_DIR / skill_name

    # Ensure target directory exists
    CLAUDE_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    # Check if already installed
    if target_path.exists():
        if target_path.is_symlink():
            existing_target = target_path.resolve()
            if existing_target == skill_path.resolve():
                print(f"  ✓ Already linked: {skill_name}")
                return False
            elif force:
                target_path.unlink()
                print(f"  Force replacing: {skill_name}")
            else:
                print(f"  ⚠ Skipped (existing link): {skill_name}")
                return False
        else:
            if force:
                # Remove existing directory/file
                import shutil
                shutil.rmtree(target_path) if target_path.is_dir() else target_path.unlink()
                print(f"  Force replacing: {skill_name}")
            else:
                print(f"  ⚠ Skipped (exists and not a symlink): {skill_name}")
                return False

    # Create symlink
    target_path.symlink_to(skill_path.resolve())
    print(f"  ✓ Linked: {skill_name}")
    return True


def install_skills(force: bool = False):
    """Install all skills from the skills directory."""
    skill_dirs = get_skill_dirs()

    if not skill_dirs:
        print("No skill directories found.")
        return

    print(f"Installing {len(skill_dirs)} skill(s)...")
    installed = 0

    for skill_path in skill_dirs:
        if install_skill(skill_path, force):
            installed += 1

    print(f"\nInstalled: {installed}/{len(skill_dirs)}")


def uninstall_skill(skill_path: Path) -> bool:
    """Uninstall a single skill by removing its symlink."""
    skill_name = skill_path.name
    target_path = CLAUDE_SKILLS_DIR / skill_name

    if not target_path.exists():
        print(f"  ⚠ Not installed: {skill_name}")
        return False

    # Verify it's a symlink pointing to our skill
    if target_path.is_symlink():
        target_path.unlink()
        print(f"  ✓ Unlinked: {skill_name}")
        return True
    else:
        print(f"  ⚠ Skipped (not a symlink): {skill_name}")
        return False


def uninstall_skills():
    """Uninstall all skills from the skills directory."""
    skill_dirs = get_skill_dirs()

    if not skill_dirs:
        print("No skill directories found.")
        return

    print(f"Uninstalling {len(skill_dirs)} skill(s)...")
    uninstalled = 0

    for skill_path in skill_dirs:
        if uninstall_skill(skill_path):
            uninstalled += 1

    print(f"\nUninstalled: {uninstalled}/{len(skill_dirs)}")


def list_skills():
    """List all skills and their installation status."""
    skill_dirs = get_skill_dirs()

    if not skill_dirs:
        print("No skill directories found.")
        return

    print(f"Skills ({len(skill_dirs)} total):")

    for skill_path in sorted(skill_dirs, key=lambda x: x.name):
        skill_name = skill_path.name
        target_path = CLAUDE_SKILLS_DIR / skill_name

        # Check if SKILL.md exists
        skill_md = skill_path / "SKILL.md"
        has_skill_md = skill_md.exists() if skill_path.is_dir() else False

        status = "installed"
        if target_path.exists():
            if target_path.is_symlink() and target_path.resolve() == skill_path.resolve():
                status = "✓ installed"
            else:
                status = "⚠ conflict"
        else:
            status = "not installed"

        print(f"  [{status}] {skill_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Claude Code skills installation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/skills.py install       # Install all skills
  python scripts/skills.py install -f    # Force reinstall all skills
  python scripts/skills.py uninstall     # Uninstall all skills
  python scripts/skills.py list          # List skills with status
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install skills")
    install_parser.add_argument(
        "-f", "--force", action="store_true", help="Force reinstall existing skills"
    )

    # Uninstall command
    subparsers.add_parser("uninstall", help="Uninstall skills")

    # List command
    subparsers.add_parser("list", help="List skills and their status")

    args = parser.parse_args()

    if args.command == "install":
        install_skills(force=args.force)
    elif args.command == "uninstall":
        uninstall_skills()
    elif args.command == "list":
        list_skills()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
