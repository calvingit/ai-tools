# AGENTS.md

## Project Overview

This is an AI coding assistant configuration and skills management repository. It provides:

- Configuration templates for Codex (`~/.codex/config.toml`) and Claude (`~/.claude/settings.json`)
- An `AGENTS.md` template for AI agents context
- A curated collection of open-source skills from various GitHub repositories
- Python scripts to download, update, and install skills to local AI assistants

## Repository Structure

```
├── codex/                    # Codex configuration templates
│   ├── config.toml          # Main configuration template
│   └── AGENTS.md            # AGENTS.md template
├── claude/                   # Claude configuration templates
│   └── settings.json        # Settings template
├── skills/                   # Downloaded skills (auto-generated)
│   ├── Tool/                # Tool-related skills
│   ├── Documentation/       # Documentation skills
│   ├── React/               # React skills
│   ├── Vue/                 # Vue.js skills
│   ├── Flutter/             # Flutter skills
│   └── ...                  # Other categories
├── scripts/                  # Python management scripts
│   ├── update.py            # Download/update skills from GitHub
│   ├── install.py           # Install skills to AI assistants
│   └── render_readme_skills.py  # Generate skills list for README
├── index.json               # Skills registry (source of truth)
├── .skills-lock.json        # Lock file with commit hashes
└── README.md                # Human-facing documentation (Chinese)
```

## Setup Commands

### Initialize Python Environment

```bash
# Install uv if not already installed
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates .venv)
uv sync
```

## Development Workflow

### Update Skills from GitHub

Download and update skills to the local `skills/` directory:

```bash
# Run with uv
uv run python ./scripts/update.py

# Or activate venv first
source .venv/bin/activate
python ./scripts/update.py
```

This script:
- Parses `index.json` to find all skills
- Clones/updates repositories to `.cache/`
- Copies skill files to `skills/<category>/<skill-name>/`
- Generates `.skills-lock.json` with commit hashes

### Install Skills to AI Assistant

Install skills to your local AI assistant using `npx skills add`:

```bash
# Interactive mode (select category and units)
uv run python ./scripts/install.py

# Install specific category
uv run python ./scripts/install.py --category Tool

# Install specific skill within a category
uv run python ./scripts/install.py --category Web --unit next-skills

# Install all categories
uv run python ./scripts/install.py --category all

# Global installation
uv run python ./scripts/install.py --category Tool -g

# Specify agent
uv run python ./scripts/install.py --category Tool -a codex
```

### Generate Skills List for README

```bash
uv run python ./scripts/render_readme_skills.py
```

## Testing Instructions

### Run Tests for Scripts

```bash
# Run update script tests
uv run python ./scripts/test_update.py

# Run install script tests  
uv run python ./scripts/test_install.py
```

## Code Style Guidelines

### Python Code

- Use type hints where appropriate
- Follow PEP 8 naming conventions
- Use f-strings for string formatting
- Handle errors with specific exception types
- Use `pathlib.Path` for file operations

### Project Conventions

- Keep `index.json` as the single source of truth for skills
- Skills are organized by category in `skills/<category>/`
- Each skill should have a `SKILL.md` file
- Scripts use logging with consistent formatting
- Support both interactive and CLI argument modes

## Key Files

### index.json

The skills registry. Structure:

```json
{
  "categories": [
    {
      "name": "CategoryName",
      "items": [
        {
          "id": "skill-id",
          "url": "https://github.com/owner/repo/tree/main/path/to/skill",
          "desc": "Skill description"
        }
      ]
    }
  ]
}
```

### .skills-lock.json

Auto-generated lock file tracking:
- Repository URL
- Path within repo
- Category
- Last commit hash
- Last update timestamp

## Git Workflow

### CI/CD

GitHub Actions workflow (`.github/workflows/update-skills.yml`):
- Runs daily at 00:00 UTC
- Executes `update.py` to sync skills
- Commits changes if skills are updated

### Manual Git Operations

```bash
# Check status
git status

# Add skills updates
git add .skills-lock.json skills/

# Commit with descriptive message
git commit -m "feat: update skills to latest commits"
```

## Troubleshooting

### Common Issues

1. **npx not found**: Install Node.js/npm first
2. **Permission errors**: Ensure write access to `skills/` and `.cache/`
3. **GitHub rate limits**: The script has retry logic with exponential backoff

### Cache Management

- Cached repos stored in `.cache/`
- Old cache directories are auto-cleaned
- Temporary directories prefixed with `__skill_temp_` or containing `-tmp-` are cleaned

## Dependencies

### Python (managed by uv)

See `pyproject.toml` for dependencies. Key packages:
- No external runtime dependencies (stdlib only)
- Development dependencies in `pyproject.toml`

### System Requirements

- Python 3.10+
- Git
- Node.js + npm (for `npx skills add`)
- uv (for dependency management)

## Notes

- The project README is in Chinese (中文)
- Skills are sourced from multiple GitHub repositories
- Some skills are bundles (multiple skills in one directory)
- The `AGENTS.md` in `codex/` is a template for users to copy
