# Shared Configuration Constants

Centralized configuration values used across multiple skills. Reference this file instead of hardcoding values — it makes tuning easier and prevents drift between skills.

## Scoring

| Constant | Value | Used By |
|----------|-------|---------|
| Tier 1 points | 4 | ghs-repo-scan, ghs-backlog-score, ghs-backlog-board, ghs-backlog-next |
| Tier 2 points | 2 | ghs-repo-scan, ghs-backlog-score, ghs-backlog-board, ghs-backlog-next |
| Tier 3 points | 1 | ghs-repo-scan, ghs-backlog-score, ghs-backlog-board, ghs-backlog-next |
| Core max points | 74 | ghs-backlog-score |
| .NET max points | 34 | ghs-backlog-score |
| Core weight (with lang module) | 0.6 (60%) | ghs-repo-scan, ghs-backlog-score |
| Language module weight | 0.4 (40%) | ghs-repo-scan, ghs-backlog-score |

## Modules

| Module | Slug | Detection Marker | Backlog Subdir |
|--------|------|------------------|----------------|
| Core | `core` | Always active | `health/` |
| .NET | `dotnet` | `*.sln` in repo root | `dotnet/` |

## Display

| Constant | Value | Used By |
|----------|-------|---------|
| Progress bar width | 8 chars | ghs-repo-scan, ghs-backlog-board, ghs-backlog-score |
| Progress bar filled char | `█` | ghs-repo-scan, ghs-backlog-board, ghs-backlog-score |
| Progress bar empty char | `░` | ghs-repo-scan, ghs-backlog-board, ghs-backlog-score |
| Max terminal issues | 20 | ghs-repo-scan |
| Issue body truncation | 500 chars | ghs-repo-scan |
| Title kebab truncation | 50 chars | ghs-repo-scan |

## Thresholds

| Constant | Value | Used By |
|----------|-------|---------|
| Stale scan threshold | 30 days | ghs-backlog-board, ghs-backlog-next |
| Max issues fetched | 500 | ghs-repo-scan |
| Classification body limit | 2000 chars | ghs-issue-triage |

## Status Indicators

| Indicator | Meaning | Used By |
|-----------|---------|---------|
| `[PASS]` | Check passed | ghs-repo-scan, ghs-backlog-fix |
| `[FAIL]` | Check failed | ghs-repo-scan, ghs-backlog-fix |
| `[WARN]` | Cannot verify (permissions) | ghs-repo-scan |
| `[INFO]` | Informational only (no score impact) | ghs-repo-scan |
