# Security Alerts

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/BelgiumVatChecker` |
| **Source** | Health Check |
| **Tier** | 3 — Nice to Have |
| **Points** | 1 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

GitHub vulnerability alerts are not enabled for this repository.

## Why It Matters

Without vulnerability alerts, you won't be notified when dependencies have known security issues. The project uses several NuGet packages and Docker base images that should be monitored for CVEs.

## How to Fix

### Quick Fix

```bash
gh api repos/phmatray/BelgiumVatChecker/vulnerability-alerts -X PUT
```

### Full Solution

1. Enable GitHub vulnerability alerts via the command above or in Settings > Security > Dependabot alerts
2. This repo already uses **Renovate** for dependency version updates (detected via Dependency Dashboard issue), so there is no need to add a `dependabot.yml` — Renovate already handles update PRs
3. GitHub vulnerability alerts complement Renovate by providing CVE notifications in the Security tab

## Acceptance Criteria

- [ ] Vulnerability alerts are enabled for the repository
- [ ] No open critical or high severity alerts

## References

- https://docs.github.com/en/code-security/dependabot/dependabot-alerts/configuring-dependabot-alerts
