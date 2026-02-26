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

Vulnerability alerts (Dependabot) are not enabled for this repository.

## Why It Matters

Without vulnerability alerts, you won't be notified when dependencies like Google.OrTools or Microsoft.Extensions packages have known security issues. Dependabot can automatically flag vulnerable packages and even create PRs to update them.

## How to Fix

### Quick Fix

```bash
gh api repos/phmatray/SudokuSolver/vulnerability-alerts -X PUT
```

### Full Solution

1. Enable vulnerability alerts (command above)
2. Optionally enable Dependabot security updates in Settings > Code security
3. Consider adding a `dependabot.yml` for automatic version updates:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "nuget"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Acceptance Criteria

- [x] Vulnerability alerts are enabled (`gh api repos/phmatray/SudokuSolver/vulnerability-alerts` returns 204)
- [x] No open critical or high severity alerts

## References

- https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts
