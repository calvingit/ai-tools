# Flutter Clean Architecture CLI Design

**Date:** 2025-01-12
**Status:** Approved
**Location:** `flutter-clean-app-creator/`

## Overview

An interactive Python CLI for creating Flutter applications with Clean Architecture from scratch. The CLI provides a rich terminal interface with step-by-step prompts, comprehensive customization options, and post-creation action support.

## Goals

- Simplify Flutter project setup with Clean Architecture
- Provide interactive, user-friendly experience
- Support comprehensive customization options
- Offer helpful post-creation actions

## Architecture

### Module Structure

```
flutter-clean-app-creator/
├── clean_flutter_cli.py       # Main entry point
├── modules/
│   ├── __init__.py
│   ├── prompts.py             # Questionary prompt definitions
│   ├── generator.py           # File generation logic
│   ├── actions.py             # Post-creation actions
│   ├── config.py              # Config validation & defaults
│   └── utils.py               # Helper functions
├── templates/
│   ├── base/                  # Always included
│   ├── state_management/      # bloc/, provider/, riverpod/
│   ├── navigation/            # go_router/, auto_route/, navigator/
│   ├── firebase/              # auth/, firestore/, etc.
│   └── testing/               # test/ templates
├── scripts/
│   ├── scaffold_app.py        # Existing (backward compat)
│   ├── feature-dev.py         # Existing
│   └── install_dependencies.sh # Existing
├── requirements.txt           # Python dependencies
└── SKILL.md                   # Updated usage docs
```

### Core Modules

**prompts.py** - Organized prompt sections using `questionary`:
- Section 1: Project Basics (name, org, description, output)
- Section 2: Architecture & State Management
- Section 3: Platforms & Features
- Section 4: Development Tools
- Section 5: First Feature

**generator.py** - Orchestrates file creation:
- Runs `flutter create` for base project
- Copies template files with conditional overlays
- Applies `{{variable}}` substitutions
- Merges pubspec dependencies

**actions.py** - Post-creation actions:
- flutter pub get
- build_runner
- Open in editor
- Run app
- Create additional features

## Prompt Flow

### Section 1: Project Basics
| Field | Type | Default |
|-------|------|---------|
| Project name | text (snake_case) | required |
| Organization ID | text | `com.example` |
| Description | text | optional |
| Output directory | path | current |

### Section 2: Architecture & State Management
| Field | Type | Options |
|-------|------|---------|
| State management | select | Bloc, Provider, Riverpod |
| Navigation | select | GoRouter, AutoRoute, Navigator 2.0 |
| DI | select | GetIt, Provider, Riverpod |
| Include example code | confirm | Yes/No |

### Section 3: Platforms & Features
| Field | Type | Options |
|-------|------|---------|
| Platforms | checkbox | iOS, Android, Web, macOS, Windows, Linux |
| Authentication | confirm → select | Email, Google, Apple, Phone |
| Firebase | confirm → checkbox | Auth, Firestore, Functions, Analytics, Messaging, Storage |

### Section 4: Development Tools
| Field | Type | Options |
|-------|------|---------|
| API layer | confirm → select | Dio, Retrofit, Fetch |
| State persistence | confirm → select | Shared Preferences, Hive, Isar |
| Analytics | confirm → select | Firebase Analytics, Sentry, Mixpanel |
| Testing | confirm → checkbox | Unit, Widget, Integration |
| CI/CD | confirm → select | GitHub Actions, GitLab CI |

### Section 5: First Feature
| Field | Type | Options |
|-------|------|---------|
| Create initial feature | confirm → text | Feature name (PascalCase) |

## Template System

### Conditional Overlay

Templates use a conditional overlay system where base templates are always included, and feature-specific templates are added based on user choices.

**Common substitution variables:**
- `{{project_name}}` - Snake case
- `{{ProjectName}}` - Pascal case (classes)
- `{{project_name_camel}}` - CamelCase (widgets)
- `{{org_id}}` - Organization domain
- `{{description}}` - Project description

### Generation Process

1. Run `flutter create --org {{org_id}} {{project_name}}`
2. Replace `lib/` with template files
3. Apply string substitutions
4. Merge `pubspec.yaml` dependencies
5. Create initial feature if requested

## Post-Creation Actions

After successful generation, display success message with project summary, then present action menu (multi-select):

- Run `flutter pub get`
- Run `dart run build_runner build`
- Open in VS Code
- Open in Android Studio/IntelliJ
- Run on connected device
- Create additional feature
- View project structure
- Exit

## Dependencies

**Python:**
- `questionary` - Interactive prompts
- `rich` - Terminal formatting, progress, spinners
- `pyyaml` - Config management

**Flutter (in pubspec.yaml):**
- State management (bloc/provider/riverpod)
- Navigation (go_router/auto_route)
- DI (get_it)
- Networking (dio/retrofit)
- Testing (flutter_test, mocktail)

## Usage

```bash
python3 flutter-clean-app-creator/clean_flutter_cli.py
```

Optional shell alias:
```bash
alias flutter-clean='python3 /path/to/ai-tools/flutter-clean-app-creator/clean_flutter_cli.py'
```

## Implementation Checklist

- [ ] Create `modules/` directory structure
- [ ] Implement `prompts.py` with all 5 sections
- [ ] Implement `generator.py` with template overlay system
- [ ] Implement `actions.py` with post-creation menu
- [ ] Create `requirements.txt`
- [ ] Reorganize existing templates into new structure
- [ ] Add state management template variants (bloc/provider/riverpod)
- [ ] Add navigation template variants (go_router/auto_route/navigator)
- [ ] Add Firebase service templates
- [ ] Update `SKILL.md` with new usage
- [ ] Test end-to-end flow
