---
layout: home

hero:
  name: "GHS"
  text: "Your repos deserve better."
  tagline: "38 health checks. Parallel AI agents. Real pull requests."
  actions:
    - theme: brand
      text: Get Started
      link: /getting-started/installation
    - theme: alt
      text: See All Checks
      link: /checks/

features:
  - icon: "🔍"
    title: Scan
    details: Run 38 health checks across documentation, settings, CI/CD, security, and community standards. Get a scored report in seconds.
  - icon: "🔧"
    title: Fix
    details: Parallel worktree-based agents fix multiple issues simultaneously. Each fix gets its own branch and pull request.
  - icon: "🔄"
    title: Loop
    details: Continuous improvement cycle — scan, review the board, fix the highest-impact item, merge, repeat until 100%.
---

## What Gets Checked

GHS audits your repository against **38 health checks** organized into 3 tiers:

| Tier | Focus | Checks | Points Each | Subtotal |
|------|-------|--------|-------------|----------|
| **Tier 1 — Required** | Fundamental repo quality | 4 | 4 pts | 16 pts |
| **Tier 2 — Recommended** | Professional standards | 20 | 2 pts | 40 pts |
| **Tier 3 — Nice to Have** | Polish and completeness | 11 scored + 3 INFO | 1 pt | 11 pts |
| **Total** | | **35 scored** | | **67 pts** |

**Tier 1** covers the essentials every repo needs: README, LICENSE, repository description, and branch protection.

**Tier 2** covers professional standards: .gitignore, CI/CD workflows, .editorconfig, CODEOWNERS, issue templates, PR template, topics, changelog, GitHub releases, stale issue/PR/branch detection, merge strategy, and README content quality (description, badges, installation, usage, features).

**Tier 3** adds polish: SECURITY.md, CONTRIBUTING.md, security alerts, .editorconfig drift detection, code of conduct, homepage URL, .gitattributes, version pinning, dependency update config, README table of contents, README license mention, and three informational checks (funding, discussions, commit signoff).

## How It Works

```
"scan my repo" --> scored report --> "fix the backlog" --> PRs created --> "merge my PRs" --> improved score
```

GHS follows a simple loop: **scan** to find problems, **fix** to create pull requests, and **merge** to land the improvements. Each cycle raises your health score closer to 100%.

## Terminal Output Preview

```
Repository Health: phmatray/my-project
Score: 45/67 (67%) ██████░░

Tier 1 — Required (4 checks)
  [PASS] README exists
  [PASS] LICENSE exists
  [FAIL] Repository description is empty
  [PASS] Branch protection enabled

Tier 2 — Recommended (20 checks)
  [PASS] .gitignore exists
  [FAIL] No CI/CD workflows found
  [PASS] CI workflow health — all workflows passing
  [FAIL] .editorconfig not found
  [PASS] CODEOWNERS exists
  [PASS] Issue templates configured
  [FAIL] No PR template found
  [PASS] Repository topics set
  [PASS] CHANGELOG exists
  [PASS] Delete branch on merge enabled
  [PASS] GitHub releases found
  [PASS] No stale issues (> 90 days)
  [PASS] No stale PRs (> 30 days)
  [WARN] Stale branches — 3 branches with no recent activity
  [PASS] Merge strategy configured
  [PASS] README has description section
  [PASS] README has badges
  [PASS] README has installation instructions
  [PASS] README has usage section
  [FAIL] README has no features section

Tier 3 — Nice to Have (14 checks)
  [FAIL] SECURITY.md not found
  [FAIL] CONTRIBUTING.md not found
  [PASS] Security alerts enabled
  [PASS] .editorconfig matches file styles
  [FAIL] No code of conduct
  [PASS] Homepage URL set
  [PASS] .gitattributes exists
  [FAIL] No version pinning (global.json / .tool-versions)
  [PASS] Dependabot or Renovate configured
  [FAIL] README has no table of contents
  [PASS] README mentions license
  [INFO] FUNDING.yml not found (optional)
  [INFO] Discussions not enabled (optional)
  [INFO] Commit signoff not required (optional)

Backlog saved to: backlog/phmatray_my-project/
  health/   — 10 items (9 FAIL, 1 WARN)
  issues/   — 7 items
```
