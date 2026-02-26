---
name: Security Alerts
slug: security-alerts
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Security Alerts

## Verification

```bash
echo "=== ALERTS ENABLED ===" && (gh api repos/{owner}/{repo}/vulnerability-alerts 2>&1 || true)
echo "=== OPEN ALERTS ===" && (gh api repos/{owner}/{repo}/dependabot/alerts?state=open&per_page=1 2>&1 || true)
echo "=== RENOVATE ROOT ===" && (gh api repos/{owner}/{repo}/contents/renovate.json 2>&1 || true)
echo "=== RENOVATE GITHUB ===" && (gh api repos/{owner}/{repo}/contents/.github/renovate.json 2>&1 || true)
echo "=== RENOVATE JSON5 ===" && (gh api repos/{owner}/{repo}/contents/.github/renovate.json5 2>&1 || true)
echo "=== DEPENDABOT ===" && (gh api repos/{owner}/{repo}/contents/.github/dependabot.yml 2>&1 || true)
```

### Pass Condition
Vulnerability alerts are enabled AND there are no open critical/high security alerts.

### Status Rules
- **PASS**: Alerts enabled (API returns 204) and no open critical/high alerts
- **FAIL**: Alerts not enabled or there are open critical/high alerts
- **WARN**: Alerts API returns 403 (requires admin access)

**Important -- Dependency manager detection**: Before suggesting fixes, detect which dependency manager is in use:

| Indicator | Tool |
|-----------|------|
| `renovate.json` in root | Renovate |
| `.github/renovate.json` or `.github/renovate.json5` | Renovate |
| Open issue titled "Dependency Dashboard" | Renovate |
| `.github/dependabot.yml` | Dependabot |
| None | No automated dependency management |

## Backlog Content

### What's Missing
Vulnerability alerts are not enabled or there are open critical/high security alerts.

### Why It Matters
Without vulnerability alerts, known security issues in dependencies go unnoticed. Open critical/high alerts represent active security risks that could be exploited.

### Quick Fix
```bash
gh api repos/{owner}/{repo}/vulnerability-alerts -X PUT
```

### Full Solution
- **If Renovate detected**: Enable vulnerability alerts for CVE notifications. Do NOT suggest adding dependabot.yml -- Renovate already handles updates and running both creates duplicate PRs. Note: "Renovate handles dependency updates. GitHub vulnerability alerts provide CVE notifications independently."
- **If Dependabot detected**: Enable alerts if not already. Dependabot is already configured.
- **If no dependency manager**: Enable alerts (quick fix). Suggest adding `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "{ecosystem}"
    directory: "/"
    schedule:
      interval: "weekly"
```

Ecosystem mapping: .NET=nuget, Node.js=npm, Python=pip, Rust=cargo, Go=gomod, Java Maven=maven, Java Gradle=gradle, Ruby=bundler, PHP=composer, GitHub Actions=github-actions.

### Acceptance Criteria
- [ ] Vulnerability alerts are enabled (API returns 204)
- [ ] No open critical or high severity alerts

### Notes
Two parts -- enabling alerts (API-only) and resolving open alerts (may require dependency updates). The vulnerability-alerts endpoint requires admin access; if 403, report as WARN.

### References
- https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts
