# fwen Open Source Project Design

**Date:** 2025-01-12
**Status:** Approved
**Project:** fwen (Flutter Clean Architecture Scaffolder)

## Overview

Transform the `flutter-clean-app-creator` directory into a standalone open source project called "fwen" - a CLI tool for scaffolding Flutter applications with Clean Architecture. The goal is to build a community and provide practical utility for Flutter developers.

## Project Identity

**Name:** fwen
**Tagline:** Flutter Clean Architecture scaffolder
**License:** MIT

## Repository Structure

```
fwen/
├── .github/
│   ├── ISSUE_TEMPLATE/           # 4 templates: bug, feature, docs, help
│   ├── PULL_REQUEST_TEMPLATE.md  # PR guidelines
│   ├── workflows/                # CI/CD pipelines
│   │   ├── test.yml              # Run tests on all PRs
│   │   ├── lint.yml              # Code quality checks
│   │   ├── release.yml           # Automated PyPI releases
│   │   └── security.yml          # Dependency scanning
│   └── CODE_OF_CONDUCT.md        # Community guidelines
├── src/
│   └── fwen/                     # Main package (rename from modules/)
│       ├── __init__.py
│       ├── __main__.py           # CLI entry point (enables python -m fwen)
│       ├── cli.py                # Argument parser
│       ├── config.py
│       ├── generator.py
│       ├── prompts.py
│       ├── actions.py
│       └── utils.py
├── tests/                        # Keep existing test structure
├── templates/                    # Keep existing templates
├── scripts/                      # Keep helper scripts
├── docs/                         # Documentation site
│   ├── index.md
│   ├── installation.md
│   ├── usage.md
│   ├── templates.md
│   └── contributing.md
├── examples/                     # Example generated projects
├── .python-version               # Pin Python version for uv
├── pyproject.toml                # Modern Python packaging
├── uv.lock                       # Lock file for reproducible builds
├── README.md                     # Main documentation
├── LICENSE                       # MIT License
├── CONTRIBUTING.md               # Contribution guide
├── CHANGELOG.md                  # Version history
└── SECURITY.md                   # Security policy
```

## Key Changes from Current Structure

1. **Package Layout**: `modules/` → `src/fwen/` (proper Python package)
2. **Entry Point**: `clean_flutter_cli.py` → `src/fwen/__main__.py`
3. **Modern Packaging**: Add `pyproject.toml` for PyPI publishing
4. **uv Integration**: `.python-version`, `pyproject.toml`, `uv.lock`

## README.md Structure

**Documentation-First Approach:**

```markdown
# fwen

> Flutter Clean Architecture scaffolder

[Badges: PyPI, Python, License, Tests]

## Table of Contents
- Overview
- Why fwen?
- Features
- Installation
- Quick Start
- Documentation
- Contributing
- License
```

**Installation Section:**
- Using uv (recommended)
- Using pip
- From source

**Quick Start:**
- Interactive mode
- Non-interactive mode
- Generated structure preview

## Open Source Files

### Essential Files
1. **LICENSE** - MIT License
2. **CONTRIBUTING.md** - Setup, development workflow, PR process
3. **CODE_OF_CONDUCT.md** - Contributor Covenant 2.1
4. **CHANGELOG.md** - Version history starting with v0.1.0
5. **SECURITY.md** - Security policy and reporting

### GitHub Templates
- `bug_report.md` - Bug reproduction template
- `feature_request.md` - Feature proposal template
- `documentation.md` - Doc improvement template
- `help.md` - Support question template
- `PULL_REQUEST_TEMPLATE.md` - PR guidelines

## CI/CD Pipeline

### Workflows

**1. test.yml**
- Triggers: push, pull_request
- Matrix: Python 3.11, 3.12
- Uses uv for setup
- Runs pytest with coverage
- Reports to Codecov

**2. lint.yml**
- Runs ruff for linting
- Checks formatting with ruff format

**3. release.yml**
- Triggers: git tags (v*)
- Builds package with uv
- Publishes to PyPI automatically
- Requires id-token and contents permissions

**4. security.yml**
- Weekly dependency scanning
- Uses safety checker
- Manual trigger available

## uv Integration

**Configuration:**

`.python-version`:
```
3.11
```

`pyproject.toml`:
```toml
[project]
name = "fwen"
version = "0.1.0"
description = "Flutter Clean Architecture scaffolder"
requires-python = ">=3.11"
dependencies = [
    "questionary>=2.0",
    "rich>=14.0",
    "pyyaml>=6.0",
]

[project.scripts]
fwen = "fwen.__main__:main"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]
```

**Usage:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install fwen
uv pip install -e .

# Or run directly
uv run fwen --project-name my_app
```

## Release Strategy

### v0.1.0 Release

**Pre-Release Checklist:**
1. Create standalone GitHub repo `yourusername/fwen`
2. Restructure code (`src/fwen/`, `pyproject.toml`, `.python-version`)
3. Add all open source files
4. Set up CI/CD workflows
5. Write comprehensive README.md
6. Add documentation site stubs
7. Run full test suite
8. Test installation via `uv pip install -e .`

**Release Day:**
```bash
git tag -a v0.1.0 -m "Initial release of fwen"
git push origin v0.1.0
```

**Announcement Channels:**
- GitHub Release (with notes)
- Reddit: r/Flutter, r/Python
- Twitter/X with demo GIF
- Dev.to blog post
- LinkedIn

**Post-Release:**
- Monitor issues
- Patch releases for critical bugs
- Gather feedback for v0.2.0

## Implementation Checklist

### Phase 1: Repository Setup
- [ ] Create new GitHub repo `yourusername/fwen`
- [ ] Initialize with MIT LICENSE
- [ ] Create directory structure
- [ ] Copy and restructure existing code

### Phase 2: Python Package
- [ ] Create `pyproject.toml`
- [ ] Add `.python-version`
- [ ] Move `modules/` → `src/fwen/`
- [ ] Create `__main__.py` entry point
- [ ] Generate `uv.lock`

### Phase 3: Documentation
- [ ] Write README.md
- [ ] Create CONTRIBUTING.md
- [ ] Create CHANGELOG.md (v0.1.0)
- [ ] Create SECURITY.md
- [ ] Create GitHub templates

### Phase 4: CI/CD
- [ ] Add test.yml workflow
- [ ] Add lint.yml workflow
- [ ] Add release.yml workflow
- [ ] Add security.yml workflow
- [ ] Test with uv

### Phase 5: Release
- [ ] Tag v0.1.0
- [ ] Push to PyPI
- [ ] Create GitHub Release
- [ ] Announce on social channels

## Migration from Current Project

**Files to move:**
- `modules/*` → `src/fwen/*`
- `clean_flutter_cli.py` → `src/fwen/__main__.py`
- `tests/` → `tests/` (keep)
- `templates/` → `templates/` (keep)
- `scripts/` → `scripts/` (keep)

**Files to transform:**
- `SKILL.md` → `README.md` (restructure as docs-first)
- `requirements.txt` → `pyproject.toml` dependencies

**Files to create:**
- `LICENSE`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `SECURITY.md`
- `.python-version`
- `.github/` directory structure

## Success Criteria

- [ ] PyPI package installable via `pip install fwen`
- [ ] `uv run fwen` works correctly
- [ ] All CI/CD pipelines passing
- [ ] README.md provides clear documentation
- [ ] First community contribution received
- [ ] 100+ GitHub stars within 3 months
