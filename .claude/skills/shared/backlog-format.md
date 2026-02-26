# Backlog Format Reference

Canonical reference for backlog directory structure, file naming, metadata formats, scoring rules, and status values. Consumed by: ghs:repo-scan, ghs:backlog-fix, ghs:backlog-board, ghs:backlog-score, ghs:backlog-next.

For the full list of health checks (verification commands, pass conditions, fix suggestions), see `checks/index.md` and the individual check files in `checks/`.

## Table of Contents

1. [Directory Structure](#directory-structure)
2. [File Naming Conventions](#file-naming-conventions)
3. [Tier System](#tier-system)
4. [Metadata Table Formats](#metadata-table-formats)
5. [Status Values](#status-values)
6. [Scoring Rules](#scoring-rules)

---

## Directory Structure

All backlog items live under `backlog/` in the project root, organized by repository:

```
backlog/{owner}_{repo}/
├── SUMMARY.md                              # Unified repo summary (scores, tables, links)
├── health/                                 # Health check findings (FAIL/WARN only)
│   ├── tier-1--readme.md
│   ├── tier-1--license.md
│   ├── tier-2--gitignore.md
│   └── ...
└── issues/                                 # Open GitHub issues
    ├── issue-42--login-page-crashes.md
    ├── issue-108--add-dark-mode.md
    └── ...
```

- The `{owner}_{repo}` directory name uses an underscore separator (not slash).
- `health/` is only created when at least one check results in FAIL or WARN.
- `issues/` is only created when the repository has open issues.
- `SUMMARY.md` is always created, even when all checks pass and there are no issues.

---

## File Naming Conventions

### Health items

```
tier-{N}--{check-name-kebab}.md
```

- `{N}` is the tier number: 1, 2, or 3.
- `{check-name-kebab}` is the check slug from `checks/index.md` (e.g., `branch-protection`, `ci-cd-workflows`, `security-alerts`).
- Only create files for checks with status **FAIL** or **WARN**. Passing checks are listed in SUMMARY.md but do not get their own file.

Examples:
- `tier-1--readme.md`
- `tier-1--branch-protection.md`
- `tier-2--issue-templates.md`
- `tier-3--security-alerts.md`

### Issue items

```
issue-{number}--{title-kebab}.md
```

- `{number}` is the GitHub issue number.
- `{title-kebab}` is the issue title converted to kebab-case, **truncated to 50 characters maximum**.
- Truncation cuts at the last complete word within the 50-char limit (no trailing hyphens).

Examples:
- `issue-42--login-page-crashes-on-mobile.md`
- `issue-108--add-dark-mode-support.md`
- `issue-250--refactor-authentication-module-to-sup.md` (truncated)

---

## Tier System

Health checks are organized into three tiers reflecting their importance:

| Tier | Label | Points per Check | Description |
|------|-------|-----------------|-------------|
| **1** | Required | 4 | Non-negotiable for any public or team-shared repository |
| **2** | Recommended | 2 | Important for maintainability and collaboration |
| **3** | Nice to Have | 1 | Polish items that signal a mature, well-maintained project |

---

## Metadata Table Formats

### Health item metadata

Every health item file begins with a title and a metadata table in this exact format:

```markdown
# {Check Name}

| Field | Value |
|-------|-------|
| **Repository** | `{owner}/{repo}` |
| **Source** | Health Check |
| **Tier** | {1|2|3} — {Required|Recommended|Nice to Have} |
| **Points** | {4|2|1} |
| **Status** | {FAIL|WARN} |
| **Detected** | {YYYY-MM-DD} |
```

Fields:
- **Repository**: The `owner/repo` string in backticks.
- **Source**: Always the literal string `Health Check`.
- **Tier**: Tier number followed by em-dash and label (e.g., `1 — Required`).
- **Points**: The point value for this tier (4, 2, or 1).
- **Status**: `FAIL` or `WARN` at creation. Updated to `PASS` when the fix is applied.
- **Detected**: Date the scan was run, in `YYYY-MM-DD` format.

### Issue item metadata

```markdown
# {Issue Title}

| Field | Value |
|-------|-------|
| **Repository** | `{owner}/{repo}` |
| **Source** | Issue #{number} |
| **Labels** | {comma-separated labels, or "none"} |
| **Assignee** | {assignee login, or "unassigned"} |
| **Status** | {OPEN|PR CREATED|CLOSED} |
| **Created** | {YYYY-MM-DD} |
| **Updated** | {YYYY-MM-DD} |
```

Fields:
- **Repository**: The `owner/repo` string in backticks.
- **Source**: `Issue #` followed by the GitHub issue number.
- **Labels**: All labels comma-separated, or the literal string `none`.
- **Assignee**: GitHub username (without `@`) or `unassigned`.
- **Status**: One of the issue status values (see below).
- **Created** / **Updated**: Dates in `YYYY-MM-DD` format.
- When a PR is created, a `| **PR** | {url} |` row is appended to the table.

---

## Status Values

### Health items

| Status | Meaning |
|--------|---------|
| **FAIL** | The check did not pass; action required |
| **PASS** | The check passed (set after fix is applied) |
| **WARN** | Unable to verify (usually permission-related: 403 from API) |

### Issue items

| Status | Meaning |
|--------|---------|
| **OPEN** | Issue is open on GitHub, no PR yet |
| **PR CREATED** | A fix PR has been created referencing this issue |
| **CLOSED** | Issue has been closed on GitHub |

---

## Scoring Rules

1. Each health check contributes points based on its tier: Tier 1 = 4 pts, Tier 2 = 2 pts, Tier 3 = 1 pt.
2. **WARN items are excluded** from both earned and possible totals. Do not penalize for checks that cannot be verified due to permissions.
3. **INFO items** (currently only FUNDING.yml) are purely informational and do not affect the score at all. They are not counted in earned or possible totals.
4. Percentage calculation: `earned_points / possible_points * 100`, **rounded to the nearest integer**.
5. Issues do not have a point score. They are tracked by count and label breakdown.

### Maximum possible points (all checks verifiable)

| Tier | Checks | Points each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 | 4 | 4 | 16 |
| Tier 2 | 8 | 2 | 16 |
| Tier 3 | 4 (excluding Funding) | 1 | 4 |
| **Total** | **16** | | **36** |

### Progress bar format

Use `█` for filled and `░` for empty, **8 characters wide**. Calculate filled characters as `round(percentage / 100 * 8)`.

Example: 50% = `████░░░░`
