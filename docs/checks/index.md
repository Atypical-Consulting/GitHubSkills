# Check Registry

GHS scans repositories against **38 health checks** organized into 3 tiers and 7 categories.

## Scoring

| Tier | Checks | Points Each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 — Required | 4 | 4 | 16 |
| Tier 2 — Recommended | 20 | 2 | 40 |
| Tier 3 — Nice to Have | 11 scored + 3 INFO | 1 | 11 |
| **Total** | **35 scored** | | **67** |

WARN items are excluded from both earned and possible totals -- they indicate permission issues, not real failures. INFO items carry no points and do not affect the score.

## All Checks

| # | Check | Slug | Tier | Category | Points |
|---|-------|------|------|----------|--------|
| 1 | README exists | `readme` | 1 | Documentation | 4 |
| 2 | LICENSE exists | `license` | 1 | Documentation | 4 |
| 3 | Repository description set | `description` | 1 | Repo Settings | 4 |
| 4 | Branch protection enabled | `branch-protection` | 1 | Repo Settings | 4 |
| 5 | .gitignore exists | `gitignore` | 2 | Dev Config | 2 |
| 6 | CI/CD workflows present | `ci-cd-workflows` | 2 | CI/CD | 2 |
| 7 | CI workflow health | `ci-workflow-health` | 2 | CI/CD | 2 |
| 8 | .editorconfig exists | `editorconfig` | 2 | Dev Config | 2 |
| 9 | CODEOWNERS exists | `codeowners` | 2 | Dev Config | 2 |
| 10 | Issue templates configured | `issue-templates` | 2 | Community | 2 |
| 11 | PR template exists | `pr-template` | 2 | Community | 2 |
| 12 | Repository topics set | `topics` | 2 | Repo Settings | 2 |
| 13 | CHANGELOG exists | `changelog` | 2 | Documentation | 2 |
| 14 | Delete branch on merge | `delete-branch-on-merge` | 2 | Repo Settings | 2 |
| 15 | GitHub releases present | `github-releases` | 2 | Maintenance | 2 |
| 16 | No stale issues | `stale-issues` | 2 | Maintenance | 2 |
| 17 | No stale PRs | `stale-prs` | 2 | Maintenance | 2 |
| 18 | No stale branches | `stale-branches` | 2 | Maintenance | 2 |
| 19 | Merge strategy configured | `merge-strategy` | 2 | Repo Settings | 2 |
| 20 | README has description | `readme-description` | 2 | Documentation | 2 |
| 21 | README has badges | `readme-badges` | 2 | Documentation | 2 |
| 22 | README has installation | `readme-installation` | 2 | Documentation | 2 |
| 23 | README has usage section | `readme-usage` | 2 | Documentation | 2 |
| 24 | README has features section | `readme-features` | 2 | Documentation | 2 |
| 25 | SECURITY.md exists | `security-md` | 3 | Community | 1 |
| 26 | CONTRIBUTING.md exists | `contributing-md` | 3 | Documentation | 1 |
| 27 | Security alerts enabled | `security-alerts` | 3 | Security | 1 |
| 28 | .editorconfig drift | `editorconfig-drift` | 3 | Dev Config | 1 |
| 29 | Code of conduct | `code-of-conduct` | 3 | Documentation | 1 |
| 30 | Homepage URL set | `homepage-url` | 3 | Repo Settings | 1 |
| 31 | .gitattributes exists | `gitattributes` | 3 | Dev Config | 1 |
| 32 | Version pinning | `version-pinning` | 3 | Dev Config | 1 |
| 33 | Dependency update config | `dependency-update-config` | 3 | Security | 1 |
| 34 | README has table of contents | `readme-toc` | 3 | Documentation | 1 |
| 35 | README mentions license | `readme-license-mention` | 3 | Documentation | 1 |
| 36 | FUNDING.yml exists | `funding` | 3 | Documentation | INFO |
| 37 | Discussions enabled | `discussions-enabled` | 3 | Repo Settings | INFO |
| 38 | Commit signoff required | `commit-signoff` | 3 | Repo Settings | INFO |

## By Category

| Category | Checks | Description |
|----------|--------|-------------|
| **Documentation** | 13 | README, LICENSE, CHANGELOG, CONTRIBUTING, code of conduct, funding, and README content quality |
| **Repo Settings** | 8 | Description, branch protection, topics, delete-branch-on-merge, merge strategy, homepage URL, discussions, commit signoff |
| **Dev Config** | 6 | .gitignore, .editorconfig, CODEOWNERS, .editorconfig drift, .gitattributes, version pinning |
| **CI/CD** | 2 | Workflow presence and workflow health |
| **Community** | 3 | Issue templates, PR template, SECURITY.md |
| **Security** | 2 | Security alerts, dependency update config |
| **Maintenance** | 4 | GitHub releases, stale issues, stale PRs, stale branches |

## Tier Deep Dives

- [Tier 1 — Required](/checks/tier-1) (4 checks, 4 pts each)
- [Tier 2 — Recommended](/checks/tier-2) (20 checks, 2 pts each)
- [Tier 3 — Nice to Have](/checks/tier-3) (14 checks, 1 pt or INFO)
