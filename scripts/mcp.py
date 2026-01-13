#!/usr/bin/env python3
"""MCP server installation script for Claude Code."""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Default paths
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_MCP_CONFIG = PROJECT_ROOT / "mcp" / "claude.json"
USER_CLAUDE_CONFIG = Path.home() / ".claude.json"
BACKUP_DIR = Path.home() / ".claude.json.backup"


def load_json_file(path: Path) -> dict:
    """Load a JSON file, return empty dict if not found."""
    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}")
        sys.exit(1)


def save_json_file(path: Path, data: dict):
    """Save data to a JSON file with pretty formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_mcp_servers(config: dict) -> dict:
    """Extract mcpServers from config, handling different structures."""
    if "mcpServers" in config:
        return config.get("mcpServers", {})
    return {}


def backup_config() -> Path:
    """Create a timestamped backup of ~/.claude.json."""
    if not USER_CLAUDE_CONFIG.exists():
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"claude.json.{timestamp}"

    shutil.copy2(USER_CLAUDE_CONFIG, backup_path)
    print(f"✓ Backed up to: {backup_path}")

    # Clean up old backups (keep last 10)
    clean_old_backups(keep=10)

    return backup_path


def clean_old_backups(keep: int = 10):
    """Remove old backups, keeping only the most recent ones."""
    if not BACKUP_DIR.exists():
        return

    backups = sorted(BACKUP_DIR.glob("claude.json.*"), reverse=True)

    for old_backup in backups[keep:]:
        old_backup.unlink()
        print(f"  Removed old backup: {old_backup.name}")


def list_backups():
    """List all available backups."""
    if not BACKUP_DIR.exists():
        print("No backups found.")
        return

    backups = sorted(BACKUP_DIR.glob("claude.json.*"), reverse=True)

    if not backups:
        print("No backups found.")
        return

    print(f"Backups ({len(backups)} total):")
    for backup in backups:
        # Extract timestamp from filename
        timestamp_str = backup.name.replace("claude.json.", "")
        try:
            dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted_time = timestamp_str

        size = backup.stat().st_size
        size_kb = size / 1024

        print(f"  {formatted_time}  ({size_kb:.1f} KB)  {backup.name}")


def restore_backup(backup_name: str):
    """Restore ~/.claude.json from a backup."""
    backup_path = BACKUP_DIR / backup_name

    if not backup_path.exists():
        print(f"Error: Backup not found: {backup_path}")
        print("\nAvailable backups:")
        list_backups()
        sys.exit(1)

    # Create a backup of current config before restoring
    if USER_CLAUDE_CONFIG.exists():
        print("Creating backup of current config...")
        pre_restore_backup = backup_config()
        print(f"  Pre-restore backup: {pre_restore_backup}")

    shutil.copy2(backup_path, USER_CLAUDE_CONFIG)
    print(f"✓ Restored from: {backup_path}")
    print(f"  Updated: {USER_CLAUDE_CONFIG}")


def merge_mcp_configs(local_config: dict, user_config: dict, force: bool = False) -> tuple:
    """Merge local MCP config with user config, avoiding conflicts.

    Returns:
        (merged_config, added_servers, skipped_servers, replaced_servers)
    """
    local_servers = get_mcp_servers(local_config)
    user_servers = get_mcp_servers(user_config)

    merged = user_config.copy()
    merged_servers = user_servers.copy()
    added_servers = []
    skipped_servers = []
    replaced_servers = []

    for name, local_config in local_servers.items():
        if name in merged_servers:
            user_config = merged_servers[name]
            if local_config == user_config:
                skipped_servers.append(name)
            else:
                if force:
                    merged_servers[name] = local_config
                    replaced_servers.append(name)
                else:
                    skipped_servers.append(name)
        else:
            merged_servers[name] = local_config
            added_servers.append(name)

    merged["mcpServers"] = merged_servers

    return merged, added_servers, skipped_servers, replaced_servers


def install_mcps(force: bool = False, dry_run: bool = False, no_backup: bool = False):
    """Install MCP servers from local config to user config."""
    if not LOCAL_MCP_CONFIG.exists():
        print(f"Error: Local MCP config not found: {LOCAL_MCP_CONFIG}")
        sys.exit(1)

    local_config = load_json_file(LOCAL_MCP_CONFIG)
    user_config = load_json_file(USER_CLAUDE_CONFIG)

    merged, added, skipped, replaced = merge_mcp_configs(
        local_config, user_config, force=force
    )

    local_servers = get_mcp_servers(local_config)
    print(f"Found {len(local_servers)} MCP server(s) in local config")

    if added:
        print(f"  New servers to add: {len(added)}")
        for name in added:
            print(f"    + {name}")

    if replaced:
        print(f"  Servers to replace: {len(replaced)}")
        for name in replaced:
            print(f"    ~ {name}")

    if skipped:
        print(f"  Skipped (already exists): {len(skipped)}")
        for name in skipped:
            print(f"    - {name}")

    if dry_run:
        print("\n[Dry run] No changes made.")
        return

    if added or replaced:
        # Create backup before modifying
        if not no_backup:
            print("\nCreating backup...")
            backup_config()

        save_json_file(USER_CLAUDE_CONFIG, merged)
        print(f"\n✓ Updated: {USER_CLAUDE_CONFIG}")
    else:
        print("\nNo changes needed.")


def uninstall_mcps(dry_run: bool = False, no_backup: bool = False):
    """Uninstall MCP servers that were added from local config."""
    if not LOCAL_MCP_CONFIG.exists():
        print(f"Error: Local MCP config not found: {LOCAL_MCP_CONFIG}")
        sys.exit(1)

    if not USER_CLAUDE_CONFIG.exists():
        print(f"Error: User config not found: {USER_CLAUDE_CONFIG}")
        sys.exit(1)

    local_config = load_json_file(LOCAL_MCP_CONFIG)
    user_config = load_json_file(USER_CLAUDE_CONFIG)

    local_servers = get_mcp_servers(local_config)
    user_servers = get_mcp_servers(user_config)

    removed = []
    for name in local_servers:
        if name in user_servers:
            removed.append(name)
            del user_servers[name]

    if removed:
        print(f"Removing {len(removed)} MCP server(s):")
        for name in removed:
            print(f"  - {name}")

        if dry_run:
            print("\n[Dry run] No changes made.")
            return

        # Create backup before modifying
        if not no_backup:
            print("\nCreating backup...")
            backup_config()

        user_config["mcpServers"] = user_servers
        save_json_file(USER_CLAUDE_CONFIG, user_config)
        print(f"\n✓ Updated: {USER_CLAUDE_CONFIG}")
    else:
        print("No MCP servers to remove.")


def list_mcps():
    """List MCP servers and their status."""
    local_config = load_json_file(LOCAL_MCP_CONFIG)
    user_config = load_json_file(USER_CLAUDE_CONFIG)

    local_servers = get_mcp_servers(local_config)
    user_servers = get_mcp_servers(user_config)

    all_names = sorted(set(local_servers) | set(user_servers))

    if not all_names:
        print("No MCP servers configured.")
        return

    print(f"MCP Servers ({len(all_names)} total):")

    for name in all_names:
        in_local = name in local_servers
        in_user = name in user_servers

        if in_local and in_user:
            configs_match = local_servers[name] == user_servers[name]
            if configs_match:
                status = "✓ installed"
            else:
                status = "⚠ conflict (different config)"
        elif in_user:
            status = "→ user only"
        elif in_local:
            status = "○ not installed"
        else:
            status = "? unknown"

        # Get server type
        if in_local:
            server_type = local_servers[name].get("type", "stdio")
        else:
            server_type = user_servers[name].get("type", "stdio")

        print(f"  [{status}] {name} ({server_type})")


def show_diff():
    """Show differences between local and user MCP configs."""
    local_config = load_json_file(LOCAL_MCP_CONFIG)
    user_config = load_json_file(USER_CLAUDE_CONFIG)

    local_servers = get_mcp_servers(local_config)
    user_servers = get_mcp_servers(user_config)

    print("MCP Server Configuration Differences:")
    print("=" * 50)

    has_diff = False

    # Servers in local but not in user
    only_local = set(local_servers) - set(user_servers)
    if only_local:
        has_diff = True
        print(f"\nServers in local config only (will be added):")
        for name in sorted(only_local):
            print(f"  + {name}")

    # Servers in user but not in local
    only_user = set(user_servers) - set(local_servers)
    if only_user:
        has_diff = True
        print(f"\nServers in user config only:")
        for name in sorted(only_user):
            print(f"  - {name}")

    # Servers in both but with different configs
    both = set(local_servers) & set(user_servers)
    diff_configs = []
    for name in both:
        if local_servers[name] != user_servers[name]:
            diff_configs.append(name)

    if diff_configs:
        has_diff = True
        print(f"\nServers with different configurations:")
        for name in sorted(diff_configs):
            print(f"  ~ {name}")
            print(f"    Local:  {json.dumps(local_servers[name], sort_keys=True)}")
            print(f"    User:   {json.dumps(user_servers[name], sort_keys=True)}")

    if not has_diff:
        print("\n✓ Configs are in sync.")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Claude Code MCP server installation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/mcp.py install              # Install MCP servers
  python scripts/mcp.py install -f           # Force reinstall
  python scripts/mcp.py install --dry-run    # Preview changes
  python scripts/mcp.py install --no-backup  # Install without backup
  python scripts/mcp.py uninstall            # Uninstall MCP servers
  python scripts/mcp.py list                 # List MCP servers
  python scripts/mcp.py diff                 # Show differences
  python scripts/mcp.py backups              # List backups
  python scripts/mcp.py restore <backup>     # Restore from backup
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install MCP servers")
    install_parser.add_argument(
        "-f", "--force", action="store_true", help="Force replace conflicting configs"
    )
    install_parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying"
    )
    install_parser.add_argument(
        "--no-backup", action="store_true", help="Skip creating backup"
    )

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall MCP servers")
    uninstall_parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying"
    )
    uninstall_parser.add_argument(
        "--no-backup", action="store_true", help="Skip creating backup"
    )

    # List command
    subparsers.add_parser("list", help="List MCP servers and their status")

    # Diff command
    subparsers.add_parser("diff", help="Show differences between configs")

    # Backups command
    subparsers.add_parser("backups", help="List available backups")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("backup", help="Backup file name (e.g., claude.json.20250113_123456)")

    args = parser.parse_args()

    if args.command == "install":
        install_mcps(force=args.force, dry_run=args.dry_run, no_backup=args.no_backup)
    elif args.command == "uninstall":
        uninstall_mcps(dry_run=args.dry_run, no_backup=args.no_backup)
    elif args.command == "list":
        list_mcps()
    elif args.command == "diff":
        show_diff()
    elif args.command == "backups":
        list_backups()
    elif args.command == "restore":
        restore_backup(args.backup)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
