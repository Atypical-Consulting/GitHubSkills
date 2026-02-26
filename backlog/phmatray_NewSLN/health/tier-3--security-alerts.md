# Security Alerts

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Source** | Health Check |
| **Tier** | 3 — Nice to Have |
| **Points** | 1 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

Vulnerability alerts are disabled for this repository.

## Why It Matters

With vulnerability alerts disabled, you won't be notified when dependencies have known security issues. This means vulnerable packages can persist undetected, increasing the attack surface.

## How to Fix

### Quick Fix

```bash
gh api repos/phmatray/NewSLN/vulnerability-alerts -X PUT
```

### Full Solution

1. Enable vulnerability alerts (command above)
2. Enable Dependabot security updates:
   ```bash
   gh api repos/phmatray/NewSLN/automated-security-fixes -X PUT
   ```
3. Optionally add a `.github/dependabot.yml` for automated version updates:
   ```yaml
   version: 2
   updates:
     - package-ecosystem: "nuget"
       directory: "/"
       schedule:
         interval: "weekly"
   ```

## Acceptance Criteria

- [ ] Vulnerability alerts are enabled for the repository
- [ ] No open critical or high severity alerts

## References

- https://docs.github.com/en/code-security/dependabot/dependabot-alerts/configuring-dependabot-alerts
