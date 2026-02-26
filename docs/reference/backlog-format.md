# Backlog Format

The backlog is GHS's structured storage for scan results and issue tracking.

## Directory Structure

```
backlog/
└── {owner}_{repo}/
    ├── SUMMARY.md
    ├── health/
    │   ├── tier-1--readme.md
    │   ├── tier-2--gitignore.md
    │   └── ...
    └── issues/
        ├── issue-42--fix-login-bug.md
        └── ...
```

## File Naming

- Health items: `tier-{N}--{slug}.md` (e.g., `tier-1--readme.md`)
- Issue items: `issue-{number}--{title-kebab}.md` (e.g., `issue-42--fix-login-bug.md`)
- Title kebab truncated to 50 characters

## Health Item Metadata

Each health item has a metadata table:

| Field | Description |
|-------|-------------|
| Check | Human-readable name |
| Slug | Kebab-case identifier |
| Tier | 1, 2, or 3 |
| Points | 4, 2, or 1 |
| Status | FAIL, PASS, or WARN |
| Category | One of 7 categories |

## Issue Item Metadata

| Field | Description |
|-------|-------------|
| Issue | Number + title |
| URL | GitHub issue URL |
| Labels | Applied labels |
| Status | OPEN, PR CREATED, or CLOSED |
| Priority | From triage labels |

## SUMMARY.md

Contains the overall score, progress bar, and counts of passing/failing checks per tier.
