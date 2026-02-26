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

Vulnerability alerts (Dependabot) are not enabled for this repository.

## Why It Matters

Without vulnerability alerts, you won't be notified when dependencies have known security issues. The project uses several NuGet packages and Docker base images that should be monitored for CVEs.

## How to Fix

### Quick Fix

```bash
gh api repos/phmatray/BelgiumVatChecker/vulnerability-alerts -X PUT
```

### Full Solution

1. Enable vulnerability alerts via the command above or in Settings > Security > Dependabot alerts
2. Optionally enable Dependabot security updates for automatic PRs:
   - Settings > Security > Dependabot security updates
3. Optionally add a `dependabot.yml` config for version updates:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "nuget"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Acceptance Criteria

- [ ] Vulnerability alerts are enabled for the repository
- [ ] No open critical or high severity alerts

## References

- https://docs.github.com/en/code-security/dependabot/dependabot-alerts/configuring-dependabot-alerts
