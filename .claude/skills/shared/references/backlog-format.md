# Backlog Format Reference

Canonical reference for backlog directory structure, file naming, metadata formats, scoring rules, and status values. Consumed by: ghs-repo-scan, ghs-backlog-fix, ghs-backlog-board, ghs-backlog-score, ghs-backlog-next.

For the full list of health checks (verification commands, pass conditions, fix suggestions), see `checks/index.md` (module registry) and the individual module indexes (`checks/core/index.md`, `checks/dotnet/index.md`).

## Table of Contents

1. [Directory Structure](#directory-structure)
2. [File Naming Conventions](#file-naming-conventions)
3. [Tier System](#tier-system)
4. [Metadata Table Formats](#metadata-table-formats)
5. [Status Values](#status-values)
6. [Scoring Rules](#scoring-rules)

---

## Directory Structure

All backlog items live under `backlog/` in the project root, organized by repository and module:

```
backlog/{owner}_{repo}/
├── SUMMARY.md                              # Unified repo summary (scores, tables, links)
├── STATE.md                                # Session state: decisions, blockers, history (optional)
├── health/                                 # Core module findings (FAIL/WARN only)
│   ├── tier-1--readme.md
│   ├── tier-1--license.md
│   ├── tier-2--gitignore.md
│   └── ...
├── dotnet/                                 # .NET module findings (FAIL/WARN only)
│   ├── tier-1--dotnet-build-props.md
│   ├── tier-2--dotnet-nullable.md
│   ├── tier-3--dotnet-sourcelink.md
│   └── ...
└── issues/                                 # Open GitHub issues
    ├── issue-42--login-page-crashes.md
    ├── issue-108--add-dark-mode.md
    └── ...
```

- The `{owner}_{repo}` directory name uses an underscore separator (not slash).
- `health/` is only created when at least one core check results in FAIL or WARN.
- `dotnet/` is only created when the .NET module is active and at least one check results in FAIL or WARN.
- `issues/` is only created when the repository has open issues.
- `SUMMARY.md` is always created, even when all checks pass and there are no issues.
- `STATE.md` is created on first mutation (by ghs-backlog-fix, ghs-issue-implement, or ghs-action-fix). Not created by read-only skills. See `state-persistence.md` for the full format and lifecycle.

### Module-to-Directory Mapping

| Module | Backlog Directory | When Created |
|--------|------------------|--------------|
| Core | `health/` | At least one core FAIL/WARN |
| .NET | `dotnet/` | .NET module active + at least one FAIL/WARN |
| Issues | `issues/` | Repo has open issues |

Future modules will use their slug as the directory name (e.g., `node/`, `python/`).

---

## File Naming Conventions

### Health items (core and language modules)

```
tier-{N}--{check-slug}.md
```

- `{N}` is the tier number: 1, 2, or 3.
- `{check-slug}` is the check slug from the module's `index.md` (e.g., `branch-protection`, `dotnet-nullable`).
- Only create files for checks with status **FAIL** or **WARN**. Passing checks are listed in SUMMARY.md but do not get their own file.
- Core items go in `health/`, .NET items go in `dotnet/`.

Examples:
- `health/tier-1--readme.md`
- `health/tier-1--branch-protection.md`
- `health/tier-2--issue-templates.md`
- `dotnet/tier-1--dotnet-build-props.md`
- `dotnet/tier-2--dotnet-nullable.md`
- `dotnet/tier-3--dotnet-sourcelink.md`

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
| **Module** | {core|dotnet} |
| **Tier** | {1|2|3} — {Required|Recommended|Nice to Have} |
| **Points** | {4|2|1} |
| **Status** | {FAIL|WARN} |
| **Detected** | {YYYY-MM-DD} |
```

Fields:
- **Repository**: The `owner/repo` string in backticks.
- **Source**: Always the literal string `Health Check`.
- **Module**: The module slug (`core` or `dotnet`). This determines the backlog subdirectory.
- **Tier**: Tier number followed by em-dash and label (e.g., `1 — Required`).
- **Points**: The point value for this tier (4, 2, or 1).
- **Status**: `FAIL` or `WARN` at creation. Updated to `PASS` when the fix is applied.
- **Detected**: Date the scan was run, in `YYYY-MM-DD` format.

### Sync Metadata (optional)

After `ghs-backlog-sync` runs, two additional rows may appear in the health item metadata table:

```markdown
| **Synced Issue** | #{number} |
| **Issue URL** | {url} |
```

These are appended after the `Detected` row. They are backward-compatible — items that have not been synced simply lack these rows. Skills that parse health items should treat these fields as optional.

- **Synced Issue**: The GitHub issue number (prefixed with `#`) created by `ghs-backlog-sync`.
- **Issue URL**: The full URL to the GitHub issue.

See `sync-format.md` for the full sync contract including label taxonomy and issue body template.

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
3. **INFO items** are purely informational and do not affect the score at all. They are not counted in earned or possible totals.
4. Issues do not have a point score. They are tracked by count and label breakdown.

### Module scoring

Each module is scored independently, then combined:

| Module | Max Points | Weight (with lang module) | Weight (solo) |
|--------|------------|---------------------------|---------------|
| Core | 74 | 60% | 100% |
| .NET | 34 | 40% | — |

**Combined formula**: `score = round(core_pct * 0.6 + lang_pct * 0.4)`

If no language module is active: `score = core_pct` (100% weight).

### Per-module percentage

```
module_pct = round(earned_points / possible_points * 100)
```

### Progress bar format

Use `█` for filled and `░` for empty, **8 characters wide**. Calculate filled characters as `round(percentage / 100 * 8)`.

Example: 50% = `████░░░░`
