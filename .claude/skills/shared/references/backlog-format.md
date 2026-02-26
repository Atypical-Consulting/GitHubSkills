# Backlog Format Reference

Quick reference for backlog directory structure, file naming, metadata formats, and status values. For full details, see `../backlog-format.md`.

## Directory Structure

```
backlog/{owner}_{repo}/
  SUMMARY.md                           # Always created — scores, tables, links
  health/                              # Only if FAIL/WARN checks exist
    tier-1--readme.md
    tier-1--license.md
    tier-2--editorconfig.md
  issues/                              # Only if open issues exist
    issue-42--login-page-crashes.md
    issue-108--add-dark-mode.md
```

- `{owner}_{repo}` uses underscore separator (not slash)
- `repos/` directory holds cloned repos (gitignored, ephemeral)
- `backlog/` directory holds persistent backlog data

## File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Health item | `tier-{N}--{slug}.md` | `tier-1--branch-protection.md` |
| Issue item | `issue-{number}--{title-kebab}.md` | `issue-42--login-page-crashes.md` |

- Health slugs come from `checks/index.md`
- Issue title-kebab: lowercase, non-alphanumeric to `-`, truncated to 50 chars at word boundary
- Only FAIL/WARN checks get files; PASS checks are listed in SUMMARY.md only

## Health Item Metadata

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

Optional sync rows (added by `ghs-backlog-sync`):

```markdown
| **Synced Issue** | #{number} |
| **Issue URL** | https://github.com/{owner}/{repo}/issues/{number} |
```

## Issue Item Metadata

```markdown
# {Issue Title}

| Field | Value |
|-------|-------|
| **Repository** | `{owner}/{repo}` |
| **Source** | Issue #{number} |
| **Labels** | {comma-separated, or "none"} |
| **Assignee** | {login, or "unassigned"} |
| **Status** | {OPEN|PR CREATED|CLOSED} |
| **Created** | {YYYY-MM-DD} |
| **Updated** | {YYYY-MM-DD} |
```

## Status Values

| Source | Status | Meaning |
|--------|--------|---------|
| Health | FAIL | Check did not pass; action required |
| Health | PASS | Check passed (after fix applied) |
| Health | WARN | Unable to verify (permission issue, 403) |
| Issue | OPEN | Issue open, no PR yet |
| Issue | PR CREATED | Fix PR created referencing this issue |
| Issue | CLOSED | Issue closed on GitHub |

## Status Indicators (Terminal Output)

| Indicator | Meaning |
|-----------|---------|
| `[PASS]` | Check passed |
| `[FAIL]` | Check failed |
| `[WARN]` | Cannot verify (permissions) |
| `[INFO]` | Informational only (no score impact) |

## Parsing

```bash
# Parse a single backlog item
python .claude/skills/shared/scripts/parse_backlog_item.py <path>

# Calculate aggregate score for a repo
python .claude/skills/shared/scripts/calculate_score.py backlog/{owner}_{repo}
```
