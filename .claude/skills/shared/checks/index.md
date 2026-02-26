# Health Checks Index

Registry of all health checks used by the ghs-repo-scan skill. Each check has its own file organized in category subdirectories.

Consumed by: ghs-repo-scan (orchestrator and check agents), ghs-backlog-fix, ghs-backlog-board, ghs-backlog-score.

## Directory Structure

```
checks/
├── index.md                    ← this file
├── documentation/              ← project documentation files
├── repo-settings/              ← GitHub repository settings
├── dev-config/                 ← developer configuration files
├── ci-cd/                      ← continuous integration and delivery
├── community/                  ← community health and templates
├── security/                   ← security posture
└── maintenance/                ← ongoing project health
```

## Check Registry

### Tier 1 — Required (4 points each)

| Check | Slug | Category | File | Scoring |
|-------|------|----------|------|---------|
| README | `readme` | documentation | [readme.md](documentation/readme.md) | Normal |
| LICENSE | `license` | documentation | [license.md](documentation/license.md) | Normal |
| Description | `description` | repo-settings | [description.md](repo-settings/description.md) | Normal |
| Branch Protection | `branch-protection` | repo-settings | [branch-protection.md](repo-settings/branch-protection.md) | Normal |

### Tier 2 — Recommended (2 points each)

| Check | Slug | Category | File | Scoring |
|-------|------|----------|------|---------|
| .gitignore | `gitignore` | dev-config | [gitignore.md](dev-config/gitignore.md) | Normal |
| CI/CD Workflows | `ci-cd-workflows` | ci-cd | [ci-cd-workflows.md](ci-cd/ci-cd-workflows.md) | Normal |
| CI Workflow Health | `ci-workflow-health` | ci-cd | [ci-workflow-health.md](ci-cd/ci-workflow-health.md) | Normal |
| Action Version Pinning | `action-version-pinning` | ci-cd | [action-version-pinning.md](ci-cd/action-version-pinning.md) | Normal |
| Workflow Permissions | `workflow-permissions` | ci-cd | [workflow-permissions.md](ci-cd/workflow-permissions.md) | Normal |
| .editorconfig | `editorconfig` | dev-config | [editorconfig.md](dev-config/editorconfig.md) | Normal |
| CODEOWNERS | `codeowners` | dev-config | [codeowners.md](dev-config/codeowners.md) | Normal |
| Issue Templates | `issue-templates` | community | [issue-templates.md](community/issue-templates.md) | Normal |
| PR Template | `pr-template` | community | [pr-template.md](community/pr-template.md) | Normal |
| Topics | `topics` | repo-settings | [topics.md](repo-settings/topics.md) | Normal |
| Changelog | `changelog` | documentation | [changelog.md](documentation/changelog.md) | Normal |
| Delete Branch on Merge | `delete-branch-on-merge` | repo-settings | [delete-branch-on-merge.md](repo-settings/delete-branch-on-merge.md) | Normal |
| GitHub Releases | `github-releases` | maintenance | [github-releases.md](maintenance/github-releases.md) | Normal |
| Stale Issues | `stale-issues` | maintenance | [stale-issues.md](maintenance/stale-issues.md) | Normal |
| Stale PRs | `stale-prs` | maintenance | [stale-prs.md](maintenance/stale-prs.md) | Normal |
| Stale Branches | `stale-branches` | maintenance | [stale-branches.md](maintenance/stale-branches.md) | Normal |
| Merge Strategy | `merge-strategy` | repo-settings | [merge-strategy.md](repo-settings/merge-strategy.md) | Normal |
| README Description | `readme-description` | documentation | [readme-description.md](documentation/readme-description.md) | Normal |
| README Badges | `readme-badges` | documentation | [readme-badges.md](documentation/readme-badges.md) | Normal |
| README Installation | `readme-installation` | documentation | [readme-installation.md](documentation/readme-installation.md) | Normal |
| README Usage Examples | `readme-usage` | documentation | [readme-usage.md](documentation/readme-usage.md) | Normal |
| README Features | `readme-features` | documentation | [readme-features.md](documentation/readme-features.md) | Normal |

### Tier 3 — Nice to Have (1 point each)

| Check | Slug | Category | File | Scoring |
|-------|------|----------|------|---------|
| Workflow Naming | `workflow-naming` | ci-cd | [workflow-naming.md](ci-cd/workflow-naming.md) | Normal |
| Workflow Timeouts | `workflow-timeouts` | ci-cd | [workflow-timeouts.md](ci-cd/workflow-timeouts.md) | Normal |
| Workflow Concurrency | `workflow-concurrency` | ci-cd | [workflow-concurrency.md](ci-cd/workflow-concurrency.md) | Normal |
| SECURITY.md | `security-md` | community | [security-md.md](community/security-md.md) | Normal |
| CONTRIBUTING.md | `contributing-md` | documentation | [contributing-md.md](documentation/contributing-md.md) | Normal |
| Security Alerts | `security-alerts` | security | [security-alerts.md](security/security-alerts.md) | Normal |
| .editorconfig Drift | `editorconfig-drift` | dev-config | [editorconfig-drift.md](dev-config/editorconfig-drift.md) | Normal |
| Code of Conduct | `code-of-conduct` | documentation | [code-of-conduct.md](documentation/code-of-conduct.md) | Normal |
| Homepage URL | `homepage-url` | repo-settings | [homepage-url.md](repo-settings/homepage-url.md) | Normal |
| .gitattributes | `gitattributes` | dev-config | [gitattributes.md](dev-config/gitattributes.md) | Normal |
| Version Pinning | `version-pinning` | dev-config | [version-pinning.md](dev-config/version-pinning.md) | Normal |
| Dependency Update Config | `dependency-update-config` | security | [dependency-update-config.md](security/dependency-update-config.md) | Normal |
| README Table of Contents | `readme-toc` | documentation | [readme-toc.md](documentation/readme-toc.md) | Normal |
| README License Mention | `readme-license-mention` | documentation | [readme-license-mention.md](documentation/readme-license-mention.md) | Normal |
| Funding | `funding` | documentation | [funding.md](documentation/funding.md) | **INFO only** |
| Discussions Enabled | `discussions-enabled` | repo-settings | [discussions-enabled.md](repo-settings/discussions-enabled.md) | **INFO only** |
| Commit Signoff | `commit-signoff` | repo-settings | [commit-signoff.md](repo-settings/commit-signoff.md) | **INFO only** |

