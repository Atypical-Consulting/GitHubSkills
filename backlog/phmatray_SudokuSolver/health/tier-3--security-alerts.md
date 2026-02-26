# Security Alerts

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/SudokuSolver` |
| **Source** | Health Check |
| **Tier** | 3 — Nice to Have |
| **Points** | 1 |
| **Status** | PASS |
| **Detected** | 2026-02-26 |

## What's Missing

GitHub vulnerability alerts were not enabled for this repository (now resolved).

## Why It Matters

Without vulnerability alerts, you won't be notified when dependencies like Google.OrTools or Microsoft.Extensions packages have known security issues. GitHub vulnerability alerts provide CVE notifications in the Security tab.

## How to Fix

### Quick Fix

```bash
gh api repos/phmatray/SudokuSolver/vulnerability-alerts -X PUT
```

### Full Solution

1. Enable vulnerability alerts (command above)
2. This repo already uses **Renovate** for dependency version updates, so there is no need to add a `dependabot.yml` — Renovate already handles update PRs
3. GitHub vulnerability alerts complement Renovate by providing CVE notifications in the Security tab

## Acceptance Criteria

- [x] Vulnerability alerts are enabled (`gh api repos/phmatray/SudokuSolver/vulnerability-alerts` returns 204)
- [x] No open critical or high severity alerts

## References

- https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts
