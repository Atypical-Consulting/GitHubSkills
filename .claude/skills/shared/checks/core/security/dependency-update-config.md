---
name: Dependency Update Config
slug: dependency-update-config
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Dependency Update Config

## Verification

```bash
echo "=== RENOVATE ROOT ===" && (gh api repos/{owner}/{repo}/contents/renovate.json --jq '.size' 2>&1 || true)
echo "=== RENOVATE GITHUB ===" && (gh api repos/{owner}/{repo}/contents/.github/renovate.json --jq '.size' 2>&1 || true)
echo "=== RENOVATE JSON5 ===" && (gh api repos/{owner}/{repo}/contents/.github/renovate.json5 --jq '.size' 2>&1 || true)
echo "=== DEPENDABOT ===" && (gh api repos/{owner}/{repo}/contents/.github/dependabot.yml --jq '.size' 2>&1 || true)
echo "=== RENOVATE CONTENT ===" && (gh api repos/{owner}/{repo}/contents/renovate.json --jq '.content' 2>&1 | base64 -d 2>/dev/null || true)
echo "=== DEPENDABOT CONTENT ===" && (gh api repos/{owner}/{repo}/contents/.github/dependabot.yml --jq '.content' 2>&1 | base64 -d 2>/dev/null || true)
```

### Pass Condition
A Renovate or Dependabot configuration file exists with meaningful customization beyond bare defaults. "Meaningful" means the config either specifies a schedule, groups updates, defines custom rules, pins specific packages, or extends a non-trivial preset.

### Status Rules
- **PASS**: Config file exists with customization beyond bare defaults
- **FAIL**: No dependency update config exists, or config is bare-minimum default only
- **WARN**: Config exists but could not be parsed

**Bare-minimum defaults (these count as FAIL):**
- Renovate: `{"$schema": "...", "extends": ["config:recommended"]}` with nothing else
- Dependabot: Only a single ecosystem with `interval: "weekly"` and no other settings

## Backlog Content

### What's Missing
No dependency update configuration exists, or the configuration is a bare-minimum default with no project-specific customization.

### Why It Matters
A minimal default config creates PR noise without thoughtful management. Grouped updates, schedules, and auto-merge rules reduce the burden of keeping dependencies current. Without them, maintainers get overwhelmed by individual dependency PRs and start ignoring them.

### Quick Fix

**Renovate (if already using Renovate):**
```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "schedule": ["before 8am on Monday"],
  "automerge": true,
  "automergeType": "pr",
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    }
  ]
}
```

**Dependabot (if already using Dependabot):**
```yaml
version: 2
updates:
  - package-ecosystem: "{ecosystem}"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    groups:
      minor-and-patch:
        update-types:
          - "minor"
          - "patch"
```

### Full Solution
Choose one dependency manager and configure it thoughtfully:

**Renovate (recommended for complex projects):**
```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended",
    ":automergeMinor",
    "schedule:earlyMondays"
  ],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "matchDepTypes": ["devDependencies"],
      "automerge": true
    },
    {
      "matchUpdateTypes": ["major"],
      "dependencyDashboardApproval": true
    }
  ]
}
```

**Dependabot (simpler, GitHub-native):**
```yaml
version: 2
updates:
  - package-ecosystem: "{ecosystem}"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    groups:
      minor-and-patch:
        update-types:
          - "minor"
          - "patch"
    reviewers:
      - "{owner}"
```

Ecosystem mapping: .NET=nuget, Node.js=npm, Python=pip, Rust=cargo, Go=gomod, GitHub Actions=github-actions.

### Acceptance Criteria
- [ ] A Renovate or Dependabot config file exists
- [ ] Config includes at least one customization beyond bare defaults (schedule, grouping, auto-merge, or package rules)

### Notes
Do not suggest switching from Renovate to Dependabot or vice versa — respect the existing choice. If neither exists, suggest Dependabot for simplicity or Renovate for more control. Running both creates duplicate PRs and should be avoided.

### References
- https://docs.renovatebot.com/configuration-options/
- https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file
