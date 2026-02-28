# Configuration Constants

Centralized configuration values used across multiple skills. Skills reference these constants instead of hardcoding values to prevent drift.

## Scoring

| Constant | Value | Used By |
|----------|-------|---------|
| Tier 1 points | 4 | repo-scan, backlog-score, backlog-board, backlog-next |
| Tier 2 points | 2 | repo-scan, backlog-score, backlog-board, backlog-next |
| Tier 3 points | 1 | repo-scan, backlog-score, backlog-board, backlog-next |
| Core max points | 74 | backlog-score |
| .NET max points | 34 | backlog-score |
| Core weight (with lang module) | 60% | repo-scan, backlog-score |
| Language module weight | 40% | repo-scan, backlog-score |

## Modules

| Module | Slug | Detection Marker | Project Field Value |
|--------|------|------------------|---------------------|
| Core | `core` | Always active | `core` |
| .NET | `dotnet` | `*.sln` in repo root | `dotnet` |

## Display

| Constant | Value |
|----------|-------|
| Progress bar width | 8 characters |
| Progress bar filled char | `\u2588` |
| Progress bar empty char | `\u2591` |
| Max terminal issues | 20 |
| Issue body truncation | 500 chars |
| Title kebab truncation | 50 chars |

## Thresholds

| Constant | Value |
|----------|-------|
| Stale scan threshold | 30 days |
| Max issues fetched | 500 |
| Classification body limit | 2000 chars |

## GitHub Projects

| Constant | Value |
|----------|-------|
| Project title prefix | `[GHS]` |
| Project title format | `[GHS] {owner}/{repo}` |
| State issue label | `ghs:state` |
| State issue title | `[GHS State] {owner}/{repo}` |
| Score item title | `[GHS Score]` |
| Health item title prefix | `[Health]` |
| Auth scope required | `project` |

## Status Indicators

| Indicator | Meaning |
|-----------|---------|
| `[PASS]` | Check passed |
| `[FAIL]` | Check failed |
| `[WARN]` | Cannot verify (permissions) |
| `[INFO]` | Informational only (no score impact) |
