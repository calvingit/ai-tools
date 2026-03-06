---
name: lint-agents-md
description: Evaluate and improve the quality of a repository AGENTS.md file using best practices.
---

# AGENTS.md Linter

Evaluate a repository's `AGENTS.md` and propose improvements.

Goal:

1. Detect structural weaknesses
2. Identify missing project context
3. Detect harmful instruction patterns
4. Propose concrete improvements
5. Suggest rewritten sections

Use the process below.

---

## Phase 1 — File Classification

Identify the **type of AGENTS.md**.

Possible categories:

1. Global agent rules
2. Repository engineering guide
3. Specialized agent definition
4. Hybrid

Explain the detected category.

---

## Phase 2 — Structural Analysis

Evaluate whether the file includes the most useful sections observed in real repositories.

Checklist:

| Section              | Present | Notes |
| -------------------- | ------- | ----- |
| Project overview     | ✅      |       |
| Tech stack           | ✅      |       |
| Repository structure | ✅      |       |
| Build / dev commands | ✅      |       |
| Test commands        | ✅      |       |
| Code style           | ✅      |       |
| Agent boundaries     | ✅      |       |

These elements appear in the majority of successful agent context files.

Missing sections reduce agent reliability.

---

## Phase 3 — Actionability Test

Determine whether instructions are **executable**.

Evaluate:

| Item                 | Result |
| -------------------- | ------ |
| Commands runnable    | ✅     |
| Paths explicit       | ✅     |
| Tools specified      | ✅     |
| Testing instructions | ✅     |
| Lint instructions    | ✅     |

Example of good instruction:

```bash

pnpm install
pnpm test
pnpm lint

```

Avoid vague rules such as:

"Run tests before committing."

Instructions should be **machine-operational whenever possible**.

---

## Phase 4 — Agent Workflow Guidance

Evaluate whether the file describes **how the agent should operate**.

Checklist:

| Capability               | Present |
| ------------------------ | ------- |
| problem solving workflow | ✅      |
| change policy            | ✅      |
| refactor rules           | ✅      |
| dependency policy        | ✅      |
| debug strategy           | ✅      |
| PR workflow              | ✅      |

Agent performance improves when operating procedures are explicit.

---

## Phase 5 — Guardrails & Safety

Evaluate whether the file defines boundaries.

Checklist:

| Guardrail                | Present |
| ------------------------ | ------- |
| restricted directories   | ✅      |
| infra modification rules | ✅      |
| database migration rules | ✅      |
| dependency upgrade rules | ✅      |

Examples of strong boundaries:

- never modify `infra/`
- migrations require human approval
- never delete tests

Missing guardrails increases risk of destructive changes.

---

## Phase 6 — Context Coverage

Evaluate whether the file provides **sufficient project context**.

Check for:

| Context               | Present |
| --------------------- | ------- |
| architecture overview | ✅      |
| major modules         | ✅      |
| external services     | ✅      |
| environment variables | ✅      |
| design patterns       | ✅      |

Agent context files typically include architecture and implementation hints.

---

## Phase 7 — Signal-to-Noise Analysis

Estimate instruction density.

Guidelines:

Recommended length:

60–300 lines.

Detect issues:

| Problem                  | Description |
| ------------------------ | ----------- |
| instruction overload     |             |
| duplicated rules         |             |
| contradictions           |             |
| irrelevant documentation |             |

Large instruction sets degrade agent performance.

---

## Phase 8 — Anti-Patterns

Detect common problems.

Common anti-patterns:

1. Vague instructions
2. Overly strict requirements
3. Missing runnable commands
4. Excessive architectural description
5. Contradictory rules
6. Missing boundaries

Explain which ones are present.

---

## Phase 9 — Quality Score

Score each dimension.

| Dimension              | Score (0-5) |
| ---------------------- | ----------- |
| Structure completeness | 4           |
| Command actionability  | 4           |
| Workflow clarity       | 4           |
| Safety guardrails      | 4           |
| Project context        | 4           |
| Signal-to-noise        | 4           |

Overall rating:

- Excellent
- Good
- Needs improvement
- Poor

---

## Phase 10 — Improvement Plan

Provide recommendations.

Structure:

### Critical Fixes

(must fix)

### Recommended Improvements

(strongly suggested)

### Optional Enhancements

(nice to have)

Each suggestion must include:

- what to add
- why it matters
- example snippet

---

## Phase 11 — Example Rewrite

If major issues exist, generate improved sections.

Possible rewrites:

- Commands
- Guardrails
- Workflow
- Architecture summary

Keep rewritten sections concise.

---

## Output Format

```

AGENTS.md Lint Report

Type: <detected type>

Summary: <short assessment>

Scorecard:

<table>

Major Issues:

<ul>

Improvement Plan: <sectioned>

Example Improvements: <code blocks>

```

Focus on **clear engineering improvements**, not generic advice.
