# Backlog Format

The backlog is GHS's structured storage for scan results and issue tracking.

## Directory Structure

```
backlog/
└── {owner}_{repo}/
    ├── SUMMARY.md
    ├── health/              # Core module findings
    │   ├── tier-1--readme.md
    │   ├── tier-2--gitignore.md
    │   └── ...
    ├── dotnet/              # .NET module findings (if detected)
    │   ├── tier-1--dotnet-build-props.md
    │   ├── tier-2--dotnet-nullable.md
    │   └── ...
    └── issues/
        ├── issue-42--fix-login-bug.md
        └── ...
```

### Module-to-Directory Mapping

| Module | Directory | When Created |
|--------|-----------|--------------|
| Core | `health/` | At least one core FAIL/WARN |
| .NET | `dotnet/` | .NET module active + at least one FAIL/WARN |
| Issues | `issues/` | Repo has open issues |

Future modules use their slug as the directory name (e.g., `python/`, `node/`).

## File Naming

- Core health items: `tier-{N}--{slug}.md` in `health/` (e.g., `tier-1--readme.md`)
- .NET items: `tier-{N}--{slug}.md` in `dotnet/` (e.g., `tier-2--dotnet-nullable.md`)
- Issue items: `issue-{number}--{title-kebab}.md` (e.g., `issue-42--fix-login-bug.md`)
- Title kebab truncated to 50 characters

## Health Item Metadata

Each health item has a metadata table:

| Field | Description |
|-------|-------------|
| Repository | `owner/repo` |
| Source | Always `Health Check` |
| Module | `core` or `dotnet` |
| Tier | 1, 2, or 3 with label |
| Points | 4, 2, or 1 |
| Status | FAIL, PASS, or WARN |
| Detected | Date of scan |

### Sync Metadata (optional)

After running `ghs-backlog-sync`, two additional fields may appear in health items:

| Field | Description |
|-------|-------------|
| Synced Issue | GitHub issue number (e.g., `#42`) |
| Issue URL | Full URL to the GitHub issue |

These fields are backward-compatible --- items that have not been synced simply lack them.

## Issue Item Metadata

| Field | Description |
|-------|-------------|
| Issue | Number + title |
| URL | GitHub issue URL |
| Labels | Applied labels |
| Status | OPEN, PR CREATED, or CLOSED |
| Priority | From triage labels |

## SUMMARY.md

Contains per-module score breakdowns, combined weighted score (if language module active), progress bars, and counts of passing/failing checks per tier per module.
