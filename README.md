# AI Tools

Collection of Claude Code skills and MCP (Model Context Protocol) servers configuration for enhanced development experience.

## Overview

This repository contains:

- **Skills**: Reusable Claude Code skills for Flutter/Dart development
- **MCP Servers**: Pre-configured MCP servers for various development tools
- **Scripts**: Python scripts for easy installation and management
- **Makefile**: Convenient commands for installation and maintenance

## Quick Start

```bash
# Install everything (skills + MCP servers)
make install

# Or install separately
make install-skills   # Install skills only
make install-mcp      # Install MCP servers only

# List installed items
make list

# Show help
make help
```

## Project Structure

```
ai-tools/
├── skills/              # Claude Code skills
│   ├── flutter-dev/    # Flutter & Dart development
│   ├── swift-concurrency/  # Swift concurrency guidance
│   └── flutter-firebase/   # Firebase integration for Flutter
├── mcp/                 # MCP server configurations
│   ├── claude.json     # Local MCP server config
│   └── MCP-Servers.md   # MCP server documentation
├── scripts/             # Python management scripts
│   ├── skills.py       # Skill installation/management
│   └── mcp.py          # MCP server installation/management
├── Makefile            # Convenient commands
└── README.md           # This file
```

## Skills

### flutter-dev
Expert guidance for Flutter and Dart development, including:
- State management (Bloc, Riverpod, Provider, ChangeNotifier)
- Testing with Mocktail
- Navigation with GoRouter
- Code quality standards
- Architecture patterns
- Error handling

### swift-concurrency
Guidance for Swift Concurrency concepts:
- async/await
- Actors
- MainActor
- Sendable
- Isolation domains

### flutter-firebase
Firebase integration for Flutter:
- Authentication
- Firestore
- Cloud Functions
- Messaging
- Analytics
- And more...

## MCP Servers

Configured MCP servers (see `mcp/MCP-Servers.md` for details):

| Server | Type | Purpose |
|--------|------|---------|
| chrome-devtools | stdio | Browser automation |
| context7 | stdio | Documentation lookup |
| dart | stdio | Dart/Flutter dev tools |
| fetch | stdio | URL fetching |
| sequential-thinking | stdio | Structured reasoning |
| filesystem | stdio | File operations |
| git | stdio | Git operations |
| memory | stdio | Knowledge graph |
| time | stdio | Time/timezone |
| web-reader | HTTP | Web page reading (Zhipu) |
| web-search-prime | HTTP | Web search (Zhipu) |
| zai-mcp-server | stdio | Image/video analysis (Zhipu) |
| zread | HTTP | GitHub repo reading (Zhipu) |

## Installation

### Using Make (Recommended)

```bash
# Install everything
make install

# Install skills only
make install-skills

# Install MCP servers only
make install-mcp

# Force reinstall (override conflicts)
make reinstall-skills
make reinstall-mcp

# Uninstall
make uninstall
```

### Using Python Scripts Directly

```bash
# Skills
python3 scripts/skills.py install
python3 scripts/skills.py uninstall
python3 scripts/skills.py list

# MCP Servers
python3 scripts/mcp.py install
python3 scripts/mcp.py install --dry-run    # Preview changes
python3 scripts/mcp.py install -f          # Force reinstall
python3 scripts/mcp.py uninstall
python3 scripts/mcp.py list
python3 scripts/mcp.py diff                # Show differences
python3 scripts/mcp.py backups             # List backups
python3 scripts/mcp.py restore <backup>    # Restore from backup
```

## MCP Server Management

### Automatic Backup

Before installing or uninstalling MCP servers, the script automatically creates a backup of `~/.claude.json`.

- Backups are stored in: `~/.claude.json.backup/`
- Keeps the most recent 10 backups
- Format: `claude.json.YYYYMMDD_HHMMSS`

### Backup Commands

```bash
# List all backups
make backups
# or
python3 scripts/mcp.py backups

# Restore from backup
make restore BACKUP=claude.json.20250113_123456
# or
python3 scripts/mcp.py restore claude.json.20250113_123456
```

### Conflict Detection

The MCP installation script checks for conflicts before modifying `~/.claude.json`:

- **Already exists with same config**: Skipped
- **Already exists with different config**: Skipped (use `-f` to override)
- **Not installed**: Added

```bash
# Check for conflicts without installing
make diff
# or
python3 scripts/mcp.py diff
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make install` | Install everything |
| `make install-skills` | Install skills only |
| `make install-mcp` | Install MCP servers only |
| `make uninstall` | Uninstall everything |
| `make list` | List all installed items |
| `make list-skills` | List skills |
| `make list-mcp` | List MCP servers |
| `make diff` | Show MCP config differences |
| `make backups` | List MCP backups |
| `make dry-run-mcp` | Preview MCP installation |
| `make reinstall-skills` | Force reinstall skills |
| `make reinstall-mcp` | Force reinstall MCP servers |
| `make restore BACKUP=...` | Restore from backup |
| `make help` | Show all commands |

## Configuration Files

### Skills Location

Skills are symlinked to `~/.claude/skills/`:

```bash
~/.claude/skills/
├── flutter-dev -> /path/to/ai-tools/skills/flutter-dev
├── swift-concurrency -> /path/to/ai-tools/skills/swift-concurrency
└── flutter-firebase -> /path/to/ai-tools/skills/flutter-firebase
```

### MCP Configuration

MCP servers are merged into `~/.claude.json` from `mcp/claude.json`.

**Note 1**: Zhipu AI services require API key configuration. Put `Z_AI_API_KEY` in your environment variables.

**Note 2**: Context7 services do not require API key configuration. But if you want get more quick response, you can put `CONTEXT7_API_KEY` in your environment variables.

## Requirements

- Python 3.x
- Claude Code CLI
- Make (optional, for Makefile commands)

## License

MIT