## Scoring Summary

| Tier | Checks | Points each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 | 4 | 4 | 16 |
| Tier 2 | 22 | 2 | 44 |
| Tier 3 | 14 (excluding Funding, Discussions, Commit Signoff) | 1 | 14 |
| **Total** | **40** | | **74** |

- WARN items are excluded from both earned and possible totals.
- INFO items (Funding, Discussions Enabled, Commit Signoff) carry no points and no penalty.
- Percentage: `earned / possible * 100`, rounded to nearest integer.

## Category Summary

| Category | Checks | Description |
|----------|--------|-------------|
| documentation | 13 | Project documentation files (README, LICENSE, CHANGELOG, README content quality, etc.) |
| repo-settings | 8 | GitHub repository configuration (description, topics, branch protection, merge strategy, etc.) |
| dev-config | 6 | Developer tooling and config files (.gitignore, .editorconfig, .gitattributes, etc.) |
| ci-cd | 7 | CI/CD pipelines, workflow health, and GitHub Actions best practices |
| community | 3 | Community health templates (issue/PR templates, security policy) |
| security | 2 | Security posture and dependency management |
| maintenance | 4 | Ongoing project health (releases, stale issues, stale PRs, stale branches) |

## Slug-to-Path Lookup

Agents use this table to resolve check file paths from slugs:

| Slug | Path |
|------|------|
| `readme` | `documentation/readme.md` |
| `license` | `documentation/license.md` |
| `changelog` | `documentation/changelog.md` |
| `contributing-md` | `documentation/contributing-md.md` |
| `code-of-conduct` | `documentation/code-of-conduct.md` |
| `funding` | `documentation/funding.md` |
| `readme-description` | `documentation/readme-description.md` |
| `readme-badges` | `documentation/readme-badges.md` |
| `readme-installation` | `documentation/readme-installation.md` |
| `readme-usage` | `documentation/readme-usage.md` |
| `readme-features` | `documentation/readme-features.md` |
| `readme-toc` | `documentation/readme-toc.md` |
| `readme-license-mention` | `documentation/readme-license-mention.md` |
| `description` | `repo-settings/description.md` |
| `topics` | `repo-settings/topics.md` |
| `homepage-url` | `repo-settings/homepage-url.md` |
| `branch-protection` | `repo-settings/branch-protection.md` |
| `delete-branch-on-merge` | `repo-settings/delete-branch-on-merge.md` |
| `merge-strategy` | `repo-settings/merge-strategy.md` |
| `discussions-enabled` | `repo-settings/discussions-enabled.md` |
| `commit-signoff` | `repo-settings/commit-signoff.md` |
| `gitignore` | `dev-config/gitignore.md` |
| `editorconfig` | `dev-config/editorconfig.md` |
| `editorconfig-drift` | `dev-config/editorconfig-drift.md` |
| `gitattributes` | `dev-config/gitattributes.md` |
| `version-pinning` | `dev-config/version-pinning.md` |
| `codeowners` | `dev-config/codeowners.md` |
| `ci-cd-workflows` | `ci-cd/ci-cd-workflows.md` |
| `ci-workflow-health` | `ci-cd/ci-workflow-health.md` |
| `action-version-pinning` | `ci-cd/action-version-pinning.md` |
| `workflow-permissions` | `ci-cd/workflow-permissions.md` |
| `workflow-naming` | `ci-cd/workflow-naming.md` |
| `workflow-timeouts` | `ci-cd/workflow-timeouts.md` |
| `workflow-concurrency` | `ci-cd/workflow-concurrency.md` |
| `issue-templates` | `community/issue-templates.md` |
| `pr-template` | `community/pr-template.md` |
| `security-md` | `community/security-md.md` |
| `security-alerts` | `security/security-alerts.md` |
| `dependency-update-config` | `security/dependency-update-config.md` |
| `stale-issues` | `maintenance/stale-issues.md` |
| `stale-prs` | `maintenance/stale-prs.md` |
| `stale-branches` | `maintenance/stale-branches.md` |
| `github-releases` | `maintenance/github-releases.md` |

## How Agents Use This Index

Each check agent receives a tier assignment. It:
1. Reads this index to find the checks in its tier
2. For each check, uses the **Slug-to-Path Lookup** table to find the check file: `{category}/{slug}.md`
3. Reads the individual check file
4. Runs the verification command from the check file
5. Determines PASS/FAIL/WARN based on status rules
6. If FAIL/WARN, writes a backlog item using the Backlog Content section from the check file
7. Returns structured results to the orchestrator
